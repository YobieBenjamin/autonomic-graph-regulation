# YB-0051 pre-registration (DRAFT): precision at low false-alarm rates

Status: DRAFT, 2026-10-07. Not timestamped. Becomes binding only when committed and timestamped (scripts/timestamp_prereg.sh) BEFORE
any test-seed recording starts (PROTOCOL rules 1, 13, 16). Two design choices are open (marked OPEN) and are the author's to make.

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
alarms: probe 105, the combination 180. A per-task-type calibration was tried and produced degenerate scores (ties at the top of the
scale); it is an implementation fault to fix, not a finding.

Position held by the author (design principle): no language model is the judge. Self-consistency enters only as a number measured by
outside code; the combination, the threshold and the decision are non-LLM code.

## Data
- NEW test seeds 27 to 38 (12 seeds), recorded after this plan is timestamped, YB-0050 settings unchanged (recorder.py 100 800
  --layers --hs; self-consistency as agr/selfcons_yb0050.py with only seeds and file names changed). Expected about 6,400 answered
  episodes, about 530 errors, about 5,900 correct answers (so a 1% false-alarm rate is about 59 false alarms, 0.5% about 30).
- OPEN 1, self-consistency samples: (a) k = 4 as in YB-0050 (about 28 h total), or (b) k = 8 (about 47 h), which also tests whether
  more samples give the resolution directly. Recommended: (b), recorded so that the first 4 samples are the k = 4 score, giving both.
- OPEN 2, size: 12 seeds (0.1% false alarms about 6 events: descriptive only), or 24 seeds (about 56 h at k = 4, about 94 h at k = 8;
  0.1% about 12 events). Recommended: 12 seeds.
- Derivation: seeds 2 to 26 for the non-LLM monitors (as YB-0050); the combination rule is fitted on seeds 15 to 26, the only
  derivation seeds with self-consistency reviews. All normalisation (ranks) uses derivation empirical distributions, never test ranks.

## Monitors (frozen before the test data exist)
Probe, text, difficulty, regulator, non-LLM stack and banded score exactly as YB-0050. Self-consistency d (k = 4; and k = 8 if OPEN 1 b).
- C1, tie-break: d + 0.2 x (derivation percentile of the stack score).
- C2, combination (primary): L2 logistic regression (C = 1) on [d, derivation percentiles of stack, probe, text, difficulty, a
  monitored flag], fitted once on seeds 15 to 26 and frozen.
- C3, conjunction (high-precision rule): alarm only if the stack is above its derivation 90th percentile on correct episodes AND
  d >= 0.75 (grid point chosen on derivation; reported, not tuned on test).
- C4, per-task calibration of C2, re-implemented with a continuous within-task percentile and tested on derivation before freezing.

## Hypotheses and decision rules (2,000 paired bootstrap resamples, thresholds re-set in every resample)
- H1 (primary): recall of C2 minus recall of the probe alone, both at a 1% false-alarm rate. Supported if the lower 95% bound > 0.
- H2: precision at a 1% error base rate for C2 at a 1% false-alarm rate is at least 33% (no more than two false alarms per true
  one). Supported if the lower 95% bound >= 0.33.
- H3 (if OPEN 1 b): recall at 1% of self-consistency with k = 8 plus tie-break minus k = 4 plus tie-break. Supported if lower bound > 0.
- Secondary (descriptive): all candidates at 0.5%, 1%, 2% and 10% false alarms; partial AUROC up to 1%; C3 recall and false-alarm
  rate; C4 vs C2; 0.1% false alarms with exact event counts; cost per check (as YB-0050 H4).

## Pre-declared consequences
- H1 supported: combining the model's self-disagreement with non-LLM internal-state scores is the measured way to raise recall at low
  false-alarm rates. Not supported: the exploratory gain was an artefact of fitting on the evaluation data.
- H2 supported: two or fewer false alarms per true one at a 1% error base rate is reachable on this task set. Not supported: report
  the measured precision as the current ceiling.

## Process
As YB-0050: one command (start script waits for AC power; battery guard with SIGINT, SIGTERM, SIGKILL escalation), smoke, dry run on
derivation with synthetic test scores, commit, timestamp, then record, review, pack, confirmatory analysis, publish. Each seed checks
AC power before it starts (lesson of the YB-0050 battery stop).
