# YB-0051 pre-registration: precision at low false-alarm rates

Status: FINAL, 2026-10-10. Binding from the moment this file is committed and timestamped (scripts/timestamp_prereg.sh), which happens
BEFORE any test-seed recording starts (PROTOCOL rules 1, 13, 16). The draft of 2026-10-07 had two open choices; the author chose
OPEN 1 = (b) k = 8 and OPEN 2 = 12 seeds. Changes from the draft, all made before any test data exist, are listed at the end.

## Why
YB-0050 showed the binding limit at scale is precision, not compute. At a 1% error base rate and a 10% false-alarm budget every
monitor sends about 8 to 14 false alarms per true one. At a 1% budget the probe catches 30% at 23% precision, and self-consistency
with 4 samples cannot operate at all: its score has five values (0, 0.25, 0.5, 0.75, 1), and its smallest step alarms more than 1%
of correct answers. An exploratory analysis of the YB-0050 test seeds (now derivation data; docs/explore.json, cross-fitted, selection
only, not evidence) suggests the fix is resolution, not a new signal: breaking the ties inside each self-consistency level with a
continuous non-LLM score roughly doubles recall at a 1% false-alarm rate.

Exploratory numbers (YB-0050 seeds 15-26, 530 errors, recall at 1% false alarms; precision at a 1% error base rate):
probe 159 (30%; 23%), non-LLM stack 150 (28%; 22%), self-consistency alone 0, self-consistency with a probe tie-break 271 (51%; 34%),
with a stack tie-break 276 (52%; 35%), cross-fitted logistic of self-consistency plus non-LLM ranks 295 (56%; 36%). At 0.5% false
alarms: probe 105, the combination 180.

Position held by the author (design principle): no language model is the judge. Self-consistency enters only as a number measured by
outside code; the combination, the threshold and the decision are non-LLM code.

## Data
- NEW test seeds 27 to 38 (12 seeds), recorded after this plan is timestamped, YB-0050 recording settings unchanged (agr/recorder.py
  100 800 --layers --hs). Expected about 6,400 answered episodes, about 530 errors, about 5,900 correct answers (a 1% false-alarm rate
  is about 59 false alarms, 0.5% about 30, 0.1% about 6: the 0.1% results are descriptive only).
- Self-consistency: k = 8 samples per answered episode (agr/selfcons_yb0051.py, a copy of agr/selfcons_yb0050.py with 8 samples).
  Sample k uses random seed 1000 x idx + k, so samples 0-3 are exactly the YB-0050 k = 4 procedure: d4 = disagreement over samples
  0-3, d8 = over samples 0-7. Both come from one recording. About 47 hours in total.
- Reference (derivation) data: data/explore_scores.npz = YB-0050 test seeds 15-26 (6,457 answered, 530 wrong), scored by the non-LLM
  monitors fitted on seeds 2-14, with d4. The combination rule is fitted on this file and every percentile is taken against it.
- Test scoring (tests/score_test.py): the non-LLM monitors (difficulty, text, probe, regulator, stack, banded) are fitted on seeds 2-14
  EXACTLY as for the reference (same code, same seeds), then score seeds 27-38. Test scores and reference scores therefore come from the
  same fitted monitors and live on the same scale. Test labels are used only to count hits and false alarms.

## Candidates (frozen before the test data exist; tests/candidates.py)
pct(v) = mid-rank percentile of v within the reference values (ties count half); never-monitored episodes have score -inf.
- probe, stack: the YB-0050 in-time scores.
- self-consistency alone: d4, d8.
- C1, tie-break: d + (0.8 / k) x pct(stack): 0.2 for k = 4, 0.1 for k = 8; always below one level step (1/k), so it orders episodes
  inside a self-consistency level and never moves one across levels. C1_k4, C1_k8.
- C2, combination (primary): L2 logistic regression (C = 1) on [d4, pct(stack), pct(probe), pct(text), pct(difficulty), monitored
  flag (probe finite)], fitted once on the reference and frozen.
- C3, conjunction (high-precision rule, fixed operating point): stack above the 90th percentile of reference stack scores on correct
  episodes AND d >= 0.75. Reported for d4 and d8 with exact counts.
- C4, per-task calibration of C2: C2 mapped to its mid-rank percentile among CORRECT reference episodes of the same task type (all
  correct episodes if the task type is unseen), plus 1e-3 x C2 so scores above every reference value stay ordered (the exploratory
  version tied at the top). Pre-freeze derivation check (docs/c4_derivation_check.json, cross-fitted on the reference only, selection
  evidence): errors caught at 1% false alarms C4 314 vs C2 299, at 0.5% C4 239 vs C2 178; 129 distinct values in the top 2% for both
  (no ties). C2 stays the primary candidate as declared in the draft; C4 is secondary.

## Hypotheses and decision rules (2,000 paired bootstrap resamples over test episodes, thresholds re-set in every resample from the
## correct episodes of that resample; tests/experiment.py with src/decider.py from YB-0050)
- H1 (primary): recall of C2 minus recall of the probe alone, both at a 1% false-alarm rate. Supported if the lower 95% bound > 0.
- H2: precision of C2 at a 1% false-alarm rate and a 1% error base rate is at least 33% (no more than two false alarms per true
  one). Supported if the lower 95% bound >= 0.33.
- H3: recall at 1% false alarms of C1_k8 minus C1_k4. Supported if the lower 95% bound > 0.
- Secondary (descriptive): every candidate at 0.5%, 1%, 2% and 10% false alarms with recall intervals; partial AUROC up to 1%; burden
  tables (precision, alarms per million, false per true) at 1% and 10% false alarms for error base rates 10%, 1%, 0.1%; C4 minus C2 and
  C2 minus C1_k4 at 1%; C3 counts; exact event counts at 0.1%; review cost (mean seconds for 4 and 8 samples, and as a share of
  generation wall-clock). The non-LLM monitors are the YB-0050 code, so their cost is the YB-0050 H4 measurement.

## Pre-declared consequences
- H1 supported: combining the model's self-disagreement with non-LLM internal-state scores is the measured way to raise recall at low
  false-alarm rates. Not supported: the exploratory gain was an artefact of fitting on the evaluation data.
- H2 supported: two or fewer false alarms per true one at a 1% error base rate is reachable on this task set. Not supported: report
  the measured precision as the current ceiling.
- H3 supported: more samples buy resolution directly, and a k = 8 review is worth its cost at low false-alarm budgets. Not supported:
  the tie-break, not more samples, is where the resolution comes from; k = 4 stays the default.

## Process
As YB-0050, one command (agr/yb0051_start.sh): unit tests and the C4 derivation check in the sandbox, a 2-episode real-model review
smoke on derivation seed 2, smoke and dry run in the sandbox (dry run: monitors fitted on seeds 2-8, evaluated on 10-12, synthetic
self-consistency), commit and push, check that the plan and the frozen code equal the commit, timestamp (RFC 3161 + OpenTimestamps),
then alignment tests, record seeds 27-38, review every answered episode with 8 samples, completeness check, pack, confirmatory analysis
(make confirmatory, rule 14), publish, public snapshot. AC power is checked before every seed of recording and of review; a battery
guard stops everything cleanly at 12% (SIGINT, SIGTERM, SIGKILL) and every recorder resumes where it stopped. Frozen files checked
before the timestamp and on resume: this plan, agr/selfcons_yb0051.py, agr/recorder.py, tests/candidates.py, tests/score_test.py,
tests/experiment.py.

## Changes from the 2026-10-07 draft (before any test data)
1. OPEN 1 resolved: k = 8, recorded so the first 4 samples are the k = 4 score. OPEN 2 resolved: 12 seeds.
2. Derivation for the test-time non-LLM monitors is seeds 2-14, not 2-26, so the test scores come from the same fitted monitors as the
   reference on which C2 is fitted and percentiles are taken (fitting them on 2-26 would put test scores on a different scale from the
   reference). Seeds 15-26 are used once, as the reference.
3. C1 tie-break weight scaled with k (0.8 / k), so for k = 8 it stays below the level step of 0.125.
4. C4 re-implemented (continuous tie-break) and checked on derivation before freezing (numbers above).
5. Cost: review seconds measured directly; non-LLM monitor costs carried from YB-0050 (same code).
