An External Nervous System for Transformers: Real-Time Early Warning
From Layer Telemetry

*Garbage In, Gospel Out, Part II, the technical version: methods,
mathematics, pre-registered results, audit and next steps.*

1\. Thesis

Transformer outputs are uncalibrated with respect to correctness. On our
tasks, answer-token confidence (one minus the minimum top-1 probability
over answer tokens) detected wrong answers at AUROC 0.366 \[95% CI
0.304, 0.433\] on a fresh test set: inverted, not merely uninformative.
75% of errors (27 of 36) in an early study carried top-1 probability of
at least 0.9 on every answer token. Output-level monitoring therefore
has a structural blind spot exactly where confident errors live.

The program's premise is that judgment should be modelled on biological
regulation (interoception, autonomic and endocrine regulation, graded
warning), and that the regulator must obey an Independence Principle: it
is not a transformer, contains none, never consumes the monitored
model's text or self-report (text-blind), receives only numeric
telemetry, and acts through effectors. The evaluation template is the
clinical early-warning score (NEWS2): serial observations, graded
levels, and action before deterioration becomes an event.

2\. Instruments

-   **Monitored model:** gpt-oss-20b (MLX, M4 Max 128 GB), 24
    transformer blocks, 32 routed experts per block, greedy decoding.

-   **Telemetry tap:** a wrapper on each block's forward pass records,
    for the newest token at layer ℓ: ‖aℓ‖ (attention update), ‖mℓ‖
    (expert update), ‖xℓ,out‖, cos(xℓ,in, xℓ,out), and router entropy −Σ
    pₑ log pₑ: 120 channels per token, norms log(1+·)-scaled. The tap is
    output-invariant (token-identical generations). A permanent
    synchronization test compares each streamed reading with a fresh
    uncached forward pass over the same prefix.

-   **Ground truth:** machine-gradable tasks (5- and 6-digit
    multiplication, letter counting, day-of-week, modular
    exponentiation, long addition); correctness is computed, never
    judged by a model.

-   **Competitors:** an LLM judge (gpt-oss-120b; 5.6x the monitored
    model's total parameters, 1.4x its active parameters) reading the
    question and the reasoning prefix; prefix self-consistency (two T =
    0.8 continuations, disagreement); and length controls C1(t) = t and
    C2(t) = derivation percentile of t within question type.

-   **Infrastructure:** all analysis runs in a locked-down Docker
    sandbox; compiled C cores via ctypes; proofs as tests;
    pre-registration of hypotheses, decision rules, and (since YB-0035)
    the full analysis code plus a dry run before test data exists; one
    verification path shared by local publishing and CI.

3\. The regulator

Features at a real-time checkpoint t (only tokens before t; nothing
derived from total reasoning length): for each layer and channel, the
mean and RMSSD over the prefix (240 features), plus two 24-node layer
coupling graphs (expert-update and router-entropy signals) summarised by
windowed spectral statistics, trends and one-window extrapolations (74
features), plus log t. Features are z-scored per (question type, t) with
derivation statistics; the model is L2-regularised logistic regression
(C = 0.1) fitted on all derivation observations.

> Coupling: Wᵢⱼ = max over g ∈ {0..3} of \|ρ(xᵢ(t), xⱼ(t+g))\|, 24-token
> windows, stride 8
>
> Normalised Laplacian: L = I − D\^(−1/2) W D\^(−1/2); algebraic
> connectivity λ₂
>
> Spectral modularity: B = W − d dᵀ/(2m), Q = sᵀBs/(4m), s = sign of B's
> leading eigenvector

Derivation data: 5,367 answered episodes (402 wrong) from three seeds,
contributing serial observations at every checkpoint an episode reaches.

4\. The real-time race

Checkpoints t ∈ {48, 96, 192, 384} exist only while the model is still
reasoning. Let t_clock(t) be the wall-clock time at checkpoint t, D the
time the answer is emitted, c the monitor's compute time (fixed at 5 ms
per regulator check, measured 4.1 ms; measured per call for behavior
monitors). An alarm is in time iff

> s(t) \> τ and t_clock(t) + c ≤ D

Each episode's in-time score is the maximum over checkpoints satisfying
the deadline. Every monitor's threshold is the tightest value with at
most 10% of correct test episodes alarmed:

> τ\* = min { τ : (1/n) Σ 1\[vᵢ \> τ\] ≤ 0.10 } over correct episodes

Uncertainty: a paired bootstrap (1,000 resamples) over all test
episodes, re-setting τ\* for both monitors in every resample. Lead time
is reported as seconds to spare at the first in-time crossing. Primary
criterion: the regulator beats both the best behavior monitor and the
best length control on in-time recall, both 95% CIs above zero.

5\. Results (YB-0035, corrected protocol)

Protocol and analysis code committed (b6c795b) and confirmed on GitHub
before the seed-7 test set was recorded.

  -------------------- ------------- ----------- ---------- ----------- -----------
  **Test set**         **Regulator   **Judge**   **Length   **Reg. −    **Reg. −
                       in time**                 C1**       judge \[95% length
                                                            CI\]**      \[95%
                                                                        CI\]**

  Seed 7 (primary; 535 23 (57.5%),   11          9          +0.300      +0.350
  answered, 40 wrong)  FPR 9.9%                             \[+0.049,   \[+0.128,
                                                            +0.487\]    +0.544\]

  Seed 5               30 (68.2%)    13          17         +0.386      +0.296
  (resynchronized; 44                                       \[+0.140,   \[+0.088,
  wrong)                                                    +0.575\]    +0.491\]

  Seed 6               25 (58.1%)    13          11         +0.279      +0.326
  (resynchronized; 43                                       \[+0.060,   \[+0.108,
  wrong)                                                    +0.486\]    +0.514\]

  Pooled (1,610; 127                                        +0.323      +0.323
  wrong)                                                    \[+0.186,   \[+0.205,
                                                            +0.433\]    +0.434\]
  -------------------- ------------- ----------- ---------- ----------- -----------

-   Within-checkpoint AUROC on seed 7 (t = 48/96/192/384): regulator
    0.704/0.730/0.798/0.828; judge 0.544/0.562/0.609/0.783. Within a
    checkpoint every still-reasoning episode has the same elapsed
    length, so C1 is exactly at chance there; the regulator's
    discrimination cannot come from elapsed length.

-   Disclosed: the regulator's false-alarm rate among monitorable
    correct episodes is 16.3%; self-consistency on prefixes caught 0/40;
    the transparent AI-EWS score (8 banded vitals) caught 9/40, no
    better than length.

-   **Boundary (pre-declared sensitivity):** counting never-answered
    episodes as failures (105 failures), regulator 68, length 74, judge
    65; neither difference is significant. The advantage is specific to
    answered, confidently wrong outputs.

6\. How the result survived an adversarial audit

A separate, read-only Claude Code session audited the repository blind:
38 findings (3 critical, 23 major, 12 minor). We verified every critical
finding independently. The most consequential: the telemetry tap
delivered each token's reading one step late (stale, not future
information), which we reproduced against fresh forward passes and
corrected by a verified one-step resynchronization of old recordings
(0.012 to 0.014 vs 0.5 to 0.9 channel standard deviations). Earlier
earliness claims (YB-0012, YB-0019) were artifacts of alarms that fired
on most correct answers (89.3% at the first check), and are retracted.
Early regulators did not beat question-type (AUROC 0.764) or length
(0.796) baselines on their test set; the current regulator does. We also
found that greedy generation is deterministic within a session but can
diverge across sessions under GPU sharing, which led to a run-alone
guard and environment snapshots. Every finding and its resolution is
logged in CORRECTIONS.md, and twelve process rules now encode the
lessons (docs/PROTOCOL.md).

7\. Limitations

-   One monitored model and one family of single-answer,
    machine-gradable tasks; 40 wrong answers in the primary set.

-   Not yet evidence for hallucination detection in open prose, for
    intent-type failures, or for robustness to adversarial inputs
    (text-blind by construction, but untested against attacks on the
    telemetry).

-   Judge compute times come from one Mac; faster serving would help
    every monitor. Seeds 5 and 6 used re-tokenized judge prefixes (seed
    7 uses exact token ids).

8\. Related work

Hidden-state truthfulness and error probes (Azaria and Mitchell, 2023;
Kadavath et al., 2022; Orgad et al., 2024; semantic entropy probes,
Kossen et al., 2024), output-uncertainty methods (semantic entropy,
Farquhar et al., 2024; self-consistency, Wang et al., 2022), activation
monitors for deception (Goldowsky-Dill et al., 2025), biology-inspired
regulation and interoception (Man and Damasio, 2019; Chiba and Krichmar,
2020; Byrnes; Mineault et al., 2024), clinical early warning (NEWS2) and
critical transitions (Scheffer et al., 2009), and accelerator-adjacent
guarantee processors (flexHEG). What this work adds, to our knowledge,
is the combination: an external, text-blind regulator evaluated in a
deadline race that counts compute, against a larger LLM judge and a
length control, with pre-registered fresh test sets.

9\. Conclusion

Under a pre-registered, audited and corrected protocol, a text-blind
regulator reading a transformer's layer telemetry raises in-time
warnings on substantially more confident wrong answers than a larger LLM
judge and a length-only control, at about 5 ms per check. The result is
narrow in scope and robustly supported within it; it is the program's
first confirmed evidence that physiological monitoring can outperform
behavioral monitoring where the output looks like gospel.

10\. Next steps

1.  **External validation (YB-0037):** Qwen3-VL-30B-A3B (48 layers, 128
    experts), with its synchronization bug already fixed and tested.

2.  **Prose-span hallucination flagging (YB-0038):** span-level ground
    truth; does the risk trace rise inside false claims and not around
    true ones?

3.  **Dense models:** Qwen3-8B, Llama 3.1 8B, Gemma 2 9B, where router
    entropy, the most consistent warning channel, does not exist.

4.  **Transparent scoring:** close the gap between AI-EWS and the
    black-box regulator; re-test the reasoning-only claim (YB-0036).

5.  **Graded, agentic settings (YB-0022):** time-resolved severity in a
    simulated operations sandbox; critical-slowing-down indicators; the
    hunch-field architecture.

6.  **Hardware path:** a virtual-SoC interface specification (telemetry
    port, regulator core, flag lane), and outside replication from the
    published code and data.
