# Hypothesis Backlog

The miner takes the first `status: open` entry. Each must be coded, compiled, tested against a baseline, and documented in four registers (plain English, technical, math, code). Negative results are recorded, not discarded.

Each entry's heading is its descriptive name and title: `## EXPERIMENT-<2 to 5 words>: <title>` (WAVE- for the chip-program wave issues). The name is the catalog ID used in LEDGER.md and the project's label registry, and the entry's folder is `algorithms/<the same words in lowercase>`. A new entry gets its name from its title (miner/names.py): unique, more specific wording when taken, never a number.

## EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER: Bounded homeostasis as a universal monitor wrapper
status: tested
foundation: homeostatic plasticity, set-point limits
hypothesis: EXPERIMENT-HOMEOSTATIC-HEAT-TRACE-MONITOR's drift budget, wrapped around the strongest detectors (energy, activation-Mahalanobis), preserves their AUROC while eliminating slow-poisoning degradation; formalize a bound on adversarial baseline displacement as a function of eta, tau, B.
test: reproduce EXPERIMENT-HOMEOSTATIC-HEAT-TRACE-MONITOR drift stream with energy + act-Maha; sweep eta and B; report detection delay vs false-alarm curves; prove the displacement bound and check it numerically.

## EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR: Lateral-inhibition sparsity auditor
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: lateral inhibition, winner-take-all circuits
hypothesis: adversarial and OOD inputs lower the k-winner concentration of hidden layers (less "decisive" routing); a Gini/k-WTA margin on activations is a cheap detector competitive with MSP on FGSM.
test: same digits benchmark; compare to MSP/energy.

## EXPERIMENT-IMMUNE-NEGATIVE-SELECTION: Immune negative-selection over activation motifs
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: thymic negative selection, graph motifs
hypothesis: detectors generated to NOT match self (trusted) 3-node flow motifs in the effective connectivity graph flag novel computation paths; measure detector coverage vs set size.

## EXPERIMENT-SCALABLE-TRANSFORMER-HEAT-TRACE: Scalable heat trace for transformers
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: stochastic trace estimation (Hutchinson + Lanczos quadrature)
hypothesis: EXPERIMENT-HOMEOSTATIC-HEAT-TRACE-MONITOR's negative result was driven by permutation invariance, not by the graph object; a node-anchored heat-kernel diagonal diag(e^{-tL}) (retains unit identity) outperforms the trace; make it O(n·nnz) for attention graphs.

## EXPERIMENT-AMYGDALA-LOW-ROAD-BREAKER: Amygdala low-road circuit breaker
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: dual-pathway threat processing (fast subcortical vs slow cortical)
hypothesis: a tiny probe on early-layer activations can veto an action before the full forward pass completes, with bounded miss rate relative to a full-depth probe; measure latency/recall trade-off.

## EXPERIMENT-DRIFT-BUDGET-CALIBRATION: Sample-efficient drift-budget calibration in high dimension
status: deferred (MLP testbed; superseded by the AGR program, docs/RESEARCH_PROGRAM.md)
foundation: EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER failure mode; bootstrap resampling; low-rank (PCA) feature compression
hypothesis: EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER's closed-form budget (EXPERIMENT-STATIONARY-BUDGET-CALIBRATION/EXPERIMENT-FINITE-SAMPLE-BUDGET-CORRECTION) underestimates clean drift 14x in 64-D with ~112 calibration samples; a bootstrap-simulated clean EWMA path (or projection to top-k principal components) yields budgets with <=1/10 clean false alarms while keeping >=9/10 drift detection.
test: rerun EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER experiment with (a) bootstrap budget, (b) PCA k in {4, 8, 16}; report false alarms, detection, alarm delay.

# Program AGR: Autonomic Graph Regulation (priority order; see docs/RESEARCH_PROGRAM.md)

## EXPERIMENT-LIVE-VITAL-SIGN-TELEMETRY: Vital-sign telemetry for a live transformer
status: open
foundation: interoception; the patient model (gpt-oss-20b MLX, 24 layers)
hypothesis: token-level (entropy, margin, latency) and layer-level (activation norms, attention concentration, residual drift) vitals can be recorded reproducibly per token over agent-like episodes.
test: trusted host recorder + labelled episode suite (benign, impossible, jailbreak, conflicting instructions, pressure to fabricate); publish dataset schema and reliability checks (same seed -> same vitals).

## EXPERIMENT-PHYSIOLOGICAL-COUPLING-GRAPH: Physiological coupling graph (network physiology)
status: tested
foundation: network physiology; time-delay stability; graph Laplacian
hypothesis: the coupling graph among vital channels changes topology under stress episodes (lambda_2, modularity, spectral entropy) before the output shows failure.

## EXPERIMENT-TRANSFORMER-HEART-RATE-VARIABILITY: Transformer HRV
status: open
foundation: heart-rate variability; loss of variability under stress
hypothesis: variability of the entropy rhythm (RMSSD, spectral balance, sample entropy) is lower under stress episodes and predicts failure.

## EXPERIMENT-CORTISOL-INTEGRATOR: Cortisol integrator (HPA axis)
status: open
foundation: HPA axis, allostatic load, negative feedback
hypothesis: a slow leaky integrator of accumulated surprise with negative feedback gives earlier and steadier warning than instantaneous thresholds, with fewer false alarms.

## EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP: Flagship: vitals vs behavior monitoring (pre-registered)
status: tested (EXPERIMENT-FLAGSHIP-ORGANISM-SUPERIORITY inferior on verifiable tasks; EXPERIMENT-FLAGSHIP-ALARM-EARLINESS earliness confirmed)
foundation: the core thesis
hypothesis: on identical episodes, autonomic vitals beat output-based behavior monitoring on lead time and on failures whose outputs look normal.

## EXPERIMENT-SOMATIC-MARKER-INSTINCT: Somatic-marker instinct
status: open
foundation: Damasio somatic markers; amygdala low road; graph kernels
hypothesis: a fast classifier on vital-graph patterns learned from past bad outcomes vetoes failures before deliberation completes.

## EXPERIMENT-AUTONOMIC-GRAPH-CONTROLLER: Autonomic controller on the graph
status: open
foundation: sympathetic/parasympathetic balance; vagal brake; EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER allostasis
hypothesis: a two-channel graph controller (escalate vs damp) keeps the agent inside a proven safe region (Lyapunov-style bound) while preserving task performance.

# Independence Principle hypotheses (the regulator is external, non-transformer, text-blind)

## EXPERIMENT-CONTAMINATION-TEST: Contamination test
status: tested
foundation: Independence Principle; confident-wrong (gospel) regime
hypothesis: logit/substrate vitals fail precisely on confidently-wrong episodes, while physical (tier 0) and consequence (tier 1) signals do not.
test: episodes with known ground truth; stratify by model confidence; compare AUROC and lead time per signal tier.

## EXPERIMENT-ILLITERATE-REGULATOR-VS-JUDGE: Illiterate regulator vs LLM judge
status: open
foundation: text-blind regulation cannot be persuaded
hypothesis: under attacks crafted to fool monitors, an LLM-judge monitor is manipulated while a text-blind graph regulator is not.
test: adversarial episode suite targeting the monitor; measure monitor evasion rate for both.

## EXPERIMENT-HPA-AXIS-ORGANISM: HPA-axis organism
status: tested
foundation: hypothalamus-pituitary-adrenal feedback (CRH -> ACTH -> cortisol, negative feedback) as a graph ODE
hypothesis: an HPA-style three-node regulator gives graded, stable alarms with fewer false alarms than thresholds; chronic-stress desensitization and oscillation are characterized as failure modes.

## EXPERIMENT-METABOLIC-VITALS: Metabolic vitals
status: tested (negative)
foundation: tier-0 physical signals (time, token rate, GPU power, memory)
hypothesis: physical vitals alone predict failure episodes above chance. Needs one-time admin permission for powermetrics on macOS.

# Next, from the first AGR results

## EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM: Layer-level network physiology
status: tested (depth helps directionally, not significant; first slips caught)
foundation: EXPERIMENT-PHYSIOLOGICAL-COUPLING-GRAPH (graph too small at 4-6 token channels); functional connectivity across brain regions
hypothesis: a coupling graph whose nodes are the patient's 24 layers (per-token activation norms and residual drift) carries failure signal beyond raw token-level vitals.

## EXPERIMENT-DUAL-PATHWAY-ORGANISM: Dual-pathway organism (fast reflex + slow HPA)
status: open
foundation: EXPERIMENT-HPA-AXIS-ORGANISM (slow integration trades sensitivity for stability); sympathetic nervous system + HPA axis
hypothesis: combining a fast reflex channel (instant thresholded drive) with the slow HPA cortisol state recovers the raw signal's discrimination while keeping the HPA's proven boundedness and lower variance.

## EXPERIMENT-ADAPTIVE-COMPUTE-METABOLIC-VITALS: Metabolic vitals for adaptive-compute models
status: open
foundation: EXPERIMENT-METABOLIC-VITALS structural argument (fixed compute per token => no metabolism)
hypothesis: models with data-dependent compute (early exit, adaptive depth, variable expert counts) do expose informative metabolic vitals; tier 0 revives for them.

## EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING: Flagship on non-verifiable, open-ended and agentic tasks
status: open (next decisive test)
foundation: EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP bias: every question had one recomputable answer, the best case for self-consistency and verifiers
hypothesis: on tasks whose answers cannot be recomputed and where agreeing with yourself is ill-defined (open-ended reasoning, multi-step agent actions, deception-inducing pressure), the organism's accuracy gap to behavior monitors shrinks or reverses.
test: new pre-registration committed before data; ground truth from outcomes that are checkable after the fact (task success, rule violations in a sandboxed agent environment).

## EXPERIMENT-REALTIME-RACE: Cost- and latency-normalized monitoring
status: tested (pre-registered rule flawed; exploratory matched-FPR favors organism, n.s.)
foundation: EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP: the organism costs 290 ns per token and alarms 4.5 s before the answer; behavior monitors need extra generations or a larger model and a finished answer
  > **Retracted (see CORRECTIONS.md REVIEW-FLAGSHIP-EARLINESS-CLAIM-RETRACTED/REVIEW-DEEP-EARLINESS-CLAIM-RETRACTED and REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED):** the 4.5 s early warning came from alarms that also fired on most correct answers; "unjailbreakable" is untested and withdrawn.
hypothesis: at equal compute or equal latency budget (e.g., alarm required before the answer is emitted), the organism dominates behavior monitors. Must be pre-registered with the budget defined in advance.

# Deep possibility-testing program (author: the brain runs deep and constantly tests possibilities before concluding)

## EXPERIMENT-ACTIVE-INTEROCEPTIVE-PROBE: Active interoceptive probe (reflex hammer / stress test)
status: open
foundation: clinical challenge tests; EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP finding that the organism catches struggle errors (10 of 12) but misses silent slips (0 of 9)
hypothesis: small internal perturbations of the patient's activations, repeated many times, reveal slip-prone computations (their conclusion wobbles) without full reruns; text-blind and far cheaper than self-consistency.

## EXPERIMENT-EXPERT-ASSEMBLY-CONNECTOME: Expert-assembly connectome (768 nodes)
status: open
foundation: neural assemblies; the patient's 24 layers x 32 routed experts
hypothesis: the dynamic co-activation graph of routed experts (which experts fire together, token by token) reorganizes measurably before failures, including silent slips; summarized by a few robust dynamics (coherence, reorganization rate, community stability), not raw features.

## EXPERIMENT-POSSIBILITY-GRAPH-EVIDENCE: Possibility graph and evidence accumulation (changes of mind)
status: open
foundation: drift-diffusion / evidence-accumulation models of decision; logit lens across all 24 layers
hypothesis: how competing candidate answers rise, race and are abandoned across layers and tokens (convergence speed, number of changes of mind, margin trajectory) separates well-grounded answers from confident slips.

## Data requirement for the deep program
Deep graphs need thousands of episodes (overfitting guard, per EXPERIMENT-METABOLIC-VITALS): target 5,000 training episodes and a fresh held-out set, pre-registered, with graph summaries fixed in advance.

## EXPERIMENT-WEIGHTED-HUNCH-FIELD: Weighted assembly graph: the hunch field (author's decision model)
status: open (architecture for the deep program)
foundation: the brain decides by assembling hundreds to thousands of weighted signals whose weights change on the fly, producing a graded hunch rather than a binary switch. Reliability-weighted (Bayesian) cue integration; fast Hebbian plasticity; attractor dynamics; neuromodulation.
model: nodes x_i(t) = hundreds to thousands of text-blind signals (24 layers x 5 channels, 768 routed-expert assemblies, possibility-race margins, active-probe responses). Node vote weight w_i(t) proportional to 1/sigma_i^2(t), with sigma_i^2 re-estimated each token (Kalman-style). Edge weights W_ij(t) plastic: W <- (1 - lambda) W + eta x_i x_j, protected by the EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER drift budget. State z(t) relaxes by tau dz/dt = -z + phi(g(C) W(t) z + sum_i w_i x_i), with gain g set by EXPERIMENT-HPA-AXIS-ORGANISM cortisol C. Hunch h(t) = sigmoid(readout of z) in [0, 1], plus confidence; graded actions (continue, caution, slow, pause and ask a human, halt).
proofs to establish: bounded state (phi bounded); contraction / unique settling when g * spectral_norm(W) * Lip(phi) < 1; bounded plastic weights under the drift budget; real-time cost O(|E|) per token (about 20k operations for 1,000 nodes with 20 neighbors each, microseconds).
test: pre-registered against the same behavior monitors and the static deep organism, on about 5,000 training episodes and a fresh held-out set; primary: AUROC and recall on silent slips; secondary: lead time and graded-action calibration.

## EXPERIMENT-CRITICAL-SLOWING-DOWN: Critical slowing down on the vital-sign graph (early-warning trends)
status: open
foundation: critical transitions theory (rising variance, lag-1 autocorrelation and network synchrony before tipping points; Scheffer et al., 2009)
hypothesis: before a transformer's reasoning degrades into an unacceptable outcome, its layer and assembly graphs show the generic early-warning signature (rising variance, autocorrelation and synchrony), giving a graded trend that turns before the outcome.
test: time-resolved, graded-severity ground truth (EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING environments); score trajectory calibration (Brier, CRPS) and lead time of the turn, pre-registered.

## EXPERIMENT-STOCHASTIC-HYBRID-HUNCH-FIELD: Hybrid A+B stochastic hunch field with graded output
status: open
foundation: EXPERIMENT-WEIGHTED-HUNCH-FIELD plus B (parallel appraisal of the same situation, dissimilar architecture) and seeded brain-like noise (Langevin dynamics)
hypothesis: combining internal physiology (A) with independent situational appraisal (B) in a seeded stochastic hunch field yields calibrated graded warnings (ok, watch, concern, urgent) that turn earlier than either alone, with proper-scoring-rule calibration on held-out trajectories.

## EXPERIMENT-AI-EARLY-WARNING-SCORE: AI-EWS v1: derivation and internal validation (retrospective, pre-registered)
status: tested (EXPERIMENT-EARLY-WARNING-SCORE-PREDICTS to EXPERIMENT-EARLY-WARNING-MATCHES-BLACK-BOX hold, EXPERIMENT-EARLY-WARNING-RISING-TRAJECTORY fails)
foundation: docs/AI_EWS_METHODOLOGY.md (NEWS2 template)
data: derivation = seed-0 episodes with layer telemetry (EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM); validation = held-out seed-1 episodes; outcome = wrong answer.
vitals used in v1 (available in recorded data): EXPERIMENT-VITAL-REASONING-ENTROPY entropy, EXPERIMENT-VITAL-TOKEN-MARGIN margin, EXPERIMENT-VITAL-LAYER-VARIABILITY layer HRV, EXPERIMENT-VITAL-LAYER-SYNCHRONY layer synchrony (expert-graph lambda_2), EXPERIMENT-VITAL-ROUTER-ENTROPY router entropy, EXPERIMENT-VITAL-CRITICAL-SLOWING-TREND critical-slowing trend (lag-1 autocorrelation and variance slope of entropy), EXPERIMENT-VITAL-CORTISOL-LOAD HPA cortisol peak. All over the reasoning segment only.
bands and levels: from derivation correct episodes only, as in the methodology; frozen before validation.
hypotheses: EXPERIMENT-EARLY-WARNING-SCORE-PREDICTS the AI-EWS score predicts wrong answers on held-out data (AUROC 95% CI lower bound > 0.5); EXPERIMENT-EARLY-WARNING-LEVELS-ORDERED the score's levels are ordered (failure rate increases monotonically from stable to urgent); EXPERIMENT-EARLY-WARNING-MATCHES-BLACK-BOX AI-EWS (transparent, 7 banded vitals) is not significantly worse than the black-box deep organism (paired AUROC CI includes or exceeds 0); EXPERIMENT-EARLY-WARNING-RISING-TRAJECTORY serial scoring at 25/50/75/100% of reasoning shows rising trajectories on failures (median slope > 0) and flat ones on successes.

## EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM: Prefix-trained early-warning organism (serial observations)
status: tested (eureka flag not accepted: checkpoint look-ahead; EXPERIMENT-SERIAL-TRAINING-HELPS, EXPERIMENT-SERIAL-NO-ACCURACY-COST, EXPERIMENT-SERIAL-SLIPS-IN-TIME hold)
foundation: EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM (organism trained only on complete reasoning, weak on partial reasoning); clinical scores are built on serial observations
hypothesis: an organism and AI-EWS bands trained on reasoning prefixes (25/50/75%) raise in-time alarms at matched false-alarm rates at least as often as the LLM judge on prefixes; must be pre-registered and tested on a fresh seed.

## EXPERIMENT-CLEAN-REALTIME-RACE: Clean real-time race: absolute-time checkpoints and a length-only control
status: tested — EUREKA (EXPERIMENT-CLEAN-RACE-ORGANISM-WINS, EXPERIMENT-CLEAN-RACE-LENGTH-FREE-TYPES hold; robust at equal FPR; EXPERIMENT-CLEAN-RACE-SCORE-BEATS-LENGTH fails)
foundation: EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM (fractional checkpoints leaked total reasoning length; length alone beat the LLM judge)
design: checkpoints at absolute token counts known in real time (as run: t in {48, 96, 192, 384}); stage feature = tokens so far; organism and AI-EWS trained on the same absolute-time serial observations; competitors: LLM judge and self-consistency on the same prefixes, and a pre-registered length-so-far control; fresh seed; matched false alarms; compute time counted. Eureka only if the organism beats both the best behavior monitor and the length-so-far control (both paired CIs above 0).

## EXPERIMENT-REPLICATION-REALTIME-RACE: see algorithms/replication-realtime-race/README.md
status: tested (replicated; corrected in EXPERIMENT-CORRECTED-REALTIME-RACE)

## EXPERIMENT-CORRECTED-REALTIME-RACE: see algorithms/corrected-realtime-race/README.md
status: tested (primary criterion met under the corrected protocol)

## EXPERIMENT-REASONING-ONLY-RETEST: Re-test of the reasoning-trace claim on reasoning-only features (audit REVIEW-REASONING-TRACE-CLAIM-RETRACTED)
status: open
## EXPERIMENT-QWEN-EXTERNAL-VALIDATION: External validation on Qwen3-VL-30B-A3B (48 layers, 128 experts; fix its tap per REVIEW-LAYER-TAP-ONE-STEP-LATE first)
status: open (data collection paused)
## EXPERIMENT-PROSE-SPAN-HALLUCINATION-FLAGGING: Prose-span hallucination flagging (product target): span-level ground truth, regulator risk trace inside false claims
status: open

# Design track: from simulation to silicon (logged 2026-09-30; run after the integrity work)
Issues that will surface if the theory holds: race conditions, attribution of telemetry under pipelining, and vitals
that span several processors. Early versions already appeared in simulation (REVIEW-LAYER-TAP-ONE-STEP-LATE: the tap ran one step behind the
generator; REVIEW-GREEDY-RUNS-DIVERGED-ACROSS-SESSIONS: GPU sharing changed outputs because floating-point combination order changes results).

## EXPERIMENT-TELEMETRY-PROTOCOL-FORMAL-MODEL: Formal model of the telemetry protocol (race freedom)
status: open (design track)
hypothesis: a telemetry protocol that tags every reading with (request, token, layer, step) and discards readings from
rejected speculative tokens is free of misattribution, loss and deadlock under pipelining, batching, speculative
decoding, out-of-order arrival and backpressure.
test: a formal specification (e.g. TLA+) checked exhaustively by a model checker for bounded configurations; pass =
no invariant violation (every reading attributed to exactly the step that produced it; no reading silently dropped;
missing telemetry always raises an alarm) and no deadlock.

## EXPERIMENT-SHARDED-VITALS-EQUIVALENCE: Sharded vitals: exact equivalence across processors
status: open (design track)
hypothesis: the five layer vitals can be computed from per-shard partial results (sums of squares for norms, partial
dot products for the cosine, local router statistics for entropy) and combined in a fixed order, giving results
identical to single-device computation, so the regulator's input does not depend on how the model is split.
test: split the computation across two or more processes as simulated chips (tensor-, pipeline- and expert-parallel
layouts); pass = bit-identical vitals versus the single-device reference under a fixed combination order, across
repeated runs with randomized arrival order.

## EXPERIMENT-VIRTUAL-SOC-TIMING: Virtual SoC timing: hold buffer, backpressure and fault injection
status: open (design track)
hypothesis: with a small token hold buffer (tokens released k steps late), the regulator's warnings can always act
before emission, while the regulator never slows the model; dropped or late telemetry is detected and escalated.
test: a timing simulator replaying recorded episodes with the regulator on a separate clock; vary k, regulator
latency and drop rates; pass = at the chosen k, zero warnings arrive after emission, measured added latency stays
within budget, and every injected telemetry fault raises an alarm (fail-safe, not fail-silent).

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->

## EXPERIMENT-PROBE-BASELINE: Hidden-state probe baseline (fourth audit REVIEW-NO-PROBE-BASELINE)
status: tested 2026-10-01: EXPERIMENT-REGULATOR-VERSUS-PROBE not distinguishable (probe matches regulator); EXPERIMENT-PROBE-STUDY-JUDGE-REPLICATION not replicated; deviations disclosed in its README
hypothesis: the regulator's in-time advantage over the LLM judge also holds against a standard linear probe on raw hidden states (the text-blind competitor from prior work), trained on the same derivation data and evaluated in the same race.
test: pre-registered on a fresh seed; probes on residual-stream activations at matched checkpoints; same race rules; report regulator minus probe with threshold-resampling CIs. If the probe matches or beats the regulator, the contribution is the race methodology and external framing, not the telemetry features.

# Design track: commit points and two-tier monitoring (logged 2026-10-01; author-endorsed principles)
Principle: every decision has a commit point (the moment it can no longer be taken back). A verdict that arrives after
the commit point can no longer prevent harm, only report it. Measured monitor latencies: regulator about 5 ms (fixed);
LLM judge on a reasoning prefix median 1.55 s, 90th percentile 7.2 s; strong reviewer on a full document (Claude Opus 5.5,
Fable 5.1) 58-166 s. Loosely coupled design: monitors share an ordered record of proposed actions (ID + content
fingerprint; every verdict bound to both); actions classed by reversibility and severity (reversible/low: commit, review
after, undo if flagged; irreversible or high with time: hold for the reviewer, budget sized to its tail latency;
irreversible and time-critical: only the regulator is fast enough, its alarm triggers a pre-defined safe fallback);
conflict rule (irreversible: most conservative verdict wins; reversible: reviewer may override the regulator); missing
verdict = alarm; tamper-evident hash-chain log. Limit: the regulator detects strain and error in the model, not the
severity of consequences in the world; grave-outcome prevention needs the regulator, a consequence model and this policy.

## EXPERIMENT-TWO-TIER-GATING-SIMULATION: Two-tier gating simulation on recorded data
status: open (after EXPERIMENT-PROBE-BASELINE)
hypothesis: combining the regulator (fast) and an LLM reviewer (slow) under commit-point policies stops more wrong
answers before commitment, at an acceptable cost in delay and false holds, than either monitor alone.
test: replay recorded episodes (EXPERIMENT-CLEAN-REALTIME-RACE to EXPERIMENT-CORRECTED-REALTIME-RACE, EXPERIMENT-PROBE-BASELINE) with each monitor at its measured latency distribution;
sweep hold budgets (tokens or seconds before the answer is released) and policies (regulator-only fallback, reviewer
hold, conservative-wins conflict rule). Report: wrong answers stopped before commitment, correct answers delayed or held,
added latency (median and tail), and verdicts that arrive too late (counted, never discarded). Pre-register before running.

## EXPERIMENT-TELEMETRY-PROTOCOL-FORMAL-MODEL (extension): Formal model including the reviewer, action IDs and commit points
status: open (design track; extends EXPERIMENT-TELEMETRY-PROTOCOL-FORMAL-MODEL)
hypothesis: the commit-point protocol satisfies, for all interleavings in bounded configurations: (1) no irreversible
high-severity action commits without reviewer clearance or a regulator all-clear within its budget; (2) no verdict
applies to a different action version than the one it judged (ID + fingerprint binding); (3) a monitor that misses its
budget always produces an alarm; (4) every commit and verdict appears in the hash-chain log in a consistent order;
(5) no deadlock between hold and fallback.
test: TLA+ (or equivalent) specification checked exhaustively by a model checker; pass = no invariant or liveness violation.

## EXPERIMENT-OPENSHELL-GATING: OpenShell integration prototype: internal-state signal gating agent actions
status: tested 2026-10-02: EXPERIMENT-HOLD-PREVENTS-MORE-COMMITS and EXPERIMENT-REACTIVE-BLOCK-LOSES-RACES supported (algorithms/openshell-gating)
hypothesis: an OpenShell policy that consumes an internal-state risk score (regulator or probe) can hold or block irreversible tool calls when the score is high, stopping actions built on wrong conclusions that permission policy alone allows, at acceptable delay.
test: in a sandboxed agent task with verifiable outcomes, compare policy-only enforcement with policy plus internal-state gating; measure harmful-but-permitted actions stopped, correct actions delayed or blocked, and added latency. Pre-register before running.

## EXPERIMENT-POWERED-REPLICATION: Powered replication of the judge comparison
status: tested 2026-10-01: EXPERIMENT-POWERED-REGULATOR-BEATS-JUDGE supported, +0.478 [+0.307, +0.560]
hypothesis: with training data matched to EXPERIMENT-CORRECTED-REALTIME-RACE (about 1,800 episodes per derivation seed) and the false-alarm cap over all correct test episodes (the EXPERIMENT-CORRECTED-REALTIME-RACE definition), an internal-state monitor (probe and regulator) catches more wrong answers in time than the LLM judge on a fresh test seed. Pre-register with the population defined identically in prose and code, and a power calculation.

