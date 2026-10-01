# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""YB-0001 empirical evaluation. Deterministic; prints a results table + JSON.
Train MLP on digits 0-4 (sklearn 8x8). Detect: near-OOD (digits 5-9),
far-OOD (uniform noise), adversarial (FGSM on held-out 0-4).
Compare H2CM against MSP, energy, and activation-Mahalanobis baselines."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from sklearn.datasets import load_digits
from sklearn.metrics import roc_auc_score
from mlp import MLP
from h2cm import H2CM, signature

SEED = 0
r = np.random.default_rng(SEED)
X, y = load_digits(return_X_y=True); X = X / 16.0
idx = r.permutation(len(X)); X, y = X[idx], y[idx]
ind = y < 5
Xi, yi, Xo = X[ind], y[ind], X[~ind]
n = len(Xi); Xtr, ytr = Xi[: n//2], yi[: n//2]
Xcal = Xi[n//2: 3*n//4]; Xte, yte = Xi[3*n//4:], yi[3*n//4:]

net = MLP(64, 32, 32, 5, seed=SEED); net.train(Xtr, ytr)
acc = (net.predict(Xte) == yte).mean()

def feats(Xs, rich=True):
    _, a1, _, a2, lo = net.forward(Xs)
    sig = np.array([signature([net.p["W2"], net.p["W3"]], [a1[i], a2[i]], rich=rich) for i in range(len(Xs))])
    return sig, np.hstack([a1, a2]), lo

def maha_fit(F):
    mu = F.mean(0); S = np.cov(F.T); S += 1e-3*np.trace(S)/len(S)*np.eye(len(S))
    P = np.linalg.inv(S); return lambda G: np.sqrt(np.einsum("ij,jk,ik->i", G-mu, P, G-mu))

sc, ac, _ = feats(Xcal)
sc1, _, _ = feats(Xcal, rich=False)
mon = H2CM().fit(sc); mon1 = H2CM().fit(sc1); act_m = maha_fit(ac)
def scores(Xs):
    s, a, lo = feats(Xs)
    p = MLP.softmax(lo)
    s1, _, _ = feats(Xs, rich=False)
    h = np.array([mon.score(v) for v in s]); am = act_m(a)
    h1 = np.array([mon1.score(v) for v in s1])
    zh = (h - h_ref[0]) / h_ref[1]; za = (am - a_ref[0]) / a_ref[1]
    return {"MSP": -p.max(1), "Energy": -np.log(np.exp(lo).sum(1)),
            "Act-Mahalanobis": am, "H2CM v1 shape-only": h1, "H2CM v2 (ours)": h, "H2CM + Act-Maha (z-sum)": zh + za}
hc = np.array([mon.score(v) for v in sc]); h_ref = (hc.mean(), hc.std())
amc = act_m(ac); a_ref = (amc.mean(), amc.std())

S_in = scores(Xte)
sets = {"near-OOD (digits 5-9)": Xo[:len(Xte)],
        "far-OOD (noise)": r.uniform(0, 1, Xte.shape),
        "FGSM eps=0.1": net.fgsm(Xte, yte, 0.10),
        "FGSM eps=0.2": net.fgsm(Xte, yte, 0.20)}
res = {"test_acc_in_dist": float(acc), "auroc": {}}
for name, Xs in sets.items():
    S_out = scores(Xs)
    res["auroc"][name] = {k: float(roc_auc_score(np.r_[np.zeros(len(S_in[k])), np.ones(len(S_out[k]))],
                                                 np.r_[S_in[k], S_out[k]])) for k in S_in}

# ---- Drift ("boiling frog") experiment: stream slides from 0-4 to 5-9 ----
T = 3000; alpha = np.clip((np.arange(T) - 500) / 2000, 0, 1)
a_idx = r.integers(0, len(Xte), T); b_idx = r.integers(0, len(Xo), T)
stream = (1 - alpha)[:, None] * Xte[a_idx] + alpha[:, None] * Xo[b_idx]
ss, _, _ = feats(stream)
drift = {}
for mode, kw in {"static": dict(adapt=False), "homeostatic-unbounded": dict(budgeted=False),
                 "homeostatic-budgeted (ours)": dict(budgeted=True)}.items():
    m = H2CM(eta=0.02, drift_budget=1.5).fit(sc); flags = []; alarm_t = None
    for t, s in enumerate(ss):
        f, a = m.step(s, **kw); flags.append(f)
        if a and alarm_t is None: alarm_t = t
    flags = np.array(flags)
    drift[mode] = {"flag_rate_final_500_(fully_OOD)": float(flags[-500:].mean()),
                   "flag_rate_first_500_(clean)": float(flags[:500].mean()),
                   "drift_alarm_step": alarm_t}
res["drift_stream"] = drift

print(f"In-distribution test accuracy: {acc:.3f}\n\nAUROC (higher = better detection)")
keys = list(S_in)
print(f"{'set':24s}" + "".join(f"{k[:22]:>24s}" for k in keys))
for name, row in res["auroc"].items():
    print(f"{name:24s}" + "".join(f"{row[k]:24.3f}" for k in keys))
print("\nSlow-drift stream (alpha ramps 0->1 over steps 500-2500):")
for k, v in drift.items(): print(f"  {k:30s} {v}")
out = os.path.join(os.path.dirname(__file__), "..", "docs", "results.json")
json.dump(res, open(out, "w"), indent=2)

# ---- Control: drift budget on CLEAN streams (false-alarm check), 5 seeds ----
ctrl = {"clean_false_alarms": 0, "drift_detected": 0, "alarm_alpha": [], "seeds": 5}
for sd in range(5):
    rr = np.random.default_rng(100 + sd)
    clean = Xte[rr.integers(0, len(Xte), T)] + rr.normal(0, 0.02, (T, 64))
    cs, _, _ = feats(np.clip(clean, 0, 1))
    m = H2CM(eta=0.02, drift_budget=1.5).fit(sc)
    ctrl["clean_false_alarms"] += int(any(m.step(s)[1] for s in cs))
    a_i = rr.integers(0, len(Xte), T); b_i = rr.integers(0, len(Xo), T)
    ds, _, _ = feats((1 - alpha)[:, None] * Xte[a_i] + alpha[:, None] * Xo[b_i])
    m = H2CM(eta=0.02, drift_budget=1.5).fit(sc)
    for t, s in enumerate(ds):
        if m.step(s)[1]:
            ctrl["drift_detected"] += 1; ctrl["alarm_alpha"].append(round(float(alpha[t]), 3)); break
res["drift_budget_control"] = ctrl
print("\nDrift-budget control over 5 seeds:", ctrl)
json.dump(res, open(out, "w"), indent=2)
