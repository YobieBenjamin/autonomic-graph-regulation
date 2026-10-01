#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0032 test-set collection (seed 4), sequential so timed stages run alone: record -> prefix judge -> prefix self-consistency.
cd "$(dirname "$0")/.."; export PATH=$HOME/.lmstudio/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
log() { echo "$(date +%H:%M) $1" >> /tmp/seed4_chain.log; }
.venv/bin/python agr/recorder.py 100 800 --layers --seed=4 > /tmp/rec_L4.log 2>&1; log 'seed 4 recorded'
lms server status 2>&1 | grep -q 'is running' || lms server start --port 1234 >/dev/null 2>&1
lms load openai/gpt-oss-120b --context-length 65536 --gpu max -y --identifier local-strong >/dev/null 2>&1
SEED=4 .venv/bin/python agr/prefix_monitors.py judge > /tmp/prefix_judge4.log 2>&1; log 'prefix judge done'
lms unload local-strong >/dev/null 2>&1
SEED=4 .venv/bin/python agr/prefix_monitors.py selfcons > /tmp/prefix_selfcons4.log 2>&1; log 'prefix selfcons done'
log SEED4_DONE
