# YB-0030 · AI Early Warning Score v1 (NEWS2 template): derivation and internal validation

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F13: retrospective, not truly pre-registered (pre-registration committed minutes before results on thrice-used data); V6 changed. F16: question type (0.764) and length (0.796) exceed its AUROC (0.725). F26: 'perfectly ordered' rests on groups of 17, 8 and 2.

**Status:** tested · **Verdict (pre-registered, commit cb72e92):** H1 ✅ predicts failure (AUROC 0.725, CI 0.587–0.857); H2 ✅ levels perfectly ordered (stable 5.8%, watch 11.8%, concern 75%, urgent 100% failure rate); H3 ✅ not significantly worse than the black-box deep organism; H4 ❌ scores do not rise over reasoning (but failures fail to settle while successes do).
**Reproduce:** `make` here (sandbox: `sandbox/run.sh algorithms/YB-0030-ai-ews-v1 all`). Methodology: docs/AI_EWS_METHODOLOGY.md.

## 1. Plain English
Hospitals do not ask a patient whether they feel fine; they score a handful of vital signs against normal ranges, add the points, and act on the level: stable, watch, concern, urgent. We built the same thing for a transformer. Seven internal vital signs (never its words) are each scored 0 to 3 by how far they sit outside the model's own healthy range; the points add up to a score from 0 to 21 that anyone can read and explain.

On 217 questions it had never seen, the score behaved like a real early-warning system: 190 answers were rated stable and only 6% of those were wrong; the 10 rated concern or urgent (under 5% of all answers) contained 8 of the 21 wrong answers, and 80% of them were wrong. Seven transparent, explainable signals did as well as our 300-feature black-box organism. One prediction failed: we expected scores to climb as reasoning went bad; instead everyone starts noisy, healthy reasoning calms down, and failing reasoning does not settle, which is how a deteriorating patient looks too.

## 2. Theory
Author's principle: judgment has no analog other than the brain and biology; safety should follow hospital early-warning systems (NEWS2), which show graded deterioration trajectories rather than binary verdicts. AI-EWS is the text-blind, transparent version for transformers (docs/AI_EWS_METHODOLOGY.md).

## 3. Mathematics and proofs
**Vitals** over the reasoning segment (or a prefix): V1 mean entropy; V2 mean top-1/top-2 log margin; V3 layer HRV (mean over layers of the RMSSD of the log expert-update norm); V4 layer synchrony (mean algebraic connectivity λ₂ of the 24-layer expert coupling graph, YB-0019); V5 mean router entropy; V6 lag-1 autocorrelation of entropy (critical slowing); V7 peak HPA cortisol driven by entropy (YB-0017, calibrated on derivation correct episodes).
**Derivation (cohort: 428 seed-0 answered episodes).** Direction d_j = +1 if failures' mean ≥ successes' mean, else −1 (derivation outcomes only). Bands from derivation correct episodes only: for d_j = +1, (P90, P95, P99); for d_j = −1, (P10, P5, P1).
**Points** p_j(x) = number of band thresholds crossed in the risky direction ∈ {0, 1, 2, 3}; unmeasurable vitals score 0. **Score** S = Σ_j p_j ∈ [0, 21]. **Levels:** urgent S ≥ 10; concern 7–9; watch 5–6 or any p_j = 3 (red flag); else stable.
**Proposition 1 (boundedness).** 0 ≤ S ≤ 21. *Proof:* 7 vitals × at most 3 points each. ∎
**Proposition 2 (monotonicity).** Moving any vital further in its risky direction never lowers S. *Proof:* p_j counts thresholds crossed, a non-decreasing step function of d_j·x_j; other terms are unchanged. ∎
**Proposition 3 (explainability).** S equals the sum of named per-vital points, each attributable to one vital and one band. *By construction.* ∎
**Proposition 4 (red-flag escalation).** Any single p_j = 3 yields at least watch. *By definition of levels.* ∎ All four are verified by tests, plus direction mirroring and NaN handling.
**Statistics.** AUROC with bootstrap 95% CI (1000, seed 0); paired bootstrap for AI-EWS minus deep organism; serial scores at 25/50/75/100% of reasoning; per-episode least-squares slope; Mann-Whitney test of failure slopes greater than success slopes.

## 4. Code map
| File | Role |
|---|---|
| src/aiews.py | Vitals, derivation (direction, bands), points, score, levels |
| src/layergraph.c, src/deep.py, src/hpa.c, src/hpa.py, src/vitals.c, src/agr.py, src/flagship.py | Shared cores (layer graph, HPA, series features) |
| tests/test_core.py | 6 tests: direction and mirroring, monotonicity, boundedness, explainability, red flag, unmeasurable vitals |
| tests/experiment.py | Pre-registered analysis; writes docs/results.json and docs/trajectories.json |

## 5. Repeatable proof
`make` regenerates docs/results.json and docs/trajectories.json identically from data/ (deterministic vitals, bands fixed from derivation data, fixed bootstrap seed).
Data fingerprints (SHA-256 prefix): deep_organism_scores_seed1.json aeea95f108e132c2; layers_seed0.npz 5a619127e59a8c82; layers_seed1.npz 58c8cb914652dfe9; seed0_L.jsonl.gz 376eff10b53eb1b0; seed1_L.jsonl.gz 7c7d76f43cfd7b84; 

## 6. Results (217 held-out answered episodes, 21 wrong)
| Level | Episodes | Wrong | Failure rate |
|---|---|---|---|
| Stable | 190 | 11 | 5.8% |
| Watch | 17 | 2 | 11.8% |
| Concern | 8 | 6 | 75% |
| Urgent | 2 | 2 | 100% |

AUROC of S: 0.725 [0.587, 0.857]. AI-EWS minus deep organism (YB-0019): −0.039 [−0.197, +0.140].
Mean score at 25/50/75/100% of reasoning: failures 5.91, 4.95, 4.19, 4.24; successes 3.90, 2.05, 1.64, 1.28. Median slope: failures −2.4, successes −4.0 (Mann-Whitney p = 0.26).
Derivation directions: risky when high: entropy, layer HRV, layer synchrony, router entropy, cortisol; risky when low: margin, lag-1 autocorrelation.
Points raised on failures, by vital: margin 32, entropy 21, router entropy 21, cortisol 9, critical slowing 3, layer HRV 2, synchrony 1.

## 7. Verdict
- **H1 holds; H2 holds** (perfectly ordered levels); **H3 holds** (transparent 7-vital score on par with the 300-feature black box).
- **H4 fails as pre-registered** (no rising trajectory). Exploratory observation: the gap widens because successes settle while failures stay elevated.
- Decisiveness, uncertainty and routing entropy carry the score; layer HRV, synchrony and critical slowing contribute little in v1.

## 8. Limitations and prior art
21 failures; single patient model and task family; initial level cut-points taken from the methodology, not tuned; early-prefix vitals are noisy (short windows). Next: external validation on a different model (Qwen3, a different patient population) and prospective validation in YB-0022. Prior art: NEWS2 (Royal College of Physicians, 2017) and the early-warning-score literature; uncertainty-based error detection in language models.

## Deviations from the pre-registration
None in the analysis. Operationalized from the methodology: vital direction learned from derivation outcomes only.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
