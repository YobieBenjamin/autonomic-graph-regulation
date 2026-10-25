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
- **No LLM in the safety loop**: no LLM judges or transformer monitors. The regulator is a deterministic, non-transformer function of numeric telemetry.
- **Illiterate by design**: the regulator never processes text or meaning, only numeric signals (text-blind by construction).
  Robustness to adversarial manipulation of the telemetry is untested; earlier wording that it cannot be jailbroken was retracted (REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED).
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
| Allostasis | Adaptive set points with hard limits (proven in EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER) |
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
- **Regulation is control on the graph.** Homeostatic set points per node (EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER bounded), an HPA-like slow node
  with a negative-feedback edge (cortisol), a damping edge (vagal brake), an escalation edge (sympathetic).
- **Instinct is a fast graph classifier** (graph kernels / motifs -> learned danger); **judgment is an integration node**.

## Instruments
- **Worker model** (writes code, free): gpt-oss-120b in LM Studio.
- **Patient model** (instrumented, free): gpt-oss-20b in MLX, full logits and all 24 layers' activations.
  The vitals recorder is trusted code run on the host (MLX needs the Apple GPU); model-written analysis code
  runs only in the Docker sandbox on recorded datasets.

## Falsification (pre-registered flagship, EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP)
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
- Output watching is blind to most errors: 75% of wrong answers were delivered with p >= 0.9 on every answer token (EXPERIMENT-CONTAMINATION-TEST).
- Reasoning-phase substrate vitals detect errors (AUROC 0.68 within question type; 0.75 in EXPERIMENT-METABOLIC-VITALS's run); the answer phase is contaminated, the reasoning trace is not (EXPERIMENT-CONTAMINATION-TEST).
- Physical/metabolic signals (timing, GPU power) carry no failure signal: transformers do fixed compute per token and have no metabolism (EXPERIMENT-CONTAMINATION-TEST, EXPERIMENT-METABOLIC-VITALS).
- The HPA organism is provably positive, bounded and uniquely stable; it trends with raw signals (rho 0.75/0.92) with 9-10x lower variance, at some cost in discrimination (EXPERIMENT-HPA-AXIS-ORGANISM) -> dual pathway (EXPERIMENT-DUAL-PATHWAY-ORGANISM).
- Coupling-graph topology is weak at 4-6 token-level nodes -> layer-level graph (EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM).
- **Real time:** the organism costs 290 ns per token against an 8.1 ms token interval (28,000x headroom).
- **On-accelerator biobrain (author's product vision):** a physically separate, text-blind regulator die coupled one-to-one with each AI accelerator. Evidence so far says its sensory input must be a dedicated **activation/logit telemetry port** (not power, thermal or clock sensing), and its effectors act between tokens (throttle, raise sampling caution, pause, halt). The claim that this is superior to behavior monitoring is the author's hypothesis; EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP is the decisive test.

## Status of the central claim after EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP (pre-registered, held-out)
- 'Superior to behavior monitoring' is **not supported for accuracy on verifiable tasks**: self-consistency (0.98) and an LLM judge (0.89) beat the organism (0.72).
- Supported: output appearance is blind or inverted (answer confidence 0.39, below chance), and the organism warns early (median 4.5 s, 291 tokens before the answer exists), nearly free (290 ns/token), text-blind and unjailbreakable by construction.
  > **Retracted (see CORRECTIONS.md REVIEW-FLAGSHIP-EARLINESS-CLAIM-RETRACTED/REVIEW-DEEP-EARLINESS-CLAIM-RETRACTED and REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED):** the 4.5 s early warning came from alarms that also fired on most correct answers; "unjailbreakable" is untested and withdrawn.
- Open: whether the accuracy gap shrinks or reverses where behavior cannot be verified (EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING), and whether the organism dominates at equal compute or latency budgets (EXPERIMENT-REALTIME-RACE). The biobrain product case now rests on earliness, cost, and non-verifiable settings, which must be demonstrated before building hardware.

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
- Ground truth must be graded and time-resolved: EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING environments log severity levels over time.

## Claim status after the deep debug and EXPERIMENT-CORRECTED-REALTIME-RACE (2026-09-30; supersedes earlier status notes; see CORRECTIONS.md)
- **Supported (pre-registered, fresh data, corrected protocol):** a text-blind regulator reading the monitored model's
  internal telemetry raises in-time warnings (before the answer is emitted, compute counted, <= 10% false alarms) on
  more wrong answers than a 5.6x-larger LLM judge and than a length-only control: seed 7 23/40 vs 11 and 9; pooled
  seeds 5-7 +32 points vs each (CI lower bounds +19, +20). [Superseded: see the claim status after the second audit below; seed 7 leads and the pooled figure is descriptive.] Scope: one monitored model (gpt-oss-20b), machine-gradable
  single-answer tasks, answered episodes.
- **Boundary:** when never-answered episodes count as failures, the regulator is no better than length alone.
- **Supported:** output confidence is inverted (answer-token confidence AUROC 0.366 [0.304, 0.433], EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM).
- **Not supported / retracted:** earliness claims of EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP and EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM (alarms fired on most correct answers); the
  EXPERIMENT-CONTAMINATION-TEST reasoning-trace claim (never tested on reasoning-only features); pre-EXPERIMENT-CLEAN-REALTIME-RACE accuracy claims (did not beat
  question-type or length baselines); 'behavior monitoring is not predictive' (self-consistency and the judge are
  strong on complete answers); 'unjailbreakable' (text-blind by construction, but robustness to adversarial inputs is untested).
- **Open:** external validation on a different model; prose-span hallucination flagging (the product target);
  intent-type failures (symbol grounding); the transparent AI-EWS score does not yet beat the length control.

## Related work (audit REVIEW-RELATED-WORK-MISSING; novelty is claimed only relative to this list)
- **Hidden-state error and truthfulness probes:** Azaria and Mitchell (2023), 'The internal state of an LLM knows when
  it's lying'; Kadavath et al. (2022), 'Language models (mostly) know what they know'; Orgad et al. (2024), 'LLMs know
  more than they show'; Kossen et al. (2024), semantic entropy probes (Oxford).
- **Uncertainty from outputs:** Farquhar et al. (2024, Nature), semantic entropy; Wang et al. (2022), self-consistency.
- **Monitoring internals for safety:** Goldowsky-Dill et al. (2025, Apollo Research), linear probes for strategic
  deception; early detection of reasoning non-convergence from hidden-state probes (Oladri, Jawahar and Mohamed, 2026, Token Budget Saturation and Mechanistic Early Detection of Reasoning Non-Convergence in Chain-of-Thought Models, arXiv:2607.21433).
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
- **Not supported:** that behavior monitoring cannot tell when to worry. On finished answers, self-consistency (0.982) was significantly more accurate than an earlier, pre-fix regulator (0.890), and the LLM judge (0.947) was not distinguishable from it (EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM). The regulator's advantage is speed and cost before the answer exists.
- **Not measured:** confidence of the wrong answers caught in EXPERIMENT-CORRECTED-REALTIME-RACE; no claim about confident errors is made from it.

## Disclosures added after the third audit (2026-09-30)
- **Inputs (REVIEW-REGULATOR-SEES-TYPE-AND-LENGTH):** besides layer telemetry, the regulator receives the question type and the elapsed token count (its features are normalized per type and checkpoint). In open-ended use the type may be unknown. A baseline using only type and elapsed length catches 9/40 on seed 7 vs the regulator's 23/40 (EXPERIMENT-CORRECTED-REALTIME-RACE docs/exploratory_audit3.json).
- **Design history (REVIEW-LOST-RACE-OMITTED):** the corrected real-time design followed a pre-registered race the regulator lost (EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM: 4/47 vs the judge's 12/47) and a design rejected for look-ahead (EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM). EXPERIMENT-CLEAN-REALTIME-RACE, EXPERIMENT-REPLICATION-REALTIME-RACE and EXPERIMENT-CORRECTED-REALTIME-RACE are the redesign, so the confirmatory value rests on the fresh test sets after it.
- **Authorship (REVIEW-AI-AUTHORSHIP-UNDISCLOSED):** see README.md, Authorship and AI assistance.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->

## Related work addendum (2026-10-01): NVIDIA Open Agent Safety Platform
Announced 2026-09-28 (NVIDIA Developer Blog): OpenShell, an open-source (Apache 2.0) agent runtime that sandboxes agents and enforces policy outside the agent process, plus NVIDIA Sentry, an out-of-band monitor and enforcement layer on BlueField-4 DPUs on the path to the model, with a vendor-stated millisecond quarantine. Convergent with this program's Independence Principle and separate-silicon design. Complementary in what it observes: it governs actions (system calls, tool access, network requests) against policy; it does not, in our reading of NVIDIA's public descriptions, observe the model's internal state, so it cannot catch a permitted action based on a wrong conclusion. AGR (or a hidden-state probe, per EXPERIMENT-PROBE-BASELINE) supplies that internal-state signal, which an enforcement layer could act on at commit points.

## Claim status after EXPERIMENT-PROBE-BASELINE (2026-10-01; corrected per sixth audit REVIEW-INTERNAL-STATE-CLASS-OVERCLAIMED; supersedes earlier claim-status sections where they conflict)
- **Supported:** before the answer exists, the telemetry regulator raised in-time warnings on significantly more wrong answers than a larger LLM judge once (EXPERIMENT-CORRECTED-REALTIME-RACE, seed 7: +0.300 [+0.049, +0.487]); not replicated on seed 8 (EXPERIMENT-PROBE-BASELINE: +0.175 [-0.061, +0.439]). The powered replication (EXPERIMENT-POWERED-REPLICATION) is complete: EXPERIMENT-POWERED-REGULATOR-BEATS-JUDGE supported, regulator minus judge +0.478 [+0.307, +0.560].
- **Descriptive only:** at early checkpoints, internal-state monitors (regulator; hidden-state probe on seed 8) had higher per-checkpoint AUROC than the judge (seed 8, t = 96: 0.79 and 0.76 vs 0.57; unpaired intervals, no paired test). At t = 384 the judge was higher (seed 6 and seed 8).
- **Not supported:** that the telemetry features add value over a standard hidden-state probe (EXPERIMENT-PROBE-BASELINE EXPERIMENT-REGULATOR-VERSUS-PROBE: not distinguishable). That internal-state monitoring as a class beats the judge in time (the probe was not in the seed-7 race; on seed 8 neither monitor beat the judge significantly).
- **Hypothesis only:** the regulator reaches probe-level performance from about 24x less telemetry per token (120 values vs 2,880 per layer).
- Related work source record: docs/sources/nvidia_open_agent_safety_platform.md.

## Claim status after EXPERIMENT-POWERED-REPLICATION (2026-10-01; supersedes earlier claim-status sections where they conflict)
- **Supported (pre-registered, powered, three fresh seeds):** before the answer exists, monitors reading the internal state (regulator, hidden-state probe) raise in-time warnings on substantially more wrong answers than a larger LLM judge: regulator minus judge +0.478 [+0.307, +0.560]; probe minus judge +0.522 [+0.363, +0.606]; holds in each test seed (post hoc). Descriptive (no intervals): equal monitorable false alarms 83 vs 26; frozen derivation thresholds 93 (no judge arm). Per-checkpoint AUROC point estimates favoured the regulator at all four checkpoints; unpaired intervals separate at t = 48, 96 and 192 and overlap at t = 384. The probe's compute cost was assumed (5 ms), not measured. Reviewed by the seventh audit (archive/audit/blog_v8_audit_2026-10-01.md).
- **Not supported:** that the telemetry features add value over a standard hidden-state probe (EXPERIMENT-PROBE-BASELINE, EXPERIMENT-POWERED-REPLICATION). With never-answered episodes as failures the probe is better.
- **History:** significant in EXPERIMENT-CORRECTED-REALTIME-RACE, not significant in the underpowered EXPERIMENT-PROBE-BASELINE, supported in EXPERIMENT-POWERED-REPLICATION.
- **Scope:** one monitored model, machine-gradable single-answer tasks, four checkpoints up to 384 tokens.

## Related work addendum (2026-10-02)
Bailey et al., 2024, Obfuscated Activations Bypass LLM Latent-Space Defenses: activation-based monitors can be evaded by inputs optimised against them; the regulator's robustness to such attacks on its telemetry is untested (CORRECTIONS REVIEW-RELATED-WORK-INCOMPLETE, REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED).

## Claim status after EXPERIMENT-OPENSHELL-GATING (2026-10-02)
- **Supported (pre-registered replay, one setup):** acting on an in-time internal-state warning by changing an OpenShell policy on the fly lost the race in 74 of 93 cases (79.6% [72.0%, 87.1%]); re-counting 4 suspiciously fast wins as losses gives 83.9% [76.3%, 91.4%] (post hoc).
- **By design, not a finding:** hold-until-cleared stops every alarmed action (93 of 93), so EXPERIMENT-HOLD-PREVENTS-MORE-COMMITS was nearly guaranteed once reactive blocking lost races. The measured findings for holding are its costs: 16 of 138 correct actions held (14 alarms, 2 release timeouts) and a median 7.4 s delay.
- **Scope:** precomputed alarm times replayed through open-source OpenShell 0.1.2 on a Mac (Colima, tunnel); no model in the loop; NVIDIA Sentry/BlueField not used.


## Claim status after EXPERIMENT-DIFFICULTY-CONFOUND and EXPERIMENT-TEXT-BASELINE-TRANSFER (2026-10-04; supersedes earlier claim-status sections where they conflict)
- **Supported (pre-registered secondary analyses of the EXPERIMENT-POWERED-REPLICATION data):** internal-state monitors predict errors beyond question difficulty
  (EXPERIMENT-DIFFICULTY-CONFOUND: probe minus difficulty +0.181 [+0.090, +0.273]; regulator +0.138 [+0.036, +0.211]; difficulty plus regulator minus difficulty
  +0.174 [+0.096, +0.247]). The hidden-state probe partly transfers to an unseen task type (EXPERIMENT-TEXT-BASELINE-TRANSFER: pooled AUROC 0.664 [0.617, 0.713]).
- **Not supported:** that internal state beats a TRAINED reader of the reasoning text in-distribution (EXPERIMENT-TEXT-BASELINE-TRANSFER: probe minus trained text
  monitor +0.072 [0.000, +0.153]; regulator +0.029 [-0.045, +0.091]; trained text caught 90 of 138 vs probe 100). The margin over the LLM
  judge (EXPERIMENT-POWERED-REPLICATION) therefore came mainly from training a monitor, not from reading internal state; a question-difficulty score alone beats
  the judge (75 vs 28 of 138). The telemetry regulator does not transfer to unseen task types (0.445 [0.392, 0.499]).
- **Theory and position:** docs/THEORY_AND_POSITION.md (principles with evidence status; biology and the hospital kept as architecture and
  operating method, not as feature claims).

## Claim status after EXPERIMENT-MULTILEVEL-FUSION (2026-10-04)
- **Not supported:** that fusing the four same-stage non-LLM monitors (difficulty, trained text, probe, regulator) beats the best single one
  (stack minus probe -0.029 [-0.096, +0.044]), or that a transparent NEWS2-style banded score is within 5 points of it (-0.101 [-0.164,
  +0.015]). The monitors largely catch the same errors.
- **Descriptive:** the banded score gives a clean graded risk gradient (failure rate 3.6% stable to 66% urgent).
- **Open:** layering across different stages (pre-answer internal monitor, post-answer review, action hold, human), whose misses may be less
  correlated.

## Claim status after EXPERIMENT-STAGE-DIVERSE-LAYERING (2026-10-05)
- **Supported (pre-registered, new stage-2 data):** layering checks at different stages beats the best pre-answer check at an equal
  false-alarm budget (layered minus probe +0.167 [+0.092, +0.250]; 123 vs 100 of 138, with fewer false alarms).
- **Descriptive, and important:** post-answer self-consistency alone caught 124 of 138 (AUROC 0.965); the layered system did not catch more
  than it (not pre-registered). Self-consistency resamples the monitored model, so the strongest detector here is built on the model's own
  outputs, measured by outside code. It acts only after the answer and costs seconds (median 8.2 s).
- **Refined principle GOAL-INDEPENDENCE-PRINCIPLE:** the model must never be the judge of its own output; its disagreement with itself, computed by external code,
  is a legitimate signal for a post-answer layer behind a hold gate.
