#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0045 chain (usage: agr/yb0045_chain.sh <protocol-commit>): wait for the pre-registration on GitHub -> alignment tests ->
# record derivation seeds 5 6 7 10 11 12 then fresh test seeds 9 13 14 -> judge on test seeds -> pack (no shift) ->
# reuse packed seeds 2 3 4 8 from YB-0042 -> analysis in the sandbox -> publish. Each stage alone.
cd "$(dirname "$0")/.."; export PATH=$HOME/.lmstudio/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
PROTO="$1"; LOG=/tmp/yb45_chain.log; log() { echo "$(date +%H:%M) $1" >> $LOG; }
[ -n "$PROTO" ] || { echo 'usage: agr/yb0045_chain.sh <protocol-commit>'; exit 1; }
until git fetch -q origin && git merge-base --is-ancestor "$PROTO" origin/main; do sleep 30; done
log "protocol $PROTO confirmed on GitHub"
.venv/bin/python agr/test_layertap_alignment.py > /tmp/yb45_align1.log 2>&1 || { log 'ABORT: telemetry alignment test failed'; exit 1; }
.venv/bin/python agr/test_hstap_alignment.py > /tmp/yb45_align2.log 2>&1 || { log 'ABORT: hidden-state alignment test failed'; exit 1; }
log 'both alignment tests passed'
for S in 5 6 7 10 11 12 9 13 14; do
  .venv/bin/python agr/recorder.py 100 800 --layers --hs --seed=$S > /tmp/yb45_rec$S.log 2>&1 || { log "ABORT: recording seed $S failed"; exit 1; }
  log "seed $S recorded ($(wc -l < data/agr/episodes_LH_seed$S.jsonl) episodes)"
done
lms server status 2>&1 | grep -q 'is running' || lms server start --port 1234 >/dev/null 2>&1
lms load openai/gpt-oss-120b --context-length 65536 --gpu max -y --identifier local-strong >/dev/null 2>&1
for S in 9 13 14; do
  EPISODES_FILE=data/agr/episodes_LH_seed$S.jsonl ALL_EPISODES=1 CKPT=abs SEED=$S .venv/bin/python agr/prefix_monitors.py judge > /tmp/yb45_judge$S.log 2>&1; log "judge on seed $S done"
done
lms unload local-strong >/dev/null 2>&1
D=algorithms/YB-0045-powered-replication/data
for f in algorithms/YB-0042-probe-baseline/data/seed{2,3,4,8}_LH.jsonl.gz algorithms/YB-0042-probe-baseline/data/layers_LH_seed{2,3,4,8}_0.npz algorithms/YB-0042-probe-baseline/data/hs_seed{2,3,4,8}.npz; do cp "$f" $D/; done
.venv/bin/python - <<'PY' >> $LOG 2>&1
import json, gzip, os, numpy as np
D = 'algorithms/YB-0045-powered-replication/data'
for S in ('5', '6', '7', '10', '11', '12', '9', '13', '14'):
    src = 'data/agr/episodes_LH_seed%s.jsonl' % S; R = [json.loads(l) for l in open(src)]
    assert all('toks' in r for r in R), 'fixed recorder required'
    with gzip.open(os.path.join(D, 'seed%s_LH.jsonl.gz' % S), 'wt') as f: f.write(open(src).read())
    lay, hs = {}, {}
    for r in R:
        st = np.load('data/agr/layers_LH_seed%s/%d.npy' % (S, r['idx'])).astype(float)
        assert len(st) == r['n_tokens'], 'fixed tap: one reading per generated token'
        X = st[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); lay['i%d' % r['idx']] = X.astype(np.float16)
        z = np.load('data/agr/hs_seed%s/%d.npz' % (S, r['idx']))
        for k in z.files: hs['i%d_%s' % (r['idx'], k)] = z[k]
    np.savez_compressed(os.path.join(D, 'layers_LH_seed%s_0.npz' % S), **lay); np.savez_compressed(os.path.join(D, 'hs_seed%s.npz' % S), **hs)
    print('packed seed', S, len(R), 'episodes, no shift')
for S in ('9', '13', '14'):
    with gzip.open(os.path.join(D, 'prefix_judge_abs_s%s.jsonl.gz' % S), 'wt') as f: f.write(open('data/agr/prefix_judge_abs_seed%s.jsonl' % S).read())
PY
log 'packed'
SANDBOX_MEM=16g SANDBOX_TIMEOUT=21600 sandbox/run.sh algorithms/YB-0045-powered-replication all > /tmp/yb45_analysis.log 2>&1; log "ANALYSIS EXIT=$?"
./publish.sh 'YB-0045 powered replication: raw results per pre-registration (interpretation pending)' > /tmp/yb45_publish.log 2>&1; log "PUBLISH EXIT=$?"
log YB0045_ALL_DONE
