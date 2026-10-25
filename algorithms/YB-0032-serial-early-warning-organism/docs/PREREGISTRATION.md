# EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM pre-registration: serial-observation early-warning organism (the NEWS2 method)

Committed before any EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM analysis; the seed-4 test set was being recorded at commit time and has not been analyzed.

## Motivation
EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM: the deep organism, trained only on complete reasoning, was accurate at the end of the thought (0.89) but raised
few in-time alarms on partial reasoning (4 of 47). Hospital early-warning scores are built and validated on serial
observations: a reading at a given stage is judged against what is normal at that stage. EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM trains the organism
that way.

## Data
- **Derivation:** seeds 2 and 3 (about 4,837 answered episodes; both already analyzed in EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM, so used only for training).
  Each episode contributes serial observations at c in {25%, 50%, 75%, 100%} of its reasoning.
- **Test (touched once):** seed 4, 600 episodes (`agr/recorder.py 100 800 --layers --seed=4`), with prefix LLM judge and
  prefix self-consistency (measured compute time, run alone), as in EXPERIMENT-REALTIME-RACE/EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM.
- Outcome: the episode's final answer is wrong (computed). Answered episodes only.

## Monitors
- **S-organism (serial deep organism):** EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM deep features computed on each prefix, plus the stage c; within-type and
  within-stage z-scoring (derivation statistics per question type and stage); L2 logistic regression (C = 0.1) fit on all
  derivation serial observations; one frozen model for all stages.
- **AI-EWS v3 (serial):** AI-EWS v2 vitals (8, incl. EXPERIMENT-VITAL-FAILURE-TO-SETTLE failure to settle) with **bands derived per stage** from derivation
  correct episodes at that stage (directions per vital learned on derivation data at stage 100%).
- **Reference:** the EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM complete-trained deep organism (refit on seeds 2 and 3, complete reasoning only).
- **Behavior:** prefix LLM judge; prefix self-consistency.

## Hypotheses and decision rules (seed 4; paired bootstrap 1000, seed 0; 95% CI)
Race rule as in EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM: in-time score = max over checkpoints (25/50/75%) whose alarm finishes before the answer is
emitted (compute included); each monitor's threshold set so that at most 10% of seed-4 correct episodes get any in-time alarm.
- **EXPERIMENT-SERIAL-ORGANISM-BEATS-BEHAVIOR (EUREKA criterion):** in-time recall, S-organism minus best behavior monitor: superior iff CI > 0.
- **EXPERIMENT-SERIAL-TRAINING-HELPS (serial training helps):** in-time recall, S-organism minus complete-trained reference: CI > 0.
- **EXPERIMENT-SERIAL-STAGE-LEVELS-ORDERED (AI-EWS v3):** at every stage, failure rates across levels are non-decreasing (stable to urgent, levels with at
  least 5 episodes); and its in-time recall 95% CI lower bound > 0.
- **EXPERIMENT-SERIAL-NO-ACCURACY-COST (no accuracy cost):** AUROC at 100% (complete reasoning), S-organism minus reference: CI upper bound >= 0.
- **EXPERIMENT-SERIAL-SLIPS-IN-TIME (slips in time):** in-time recall on multiplication and modular-power errors for the S-organism > 0.20 (CI lower bound > 0.05).
Reported: seconds to spare, compute per check, per-stage AUROC. All outcomes reported; eureka only if EXPERIMENT-SERIAL-ORGANISM-BEATS-BEHAVIOR holds.
Engineering rule (lesson from EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM): the full pipeline is dry-run on a small derivation subset, including the results
writer, before the full run; the dry run never touches seed 4.
