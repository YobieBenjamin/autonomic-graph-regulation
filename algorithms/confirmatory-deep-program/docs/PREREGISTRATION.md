# YB-0031 pre-registration: confirmatory test of the deep program (derive on seed 2, test once on fresh seed 3)

Committed while the seed-2 recording is still in progress and before seed 3 exists. Seed 1 is retired as a test set:
five experiments have been designed with knowledge of its results, so it can no longer give an uncontaminated verdict.

## Data
- **Derivation:** seed 2, ~4,800 episodes (`agr/recorder.py 800 800 --layers --seed=2`), same six machine-gradable
  question types, patient gpt-oss-20b (MLX, greedy), 24-layer telemetry. Every model, band, threshold and level below is
  fitted on seed 2 only.
- **Test (touched once):** seed 3, 600 episodes (`agr/recorder.py 100 800 --layers --seed=3`), recorded after seed 2.
  Behavior monitors run on seed 3 exactly as in YB-0012 (full answer) and YB-0023 (prefixes at 25/50/75%, measured
  compute time, quiet machine).
- Primary analysis: answered episodes; failure = wrong answer (computed; no model decides truth).

## Monitors
- **AI-EWS v2** (docs/AI_EWS_METHODOLOGY.md): v1's seven vitals plus **V8 failure to settle** = mean entropy over the last
  third of the reasoning minus mean entropy over the first third (direction learned on seed 2). Levels as in v1.
- **Deep organism** (YB-0019 features, L2 logistic C = 0.1) and **hunch field** (YB-0027: reliability-weighted vitals,
  fixed seeded noise, graded output), both fitted on seed 2.
- **Behavior:** LLM judge (gpt-oss-120b), self-consistency (4 samples), answer confidence; prefix versions for the race.

## Hypotheses and decision rules (paired bootstrap 1000, seed 0; 95% CI; all thresholds from seed 2 or matched as stated)
- **H1 (real-time superiority, the decisive claim):** at a matched 10% false-alarm rate on seed-3 correct episodes (each
  monitor's threshold set so that at most 10% of correct episodes receive any in-time alarm), recall of wrong answers
  alarmed before the answer is emitted, compute time included: best organism (declared now: the deep organism) minus
  best behavior monitor. **Superior iff the CI lies above 0.**
- **H2 (accuracy):** AUROC of the deep organism vs the LLM judge and vs self-consistency (full answers). Superior /
  not distinguishable / inferior by the CI of the paired difference.
- **H3 (transparent score):** AI-EWS v2 levels are ordered (failure rate non-decreasing stable to urgent) and its
  AUROC 95% CI lower bound > 0.5.
- **H4 (silent slips):** recall at 10% FPR on multiplication and modular-power errors for the deep organism > 0.25
  (CI lower bound > 0.10).
- **H5 (settling):** V8 differs between failures and successes on seed 3 (Mann-Whitney p < 0.05, direction as learned on seed 2).
All outcomes reported. A 'eureka' is claimed only if H1 holds.
