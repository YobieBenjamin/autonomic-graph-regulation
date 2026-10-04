# YB-0046: is the internal-state signal more than a difficulty detector?

Pre-registered secondary analysis of the YB-0045 recordings. Adds a difficulty baseline built only from the question text (digits, carries,
string length, exponent size and so on) and asks whether the regulator and probe beat it, and whether internal state adds to it.
Plan: docs/PREREGISTRATION.md. Dry run (seeds 2-8 vs 10-12, test seeds untouched): docs/dryrun.json. Results: docs/results.json.
Code: src/difficulty.py (features and baseline), tests/experiment.py; src/ otherwise a byte-identical copy of YB-0045 (docs/src_hashes.txt).

## Results (confirmatory, 2026-10-04; plan timestamped 18:29:48 UTC, analysis started 18:29:59 UTC)
All three hypotheses supported. Caught of 138 wrong answers at 10% false alarms: probe 100, combined 99, regulator 94, difficulty plus length 75, difficulty only 73, judge 28 (regulator, probe and judge exactly reproduce YB-0045). H1 regulator minus difficulty +0.138 [+0.036, +0.211]; H2 probe minus difficulty +0.181 [+0.090, +0.273]; H3 combined minus difficulty +0.174 [+0.096, +0.247]. Secondary: difficulty minus judge +0.341 [+0.190, +0.423]. The advantage over difficulty grows with reasoning length and is concentrated in weekday and modpow (descriptive). docs/results.json.

## Data
This analysis reads the YB-0045 recordings through a local hard-linked copy in data/ (not tracked in git). The record is algorithms/YB-0045-powered-replication/data; every file is SHA-256 identical (checked 2026-10-04).
