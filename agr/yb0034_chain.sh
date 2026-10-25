#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# EXPERIMENT-CLEAN-REALTIME-RACE: wait for seed 5 + absolute-checkpoint monitors, pack, analyze once in the sandbox, publish.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q SEED6_DONE /tmp/seed6_chain.log 2>/dev/null; do sleep 60; done
# Registered name: EXPERIMENT-REPLICATION-REALTIME-RACE (old ID YB-0034 is kept because code matches on it)
D=algorithms/YB-0034-replication-realtime-race/data
gzip -9 -c data/agr/episodes_L_seed6.jsonl > $D/seed6_L.jsonl.gz
gzip -9 -c data/agr/prefix_judge_abs_seed6.jsonl > $D/prefix_judge_abs_s6.jsonl.gz; gzip -9 -c data/agr/prefix_selfcons_abs_seed6.jsonl > $D/prefix_selfcons_abs_s6.jsonl.gz
.venv/bin/python - <<'PY'
import json, os, numpy as np
R = [json.loads(l) for l in open('data/agr/episodes_L_seed6.jsonl')]; arrs = {}
for r in R:
    f = 'data/agr/layers_seed6/' + str(r['idx']) + '.npy'
    if os.path.exists(f):
        X = np.load(f).astype(float)[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); arrs['i' + str(r['idx'])] = X.astype(np.float16)
np.savez_compressed('algorithms/YB-0034-replication-realtime-race/data/layers_seed6_0.npz', **arrs)
PY
SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/YB-0034-replication-realtime-race all > /tmp/yb0034.log 2>&1; echo "ANALYSIS EXIT=$?" > /tmp/yb0034_chain.log
./publish.sh 'EXPERIMENT-REPLICATION-REALTIME-RACE frozen replication: raw results per pre-registration c8cec65 (interpretation pending)' >> /tmp/yb0034_chain.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/yb0034_chain.log; git -C ~/safety pull -q; echo ALL_DONE >> /tmp/yb0034_chain.log
# EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS (pre-registered for EXPERIMENT-REPLICATION-REALTIME-RACE): equal-false-alarm robustness, then publish again
SANDBOX_MEM=6g SANDBOX_TIMEOUT=3600 sandbox/run.sh algorithms/YB-0034-replication-realtime-race robust > /tmp/yb0034_r2.log 2>&1; echo "EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS EXIT=$?" >> /tmp/yb0034_chain.log
./publish.sh 'EXPERIMENT-REPLICATION-REALTIME-RACE EXPERIMENT-EQUAL-FALSE-ALARM-ROBUSTNESS equal-false-alarm robustness (pre-registered)' >> /tmp/yb0034_chain.log 2>&1; echo R2_PUBLISHED >> /tmp/yb0034_chain.log
