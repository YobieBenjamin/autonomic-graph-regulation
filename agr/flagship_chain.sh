#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0012 unattended: wait until BOTH behavior monitors have covered every answered episode, then analyze and publish.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
need=$(.venv/bin/python -c "import json; print(sum(1 for l in open('data/agr/episodes_seed1.jsonl') if json.loads(l)['answered']))")
while true; do
  j=$(wc -l < data/agr/monitors_seed1_judge.jsonl 2>/dev/null || echo 0); s=$(wc -l < data/agr/monitors_seed1_selfcons.jsonl 2>/dev/null || echo 0)
  [ "$j" -ge "$need" ] && [ "$s" -ge "$need" ] && break
  pgrep -f 'monitors.py judge' >/dev/null || [ "$j" -ge "$need" ] || .venv/bin/python agr/monitors.py judge >> /tmp/mon_judge.log 2>&1 &
  pgrep -f 'monitors.py selfcons' >/dev/null || [ "$s" -ge "$need" ] || { echo "selfcons not running with $s/$need done" >> /tmp/flagship.log; exit 1; }
  sleep 30
done
D=algorithms/YB-0012-vitals-vs-behavior-flagship/data
cp algorithms/YB-0015-contamination-test/data/episodes.jsonl.gz $D/seed0.jsonl.gz
gzip -9 -c data/agr/episodes_seed1.jsonl > $D/seed1.jsonl.gz
gzip -9 -c data/agr/monitors_seed1_judge.jsonl > $D/monitors_judge.jsonl.gz
gzip -9 -c data/agr/monitors_seed1_selfcons.jsonl > $D/monitors_selfcons.jsonl.gz
sandbox/run.sh algorithms/YB-0012-vitals-vs-behavior-flagship all > /tmp/yb0012.log 2>&1; echo "ANALYSIS EXIT=$?" >> /tmp/flagship.log
./publish.sh 'YB-0012 flagship: raw results per pre-registration (interpretation pending)' >> /tmp/flagship.log 2>&1; echo "PUBLISH EXIT=$?" >> /tmp/flagship.log
git -C ~/safety pull -q; echo ALL_DONE >> /tmp/flagship.log
