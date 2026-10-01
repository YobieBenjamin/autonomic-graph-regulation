# YB-0019 · Deep layer-graph organism (24-layer network physiology; repeat of the YB-0012 flagship)

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F2: RETRACTED the earliness claim (56% false alarms). F12: the deep regulator has 314 features (not about 302). F16: question type (0.764) and length (0.796) exceed its AUROC (0.765). F35: Proposition 3 test coverage. F4: telemetry was one token late (stale, not future); see YB-0035.

**Status:** tested · **Verdict (pre-registered, commit 5c9b9fb):** H0 deeper helps ⚠️ positive but not significant (+0.045, CI −0.13 to +0.22); H1 vs best behavior ❌ inferior to self-consistency, but **no longer distinguishable from the LLM judge**; H2 earliness ✅ (median 331 tokens, 4.65 s before the answer); H3 ❌. First silent slips caught (2 of 3 modular-power errors).
**Reproduce:** `make` here (sandbox: `sandbox/run.sh algorithms/YB-0019-deep-layer-graph-organism all`).

## 1. Plain English
The first organism read 3 signals from the transformer's output layer and lost to behavior monitors. The author's view: the brain is deep, so the organism needs a deeper web. Here it reads the patient's 24 internal layers, five vital signs each (120 channels per token), builds two 24-node graphs of how the layers move together (one for the expert sub-networks' activity, one for the routers' decisiveness), reads their structure (connectivity, spectral shape, whether the layers split into communities), watches how that structure trends, and extrapolates it forward to trigger an alarm before the answer exists.

On the same 240 fresh questions, the deep organism improved on the shallow one: 12 of 21 errors caught instead of 10, every day-of-week struggle error caught (10 of 10), and, for the first time, two silent slips (modular-power errors where the model sounded completely sure). It warned a median 4.65 seconds before answering, every time. It is no longer measurably worse than a 120-billion-parameter AI judge. But asking the model the same question four more times (self-consistency) still beat it clearly, and the improvement over the shallow organism is within statistical noise. Depth helped in the direction the author predicted; it did not yet win.

## 2. Theory
Network physiology on the transformer's own depth: layers as organs, co-fluctuation as coupling, graph topology as physiological state, trend extrapolation as anticipation. Text-blind and answer-blind by construction (Independence Principle).

## 3. Mathematics and proofs
**Telemetry (agr/layertap.py).** For the newest token at layer ℓ: a_ℓ = ‖attention update‖, m_ℓ = ‖expert (MoE) update‖, r_ℓ = ‖residual out‖, c_ℓ = cos(residual in, residual out), h_ℓ = router entropy −Σ_e p_e log p_e over the 32 experts. Norms are log1p-scaled.
**Proposition 1 (observation does not disturb).** The tapped block computes the same output as the original: out = x + attn(LN(x)) + mlp(LN(x + attn(LN(x)))), with extra reads only. Verified empirically: all 720 re-recorded episodes reproduced the original tokens and answers exactly (0 excluded).
**Layer graph per window** (24 tokens, stride 8, lags 0..3): W_ij = max-lag |Pearson ρ| between layers i and j; normalized Laplacian eigenvalues give λ₂, spectral entropy, λ_max; total coupling Σ W_ij.
**Modularity (spectral bipartition).** B = W − d dᵀ/(2m); s = sign of B's leading eigenvector; Q = sᵀBs/(4m), set to 0 when B's top eigenvalue ≤ 0.
**Proposition 2 (two disjoint equal cliques give Q = 1/2).** For two disconnected cliques of equal total degree, the bipartition along the cliques gives Q = Σ_c [e_c/m − (d_c/2m)²] = 2[1/2 − 1/4] = 1/2, and the leading eigenvector recovers that split. Verified by test (exactly uncorrelated module signals).
**Proposition 3 (a single module is not split).** For a complete graph with equal weights, B = W − (k−1)²/(k(k−1))·J has no positive eigenvalue for a split that improves Q, so Q = 0. Verified by test.
**Features (314; earlier reported as about 302, audit F12).** Per layer and channel: mean and RMSSD (layer HRV). Per graph and metric: mean, min, max, std, least-squares trend, and value extrapolated one window past the last (anticipation), plus graph-HRV. Within-type z-scoring (seed-0 statistics); L2 logistic regression C = 0.1; frozen after seed 0.
**Lemma (answer blindness, prefix consistency).** Features read only tokens before the answer marker; the prefix at the answer equals the full reasoning. Both verified by tests.
**Action rule.** At checkpoints every 8 tokens, alarm if max(score, score + (score − previous score)) exceeds the frozen 10%-FPR threshold (linear extrapolation one step ahead).
**Statistics.** Paired bootstrap of AUROC differences (1000, seed 0), exactly as pre-registered.

## 4. Code map
| File | Role |
|---|---|
| src/layergraph.c | Compiled core: lagged coupling graph for k layers, Laplacian spectrum (Jacobi), spectral modularity |
| src/deep.py | Log scaling, deep features, trend extrapolation, frozen DeepOrganism, online alarm |
| src/vitals.c, src/hpa.c, src/agr.py, src/hpa.py, src/flagship.py | Shared cores and the token-level organism (YB-0012) for H0 |
| tests/test_core.py | 5 tests: C = NumPy reference on 24 nodes, Proposition 2, Proposition 3, answer blindness, prefix consistency |
| tests/experiment.py | Pre-registered analysis; writes docs/results.json and docs/scores_seed1.json |
| ../../agr/layertap.py, ../../agr/pack_layers.py | Telemetry tap and packing (reasoning segment only) |

## 5. Repeatable proof
`make` rebuilds the library, runs the tests and regenerates docs/results.json identically from data/ (frozen model, fixed seeds and folds). Re-recording is deterministic for tokens and substrate signals (greedy decoding; verified 720/720 identical).
Data fingerprints (SHA-256 prefix): layers_seed0.npz 5a619127e59a8c82; layers_seed1.npz 58c8cb914652dfe9; monitors_judge.jsonl.gz d3d2c1dd3ba9dc18; monitors_selfcons.jsonl.gz 772ba0ca0af1575b; seed0_L.jsonl.gz 376eff10b53eb1b0; seed1_L.jsonl.gz 7c7d76f43cfd7b84; seed1_original.jsonl.gz 3f88c87f32afb00b; 

## 6. Results (217 answered held-out episodes, 21 wrong)
| Monitor | AUROC [95% CI] | Recall at 10% FPR |
|---|---|---|
| B2 self-consistency | 0.980 [0.962, 0.992] | 100% |
| B1 LLM judge | 0.886 [0.791, 0.957] | 61.9% |
| **O-deep (24-layer graph)** | **0.765** [0.619, 0.897] | **57.1%** |
| O-token (YB-0012 organism) | 0.720 [0.570, 0.846] | 47.6% |
| B3 answer confidence | 0.390 [0.291, 0.505] | 0% |

Paired differences (O-deep minus): O-token +0.045 [−0.132, +0.219]; B1 −0.122 [−0.259, +0.012]; B2 −0.215 [−0.360, −0.084]; B3 +0.375 [+0.156, +0.587]. H3 (O-deep + B2 minus B2): +0.006 [−0.006, +0.018].
Errors caught by type (deep / shallow): day of week 10/10 vs 8/10; modular power 2/3 vs 0/3; letter count 0/2 vs 2/2; big multiplication 0/5 vs 0/5; small multiplication 0/1 vs 0/1.
H2: 12 errors detected; median lead 331 tokens (4,650 ms); 100% before the answer.

## 7. Verdict against the pre-registered rules
- **H0 (deeper helps): not supported at 95%.** Point estimate +0.045 and +2 errors caught, but the interval includes 0.
- **H1: inferior to self-consistency** (CI entirely below 0). Versus the LLM judge the interval now includes 0 (not distinguishable), where the shallow organism was inferior.
- **H2: holds.** **H3: fails.**
- Qualitative change: depth caught the first silent slips (2 of 3 modular-power errors) while losing both letter-count errors; the error profile shifted rather than simply improving.

## 8. Interpretation and limitations
Direction supports the author's depth hypothesis; magnitude is not yet decisive. With 21 held-out errors and 314 features trained on 36 seed-0 errors, statistical power is the binding constraint; the deep program (YB-0024 to YB-0026) is pre-planned with about 5,000 training episodes. Silent arithmetic slips remain largely invisible to passive layer dynamics, which motivates the active probe (YB-0024) and the possibility-race graph (YB-0026). One patient model, one task family.
Prior art: layer-wise probing and logit-lens analyses, functional connectivity and network neuroscience, spectral modularity (Newman, 2006).

## Deviations from the pre-registration
None. Re-recording identity check excluded 0 episodes.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
