# YB-0009 · Physiological coupling graph: does the shape of how vital signs move together predict failure?

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** F17: topology features include the number of windows, a proxy for reasoning length; results pending a rerun without it (open).

**Status:** tested · **Verdict:** graph topology carries signal ✅ (95% CI above chance, barely); adds information beyond raw signals ❌ not at this node count.
**Reproduce:** `make` in this folder (sandbox: `sandbox/run.sh algorithms/YB-0009-physiological-coupling-graph all`).

## 1. Plain English
In medicine, network physiology looks not only at each vital sign but at how they move together: heart, breathing and brain rhythms couple and decouple as the body changes state. Here each vital sign of the patient transformer (uncertainty, confidence, margin, token timing, and their moment-to-moment variability) is a node, and an edge links two signals by how strongly they move together, allowing small time lags. For every stretch of 24 tokens we get a small graph, and we read its shape: how tightly it is knit (algebraic connectivity), how evenly organized (spectral entropy), how much total coupling, and how much that coupling itself fluctuates over time (graph-HRV).

Result: the graph's shape does predict wrong answers better than chance, even with question type controlled, but only weakly, and it adds nothing beyond the raw signals themselves. With only 4–6 token-level signals the graph is too small to carry much structure. The natural next step is a richer graph whose nodes are the transformer's 24 internal layers (YB-0019).

## 2. Theory
Network physiology: physiological state is expressed in the topology of coupling between organ systems, not only in each signal. Graph representation of the organism (docs/RESEARCH_PROGRAM.md): nodes = vital channels, edges = coupling, state = topology. Pre-registered: (1) topology predicts failure (AUROC 95% CI lower bound > 0.5); (2) it adds beyond raw per-channel statistics.

## 3. Mathematics and proofs
Channels X ∈ ℝ^{T×k} (mixed: entropy, top-1 probability, margin, |Δentropy|, latency, |Δlatency|; substrate: the first four). Window length w = 24, stride 8, maximum lag L = 3.
**Edge weight.** W_ij = max_{0≤g≤L} max(|ρ(x_i(t), x_j(t+g))|, |ρ(x_j(t), x_i(t+g))|) over the window, with ρ the Pearson correlation. So 0 ≤ W_ij ≤ 1 and W is symmetric with zero diagonal.
**Graph readout.** Normalized Laplacian L = I − D^{−1/2} W D^{−1/2}, eigenvalues 0 = λ1 ≤ λ2 ≤ … ≤ λk ≤ 2. Per window: algebraic connectivity λ2, spectral entropy −Σ p_i log p_i with p_i = λ_i/Σλ (bounded by log k), total coupling Σ_{i<j} W_ij, and λ_max. Per episode: mean, min, max, std over windows, plus graph-HRV = RMSSD of total coupling across windows.
**Proposition 1 (complete graph).** If all k channels are identical (non-constant), every W_ij = 1 and λ2 = k/(k−1), total coupling = k(k−1)/2. *Proof:* W = J − I (J all-ones), D = (k−1)I, so D^{−1/2}WD^{−1/2} = (J − I)/(k−1) with eigenvalues (k−1)/(k−1) = 1 (once) and −1/(k−1) (k−1 times); hence L has eigenvalues 0 and 1 + 1/(k−1) = k/(k−1). ∎ Test: k = 4 gives λ2 = 4/3 and total coupling 6.
**Proposition 2 (lag detection).** If x_j(t) = a·x_i(t − g) + c with a ≠ 0 and g ≤ L, then W_ij = 1. *Proof:* at lag g the two windowed series are affine images of each other, so |ρ| = 1, the maximum possible. ∎ Test: a 2-step lag is detected with L = 2 (weight > 0.99) and missed with L = 0 (< 0.9).
**Proposition 3 (independence).** For independent channels, E[ρ] = 0 and |ρ| = O(1/√w), so total coupling concentrates near 0 as w grows. Test: w = 1000 gives total coupling < 6 × 0.15 for 4 channels.
**Protocol.** Within-question-type z-scoring (YB-0015, Proposition 2), out-of-fold logistic regression (stratified 5-fold, seed 0), bootstrap 95% CIs (1000, seed 0). Answered episodes only.
The eigensolver is the cyclic Jacobi method reused from YB-0001.

## 4. Code map
| File | Role |
|---|---|
| src/coupling.c | Compiled core: lagged-correlation coupling graph per window, normalized Laplacian, Jacobi eigenvalues, readouts |
| src/graph.py | ctypes binding, NumPy reference, channel construction, episode graph features |
| tests/test_core.py | 5 tests: C = NumPy reference, Proposition 1, Proposition 2, Proposition 3, short episodes |
| tests/experiment.py | Pre-registered experiment; writes docs/results.json |
| data/episodes.jsonl.gz | Same 480 episodes as YB-0015 (SHA-256 begins a5b60ae4691a635c) |

## 5. Repeatable proof
Propositions 1–3 are proved above and checked by `make test`; `make` regenerates docs/results.json identically from the data file (deterministic windows, fixed folds and seeds).

## 6. Results (428 answered episodes, 36 wrong; all within question type)
| Features | AUROC [95% CI] |
|---|---|
| Coupling graph, mixed nodes (physical + substrate) | 0.655 [0.541, 0.758] |
| Coupling graph, substrate nodes only | 0.670 [0.543, 0.774] |
| Raw per-channel statistics (mean, std) | 0.702 [0.587, 0.808] |
| Raw + graph | 0.682 [0.559, 0.784] |

## 7. Verdict
- **Prediction 1 (topology predicts failure): holds, weakly.** Lower CI bound 0.541 > 0.5.
- **Prediction 2 (adds beyond raw): fails.** Raw + graph (0.682) does not beat raw alone (0.702); the difference is within noise.
- **Interpretation:** with 4–6 token-level channels, most topology is already implied by the channels themselves. The graph formalism is sound (proved properties hold); it needs richer nodes. Next: nodes = the patient's 24 internal layers (YB-0019), a genuinely network-scale physiology.

## 8. Limitations and prior art
Small graphs, 36 failures (wide intervals), one patient and task family, window and lag chosen a priori (not tuned). Prior art: network physiology and time-delay stability (Bashan, Ivanov et al., 2012), graph signal processing, functional connectivity in neuroscience. The new element is applying coupling-graph topology to a transformer's vital signs as an external monitor.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
