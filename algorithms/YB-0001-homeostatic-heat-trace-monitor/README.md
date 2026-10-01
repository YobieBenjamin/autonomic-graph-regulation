# YB-0001 · Homeostatic Heat-Trace Circuit Monitor (H2CM)

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F32: theorem wording and test coverage to be tightened (open).

**Status:** tested · **Verdict:** split — spectral detector ❌ negative result; homeostatic drift budget ✅ positive result
**Run:** `make` (compiles C core, runs 6 unit tests, runs full evaluation, writes `docs/results.json`)

## 1. Plain English

A brain doesn't just fire neurons; it routes signal along pathways, and the *shape* of that routing changes when something unusual happens (seizures, novelty, stress). This algorithm watches an AI model the same way. For every input it draws a map of which internal units actually passed signal to which others, measures the geometric "shape" of that map, and compares it to what the shape normally looks like. Unusual shape → the model may be operating outside what it was vetted on.

The second idea comes from how living systems stay stable. Your body re-calibrates its "normal" constantly (homeostasis), but only within limits — a thermostat that re-learns "normal" without limits can be walked, one small step at a time, into accepting a fire. Attackers can do exactly this to an AI monitor: feed it slowly-shifting inputs until its idea of normal has drifted to where they want it. H2CM lets its baseline adapt, but caps the *total* distance the baseline may ever move from its original trusted set point. Cross the cap, and it raises an alarm and stops adapting.

**What we found:** the shape-of-routing detector, on its own, was *worse* than simple standard detectors on this test. The drift budget, however, worked: it caught slow poisoning in 5 of 5 trials, with 0 false alarms in 5 clean trials, and we reproduced the danger it guards against (an unlimited self-adapting monitor lost ~45% of its detection power during a slow drift).

## 2. Technical summary

For an MLP with post-activation vectors a₁, a₂ and weights W₂, W₃, build the per-input **effective connectivity graph** G(x) over hidden + output units. Compute the **heat trace** of its normalized Laplacian at 8 log-spaced diffusion times, score its Mahalanobis distance to a calibration baseline, threshold at the calibration 95th percentile. Maintain the baseline mean with a gated EWMA (updates only on accepted inputs) subject to a **drift budget** B on the Mahalanobis displacement of the running mean from the anchored mean μ₀.

## 3. Mathematics

**Effective connectivity.** For layer l with weights W⁽ˡ⁾ ∈ ℝ^{m×k} and input activations a⁽ˡ⁾ ∈ ℝᵏ, the flow on synapse j→i is
  F⁽ˡ⁾ᵢⱼ(x) = |W⁽ˡ⁾ᵢⱼ · a⁽ˡ⁾ⱼ(x)|.
Stacking all layers block-off-diagonally gives directed B(x); set A(x) = B(x) + B(x)ᵀ (symmetric, non-negative).

**Normalized Laplacian.** With degree dᵢ = Σⱼ Aᵢⱼ,
  L = I − D^{−1/2} A D^{−1/2},  spectrum 0 = λ₁ ≤ … ≤ λₙ ≤ 2.
(Isolated nodes — dead ReLUs — get a zero row, eigenvalue 0.)

**Heat trace.** h(t) = Tr(e^{−tL}) = Σₖ e^{−tλₖ}. Properties used as unit tests: h(0) = n; lim_{t→∞} h(t) = number of connected components. Small t probes local structure, large t global connectivity — a multiscale, permutation-invariant fingerprint (the neurons can be relabelled without changing it).

**Signature.** v1: s(x) = [log(h(tᵢ)/n)]ᵢ₌₁..₈, tᵢ ∈ logspace(−1, 1.5). v2 appends log total flow per layer and the Shannon entropy of the node-strength distribution pᵢ = dᵢ/Σd.

**Score.** d(x) = √((s − μ)ᵀ Σ⁻¹ (s − μ)), Σ = Ĉov + ε·(tr Ĉov/p)·I (shrinkage, ε=10⁻³). Flag if d(x) > τ, τ = Q₀.₉₅ of calibration scores.

**Bounded homeostasis.** Anchor μ₀ at calibration. For each unflagged input,
  μ ← μ + η (s − μ),
then if D = √((μ − μ₀)ᵀ Σ⁻¹ (μ − μ₀)) > B, raise DRIFT and freeze μ. Because μ is a convex combination of accepted signatures, an adversary can only move it by feeding inputs that are individually accepted; B bounds the cumulative effect of any such sequence regardless of its length — the core safety property. Without B, a drift of rate below roughly η·τ per step is never flagged and the baseline follows it indefinitely.

## 4. Code map

| File | What |
|---|---|
| `src/heattrace.c` | Compiled core: Laplacian build, cyclic Jacobi eigensolver, heat trace (`-Wall -Wextra -Werror` clean) |
| `src/h2cm.py` | ctypes binding, `effective_connectivity`, `signature`, `H2CM` monitor (`fit`, `score`, `step`, `drift`) |
| `src/mlp.py` | Dependency-free numpy MLP with Adam and FGSM, used as the test subject |
| `tests/test_core.py` | 6 tests: vs numpy `eigvalsh`, spectral bounds, h(0)=n, component counting, K₄ closed form, drift freeze |
| `tests/experiment.py` | OOD + adversarial AUROC vs baselines, slow-drift stream, 5-seed control |

Usage:
```python
from h2cm import H2CM, signature
mon = H2CM(drift_budget=1.5).fit([signature([W2, W3], [a1, a2]) for a1, a2 in trusted])
flagged, drift_alarm = mon.step(signature([W2, W3], [a1_new, a2_new]))
```

## 5. Results (sklearn digits, MLP 64-32-32-5 trained on digits 0–4, test acc 1.000)

AUROC, higher is better:

| Set | MSP | Energy | Act-Maha | H2CM v1 | H2CM v2 | H2CM+Act-Maha |
|---|---|---|---|---|---|---|
| near-OOD (5–9) | 0.940 | **0.955** | 0.855 | 0.781 | 0.719 | 0.864 |
| far-OOD (noise) | 0.967 | 0.972 | **1.000** | 0.758 | 0.643 | **1.000** |
| FGSM ε=0.1 | **0.935** | 0.899 | 0.697 | 0.648 | 0.578 | 0.680 |
| FGSM ε=0.2 | 0.848 | 0.826 | **0.890** | 0.648 | 0.632 | 0.862 |

Slow-drift stream (inputs morph 0–4 → 5–9 over 2000 steps), flag rate on the fully-shifted final 500 steps: static 25.6%, unbounded homeostasis **14.2%**, budgeted 15.8% + DRIFT alarm at step 1258. Control over 5 seeds: **0/5** false drift alarms on clean streams; **5/5** drifts detected, at 35–40% of the way through the shift.

## 6. Interpretation and honest limitations

- The heat-trace signature is not competitive as a standalone detector here; adding it to activation-Mahalanobis does not help. The permutation invariance that makes it elegant also discards which units fire — often the most informative thing. Kept as a documented negative result.
- The drift budget is detector-agnostic: it wraps any score with a mean-shifting baseline. It should be re-tested on the strongest baseline (energy / activation-Mahalanobis) and on a transformer — that is hypothesis YB-0002.
- Scale: toy MLP, 8×8 digits, 5 seeds. O(n³) Jacobi per input is fine at n≈70, not at transformer width (would need Lanczos / stochastic trace estimation).
- Prior art: activation-Mahalanobis OOD (Lee et al., 2018), energy scores (Liu et al., 2020), graph heat-kernel signatures (Sun et al., 2009), CUSUM-style change detection. The novel parts are the per-input effective-connectivity graph as the object of monitoring and the bounded-homeostasis framing of anti-poisoning; neither novelty has been checked against a systematic literature search yet.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
