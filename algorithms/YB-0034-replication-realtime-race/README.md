# EXPERIMENT-REPLICATION-REALTIME-RACE · Frozen replication of EXPERIMENT-CLEAN-REALTIME-RACE on a fresh test set (seed 6)

**Status:** tested · **Replicated** (pre-registration c8cec65): EXPERIMENT-EUREKA-REPLICATION-CRITERION and EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS hold; EXPERIMENT-POOLED-SEEDS-ESTIMATE (pooled estimate) was not computed by this analysis and was completed in EXPERIMENT-CORRECTED-REALTIME-RACE. Superseded by the corrected re-analysis in EXPERIMENT-CORRECTED-REALTIME-RACE (telemetry synchronization and statistics fixed), where seed 6 is a secondary test set and the result again holds.
**Reproduce:** `SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0034-replication-realtime-race all`; EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS: `... robust`.

## 1. Plain English
To check that EXPERIMENT-CLEAN-REALTIME-RACE's result was not luck, we re-ran the identical experiment, same code and same training data, on 600 new questions. The regulator again caught about twice as many wrong answers in time as the 120-billion-parameter AI judge, and more than the length-only monitor, also when every monitor was held to exactly the same false-alarm rate.

## 2-5. Theory, mathematics, code and repeatable proof
Identical to EXPERIMENT-CLEAN-REALTIME-RACE (code copied unchanged except test-seed file names); the equal-false-alarm check (tests/exploratory_equal_fpr.py, make target `robust`) was pre-registered here as EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS. The audit findings for EXPERIMENT-CLEAN-REALTIME-RACE (REVIEW-LAYER-TAP-ONE-STEP-LATE, REVIEW-UNANSWERED-EPISODES-EXCLUDED, REVIEW-FALSE-ALARM-CAP-EXCEEDED to REVIEW-BOOTSTRAP-IGNORED-THRESHOLD-UNCERTAINTY) apply equally; they are fixed in EXPERIMENT-CORRECTED-REALTIME-RACE.
Data fingerprints (SHA-256 prefix): seed6_L.jsonl.gz b9a9de7b0b9db107; layers_seed6_0.npz 0499d24b535a98bd; prefix_judge_abs_s6.jsonl.gz 7488a1b2ae97d115; prefix_selfcons_abs_s6.jsonl.gz 5b90f9c1d2877c6d; 

## 6. Results (537 answered, 43 wrong)
Regulator 24/43 in time (55.8%, FPR 10.1%); LLM judge 13/43 (FPR 9.3%); length control EXPERIMENT-LENGTH-CONTROL-STILL-REASONING 11/43 (FPR 7.3%); AI-EWS v4 11/43; self-consistency 0/43.
EXPERIMENT-EUREKA-REPLICATION-CRITERION: regulator minus judge +0.256 [+0.070, +0.442]; minus length +0.302 [+0.116, +0.488]. EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS (exactly equal false alarms): 24 vs 13 at 9.3% and 22 vs 11 at 7.3%, both CIs above 0.

## 7. Verdict
Replicated (EXPERIMENT-EUREKA-REPLICATION-CRITERION, EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS). EXPERIMENT-POOLED-SEEDS-ESTIMATE missing here (audit REVIEW-POOLED-ESTIMATE-NEVER-COMPUTED); computed in EXPERIMENT-CORRECTED-REALTIME-RACE: pooled seeds 5-7, +0.323 [+0.186, +0.433] vs the judge and +0.323 [+0.205, +0.434] vs length.

## Deviations
EXPERIMENT-POOLED-SEEDS-ESTIMATE not computed by the analysis script (discovered in the audit); completed in EXPERIMENT-CORRECTED-REALTIME-RACE. A brief GPU-sharing window at the start of the seed-6 recording is logged in data/agr/contention_windows.txt.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
