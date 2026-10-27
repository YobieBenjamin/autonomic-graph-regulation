#!/usr/bin/env bash
# Waits for AC power, then runs the EXPERIMENT-STAGE-DIVERSE-LAYERING chain (agr/stage-diverse-layering-chain.sh) under caffeinate, plus the OpenTimestamps retry loop.
# The chain is a clean restart: EXPERIMENT-STAGE-DIVERSE-LAYERING was stopped on 2026-10-04 before any commit or timestamp.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
L=/tmp/stage-diverse-layering-power-wait.log; cd ~/Desktop/SAFETY
echo "$(date -u +%H:%M) waiting for AC power" > $L
until pmset -g batt | grep -q "AC Power"; do sleep 60; done
echo "$(date -u +%H:%M) on AC power: starting" >> $L
nohup agr/ots_upgrade_loop.sh > /dev/null 2>&1 &
caffeinate -dimsu agr/stage-diverse-layering-chain.sh
echo "$(date -u +%H:%M) chain exited" >> $L
