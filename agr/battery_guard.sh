#!/usr/bin/env bash
# Stops EXPERIMENT-STAGE-DIVERSE-LAYERING cleanly if the Mac is on battery at 12% or less (the chain and recorder resume later; no re-timestamp, rule 16).
export PATH=/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH; L=/tmp/battery_guard.log
while pgrep -f agr/yb0049_chain.sh > /dev/null; do
  b=$(pmset -g batt); pct=$(echo "$b" | grep -o '[0-9]*%' | head -1 | tr -d '%')
  if ! echo "$b" | grep -q 'AC Power' && [ "${pct:-100}" -le 12 ]; then
    echo "$(date -u +%H:%M) battery $pct%: stopping EXPERIMENT-STAGE-DIVERSE-LAYERING cleanly" >> $L
    pkill -f agr/yb0049_chain.sh; pkill -INT -f selfcons_yb0049.py
    # Registered name: EXPERIMENT-STAGE-DIVERSE-LAYERING (old ID YB-0049 is kept because code matches on it)
    for c in $(docker ps -q); do docker inspect --format '{{range .Mounts}}{{.Source}} {{end}}' $c | grep -q YB-0049 && docker kill $c > /dev/null; done
    exit 0
  fi
  sleep 60
done
