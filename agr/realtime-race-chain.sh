#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# EXPERIMENT-REALTIME-RACE monitors on a quiet machine: wait for EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM to finish, then judge alone, then self-consistency alone.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd "$(dirname "$0")/.."; export PATH=$HOME/.lmstudio/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q ALL_DONE /tmp/deep-layer-graph-organism-chain.log 2>/dev/null; do sleep 60; done
lms server status 2>&1 | grep -q 'is running' || lms server start --port 1234 >/dev/null 2>&1
lms load openai/gpt-oss-120b --context-length 65536 --gpu max -y --identifier local-strong >/dev/null 2>&1
.venv/bin/python agr/prefix_monitors.py judge > /tmp/prefix_judge.log 2>&1
lms unload local-strong >/dev/null 2>&1
.venv/bin/python agr/prefix_monitors.py selfcons > /tmp/prefix_selfcons.log 2>&1
echo REALTIME_RACE_MONITORS_DONE > /tmp/realtime-race-chain.log
