# YB-0015 · Contamination test: which vital signs may the organism trust?

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F3: RETRACTED 'the reasoning trace detects errors and is not contaminated': the tier-2 features used the whole generation and the answer segment; no reasoning-only feature was tested. Re-test open.

**Status:** tested · **Verdict:** gospel premise ✅ confirmed; contamination hypothesis ❌ not supported for reasoning-phase substrate signals; physical timing ⚠️ weak once question type is controlled.
**Reproduce:** `make` in this folder (or `sandbox/run.sh algorithms/YB-0015-contamination-test all` from the repo root).

## 1. Plain English
The author's thesis: watching a transformer's output fails, because the output always sounds confident ('gospel') whether it is right or wrong, so safety must come from internal vital signs. This experiment asked a stricter question: are the transformer's own internal statistics (how uncertain it is, token by token) trustworthy, or contaminated by the same confidence problem? And do physical signals (timing, effort) catch what the internal statistics miss?

We gave the patient model (gpt-oss-20b) 480 questions a computer can grade exactly, recorded its vital signs at every token, and graded every answer by machine. No AI judged anything.

- **The output really is gospel.** 75% of wrong answers (27 of 36) were delivered with at least 90% confidence on every answer token. Anyone watching the output saw a confident answer.
- **The vital signs during the model's reasoning gave most of them away.** Uncertainty signals recorded while it was thinking, before the confident answer, flagged 59% of the confidently wrong answers at a 10% false-alarm rate, with question type controlled (70% without that control). Internal signals beat output watching, as the thesis predicts, but the substrate signals were less contaminated than feared.
- **Physical timing was weak.** Once question type is accounted for, timing and effort barely beat a coin flip. A fixed-size transformer spends about the same compute per token, so timing may simply not carry stress; real power draw (YB-0018) is the next test.

## 2. Theory
Independence Principle (docs/RESEARCH_PROGRAM.md): signals are ranked by independence from the transformer's statistics: tier 0 physical (latency, effort), tier 2 substrate (entropy, probabilities). The contamination hypothesis says tier-2 signals fail exactly when the model is confidently wrong. Pre-registered before data: **P1** a meaningful share of errors is confident and the substrate tier misses them at 10% FPR; **P2** the physical tier catches a meaningful share of what the substrate tier misses.

## 3. Mathematics and proofs
**Signals.** For next-token distribution p_t: entropy H_t = −Σ_v p_t(v) log p_t(v); top-1 probability π_t = max_v p_t(v); margin m_t = log p_(1) − log p_(2). Latency ℓ_t = time between tokens t−1 and t (prefill excluded). Effort = number of generated tokens.
**Episode features.** For a series x_1..x_n: mean, std, **RMSSD** = √(Σ(x_{i+1}−x_i)²/(n−1)) (the heart-rate-variability statistic), max, min, least-squares slope, spike fraction (share above mean + 2·std); over the whole generation and over the answer segment (tokens after the final-channel marker).
**Proposition 1 (C core correctness).** The C routine equals the closed forms: a constant series gives std = RMSSD = slope = 0; a unit ramp gives slope = RMSSD = 1; one spike of 100 in 100 zeros gives spike fraction 0.01. *Proof:* direct substitution into the definitions; verified in tests, with exact agreement against an independent NumPy implementation on random series (n = 2, 3, 17, 400). ∎
**Protocol (why the numbers are not optimistic).** Scores are out-of-fold predictions of a standardized logistic regression under stratified 5-fold cross-validation (seed 0): no episode is scored by a model that saw it. Recall at 10% FPR uses a threshold set only on correct episodes' scores (their 90th percentile). 95% confidence intervals: 1000 bootstrap resamples (seed 0).
**Proposition 2 (category control).** Within-category z-scoring maps each feature to mean 0, variance 1 inside each question type, so a feature that merely identifies the type carries no signal. *Proof:* if f(x) = g(category(x)), f is constant within a category, its z-score is 0 for every member, hence independent of the label. ∎ Within-category results are therefore the fair test; raw results are shown alongside.
**Exclusion rule.** 52 episodes hit the 800-token cap without answering; they are excluded from the primary analysis, because effort = cap would identify them trivially and inflate the physical tier.

## 4. Code map
| File | Role |
|---|---|
| src/vitals.c | Compiled core: series features (mean, std, RMSSD, max, min, slope, spikes) |
| src/agr.py | ctypes binding, NumPy reference, per-episode tier features |
| tests/test_core.py | 5 tests: C vs NumPy, closed forms, edge cases |
| tests/experiment.py | Pre-registered analysis; writes docs/results.json and docs/oof_scores.npy |
| data/episodes.jsonl.gz | The 480 recorded episodes (agr/recorder.py; patient gpt-oss-20b MLX) |

## 5. Repeatable proof
- Data fingerprint: SHA-256 of data/episodes.jsonl.gz begins **a5b60ae4691a635c**.
- Deterministic question set (seed 0, `agr/recorder.py 80 800`) and deterministic analysis (fixed seeds and folds).
- `make` rebuilds the C core, runs the proofs as tests, and regenerates docs/results.json identically from the data file. Re-recording reproduces the tier-2 signals exactly (greedy decoding); tier-0 latencies are physical, so they reproduce statistically, not bit for bit.

## 6. Results (428 answered episodes, 36 wrong)
Errors by type: count 4/80, modpow 10/29 answered, mul_hard 9/79, weekday 13/80, add_hard 0/80, mul_easy 0/80.

| AUROC [95% CI] | Raw | Within question type (fair test) |
|---|---|---|
| Tier 0 physical (timing, effort) | 0.671 [0.584, 0.752] | 0.557 [0.429, 0.663] |
| Tier 2 substrate (entropy, probability, margin) | **0.864** [0.805, 0.918] | **0.681** [0.566, 0.793] |
| Combined | 0.852 [0.790, 0.910] | 0.676 [0.554, 0.789] |

Gospel regime: 27 of 36 errors (75%) had every answer token at p ≥ 0.9.
At 10% FPR, within type: substrate recall 52.8% overall and **59.3% on confident errors**; physical recall 30.6% overall and 37.0% on confident errors; physical caught 2 of the 17 errors the substrate tier missed (raw: 5 of 15).

## 7. Verdict on the predictions
- **P1: partly.** First half holds strongly: most errors are confidently delivered (75%), so output watching is blind to them, which is the author's core premise. Second half fails: reasoning-phase substrate signals catch most confident errors. The answer tokens are contaminated (confident); the reasoning trace is not.
- **P2: not supported.** Physical timing adds little once question type is controlled (CI includes 0.5; 2 of 17 misses caught).
- **Implication for the organism:** trust substrate signals from the reasoning phase, not the answer phase; treat timing as weak; test true metabolic power (YB-0018) before discarding tier 0.

## 8. Limitations and prior art
36 errors, so confidence intervals are wide. One patient model, one task family (verifiable arithmetic and lookup), greedy decoding. One ~1 minute publish window overlapped recording and episode start times were not yet stored, so affected episodes (~10 of 480, tier 0 only) cannot be identified; the recorder now stamps t_unix. Related work: token-level uncertainty and semantic entropy for error detection (Farquhar et al., 2024); confidence calibration of language models. The new element is the tiered contamination test under the Independence Principle.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
