#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0032 full run: wait for the seed-4 test set and its prefix monitors, pack, analyze once in the sandbox, publish.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q SEED4_DONE /tmp/seed4_chain.log 2>/dev/null; do sleep 60; done
D=algorithms/YB-0032-serial-early-warning-organism/data
gzip -9 -c data/agr/episodes_L_seed4.jsonl > $D/seed4_L.jsonl.gz
gzip -9 -c data/agr/prefix_judge_seed4.jsonl > $D/prefix_judge_s4.jsonl.gz; gzip -9 -c data/agr/prefix_selfcons_seed4.jsonl > $D/prefix_selfcons_s4.jsonl.gz
.venv/bin/python - <<'PY'
import json, os, numpy as np
R = [json.loads(l) for l in open('data/agr/episodes_L_seed4.jsonl')]; arrs = {}
for r in R:
    f = 'data/agr/layers_seed4/' + str(r['idx']) + '.npy'
    if os.path.exists(f):
        X = np.load(f).astype(float)[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); arrs['i' + str(r['idx'])] = X.astype(np.float16)
np.savez_compressed('algorithms/YB-0032-serial-early-warning-organism/data/layers_seed4_0.npz', **arrs)
PY
SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0032-serial-early-warning-organism all > /tmp/yb0032.log 2>&1; echo "ANALYSIS EXIT=$?" > /tmp/yb0032_chain.log
./publish.sh 'YB-0032 serial early-warning organism: raw results per pre-registration f0fe5cc (interpretation pending)' >> /tmp/yb0032_chain.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/yb0032_chain.log; git -C ~/safety pull -q; echo ALL_DONE >> /tmp/yb0032_chain.log
