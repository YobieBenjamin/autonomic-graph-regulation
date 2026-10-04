# YB-0047 pre-registration: internal state vs a trained text monitor, and cross-task transfer

Status: committed and publicly timestamped (scripts/timestamp_prereg.sh) BEFORE the real analysis is run.

## Why
Two open threats to YB-0045 raised in the final review. (1) The LLM judge it beat was untrained (one prompt), so the result may show only that a
trained monitor beats an untrained one, not that internal state beats text. (2) Hidden-state error detectors are known to transfer poorly across
datasets (Orgad et al., 2024); YB-0045 trained and tested on the same six task types.

## Nature of this test (disclosed up front)
Pre-registered SECONDARY analysis of the YB-0045 recordings; the evaluation seeds (9, 13, 14) were analysed in YB-0045, so this is not a fresh
test. Regulator and probe are rebuilt with YB-0045 code unchanged (src/ byte-identical copy, docs/src_hashes.txt). Dry run (DRY_RUN=1) fits on
seeds 2-8 and evaluates on 10-12 only.

## Monitors
- text_trained: L2 logistic regression on TF-IDF of token-id unigrams and bigrams of the reasoning tokens before checkpoint t (min_df 3, at most
  50,000 features, sublinear tf), plus log t and task-category indicators. The token ids are the text, undecoded (the sandbox has no network to
  fetch the tokenizer). C chosen from {0.1, 1, 10} by grouped 5-fold CV on derivation data only. Compute cost charged: 5 ms (assumed, as for the
  probe; disclosed).
- regulator, probe: exactly as YB-0045 (5 ms).

## Measure and uncertainty (identical to YB-0045)
In-time recall of wrong answers at the tightest threshold with at most 10% of all correct answered evaluation episodes alarmed; checkpoints
{48, 96, 192, 384}; paired bootstrap, 1,000 resamples, thresholds re-set in every resample.

## Hypotheses and decision rules
- H1 (primary): probe minus text_trained > 0; supported if the lower 95% bound > 0.
- H2: regulator minus text_trained > 0; same rule.
- H3 (transfer): for each task category, refit all three monitors on derivation data excluding that category and score its evaluation
  episodes. Pooled leave-one-task-out in-time AUROC (bootstrap, 1,000 resamples): transfer holds for a monitor if the lower 95% bound > 0.5.
- Secondary (descriptive): per-checkpoint AUROC with intervals; per-category held-out vs in-task AUROC for categories with at least 10 wrong.

## Pre-declared consequences
- H1 supported: internal state beats text even when the text monitor is trained on the same labels.
- H1 not supported: the posts must say the advantage over the judge is not shown to come from internal state rather than from training a
  monitor; the next experiment must include trained text baselines as standard.
- H3 not supported: the posts must say the detector does not transfer to unseen task types on this data, and scale-up must test transfer
  explicitly.

## Run gating
The confirmatory analysis runs only via make confirmatory (RUN_CONFIRMATORY=1). make experiment, which the publish pipeline calls, exits without analysing, so publishing this plan cannot run the analysis before the timestamp.

## Scoring rule for episodes with no in-time checkpoint
Episodes that finish before the first checkpoint, or whose checkpoints all miss the deadline, are never alarmed; for AUROC they receive the lowest possible score (ties at the bottom). Added 2026-10-04 after the first dry run failed on infinite scores, before this plan was timestamped.

## Normalisation for the held-out task type (H3)
The regulator and probe standardise features per (task type, checkpoint). In leave-one-task-out, the held-out type has no training statistics; without a fix its features would enter unscaled, biasing the test against internal state. Rule: for the held-out type, per-(type, checkpoint) means and standard deviations are computed from its derivation-seed episodes without using any labels (available in deployment from unlabelled traffic). Added 2026-10-04 during code review, before this plan was timestamped.
