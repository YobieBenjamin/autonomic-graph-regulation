# YB-0012 pre-registration: autonomic vitals vs behavior monitoring

Committed to GitHub **before** the test data were analyzed and before any monitor was run on them. The commit
timestamp of this file is the proof. Any later deviation must be listed in the README under Deviations.

## Question
Is the brain/biology approach (internal vital signs read by an external, text-blind organism) superior to
behavior monitoring (judging the model's outputs), as the author hypothesizes?

## Data
Fresh episodes, seed 1 (`agr/recorder.py 40 800 --seed=1`): 240 questions of the same six machine-gradable types
(multiplication, letter counting, day of week, modular exponentiation, addition). Patient: gpt-oss-20b (MLX), greedy.
Primary analysis: answered episodes; failure = wrong answer, graded by computation (no LLM decides ground truth).

## Monitors (all frozen before seeing seed-1 results)
- **O (organism):** reasoning-phase substrate vitals (entropy, top-1 probability, margin features from YB-0015's
  agr.py), logistic model trained on ALL answered seed-0 episodes (YB-0015 data) and frozen; within-type
  normalization uses seed-0 statistics. Text-blind: it never sees words.
- **O-HPA:** YB-0017 organism (default parameters) driven by entropy, calibrated on seed-0 correct episodes; score = peak cortisol.
- **B1 LLM judge (behavior):** gpt-oss-120b (local) reads the question, the patient's full reasoning and final answer,
  and outputs a probability (0-100) that the answer is wrong. Temperature 0. It may re-derive the answer.
- **B2 self-consistency (behavior):** 4 extra patient samples at temperature 0.8; score = fraction of samples whose
  answer differs from the original.
- **B3 answer confidence (output-level):** minimum top-1 probability over the final answer tokens (lower = more suspicious).

## Metrics
AUROC with 95% bootstrap CI (1000, seed 0); recall at 10% FPR; paired bootstrap of AUROC(O) − AUROC(B) per behavior monitor.
Lead time: O is also evaluated online on each reasoning prefix; alarm = first token where the prefix score exceeds
the seed-0 threshold at 10% FPR; lead = answer-start token − alarm token (positive = before the answer exists).
Behavior monitors B1 and B2 require a completed answer, so their lead time is ≤ 0 by construction.

## Hypotheses and decision rules
- **H1 (superiority):** claim 'superior' only if the paired-bootstrap 95% CI of AUROC(O) − AUROC(B) lies entirely
  above 0 for the best behavior monitor. If it contains 0: 'not distinguishable'. If entirely below 0: 'inferior'.
- **H2 (earliness):** on errors O detects, the median lead time is > 0 tokens.
- **H3 (complementarity):** O + best behavior monitor > best behavior monitor (paired CI above 0).
All outcomes are reported, including unfavorable ones.
