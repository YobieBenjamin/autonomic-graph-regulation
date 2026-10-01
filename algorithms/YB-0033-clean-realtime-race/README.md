# YB-0033 · Clean real-time race: the organism warns before the answer, and beats both the AI judge and a length control

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F4 (telemetry one token late), F5 (never-answered episodes excluded), F8 (false alarms 10.12% > 10%), F9, F10 (intervals ignored threshold uncertainty), F7 (wording). All fixed and re-run in YB-0035, which confirmed the result: primary criterion met under the corrected protocol.

**Status:** tested · **EUREKA: true (pre-registered, commit 300f037, fresh seed 5), confirmed robust at exactly equal false-alarm rates.** With every source of future information removed, the text-blind organism caught 28 of 44 wrong answers before the answer was emitted, vs 13 for a 120-billion-parameter LLM judge and 17 for a monitor that knows only how long the reasoning has run. H1 ✅ and H3 ✅; H2 ❌ (the transparent AI-EWS v4 does not beat the length control).
**Reproduce:** `SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0033-clean-realtime-race all`; robustness check: `PYTHONPATH=.:src python3 tests/exploratory_equal_fpr.py` in the sandbox.

## 1. Plain English
The question since YB-0012: can an external 'nervous system' that reads a transformer's internal vital signs, never its words, warn about a wrong answer before the model gives it, better than watching the model's behavior? Every earlier attempt either lost or had a flaw we found ourselves. The last one, YB-0032, quietly let the monitor know how long the model would think, and length alone predicts mistakes.

So this test removed every trace of the future. The monitor looks only at moments a real chip would know (after 48, 96, 192 and 384 words of reasoning, and only if the model is still thinking), and it competes against two opponents: an AI judge six times larger than the model, reading the reasoning so far, and a 'length monitor' that simply raises the alarm when the model has been thinking a long time. Every warning counts only if it arrives, compute time included, before the answer comes out. Everyone gets the same false-alarm budget.

On 538 fresh questions no analysis had ever touched, the organism caught 28 of the 44 wrong answers in time. The AI judge caught 13; the length monitor caught 17. Checked again with every monitor held to exactly the same false-alarm rate, the organism still won: 26 vs 13 and 26 vs 17. At each fixed moment, when every monitor sees a model that is still thinking, the organism's vital signs tell right from wrong far better than the judge reading the words. It needs about 4 milliseconds per check; the judge needs about 2 seconds.

This is the first pre-registered, leak-free result where reading the transformer's physiology beats watching its behavior. It is one model and one kind of task, and it must be replicated.

## 2. Theory
Author's thesis: output is gospel; judgment must be modeled on biology; safety should follow hospital early-warning systems built on serial observations. The Independence Principle: an external, text-blind regulator. YB-0032 showed serial (NEWS2-style) training moves the organism's accuracy earlier; YB-0033 tests it under real-time-knowable information only.

## 3. Mathematics and proofs
**Checkpoints.** T = {48, 96, 192, 384}; checkpoint t exists for an episode iff t < answer start. **Features** x(r, t) = [deep features of tokens < t (YB-0019), log t]; normalization per (question type, t) from derivation data; one L2 logistic model (C = 0.1). **Controls:** C1(t) = t; C2(t) = derivation percentile of t among same-type episodes. **Race:** in-time score m_i = max over checkpoints with t_clock(t) + compute ≤ answer time; threshold: at most 10% of correct test episodes alarmed.
**Proposition 1 (no dependence on the future).** x(r, t) is a function of tokens < t and t only; in particular, for two episodes with identical first t tokens and different total lengths, x is identical. *Proof:* deep features read only the first t rows of the layer tensor (prefix lemma, YB-0019) and log t does not involve the total length; no normalization uses the total length. ∎ Tested (t_features_independent_of_total_length, t_no_look_ahead).
**Proposition 2 (length control is uninformative within a checkpoint).** At a fixed t every still-reasoning episode has C1 = t, so C1's within-checkpoint AUROC is exactly 1/2; any within-checkpoint discrimination by the organism is not attributable to elapsed length. *Proof:* a constant score gives AUROC 1/2. ∎ Observed: 0.500 at every checkpoint.
**Proposition 3 (parallel = serial).** Tested.
Statistics: paired bootstrap over wrong episodes (1000, seed 0).

## 4. Code map
| File | Role |
|---|---|
| src/absrace.py | Checkpoints, real-time features, parallel pool, AbsOrganism, AbsAIEWS (per-checkpoint bands), LengthControls |
| src/aiews.py, src/deep.py, src/layergraph.c, src/hpa.*, shared cores | AI-EWS vitals and deep layer-graph features |
| tests/test_core.py | 5 tests: checkpoints only while reasoning, independence of total length, no look-ahead, parallel = serial, length controls |
| tests/experiment.py | The pre-registered analysis (DRY_RUN never reads seed 5) |
| tests/exploratory_equal_fpr.py | Robustness at exactly equal false-alarm rates |
| ../../agr/prefix_monitors.py (CKPT=abs) | Judge and self-consistency at absolute checkpoints, measured compute, run alone |

## 5. Repeatable proof
The commands above regenerate docs/results.json and docs/exploratory_equal_fpr.json from data/ (deterministic features, fixed seeds). Recordings are token-reproducible (greedy); latencies and monitor compute times are physical measurements on this machine.
Data fingerprints (SHA-256 prefix): layers_seed2_0.npz 6b241b7133cefde7; layers_seed2_1.npz 106a41cfe3544508; layers_seed2_2.npz 8fbf5acfa88df464; layers_seed2_3.npz 40df3794a0f0225d; layers_seed2_4.npz f22b41d2bb328028; layers_seed2_5.npz 95966943c68a619a; layers_seed3_0.npz 9f0aeb8621ba5ef9; layers_seed4_0.npz 4b098cd008d84d33; layers_seed5_0.npz 97aa62d76ee7f44d; prefix_judge_abs_s5.jsonl.gz ef6258725cb91d15; prefix_selfcons_abs_s5.jsonl.gz 4ca13718f6c380f1; seed2_L.jsonl.gz 51802ba63f25bc92; seed3_L.jsonl.gz 173b29eef25be3fb; seed4_L.jsonl.gz 26984bd801f3e2b8; seed5_L.jsonl.gz c901f56c8564343c; 

## 6. Results (derivation seeds 2-4: 5,367 answered, 402 wrong, 9,258 real-time observations; test seed 5: 538 answered, 44 wrong)
| Monitor | Caught in time | False alarms | Seconds to spare | Compute per check |
|---|---|---|---|---|
| **Organism** | **28/44 (63.6%)** | 10.1% | 2.71 | 4.1 ms |
| Length control C1 (still reasoning at t) | 17/44 (38.6%) | 6.7% | 2.14 | ~0 |
| AI-EWS v4 | 15/44 (34.1%) | 8.1% | 3.01 | 2.6 ms |
| LLM judge on prefix | 13/44 (29.5%) | 7.7% | 5.71 | 1.98 s |
| Length control C2 (type percentile) | 6/44 (13.6%) | 4.9% | 1.12 | ~0 |
| Self-consistency on prefix | 0/44 | 0.8% | — | 5.37 s |

H1: organism minus judge +0.341 [+0.114, +0.523]; organism minus length C1 +0.250 [+0.068, +0.455] → **holds (EUREKA)**. H2: AI-EWS v4 minus C1 −0.045 [−0.250, +0.159] → fails. H3 (types where length has no derivation signal: modpow, mul_easy, mul_hard, weekday; 40 errors): organism minus judge +0.350 [+0.125, +0.575] → holds.
**Robustness (exploratory): exactly equal false-alarm rates.** At the judge's 7.69%: organism 26 vs judge 13, +0.295 [+0.091, +0.500]. At the length control's 6.68%: organism 26 vs C1 17, +0.205 [+0.023, +0.409].
Within-checkpoint AUROC (t = 48/96/192/384; errors/episodes 44/345, 44/297, 36/228, 17/50): organism 0.733/0.765/0.786/0.693; judge 0.636/0.623/0.733/0.668; self-consistency 0.713/0.719/0.714/0.513; AI-EWS v4 0.511/0.655/0.697/0.666; C1 0.500 at every t.
Silent slips caught in time: organism 40%, judge 60%, C1 55%, AI-EWS v4 15%.

## 7. Verdict
**EUREKA per the pre-registered criterion, and robust:** on fresh data, with no future information, compute time counted and false alarms matched (and then exactly equalized), the text-blind organism raises in-time warnings on about twice as many wrong answers as a 6x larger LLM judge, and significantly more than a length-only monitor, at about 500x less compute per check. At every fixed checkpoint its discrimination exceeds the judge's and cannot come from elapsed length (Proposition 2).
Not supported: the transparent AI-EWS v4 (H2). Weakness: on silent slips the organism's in-time recall (40%) trails the judge and the length control.

## 8. Limitations
One patient model (gpt-oss-20b) and one family of machine-gradable tasks; 44 test errors (the lower CI bound vs the length control is +0.02 at equal FPR); timings from one Mac (a faster judge would do better); the equal-FPR analysis is exploratory. Required next: replication on a fresh seed and **external validation on a different model** (a different 'patient population'), then non-verifiable agentic tasks (YB-0022).

## Deviations from the pre-registration
None in the analysis. The equal-false-alarm robustness check was added after seeing results and is labeled exploratory.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
