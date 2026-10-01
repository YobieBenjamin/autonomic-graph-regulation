# Error and hallucination detection prompt: four-model comparison (2026-10-01)

PROMPT.md was applied, unchanged and one model at a time, to seeded.md: the technical v4 blog draft with 9 planted errors
(ground_truth.json: arithmetic x3, inconsistency x2, math, overclaim, citation, external fact). run_models.py ran the
models; score.py scores findings against the planted errors (scores.json). Raw outputs: out_*.txt.

| Model | Planted caught | Genuine pre-existing issues | False alarms | Seconds |
|---|---|---|---|---|
| Claude Fable 5.1 | 9/9 | 2 (audit count; coupling formula implied an asymmetric W, code is symmetric) | 0 | 166 |
| Claude Opus 5.5 | 9/9 | 2 (audit count; regulator always in time) | 0 | 58 |
| gpt-oss-120b (local) | 3/9 | 0 | 1 (swapped the all/monitorable false-alarm rates) | 53 |
| Qwen3-VL-30B (local) | 0/9 | 0 | n/a: repetition loop, JSON never closed | 570 |

Both Claude models marked a 2026 citation beyond their training as unverifiable rather than wrong, as instructed.
Limitations: one document, nine planted errors, one run per model, keyword-based matching checked by hand.
