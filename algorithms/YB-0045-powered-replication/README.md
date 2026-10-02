# YB-0045 · Powered replication of the in-time comparison with the LLM judge

**Status:** pre-registered (docs/PREREGISTRATION.md, analysis code, dry run docs/dryrun.json) before any test recording. **Result: H1 supported**, regulator minus judge +0.478 [+0.307, +0.560].
**Reproduce:** SANDBOX_MEM=16g SANDBOX_TIMEOUT=21600 sandbox/run.sh algorithms/YB-0045-powered-replication all (dry run: DRY_RUN=1).

Training data matched to YB-0035 (10 seeds, about 5,350 answered); three fresh test seeds (9, 13, 14; about 120 wrong answers); false-alarm population identical in prose and code (all answered test episodes; verified in the dry run). Primary: regulator minus LLM judge, in-time recall, lower 95% bound > 0. Chain: agr/yb0045_chain.sh.

## Results (pre-registered analysis, run unchanged; docs/results.json)
Test: seeds 9, 13, 14 pooled, 1,605 answered, 138 wrong; population = all correct answered test episodes (582 short correct episodes included). Derivation: 5,365 answered (9,189 observations).

| Monitor | In time (of 138) | FPR (all / monitorable) |
|---|---|---|
| Probe (layer 18, C = 0.001) | 100 | 9.95% / 16.5% |
| Probe, four layers | 97 | 9.95% / 16.5% |
| Regulator | 94 | 9.95% / 16.5% |
| Length | 39 | 6.3% / 10.4% |
| Question type | 31 | 5.3% / 8.7% |
| LLM judge | 28 | 7.0% / 11.6% |

- **H1 (primary)** regulator minus judge: **+0.478 [+0.307, +0.560], supported.**
- Probe minus judge +0.522 [+0.363, +0.606]; regulator minus probe -0.044 [-0.128, +0.024] (not distinguishable); regulator minus length +0.399 [+0.293, +0.496]; minus type +0.457 [+0.344, +0.548].
- Equal monitorable false alarms: regulator 83, probe 90, judge 26. Frozen derivation thresholds: regulator 93, probe 100.
- Per-checkpoint AUROC t = 48/96/192/384: regulator 0.763/0.816/0.839/0.761; probe 0.815/0.832/0.869/0.840; judge 0.617/0.590/0.643/0.690.
- Never-answered as failures: regulator minus probe -0.081 [-0.146, -0.036] (probe better).

## Deviations
1. Per-test-seed results were listed as secondary but not computed by the pre-registered code; computed post hoc by tests/posthoc_per_seed.py (docs/posthoc_per_seed.json): seed 9 +0.405 [+0.241, +0.595], seed 13 +0.469 [+0.250, +0.623], seed 14 +0.404 [+0.208, +0.628] (regulator minus judge).
2. The chain publish failed (sandbox tmpfs too small); results were committed by a re-run publish whose check re-ran the analysis; sandbox tmpfs made configurable.
