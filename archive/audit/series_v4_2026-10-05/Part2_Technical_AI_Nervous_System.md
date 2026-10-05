An External Nervous System for Transformers: What Held Up, What Didn't,
and the Architecture Left Standing

*Part 2 of 2, the evidence: the theory, the math and code of every
check, YB-0045 and four pre-registered attempts to knock it down,
enforcement timing, the chip, and every limit. Every claim points to a
public file.*

*By Yobie Benjamin and AI. I came up with the ideas and directed the
work; code, experiments, analyses and drafts were produced by me
together with AI systems (Anthropic's Claude as research assistant; a
locally run gpt-oss-120b for some code).*

*Two GitHub repositories. The public one,
github.com/YobieBenjamin/autonomic-graph-regulation, holds the code, the
packed recordings, every pre-registration, result file, audit and
correction; every path in this post points there. The private one,
github.com/YobieBenjamin/safety, holds the full commit history that
timestamps the pre-registrations; each public snapshot names the private
commit it came from, and reviewers can have read access on request.*

Part 1 told the story in plain English: the AI sounds just as sure when
it's wrong; the brain and the hospital show how to build checks that
don't trust its words; my watchdog beat an AI judge; then I tried to
knock that result down four ways over two days: one test knocked it
down, one confirmed the layered design, and one turned up a surprise.
This part is the evidence: the math, the code, every number with its
interval and the file it lives in. If you read only two sections, read 6
to 9 (the four new tests) and 13 (the limitations).

1\. The theory, and where each piece stands

A decoder-only transformer computes p(x_t \| x_1 ... x\_{t−1}) and
samples. That is the entire machine: extremely fancy autocomplete with a
PhD vocabulary. Ask it to check itself and you get another sample from
the same weights, so errors in the answer and errors in the review are
correlated by construction. Self-evaluation is not useless (Kadavath et
al., 2022, found large models reasonably calibrated in suitable
formats), but a model's judgment is least reliable exactly where it
fails. Measured here: answer-token confidence detected wrong answers at
AUROC 0.366 \[0.304, 0.433\] on a fresh test set, worse than a coin flip
(YB-0031,
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0031-confirmatory-deep-program/docs/results.json).

The theory (full text with evidence labels:
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/docs/THEORY_AND_POSITION.md):
safety needs checks that are not language models, that read internal
state rather than words, that act faster than the model can commit an
action, that are layered, that give graded alarms the way a hospital
does, and that eventually run on their own hardware. Status after
YB-0049:

  -------- --------------------------- ---------------- -------------------------
  **\#**   **Principle**               **Status**       **Evidence**

  P1       The model never judges its  Established      Every outside-code
           own output; outside code    here; refined    monitor caught more
           checks                                       errors than the LLM
                                                        judge; the gap was tested
                                                        for difficulty,
                                                        regulator, probe, stack
                                                        and banded score
                                                        (YB-0045, YB-0046,
                                                        YB-0048); the strongest
                                                        detector is the model's
                                                        self-disagreement
                                                        measured by outside code
                                                        (YB-0049)

  P2       Read internal state, not    Split            Beats difficulty
           words                                        (YB-0046) and transfers
                                                        to unseen task types
                                                        (YB-0047 B); not shown to
                                                        beat a trained text
                                                        reader in-distribution
                                                        (YB-0047 A)

  P3       Reflex speed: t_alarm +     Established here YB-0044
           L_enforce \< t_commit       (timing)         

  P4       Graded escalation, hospital Triage only      Clean risk gradient;
           style                                        worse than the best
                                                        monitor as a single alarm
                                                        (YB-0048)

  P5       Layering                    Stage-diverse:   YB-0049 +0.167 \[+0.092,
                                       beats best       +0.250\]; YB-0048; not
                                       pre-answer       shown to beat
                                       check;           self-consistency alone
                                       same-stage: no   

  P6       Separate substrate          Proposal         Section 10
           (dedicated chip)                             

  P7       Biology-inspired features   Evidence against Telemetry regulator never
           beat generic ones                            beat the probe; did not
                                                        transfer
  -------- --------------------------- ---------------- -------------------------

2\. Instruments

-   **Monitored model:** gpt-oss-20b (MXFP4/Q8 MLX build, M4 Max 128
    GB), 24 blocks, 32 routed experts per block, greedy decoding, low
    reasoning effort.

-   **Telemetry tap:** per token and layer ℓ: ‖a_ℓ‖ (attention update),
    ‖m_ℓ‖ (expert update), ‖x_ℓ,out‖, cos(x_ℓ,in, x_ℓ,out) and router
    entropy −Σ p_e log p_e: 120 values per token. A synchronization test
    against fresh uncached forward passes runs before every recording
    (an early one-token lag was found by audit, fixed and verified:
    github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/archive/audit/artifacts/shift_verification.json).

-   **Ground truth:** six machine-gradable task types (5- and 6-digit
    and 3-by-2-digit multiplication, long addition, letter counting, day
    of week, modular exponentiation); correctness is computed, never
    judged by a model.

-   **Data:** YB-0045 recorded 10 derivation seeds (5,365 answered
    episodes) and 3 fresh test seeds 9, 13, 14 (1,605 answered, 138
    wrong) with telemetry and hidden states in the same pass. YB-0046 to
    YB-0048 reuse exactly these recordings through hash-identical local
    copies; the record is
    github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0045-powered-replication/data.

-   **Judge:** gpt-oss-120b (5.6x the monitored model's total
    parameters, 1.4x its active parameters:
    github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/archive/audit/artifacts/model_sizes.json),
    reading the question and the reasoning prefix; median 1.55 s per
    check, 90th percentile 7.2 s
    (github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/archive/audit/artifacts/judge_timing.json).

3\. The race and the statistics

Checkpoints t ∈ {48, 96, 192, 384} tokens exist only while the model is
still reasoning. With t_clock(t) the wall-clock time at t, D the time
the answer is emitted and c the monitor's compute cost (a fixed 5 ms
charge for internal-state and text monitors, assumed and never measured;
measured per call for the judge; 0 for metadata baselines), an alarm
counts only if:

> alarm at t ⇔ s(t) \> τ and t_clock(t) + c ≤ D
>
> v_i = max { s_i(t) : t a checkpoint with t_clock(t) + c ≤ D } (v_i =
> −∞ if no checkpoint qualifies)
>
> τ\* = min { τ : (1/n₀) Σ\_{i: y_i = 0} 1\[v_i \> τ\] ≤ 0.10 } recall =
> (1/n₁) Σ\_{i: y_i = 1} 1\[v_i \> τ\*\]
>
> Δ = recall_A − recall_B; 95% interval: paired bootstrap over episodes,
> 1,000 resamples, τ\* re-set for both monitors in every resample

Every correct answered episode counts in n₀, including those that finish
before the first checkpoint and so can never be alarmed; the threshold
is a comparison device, not a deployment guarantee. The in-time score in
code (identical in YB-0045 to YB-0048):

> def in_time(R, fn, cost):
> V = \[\]
> for r in R:
> lat = np.asarray(r\[\'latency\'\], float); D =
> float(lat\[:r\[\'final_start\'\]\].sum())
> V.append(in_time_max(\[(fn(r, t), float(lat\[:t\].sum()), cost(r, t),
> D) for t in checkpoints(r)\]))
> return np.array(V)

Source:
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0048-multilevel-fusion/tests/experiment.py;
in_time_max, cap_threshold and boot_diff:
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0045-powered-replication/src/corrected.py.

4\. The monitors

4.1 Regulator (the 120-channel telemetry)

At checkpoint t, using only tokens before t: per layer and channel, the
mean and RMSSD over the prefix (24 × 5 × 2 = 240 features); two 24-node
layer coupling graphs summarised by windowed spectral statistics (74
features); and log t. Features are z-scored per (task type, t) with
derivation statistics; L2 logistic regression, C = 0.1
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0045-powered-replication/src/absrace.py).

> W_ij = max\_{g ∈ {0..3}} max( \|ρ(x_i(t), x_j(t+g))\|, \|ρ(x_j(t),
> x_i(t+g))\| ), 24-token windows, stride 8
>
> L = I − D\^(−1/2) W D\^(−1/2); algebraic connectivity λ₂; modularity Q
> = sᵀBs/(4m), B = W − ddᵀ/(2m)

4.2 Hidden-state probe (the standard tool)

> x(t) = \[ h_ℓ(t−1) ; (1/t) Σ\_{k\<t} h_ℓ(k) ; log t \], z-scored per
> (task type, t); p = σ(wᵀx + b)

Layer ℓ and the L2 penalty are chosen by grouped 5-fold cross-validation
on derivation data only (selected: layer 18, C = 0.001). One layer of
gpt-oss-20b is 2,880 values, so x has 5,761 entries
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0045-powered-replication/src/probe.py).

4.3 Question difficulty (no access to the model at all)

Built only from the question text and the true answer, never the model
output
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0046-difficulty-confound/src/difficulty.py).
For addition, carries follow the schoolbook recursion over digits a_k,
b_k from the right:

> c_0 = 0, c\_{k+1} = ⌊(a_k + b_k + c_k) / 10⌋, carries = Σ_k
> 1\[c\_{k+1} \> 0\], chain = longest run of consecutive carries

For multiplication, column sums s_k = Σ\_{i+j=k} a_i b_j are propagated
the same way, giving the number of carrying columns and log(1 + total
carry mass). Other types use string length and true count (letter
counting), year distance, century and leap year (day of week), and
exponent size and binary weight (modular powers). A per-type L2 logistic
regression (C = 1) on these features plus log t forms the baseline;
types with fewer than 5 training errors use their training error rate.

> def add_carries(a, b):
> da, db = \_digits(a)\[::-1\], \_digits(b)\[::-1\]; c = n = run = best
> = 0
> for k in range(max(len(da), len(db))):
> s = (da\[k\] if k \< len(da) else 0) + (db\[k\] if k \< len(db) else
> 0) + c
> c = 1 if s \>= 10 else 0; n += c; run = run + 1 if c else 0; best =
> max(best, run)
> return n, best

4.4 Trained text monitor (reads the words, but is trained)

TF-IDF over token-id unigrams and bigrams of the reasoning tokens before
t (the ids are the text, undecoded; the sandbox has no network to fetch
the tokenizer), at most 50,000 features, min_df 3, sublinear term
frequency, plus log t and task-type indicators; L2 logistic regression
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0047-text-baseline-transfer/src/textmon.py):

> w(g, d) = (1 + ln tf(g, d)) · idf(g), idf(g) = ln((1 + n)/(1 +
> df(g))) + 1, each document vector L2-normalised

C was chosen from {0.1, 1, 10} by grouped 5-fold cross-validation on
derivation data: 1.0, cross-validated AUROC 0.841. A unit test plants a
signal after token t and checks the monitor cannot see it at t.

4.5 Fusion: a learned stack and a hospital-style banded score

Both are fitted on GroupKFold(5) cross-fitted derivation scores of the
four components, so no component's score is evaluated on episodes it was
trained on
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0048-multilevel-fusion/src/fusion.py).

> stack: p = σ( β₀ + Σ_j β_j z( logit s_j ) ), j ∈ {difficulty, text,
> probe, regulator}
>
> banded (NEWS2-style): pts_j(t) = Σ\_{k ∈ {90, 95, 99}} 1\[ s_j(t) \>
> q_k\^(j,t) \], S(t) = Σ_j pts_j(t) ∈ {0, ..., 12}

Here q_k\^(j,t) is the kth percentile of component j's cross-fitted
scores on correct derivation observations at checkpoint t. Every point
traces to one component and one band:

> def points(self, s, t):
> return \[int(sum(v \> q for q in self.b\[(n, t)\])) for n, v in
> zip(self.names, s)\]

5\. The result being tested: YB-0045

Pre-registered, powered (0.77 at an effect of +0.175, above 0.99 at
+0.30), fresh test seeds, plan publicly timestamped before recording.
Regulator minus judge +0.478 \[+0.307, +0.560\]
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0045-powered-replication/docs/results.json):

  ------------------------- ------------ ------------------- ------------
  **Monitor**               **In time    **False alarms (all **Share**
                            (of 138)**   / monitorable)**    

  Probe                     100          9.95% / 16.5%       72%

  Regulator                 94           9.95% / 16.5%       68%

  Length                    39           6.3% / 10.4%        28%

  Task type                 31           5.3% / 8.7%         22%

  LLM judge                 28           7.0% / 11.6%        20%
  ------------------------- ------------ ------------------- ------------

Read at face value, internal state beats the words by a mile. Sections 6
to 8 test whether that reading survives. All three are pre-registered
secondary analyses of the same recordings: the test seeds were analysed
in YB-0045, so they are not fresh tests, and each plan says so. Each
plan was committed, then timestamped by two RFC 3161 authorities and
OpenTimestamps, and only then analysed; the confirmatory runs are gated
so the publish pipeline cannot run them early (protocol rule 14,
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/docs/PROTOCOL.md).

6\. YB-0046: is it just detecting hard questions?

Plan commit fe4ad29; RFC 3161: FreeTSA 18:29:48 UTC, DigiCert 18:29:50
UTC; analysis started 18:29:59 UTC
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0046-difficulty-confound/docs/PREREGISTRATION.md,
with results.json alongside and the start-time record in
docs/run_logs/). The rebuilt regulator, probe and judge reproduce
YB-0045 exactly (94, 100, 28).

  ---------------------------------- ------------------ ------------------
  **Monitor**                        **In time (of      **False alarms**
                                     138)**             

  Probe                              100                9.95%

  Difficulty + regulator (stacked)   99                 9.95%

  Regulator                          94                 9.95%

  Difficulty + length                75                 9.95%

  Difficulty only                    73                 9.95%

  LLM judge                          28                 7.0%
  ---------------------------------- ------------------ ------------------

-   **H1, regulator minus difficulty:** +0.138 \[+0.036, +0.211\].
    Supported.

-   **H2, probe minus difficulty:** +0.181 \[+0.090, +0.273\].
    Supported.

-   **H3, difficulty plus regulator minus difficulty (the decisive
    one):** +0.174 \[+0.096, +0.247\]. Supported.

-   **Secondary, difficulty minus judge:** +0.341 \[+0.190, +0.423\]. A
    score that never touches the model beats the judge.

Descriptive: the advantage grows with reasoning length (per-checkpoint
AUROC at t = 48: difficulty 0.809, probe 0.815, regulator 0.763; at t =
192: 0.741, 0.869, 0.839; at t = 384: 0.521, 0.840, 0.761), and is
concentrated in two task types (day of week, modular powers); for
multiplication and letter counting the regulator does not beat
difficulty and the probe roughly ties it.

7\. YB-0047: internal state vs a trained text monitor, and transfer

Plan commit 9307f20; RFC 3161: FreeTSA and DigiCert 19:24:49 UTC;
analysis started 19:24:50 UTC
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0047-text-baseline-transfer/docs/).
Two flaws were found and fixed before the timestamp, both written into
the plan: infinite in-time scores for never-monitored episodes (now
ranked lowest), and unscaled features for a held-out task type, which
would have biased the transfer test against internal state.

Part A: the trained text monitor

  ---------------------------------- ------------------ ------------------
  **Monitor**                        **In time (of      **False alarms**
                                     138)**             

  Probe                              100                9.95%

  Regulator                          94                 9.95%

  Trained text monitor               90                 9.95%
  ---------------------------------- ------------------ ------------------

-   **H1, probe minus trained text:** +0.072 \[0.000, +0.153\]. Not
    supported (the rule needs the lower bound above zero).

-   **H2, regulator minus trained text:** +0.029 \[−0.045, +0.091\]. Not
    supported.

Per-checkpoint AUROC, text vs probe: 0.822 vs 0.815 (t = 48), 0.848 vs
0.832 (96), 0.859 vs 0.869 (192), 0.855 vs 0.840 (384). Pre-declared
consequence, now triggered: the margin over the judge is not shown to
come from internal state rather than from training a monitor.

Part B: transfer to an unseen task type

For each task type c, all three monitors are refitted without c and
scored on c's test episodes. The regulator and probe standardise per
(type, t); for the held-out type, the statistics come from its
derivation episodes without labels, which a deployment can always
compute from unlabelled traffic:

> μ\_(c,t) = mean { x(r, t) : r a derivation episode of type c },
> σ\_(c,t) = sd { same }; no y used

  ---------------------- ---------------- ---------------- ----------------
  **Held-out type        **Probe**        **Regulator**    **Trained text**
  (errors)**                                               

  Letter counting (13)   0.765            0.570            0.710

  Modular powers (31)    0.698            0.547            0.453

  Hard multiplication    0.715            0.552            0.565
  (36)                                                     

  Day of week (58)       0.530            0.291            0.518

  Pooled (pre-registered 0.664 \[0.617,   0.445 \[0.392,   0.384 \[0.340,
  H3)                    0.713\]          0.499\]          0.433\]
  ---------------------- ---------------- ---------------- ----------------

H3 is supported for the probe only. Pooled values below 0.5 partly
reflect miscalibration across task types (a held-out type's scores land
at the wrong level), rather than only ranking within a type; the
within-type rows show ranking. No monitor transfers to day-of-week
problems.

8\. YB-0048: does same-stage layering beat the best single check?

Plan commit 4a1e395; RFC 3161: FreeTSA and DigiCert 20:10:55 UTC;
analysis started 20:10:56 UTC
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0048-multilevel-fusion/docs/).
The plan disclosed that the single-monitor results were known; only the
fusions were new.

  ---------------------------------- ------------------ ------------------
  **Monitor**                        **In time (of      **False alarms**
                                     138)**             

  Probe (best single)                100                9.95%

  Stack (learned fusion of four)     96                 9.95%

  Hospital banded score              86                 6.4%
  ---------------------------------- ------------------ ------------------

-   **H1, stack minus probe:** −0.029 \[−0.096, +0.044\]. Not supported.

-   **H2, banded minus probe, non-inferiority margin −0.05:** −0.101
    \[−0.164, +0.015\]. Not non-inferior. Integer ties let it use only
    6.4% of the 10% false-alarm budget, a handicap the plan disclosed.

The reason is in the overlap (H3, descriptive; each component at its own
10% threshold): probe and text both caught 81 errors, the probe alone
19, the text monitor alone 9; probe and regulator shared 84. Four views
of the same moment miss the same errors. 117 of 138 errors were caught
by at least one component; 21 by none. Two descriptive results survive:
the stack ranks best at every checkpoint (AUROC 0.852, 0.871, 0.880,
0.876 vs the probe's 0.815, 0.832, 0.869, 0.840), and the banded score
is a clean triage gradient (descriptive; the 1,021 episodes that reached
a checkpoint, 136 of them wrong):

  -------------------------- -------------- -------------- ---------------
  **Banded level**           **Episodes**   **Wrong**      **Failure
                                                           rate**

  Stable (0)                 634            23             3.6%

  Watch (1 to 2)             207            27             13.0%

  Concern (3 to 5)           78             19             24.4%

  Urgent (6 to 12)           102            67             65.7%
  -------------------------- -------------- -------------- ---------------

9\. YB-0049: layers at different stages

Plan commit 1ec19a9; RFC 3161: FreeTSA and DigiCert 23:18:49 UTC on 4
October 2026; OpenTimestamps proof anchored in Bitcoin. Unlike YB-0046
to YB-0048, stage 2 is new data, recorded only after the timestamp:
1,605 reviews between 23:18 UTC and 07:39 UTC, with one manual clean
stop at 20% battery (the 12% guard never fired) and a resume that
verified the plan against the timestamped commit and did not
re-timestamp; run logs in docs/run_logs/ (the review records carry
durations, not wall-clock times; their sum, 4.71 h, matches the two
recording windows)
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0049-stage-diverse-layering/docs/;
recorder
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/agr/selfcons_yb0049.py;
reviews in the same folder's data/).

Stage 2 is self-consistency exactly as in YB-0012 and YB-0031: four
samples of the monitored model at temperature 0.8 with fixed sample
seeds, answers normalised, disagreement with the original answer a_0:

> d = (1/4) Σ\_{k=1..4} 1\[ norm(a_k) ≠ norm(a_0) \] ∈ {0, 0.25, 0.5,
> 0.75, 1}
>
> alarm = 1\[ v1 \> τ1 \] ∨ 1\[ d ≥ δ \], τ1: at most 5% of correct
> episodes alarmed by stage 1, δ = min{ δ\' ∈ {0.25, 0.5, 0.75, 1} :
> union false-alarm rate ≤ 0.10 }

The allocation was fixed in advance; τ1, δ and the comparator's
threshold are re-set in every bootstrap resample. Unit tests check that
the union never exceeds the 10% cap and that a useless stage 2 reduces
exactly to the probe at 5%
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0049-stage-diverse-layering/src/layered.py):

> def choose(v1, d, y, alpha1=0.05, cap=0.10):
> c = y == 0; t1 = tight(v1\[c\], alpha1); s1 =
> np.where(np.isfinite(v1), v1, -1e18) \> t1
> for dl in D_GRID:
> if np.mean((s1 \| (d \>= dl))\[c\]) \<= cap: return t1, dl
> return t1, None

  ---------------------------------- ------------------ ------------------
  **Monitor**                        **In time or       **False alarms**
                                     before release (of 
                                     138)**             

  Layered: probe at 5% + review at d 123                6.95%
  ≥ 0.75                                                

  Self-consistency alone             124                8.86%
  (descriptive)                                         

  Probe alone                        100                9.95%
  ---------------------------------- ------------------ ------------------

-   **H1, layered minus probe:** +0.167 \[+0.092, +0.250\]. Supported.

-   **H2 (descriptive):** of the 38 errors the probe missed, the review
    caught 28.

-   **H3 (descriptive):** overlap of caught errors, probe vs
    self-consistency 0.697 (Jaccard), against 0.743 for probe vs text in
    YB-0048: the stages fail somewhat more differently.

The finding the plan did not anticipate: self-consistency alone (AUROC
0.965) caught as many errors as the layered system. That comparison was
not pre-registered, so it is descriptive, but it changes the picture.
The strongest detector here resamples the monitored model. It does not
ask the model to judge its answer; outside code measures whether the
model reproduces it. Principle P1 is refined accordingly: the model
never judges its own output, and its self-disagreement, computed
externally, is a legitimate post-answer signal. The review costs a
median 8.2 s (90th percentile 20.7 s), so it needs a hold gate; it is
the only layer that sees the 584 answered episodes that finish before
the first checkpoint (it caught 2 errors there); and the layered system
reached nearly the same recall (123 vs 124) with fewer false alarms
(6.95% vs 8.86%). Exploratory allocation sensitivity: a 2.5% stage-1
budget gives 121 caught at 4.8% false alarms, 7.5% gives 127 at 9.3%.

10\. YB-0044: the warning meets real enforcement

NVIDIA's Open Agent Safety Platform pairs OpenShell, an open-source
sandbox that enforces policy outside the agent process, with Sentry, a
reference design on BlueField-4. It governs actions, not model
internals, so a permitted action resting on a wrong conclusion passes.
YB-0044 (pre-registered, replay of 276 YB-0045 episodes through
open-source OpenShell on a Mac, no model in the loop, not Sentry)
measured the race:

> a warning protects only if t_alarm + L_enforce \< t_commit

A deny took effect after a median 5.47 s (4.99 to 5.94 s) on this setup
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0044-openshell-gating/docs/reload_timing.json).
Reactive blocking let 74 of 93 alarmed wrong commits through, 79.6%
\[72.0%, 87.1%\]; hold-until-cleared stopped all 93 by design, at a
median 7.4 s wait and 16 of 138 correct commits held
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/algorithms/YB-0044-openshell-gating/docs/results.json).
The direction was foreseeable from the plan's own files; the run
confirmed real enforcement behaved as predicted.

11\. The architecture the evidence now supports

YB-0048 refines P5: layers must differ in stage and signal, or their
misses correlate. The proposed stack, each level mapped to its
biological and clinical analogue
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/docs/THEORY_AND_POSITION.md):

-   **Pre-answer, milliseconds:** internal-state monitor (probe class),
    with difficulty and trained-text monitors as context. Analogue:
    error-related negativity, which peaks roughly 100 ms after an error
    (Yeung, Botvinick and Cohen, 2004).

-   **Graded score:** a NEWS2-style banded level used for triage and to
    pick the action (Royal College of Physicians, 2017).

-   **Post-answer, seconds:** self-consistency review: 124 of 138 alone
    in YB-0049 (AUROC 0.965), AUROC 0.982 on finished answers in
    YB-0031. The model's answers are resampled; outside code decides.
    Seconds, so it sits behind a hold gate.

-   **Gate:** hold irreversible actions until cleared. Analogue: the
    stop process racing the go process (Logan and Cowan, 1984);
    stop-signal reaction times near 190 ms, and as fast as about 120 ms
    (Aron and Poldrack, 2006).

-   **Human:** authorisation for lethal or irreversible actions, by
    someone who can be held accountable (the responsibility gap,
    Sparrow, 2007, an argument rather than a settled conclusion).

The dedicated chip (proposal, not built). One probe check is a dot
product over 5,761 values: about 5,800 multiply-adds. In 16-bit
precision one tapped layer is 5.8 KB per token; at the measured median
of 14.4 ms per token over 442,306 tokens
(github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/archive/audit/artifacts/token_timing_and_width.json)
that is about 400 KB/s per stream, and about 58 MB/s per layer at 10,000
tokens per second. Trivial for fixed-function silicon. Two hard
dependencies: accelerator vendors would need to expose a read-only
activation tap, and a separate chip protects the monitor from tampering,
not from a model trained to obfuscate its activations (Bailey et al.,
2024).

12\. Process integrity, including what went wrong along the way

Seven process findings from these three tests are logged as PF-1 to PF-7
in
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/CORRECTIONS.md,
and four became protocol rules (14 to 17). The ones that mattered: the
publish pipeline re-runs experiments, so for analyses whose test data
already existed it would have run them before the timestamp (now gated,
verified in the sandbox and in the live publish); a waiting script would
have re-timestamped a plan after its analysis started (stopped before it
could); a dry-run crash surfaced only after 30 minutes (a smoke mode now
runs every code path in minutes before any dry run); and hard-linked
data copies were tracked in git, doubling uploads and breaking the
public push (copies untracked, hash-identical to YB-0045's data, which
remains the public record). The earlier, audited drafts of this series
overstate what internal state adds and are marked superseded in the
archive.

13\. Limitations

-   **One model, one task family:** gpt-oss-20b on six synthetic
    machine-gradable task types, four checkpoints up to 384 tokens, one
    machine. Hidden-state error detectors generalise poorly across
    datasets (Orgad et al., 2024); YB-0047 B shows partial transfer for
    the probe only.

-   **Secondary analyses:** YB-0046 to YB-0048 reuse YB-0045's test
    seeds; their plans were fixed before analysis, but the data were not
    fresh. YB-0049's stage-2 data are new, but its test episodes and
    stage-1 results were known.

-   **Audits:** twelve so far. The twelfth (Claude Fable 5.1 and
    GPT-5.5, both with repository access, and GLM with an evidence
    bundle) covered this version and YB-0046 to YB-0049; all three
    returned publishable with fixes, with no wrong number and no
    critical finding, and the fixes are applied (CORRECTIONS.md, A12-1
    to A12-8). No human expert review yet.

-   **Untested:** open prose, intent-type failures, adversarial
    manipulation of activations, live agents, deployment-speed
    enforcement, the chip.

-   **YB-0044** is a replay through open-source OpenShell on a
    Mac-specific setup; it demonstrates the race, not deployment
    performance.

14\. Related work

Hidden-state truthfulness and error probes (Azaria and Mitchell, 2023;
Burns et al., 2023; Kadavath et al., 2022; Orgad et al., 2024; Kossen et
al., 2024); output-uncertainty methods (Kuhn, Gal and Farquhar, 2023;
Farquhar et al., 2024; self-consistency, Wang et al., 2022, proposed
there to improve accuracy and adapted here as a disagreement signal);
early detection of reasoning non-convergence (Oladri, Jawahar and
Mohamed, 2026, arXiv:2607.21433); activation monitors for deception
(Goldowsky-Dill et al., 2025) and their vulnerability to obfuscated
activations (Bailey et al., 2024); biology-inspired self-monitoring
(Chiba and Krichmar, 2020; Byrnes, 2022, blog series; Mineault et al.,
2024); response inhibition and error monitoring (Logan and Cowan, 1984;
Aron and Poldrack, 2006; Yeung, Botvinick and Cohen, 2004); the
responsibility gap (Sparrow, 2007); clinical early warning (Royal
College of Physicians, 2017); accelerator-adjacent guarantee processors
(Petrie and Aarne, 2025); and agent sandboxing with out-of-band
enforcement (NVIDIA OpenShell and Sentry, 2026). Every citation was read
in full; registry with links:
github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/docs/sources/CITATIONS.md.

15\. Where I stand

-   **Holds:** the model should never judge its own output; layers at
    different stages beat the best pre-answer check; internal state sees
    more than question difficulty, and the probe (not the telemetry
    regulator) kept working on an unseen task type where the trained
    text monitor did not (a comparison that was not pre-registered);
    timing decides whether a warning protects anyone; a hospital-style
    score gives a clean triage gradient (descriptive).

-   **Did not hold:** internal state beating a trained text reader on
    familiar tasks; my telemetry features beating a standard probe;
    same-stage layering beating the best single check; stage-diverse
    layering beating self-consistency alone (a tie, descriptive).

-   **Next:** YB-0050, a powered decider on fresh test sets for the
    close calls (internal state vs a trained text reader; layered vs
    self-consistency alone), then the scale-up.

-   **Then, at scale:** eight theories with pass criteria, models,
    compute (roughly 1,000 to 2,000 GPU-hours) and people:
    github.com/YobieBenjamin/autonomic-graph-regulation/blob/main/docs/SCALE_UP_PROPOSAL.md.
    The centre of it is T3 (internal state vs trained text across six
    models) and T4 (transfer).

16\. An invitation to people with more compute than one MacBook

The next proofs need open-weights models at frontier scale, test sets
with thousands of errors across task families, accelerator-adjacent
telemetry hardware, and human experts trying to break the results. If
you run a model lab, a cloud or chip company, or a university group and
can do any of that, the repository is public under PolyForm
Noncommercial and CC BY-NC, and I would love to hear from you:
yobie@ieee.org. Bring your hardest test.
