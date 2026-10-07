#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Starts the YB-0050 chain: waits for AC power (skip with --now; the chain itself still waits for AC power before recording), then runs the chain under caffeinate with the battery guard
# and the OpenTimestamps upgrade loop. Progress: /tmp/chain50.log (copied to agr/yb0050_chain_progress.log).
cd "$(dirname "$0")/.."; L=/tmp/yb0050_start.log
if [ "$1" != --now ]; then echo "$(date -u +%H:%M) waiting for AC power (use --now to skip)" | tee -a $L; until pmset -g batt | grep -q 'AC Power'; do sleep 60; done; fi
nohup agr/ots_upgrade_loop_yb0050.sh > /dev/null 2>&1 &
nohup caffeinate -dimsu agr/yb0050_chain.sh > /dev/null 2>&1 &
sleep 3; nohup agr/battery_guard_yb0050.sh > /dev/null 2>&1 &
echo "$(date -u +%H:%M) YB-0050 started: progress in /tmp/chain50.log" | tee -a $L
