# YB-0033 pre-registration: clean real-time race (absolute-time checkpoints, length controls)

Committed before seed 5 exists and before any YB-0033 analysis.

## Why
YB-0032's checkpoints sat at fractions (25/50/75%) of the total reasoning length, which a real-time monitor cannot
know; checkpoint position leaked that length, and length alone caught 15/46 errors in time (more than the LLM judge).
YB-0033 removes every source of future information and adds length-only competitors.

## Data
- **Derivation:** seeds 2, 3 and 4 (all previously analyzed; used only for training), answered episodes.
- **Test (touched once):** seed 5, 600 episodes (`agr/recorder.py 100 800 --layers --seed=5`), same six question types,
  patient gpt-oss-20b (MLX, greedy), 24-layer telemetry.
- Outcome: final answer wrong (computed).

## Checkpoints (real-time knowable)
Absolute token counts t in T = {48, 96, 192, 384}. A checkpoint exists for an episode only while it is still reasoning
(t < answer start); being still reasoning at t is information a real-time monitor has. No quantity derived from the
total reasoning length is used anywhere (features, normalization, stage labels, checkpoint placement).

## Monitors (all scored at every existing checkpoint)
- **Organism (A-organism):** YB-0019 deep features of the first t tokens plus log t; normalization per (question type, t)
  from derivation statistics; one L2 logistic model (C = 0.1) over all derivation serial observations at the same T.
- **AI-EWS v4:** AI-EWS v2 vitals (8) on the first t tokens; bands per checkpoint t from derivation correct episodes
  still reasoning at t; directions learned on derivation data at t = 384 (or the largest t with enough episodes).
- **Length controls:** C1 = t (still reasoning at token t); C2 = derivation percentile of t among episodes of the same
  question type (how unusually long this reasoning already is for its type).
- **Behavior:** LLM judge (gpt-oss-120b) on the question + first t tokens; self-consistency (2 continuations from the
  first t tokens, disagreement); both with measured compute time, run alone.

## Race rule and hypotheses (seed 5; paired bootstrap over wrong episodes, 1000, seed 0; 95% CI)
In-time score = max over checkpoints whose alarm finishes before the answer is emitted (compute time included; clock =
the seed-5 recording's per-token latencies). Each monitor's threshold: at most 10% of seed-5 correct episodes receive any
in-time alarm.
- **H1 (EUREKA criterion):** in-time recall, organism minus best behavior monitor, CI > 0 **and** organism minus best
  length control, CI > 0. EUREKA only if both hold.
- **H2:** AI-EWS v4 in-time recall minus best length control, CI > 0.
- **H3:** organism in-time recall minus best behavior monitor on errors from types where length has no signal in
  derivation data (within-type length AUROC < 0.6 on seeds 2-4), CI lower bound > 0 (reported with n).
- Reported: per-checkpoint AUROC of every monitor, seconds to spare, compute per check, silent-slip recall.
All outcomes reported. Engineering rule: the full analysis is dry-run on derivation data with stand-in monitor scores
before seed 5 is analyzed; the dry run never reads seed 5.
