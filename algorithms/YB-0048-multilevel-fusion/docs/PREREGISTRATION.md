# YB-0048 pre-registration: does a multi-level, hospital-style combination of non-LLM monitors beat its best single component?

Status: committed and publicly timestamped (scripts/timestamp_prereg.sh) BEFORE the confirmatory analysis is run.

## Why
The AGR theory (docs/THEORY_AND_POSITION.md) claims safety needs layered, independent, non-LLM checks combined into a graded score, as a
hospital combines vital signs (principles P4 and P5, currently Open). YB-0046 and YB-0047 produced four non-LLM monitors on the same data:
question difficulty plus elapsed length, a trained text-prefix monitor, a hidden-state probe and the telemetry regulator. If they catch
different errors, combining them should beat the best of them. This test can fail.

## Nature of this test (disclosed up front)
Pre-registered SECONDARY analysis of the YB-0045 recordings; evaluation seeds 9, 13, 14 were analysed in YB-0045 to YB-0047, and their
single-monitor results are known (probe 100, regulator 94, text 90, difficulty 75 of 138). The fusion results are not known. Components are
rebuilt with unchanged code (src/ byte-identical to YB-0045 plus difficulty.py from YB-0046 and textmon.py from YB-0047; hashes in
docs/src_hashes.txt). Text monitor C = 1.0, the value YB-0047 selected by derivation-only cross-validation. Smoke test (SMOKE=1) and dry run
(DRY_RUN=1, fit on seeds 2-8, evaluate on 10-12) never read the evaluation seeds.

## Monitors
- Components: difficulty (difficulty features plus log t, YB-0046), text (YB-0047), probe and regulator (YB-0045).
- stack: logistic regression (C = 1.0, standardised) on the logits of the four component scores, fitted on GroupKFold(5) cross-fitted
  derivation scores; applied with full-fit component scores.
- hospital_banded (NEWS2-style): at each checkpoint t, each component earns one point for each of the 90th, 95th and 99th percentiles of
  its cross-fitted scores on CORRECT derivation observations at the same t that it exceeds (0 to 3 points); points are summed (0 to 12).
  Every point is explainable. Because the total is an integer, ties may force a threshold stricter than the 10% cap (a handicap, disclosed).
- Compute cost charged: 5 ms for monitors needing internal state or text (difficulty 0 ms).

## Measure and uncertainty (identical to YB-0045)
In-time recall at the tightest threshold with at most 10% of all correct answered evaluation episodes alarmed; checkpoints {48, 96, 192,
384}; paired bootstrap, 1,000 resamples, thresholds re-set in every resample. Episodes with no in-time checkpoint are never alarmed (lowest
score for AUROC).

## Hypotheses and decision rules
- H1 (primary): stack minus probe > 0; supported if the lower 95% bound > 0.
- H2 (non-inferiority of the transparent hospital score): hospital_banded minus probe; non-inferior if the lower 95% bound > -0.05.
- H3 (descriptive): for each pair of components, errors caught by both, only the first, only the second, each at its own 10% threshold;
  errors caught by any component.
- Secondary (descriptive): stack and hospital score minus the LLM judge; failure rate by banded level (stable 0, watch 1-2, concern 3-5,
  urgent 6-12); per-checkpoint AUROC with intervals.

## Pre-declared consequences
- H1 supported: layering independent non-LLM checks beats the best single check on this data (P5 supported, narrow).
- H1 not supported: on this data the best single internal-state monitor is as good as the combination; P5 remains Open.
- H2 non-inferior: a fully explainable, hospital-style score is within 5 points of the best learned monitor (P4 supported, narrow).
- H2 not non-inferior: transparency costs accuracy here; P4 remains Open.

## Run gating
The confirmatory analysis runs only via make confirmatory (RUN_CONFIRMATORY=1). make experiment, which the publish pipeline calls, exits
without analysing.
