# YB-0045 pre-registration: powered replication of the in-time comparison with the LLM judge

**Status:** pre-registered before any YB-0045 test recording exists, with the full analysis code (tests/experiment.py,
unchanged YB-0042 probe and YB-0035 statistics) and a dry run (docs/dryrun.json). Publicly timestamped (rule 13).

## Why
YB-0035 (seed 7) found the regulator caught significantly more wrong answers in time than the LLM judge; YB-0042 (seed 8)
did not replicate this (+0.175 [-0.061, +0.439]) with a third of the training data and a false-alarm population that
differed between its prose and code. This experiment fixes both and is powered to settle the question.

## Data
- Monitored model and generator as before (gpt-oss-20b, greedy, low effort, 800 tokens, 100 questions per type per seed).
- **Derivation (10 seeds, about 5,350 answered episodes, matched to YB-0035's 5,367):** seeds 2, 3, 4, 8 (recorded for
  YB-0042, packed copies reused unchanged) and seeds 5, 6, 7, 10, 11, 12 recorded now with telemetry and hidden states in
  the same pass. Seeds 5-8 were test sets of earlier experiments and now serve only as derivation data (protocol rule 2).
- **Test (fresh, recorded once):** seeds 9, 13, 14, pooled (about 1,600 answered, about 120 wrong).
- Both alignment tests must pass before recording. LLM judge (gpt-oss-120b, medium effort, 4,000 tokens) on test prefixes.

## Population (identical in prose and code)
All answered test episodes. Episodes that finish before the first checkpoint stay in the population: they can never be
alarmed and count in the false-alarm denominator (the YB-0035 definition). The threshold for every monitor is the tightest
value with at most 10% of all correct answered test episodes alarmed. The dry run verifies short episodes are included.

## Hypotheses (paired threshold-resampling bootstrap, 1,000 resamples, 95% CIs)
- **H1 (primary):** regulator minus judge, in-time recall; **supported iff the lower bound > 0.**
- Secondary: probe minus judge; regulator minus probe; regulator minus length and question type; per-test-seed results;
  equal false alarms among monitorable episodes; frozen derivation thresholds; per-checkpoint AUROC with CIs;
  never-answered episodes as failures.

## Power
With about 120 wrong answers the 95% CI half-width is about 0.13 (scaled from YB-0035's 0.22 at 40). Power is about 0.77 if
the true difference is seed 8's +0.175 and about 0.99 at YB-0035's +0.30.

## Pre-declared consequences
- H1 supported: the in-time advantage over the judge is replicated with adequate power.
- H1 not supported: the in-time advantage is not supported; public claims are limited to earlier discrimination
  (per-checkpoint AUROC) and to beating length and type baselines.
- No re-runs of the test analysis except after a crash with no output seen (logged as a deviation).
