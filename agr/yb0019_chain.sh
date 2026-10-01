#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while [ ! -f /tmp/deep_chain.log ]; do sleep 30; done
D=algorithms/YB-0019-deep-layer-graph-organism/data; F=algorithms/YB-0012-vitals-vs-behavior-flagship/data
gzip -9 -c data/agr/episodes_L_seed0.jsonl > $D/seed0_L.jsonl.gz
gzip -9 -c data/agr/episodes_L_seed1.jsonl > $D/seed1_L.jsonl.gz
cp $F/seed1.jsonl.gz $D/seed1_original.jsonl.gz; cp $F/monitors_judge.jsonl.gz $F/monitors_selfcons.jsonl.gz $D/
.venv/bin/python agr/pack_layers.py 0 $D/layers_seed0.npz >> /tmp/yb0019_chain.log 2>&1
.venv/bin/python agr/pack_layers.py 1 $D/layers_seed1.npz >> /tmp/yb0019_chain.log 2>&1
sandbox/run.sh algorithms/YB-0019-deep-layer-graph-organism all > /tmp/yb0019.log 2>&1; echo "ANALYSIS EXIT=$?" >> /tmp/yb0019_chain.log
./publish.sh 'YB-0019 deep layer-graph organism: raw results per pre-registration 5c9b9fb (interpretation pending)' >> /tmp/yb0019_chain.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/yb0019_chain.log; git -C ~/safety pull -q; echo ALL_DONE >> /tmp/yb0019_chain.log
