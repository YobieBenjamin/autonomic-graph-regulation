# YB-0017 · HPA-axis organism: an external, text-blind stress regulator

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F19: 'variance 9-10x lower' is a coefficient-of-variation ratio (about 3.7x above resting level) and the drive correlates with length; F20: 290 ns/token is the HPA regulator only (the competing regulators cost 2-4 ms per check); F34: wording.

**Status:** tested · **Verdict:** theorems T1–T3 ✅ proved and confirmed; author's trend prediction ✅ confirmed (rho 0.75 and 0.92; variance 9–10× lower); discrimination ⚠️ lower than raw signals (the price of stability).
**Reproduce:** `make` in this folder (sandbox: `sandbox/run.sh algorithms/YB-0017-hpa-axis-organism all`).

## 1. Plain English
The body does not react to every flicker of danger. The hypothalamus, pituitary and adrenal glands (the HPA axis) form a chain: a stress signal releases CRH, CRH releases ACTH, ACTH releases cortisol, and cortisol slowly builds up and then switches the first two off (negative feedback). That makes the stress response graded, stable and self-limiting.

We built that chain as a small mathematical organism outside any transformer. It never reads text; it receives only numbers (the patient model's vital signs) and outputs a cortisol level. We proved it can never go negative, can never run away to infinity, and always settles to one resting level under steady stress. Then we fed it the vital signs of the 428 answered episodes from YB-0015.

- **The author's prediction held.** The organism's cortisol and the raw signals trend together (rank correlation 0.75 for uncertainty, 0.92 for timing, above the predicted 0.7), while the organism's output varies 9–10 times less. Same trend, far calmer response.
- **The cost:** that calm makes it slightly worse at telling right from wrong than the raw signal (0.70 vs 0.80 for uncertainty). Biology solves this with two systems: a fast nervous reflex and the slow hormonal HPA axis. The next organism needs both (YB-0020).

## 2. Theory
Independence Principle: the regulator is external, deterministic, text-blind, and inspectable (C). It implements allostatic regulation: stress drive enters, a slow integrator with negative feedback exits. Pre-registered (author's prediction): organism and raw signals differ in variance but trend together, Spearman rho > 0.7.

## 3. Mathematics and proofs
State x = (H, A, C) ≥ 0 (CRH, ACTH, cortisol); stress drive S(t) ≥ 0; feedback f(C) = 1/(1 + (C/K_i)^n) ∈ (0, 1].

  dH/dt = b + k1·S·f(C) − w1·H,   dA/dt = k2·H·f(C) − w2·A,   dC/dt = k3·A − w3·C,   with b, k_i, w_i, K_i, n > 0.

**T1 (positivity).** If x(0) ≥ 0 then x(t) ≥ 0 for all t. *Proof:* on each face of the nonnegative orthant the field points inward: at H = 0, dH/dt = b + k1·S·f ≥ b > 0; at A = 0, dA/dt = k2·H·f ≥ 0; at C = 0, dC/dt = k3·A ≥ 0. So no trajectory can leave. ∎
**T2 (boundedness).** If S(t) ≤ S_max then H ≤ H̄ = (b + k1·S_max)/w1, A ≤ Ā = k2·H̄/w2, C ≤ C̄ = k3·Ā/w3, whenever the state starts inside this box. *Proof:* since f ≤ 1, dH/dt ≤ b + k1·S_max − w1·H, which is negative for H > H̄, so H cannot cross H̄; given H ≤ H̄, dA/dt ≤ k2·H̄ − w2·A, same argument for Ā; then C likewise. ∎ No input sequence, however adversarial, can drive the organism to infinity.
**T3 (unique resting level).** For constant S ≥ 0 there is exactly one equilibrium. *Proof:* setting derivatives to zero gives H* = (b + k1·S·f)/w1, A* = k2·H*·f/w2, and w3·C* = (k3·k2/(w1·w2))·f(C*)·(b + k1·S·f(C*)). The left side increases strictly from 0; the right side is positive and strictly decreasing in C* (f is decreasing). They cross exactly once. ∎
**T4 (feedback desensitization, numerical).** After chronic stress, the CRH response to a new pulse is smaller than from rest, because elevated C lowers the input gain k1·f(C). Confirmed by test; it is a realistic property and also a failure mode to watch (chronic stress can blunt alarms).
**Conjecture (stability).** With the default rates the equilibrium is stable and the loop does not oscillate. Supported numerically: late-time cortisol variation is 0 for feedback steepness n = 1, 2, 4, 8, 16, 32 under constant drive. (Goodwin-type loops can oscillate at very high n with near-equal rates; not observed here.)
**Numerics.** RK4, 4 substeps per token, 2000-step burn-in to the S = 0 resting state. Default parameters: b = 0.1, k1 = k2 = k3 = 1, w1 = 0.5, w2 = 0.3, w3 = 0.05 (slow cortisol), K_i = 1, n = 2.
**Stress drive.** S_t = max(0, (x_t − median)/IQR) for a vital channel x, with median and IQR fit only on correct calibration episodes (2-fold split by episode index; no leakage).

## 4. Code map
| File | Role |
|---|---|
| src/hpa.c | Compiled core: RK4 integration of the three-node graph ODE |
| src/hpa.py | ctypes binding, independent Python RK4 reference, analytic bounds (T2) |
| tests/test_core.py | 5 tests: C = reference, T1, T2 (constant, square-wave, random adversarial input), T3 from different histories, T4 |
| tests/experiment.py | Pre-registered experiment on YB-0015's recorded vitals; writes docs/results.json |
| data/episodes.jsonl.gz | Same 480 episodes as YB-0015 (SHA-256 begins a5b60ae4691a635c) |

## 5. Repeatable proof
T1–T3 are proved above and checked numerically by `make test` (C equals the independent reference to 1e-9). `make` regenerates docs/results.json identically from the data file (deterministic ODE, fixed calibration split, bootstrap seed 0).

## 6. Results (428 answered episodes, 36 wrong; AUROC without question-type control)
| Stress channel | Organism peak cortisol | Organism final cortisol | Raw accumulated drive | Spearman rho (organism vs raw) | Variation (CV) organism / raw |
|---|---|---|---|---|---|
| Tier 2 entropy | 0.703 [0.632, 0.774] | 0.703 [0.628, 0.777] | 0.799 [0.737, 0.858] | **0.751** | 0.112 / 1.140 |
| Tier 0 latency | 0.649 [0.547, 0.748] | 0.622 [0.510, 0.719] | 0.700 [0.604, 0.798] | **0.922** | 0.265 / 2.405 |

Alarm bands (entropy drive; thresholds at the 50th, 90th and 99th percentile of correct episodes): 9 of 36 failures (25%) above the 90th percentile, versus 40 of 392 correct (10%).

## 7. Verdict
- **Author's trend prediction: confirmed** for both channels (rho 0.751 and 0.922 > 0.7), with 9–10× lower variance: same direction, calmer response.
- **Safety properties: proved** (positivity, boundedness under any input, unique resting level).
- **Discrimination: lower than raw** (−0.10 AUROC on entropy). Slow integration trades sensitivity for stability. Design consequence: pair the slow HPA path with a fast reflex path (YB-0020), as the body pairs hormones with the sympathetic nervous system.

## 8. Limitations and prior art
Parameters are defaults, not fitted (deliberately, to avoid overfitting 36 failures); AUROC here is not question-type controlled; one patient model and task family. Prior art: minimal HPA-axis models (e.g., Gupta et al., 2007; Vinther et al., 2011), Goodwin oscillator theory, allostasis (Sterling). The new element is an HPA-type ODE used as an external, text-blind regulator of a transformer's vital signs.

## Addendum: real-time budget (measured 2026-09-28)
The organism costs **290 ns per token** (RK4, 4 substeps, one CPU core, software). The patient's token interval is 12.28 ms median and 8.11 ms at the fastest 1%: about **28,000x headroom**. Real-time regulation is not compute-bound; the engineering constraint for an on-accelerator biobrain is telemetry access (activations and logits every token), not the regulator itself.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
