#!/usr/bin/env bash
# Stops EXPERIMENT-STAGE-DIVERSE-LAYERING cleanly if the Mac is on battery at 12% or less (the chain and recorder resume later; no re-timestamp, rule 16).
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers), except the plan-frozen recorders and their data files (see "Kept name").
# Each log or marker was renamed in its writer and its reader together.
export PATH=/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH; L=/tmp/battery_guard.log
while pgrep -f agr/stage-diverse-layering-chain.sh > /dev/null; do
  b=$(pmset -g batt); pct=$(echo "$b" | grep -o '[0-9]*%' | head -1 | tr -d '%')
  if ! echo "$b" | grep -q 'AC Power' && [ "${pct:-100}" -le 12 ]; then
    echo "$(date -u +%H:%M) battery $pct%: stopping EXPERIMENT-STAGE-DIVERSE-LAYERING cleanly" >> $L
    # Kept name: selfcons_yb0049.py (old file name kept on purpose). The experiment's timestamped plan froze the recorder
    # and the analysis that reads its data, byte for byte and at their paths (recorded exception, resolved in a later step).
    pkill -f agr/stage-diverse-layering-chain.sh; pkill -INT -f selfcons_yb0049.py
    # Kill every sandbox container that has this experiment's folder mounted. A mount source is an absolute path, so the
    # match is "/algorithms/stage-diverse-layering" followed by "/", a space or the end: the folder is named after the experiment
    # (2026-10 rename, no YB number), and a different folder whose name merely starts the same way is not matched.
    for c in $(docker ps -q); do docker inspect --format '{{range .Mounts}}{{.Source}} {{end}}' $c | grep -qE '/algorithms/stage-diverse-layering(/| |$)' && docker kill $c > /dev/null; done
    exit 0
  fi
  sleep 60
done
