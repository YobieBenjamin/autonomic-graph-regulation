# YB-0042 pre-registration: the regulator versus a hidden-state probe

**Status:** pre-registered before any YB-0042 recording exists. The analysis code (tests/experiment.py, src/probe.py and
the unchanged YB-0035 statistics in src/corrected.py and src/absrace.py) and a dry run on synthetic data
(docs/dryrun.json) are committed with this document. Per protocol rule 13 the commit hash is publicly timestamped.

## Question
Does the text-blind regulator's in-time advantage hold against a standard linear probe trained on the monitored model's
raw hidden states (the text-blind competitor from prior work: Azaria and Mitchell 2023; Orgad et al. 2024; Oladri,
Jawahar and Mohamed 2026)? And does the regulator's advantage over the LLM judge replicate on a second fresh test set?

## Data
- Monitored model gpt-oss-20b (MLX), greedy decoding, low reasoning effort, max 800 tokens; same question generator.
- Derivation: seeds 2, 3, 4 re-recorded with telemetry (layertap) and hidden states (hstap) captured in the same pass
  (agr/recorder.py --layers --hs; new files, never mixed with earlier recordings). Test: fresh seed 8, recorded once.
- Before every recording, agr/test_layertap_alignment.py and agr/test_hstap_alignment.py must pass.
- LLM judge (gpt-oss-120b, medium effort, up to 4,000 tokens) on seed-8 prefixes at the absolute checkpoints.
  Self-consistency is not run (it caught 0/40 in YB-0035 because it cannot finish in time; disclosed, not a result).

## Monitors (identical race rules for all: checkpoints t in {48, 96, 192, 384} while still reasoning; in time iff
score > threshold and t_clock(t) + cost <= answer emission; threshold = tightest with at most 10% of correct test
episodes alarmed)
- **Regulator:** YB-0035 code unchanged, refitted on the new derivation recordings. Cost: fixed 5 ms.
- **Probe (primary):** L2 logistic regression on [hidden state of the last token before t, mean hidden state over tokens
  before t] at one layer, plus log t; z-scored per (question type, t) with derivation statistics, exactly like the
  regulator. Layer from {6, 12, 18, 23} and C from {0.001, 0.01, 0.1} chosen by 5-fold cross-validation grouped by
  episode on derivation data only (highest AUROC; ties: earlier layer, smaller C). Cost: fixed 5 ms.
- **Probe (secondary):** all four layers concatenated, C chosen the same way.
- **Controls:** length C1(t) = t; question type C3 = derivation failure rate of the type. **Judge:** measured cost.

## Hypotheses and decision rules (paired threshold-resampling bootstrap, 1,000 resamples, 95% CIs)
- **H1 (primary):** in-time recall, regulator minus probe. Lower bound > 0: regulator better. Upper bound < 0: probe
  better. Otherwise: not distinguishable. All three outcomes are reported as stated.
- **H2 (replication):** regulator minus judge; replicated iff the lower bound > 0.
- **Secondary (descriptive):** probe minus judge; regulator minus the all-layers probe; regulator minus length and type;
  equal false alarms among monitorable episodes; thresholds frozen from 5-fold cross-fitted derivation scores;
  per-checkpoint AUROC with bootstrap CIs (regulator, probe, judge, type); never-answered episodes counted as failures.

## Pre-declared consequences
- If the probe is better or not distinguishable, the public claim becomes: reading the model's internal state (probe or
  telemetry) beats the judge before the answer exists; the added value of the telemetry features is not supported.
- If H2 is not replicated, the YB-0035 result is reported as not replicated on seed 8.
- No re-runs of the seed-8 analysis except after a crash with no output seen (logged as a deviation).
