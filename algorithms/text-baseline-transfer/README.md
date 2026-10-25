# EXPERIMENT-TEXT-BASELINE-TRANSFER: internal state vs a trained text monitor, and cross-task transfer

Pre-registered secondary analysis of the EXPERIMENT-POWERED-REPLICATION recordings. Part A compares the regulator and probe with a text monitor trained on the same
reasoning prefixes and labels. Part B refits each monitor without one task type and tests it on that type (leave-one-task-out).
Plan: docs/PREREGISTRATION.md. Dry run: docs/dryrun.json. Results: docs/results.json. Code: src/textmon.py, tests/experiment.py; src/ otherwise
a byte-identical copy of EXPERIMENT-POWERED-REPLICATION (docs/src_hashes.txt).

## Results (confirmatory, 2026-10-04; plan timestamped 19:24:49 UTC, analysis started 19:24:50 UTC)
Part A: EXPERIMENT-PROBE-BEATS-TRAINED-TEXT and EXPERIMENT-REGULATOR-BEATS-TRAINED-TEXT NOT supported. Caught of 138: probe 100, regulator 94, trained text monitor 90. EXPERIMENT-PROBE-BEATS-TRAINED-TEXT probe minus text +0.072 [0.000, +0.153]; EXPERIMENT-REGULATOR-BEATS-TRAINED-TEXT regulator minus text +0.029 [-0.045, +0.091]. Per pre-declared consequence: the advantage over the LLM judge is not shown to come from internal state rather than from training a monitor. Part B: pooled leave-one-task-out AUROC: probe 0.664 [0.617, 0.713] (EXPERIMENT-UNSEEN-TASK-TRANSFER supported for the probe); regulator 0.445 [0.392, 0.499] and trained text 0.384 [0.340, 0.433] (not supported). No monitor transfers to held-out weekday. Pooled values below 0.5 partly reflect cross-task miscalibration; within-task held-out AUROC is in docs/results.json. Process: dry-run failure (infinite scores) and a code-review finding (unscaled held-out features) were fixed and written into the plan before the timestamp.

## Data
This analysis reads the EXPERIMENT-POWERED-REPLICATION recordings through a local hard-linked copy in data/ (not tracked in git). The record is algorithms/powered-replication/data; every file is SHA-256 identical (checked 2026-10-04).
