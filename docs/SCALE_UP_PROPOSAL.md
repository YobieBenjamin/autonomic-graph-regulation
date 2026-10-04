# AGR scale-up proposal: internal-state error monitoring beyond one model and one laptop

Status: DRAFT, 2026-10-04. Section 2 is filled in from YB-0046 and YB-0047 results. Every theory below gets its own pre-registration,
fresh test sets, public timestamps and the same audit trail as YB-0035 to YB-0047.

## 1. What the laptop phase established, and what it cannot
Established (one model, gpt-oss-20b; six synthetic, machine-gradable task types; four checkpoints up to 384 tokens):
- Internal-state monitors (the 120-channel telemetry regulator and a standard hidden-state probe) raised in-time warnings on far more wrong
  answers than an untrained LLM judge reading the reasoning (YB-0045: 94 and 100 of 138 vs 28; +0.478 [+0.307, +0.560]).
- The compact telemetry did not beat a standard probe (YB-0042, YB-0045).
- Reacting through a permission system loses the race at second-scale enforcement latency; holding irreversible actions avoids it by design
  (YB-0044, replay).
Cannot establish on this setup: other model families and scales; natural tasks; open prose; live agents at deployment speed; robustness to
adversarial manipulation; independent replication; hardware-speed enforcement.

## 2. Laptop-phase threat tests (filled in from results)
- YB-0046, difficulty confound (pre-registered secondary analysis of YB-0045 data; plan timestamped 18:29:48 UTC 2026-10-04, analysis started
  18:29:59): all three hypotheses supported. A baseline built only from the question (digits, carries, string length, exponent size)
  plus elapsed length caught 75 of 138 wrong answers, far more than the LLM judge (28; +0.34 [+0.19, +0.42]). The regulator (94) and probe
  (100) still beat it: +0.138 [+0.036, +0.211] and +0.181 [+0.090, +0.273]; difficulty plus regulator beat difficulty alone, +0.174
  [+0.096, +0.247]. Internal state therefore predicts errors beyond problem difficulty here, but most of the margin over the judge was
  available without internals. The advantage grows with reasoning length (checkpoint AUROC at 48 tokens: difficulty 0.81, probe 0.82;
  at 192: 0.74 vs 0.87) and is concentrated in two task types (weekday, modular powers); for multiplication and letter counting the
  regulator did not beat difficulty and the probe roughly tied it (descriptive).
- YB-0047, trained text baseline and cross-task transfer (plan timestamped 19:24:49 UTC, analysis started 19:24:50): a text monitor TRAINED
  on the reasoning tokens caught 90 of 138, close to the probe (100) and regulator (94). Probe minus text +0.072 [0.000, +0.153] and
  regulator minus text +0.029 [-0.045, +0.091]: not supported. The large margin over the LLM judge therefore came mainly from training a
  monitor, not from reading internal state. Transfer to an unseen task type: the hidden-state probe partly transfers (pooled AUROC 0.664
  [0.617, 0.713]); the telemetry regulator (0.445) and the trained text monitor (0.384) do not. No monitor transfers to held-out weekday
  problems.
- Net position entering scale-up: internal state beats question difficulty and untrained judges, is not yet shown to beat trained text
  monitors on in-distribution tasks, and shows its clearest advantage in transfer to unseen task types. The compact telemetry offers no
  accuracy benefit over a standard probe and does not transfer. The scale-up therefore centres on T3 and T4.

## 3. Theories to test, with pass criteria (each pre-registered separately)
| ID | Theory | Primary test | Pass criterion |
|---|---|---|---|
| T1 | Generality: the internal-state advantage holds across model families and scales | Same race on 6 models (MoE and dense, 8B to 120B+) | Internal-state minus best text baseline: lower 95% bound > 0 on at least 5 of 6 models, each with at least 100 wrong answers |
| T2 | Beyond difficulty: internal state predicts errors at matched problem difficulty (supported on synthetic tasks, YB-0046; untested on natural tasks) | Difficulty-matched designs plus natural tasks where difficulty cannot be read off the question; per-task-family analysis, since YB-0046 found the effect concentrated in some task types | Combined (difficulty + internal state) minus difficulty-only: lower bound > 0 in at least 4 of 5 task families |
| T3 | Internals beat text at equal training (NOT supported in-distribution on the laptop data, YB-0047: +0.072 [0.000, +0.153]) | Probe vs trained token classifier vs fine-tuned small LM reading the same prefixes, on 6 models, in-distribution AND out-of-distribution | Probe minus best trained text monitor: lower bound > 0 out-of-distribution on at least 4 of 6 models; in-distribution reported regardless |
| T4 | Transfer: internal-state detectors generalise to unseen task types better than text monitors (probe partly supported on the laptop, YB-0047: 0.664 [0.617, 0.713]; text 0.384) | Leave-one-task-family-out across 5 families, with label-free normalisation for the held-out family and per-family calibration reported separately from ranking | Probe minus trained text, held-out within-family AUROC: lower bound > 0 in at least 3 of 5 families |
| T5 | Open prose: false claims can be flagged at span level before the sentence ends | Long-form answers with programmatic or adjudicated span labels | Span AUROC lower bound > 0.5, with median flag before sentence end |
| T6 | Live gating: hold-until-cleared stops harmful-but-permitted agent actions at acceptable cost | Real multi-step agent tasks, model in the loop, OpenShell on Linux | At least 50% of harmful permitted actions stopped with at most 10% of correct actions held |
| T7 | Compact telemetry: near-probe accuracy at a fraction of the bandwidth | Compact channels vs full hidden state | Within 0.02 AUROC at 10x less data per token |
| T8 | Robustness: the monitor survives adversarial pressure | Obfuscation attacks on activations (Bailey et al., 2024 style) and prompt-level evasion | Recall at matched false alarms drops by at most half under the strongest tested attack |

### Baselines required in every test (lesson of YB-0046)
Every comparison must include, besides LLM judges: (1) a question-difficulty and metadata baseline; (2) an elapsed-length baseline; (3) a
trained text-prefix classifier. Beating an untrained judge alone is not evidence that internal state carries information.

## 4. Technical needs
### Models (open weights, full internal access required)
gpt-oss-20b (anchor, links to all prior results); gpt-oss-120b; Qwen3-VL-30B-A3B (MoE, 48 layers, 128 experts); Llama 3.1 8B and 70B (dense);
Qwen3 32B (dense); one frontier-scale open MoE model if hardware allows (stretch).
### Task families with programmatic ground truth
(a) synthetic arithmetic and symbolic tasks (anchor; difficulty-matched variants); (b) math word problems with numeric answers; (c) code with
unit tests; (d) short-answer factual QA with exact-match checking; (e) long-form prose with span-level labels (programmatic where possible,
adjudicated otherwise).
### Compute (order-of-magnitude estimate; assumptions stated)
Assumptions: 6 models x 5 task families x about 8,000 episodes = about 240,000 episodes; about 400 generated tokens each = about 100 million
tokens; telemetry capture runs in eager mode and is several times slower than optimised serving.
- Recording with telemetry: roughly 300 to 800 H100 GPU-hours (dominated by the 70B and 120B models).
- Behavioural baselines (LLM judges on up to 4 prefixes per episode, about 1 million judge calls): roughly 200 to 400 GPU-hours.
- Trained monitors, probes and analysis: small (CPU or a single GPU).
- Total: roughly 1,000 to 2,000 GPU-hours; at commonly quoted cloud rates of a few dollars per H100 hour, low thousands to under ten thousand
  dollars. Prices vary; to be confirmed with a provider before commitment.
### Storage
Hidden states at 4 checkpoints, 2 vectors per checkpoint, every 4th layer, fp16: on the order of 0.5 to 1 TB in total. Telemetry is small.
### Hardware and enforcement
Linux hosts with Landlock for OpenShell (removes the Mac VM latency confound); access to NVIDIA Sentry on BlueField-4 or equivalent
out-of-band hardware to measure millisecond enforcement (T6 and the latency principle).
### People
One to two ML engineers; one statistician to review analysis plans; two to three independent domain experts to review methods and results;
an adversarial red team for T8; an independent group to rerun the public pipeline.

## 5. Phasing
1. Phase A (laptop, now): YB-0046 and YB-0047; second model family (Qwen3-VL-30B-A3B) and one dense 8B model on the Mac.
2. Phase B (cloud): T1 to T4 on 6 models and 5 task families.
3. Phase C: T5 (prose) and T7 (bandwidth).
4. Phase D: T6 (live agents) and T8 (adversarial), with hardware partner access.

## 6. Risks
Results may not generalise beyond synthetic tasks (T2, T4); trained text baselines may close the gap (T3); adversarial attacks may defeat
activation monitors (T8, known for related monitors); compute estimates may be optimistic for telemetry capture on the largest models.
Each risk has a pre-declared consequence for what may be claimed.
