# YB-0049: stage-diverse layering

Pre-registered test: does a two-stage alarm (hidden-state probe before the answer, self-consistency review after it) beat the probe alone at the same 10% false-alarm budget? Stage 2 is recorded after the plan is timestamped (agr/selfcons_yb0049.py). Plan: docs/PREREGISTRATION.md. Code: src/layered.py, tests/experiment.py.

## Data
YB-0045 recordings via a hash-verified local link (not tracked); stage-2 recordings in data/selfcons_yb0049_seed*.jsonl (tracked).

## Results (confirmatory; plan committed 1ec19a9, RFC 3161 timestamp 23:18:49 UTC 2026-10-04, anchored in Bitcoin; stage-2 recording
23:18 UTC to 07:39 UTC 2026-10-05 with a clean pause and resume at 00:05 to 03:43 UTC, no re-timestamp; analysis 07:47 UTC)
H1 SUPPORTED: layered (probe at 5% plus self-consistency at d >= 0.75) caught 123 of 138 at 6.95% false alarms vs probe alone 100 at 9.95%;
layered minus probe +0.167 [+0.092, +0.250]. H2: stage 2 caught 28 of the 38 errors the probe missed. H3: Jaccard overlap probe vs
self-consistency 0.697 (probe vs text in YB-0048: 0.743). Descriptive: self-consistency alone caught 124 at 8.86% false alarms (AUROC
0.965), as many as the layered system; the comparison of layered vs self-consistency alone was not pre-registered. Review cost: median
8.2 s, 90th percentile 20.7 s (requires a hold gate). 584 answered episodes finished before the first checkpoint and are visible only to
stage 2. Exploratory allocation sensitivity: stage-1 budget 2.5% gives 121 (87.7%) at 4.8%; 7.5% gives 127 (92.0%) at 9.3%.
