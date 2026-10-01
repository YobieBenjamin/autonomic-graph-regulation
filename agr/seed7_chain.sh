#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0035 primary test set (seed 7) with the FIXED pipeline, each stage alone: record -> judge -> self-consistency ->
# pack WITHOUT shift (fixed tap is aligned; guard below) -> analysis in sandbox -> publish.
cd "$(dirname "$0")/.."; export PATH=$HOME/.lmstudio/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
log() { echo "$(date +%H:%M) $1" >> /tmp/seed7_chain.log; }
.venv/bin/python agr/test_layertap_alignment.py > /tmp/seed7_aligncheck.log 2>&1 || { log 'ABORT: alignment test failed'; exit 1; }; log 'alignment test passed'
.venv/bin/python agr/recorder.py 100 800 --layers --seed=7 > /tmp/rec_L7.log 2>&1; log 'seed 7 recorded'
lms server status 2>&1 | grep -q 'is running' || lms server start --port 1234 >/dev/null 2>&1
lms load openai/gpt-oss-120b --context-length 65536 --gpu max -y --identifier local-strong >/dev/null 2>&1
ALL_EPISODES=1 CKPT=abs SEED=7 .venv/bin/python agr/prefix_monitors.py judge > /tmp/prefix_judge7.log 2>&1; log 'judge done'
lms unload local-strong >/dev/null 2>&1
ALL_EPISODES=1 CKPT=abs SEED=7 .venv/bin/python agr/prefix_monitors.py selfcons > /tmp/prefix_selfcons7.log 2>&1; log 'selfcons done'
D=algorithms/YB-0035-corrected-realtime-race/data
gzip -9 -c data/agr/episodes_L_seed7.jsonl > $D/seed7_L.jsonl.gz
gzip -9 -c data/agr/prefix_judge_abs_seed7.jsonl > $D/prefix_judge_abs_s7.jsonl.gz; gzip -9 -c data/agr/prefix_selfcons_abs_seed7.jsonl > $D/prefix_selfcons_abs_s7.jsonl.gz
.venv/bin/python - <<'PY' >> /tmp/seed7_chain.log 2>&1
import json, os, numpy as np
R = [json.loads(l) for l in open('data/agr/episodes_L_seed7.jsonl')]; arrs = {}
assert all('toks' in r for r in R), 'seed 7 must be recorded with the fixed recorder (token ids present)'
for r in R:
    st = np.load('data/agr/layers_seed7/%d.npy' % r['idx']).astype(float)
    assert len(st) == r['n_tokens'], 'fixed tap: one reading per generated token'
    X = st[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); arrs['i%d' % r['idx']] = X.astype(np.float16)   # NO shift
np.savez_compressed('algorithms/YB-0035-corrected-realtime-race/data/layers_seed7_0.npz', **arrs); print('packed seed 7 without shift:', len(arrs))
PY
SANDBOX_MEM=6g SANDBOX_TIMEOUT=10800 sandbox/run.sh algorithms/YB-0035-corrected-realtime-race all > /tmp/yb0035.log 2>&1; log "ANALYSIS EXIT=$?"
./publish.sh 'YB-0035 corrected real-time race: raw results per pre-registration (interpretation pending)' > /tmp/publish_yb0035.log 2>&1; log "PUBLISH EXIT=$?"; git -C ~/safety pull -q; log SEED7_ALL_DONE
