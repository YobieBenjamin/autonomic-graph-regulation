# YB-0002 · Bounded Homeostatic Wrapper (BHW)

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F22: detection comparisons were at unmatched false-positive rates; F33: theorem wording. Claims are qualified until a matched comparison is run (open).

**Status:** tested · **Verdict:** ✅ theorems proven and confirmed; ✅ works on a 1-D detector; ⚠️ closed-form budget calibration fails in 64-D (open problem → YB-0007)
**Run:** `make` (compiles C core, 5 theorem/correctness tests, full evaluation → `docs/results.json`)

## 1. Plain English

Any AI monitor that "learns what normal looks like" has to keep re-learning, because normal changes. But a monitor that re-learns without limits can be walked, one tiny step at a time, into believing anything is normal. We showed how bad this is: an attacker who knows the monitor can drag its idea of normal thousands of units away, and **not one input ever gets flagged**.

BHW is the fix, borrowed from biology. Living systems re-calibrate constantly (homeostasis), but only inside hard limits; a body temperature set point can drift a little, never forty degrees. BHW lets any monitor adapt, but puts a hard cap on how far its "normal" can ever move from the original trusted version. Hit the cap and it sounds a DRIFT alarm and stops adapting.

The cap comes with a mathematical guarantee: no matter how clever the attacker or how long they try, the monitor's normal can never move more than the cap plus one small step, and nothing it accepts can ever be further than a fixed distance from the original trusted behavior. We also derived a formula for how big to make the cap so it doesn't false-alarm on honest data. That formula works for simple (1-dimensional) monitors, and fails for complex (64-dimensional) ones with little calibration data. That failure is recorded as an open problem.

## 2. Technical summary

BHW wraps any detector whose score is a Mahalanobis distance of a feature vector s(x) ∈ ℝᵖ from a baseline mean μ. The baseline follows a **gated EWMA** (updates only on accepted inputs); its displacement from the anchored trusted mean μ₀ is capped by a **budget B**; exceeding B raises DRIFT and freezes adaptation. It is detector-agnostic: tested wrapping Energy (p = 1) and activation-Mahalanobis (p = 64). The streaming loop runs in C.

## 3. Mathematics

Notation: ‖v‖_P = √(vᵀPv), P = Σ̂⁻¹ (shrinkage-regularized). Threshold τ, rate η ∈ (0,1), budget B.

**Update.** d_t = ‖s_t − μ_t‖_P. If d_t ≤ τ and not frozen: μ_{t+1} = μ_t + η(s_t − μ_t); then if ‖μ_{t+1} − μ₀‖_P > B, freeze.

**Lemma (per-step speed limit).** For an accepted step, ‖μ_{t+1} − μ_t‖_P = η‖s_t − μ_t‖_P ≤ ητ. *Proof:* direct from the update and d_t ≤ τ. ∎

**T1 (baseline confinement).** sup_t ‖μ_t − μ₀‖_P ≤ B + ητ, for every input sequence, of any length. *Proof:* before freezing, ‖μ_t − μ₀‖_P ≤ B (else it would have frozen). The one step that crosses B adds at most ητ by the lemma and the triangle inequality. After freezing μ is constant. ∎

**T2 (acceptance confinement).** Every accepted input satisfies ‖s − μ₀‖_P ≤ τ + B + ητ. *Proof:* ‖s − μ₀‖ ≤ ‖s − μ_t‖ + ‖μ_t − μ₀‖ ≤ τ + (B + ητ) by T1. ∎ Without the budget, the acceptance region's radius grows as τ + tητ, **unboundedly**: this is the formal statement of the boiling-frog attack.

**T3 (minimum attack time).** Any input sequence moving the baseline past B needs at least ⌈B/(ητ)⌉ accepted steps, and the attacker who achieves this bound (inputs at c·τ along a fixed direction, c → 1) triggers DRIFT at step ⌈B/(ηcτ)⌉. *Proof:* the lemma plus a telescoping sum; for the colinear attacker, the displacement grows by exactly ηcτ per step. ∎

**C1 (budget calibration, stationary).** If clean s_t are i.i.d. with mean μ₀ and covariance Σ, the EWMA error has stationary covariance η/(2−η)·Σ, so D² = ‖μ − μ₀‖²_P ≈ η/(2−η)·χ²_p. Set B = √(η/(2−η)·χ²_p⁻¹(q)) for per-step exceedance ≈ 1 − q. (Gating truncates accepted inputs at τ, which makes this conservative.)

**C2 (finite-sample correction).** μ₀ is estimated from n points, so the true clean mean is ≈ √(χ²_p⁻¹(q)/n) away in P-norm. Use B_C2 = B_C1 + √(χ²_p⁻¹(q)/n), and fit (μ₀, P) and τ on disjoint halves of the calibration data. C1 and C2 are approximations, labelled as such and tested empirically below; T1–T3 are exact.

## 4. Code map

| File | What |
|---|---|
| `src/bhw.c` | Compiled streaming core: score, gate, EWMA, budget, freeze; static / unbounded / budgeted modes |
| `src/bhw.py` | ctypes binding; `BHW.fit` (incl. split calibration), `BHW.run`, pure-Python `run_reference`; `budget_rule` (C1/C2); `worst_case_attack` (optimal adaptive adversary) |
| `src/mlp.py` | Same numpy MLP as YB-0001 (test subject) |
| `tests/test_core.py` | C ≡ Python reference; T1 and T2 under worst-case attack at η ∈ {0.01, 0.05, 0.2}; T3 alarm step; unbounded mode is unbounded; C1 closed form |
| `tests/experiment.py` | Energy and activation-Mahalanobis × {static, unbounded, budgeted} × {C1, C2}, 10 seeds; worst-case attack; calibration check |

```python
from bhw import BHW
mon = BHW(eta=0.02, split=True).fit(trusted_features)      # B set by rule, not tuned
out = mon.run(stream_features, "budgeted")                  # out["flag"], out["frozen"] (DRIFT), out["drift"]
```

## 5. Results (digits 0–4 MLP, η = 0.02, stream morphs 0–4 → 5–9 over 2000 steps, 10 seeds)

**Worst-case adaptive attacker, 20,000 steps** (baseline displacement, Mahalanobis units):

| Detector / calibration | Unbounded | Budgeted | Bound T1 | Alarm step (pred.) | Inputs flagged |
|---|---|---|---|---|---|
| Energy, C1 | 767.6 | 0.345 | 0.370 | 9 (8.6) | 0 |
| Act-Maha, C1 | 3560.1 | 1.068 | 1.208 | 6 (5.8) | 0 |
| Energy, C2 | 785.5 | 0.668 | 0.681 | 17 (16.3) | 0 |
| Act-Maha, C2 | 5953.8 | 2.084 | 2.296 | 7 (6.7) | 0 |

**Slow natural drift** (flag rate on the fully-shifted final 500 steps; DRIFT detection; false DRIFT alarms on clean streams):

| Detector / calibration | Static | Unbounded | Budgeted | Detected (at % of shift) | Clean false alarms | Budget exceedance (pred. 0.1%) |
|---|---|---|---|---|---|---|
| Energy, C1 | 68.2% | **1.2%** | 54.5% | 10/10 (12%) | 2/10 | 0.19% |
| Energy, C2 | 70.5% | **1.1%** | 43.0% | 10/10 (18%) | **0/10** | 0.00% |
| Act-Maha, C1 | 79.4% | 66.8% | 80.2% | 10/10 (0%) | 10/10 ❌ | 82.9% |
| Act-Maha, C2 | 23.4% | 15.3% | 23.3% | 10/10 (14%) | 10/10 ❌ | 1.43% |

## 6. Interpretation and honest limitations

- **Proven and confirmed:** T1–T3 held exactly in every configuration and test. Unbounded adaptation is catastrophically exploitable: thousands of units of drift, zero flags.
- **Working configuration:** Energy + BHW + C2 reverses the collapse (1.1% → 43% detection) with 0/10 false alarms and early detection. The cost is some detection power versus a never-adapting monitor (70.5%), which is the price of tolerating benign change.
- **Failure:** in 64-D with n ≈ 112 per calibration half, C1/C2 underestimate clean drift by 14× or more, so the budget trips on honest data. Cause: covariance estimation error inflates ‖·‖_P distances in ways the χ² model ignores. Also, split calibration halves the data, which hurts the 64-D static detector (79% → 23%). Next step: YB-0007 (empirical/bootstrap budget calibration and low-rank features).
- Scale: toy MLP, 8×8 digits, 10 seeds; the adversary is feature-space (it chooses feature vectors directly), which is the strongest threat model, not an input-space attack.
- **Prior art:** EWMA / MEWMA control charts (Roberts 1959; Lowry et al. 1992) give the C1 variance; adaptive-threshold drift detectors (ADWIN, Bifet & Gavaldà 2007) and poisoning of online anomaly detectors (Kloft & Laskov 2010, who studied exactly this centroid-dragging attack) are closely related. The contribution here is the gating-plus-hard-cap wrapper, the T1–T3 confinement guarantees against that attack, and the empirical demonstration on neural-network OOD detectors. A systematic literature search has not yet been done.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
