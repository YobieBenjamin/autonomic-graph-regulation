#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# After the timed monitors finish and the queued EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM publish completes: pack EXPERIMENT-REALTIME-RACE data, analyze in the sandbox, publish.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q DONE /tmp/publish16.log 2>/dev/null; do sleep 60; done
# EXPERIMENT-REALTIME-RACE and EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM: the paths below use their descriptive folder names (2026-10 rename, which retired the YB numbers)
D=algorithms/realtime-race/data; S=algorithms/deep-layer-graph-organism/data
cp $S/seed0_L.jsonl.gz $S/seed1_L.jsonl.gz $S/seed1_original.jsonl.gz $S/layers_seed0.npz $S/layers_seed1.npz $D/
gzip -9 -c data/agr/prefix_judge_seed1.jsonl > $D/prefix_judge.jsonl.gz; gzip -9 -c data/agr/prefix_selfcons_seed1.jsonl > $D/prefix_selfcons.jsonl.gz
sandbox/run.sh algorithms/realtime-race all > /tmp/realtime-race.log 2>&1; echo "ANALYSIS EXIT=$?" > /tmp/realtime-race-analysis.log
./publish.sh 'EXPERIMENT-REALTIME-RACE real-time race: raw results per pre-registration 5c9b9fb + spec notes (interpretation pending); EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING pre-registration v1 queued' >> /tmp/realtime-race-analysis.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/realtime-race-analysis.log; git -C ~/safety pull -q; echo ALL_DONE >> /tmp/realtime-race-analysis.log
