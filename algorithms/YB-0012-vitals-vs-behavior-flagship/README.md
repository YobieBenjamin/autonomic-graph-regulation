# YB-0012 · Flagship: autonomic vitals vs behavior monitoring (pre-registered)

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F1: RETRACTED the earliness claim ('alarms 4.5 s before the answer, 100% of detections'); the online alarm also fires on 89.3% of correct answers. F16: on this test set question type alone (AUROC 0.764) and length alone (0.796) exceed the regulator (0.72). S3: the per-type breakdown (10/12 struggle, 0/9 slips) is now reproducible (archive/audit/artifacts/). Superseded by YB-0033 to YB-0035.

**Status:** tested · **Verdict (pre-registered rules):** H1 superiority ❌ **inferior** to the best behavior monitor; H2 earliness ✅ confirmed (alarms a median 291 tokens, about 4.5 s, before the answer exists); H3 complementarity ❌.
**Reproduce:** `make` in this folder (sandbox: `sandbox/run.sh algorithms/YB-0012-vitals-vs-behavior-flagship all`). Pre-registration: docs/PREREGISTRATION.md, commit bd83719, pushed before any analysis.

## 1. Plain English
This was the decisive test of the author's thesis that reading a transformer's internal vital signs is superior to watching its behavior. On 240 fresh questions nothing had been tuned on, we compared the text-blind organism (trained only on the earlier questions, then frozen) against three behavior monitors: a large AI judge that reads the patient's reasoning and answer and can redo the work, self-consistency (ask the patient four more times and see whether it agrees with itself), and how confident the final answer sounded.

- **On accuracy, the thesis lost.** Asking the model again (self-consistency, 98% AUROC) and an AI verifier (89%) both beat the organism (72%), and by the pre-registered rule the organism is inferior. It adds nothing on top of self-consistency.
- **The gospel premise held, emphatically.** How confident the final answer sounded was worse than useless (39%, below a coin flip): wrong answers sounded more confident than right ones. Watching what the output shows is blind.
- **On timing, the organism won outright.** When it caught an error, it raised the alarm a median of about 4.5 seconds and 291 tokens before the answer even existed, every time. The behavior monitors cannot act until the answer is complete, and they cost extra work: self-consistency reruns the model four times, the judge runs a model six times larger.

The honest reading: on these tasks, behavior monitors that spend extra compute are more accurate; the organism is earlier and nearly free. See section 8 for what that means for the thesis and the product.

## 2. Theory
The author's thesis: transformers are statistical machines whose outputs always sound confident ('gospel'), so
monitoring behavior (judging outputs) is blind exactly when it matters, while an external, text-blind organism reading
internal vital signs can see trouble, and see it earlier. YB-0015 showed output confidence is uninformative for most
errors (75% confidently wrong) and that reasoning-phase substrate vitals carry signal. This experiment is the decisive
head-to-head against behavior monitors that industry would actually deploy, on fresh held-out questions.
Pre-registration: docs/PREREGISTRATION.md, committed as bd83719 (2026-09-28 12:48:39 PDT) before any analysis.

## 3. Mathematics and proofs
**Ground truth.** y = 1 if the patient's answered final answer is wrong, computed exactly from the question (no model decides truth).
**Organism O.** Features φ(r) ∈ ℝ²¹: the seven series features of YB-0015 (mean, std, RMSSD, max, min, slope, spike
fraction) for each of entropy, top-1 probability and margin, computed on the **reasoning segment only** (tokens before
the final-answer marker). Within-type z-scoring with seed-0 statistics; standardized logistic regression (C = 0.5)
fit on all 428 answered seed-0 episodes; frozen. Score s_O(r) = P(y = 1 | φ(r)).
**Lemma 1 (answer blindness).** s_O(r) does not depend on any answer token. *Proof:* φ reads only indices
t < final_start of each channel; answer tokens have indices ≥ final_start; the model is fixed after seed 0. ∎
Verified by test: replacing every answer-token entropy with 9.0 leaves φ unchanged.
**Lemma 2 (prefix consistency).** For t ≥ final_start, the prefix score s_O(r, t) equals s_O(r). *Proof:* the prefix
reads indices < min(t, final_start) = final_start. ∎ Verified by test. This makes the online alarm well defined.
**O-HPA.** YB-0017 organism (default parameters) driven by S_t = max(0, (H_t − median)/IQR) of reasoning-phase
entropy, median and IQR from seed-0 correct episodes; score = peak cortisol. Proved positive and bounded (YB-0017).
**Behavior monitors.** B1: LLM judge probability (gpt-oss-120b, temperature 0, sees question, full reasoning and
answer). B2: self-consistency, fraction of 4 temperature-0.8 re-samples whose answer differs. B3: 1 − min top-1
probability over answer tokens (output confidence).
**Decision rule (H1).** Δ_B = AUROC(O) − AUROC(B). Paired bootstrap: resample episodes with replacement (1000, seed 0),
compute Δ_B on each resample, take the 2.5 and 97.5 percentiles. Superior iff the lower bound > 0; inferior iff the
upper bound < 0; otherwise not distinguishable. Pairing is valid because both monitors score the same episodes.
**Lemma 3 (bootstrap sanity).** If two monitors give identical scores, every resampled Δ = 0, so the interval is [0, 0].
Verified by test.
**Lead time (H2).** Threshold τ = 90th percentile of out-of-fold seed-0 scores on correct episodes (10% FPR, frozen).
For each wrong answer with s_O > τ, the alarm token is the first t ∈ {16, 24, …, final_start} with s_O(r, t) > τ;
lead = final_start − t tokens (and the measured wall-clock time of those tokens). Behavior monitors B1 and B2 need the
completed answer, so their lead is ≤ 0 by construction.
**Complementarity (H3).** Out-of-fold (5-fold) logistic combination of s_O and the best behavior score, compared by paired bootstrap.

## 4. Code map
| File | Role |
|---|---|
| src/vitals.c, src/hpa.c | Compiled core (series features; HPA RK4), built into one library |
| src/agr.py, src/hpa.py | Bindings and references (from YB-0015 and YB-0017) |
| src/flagship.py | Reasoning-phase features, frozen Organism and HPA organism, paired bootstrap |
| tests/test_core.py | 5 tests: C = references (vitals, HPA), Lemma 2, Lemma 1, Lemma 3 |
| tests/experiment.py | The pre-registered analysis; writes docs/results.json |
| docs/PREREGISTRATION.md | Committed before analysis (bd83719) |
| data/ | seed0 (training, from YB-0015), seed1 (held-out test), judge and self-consistency outputs |
| ../../agr/monitors.py | Behavior monitors B1 and B2 (host) |

## 5. Repeatable proof
`make` rebuilds the library, runs the lemmas as tests and regenerates docs/results.json identically from data/
(frozen model, fixed seeds and folds). Data fingerprints are listed in section 6. Re-running the monitors reproduces B1
(temperature 0) closely and B2 statistically (it samples at temperature 0.8 with fixed per-episode seeds).

## 6. Results (217 answered held-out episodes, 21 wrong; organism frozen from 428 seed-0 episodes)
| Monitor | Type | AUROC [95% CI] | Recall at 10% FPR |
|---|---|---|---|
| B2 self-consistency | behavior | **0.980** [0.962, 0.992] | 100% |
| B1 LLM judge (gpt-oss-120b) | behavior | **0.886** [0.791, 0.957] | 61.9% |
| O organism (reasoning-phase vitals) | internal, text-blind | 0.720 [0.570, 0.846] | 47.6% (same at the frozen seed-0 threshold) |
| O-HPA organism | internal, text-blind | 0.665 [0.562, 0.767] | 9.5% |
| B3 answer confidence | output | 0.390 [0.291, 0.505] | 0% |

Paired bootstrap, AUROC(O) − AUROC(B) [95% CI]: vs B2 −0.260 [−0.408, −0.128]; vs B1 −0.166 [−0.312, −0.023]; vs B3 +0.330 [+0.112, +0.526].
O-HPA minus B: vs B2 −0.315 [−0.415, −0.212]; vs B1 −0.222 [−0.340, −0.102]; vs B3 +0.274 [+0.090, +0.445].
H3: out-of-fold O + B2 minus B2: +0.001 [−0.012, +0.012].
H2: 10 errors detected at the frozen threshold; median lead 291 tokens (4,465 ms measured); 100% of alarms before the answer.
Data fingerprints (SHA-256 prefix): monitors_judge.jsonl.gz d3d2c1dd3ba9dc18; monitors_selfcons.jsonl.gz 772ba0ca0af1575b; seed0.jsonl.gz a5b60ae4691a635c; seed1.jsonl.gz 3f88c87f32afb00b; 

## 7. Verdict against the pre-registered rules
- **H1 (superiority): inferior.** The best behavior monitor (B2) beats O; the paired CI lies entirely below 0. O is also inferior to B1. O is superior only to the output-confidence monitor B3.
- **H2 (earliness): holds.** Every detected error was flagged before the answer existed (median 291 tokens, 4.5 s).
- **H3 (complementarity): fails.** O adds nothing measurable to B2.
- The organism generalizes (held-out AUROC 0.72, CI above 0.5), consistent with YB-0015.

## 8. Interpretation and limitations
**What this does and does not overturn.** It overturns 'superior to behavior monitoring' *for accuracy on verifiable tasks*. It supports two of the thesis's pillars: output appearance is blind or inverted (B3 below chance), and internal vitals give early warning that behavior monitors structurally cannot.
**Why the behavior monitors did so well here (known bias of this task family).** Every question has one exactly derivable answer. That is the best case for self-consistency (wrong answers are unstable across samples) and for a verifier (it can recompute the answer). On open-ended or agentic work, where answers cannot be recomputed and 'agreeing with yourself' is ill-defined, their advantage may shrink. That is a hypothesis for the next test (YB-0022), not a result.
**Cost and timing were not part of the pre-registered primary metric.** B2 used 4 extra full generations per question (about 11.6 s each run here); B1 used a model about 6× larger (about 10 s per verdict); O costs 290 ns per token and needs no extra generation. A cost- and latency-normalized comparison is exploratory and must be pre-registered separately.
**Limitations.** 21 errors (wide intervals); one patient model; one task family; greedy decoding for the patient; the judge and patient are from the same model family.
**Prior art.** Self-consistency (Wang et al., 2022); LLM-as-a-judge and verifiers; uncertainty-based error detection (semantic entropy, Farquhar et al., 2024).

## Deviations from the pre-registration
None in the analysis. Operational: the self-consistency monitor crashed at startup (an argument-parsing bug) and was restarted before producing any output; the analysis chain was changed to wait until both monitors had covered every answered episode.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
