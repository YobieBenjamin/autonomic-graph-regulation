#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Stops the YB-0050 chain cleanly at 12% battery when not on AC power; every recorder resumes where it stopped.
export PATH=/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH; L=/tmp/battery_guard50.log
while pgrep -f agr/yb0050_chain.sh > /dev/null; do
  b=$(pmset -g batt); pct=$(echo "$b" | grep -o '[0-9]*%' | head -1 | tr -d '%')
  if ! echo "$b" | grep -q 'AC Power' && [ "${pct:-100}" -le 12 ]; then
    echo "$(date -u +%H:%M) battery $pct%: stopping YB-0050 cleanly" >> $L
    pkill -f agr/yb0050_chain.sh; pkill -INT -f selfcons_yb0050.py; pkill -INT -f 'agr/recorder.py 100 800'; sleep 20
    pkill -TERM -f selfcons_yb0050.py; pkill -TERM -f 'agr/recorder.py 100 800'; sleep 10; pkill -KILL -f selfcons_yb0050.py; pkill -KILL -f 'agr/recorder.py 100 800'   # MLX can ignore SIGINT (seen 2026-10-06); recorders resume safely
    for c in $(docker ps -q); do docker inspect --format '{{range .Mounts}}{{.Source}} {{end}}' $c | grep -q YB-0050 && docker kill $c > /dev/null; done
    exit 0
  fi
  sleep 60
done
