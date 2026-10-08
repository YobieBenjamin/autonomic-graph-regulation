# YB-0051: precision at low false-alarm rates (exploratory stage)

YB-0050 found that precision at realistic error base rates, not compute, is the limit. This folder holds the exploratory analysis
of the YB-0050 test seeds (now derivation data) and the DRAFT pre-registration for a confirmatory test on new seeds 27 to 38.

- `make explore` (sandbox): explore/dump_scores.py (YB-0050 scoring, unchanged, writes data/explore_scores.npz) then explore/levers.py
  (cross-fitted candidates, writes docs/explore.json). Exploratory only: selection, not evidence.
- docs/PREREGISTRATION.md: DRAFT, two open choices (self-consistency samples, number of seeds).

Exploratory headline (recall at 1% false alarms, of 530 errors): probe 159, self-consistency alone 0 (too coarse), self-consistency
with a non-LLM tie-break 271 to 276, cross-fitted combination 295.
