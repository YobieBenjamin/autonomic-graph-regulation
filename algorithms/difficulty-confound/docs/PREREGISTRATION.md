# YB-0046 pre-registration: is the internal-state signal more than a difficulty detector?

Status: committed and publicly timestamped (OpenTimestamps and RFC 3161, scripts/timestamp_prereg.sh) BEFORE the real analysis is run.

## Why
Audit discussion of the final series (2026-10-04) identified the main open threat to YB-0045: the tasks are synthetic, and within one task
type some problems are harder (more digits, more carries). A monitor that only learns "this problem is hard" would flag more errors without
knowing anything about this particular answer. YB-0045 controlled for task type and elapsed length, not for difficulty within a type.

## Nature of this test (disclosed up front)
A pre-registered SECONDARY analysis of existing data. The evaluation seeds (9, 13, 14) were analysed in YB-0045, so this is not a fresh
test. The regulator and probe are rebuilt with YB-0045's code unchanged (src/ is a byte-identical copy; hashes in docs/src_hashes.txt).
The difficulty features below were fixed before examining their relation to errors on any data. The dry run (DRY_RUN=1) fits on seeds 2-8
and evaluates on 10-12 only; it never reads seeds 9, 13 or 14.

## Difficulty features (from the question text and true answer only, never the model output)
- mul_easy, mul_hard: digits of each operand; nonzero digits of each; their product (number of nonzero partial products); columns that
  produce a carry in schoolbook long multiplication; log1p of total carry mass; digits of the product.
- add_hard: digits of each operand; number of carries; longest carry chain; digits of the sum.
- count: string length; the true count; number of distinct letters.
- weekday: |year - 2000| / 100; century; leap year; month; day; month <= 2.
- modpow: digits of the base; exponent; log2 exponent; binary weight of the exponent; digits of the modulus.

## Monitors
- difficulty_plus_length (the primary baseline): per-category L2 logistic regression (C = 1.0, training-set standardisation) on the
  difficulty features plus log t, fitted on all derivation observations; categories with fewer than 5 training errors use their training
  error rate. It receives every non-telemetry input the regulator receives (task category, elapsed tokens) plus difficulty. Compute cost 0.
- difficulty_only: the same without log t (secondary).
- regulator, probe: exactly as YB-0045 (compute cost 5 ms).
- combined: logistic regression on [difficulty-baseline logit, regulator score], fitted on GroupKFold(5) cross-fitted derivation scores,
  applied with full-fit scores (compute cost 5 ms).

## Measure and uncertainty (identical to YB-0045)
In-time recall of wrong answers at the tightest threshold with at most 10% of all correct answered evaluation episodes alarmed; in-time
means score above threshold at a checkpoint t in {48, 96, 192, 384} with t_clock(t) + cost <= answer emission time. Paired bootstrap, 1,000
resamples, thresholds re-set in every resample.

## Hypotheses and decision rules
- H1 (primary): regulator minus difficulty_plus_length > 0; supported if the lower 95% bound > 0.
- H2: probe minus difficulty_plus_length > 0; same rule.
- H3 (incremental value): combined minus difficulty_plus_length > 0; same rule. This is the decisive test of whether internal state adds
  information beyond problem difficulty.
- Secondary (descriptive, no decision): difficulty_plus_length minus judge; per-checkpoint AUROC with intervals for regulator, probe,
  difficulty_plus_length and combined; within-category AUROC of in-time scores for categories with at least 10 wrong answers.

## Pre-declared consequences
- H3 supported: the posts may say the internal-state signal predicts errors beyond problem difficulty on this model and task family.
- H3 not supported: the posts must say the internal-state advantage over the judge is not shown to exceed what problem difficulty alone
  predicts, and the next experiment must use tasks where difficulty cannot be read off the question.
- H1 or H2 not supported while H3 is: report that difficulty alone is a strong baseline and the internal state adds to it.

## Dry-run disclosure
The dry run (fit on seeds 2-8, evaluate on 10-12; test seeds 9, 13, 14 not read) was run and its output (docs/dryrun.json) seen before this plan was timestamped. No hypothesis, feature, model setting or decision rule was changed after seeing it. The dry run showed difficulty_plus_length catching 78 of 137 wrong answers vs 96 for the regulator.

## Run gating
The confirmatory analysis runs only via make confirmatory (RUN_CONFIRMATORY=1). make experiment, which the publish pipeline calls, exits without analysing, so publishing this plan cannot run the analysis before the timestamp.
