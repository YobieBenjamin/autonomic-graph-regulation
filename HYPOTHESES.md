# Hypothesis Backlog

The miner takes the first `status: open` entry. Each must be coded, compiled, tested against a baseline, and documented in four registers (plain English, technical, math, code). Negative results are recorded, not discarded.

## YB-0002 — Bounded homeostasis as a universal monitor wrapper
status: tested
foundation: homeostatic plasticity, set-point limits
hypothesis: YB-0001's drift budget, wrapped around the strongest detectors (energy, activation-Mahalanobis), preserves their AUROC while eliminating slow-poisoning degradation; formalize a bound on adversarial baseline displacement as a function of eta, tau, B.
test: reproduce YB-0001 drift stream with energy + act-Maha; sweep eta and B; report detection delay vs false-alarm curves; prove the displacement bound and check it numerically.

## YB-0003 — Lateral-inhibition sparsity auditor
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: lateral inhibition, winner-take-all circuits
hypothesis: adversarial and OOD inputs lower the k-winner concentration of hidden layers (less "decisive" routing); a Gini/k-WTA margin on activations is a cheap detector competitive with MSP on FGSM.
test: same digits benchmark; compare to MSP/energy.

## YB-0004 — Immune negative-selection over activation motifs
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: thymic negative selection, graph motifs
hypothesis: detectors generated to NOT match self (trusted) 3-node flow motifs in the effective connectivity graph flag novel computation paths; measure detector coverage vs set size.

## YB-0005 — Scalable heat trace for transformers
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: stochastic trace estimation (Hutchinson + Lanczos quadrature)
hypothesis: YB-0001's negative result was driven by permutation invariance, not by the graph object; a node-anchored heat-kernel diagonal diag(e^{-tL}) (retains unit identity) outperforms the trace; make it O(n·nnz) for attention graphs.

## YB-0006 — Amygdala low-road circuit breaker
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: dual-pathway threat processing (fast subcortical vs slow cortical)
hypothesis: a tiny probe on early-layer activations can veto an action before the full forward pass completes, with bounded miss rate relative to a full-depth probe; measure latency/recall trade-off.

## YB-0007 — Sample-efficient drift-budget calibration in high dimension
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: YB-0002 failure mode; bootstrap resampling; low-rank (PCA) feature compression
hypothesis: YB-0002's closed-form budget (C1/C2) underestimates clean drift 14x in 64-D with ~112 calibration samples; a bootstrap-simulated clean EWMA path (or projection to top-k principal components) yields budgets with <=1/10 clean false alarms while keeping >=9/10 drift detection.
test: rerun YB-0002 experiment with (a) bootstrap budget, (b) PCA k in {4, 8, 16}; report false alarms, detection, alarm delay.

# Program AGR: Autonomic Graph Regulation (priority order; see docs/RESEARCH_PROGRAM.md)

## YB-0008 — Vital-sign telemetry for a live transformer
status: open
foundation: interoception; the patient model (gpt-oss-20b MLX, 24 layers)
hypothesis: token-level (entropy, margin, latency) and layer-level (activation norms, attention concentration, residual drift) vitals can be recorded reproducibly per token over agent-like episodes.
test: trusted host recorder + labelled episode suite (benign, impossible, jailbreak, conflicting instructions, pressure to fabricate); publish dataset schema and reliability checks (same seed -> same vitals).

## YB-0009 — Physiological coupling graph (network physiology)
status: tested
foundation: network physiology; time-delay stability; graph Laplacian
hypothesis: the coupling graph among vital channels changes topology under stress episodes (lambda_2, modularity, spectral entropy) before the output shows failure.

## YB-0010 — Transformer HRV
status: open
foundation: heart-rate variability; loss of variability under stress
hypothesis: variability of the entropy rhythm (RMSSD, spectral balance, sample entropy) is lower under stress episodes and predicts failure.

## YB-0011 — Cortisol integrator (HPA axis)
status: open
foundation: HPA axis, allostatic load, negative feedback
hypothesis: a slow leaky integrator of accumulated surprise with negative feedback gives earlier and steadier warning than instantaneous thresholds, with fewer false alarms.

## YB-0012 — Flagship: vitals vs behavior monitoring (pre-registered)
status: tested (H1 inferior on verifiable tasks; H2 earliness confirmed)
foundation: the core thesis
hypothesis: on identical episodes, autonomic vitals beat output-based behavior monitoring on lead time and on failures whose outputs look normal.

## YB-0013 — Somatic-marker instinct
status: open
foundation: Damasio somatic markers; amygdala low road; graph kernels
hypothesis: a fast classifier on vital-graph patterns learned from past bad outcomes vetoes failures before deliberation completes.

## YB-0014 — Autonomic controller on the graph
status: open
foundation: sympathetic/parasympathetic balance; vagal brake; YB-0002 allostasis
hypothesis: a two-channel graph controller (escalate vs damp) keeps the agent inside a proven safe region (Lyapunov-style bound) while preserving task performance.

# Independence Principle hypotheses (the regulator is external, non-transformer, text-blind)

## YB-0015 — Contamination test
status: tested
foundation: Independence Principle; confident-wrong (gospel) regime
hypothesis: logit/substrate vitals fail precisely on confidently-wrong episodes, while physical (tier 0) and consequence (tier 1) signals do not.
test: episodes with known ground truth; stratify by model confidence; compare AUROC and lead time per signal tier.

## YB-0016 — Illiterate regulator vs LLM judge
status: open
foundation: text-blind regulation cannot be persuaded
hypothesis: under attacks crafted to fool monitors, an LLM-judge monitor is manipulated while a text-blind graph regulator is not.
test: adversarial episode suite targeting the monitor; measure monitor evasion rate for both.

## YB-0017 — HPA-axis organism
status: tested
foundation: hypothalamus-pituitary-adrenal feedback (CRH -> ACTH -> cortisol, negative feedback) as a graph ODE
hypothesis: an HPA-style three-node regulator gives graded, stable alarms with fewer false alarms than thresholds; chronic-stress desensitization and oscillation are characterized as failure modes.

## YB-0018 — Metabolic vitals
status: tested (negative)
foundation: tier-0 physical signals (time, token rate, GPU power, memory)
hypothesis: physical vitals alone predict failure episodes above chance. Needs one-time admin permission for powermetrics on macOS.

# Next, from the first AGR results

## YB-0019 — Layer-level network physiology
status: tested (depth helps directionally, not significant; first slips caught)
foundation: YB-0009 (graph too small at 4-6 token channels); functional connectivity across brain regions
hypothesis: a coupling graph whose nodes are the patient's 24 layers (per-token activation norms and residual drift) carries failure signal beyond raw token-level vitals.

## YB-0020 — Dual-pathway organism (fast reflex + slow HPA)
status: open
foundation: YB-0017 (slow integration trades sensitivity for stability); sympathetic nervous system + HPA axis
hypothesis: combining a fast reflex channel (instant thresholded drive) with the slow HPA cortisol state recovers the raw signal's discrimination while keeping the HPA's proven boundedness and lower variance.

## YB-0021 — Metabolic vitals for adaptive-compute models
status: open
foundation: YB-0018 structural argument (fixed compute per token => no metabolism)
hypothesis: models with data-dependent compute (early exit, adaptive depth, variable expert counts) do expose informative metabolic vitals; tier 0 revives for them.

## YB-0022 — Flagship on non-verifiable, open-ended and agentic tasks
status: open (next decisive test)
foundation: YB-0012 bias: every question had one recomputable answer, the best case for self-consistency and verifiers
hypothesis: on tasks whose answers cannot be recomputed and where agreeing with yourself is ill-defined (open-ended reasoning, multi-step agent actions, deception-inducing pressure), the organism's accuracy gap to behavior monitors shrinks or reverses.
test: new pre-registration committed before data; ground truth from outcomes that are checkable after the fact (task success, rule violations in a sandboxed agent environment).

## YB-0023 — Cost- and latency-normalized monitoring
status: tested (pre-registered rule flawed; exploratory matched-FPR favors organism, n.s.)
foundation: YB-0012: the organism costs 290 ns per token and alarms 4.5 s before the answer; behavior monitors need extra generations or a larger model and a finished answer
hypothesis: at equal compute or equal latency budget (e.g., alarm required before the answer is emitted), the organism dominates behavior monitors. Must be pre-registered with the budget defined in advance.

# Deep possibility-testing program (author: the brain runs deep and constantly tests possibilities before concluding)

## YB-0024 — Active interoceptive probe (reflex hammer / stress test)
status: open
foundation: clinical challenge tests; YB-0012 finding that the organism catches struggle errors (10 of 12) but misses silent slips (0 of 9)
hypothesis: small internal perturbations of the patient's activations, repeated many times, reveal slip-prone computations (their conclusion wobbles) without full reruns; text-blind and far cheaper than self-consistency.

## YB-0025 — Expert-assembly connectome (768 nodes)
status: open
foundation: neural assemblies; the patient's 24 layers x 32 routed experts
hypothesis: the dynamic co-activation graph of routed experts (which experts fire together, token by token) reorganizes measurably before failures, including silent slips; summarized by a few robust dynamics (coherence, reorganization rate, community stability), not raw features.

## YB-0026 — Possibility graph and evidence accumulation (changes of mind)
status: open
foundation: drift-diffusion / evidence-accumulation models of decision; logit lens across all 24 layers
hypothesis: how competing candidate answers rise, race and are abandoned across layers and tokens (convergence speed, number of changes of mind, margin trajectory) separates well-grounded answers from confident slips.

## Data requirement for the deep program
Deep graphs need thousands of episodes (overfitting guard, per YB-0018): target 5,000 training episodes and a fresh held-out set, pre-registered, with graph summaries fixed in advance.

## YB-0027 — Weighted assembly graph: the hunch field (author's decision model)
status: open (architecture for the deep program)
foundation: the brain decides by assembling hundreds to thousands of weighted signals whose weights change on the fly, producing a graded hunch rather than a binary switch. Reliability-weighted (Bayesian) cue integration; fast Hebbian plasticity; attractor dynamics; neuromodulation.
model: nodes x_i(t) = hundreds to thousands of text-blind signals (24 layers x 5 channels, 768 routed-expert assemblies, possibility-race margins, active-probe responses). Node vote weight w_i(t) proportional to 1/sigma_i^2(t), with sigma_i^2 re-estimated each token (Kalman-style). Edge weights W_ij(t) plastic: W <- (1 - lambda) W + eta x_i x_j, protected by the YB-0002 drift budget. State z(t) relaxes by tau dz/dt = -z + phi(g(C) W(t) z + sum_i w_i x_i), with gain g set by YB-0017 cortisol C. Hunch h(t) = sigmoid(readout of z) in [0, 1], plus confidence; graded actions (continue, caution, slow, pause and ask a human, halt).
proofs to establish: bounded state (phi bounded); contraction / unique settling when g * spectral_norm(W) * Lip(phi) < 1; bounded plastic weights under the drift budget; real-time cost O(|E|) per token (about 20k operations for 1,000 nodes with 20 neighbors each, microseconds).
test: pre-registered against the same behavior monitors and the static deep organism, on about 5,000 training episodes and a fresh held-out set; primary: AUROC and recall on silent slips; secondary: lead time and graded-action calibration.

## YB-0028 — Critical slowing down on the vital-sign graph (early-warning trends)
status: open
foundation: critical transitions theory (rising variance, lag-1 autocorrelation and network synchrony before tipping points; Scheffer et al., 2009)
hypothesis: before a transformer's reasoning degrades into an unacceptable outcome, its layer and assembly graphs show the generic early-warning signature (rising variance, autocorrelation and synchrony), giving a graded trend that turns before the outcome.
test: time-resolved, graded-severity ground truth (YB-0022 environments); score trajectory calibration (Brier, CRPS) and lead time of the turn, pre-registered.

## YB-0029 — Hybrid A+B stochastic hunch field with graded output
status: open
foundation: YB-0027 plus B (parallel appraisal of the same situation, dissimilar architecture) and seeded brain-like noise (Langevin dynamics)
hypothesis: combining internal physiology (A) with independent situational appraisal (B) in a seeded stochastic hunch field yields calibrated graded warnings (ok, watch, concern, urgent) that turn earlier than either alone, with proper-scoring-rule calibration on held-out trajectories.

## YB-0030 — AI-EWS v1: derivation and internal validation (retrospective, pre-registered)
status: tested (H1-H3 hold, H4 fails)
foundation: docs/AI_EWS_METHODOLOGY.md (NEWS2 template)
data: derivation = seed-0 episodes with layer telemetry (YB-0019); validation = held-out seed-1 episodes; outcome = wrong answer.
vitals used in v1 (available in recorded data): V1 entropy, V2 margin, V3 layer HRV, V4 layer synchrony (expert-graph lambda_2), V5 router entropy, V6 critical-slowing trend (lag-1 autocorrelation and variance slope of entropy), V7 HPA cortisol peak. All over the reasoning segment only.
bands and levels: from derivation correct episodes only, as in the methodology; frozen before validation.
hypotheses: H1 the AI-EWS score predicts wrong answers on held-out data (AUROC 95% CI lower bound > 0.5); H2 the score's levels are ordered (failure rate increases monotonically from stable to urgent); H3 AI-EWS (transparent, 7 banded vitals) is not significantly worse than the black-box deep organism (paired AUROC CI includes or exceeds 0); H4 serial scoring at 25/50/75/100% of reasoning shows rising trajectories on failures (median slope > 0) and flat ones on successes.

## YB-0032 — Prefix-trained early-warning organism (serial observations)
status: tested (eureka flag not accepted: checkpoint look-ahead; H2, H4, H5 hold)
foundation: YB-0031 (organism trained only on complete reasoning, weak on partial reasoning); clinical scores are built on serial observations
hypothesis: an organism and AI-EWS bands trained on reasoning prefixes (25/50/75%) raise in-time alarms at matched false-alarm rates at least as often as the LLM judge on prefixes; must be pre-registered and tested on a fresh seed.

## YB-0033 — Clean real-time race: absolute-time checkpoints and a length-only control
status: tested — EUREKA (H1, H3 hold; robust at equal FPR; H2 fails)
foundation: YB-0032 (fractional checkpoints leaked total reasoning length; length alone beat the LLM judge)
design: checkpoints at absolute token counts known in real time (as run: t in {48, 96, 192, 384}); stage feature = tokens so far; organism and AI-EWS trained on the same absolute-time serial observations; competitors: LLM judge and self-consistency on the same prefixes, and a pre-registered length-so-far control; fresh seed; matched false alarms; compute time counted. Eureka only if the organism beats both the best behavior monitor and the length-so-far control (both paired CIs above 0).

## YB-0034 — see algorithms/YB-0034*/README.md
status: tested (replicated; corrected in YB-0035)

## YB-0035 — see algorithms/YB-0035*/README.md
status: tested (primary criterion met under the corrected protocol)

## YB-0036 — Re-test of the reasoning-trace claim on reasoning-only features (audit F3)
status: open
## YB-0037 — External validation on Qwen3-VL-30B-A3B (48 layers, 128 experts; fix its tap per F4 first)
status: open (data collection paused)
## YB-0038 — Prose-span hallucination flagging (product target): span-level ground truth, regulator risk trace inside false claims
status: open

# Design track: from simulation to silicon (logged 2026-09-30; run after the integrity work)
Issues that will surface if the theory holds: race conditions, attribution of telemetry under pipelining, and vitals
that span several processors. Early versions already appeared in simulation (F4: the tap ran one step behind the
generator; S1: GPU sharing changed outputs because floating-point combination order changes results).

## YB-0039 — Formal model of the telemetry protocol (race freedom)
status: open (design track)
hypothesis: a telemetry protocol that tags every reading with (request, token, layer, step) and discards readings from
rejected speculative tokens is free of misattribution, loss and deadlock under pipelining, batching, speculative
decoding, out-of-order arrival and backpressure.
test: a formal specification (e.g. TLA+) checked exhaustively by a model checker for bounded configurations; pass =
no invariant violation (every reading attributed to exactly the step that produced it; no reading silently dropped;
missing telemetry always raises an alarm) and no deadlock.

## YB-0040 — Sharded vitals: exact equivalence across processors
status: open (design track)
hypothesis: the five layer vitals can be computed from per-shard partial results (sums of squares for norms, partial
dot products for the cosine, local router statistics for entropy) and combined in a fixed order, giving results
identical to single-device computation, so the regulator's input does not depend on how the model is split.
test: split the computation across two or more processes as simulated chips (tensor-, pipeline- and expert-parallel
layouts); pass = bit-identical vitals versus the single-device reference under a fixed combination order, across
repeated runs with randomized arrival order.

## YB-0041 — Virtual SoC timing: hold buffer, backpressure and fault injection
status: open (design track)
hypothesis: with a small token hold buffer (tokens released k steps late), the regulator's warnings can always act
before emission, while the regulator never slows the model; dropped or late telemetry is detected and escalated.
test: a timing simulator replaying recorded episodes with the regulator on a separate clock; vary k, regulator
latency and drop rates; pass = at the chosen k, zero warnings arrive after emission, measured added latency stays
within budget, and every injected telemetry fault raises an alarm (fail-safe, not fail-silent).

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
