#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Snapshot everything this machine produced that git does not track (orchestrator run logs, raw model
# outputs, failed attempts, temp logs) into archive/<date>/ so the repo is a complete project record.
# Refuses to proceed if any API key, token or personal email address would be archived.
set -euo pipefail
cd "$(dirname "$0")/.."
d="archive/$(date +%F)"; mkdir -p "$d/orchestrator-runs" "$d/attempts" "$d/logs"
[ -d orchestrator/runs ] && rsync -a orchestrator/runs/ "$d/orchestrator-runs/"
[ -d miner/sandbox ] && rsync -a --exclude '*.so' --exclude __pycache__ miner/sandbox/ "$d/attempts/"
for f in /tmp/*.log /tmp/bench.py /tmp/par.py /tmp/pulse.py; do
  [ -f "$f" ] && cp "$f" "$d/logs/"
done
for f in /tmp/lms_load*.log; do [ -f "$f" ] && tr '\r' '\n' < "$f" | grep -v 'Loading' | tail -20 > "$d/logs/$(basename "$f")"; done
if grep -rIlE 'sk-ant-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|[A-Za-z0-9._%+-]+@(gmail|icloud|ieee|me|outlook)[.]' "$d"; then
  echo 'Secret or personal email found in the files above: archive NOT committed. Remove them and rerun.' >&2; exit 1
fi
echo "archived to $d ($(du -sh "$d" | cut -f1), $(find "$d" -type f | wc -l | tr -d ' ') files)"
