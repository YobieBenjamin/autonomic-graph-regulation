# YB-0034 pre-registration: frozen replication of the YB-0033 eureka (fresh seed 6)

Committed before seed 6 exists.

## Design
Identical to YB-0033 (commit 300f037) in every respect: code (src/ and tests/experiment.py copied unchanged except the
test-seed file names), derivation data (seeds 2-4; the fit is deterministic, so the organism, AI-EWS v4 and length controls
are the same models), checkpoints T = {48, 96, 192, 384}, race rule, matched-false-alarm thresholds, competitors (LLM judge
and self-consistency at absolute checkpoints, run alone with measured compute; length controls C1 and C2).
Test (touched once): seed 6, 600 episodes (`agr/recorder.py 100 800 --layers --seed=6`).

## Hypotheses and decision rules (as YB-0033; paired bootstrap over wrong episodes, 1000, seed 0; 95% CI)
- **R1 (replication of the eureka):** organism minus best behavior monitor CI > 0 **and** organism minus best length
  control CI > 0. Replicated iff both hold.
- **R2 (robustness):** the same two comparisons at exactly equal realized false-alarm rates (tests/exploratory_equal_fpr.py,
  now pre-registered): both CIs > 0.
- **R3 (pooled estimate, reported):** seeds 5 and 6 pooled, organism minus judge and minus C1, with CIs.
All outcomes reported, including failure to replicate.
