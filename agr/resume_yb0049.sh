#!/usr/bin/env bash
# ONE-COMMAND RESTART for YB-0049 (run from anywhere):  ~/Desktop/SAFETY/agr/resume_yb0049.sh
# State at shutdown (2026-10-05 00:05 UTC): plan committed 1ec19a9 and timestamped 23:18:49 UTC (RFC 3161, must NOT be re-timestamped);
# stage-2 recording stopped cleanly mid seed 9. The chain detects the timestamp and resumes at the recording; the recorder skips every
# episode already saved and drops a truncated last line if a power cut left one. Waits for AC power unless run with --now.
cd ~/Desktop/SAFETY || exit 1; L=/tmp/resume_yb0049.log
echo "$(date -u +%H:%M) resume requested" | tee -a $L
git diff --quiet 1ec19a9 -- algorithms/YB-0049-stage-diverse-layering/docs/PREREGISTRATION.md agr/selfcons_yb0049.py || { echo 'STOP: plan or recorder changed since the timestamped commit 1ec19a9' | tee -a $L; exit 1; }
ls algorithms/YB-0049-stage-diverse-layering/docs/PREREGISTRATION.md.*.tsr > /dev/null 2>&1 || { echo 'STOP: timestamp files missing' | tee -a $L; exit 1; }
if [ "$1" != --now ]; then echo 'waiting for AC power (use --now to skip)' | tee -a $L; until pmset -g batt | grep -q 'AC Power'; do sleep 60; done; fi
cp agr/yb0049_chain_progress.log /tmp/chain49.log 2>/dev/null
nohup agr/ots_upgrade_loop.sh > /dev/null 2>&1 &
nohup caffeinate -dimsu agr/yb0049_chain.sh > /dev/null 2>&1 &
sleep 3; nohup agr/battery_guard.sh > /dev/null 2>&1 &
echo "$(date -u +%H:%M) YB-0049 resumed: progress in /tmp/chain49.log, recorder output in /tmp/rec49.log" | tee -a $L
for S in 9 13 14; do f=data/agr/selfcons_yb0049_seed$S.jsonl; [ -f $f ] && echo "  seed $S: $(wc -l < $f) reviews saved"; done
