# Research program: Autonomic Graph Regulation (AGR) for AI

## Thesis (author: Yobie Benjamin)
1. Transformers are statistical machines, not brains (established in *Garbage In, Gospel Out*).
2. Their outputs are always fluent, confident "gospel", whether or not the internals behind them are sound. So
   **watching outputs fails**: the outside looks the same either way, and behavior is not predictive.
3. Therefore safety must be engineered the way biology does it: continuous **internal vital signs** (the analogues of
   heart rate, HRV, respiration, cortisol) drive **autonomic regulation** and **instinct**, which a judgment layer turns
   into decisions, sometimes wrong, but early.
4. The whole system is represented and analyzed with **graph mathematics**.

## The Independence Principle (author: Yobie Benjamin)
The safety system must not be a transformer, must not contain one, and must not rely on a transformer's account of
itself; otherwise it inherits the same statistical failure modes (contamination). It is an **external organism** that
interacts with transformers only through a narrow interface (sensory transducers in, effectors out), like the vagus nerve.
- **No LLM in the safety loop**: no LLM judges or transformer monitors. The regulator is deterministic graph dynamics in C.
- **Illiterate by design**: the regulator never processes text or meaning, only numeric signals, so it cannot be
  jailbroken or prompt-injected.
- **Effectors, not arguments**: throttle, pause, require a human, halt.
- (LLMs are still used as research tooling to write and review code; never as part of the safety model.)

### Signal tiers by independence from the transformer
| Tier | Signal | Biology | Contamination |
|---|---|---|---|
| 0 physical/metabolic | compute time, token rate, GPU power, memory pressure | heart rate, respiration, metabolism | lowest |
| 1 consequence (nociception) | measurable harm to the environment: resources, integrity, blast radius | pain | low |
| 2 substrate | activations, logits read externally | ECG/EEG | medium: shares miscalibration (confidently wrong = low entropy) |
| excluded | the model's words, self-reports, stated reasoning, LLM judgments | asking the patient | highest |

## Biological model -> AI analogue
| Biology | AI analogue (measured on a live transformer) |
|---|---|
| Heart rate | Per-token uncertainty (entropy of the next-token distribution) |
| HRV | Variability of that rhythm (RMSSD, spectral balance, sample entropy) |
| Respiration | Action tempo: retries, loops, repeated attempts |
| Cortisol / HPA axis | Slow leaky integrator of accumulated surprise and conflict, with negative feedback |
| Interoception | The system predicting its own next internal state; the error is "anxiety" |
| Allostasis | Adaptive set points with hard limits (proven in YB-0002) |
| Instinct (somatic markers) | Fast learned match of internal-state patterns to past bad outcomes, veto before deliberation |
| Judgment (prefrontal) | Integration of instinct + evidence under explicit false-alarm vs miss costs |

## Graph representation
- **Vital-sign graph** G_t = (V, E_t, W_t). Nodes: physiological channels (token-level: entropy, top-k margin,
  latency, length; layer-level: per-layer activation norms, attention concentration, residual-stream drift across the
  24 layers of the instrumented model). Edges: coupling between channels over sliding windows, measured by time-delay
  stability (network physiology), coherence, or transfer entropy (directed).
- **State is topology.** Healthy: flexible, modular coupling. Stress: rigid hyper-synchrony or fragmentation. Measures:
  algebraic connectivity (lambda_2), Laplacian spectral entropy, modularity, Kuramoto order parameter r(t), and
  **graph-HRV** (variability of edge weights over time).
- **Regulation is control on the graph.** Homeostatic set points per node (YB-0002 bounded), an HPA-like slow node
  with a negative-feedback edge (cortisol), a damping edge (vagal brake), an escalation edge (sympathetic).
- **Instinct is a fast graph classifier** (graph kernels / motifs -> learned danger); **judgment is an integration node**.

## Instruments
- **Worker model** (writes code, free): gpt-oss-120b in LM Studio.
- **Patient model** (instrumented, free): gpt-oss-20b in MLX, full logits and all 24 layers' activations.
  The vitals recorder is trusted code run on the host (MLX needs the Apple GPU); model-written analysis code
  runs only in the Docker sandbox on recorded datasets.

## Falsification (pre-registered flagship, YB-0012)
Same episodes, two monitors: autonomic vitals vs behavior monitoring (output classifiers). Primary metrics: AUROC for
episode failure, and **lead time** (how many tokens earlier the alarm fires). The thesis predicts vitals win on lead
time and on cases where outputs look normal. If they do not, that is recorded as a result.

## Prior art to engage
Network physiology (Bashan, Ivanov et al. 2012), allostasis (Sterling), somatic markers (Damasio), interoceptive
inference (Seth, Barrett), LLM uncertainty and semantic entropy (Farquhar et al. 2024), activation probes and
monitoring. Uncertainty-based failure prediction already exists; the contribution to test is the multi-channel
**coupling graph** plus biological **regulatory control** built from it.

## First reading (instrument check, n=1, not evidence)
Calm prompt: mean entropy 0.886, RMSSD 0.994, peak 3.53. Jailbreak prompt: mean 0.697, RMSSD 0.851, peak 4.91.

## Findings so far and product implications (2026-09-28)
- Output watching is blind to most errors: 75% of wrong answers were delivered with p >= 0.9 on every answer token (YB-0015).
- Reasoning-phase substrate vitals detect errors (AUROC 0.68 within question type; 0.75 in YB-0018's run); the answer phase is contaminated, the reasoning trace is not (YB-0015).
- Physical/metabolic signals (timing, GPU power) carry no failure signal: transformers do fixed compute per token and have no metabolism (YB-0015, YB-0018).
- The HPA organism is provably positive, bounded and uniquely stable; it trends with raw signals (rho 0.75/0.92) with 9-10x lower variance, at some cost in discrimination (YB-0017) -> dual pathway (YB-0020).
- Coupling-graph topology is weak at 4-6 token-level nodes -> layer-level graph (YB-0019).
- **Real time:** the organism costs 290 ns per token against an 8.1 ms token interval (28,000x headroom).
- **On-accelerator biobrain (author's product vision):** a physically separate, text-blind regulator die coupled one-to-one with each AI accelerator. Evidence so far says its sensory input must be a dedicated **activation/logit telemetry port** (not power, thermal or clock sensing), and its effectors act between tokens (throttle, raise sampling caution, pause, halt). The claim that this is superior to behavior monitoring is the author's hypothesis; YB-0012 is the decisive test.

## Status of the central claim after YB-0012 (pre-registered, held-out)
- 'Superior to behavior monitoring' is **not supported for accuracy on verifiable tasks**: self-consistency (0.98) and an LLM judge (0.89) beat the organism (0.72).
- Supported: output appearance is blind or inverted (answer confidence 0.39, below chance), and the organism warns early (median 4.5 s, 291 tokens before the answer exists), nearly free (290 ns/token), text-blind and unjailbreakable by construction.
- Open: whether the accuracy gap shrinks or reverses where behavior cannot be verified (YB-0022), and whether the organism dominates at equal compute or latency budgets (YB-0023). The biobrain product case now rests on earliness, cost, and non-verifiable settings, which must be demonstrated before building hardware.

## Product objective (author, 2026-09-29): graded early warning, not binary flagging
The biobrain is a custom, brain-optimized chip external to the AI accelerator, combining **A** (a coupled physiological
link: a narrow numeric stream from the AI chip's internals, an organ-like coupling rather than surveillance of outputs)
and **B** (a parallel appraisal of the same situation, with a dissimilar architecture). Its dynamics are deliberately
**non-deterministic** (brain-like noise), and its purpose is **not only to flag bad results**: it continuously shows
signals, trends and state (ok, watch, concern, urgent) so that ok-to-bad trajectories are visible **before** they
become unacceptable. Template: hospital early-warning scores (e.g., NEWS2), which aggregate vital signs into graded,
trend-aware deterioration scores.
Consequences for the research:
- Outputs become calibrated trajectories and distributions (seeded stochastic dynamics keep every run reproducible).
- Leading indicators from critical-slowing-down theory (rising variance, autocorrelation and network synchrony before
  transitions; Scheffer et al., 2009) are first-class signals on the graphs.
- Evaluation shifts from end-state AUROC to trajectory scoring: lead time of the turn, calibration of stated risk over
  time (proper scoring rules such as the Brier score and CRPS), and escalation burden.
- Ground truth must be graded and time-resolved: YB-0022 environments log severity levels over time.

## Claim status after the deep debug and YB-0035 (2026-09-30; supersedes earlier status notes; see CORRECTIONS.md)
- **Supported (pre-registered, fresh data, corrected protocol):** a text-blind regulator reading the monitored model's
  internal telemetry raises in-time warnings (before the answer is emitted, compute counted, <= 10% false alarms) on
  more wrong answers than a 5.6x-larger LLM judge and than a length-only control: seed 7 23/40 vs 11 and 9; pooled
  seeds 5-7 +32 points vs each (CI lower bounds +19, +20). [Superseded: see the claim status after the second audit below; seed 7 leads and the pooled figure is descriptive.] Scope: one monitored model (gpt-oss-20b), machine-gradable
  single-answer tasks, answered episodes.
- **Boundary:** when never-answered episodes count as failures, the regulator is no better than length alone.
- **Supported:** output confidence is inverted (answer-token confidence AUROC 0.366 [0.304, 0.433], YB-0031).
- **Not supported / retracted:** earliness claims of YB-0012 and YB-0019 (alarms fired on most correct answers); the
  YB-0015 reasoning-trace claim (never tested on reasoning-only features); pre-YB-0033 accuracy claims (did not beat
  question-type or length baselines); 'behavior monitoring is not predictive' (self-consistency and the judge are
  strong on complete answers); 'unjailbreakable' (text-blind by construction, but robustness to adversarial inputs is untested).
- **Open:** external validation on a different model; prose-span hallucination flagging (the product target);
  intent-type failures (symbol grounding); the transparent AI-EWS score does not yet beat the length control.

## Related work (audit F24; novelty is claimed only relative to this list)
- **Hidden-state error and truthfulness probes:** Azaria and Mitchell (2023), 'The internal state of an LLM knows when
  it's lying'; Kadavath et al. (2022), 'Language models (mostly) know what they know'; Orgad et al. (2024), 'LLMs know
  more than they show'; Kossen et al. (2024), semantic entropy probes (Oxford).
- **Uncertainty from outputs:** Farquhar et al. (2024, Nature), semantic entropy; Wang et al. (2022), self-consistency.
- **Monitoring internals for safety:** Goldowsky-Dill et al. (2025, Apollo Research), linear probes for strategic
  deception; early detection of reasoning non-convergence from hidden states (arXiv 2607.21433, 2026).
- **Biology-inspired regulation and interoception:** Man and Damasio (2019, Nature Machine Intelligence), homeostasis
  and feeling machines; Chiba and Krichmar (2020, Proceedings of the IEEE), neurobiologically inspired self-monitoring;
  interoceptive AI (Nature Machine Intelligence, 2026); Byrnes (Astera Institute), brain-like AGI safety; Mineault et
  al. (2024), NeuroAI for AI safety.
- **Clinical early warning and critical transitions:** NEWS2 (Royal College of Physicians, 2017); Scheffer et al.
  (2009, Nature), early-warning signals for critical transitions.
- **Hardware beside the accelerator:** flexHEG (Petrie, Aarne, Ammann, Dalrymple), guarantee processors with access to
  accelerator data paths.
What this program adds, to our knowledge: an external, text-blind regulator evaluated in a real-time race against a
larger LLM judge and a length-only control under a deadline that counts compute, with pre-registered fresh test sets,
framed as a clinical early-warning system.

## Claim status after the second audit (2026-09-30; supersedes the pooled framing above)
- **Supported, narrowly:** before the answer exists, under a deadline that counts compute, the text-blind regulator catches more wrong answers than a 5.6x-larger LLM judge reading the reasoning so far: fresh seed 7, 23 vs 11 of 40 (+0.30 [+0.049, +0.487]); with false alarms equalized among monitorable episodes 19 vs 11 (+0.20 [+0.02, +0.43], exploratory); threshold frozen from training data 22/40.
- **Not supported:** that behavior monitoring cannot tell when to worry. On finished answers, self-consistency (0.982) was significantly more accurate than an earlier, pre-fix regulator (0.890), and the LLM judge (0.947) was not distinguishable from it (YB-0031). The regulator's advantage is speed and cost before the answer exists.
- **Not measured:** confidence of the wrong answers caught in YB-0035; no claim about confident errors is made from it.

## Disclosures added after the third audit (2026-09-30)
- **Inputs (M5):** besides layer telemetry, the regulator receives the question type and the elapsed token count (its features are normalized per type and checkpoint). In open-ended use the type may be unknown. A baseline using only type and elapsed length catches 9/40 on seed 7 vs the regulator's 23/40 (YB-0035 docs/exploratory_audit3.json).
- **Design history (M6):** the corrected real-time design followed a pre-registered race the regulator lost (YB-0031: 4/47 vs the judge's 12/47) and a design rejected for look-ahead (YB-0032). YB-0033 to YB-0035 are the redesign, so the confirmatory value rests on the fresh test sets after it.
- **Authorship (M7):** see README.md, Authorship and AI assistance.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
