#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Publish only after EXPERIMENT-REALTIME-RACE's timed monitors finish (publishing loads the machine and would inflate their timings).
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q REALTIME_RACE_MONITORS_DONE /tmp/realtime-race-chain.log 2>/dev/null; do sleep 60; done
./publish.sh 'EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM report: deep 24-layer organism 0.765 (vs 0.720 shallow, n.s.), first silent slips caught, no longer distinguishable from LLM judge, still inferior to self-consistency; deep possibility-testing backlog EXPERIMENT-ACTIVE-INTEROCEPTIVE-PROBE..0026' > /tmp/publish16.log 2>&1
echo EXIT=$? >> /tmp/publish16.log; git -C ~/safety pull -q; echo DONE >> /tmp/publish16.log
