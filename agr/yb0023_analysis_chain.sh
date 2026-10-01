#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# After the timed monitors finish and the queued YB-0019 publish completes: pack YB-0023 data, analyze in the sandbox, publish.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q DONE /tmp/publish16.log 2>/dev/null; do sleep 60; done
D=algorithms/YB-0023-realtime-race/data; S=algorithms/YB-0019-deep-layer-graph-organism/data
cp $S/seed0_L.jsonl.gz $S/seed1_L.jsonl.gz $S/seed1_original.jsonl.gz $S/layers_seed0.npz $S/layers_seed1.npz $D/
gzip -9 -c data/agr/prefix_judge_seed1.jsonl > $D/prefix_judge.jsonl.gz; gzip -9 -c data/agr/prefix_selfcons_seed1.jsonl > $D/prefix_selfcons.jsonl.gz
sandbox/run.sh algorithms/YB-0023-realtime-race all > /tmp/yb0023.log 2>&1; echo "ANALYSIS EXIT=$?" > /tmp/yb0023_analysis.log
./publish.sh 'YB-0023 real-time race: raw results per pre-registration 5c9b9fb + spec notes (interpretation pending); YB-0022 pre-registration v1 queued' >> /tmp/yb0023_analysis.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/yb0023_analysis.log; git -C ~/safety pull -q; echo ALL_DONE >> /tmp/yb0023_analysis.log
