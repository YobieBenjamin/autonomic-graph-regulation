# YB-0034 · Frozen replication of YB-0033 on a fresh test set (seed 6)

**Status:** tested · **Replicated** (pre-registration c8cec65): R1 and R2 hold; R3 (pooled estimate) was not computed by this analysis and was completed in YB-0035. Superseded by the corrected re-analysis in YB-0035 (telemetry synchronization and statistics fixed), where seed 6 is a secondary test set and the result again holds.
**Reproduce:** `SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0034-replication-realtime-race all`; R2: `... robust`.

## 1. Plain English
To check that YB-0033's result was not luck, we re-ran the identical experiment, same code and same training data, on 600 new questions. The regulator again caught about twice as many wrong answers in time as the 120-billion-parameter AI judge, and more than the length-only monitor, also when every monitor was held to exactly the same false-alarm rate.

## 2-5. Theory, mathematics, code and repeatable proof
Identical to YB-0033 (code copied unchanged except test-seed file names); the equal-false-alarm check (tests/exploratory_equal_fpr.py, make target `robust`) was pre-registered here as R2. The audit findings for YB-0033 (F4, F5, F8-F10) apply equally; they are fixed in YB-0035.
Data fingerprints (SHA-256 prefix): seed6_L.jsonl.gz b9a9de7b0b9db107; layers_seed6_0.npz 0499d24b535a98bd; prefix_judge_abs_s6.jsonl.gz 7488a1b2ae97d115; prefix_selfcons_abs_s6.jsonl.gz 5b90f9c1d2877c6d; 

## 6. Results (537 answered, 43 wrong)
Regulator 24/43 in time (55.8%, FPR 10.1%); LLM judge 13/43 (FPR 9.3%); length control C1 11/43 (FPR 7.3%); AI-EWS v4 11/43; self-consistency 0/43.
R1: regulator minus judge +0.256 [+0.070, +0.442]; minus length +0.302 [+0.116, +0.488]. R2 (exactly equal false alarms): 24 vs 13 at 9.3% and 22 vs 11 at 7.3%, both CIs above 0.

## 7. Verdict
Replicated (R1, R2). R3 missing here (audit F6); computed in YB-0035: pooled seeds 5-7, +0.323 [+0.186, +0.433] vs the judge and +0.323 [+0.205, +0.434] vs length.

## Deviations
R3 not computed by the analysis script (discovered in the audit); completed in YB-0035. A brief GPU-sharing window at the start of the seed-6 recording is logged in data/agr/contention_windows.txt.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
