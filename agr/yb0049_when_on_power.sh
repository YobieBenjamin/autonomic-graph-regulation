#!/usr/bin/env bash
# Waits for AC power, then runs the YB-0049 chain (agr/yb0049_chain.sh) under caffeinate, plus the OpenTimestamps retry loop.
# The chain is a clean restart: YB-0049 was stopped on 2026-10-04 before any commit or timestamp.
L=/tmp/yb0049_power_wait.log; cd ~/Desktop/SAFETY
echo "$(date -u +%H:%M) waiting for AC power" > $L
until pmset -g batt | grep -q "AC Power"; do sleep 60; done
echo "$(date -u +%H:%M) on AC power: starting" >> $L
nohup agr/ots_upgrade_loop.sh > /dev/null 2>&1 &
caffeinate -dimsu agr/yb0049_chain.sh
echo "$(date -u +%H:%M) chain exited" >> $L
