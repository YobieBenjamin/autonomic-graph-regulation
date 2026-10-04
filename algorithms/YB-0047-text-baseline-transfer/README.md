# YB-0047: internal state vs a trained text monitor, and cross-task transfer

Pre-registered secondary analysis of the YB-0045 recordings. Part A compares the regulator and probe with a text monitor trained on the same
reasoning prefixes and labels. Part B refits each monitor without one task type and tests it on that type (leave-one-task-out).
Plan: docs/PREREGISTRATION.md. Dry run: docs/dryrun.json. Results: docs/results.json. Code: src/textmon.py, tests/experiment.py; src/ otherwise
a byte-identical copy of YB-0045 (docs/src_hashes.txt).

## Results (confirmatory, 2026-10-04; plan timestamped 19:24:49 UTC, analysis started 19:24:50 UTC)
Part A: H1 and H2 NOT supported. Caught of 138: probe 100, regulator 94, trained text monitor 90. H1 probe minus text +0.072 [0.000, +0.153]; H2 regulator minus text +0.029 [-0.045, +0.091]. Per pre-declared consequence: the advantage over the LLM judge is not shown to come from internal state rather than from training a monitor. Part B: pooled leave-one-task-out AUROC: probe 0.664 [0.617, 0.713] (H3 supported for the probe); regulator 0.445 [0.392, 0.499] and trained text 0.384 [0.340, 0.433] (not supported). No monitor transfers to held-out weekday. Pooled values below 0.5 partly reflect cross-task miscalibration; within-task held-out AUROC is in docs/results.json. Process: dry-run failure (infinite scores) and a code-review finding (unscaled held-out features) were fixed and written into the plan before the timestamp.

## Data
This analysis reads the YB-0045 recordings through a local hard-linked copy in data/ (not tracked in git). The record is algorithms/YB-0045-powered-replication/data; every file is SHA-256 identical (checked 2026-10-04).
