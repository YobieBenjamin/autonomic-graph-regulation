# EXPERIMENT-CORRECTED-REALTIME-RACE pre-registration: the real-time race re-run under the corrected protocol (independent audit fixes)

Committed together with the complete analysis code and its dry-run output **before seed 7 exists** (fixes audit REVIEW-ANALYSIS-CODE-COMMITTED-LATE).

## Why
An independent audit (archive/audit/independent_audit_2026-09-30.md) of EXPERIMENT-CLEAN-REALTIME-RACE/34 found, and we independently verified:
REVIEW-LAYER-TAP-ONE-STEP-LATE the layer tap lagged one token (stale, not future, readings); REVIEW-UNANSWERED-EPISODES-EXCLUDED never-answered episodes were silently excluded;
REVIEW-FALSE-ALARM-CAP-EXCEEDED the organism's false-alarm rate slightly exceeded the 10% cap; REVIEW-MONITORABLE-FALSE-ALARMS-UNREPORTED false alarms among monitorable episodes were
unreported; REVIEW-BOOTSTRAP-IGNORED-THRESHOLD-UNCERTAINTY bootstrap intervals ignored threshold uncertainty; REVIEW-LEAD-TIME-NOT-FIRST-CROSSING lead times were not at the first crossing; REVIEW-LIVE-TIMING-NONDETERMINISTIC
live compute timing made results non-deterministic; REVIEW-JUDGE-PREFIXES-RETOKENIZED judge prefixes were re-tokenized. EXPERIMENT-CORRECTED-REALTIME-RACE re-runs the whole
experiment with all of these fixed.

## Instruments (fixed)
agr/layertap.py discards the prompt pass (REVIEW-LAYER-TAP-ONE-STEP-LATE; permanent test agr/test_layertap_alignment.py). Old recordings (seeds 2-6)
are realigned by the verified one-step shift (agr/pack_realigned.py; agr/verify_realignment.py). Seed 7 is recorded
with the fixed tap and packed **without** a shift. The recorder saves exact token ids; judge prefixes use them (REVIEW-JUDGE-PREFIXES-RETOKENIZED).

## Data
Derivation: seeds 2-4 (realigned; answered episodes). **Primary test: seed 7** (600 episodes, `agr/recorder.py 100 800
--layers --seed=7`, recorded alone). Secondary: seeds 5 and 6 (realigned; behavior monitors as recorded in EXPERIMENT-CLEAN-REALTIME-RACE/34).

## Monitors and race
As EXPERIMENT-CLEAN-REALTIME-RACE (organism, AI-EWS v4, length controls EXPERIMENT-LENGTH-CONTROL-STILL-REASONING/EXPERIMENT-LENGTH-CONTROL-TYPE-PERCENTILE, LLM judge and self-consistency at t in {48, 96, 192, 384}),
with: fixed compute cost 5 ms per organism or AI-EWS check (REVIEW-LIVE-TIMING-NONDETERMINISTIC); behavior monitors' measured compute; threshold = the
tightest value with **at most 10%** of test correct episodes alarmed (REVIEW-FALSE-ALARM-CAP-EXCEEDED); rates also among monitorable episodes (REVIEW-MONITORABLE-FALSE-ALARMS-UNREPORTED);
seconds to spare at the first in-time crossing (REVIEW-LEAD-TIME-NOT-FIRST-CROSSING); bootstrap resampling all episodes with thresholds re-set in each
resample (REVIEW-BOOTSTRAP-IGNORED-THRESHOLD-UNCERTAINTY; 1000, seed 0).

## Hypotheses and decision rule
- **Primary (CONFIRMED iff):** on seed 7 (answered episodes), organism minus best behavior monitor **and** organism minus
  best length control, in-time recall at <= 10% false alarms, both 95% CIs above 0.
- **Sensitivity (REVIEW-UNANSWERED-EPISODES-EXCLUDED):** the same on seed 7 including never-answered episodes as failures (deadline = end of generation).
- **Secondary:** seeds 5 and 6 each; pooled 5+6+7 (EXPERIMENT-POOLED-SEEDS-ESTIMATE).
- Reported: AI-EWS v4 vs best length control; monitorable rates; per-checkpoint AUROC of organism and judge.
All outcomes reported.
