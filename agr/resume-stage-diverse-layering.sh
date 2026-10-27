#!/usr/bin/env bash
# ONE-COMMAND RESTART for EXPERIMENT-STAGE-DIVERSE-LAYERING (run from anywhere):  ~/Desktop/SAFETY/agr/resume-stage-diverse-layering.sh
# State at shutdown (2026-10-05 00:05 UTC): plan committed 1ec19a9 and timestamped 23:18:49 UTC (RFC 3161, must NOT be re-timestamped);
# stage-2 recording stopped cleanly mid seed 9. The chain detects the timestamp and resumes at the recording; the recorder skips every
# episode already saved and drops a truncated last line if a power cut left one. Waits for AC power unless run with --now.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers), except the plan-frozen recorders and their data files (see "Kept name").
# Each log or marker was renamed in its writer and its reader together.
cd ~/Desktop/SAFETY || exit 1; L=/tmp/resume-stage-diverse-layering.log
echo "$(date -u +%H:%M) resume requested" | tee -a $L
# Check the plan and the recorder before resuming.
# The plan must be byte-identical to the timestamped commit 1ec19a9. In that commit it still lived under the folder's
# old name, so the old path is read from the commit and compared with the file at its current (descriptive) path.
git show 1ec19a9:algorithms/YB-0049-stage-diverse-layering/docs/PREREGISTRATION.md | cmp -s - algorithms/stage-diverse-layering/docs/PREREGISTRATION.md \
  || { echo 'STOP: plan changed since the timestamped commit 1ec19a9' | tee -a $L; exit 1; }
# Kept name: selfcons_yb0049.py (old file name kept on purpose). The experiment's timestamped plan froze the recorder
# and the analysis that reads its data, byte for byte and at their paths (recorded exception, resolved in a later step).
# So the recorder is still checked byte for byte against the timestamped commit, at its unchanged path.
git diff --quiet 1ec19a9 -- agr/selfcons_yb0049.py || { echo 'STOP: recorder changed since the timestamped commit 1ec19a9' | tee -a $L; exit 1; }
ls algorithms/stage-diverse-layering/docs/PREREGISTRATION.md.*.tsr > /dev/null 2>&1 || { echo 'STOP: timestamp files missing' | tee -a $L; exit 1; }
if [ "$1" != --now ]; then echo 'waiting for AC power (use --now to skip)' | tee -a $L; until pmset -g batt | grep -q 'AC Power'; do sleep 60; done; fi
cp agr/stage-diverse-layering-chain-progress.log /tmp/chain49.log 2>/dev/null
nohup agr/ots_upgrade_loop.sh > /dev/null 2>&1 &
nohup caffeinate -dimsu agr/stage-diverse-layering-chain.sh > /dev/null 2>&1 &
sleep 3; nohup agr/battery_guard.sh > /dev/null 2>&1 &
echo "$(date -u +%H:%M) EXPERIMENT-STAGE-DIVERSE-LAYERING resumed: progress in /tmp/chain49.log, recorder output in /tmp/rec49.log" | tee -a $L
# Kept name: selfcons_yb0049_seed*.jsonl (old name kept: frozen by the plan, see the note above).
for S in 9 13 14; do f=data/agr/selfcons_yb0049_seed$S.jsonl; [ -f $f ] && echo "  seed $S: $(wc -l < $f) reviews saved"; done
