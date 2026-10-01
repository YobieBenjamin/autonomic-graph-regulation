# YB-0031 · Confirmatory test of the deep program (derive on seed 2, test once on fresh seed 3)

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F15: H5 (failure to settle) is driven by the day-of-week questions. F14: H4 used a test-set threshold; 'silent slip' is defined by question type. F16: its AUROC (0.89) exceeds question type (0.80) and length (0.73). F4 applies.

**Status:** tested · **EUREKA: false** (pre-registered, commit b177662). H1 real-time superiority ❌ inferior to the LLM judge. H2 accuracy: deep organism 0.89, **not distinguishable from the LLM judge**, inferior to self-consistency. H3 AI-EWS v2 levels ❌ not fully ordered. **H4 silent slips ✅ (60% caught). H5 failure to settle ✅ (p = 0.0007).**
**Reproduce:** `SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0031-confirmatory-deep-program all` (about 1 hour).

## 1. Plain English
This was the test built to make a breakthrough undeniable: every model, band and threshold was fitted on 4,800 episodes, then judged exactly once on 600 fresh ones that no analysis had ever seen, against the strongest behavior monitors, with false-alarm rates matched in advance.

The breakthrough claim failed. When warnings had to arrive before the model finished answering, counting each monitor's own compute time, the deep organism caught 4 of 47 wrong answers in time; a 120-billion-parameter AI judge reading the partial reasoning caught 12. The early lead seen in an earlier small test did not replicate.

Three things held, one of them a first. With nine times more training data, the organism's accuracy on complete reasoning rose from 0.77 to 0.89, statistically tied with that much larger judge at a sliver of the compute. It caught 60% of the silent slips (confidently delivered wrong answers) that earlier organisms missed entirely. And the pattern first glimpsed in YB-0030 was confirmed on fresh data: healthy reasoning calms down, failing reasoning does not settle, like a deteriorating patient.

## 2. Theory
Deep program under the Independence Principle and the AI-EWS methodology: text-blind physiology of the transformer (24-layer graph organism; banded early-warning score), judged on accuracy, earliness under a real deadline, silent slips, and settling.

## 3. Mathematics and proofs
Deep organism, race rules and AI-EWS as in YB-0019, YB-0023 and YB-0030 (their proofs carry over). New: **V8 failure to settle** = mean entropy over the last third of the reasoning minus mean over the first third, k = ⌊n/3⌋ ≥ 1.
**Proposition 1 (V8 closed form).** For three equal-length plateaus a, b, c, V8 = c − a. *Proof:* the first and last thirds are exactly the first and last plateaus. ∎ Tested (3, 2, 1 gives −2).
**Proposition 2 (V8 no look-ahead).** V8 on a prefix reads only tokens before the checkpoint. Tested.
**Proposition 3 (AI-EWS v2 bounds and monotonicity).** With 8 vitals, 0 ≤ S ≤ 24 and S is non-decreasing in each vital's risky direction (as YB-0030, Propositions 1-2). Tested.
**Matched false alarms (H1).** In-time score m_i = max over checkpoints whose alarm finishes before the deadline; threshold = 90th percentile of m_i on seed-3 correct episodes, so at most about 10% of correct episodes receive any in-time alarm. Paired bootstrap over wrong episodes (1000, seed 0).
Other statistics: AUROC with bootstrap CIs; paired AUROC bootstrap; slip recall bootstrap; one-sided Mann-Whitney for V8 in the direction learned on seed 2.

## 4. Code map
| File | Role |
|---|---|
| src/aiews.py | AI-EWS v1 vitals, v2 adds V8 settle, bands, score, levels |
| src/deep.py, src/layergraph.c | Deep 24-layer organism (YB-0019) |
| src/race.py | Deadline rules (YB-0023) |
| src/hpa.c, src/hpa.py, src/vitals.c, src/agr.py, src/flagship.py | Shared cores |
| tests/test_core.py | 6 tests: bounds, monotonicity (V8), V8 closed form, V8 no look-ahead, race rules, deep no look-ahead |
| tests/experiment.py | The pre-registered analysis; writes docs/results.json |
| data/ | seed 2 derivation (4,800; 6 layer shards), seed 3 test (600), judge and self-consistency outputs (full and prefix) |

## 5. Repeatable proof
The command above regenerates docs/results.json from data/ (deterministic features, fixed seeds). Episode recordings are reproducible token for token (greedy); latencies and monitor compute times are physical measurements.
Data fingerprints (SHA-256 prefix): layers_seed2_0.npz 6b241b7133cefde7; layers_seed2_1.npz 106a41cfe3544508; layers_seed2_2.npz 8fbf5acfa88df464; layers_seed2_3.npz 40df3794a0f0225d; layers_seed2_4.npz f22b41d2bb328028; layers_seed2_5.npz 95966943c68a619a; layers_seed3_0.npz 9f0aeb8621ba5ef9; monitors_judge.jsonl.gz f57499d32a582ae9; monitors_selfcons.jsonl.gz 912e73e5e9762508; prefix_judge.jsonl.gz 31e76a0fd329c6a0; prefix_selfcons.jsonl.gz 7854dbfe9eed3714; seed2_L.jsonl.gz 51802ba63f25bc92; seed3_L.jsonl.gz 173b29eef25be3fb; 

## 6. Results (derivation: 4,293 answered, 309 wrong; test: 544 answered, 47 wrong)
**H1, real-time race at matched false alarms:** deep organism 4/47 in time (8.5%, FPR 10.1%, 0.9 s to spare, 2.1 ms per check); LLM judge on prefixes 12/47 (25.5%, FPR 9.9%, 1.6 s to spare, 1.4 s per check); self-consistency on prefixes 0/47; AI-EWS v2 9/47 (19.1%, FPR 4.4%). Deep minus judge: −0.170 [−0.319, −0.021].
**H2, accuracy (complete reasoning), AUROC:** self-consistency 0.982 [0.972, 0.990]; LLM judge 0.947 [0.908, 0.980]; **deep organism 0.890 [0.826, 0.938]**; AI-EWS v2 0.776 [0.702, 0.847]; answer confidence 0.366 [0.304, 0.433]. Deep minus judge −0.057 [−0.131, +0.012]; deep minus self-consistency −0.092 [−0.157, −0.042].
**H3, AI-EWS v2 levels:** stable 27/484 (5.6%), watch 8/38 (21.1%), concern 9/14 (64.3%), urgent 3/8 (37.5%).
**H4, silent slips (multiplication and modular power):** 15 of 25 caught at 10% FPR (60%), CI [40%, 80%].
**H5, failure to settle:** V8 median −0.087 on wrong vs −0.179 on correct answers (settling is weaker on failures), one-sided p = 0.00069.

## 7. Verdict
- **No eureka.** H1 fails: the deep organism is inferior to the LLM judge at raising in-time alarms on partial reasoning. YB-0023's exploratory lead did not replicate.
- **H2:** the organism is statistically tied with a 6x larger LLM judge on accuracy (up from 0.765 in YB-0019 with 9x more training data) and inferior to self-consistency.
- **H3 fails** on ordering (urgent below concern, 8 cases); the score still discriminates (0.78) and its lower three levels are ordered.
- **H4 and H5 hold:** silent slips are now detectable (60%), and failure to settle is a confirmed, biologically shaped signature.

## 8. Interpretation and limitations
The organism was trained only on complete reasoning and then scored on partial reasoning; its knowledge lives at the end of the thought, so early detection was never trained. An early-warning organism must be trained on prefixes (as clinical scores are validated on serial observations), a hypothesis for the next pre-registration. Only 8 episodes reached urgent, too few to order reliably. One patient model and task family; latencies are from the tapped recording.

## Deviations from the pre-registration
1. The hunch field (YB-0027) was listed as a monitor but not implemented; no hypothesis depends on it.
2. The first analysis run crashed while writing results (a NumPy boolean in the JSON writer) after computing and before any output was saved or shown; the identical analysis was re-run once with a fixed writer. No test-set result was seen before the re-run.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
