# tests/experiment.py
"""
Deterministic evaluation of the Lateral‑Inhibition Sparsity Auditor (YB‑0003)
against MSP and Energy baselines on sklearn digits.
"""

import os
import json
import numpy as np
from pathlib import Path

from sklearn.datasets import load_digits
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

# deterministic RNGs
SEED = 0
rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------------
# Load data, split into in‑distribution (digits 0‑4) and OOD sets
# ----------------------------------------------------------------------
X, y = load_digits(return_X_y=True)
X = X.astype(np.float32) / 16.0          # scale to [0,1]

# shuffle once globally
perm = rng.permutation(len(X))
X, y = X[perm], y[perm]

in_mask = y < 5               # digits 0‑4 are in‑distribution
ood_mask = ~in_mask           # digits 5‑9

X_in, y_in = X[in_mask], y[in_mask]
X_ood_clean = X[ood_mask]    # near‑OOD (different classes)

# uniform noise OOD (same shape as a single sample)
def uniform_noise(n_samples):
    return rng.uniform(0.0, 1.0, size=(n_samples, X.shape[1])).astype(np.float32)

X_ood_noise = uniform_noise(len(X_ood_clean))

# ----------------------------------------------------------------------
# Train MLP on in‑distribution data
# ----------------------------------------------------------------------
from src.mlp import MLP

net = MLP(d=64, h1=32, h2=32, c=5, seed=SEED)
net.train(X_in, y_in)

# ----------------------------------------------------------------------
# Helper functions for detectors
# ----------------------------------------------------------------------
def msp_score(x_batch):
    """Maximum softmax probability (higher -> more in‑distribution)."""
    _, _, _, _, logits = net.forward(x_batch)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    return probs.max(axis=1)

def energy_score(x_batch):
    """Energy = -logsumexp(logits) (lower -> more in‑distribution)."""
    _, _, _, _, logits = net.forward(x_batch)
    # use stable log-sum-exp
    max_logit = np.max(logits, axis=1, keepdims=True)
    return -(max_logit + np.log(np.exp(logits - max_logit).sum(axis=1)))

def fgsm_examples(x, y_true, eps):
    """Generate FGSM adversarial examples for a batch."""
    # net.fgsm expects (X, y, eps) and returns perturbed X
    return net.fgsm(x, y_true, eps)

# ----------------------------------------------------------------------
# Load the compiled C core and wrap it via src.algo.SparseAuditor
# ----------------------------------------------------------------------
from src.algo import SparseAuditor

model_path = Path(__file__).parents[1] / "tmp_model.bin"
# Export the trained network to the same binary format expected by the C code.
# The MLP class already provides a helper for this (assumed _save_weights_to_file).
net._save_weights_to_file(str(model_path))

auditor = SparseAuditor(str(model_path), tau=None, use_ref=False)

def sparsity_score(x_batch):
    """Average Gini sparsity (higher -> more in‑distribution)."""
    scores = np.empty(len(x_batch), dtype=np.float32)
    for i, row in enumerate(x_batch):
        s, _ = auditor.detect(row)
        scores[i] = s
    return scores

# ----------------------------------------------------------------------
# Prepare evaluation sets
# ----------------------------------------------------------------------
X_test_in = X_in[:200]          # keep it small for speed
y_test_in = y_in[:200]

# OOD variants
ood_variants = {
    "near_ood": X_ood_clean,
    "noise_ood": X_ood_noise,
}
# adversarial attacks (on in‑distribution test set)
adv_epsilons = [0.1, 0.2]
for eps in adv_epsilons:
    X_adv = fgsm_examples(X_test_in, y_test_in, eps)
    ood_variants[f"fgsm_{eps:.2f}"] = X_adv

# ----------------------------------------------------------------------
# Compute detector scores for each variant
# ----------------------------------------------------------------------
results = {}

def compute_auroc(in_scores, ood_scores, higher_is_more_in=True):
    """Return AUROC where positive class = OOD."""
    labels = np.concatenate([np.zeros_like(in_scores), np.ones_like(ood_scores)])
    scores = np.concatenate([in_scores, ood_scores])
    if not higher_is_more_in:
        # flip so that larger means more in‑distribution
        scores = -scores
    return roc_auc_score(labels, scores)

# baseline detectors
baseline_funcs = {
    "MSP": (msp_score, True),          # higher -> more in
    "Energy": (energy_score, False),   # lower -> more in
}
# sparsity detector
sparsity_func = (sparsity_score, True)  # higher -> more in

for name, (func, higher_is_in) in baseline_funcs.items():
    in_sc = func(X_test_in)
    results[name] = {}
    for ood_name, X_ood in ood_variants.items():
        ood_sc = func(X_ood[:len(in_sc)])  # match size
        auroc = compute_auroc(in_sc, ood_sc, higher_is_more_in=higher_is_in)
        results[name][ood_name] = round(float(auroc), 4)

# sparsity auditor
in_sc = sparsity_func[0](X_test_in)
results["Sparsity"] = {}
for ood_name, X_ood in ood_variants.items():
    ood_sc = sparsity_func[0](X_ood[:len(in_sc)])
    auroc = compute_auroc(in_sc, ood_sc, higher_is_more_in=sparsity_func[1])
    results["Sparsity"][ood_name] = round(float(auroc), 4)

# ----------------------------------------------------------------------
# Save JSON and print a table
# ----------------------------------------------------------------------
docs_dir = Path(__file__).parents[2] / "docs"
os.makedirs(docs_dir, exist_ok=True)
json_path = docs_dir / "results.json"
with open(json_path, "w") as f:
    json.dump(results, f, indent=2)

# pretty‑print table
header = ["Detector"] + list(ood_variants.keys())
col_widths = [max(len(h), 9) for h in header]
row_fmt = " | ".join(f"{{:<{w}}}" for w in col_widths)
sep = "-+-".join("-" * w for w in col_widths)

print("\nAUROC results (higher is better):")
print(row_fmt.format(*header))
print(sep)
for det, scores in results.items():
    row = [det] + [f"{scores.get(col, 'N/A'):.4f}" if isinstance(scores.get(col), float) else "N/A"
                 for col in ood_variants.keys()]
    print(row_fmt.format(*row))
