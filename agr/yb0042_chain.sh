#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0042 chain (usage: agr/yb0042_chain.sh <protocol-commit>). Each stage alone, in order: wait until GitHub has the
# pre-registration -> both alignment tests -> record seeds 2, 3, 4 (derivation) and 8 (fresh test) with telemetry and
# hidden states in the same pass -> LLM judge on seed 8 -> pack WITHOUT shift -> analysis in the sandbox -> publish.
cd "$(dirname "$0")/.."; export PATH=$HOME/.lmstudio/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
PROTO="$1"; LOG=/tmp/yb42_chain.log; log() { echo "$(date +%H:%M) $1" >> $LOG; }
[ -n "$PROTO" ] || { echo 'usage: agr/yb0042_chain.sh <protocol-commit>'; exit 1; }
until git fetch -q origin && git merge-base --is-ancestor "$PROTO" origin/main; do sleep 30; done
log "protocol $PROTO confirmed on GitHub ($(git log -1 --format=%cI $PROTO))"
.venv/bin/python agr/test_layertap_alignment.py > /tmp/yb42_align1.log 2>&1 || { log 'ABORT: telemetry alignment test failed'; exit 1; }
.venv/bin/python agr/test_hstap_alignment.py > /tmp/yb42_align2.log 2>&1 || { log 'ABORT: hidden-state alignment test failed'; exit 1; }
log 'both alignment tests passed'
for S in 2 3 4 8; do
  .venv/bin/python agr/recorder.py 100 800 --layers --hs --seed=$S > /tmp/yb42_rec$S.log 2>&1 || { log "ABORT: recording seed $S failed"; exit 1; }
  log "seed $S recorded ($(wc -l < data/agr/episodes_LH_seed$S.jsonl) episodes)"
done
lms server status 2>&1 | grep -q 'is running' || lms server start --port 1234 >/dev/null 2>&1
lms load openai/gpt-oss-120b --context-length 65536 --gpu max -y --identifier local-strong >/dev/null 2>&1
EPISODES_FILE=data/agr/episodes_LH_seed8.jsonl ALL_EPISODES=1 CKPT=abs SEED=8 .venv/bin/python agr/prefix_monitors.py judge > /tmp/yb42_judge8.log 2>&1; log 'judge on seed 8 done'
lms unload local-strong >/dev/null 2>&1
D=algorithms/YB-0042-probe-baseline/data
.venv/bin/python - <<'PY' >> $LOG 2>&1
import json, gzip, os, numpy as np
D = 'algorithms/YB-0042-probe-baseline/data'
for S in ('2', '3', '4', '8'):
    src = 'data/agr/episodes_LH_seed%s.jsonl' % S; R = [json.loads(l) for l in open(src)]
    assert all('toks' in r for r in R), 'fixed recorder required'
    with gzip.open(os.path.join(D, 'seed%s_LH.jsonl.gz' % S), 'wt') as f: f.write(open(src).read())
    lay, hs = {}, {}
    for r in R:
        st = np.load('data/agr/layers_LH_seed%s/%d.npy' % (S, r['idx'])).astype(float)
        assert len(st) == r['n_tokens'], 'fixed tap: one reading per generated token'
        X = st[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); lay['i%d' % r['idx']] = X.astype(np.float16)   # NO shift
        z = np.load('data/agr/hs_seed%s/%d.npz' % (S, r['idx']))
        for k in z.files: hs['i%d_%s' % (r['idx'], k)] = z[k]
    np.savez_compressed(os.path.join(D, 'layers_LH_seed%s_0.npz' % S), **lay); np.savez_compressed(os.path.join(D, 'hs_seed%s.npz' % S), **hs)
    print('packed seed', S, len(R), 'episodes, no shift')
with gzip.open(os.path.join(D, 'prefix_judge_abs_s8.jsonl.gz'), 'wt') as f: f.write(open('data/agr/prefix_judge_abs_seed8.jsonl').read())
PY
log 'packed'
SANDBOX_MEM=12g SANDBOX_TIMEOUT=14400 sandbox/run.sh algorithms/YB-0042-probe-baseline all > /tmp/yb42_analysis.log 2>&1; log "ANALYSIS EXIT=$?"
./publish.sh 'YB-0042 probe baseline: raw results per pre-registration (interpretation pending)' > /tmp/yb42_publish.log 2>&1; log "PUBLISH EXIT=$?"
git -C ~/safety pull -q; log YB0042_ALL_DONE
