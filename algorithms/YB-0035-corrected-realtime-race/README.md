# YB-0035 · The real-time race re-run under the corrected protocol (independent-audit fixes)

> **Corrections (second audit, 2026-09-30; see CORRECTIONS.md B5, B6, B8-B10, B20, B22):** seed 7 is the only fresh test set and leads; the pooled estimate is descriptive. False alarms among monitorable episodes differ (16.3% regulator, 11.0% judge, 10.3% length); with them equalized the regulator still leads, 19 vs 11 (+0.20 [+0.02, +0.43]), and a threshold frozen from training data gives 22/40 (exploratory, tests/exploratory_audit2.py). A question-type baseline catches 6/40. On finished answers self-consistency was more accurate than an earlier regulator and the judge was not distinguishable from it (YB-0031). No concurrent jobs were logged during the seed-7 recording; the automatic run-alone guard was added afterwards. Resynchronization is verified by agr/verify_shift.py (11/11 identical-text episodes; worst single reading 2.8 SD).

**Status:** tested · **Primary criterion met under the corrected protocol** (pre-registration and full analysis code committed as b6c795b before the seed-7 test data existed). On the fresh seed-7 test set the regulator raised in-time warnings on 23 of 40 wrong answers vs 11 for the LLM judge and 9 for the length control, at <= 10% false alarms; seeds 5 and 6 (re-used test sets, re-synchronized) agree, and their pooled estimate is descriptive only. With false alarms equalized among monitorable episodes the regulator still leads, 19 vs 11 (+0.20 [+0.02, +0.43], exploratory). On finished answers self-consistency is more accurate (YB-0031). Boundary: counting never-answered episodes as failures, the regulator is no better than length alone.
**Reproduce:** `SANDBOX_MEM=6g SANDBOX_TIMEOUT=10800 sandbox/run.sh algorithms/YB-0035-corrected-realtime-race all` (dry run: `DRY_RUN=1`).

## 1. Plain English
An independent audit found real flaws in how the earlier real-time race was measured: the telemetry reached the regulator one token late, episodes that never produced an answer were quietly left out, the regulator's false-alarm rate slightly exceeded its cap, and the uncertainty intervals were too narrow. We verified every finding ourselves, fixed the instruments and the statistics, froze the full analysis code on GitHub, and only then recorded a brand-new test set of 600 questions.

The result held. With a warning counting only if it arrives, compute time included, before the model emits its answer, and every monitor allowed to flag at most 10% of correct answers, the text-blind regulator caught 23 of 40 wrong answers on the new set; a 120-billion-parameter AI judge caught 11, and a monitor that knows only how long the model has been thinking caught 9. The same holds on the two earlier test sets re-analysed with corrected telemetry, and pooled over all three.

There is a clear boundary. When 'the model never finished answering' also counts as a failure, those episodes are long by definition, and length alone spots them as well as the regulator does. The regulator's advantage is on answered wrong answers (their confidence was not measured in this experiment), not on predicting whether the model will finish.

**Inputs besides telemetry (third audit M5):** the regulator also receives the question type and the elapsed token count (normalization is per type and checkpoint). A type-by-length baseline catches 9/40 on seed 7 (docs/exploratory_audit3.json).

## 2. Theory
As YB-0033: a text-blind regulator reading the monitored model's internal telemetry, trained on real-time-knowable serial observations (the NEWS2 method), competing under a deadline against behavior monitors and a length control.

## 3. Mathematics and proofs
Race, features and controls as YB-0033 (Propositions 1-3 there). Corrections, each implemented as a tested function in src/corrected.py:
**Tightest threshold under a cap (F8).** τ* = min{τ ∈ {−∞} ∪ V_correct : (1/n)·Σ 1[vᵢ > τ] ≤ 0.10}. *Proposition 1:* the realised false-alarm rate never exceeds 10%, including with ties and discrete scores; τ* is the tightest such threshold. Tested (random, tied and sorted cases).
**Monitorable rates (F9):** rates also computed over episodes with at least one checkpoint.
**Threshold-resampling bootstrap (F10):** each of 1,000 resamples draws all episodes with replacement and re-sets τ* for both monitors before computing the recall difference. *Proposition 2:* identical monitors give exactly [0, 0, 0]. Tested.
**First crossing (F28):** seconds to spare = D − (t_clock + c) at the earliest in-time check with score > τ*. Tested.
**Fixed cost (F29):** regulator and AI-EWS checks cost a fixed 5 ms (measured 4.1 ms), making in-time status deterministic.
**Telemetry synchronization (F4):** the fixed tap discards the prompt pass; a permanent test compares each streamed reading with a fresh uncached forward pass. Old seeds are resynchronized by the one-step shift, verified by agr/verify_shift.py on all 11 of 20 re-recorded episodes whose text reproduced exactly: median error 0.012 channel standard deviations with the shift vs 0.81 without, the shift better in 11 of 11, worst single reading 2.8 (the other 9 episodes diverged across sessions; CORRECTIONS S1).

## 4. Code map
| File | Role |
|---|---|
| src/corrected.py | Cap threshold, in-time maximum, first crossing, evaluation, threshold-resampling bootstrap |
| src/absrace.py and shared cores | Checkpoints, real-time features, regulator, AI-EWS v4, length controls |
| tests/test_core.py | 8 tests (Propositions 1-2 and the corrections) |
| tests/experiment.py | Primary, sensitivity, secondary and pooled analyses; exits cleanly before seed 7 exists |
| ../../agr/layertap.py, ../../agr/test_layertap_alignment.py | Fixed tap and its permanent synchronization test |
| ../../agr/pack_realigned.py, ../../agr/verify_realignment.py | Resynchronization of seeds 2-6 and its verification |
| docs/PREREGISTRATION.md, docs/dryrun.json | Protocol and dry run committed before seed 7 |

## 5. Repeatable proof
The command above regenerates docs/results.json from data/. Seed 7 was recorded after the protocol was confirmed on GitHub (agr/start_seed7_after_push.sh), with no concurrent jobs logged; the fixed recorder saves token ids, and the pack step asserts one reading per generated token and applies no shift.
Data fingerprints (SHA-256 prefix): seed7_L.jsonl.gz 81afb1cc2efde5ef; layers_seed7_0.npz b16a3af84c5f3459; prefix_judge_abs_s7.jsonl.gz 7450675d553cc09b; prefix_selfcons_abs_s7.jsonl.gz 10db78a8751d7f07; realignment_manifest.json 6237b387b9f84d28; 

## 6. Results (derivation seeds 2-4: 5,367 answered, 402 wrong)
| Test set | Regulator caught in time | LLM judge | Length control C1 | Regulator minus judge [95% CI] | Regulator minus length [95% CI] |
|---|---|---|---|---|---|
| **Seed 7 (primary; 535 answered, 40 wrong)** | **23 (57.5%)**, FPR 9.9% | 11, FPR 6.7% | 9, FPR 6.3% | **+0.300 [+0.049, +0.487]** | **+0.350 [+0.128, +0.544]** |
| Seed 5 (resynchronized; 538, 44 wrong) | 30 (68.2%), FPR 9.9% | 13 | 17 | +0.386 [+0.140, +0.575] | +0.296 [+0.088, +0.491] |
| Seed 6 (resynchronized; 537, 43 wrong) | 25 (58.1%), FPR 9.9% | 13 | 11 | +0.279 [+0.060, +0.486] | +0.326 [+0.108, +0.514] |
| **Pooled 5+6+7 (1,610; 127 wrong)** | | | | **+0.323 [+0.186, +0.433]** | **+0.323 [+0.205, +0.434]** |

Seed 7 details: regulator false alarms among monitorable episodes 16.3%; median seconds to spare at first crossing 3.2 (judge 2.7); AI-EWS v4 9/40 (vs length +0.000 [−0.163, +0.225]); self-consistency 0/40; length control C2 3/40.
Per-checkpoint AUROC on seed 7 (t = 48/96/192/384): regulator 0.704/0.730/0.798/0.828; judge 0.544/0.562/0.609/0.783.
**Sensitivity (F5), seed 7 with never-answered episodes as failures (600; 105 failures):** regulator 68/105, length C1 74/105, judge 65/105; regulator minus judge +0.029 [−0.155, +0.121], minus length −0.057 [−0.193, +0.061]: not supported.

## 7. Verdict
- **Primary criterion met under the corrected protocol** on the fresh seed-7 test set; the re-used seeds 5 and 6 agree (their pooled estimate is descriptive only).
- **Boundary:** the advantage is on answered wrong answers; for never-answered episodes (long by definition), length alone is as good.
- AI-EWS v4 still does not beat the length control.

## 8. Limitations
One monitored model and one family of machine-gradable tasks; 40 wrong answers in the primary set; monitorable false-alarm rate 16.3%; judge timings from one Mac; seeds 5-6 judge prefixes were re-tokenized from text (seed 7 uses exact token ids). Next: external validation on a different model, and prose-span hallucination flagging.

## Deviations from the pre-registration
None.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
