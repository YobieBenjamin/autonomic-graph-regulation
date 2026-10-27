#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Stops the EXPERIMENT-LOW-FALSE-ALARM-PRECISION chain cleanly at 12% battery when not on AC power; every recorder resumes where it stopped.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers), except the plan-frozen recorders and their data files (see "Kept name").
# Each log or marker was renamed in its writer and its reader together.
export PATH=/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH; L=/tmp/battery_guard51.log
while pgrep -f agr/low-false-alarm-precision-chain.sh > /dev/null; do
  b=$(pmset -g batt); pct=$(echo "$b" | grep -o '[0-9]*%' | head -1 | tr -d '%')
  if ! echo "$b" | grep -q 'AC Power' && [ "${pct:-100}" -le 12 ]; then
    echo "$(date -u +%H:%M) battery $pct%: stopping EXPERIMENT-LOW-FALSE-ALARM-PRECISION cleanly" >> $L
    # Kept name: selfcons_yb0051.py (old file name kept on purpose). The experiment's timestamped plan froze the recorder
    # and the analysis that reads its data, byte for byte and at their paths (recorded exception, resolved in a later step).
    pkill -f agr/low-false-alarm-precision-chain.sh; pkill -INT -f selfcons_yb0051.py; pkill -INT -f 'agr/recorder.py 100 800'; sleep 20
    pkill -TERM -f selfcons_yb0051.py; pkill -TERM -f 'agr/recorder.py 100 800'; sleep 10; pkill -KILL -f selfcons_yb0051.py; pkill -KILL -f 'agr/recorder.py 100 800'
    # Kill every sandbox container that has this experiment's folder mounted. A mount source is an absolute path, so the
    # match is "/algorithms/low-false-alarm-precision" followed by "/", a space or the end: the folder is named after the experiment
    # (2026-10 rename, no YB number), and a different folder whose name merely starts the same way is not matched.
    for c in $(docker ps -q); do docker inspect --format '{{range .Mounts}}{{.Source}} {{end}}' $c | grep -qE '/algorithms/low-false-alarm-precision(/| |$)' && docker kill $c > /dev/null; done
    exit 0
  fi
  sleep 60
done
