# YB-0049: stage-diverse layering

Pre-registered test: does a two-stage alarm (hidden-state probe before the answer, self-consistency review after it) beat the probe alone at the same 10% false-alarm budget? Stage 2 is recorded after the plan is timestamped (agr/selfcons_yb0049.py). Plan: docs/PREREGISTRATION.md. Code: src/layered.py, tests/experiment.py.

## Data
YB-0045 recordings via a hash-verified local link (not tracked); stage-2 recordings in data/selfcons_yb0049_seed*.jsonl (tracked).
