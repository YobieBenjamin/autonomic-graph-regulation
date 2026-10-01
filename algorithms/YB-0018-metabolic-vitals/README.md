# YB-0018 · Metabolic vitals: can pure physics (GPU power) reveal a transformer's distress?

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F18: the substrate entropy included answer tokens; Proposition 2 is RETRACTED. Re-windowing open.

**Status:** tested · **Verdict:** ❌ negative. GPU/CPU power carries no failure signal (AUROC 0.40, CI 0.26–0.56); timing none either; reasoning-phase substrate signals do (0.75). Transformers have no metabolism.
**Reproduce:** `make` in this folder (sandbox: `sandbox/run.sh algorithms/YB-0018-metabolic-vitals all`).

## 1. Plain English
In a body, stress changes metabolism: heart rate, breathing and energy use rise. We asked whether a transformer is the same: when it is about to get an answer wrong, does the GPU work harder? We measured the Mac's GPU and CPU power about eight times a second while the patient model answered 240 machine-graded questions.

It does not. The GPU drew the same power whether the answer turned out right or wrong (11.0 W versus 10.1 W on average), and power-based signals did no better than a coin flip. The reason is structural: a transformer runs its entire network for every token, at the same cost, whether the token is easy or agonizing. Unlike an organ, it has no metabolism that responds to its state. Its internal reasoning signals, measured in the same run, still worked (0.75).

For the on-GPU biobrain product this is decisive: coupling a regulator to power rails, thermals or clocks will not work. The biobrain die needs a telemetry port into the accelerator's activations and logits.

## 2. Theory
Independence Principle, tier 0 (physical/metabolic): the most independent signals, because a transformer cannot narrate or fake physics. YB-0015 found token timing weak; this experiment tests true power. Pre-registered before analysis: **P1** GPU power/energy features predict wrong answers within question type (95% CI lower bound > 0.5); **P2** they add beyond timing features.

## 3. Mathematics and proofs
Power samples (t_i, P_i), about every 117 ms, stamped on the same monotonic clock as the tokens and taken within the episode window.
**Energy (trapezoid rule).** E = Σ_i ½(P_i + P_{i−1})(t_i − t_{i−1}); mean power E/(t_n − t_1); peak max P_i; power RMSSD √(Σ(P_i − P_{i−1})²/(n−1)); energy per token E/n_tokens; GPU/CPU power ratio.
**Proposition 1 (exactness).** The trapezoid rule is exact for piecewise-linear power: a constant 15 W over 2 s gives exactly 30 J; a ramp P(t) = 10t W on [0, 1] s gives exactly 5 J. *Proof:* the trapezoid rule integrates linear functions exactly on each interval. ∎ Both verified by tests, with the C core equal to an independent NumPy implementation.
**Proposition 2 (why no signal is expected, structural argument).** In a fixed-architecture transformer each generated token executes the same layers with the same tensor shapes (for this mixture-of-experts model, a fixed number of active experts per token), so the work per token W is constant up to context-length effects. Energy is then E ≈ W·n_tokens·e_op, a function of length, which within-question-type normalization removes. This is an argument, not a theorem: it assumes no data-dependent compute (no early exit, no adaptive depth); the experiment tests it empirically.
**Protocol.** Answered episodes with at least two power samples; within-question-type z-scoring (YB-0015, Proposition 2); out-of-fold logistic regression (stratified folds, seed 0); bootstrap 95% CIs (1000, seed 0).

## 4. Code map
| File | Role |
|---|---|
| src/metabolic.c | Compiled core: energy (trapezoid), mean/peak power, power RMSSD, duration |
| src/metab.py | ctypes binding, NumPy reference, metabolic/timing/substrate episode features |
| tests/test_core.py | 4 tests: C = reference, constant-power energy, linear-ramp exactness, short traces |
| tests/experiment.py | Pre-registered experiment; writes docs/results.json |
| data/episodes_power.jsonl.gz | 240 episodes with aligned power (agr/recorder.py --power, agr/power.py) |
| ../../agr/power.py | powermetrics streaming sampler (one scoped sudo rule; see agr/README.md) |

## 5. Repeatable proof
Data fingerprint: SHA-256 of data/episodes_power.jsonl.gz begins **d50cfdf3c9a4e10c**. `make` rebuilds, runs the tests and regenerates docs/results.json identically from the data. Re-recording: `agr/recorder.py 40 800 --power` (power and timing are physical, so they reproduce statistically, not bit for bit).

## 6. Results (215 answered episodes with power, 16 wrong; within question type)
| Features | AUROC [95% CI] |
|---|---|
| Metabolic (GPU/CPU power, energy, energy per token, variability) | 0.403 [0.265, 0.560] |
| Timing (latency mean, std, RMSSD, effort, wall) | 0.495 [0.304, 0.677] |
| Substrate (entropy mean, max, std) | **0.748** [0.602, 0.873] |
| Metabolic + timing | 0.435 [0.279, 0.595] |
| All three | 0.595 [0.386, 0.776] |

Mean GPU power: 11.01 W on correct answers, 10.09 W on wrong answers.

## 7. Verdict
- **P1 fails:** metabolic features do not predict failure (CI includes 0.5; point estimate below chance).
- **P2 fails:** metabolic + timing does not beat timing.
- **Adding weak signals hurts:** all three (0.595) is worse than substrate alone (0.748), so only validated channels should enter the organism.
- **Design consequence:** tier 0 is uninformative for fixed-compute transformers. The organism's senses must come from reasoning-phase substrate signals, and a hardware biobrain needs an activation/logit telemetry port, not power sensing. Tier 0 may revive for adaptive-compute models (early exit, variable depth): a future hypothesis.

## 8. Limitations and prior art
16 failures (wide intervals); 240 episodes; power sampled about every 117 ms, so short episodes have few samples; one patient model on one machine. Prior art: energy and power profiling of ML inference; hardware performance counters as side channels. The new element is testing metabolic signals as safety vitals under the Independence Principle, with a structural explanation of the null result.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
