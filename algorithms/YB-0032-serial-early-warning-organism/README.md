# YB-0032 · Serial-observation early-warning organism (the NEWS2 method)

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F21: the length-only control is now reproducible (archive/audit/artifacts/). F4 applies. The eureka flag was not accepted (look-ahead), as stated below.

**Status:** tested · **Pre-registered EUREKA flag: true — NOT ACCEPTED.** A post-hoc validity check found look-ahead leakage in the pre-registered checkpoint design (checkpoints at fractions of the *total* reasoning length reveal that length, which a real-time monitor cannot know). Length alone catches 15/46 errors in time, more than the LLM judge (9/46). The serial organism's 29/46 is about double the length-only control, suggesting real signal beyond length, but this design cannot prove it. Confirmation requires YB-0033 (absolute-time checkpoints, length-only control, fresh seed).
**Reproduce:** `SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0032-serial-early-warning-organism all`; dry run with `DRY_RUN=1`.

## 1. Plain English
Hospitals judge a patient's vitals against what is normal at that stage of care, measured again and again. We trained the organism the same way: on the model's internal vitals at 25%, 50%, 75% and 100% of each reasoning trace (about 19,000 observations), with 'normal' defined per stage. On 600 fresh questions it caught 29 of 46 wrong answers before the answer was emitted, against 9 for a 120-billion-parameter AI judge and 3 for the same organism trained only on finished reasoning, at the same false-alarm rate. That looked like the breakthrough.

Then we checked our own test. To look at '25% of the reasoning', you have to know how long the reasoning will be, which is the future. Wrong answers tend to come with longer reasoning, so a checkpoint placed at 25% quietly tells you the length. Using nothing but that length catches 15 of 46 wrong answers in time. So the headline comparison was contaminated. The organism still doubled the length-only baseline, which is encouraging, but a result a skeptic can explain away is not a eureka. The fix is a clean test with checkpoints at fixed clock times.

## 2. Theory
Clinical early-warning scores are built and validated on serial observations with stage-appropriate reference ranges. The organism trained only on complete reasoning (YB-0031) was accurate at the end but weak early; training on serial observations should transfer that accuracy earlier.

## 3. Mathematics and proofs
Stages c ∈ {0.25, 0.5, 0.75, 1.0}; prefix length k(c) = max(⌊c · final_start⌋, 2). Serial features x(r, c) = [deep features of the prefix (YB-0019), c]. Normalization per (question type, stage) with derivation statistics; one L2 logistic model (C = 0.1) over all derivation observations. AI-EWS v3: v2 vitals with bands per stage from derivation correct episodes, directions learned at stage 1.0. Race and matched false alarms as YB-0031.
**Proposition 1 (no look-ahead in the features).** x(r, c) reads only tokens before k(c) (tested). **Limitation discovered after analysis:** k(c) itself depends on final_start, the total reasoning length, so the checkpoint position leaks future information. Proposition 1 holds for the feature map but not for the checkpoint schedule.
**Proposition 2 (parallel = serial).** The fork-pool feature computation equals the single-process computation exactly (tested).

## 4. Code map
| File | Role |
|---|---|
| src/serial.py | Stages, serial features, parallel feature pool (fork), SerialOrganism, SerialAIEWS |
| src/aiews.py, src/deep.py, src/layergraph.c, src/race.py, shared cores | AI-EWS vitals, deep features, race rules |
| tests/test_core.py | 4 tests: stage indices, no look-ahead in features, stage feature, parallel equals serial |
| tests/experiment.py | Pre-registered analysis (DRY_RUN mode never reads seed 4) |

## 5. Repeatable proof
The command above regenerates docs/results.json from data/ (deterministic features, fixed seeds). The length-only control is reproduced from data/ alone (see section 6).
Data fingerprints (SHA-256 prefix): layers_seed2_0.npz 6b241b7133cefde7; layers_seed2_1.npz 106a41cfe3544508; layers_seed2_2.npz 8fbf5acfa88df464; layers_seed2_3.npz 40df3794a0f0225d; layers_seed2_4.npz f22b41d2bb328028; layers_seed2_5.npz 95966943c68a619a; layers_seed3_0.npz 9f0aeb8621ba5ef9; layers_seed4_0.npz 4b098cd008d84d33; prefix_judge_s3.jsonl.gz 31e76a0fd329c6a0; prefix_judge_s4.jsonl.gz 6fe549ea274cf2a4; prefix_selfcons_s3.jsonl.gz 7854dbfe9eed3714; prefix_selfcons_s4.jsonl.gz 47ba65f44a4a7549; seed2_L.jsonl.gz 51802ba63f25bc92; seed3_L.jsonl.gz 173b29eef25be3fb; seed4_L.jsonl.gz 26984bd801f3e2b8; 

## 6. Results (derivation seeds 2+3: 4,837 answered, 356 wrong, 19,348 serial observations; test seed 4: 530 answered, 46 wrong)
**Race at matched ~10% false alarms (caught before the answer is emitted):** serial organism 29/46 (63.0%, 1.25 s to spare, 2.2 ms per check); AI-EWS v3 24/46 (52.2%); LLM judge on prefixes 9/46 (19.6%, 1.6 s per check); complete-trained reference 3/46 (6.5%); self-consistency on prefixes 0/46.
H1 serial minus judge: +0.435 [+0.239, +0.609] (formally SUPERIOR). H2 serial minus reference: +0.565 [+0.413, +0.717] (holds). H3 AI-EWS v3 levels not ordered at every stage (fails); in-time recall CI [0.39, 0.67]. H4 AUROC at 100%: serial 0.839 vs reference 0.819, diff +0.020 [−0.017, +0.071] (no accuracy cost, holds). H5 silent slips in time: 6/17 (35%), CI [0.18, 0.59] (holds).
Per-stage AUROC (serial / reference): 25% 0.790 / 0.408; 50% 0.839 / 0.707; 75% 0.837 / 0.799; 100% 0.839 / 0.819.
**Post-hoc validity control (not pre-registered):** reasoning length alone (revealed exactly at the first fractional checkpoint): AUROC 0.773, 15/46 caught in time at 10.1% false alarms; within-type length percentile: AUROC 0.578, 11/46. Within-type length AUROC: count 0.60, modpow 0.48, mul_hard 0.55, weekday 0.55.

## 7. Verdict
- **H2 and H4 hold:** serial training transfers the organism's accuracy to partial reasoning (0.41 to 0.79 AUROC at 25%) at no cost at the end. This answers the YB-0031 question: the complete-trained organism's early-warning failure was substantially a training-regime problem.
- **H1 (EUREKA) formally holds but is not accepted:** the fractional checkpoint schedule leaks total reasoning length, and length alone already beats the judge. The organism's margin over the length-only control (29 vs 15) is suggestive, not proven.
- H3 fails; H5 holds.

## 8. Limitations and next step
Checkpoints must be placed at times a real-time monitor can know (absolute tokens or wall-clock), stage features must be tokens-so-far rather than fraction-of-total, and a length-only control must be a pre-registered competitor. This is YB-0033, on a fresh seed.

## Deviations from the pre-registration
None in the analysis. The look-ahead leak is a design flaw in the pre-registration itself, found by a post-hoc control; the EUREKA flag is therefore not accepted.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
