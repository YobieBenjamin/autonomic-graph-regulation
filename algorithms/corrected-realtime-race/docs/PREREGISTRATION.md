# YB-0035 pre-registration: the real-time race re-run under the corrected protocol (independent audit fixes)

Committed together with the complete analysis code and its dry-run output **before seed 7 exists** (fixes audit F11).

## Why
An independent audit (archive/audit/independent_audit_2026-09-30.md) of YB-0033/34 found, and we independently verified:
F4 the layer tap lagged one token (stale, not future, readings); F5 never-answered episodes were silently excluded;
F8 the organism's false-alarm rate slightly exceeded the 10% cap; F9 false alarms among monitorable episodes were
unreported; F10 bootstrap intervals ignored threshold uncertainty; F28 lead times were not at the first crossing; F29
live compute timing made results non-deterministic; F30 judge prefixes were re-tokenized. YB-0035 re-runs the whole
experiment with all of these fixed.

## Instruments (fixed)
agr/layertap.py discards the prompt pass (F4; permanent test agr/test_layertap_alignment.py). Old recordings (seeds 2-6)
are realigned by the verified one-step shift (agr/pack_realigned.py; agr/verify_realignment.py). Seed 7 is recorded
with the fixed tap and packed **without** a shift. The recorder saves exact token ids; judge prefixes use them (F30).

## Data
Derivation: seeds 2-4 (realigned; answered episodes). **Primary test: seed 7** (600 episodes, `agr/recorder.py 100 800
--layers --seed=7`, recorded alone). Secondary: seeds 5 and 6 (realigned; behavior monitors as recorded in YB-0033/34).

## Monitors and race
As YB-0033 (organism, AI-EWS v4, length controls C1/C2, LLM judge and self-consistency at t in {48, 96, 192, 384}),
with: fixed compute cost 5 ms per organism or AI-EWS check (F29); behavior monitors' measured compute; threshold = the
tightest value with **at most 10%** of test correct episodes alarmed (F8); rates also among monitorable episodes (F9);
seconds to spare at the first in-time crossing (F28); bootstrap resampling all episodes with thresholds re-set in each
resample (F10; 1000, seed 0).

## Hypotheses and decision rule
- **Primary (CONFIRMED iff):** on seed 7 (answered episodes), organism minus best behavior monitor **and** organism minus
  best length control, in-time recall at <= 10% false alarms, both 95% CIs above 0.
- **Sensitivity (F5):** the same on seed 7 including never-answered episodes as failures (deadline = end of generation).
- **Secondary:** seeds 5 and 6 each; pooled 5+6+7 (R3).
- Reported: AI-EWS v4 vs best length control; monitorable rates; per-checkpoint AUROC of organism and judge.
All outcomes reported.
