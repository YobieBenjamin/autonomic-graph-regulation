# The AGR theory and position (v2, 2026-10-05; v1 2026-10-04)

Every claim below carries an evidence status. **Established (here)**: supported by a pre-registered test on our data. **Narrow**: supported, but
only for one model and synthetic tasks. **Open**: tested and not supported, or untested. **Proposal**: an engineering design not yet built.

## 1. The theory in one paragraph
A language model cannot be the control on its own actions, because its check on itself is drawn from the same machinery that produced the
mistake. Safety therefore needs checks that are **not language models**, that **read the model's internal state rather than trusting its
words**, that **act faster than the model can commit an action**, and that are **layered** so no single check is trusted alone. Biology shows
the architecture (separate stop circuits, error alarms and homeostatic regulation acting on internal signals, at reflex speed), and the
hospital shows the operating method (measure vital signs, combine them into a graded score, escalate by level, never rely on the patient
saying "I'm fine"). The long-term form is a dedicated, non-LLM monitoring chip running beside the AI accelerator.

## 2. Principles and where the evidence stands
| # | Principle | Status | Evidence |
|---|---|---|---|
| P1 | **Independence:** the model must never judge its own output; checks are computed by outside code (refined after YB-0049: the model's disagreement with itself, measured externally, is a valid post-answer signal) | Established (here), narrow; refined | Every monitor that beat the LLM judge is a small non-transformer model (YB-0045 to YB-0047). Answer-token confidence is inverted (AUROC 0.366, YB-0031); self-consistency works only after the fact |
| P2 | **Interoception:** read internal state, not the words | Partly established | Beats question difficulty (YB-0046: +0.181 [+0.090, +0.273]) and transfers to unseen task types (probe 0.664 [0.617, 0.713], YB-0047). **Not** shown to beat a *trained* reader of the reasoning text in-distribution (YB-0047: +0.072 [0.000, +0.153]) |
| P3 | **Reflex speed:** a warning protects only if t_alarm + L_enforce < t_commit | Established (here) as a timing principle | YB-0044: second-scale permission changes lost 74 of 93 races; hold-until-cleared avoids the race by design (replay, Mac) |
| P4 | **Graded escalation (hospital signalling):** combine signals into a banded score that triggers escalating actions | Partly supported, as triage only | YB-0048: a NEWS2-style banded score of four non-LLM monitors gives a clean risk gradient (failure rate 3.6% stable, 13% watch, 24% concern, 66% urgent) but as a single alarm it is less accurate than the best learned monitor (86 vs 100 of 138; not non-inferior) |
| P5 | **Layering:** independent checks that fail in different ways beat any single check | Same-stage fusion: not supported (YB-0048). Stage-diverse: beats the best pre-answer check (YB-0049, +0.167 [+0.092, +0.250]); not shown to beat post-answer self-consistency alone (124 vs 123, descriptive) | YB-0048: four monitors reading the same moment share most catches and their fusion does not beat the best one (-0.029 [-0.096, +0.044]). The claim is refined: layers must differ in stage and signal (pre-answer internal state, post-answer review, action hold, human) so their misses are less correlated |
| P6 | **Separate substrate:** the check runs on hardware the monitored model's software stack cannot alter | Proposal | NVIDIA Sentry applies the same idea to actions on BlueField-4 DPUs; nothing built here |
| P7 | **Biology-inspired features beat generic ones** | Open, current evidence against | The 120-channel telemetry did not beat a standard probe (YB-0042, YB-0045, YB-0047) and did not transfer (0.445) |

**Position after the evidence:** biology and the hospital are kept as the **architecture and operating method** (P1, P3 to P6). The
specific biology-inspired measurements (P7) are not supported and are not claimed.

## 3. The multi-level checking system (proposal; levels map to biology and to the hospital)
| Level | Biological analogue | Hospital analogue | What it reads | Speed | Action |
|---|---|---|---|---|---|
| L0 Reflex | Spinal reflex | Bedside alarm on a single vital | Fixed thresholds on raw internal signals | microseconds (chip) | Raise a flag |
| L1 Interoceptive monitor | Error-related negativity (about 100 ms) | Continuous vital-signs monitor | Hidden state or telemetry (probe) | milliseconds | Score per token |
| L2 Context monitors | Prefrontal appraisal | Nurse reading the chart | Question difficulty, trained text-prefix classifier | milliseconds | Score per checkpoint |
| L3 Early-warning score | Autonomic integration | NEWS2 aggregate score | Bands from L1 and L2 combined into one level: stable, watch, concern, urgent | milliseconds | Escalation level |
| L4 Gate | Stop signal (stop-signal reaction time near 190 ms, as fast as about 120 ms) | Hold the procedure | Escalation level plus action type (permission system such as OpenShell; out-of-band enforcement such as Sentry) | must beat commit time | Allow, hold, block |
| L5 Review | Deliberate reflection | Senior physician review | Finished answer (self-consistency, LLM judge) | seconds | Second opinion on held actions |
| L6 Human | Conscious decision | Consultant sign-off | Everything above | minutes | Authorise irreversible or lethal actions; accountable |

Escalation rule (NEWS2-style, proposal): stable: proceed and log; watch: proceed, raise sampling caution; concern: hold irreversible actions
for review (L5); urgent: block and require a human (L6).

## 4. The dedicated monitoring chip (proposal; P6)
- **Why a separate chip:** a separate failure domain the monitored model's software cannot reach; fixed-function, deterministic logic that can
  be audited like a medical device; always on; and not an LLM, so it does not inherit language-model failure modes.
- **What it computes (measured sizes from our setup):** the probe reads one layer's hidden state: 2,880 values per token for gpt-oss-20b. A
  logistic check is about 6,000 multiply-adds (last token and prefix mean), trivial for fixed-function hardware. The telemetry variant reads
  120 values per token across all 24 layers.
- **Bandwidth:** about 5.8 KB per token per tapped layer in 16-bit precision. At the measured 14.4 ms per token this is about 400 KB per
  second per stream; a server at 10,000 tokens per second needs about 58 MB per second per tapped layer.
- **Latency target:** decision inside one token time (14.4 ms median measured) end to end, including enforcement (T7 criterion).
- **Coupling:** reads a mirrored activation stream (a telemetry port on the accelerator, or a PCIe or NVLink mirror); emits the escalation
  level to the action gate (L4), for example a Sentry-style out-of-band enforcer on a DPU.
- **Requires from accelerator vendors:** a read-only activation tap. This is the main dependency.
- **Prototype path:** an FPGA card fed by a software hook, measuring end-to-end alarm-to-enforcement latency against token time.
- **What a chip does not solve:** a model trained to obfuscate its activations can defeat activation monitors (Bailey et al., 2024); a
  separate chip protects the monitor from tampering, not from evasion. Robustness (T8) must be tested separately.

## 5. Where NVIDIA's platform fits, stated precisely
OpenShell (software, open source) and Sentry (a reference design on BlueField-4) govern what an agent may **do**. Our monitor watches whether
the model's **reasoning** is going wrong. In YB-0044 (a replay through open-source OpenShell on a Mac, no model in the loop, no Sentry) the
combination stopped every alarmed wrong action only in hold-until-cleared mode, by design; reacting through a permission change lost most
races. "The coupling works" is true for hold mode as a design property; it is not yet shown live, at deployment speed or on NVIDIA hardware.

## 6. Next tests
- YB-0050 (laptop): a powered decider on fresh test sets for the close calls: internal state vs a trained text reader, and layered vs self-consistency alone.
- Scale-up T1 to T8 (docs/SCALE_UP_PROPOSAL.md), including a chip prototype for P6 and T7, and adversarial tests (T8).
