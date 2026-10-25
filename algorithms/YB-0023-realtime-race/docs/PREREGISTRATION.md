# EXPERIMENT-REALTIME-RACE pre-registration: the real-time race (latency- and information-matched monitoring)

Committed before any EXPERIMENT-REALTIME-RACE analysis or any prefix monitor run.

## Question
A safety regulator coupled one-to-one to an accelerator must act before the answer is emitted. Under that constraint,
does the organism beat behavior monitoring?

## Data
EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP held-out episodes (seed 1, 217 answered, 21 wrong) with per-token wall-clock latencies; organisms O (EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP)
and O-deep (EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM), both frozen from seed 0.

## Regime EXPERIMENT-DEADLINE-REGIME, deadline (primary)
Deadline = the wall-clock time the first answer token is emitted. A monitor alarm counts only if the monitor has
finished computing before the deadline, measured on this machine. At reasoning checkpoints f in {25%, 50%, 75%} of the
reasoning tokens, each monitor may start computing on the information available then:
- O and O-deep: prefix vitals; compute time measured (organism update per token + scoring).
- EXPERIMENT-LLM-JUDGE-MONITOR judge: reads the question and the reasoning prefix text; its measured wall-clock inference time is added.
- EXPERIMENT-SELF-CONSISTENCY-MONITOR self-consistency: 2 continuations sampled from the prefix to completion; measured generation time is added.
A monitor that cannot finish before the deadline at a checkpoint contributes no alarm from that checkpoint.
Thresholds: each monitor's 10%-FPR threshold on correct episodes (seed-0 thresholds for organisms; for EXPERIMENT-LLM-JUDGE-MONITOR and EXPERIMENT-SELF-CONSISTENCY-MONITOR the
threshold is set on this data's correct episodes, which favors them).
**Primary metric:** recall of wrong answers alarmed before the deadline at 10% FPR.
**EXPERIMENT-REALTIME-RACE-ORGANISM-WINS:** recall(O or O-deep, best of the two, declared by name here: O-deep) - recall(best behavior) > 0, paired bootstrap CI above 0.

## Regime EXPERIMENT-INFORMATION-MATCHED-REGIME, information-matched (secondary)
Same checkpoints, compute time ignored: AUROC of each monitor using only the prefix. Reported per checkpoint.

All outcomes reported, including if behavior monitors still win.
