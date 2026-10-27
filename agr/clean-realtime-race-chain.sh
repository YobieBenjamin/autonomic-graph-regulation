#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# EXPERIMENT-CLEAN-REALTIME-RACE: wait for seed 5 + absolute-checkpoint monitors, pack, analyze once in the sandbox, publish.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while ! grep -q SEED5_DONE /tmp/seed5_chain.log 2>/dev/null; do sleep 60; done
# EXPERIMENT-CLEAN-REALTIME-RACE: the paths below use its descriptive folder name (2026-10 rename, which retired the YB numbers)
D=algorithms/clean-realtime-race/data
gzip -9 -c data/agr/episodes_L_seed5.jsonl > $D/seed5_L.jsonl.gz
gzip -9 -c data/agr/prefix_judge_abs_seed5.jsonl > $D/prefix_judge_abs_s5.jsonl.gz; gzip -9 -c data/agr/prefix_selfcons_abs_seed5.jsonl > $D/prefix_selfcons_abs_s5.jsonl.gz
.venv/bin/python - <<'PY'
import json, os, numpy as np
R = [json.loads(l) for l in open('data/agr/episodes_L_seed5.jsonl')]; arrs = {}
for r in R:
    f = 'data/agr/layers_seed5/' + str(r['idx']) + '.npy'
    if os.path.exists(f):
        X = np.load(f).astype(float)[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); arrs['i' + str(r['idx'])] = X.astype(np.float16)
np.savez_compressed('algorithms/clean-realtime-race/data/layers_seed5_0.npz', **arrs)
PY
SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh algorithms/clean-realtime-race all > /tmp/clean-realtime-race.log 2>&1; echo "ANALYSIS EXIT=$?" > /tmp/clean-realtime-race-chain.log
./publish.sh 'EXPERIMENT-CLEAN-REALTIME-RACE clean real-time race: raw results per pre-registration 300f037 (interpretation pending)' >> /tmp/clean-realtime-race-chain.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/clean-realtime-race-chain.log; git -C ~/safety pull -q; echo ALL_DONE >> /tmp/clean-realtime-race-chain.log
