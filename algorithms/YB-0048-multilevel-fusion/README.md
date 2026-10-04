# YB-0048: multi-level, hospital-style fusion of non-LLM monitors

Pre-registered secondary analysis of the YB-0045 recordings. Does combining question difficulty, a trained text monitor, a hidden-state probe and the telemetry regulator beat the best of them, as a learned stack and as a transparent NEWS2-style banded score? Plan: docs/PREREGISTRATION.md. Code: src/fusion.py, tests/experiment.py.

## Data
This analysis reads the YB-0045 recordings through a local hard-linked copy in data/ (not tracked in git). The record is algorithms/YB-0045-powered-replication/data; every file is SHA-256 identical (checked 2026-10-04).

## Results (confirmatory, 2026-10-04; plan committed 4a1e395 and timestamped 20:10:56 UTC, analysis started 20:10:56 UTC)
H1 NOT supported: stack minus probe -0.029 [-0.096, +0.044] (stack 96, probe 100 of 138). H2 NOT non-inferior: hospital banded minus probe
-0.101 [-0.164, +0.015] (86 caught at 6.4% false alarms; integer ties prevented use of the full 10% budget). H3 (descriptive): the
components largely catch the same errors (probe and text both 81, probe only 19, text only 9); 117 of 138 caught by at least one component
at its own threshold. Descriptive: the stack had the highest per-checkpoint AUROC at every checkpoint (0.85 to 0.88); the banded levels
form a monotone risk gradient (failure rate: stable 3.6%, watch 13%, concern 24%, urgent 66%). Interpretation: fusing same-stage signals
whose misses are correlated does not beat the best single signal; stage-diverse layering remains untested.
