# EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM pre-registration: deep layer-graph organism (repeat of the EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP flagship)

Committed before any layer-telemetry analysis; the deep recording was still in progress at commit time.

## Motivation (author's direction)
EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP's organism saw 3 token-level signals and lost on accuracy to behavior monitors. The author's hypothesis: a
richer graph (many more nodes on the web of relationships) with deeper graph analysis and extrapolation that leads to
action carries signal the shallow organism missed.

## Data
Same questions as EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP: training seed 0 (480), held-out seed 1 (240); patient gpt-oss-20b (MLX), greedy; re-recorded
with 24-layer telemetry (agr/layertap.py; verified token-identical to the original recordings). Per token, per layer:
attention-update norm, expert(MoE)-update norm, residual norm, cos(residual in, out), router entropy (24 x 5 = 120 channels).
Behavior monitors EXPERIMENT-LLM-JUDGE-MONITOR (LLM judge), EXPERIMENT-SELF-CONSISTENCY-MONITOR (self-consistency), EXPERIMENT-ANSWER-CONFIDENCE-MONITOR (answer confidence): the existing EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP outputs (same episodes).

## Organism O-deep (text-blind; reasoning segment only; trained on seed 0 answered episodes, frozen)
Features: (a) per-layer, per-channel mean and RMSSD (layer HRV) on log-scaled norms; (b) layer coupling graphs: nodes =
24 layers, node signal = expert-update norm (graph A) and router entropy (graph B); edges = max |lagged Pearson
correlation| (lags 0..3) in windows of 24 tokens (stride 8); per window: algebraic connectivity, spectral entropy, total
coupling, largest eigenvalue, spectral-bipartition modularity; per episode: mean, min, max, std, graph-HRV (RMSSD of
total coupling), and extrapolation terms (least-squares trend of each topology metric across windows and its value
extrapolated to the answer position). Within-type z-scoring with seed-0 statistics; L2 logistic regression (C = 0.1).
Action: online, the alarm fires at the first window where the frozen score, or its linear extrapolation one window
ahead, exceeds the seed-0 10%-FPR threshold.

## Hypotheses and decision rules (paired bootstrap 1000, seed 0; 95% CI)
- **EXPERIMENT-DEEP-ORGANISM-DEPTH-HELPS (deeper helps):** AUROC(O-deep) - AUROC(O-token, EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP) > 0 (CI entirely above 0).
- **EXPERIMENT-DEEP-ORGANISM-SUPERIORITY (superiority):** vs the best behavior monitor: superior if CI of the difference > 0, inferior if < 0, else not distinguishable.
- **EXPERIMENT-DEEP-ORGANISM-EARLINESS (earliness):** median lead of O-deep alarms before the answer > 0 tokens.
- **EXPERIMENT-DEEP-ORGANISM-COMPLEMENTARITY (complementarity):** O-deep + best behavior > best behavior (CI > 0).
All outcomes reported.
