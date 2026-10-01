An External Nervous System for Transformers: Warning Before the Answer
Exists

*Garbage In, Gospel Out, Part II, the technical version: methods,
mathematics, pre-registered results, four audits, limitations and next
steps.*

*By Yobie Benjamin and AI. I conceived and directed the research; code,
experiments, analyses and drafts were produced by me together with AI
systems (Anthropic's Claude as research assistant; a locally run
gpt-oss-120b for some code). The code, data, reports and corrections are
public at github.com/YobieBenjamin/autonomic-graph-regulation; the
commit history that timestamps the pre-registration is private and
available to reviewers on request.*

1\. Thesis and scope

On the monitored model and tasks studied here, output-level confidence
is a poor guide to correctness: answer-token confidence (one minus the
minimum top-1 probability over answer tokens) detected wrong answers at
AUROC 0.366 \[95% CI 0.304, 0.433\] on a fresh test set, below chance.
In an early study, 75% of errors (27 of 36) carried top-1 probability of
at least 0.9 on every answer token. These are results for one model and
one task family, not a general law.

Behavior monitors are strong once an answer is complete: on finished
answers, self-consistency reached AUROC 0.982 and an LLM judge 0.947,
versus 0.890 for an earlier version of our regulator, trained before the
telemetry fix described in Section 6; the gap to self-consistency was
significant and the gap to the judge was not (−0.057 \[−0.131, +0.012\];
YB-0031). The question this work addresses is narrower: can an external
regulator that reads only internal telemetry warn about wrong answers
before they are emitted, under a deadline that counts compute? The
regulator obeys an Independence Principle: it is not a transformer,
contains none, and never consumes the monitored model's text or
self-report (text-blind). Besides numeric telemetry it receives the task
category and the elapsed token count, used for normalization; acting
through effectors is a design principle, not yet built or tested. The
evaluation template is the clinical early-warning score (NEWS2).

2\. Instruments

-   **Monitored model:** gpt-oss-20b (MLX, M4 Max 128 GB), 24
    transformer blocks, 32 routed experts per block, greedy decoding.

-   **Telemetry tap:** per token and layer ℓ: ‖aℓ‖ (attention update),
    ‖mℓ‖ (expert update), ‖xℓ,out‖, cos(xℓ,in, xℓ,out), router entropy
    −Σ pₑ log pₑ: 120 channels per token, norms log(1+·)-scaled.
    Output-invariant (token-identical generations). A synchronization
    test, run before each recording, compares four of the five readings
    (all but the cosine) for the first 10 tokens of one test prompt with
    fresh uncached forward passes. Its pass criterion was later changed
    for a second model (each reading closer to its own token's pass than
    to the neighbour's, median error below 0.10); the seed-7 run passed
    the earlier criterion with a maximum aligned error of 0.099 against
    a minimum lag error of 0.601.

-   **Ground truth:** six machine-gradable task types (3-by-2-digit and
    5/6-digit multiplication, letter counting, day-of-week, modular
    exponentiation, long addition); correctness is computed, never
    judged by a model. Errors are unevenly distributed across types.

-   **Competitors:** an LLM judge (gpt-oss-120b; 5.6x the monitored
    model's total parameters and 1.4x its active parameters, per the
    model card; medium reasoning effort, up to 4,000 tokens per check)
    reading the question and the reasoning prefix; prefix
    self-consistency (two T = 0.8 continuations, disagreement); length
    controls C1(t) = t and C2(t) = derivation percentile of t within
    type; and, after the second audit, a question-type control C3
    (derivation failure rate of the episode's type).

-   **Infrastructure:** locked-down Docker sandbox; compiled C cores via
    ctypes; proofs as tests; pre-registration of hypotheses, decision
    rules and (since YB-0035) the full analysis code and a dry run
    before test recordings exist; one verification path shared by local
    publishing and CI.

3\. The regulator

At real-time checkpoint t (only tokens before t; nothing derived from
total reasoning length): for each layer and channel, the mean and RMSSD
over the prefix (240 features), plus two 24-node layer coupling graphs
(expert-update and router-entropy signals) summarised by windowed
spectral statistics, trends and one-window extrapolations (74 features),
plus log t. Features are z-scored per (question type, t); the model is
L2-regularised logistic regression (C = 0.1) with a single alarm
threshold. Derivation: 5,367 answered episodes (402 wrong) from three
seeds.

> Coupling: Wᵢⱼ = max over g ∈ {0..3} of \|ρ(xᵢ(t), xⱼ(t+g))\|, 24-token
> windows, stride 8
>
> Normalised Laplacian: L = I − D\^(−1/2) W D\^(−1/2); algebraic
> connectivity λ₂
>
> Spectral modularity: B = W − d dᵀ/(2m), Q = sᵀBs/(4m), s = sign of B's
> leading eigenvector

4\. The real-time race

The race is an offline replay of recorded episodes that charges each
monitor its measured compute time. Checkpoints t ∈ {48, 96, 192, 384}
exist only while the model is still reasoning. With t_clock(t) the
wall-clock time at t, D the answer emission time and c the monitor's
compute time (fixed 5 ms per regulator check, against 4.1 ms measured in
YB-0033 excluding the telemetry recorder's own overhead; measured per
call for behavior monitors), an alarm is in time iff

> s(t) \> τ and t_clock(t) + c ≤ D

Each episode's in-time score is the maximum over checkpoints meeting the
deadline. Pre-registered threshold: the tightest value with at most 10%
of the test set's correct episodes alarmed. This is a comparison device,
not a deployment guarantee: it uses test labels, and 194 of 495 correct
seed-7 answers finish before the first checkpoint and can never be
alarmed, so false-alarm rates among monitorable episodes are higher
(Section 5). Uncertainty: paired bootstrap (1,000 resamples) over all
test episodes, thresholds re-set in every resample.

5\. Results

Primary (YB-0035, fresh seed 7)

Protocol and analysis code: commit b6c795b. GitHub's server recorded its
push at 15:26:40 UTC and the CI run it triggered at 15:26:42; the first
seed-7 episode began at 15:26:49.96 UTC by the Mac's clock. That start
time is self-reported (written by the recorder from the local clock);
the Mac's offset from network time was −1 ms when checked about 10 hours
later. Public timestamps for future pre-registrations are now required
(protocol rule 13). The launch script that waited for the push was
committed after the fact (agr/start_seed7_after_push.sh). Seed 7: 600
recorded, 535 answered, 40 wrong (all from four of the six task types;
65 never answered, 64 of them modular exponentiation).

  ------------------------- ------------ ---------------- --------------------
  **Monitor**               **In time    **False alarms   **Regulator minus
                            (of 40)**    (all /           monitor \[95% CI\]**
                                         monitorable)**   

  Regulator                 23           9.9% / 16.3%     ---

  LLM judge (prefix)        11           6.7% / 11.0%     +0.300 \[+0.049,
                                                          +0.487\]

  Length control C1         9            6.3% / 10.3%     +0.350 \[+0.128,
                                                          +0.544\]

  Question-type control C3  6            6.1%             +0.425 \[+0.194,
  (exploratory)                                           +0.625\]

  Self-consistency (prefix) 0            0.8%             ---

  AI-EWS v4 (transparent    9            8.1%             ---
  banded score)                                           
  ------------------------- ------------ ---------------- --------------------

-   Per-checkpoint AUROC on seed 7 (t = 48/96/192/384; episodes
    341/302/222/40, of which wrong 40/39/33/9): regulator
    0.704/0.730/0.798/0.828; judge 0.544/0.562/0.609/0.783. Within a
    checkpoint C1 is constant, so the regulator's within-checkpoint
    discrimination is not elapsed length; it could still partly reflect
    predicting eventual length, and on seed 6 at t = 384 the judge was
    higher (0.607 vs 0.530). Intervals for these figures are not yet
    computed.

-   Judge compute per check (committed artifact): seed 7 median 1.55 s,
    90th percentile 7.2 s. Self-consistency runs two full continuations
    per check (median 5.8 s, 90th percentile 19.6 s), so it is
    structurally disadvantaged in this race.

-   Type-by-length baseline (exploratory; the regulator's non-telemetry
    inputs only: derivation failure rate by question type among episodes
    still reasoning at t): 9/40 at 6.1% false alarms.

Exploratory checks after the second audit (not pre-registered)

-   **Equal false alarms among monitorable episodes** (all monitors at
    about 10% of the 301 monitorable correct episodes): regulator 19/40
    vs judge 11/40, +0.20 \[+0.02, +0.43\]; length C1 cannot be tuned to
    that rate at four discrete checkpoints; type C3 6/40.

-   **Threshold frozen from derivation data** (5-fold cross-fitted
    regulator scores, 10% false alarms on derivation correct episodes):
    regulator 22/40 at 9.1% false alarms (15.0% monitorable); length C1
    9/40; type C3 6/40.

Secondary and boundary

-   Seeds 5 and 6 (test sets of YB-0033/34, re-used, re-synchronized;
    judge prefixes re-tokenized from text) agree: regulator 30/44 and
    25/43 (after resynchronization; originally 28 and 24) vs judge 13
    and 13 vs length 17 and 11. Their pooled estimate with seed 7 is
    descriptive only.

-   **Boundary (pre-declared sensitivity):** counting never-answered
    episodes as failures (105), regulator 68, length 74, judge 65; no
    significant difference. The advantage is specific to answered wrong
    answers; their confidence was not measured in this experiment.

6\. Four adversarial audits

A separate, read-only Claude session audited the repository blind: 38
findings (3 critical, 20 major, 15 minor). Each critical finding was
verified by the AI research assistant, under the author's direction,
before any change. The most consequential: the telemetry tap delivered
each token's reading one step late (stale, not future). Old recordings
were resynchronized by a one-step shift, verified on all 11 of 20
re-recorded seed-2 episodes whose text reproduced exactly: median error
0.012 channel standard deviations with the shift vs 0.81 without, better
in 11 of 11, worst single reading 2.8 (the other 9 diverged across
sessions: greedy generation is deterministic within a session but can
diverge across sessions, likely because of GPU sharing). Earlier
earliness claims (YB-0012, YB-0019) were artifacts of alarms firing on
most correct answers (89.3% at the first check) and are retracted; the
regulators of YB-0012, YB-0019 and YB-0030 did not beat question-type
(AUROC 0.764) or length (0.796) baselines. A second blind audit of
YB-0035 and an earlier draft of this post found no leakage but 25
findings, mostly on interpretation (2 critical); a third audit of the
next draft found 30 more on verifiability, attribution and wording (1
critical), and a fourth found 23 more (1 critical), mainly on what
readers can verify and on out-of-date records. This version incorporates
all of them. All three audits were separate sessions of an AI model
given no knowledge of earlier findings: independent of the authoring
session, not of the AI system; no human expert review has yet been
performed. All findings and resolutions are logged in CORRECTIONS.md;
thirteen process rules encode the lessons.

7\. Limitations

-   One monitored model, one task family, one set of four checkpoints
    (at most 384 tokens), one machine; 40 wrong answers in the primary
    set; the most stringent exploratory comparison has a lower bound of
    +0.02.

-   No comparison yet against a standard linear probe on raw hidden
    states, the obvious text-blind competitor from prior work; this is
    the next experiment (YB-0042).

-   No evidence yet for hallucination detection in open prose,
    intent-type failures, or robustness to adversarial manipulation of
    internal activations.

-   Faster serving would help the behavior monitors, not the regulator,
    which is always in time; seeds 5 and 6 used re-tokenized judge
    prefixes.

8\. Related work

Hidden-state truthfulness and error probes (Azaria and Mitchell, 2023;
Burns et al., 2023; Kadavath et al., 2022; Orgad et al., 2024; semantic
entropy probes, Kossen et al., 2024), output-uncertainty methods (Kuhn,
Gal and Farquhar, 2023; Farquhar et al., 2024; self-consistency, Wang et
al., 2022), early detection of reasoning non-convergence from
hidden-state probes (Oladri, Jawahar and Mohamed, 2026,
arXiv:2607.21433, which predicts runs that never finish; we target
answered wrong answers), activation monitors for deception
(Goldowsky-Dill et al., 2025) and their vulnerability to obfuscated
activations (Bailey et al., 2024), biology-inspired regulation and
interoception (Man and Damasio, 2019; Chiba and Krichmar, 2020; Byrnes,
Intro to Brain-Like-AGI Safety; Mineault et al., 2024), clinical early
warning (NEWS2) and critical transitions (Scheffer et al., 2009), and
accelerator-adjacent guarantee processors (flexHEG). What this work
adds, to our knowledge and without a systematic literature search, is
the combination: an external, text-blind regulator evaluated in a
deadline race that counts compute, against a larger LLM judge and length
and type controls, with a pre-registered fresh test set.

9\. Conclusion

Before the answer exists, under a deadline that counts compute, a
text-blind regulator reading a transformer's layer telemetry raised
in-time warnings on more wrong answers than a larger LLM judge reading
the reasoning so far and than a length control, on a pre-registered
fresh test set. Exploratory checks added afterwards point the same way:
question-type and type-by-length baselines, equal false-alarm rates
among monitorable episodes (smaller margin, lower bound near zero), and
a threshold frozen from training data (with no judge comparison). On
finished answers, self-consistency is more accurate. The design came
after a pre-registered race the regulator lost (YB-0031: 4 vs 12 of 47)
and a design rejected for look-ahead (YB-0032); the redesigned result
was first met in YB-0033 and replicated in YB-0034 under the original,
since-corrected protocol, and confirmed under the corrected protocol in
YB-0035. It is supported on the pre-registered test set and narrow in
scope.

10\. Next steps

1.  **External validation (YB-0037):** Qwen3-VL-30B-A3B (48 layers, 128
    experts), with its synchronization bug fixed and tested.

2.  **Prose-span hallucination flagging (YB-0038):** span-level ground
    truth; does the risk trace rise inside false claims and not around
    true ones?

3.  **Hidden-state probe baseline (YB-0042):** the same race against a
    standard linear probe on raw activations.

4.  **Uncertainty and per-type analyses:** per-checkpoint intervals for
    all seeds; per-type breakdown; measuring the confidence of caught
    errors.

5.  **Dense models:** Qwen3-8B, Llama 3.1 8B, Gemma 2 9B, without router
    entropy.

6.  **Transparent scoring and the reasoning-only re-test (YB-0036):**
    close the gap between AI-EWS and the regulator; test the
    reasoning-trace claim on reasoning-only features.

7.  **Hardware path:** a virtual-SoC interface specification (telemetry
    port, regulator core, flag lane), and outside replication.
