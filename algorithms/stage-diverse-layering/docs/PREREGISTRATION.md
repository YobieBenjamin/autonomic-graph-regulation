# YB-0049 pre-registration: does stage-diverse layering beat the best single check?

Status: committed and publicly timestamped (scripts/timestamp_prereg.sh) BEFORE any stage-2 data for the test seeds is recorded.

## Why
YB-0048 found that fusing four non-LLM monitors that read the same moment does not beat the best of them: their misses are correlated. The AGR
theory was refined (docs/THEORY_AND_POSITION.md, P5): layers must differ in stage and signal. This test adds a second stage that differs in
both: a post-answer self-consistency review, acting after the answer exists and before an action is released (which requires a hold gate,
YB-0044). It can fail.

## Data
- Stage 1: the YB-0045 hidden-state probe (YB-0045 code unchanged; layer and C selected on derivation data), in-time score over checkpoints
  {48, 96, 192, 384} with a 5 ms cost, on the YB-0045 test seeds 9, 13, 14 (previously analysed; stage-1 results are known: probe 100 of 138).
- Stage 2: NEW data, recorded after this plan is timestamped: agr/selfcons_yb0049.py, which reuses the YB-0012/YB-0031 self-consistency method
  verbatim: 4 samples of gpt-oss-20b at temperature 0.8, reasoning effort low, at most 800 tokens, prompt "Answer with only the final answer,
  no explanation."; d = fraction of samples whose normalised answer differs from the original answer (an empty answer counts as different);
  sample seeds 1000 * episode index + k. Wall-clock seconds for the 4 samples are recorded.
- Population: the 1,605 answered test episodes of YB-0045 (138 wrong), defined exactly as in YB-0045 to YB-0048.

## Layered alarm and allocation (fixed in advance; no tuning on test labels beyond the threshold rule itself)
Alarm if v1 > tau1 OR d >= delta. tau1: tightest threshold with at most 5% of correct episodes alarmed by stage 1. delta: the smallest value in
{0.25, 0.5, 0.75, 1.0} for which the union alarm rate on correct episodes is at most 10% (stage 2 off if none). Comparator: the probe alone at
the tightest threshold with at most 10% of correct episodes alarmed. Same 10% total false-alarm budget for both. Episodes that finish before
the first checkpoint cannot be alarmed by stage 1 but can be by stage 2.

## Hypotheses and decision rules
- H1 (primary): layered recall minus probe-alone recall > 0; paired bootstrap, 1,000 resamples, tau1, delta and the probe threshold re-set in
  every resample; supported if the lower 95% bound > 0.
- H2 (descriptive): of the errors the probe alone misses at 10%, how many stage 2 catches at delta.
- H3 (descriptive): Jaccard overlap of errors caught by the probe alone (10%) and by self-consistency alone (its own tightest threshold at
  10%), compared with the probe/text overlap in YB-0048 (0.7431). Lower means the stages fail more differently.
- Secondary (descriptive): self-consistency alone (recall, false alarms, AUROC); review seconds (median, 90th percentile), the delay a hold
  gate imposes; errors caught by stage 2 among never-monitored episodes; sensitivity to the stage-1 allocation (2.5% and 7.5%, exploratory).

## Pre-declared consequences
- H1 supported: stage-diverse layering beats the best single check at an equal false-alarm budget on this data (P5 supported, narrow; the
  cost is the review delay under a hold gate).
- H1 not supported: P5 remains not supported at this budget; report H2 and H3 regardless.

## Process
Smoke test of the recorder on derivation seed 2 only (the code refuses test seeds in smoke mode). Smoke and dry run of the analysis use
derivation seeds with SYNTHETIC stage-2 scores (pipeline checks; no test data read). The confirmatory analysis runs only via make
confirmatory (PROTOCOL rule 14), after the stage-2 recording completes and is checked for completeness.
