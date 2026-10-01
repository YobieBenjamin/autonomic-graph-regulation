# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''B2: realigned layer packs (audit F4). Old recordings stored the prompt pass first, so the true reading for generated
token t is stored[t+1] (verified: agr/verify_realignment.py, /tmp/determinism.log). Reasoning segment only, norm channels
log1p-scaled, float16. Also writes realignment_manifest.json with per-seed counts.'''
import json, os, sys, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'algorithms', 'YB-0035-corrected-realtime-race', 'data')
man = {}
for seed in sys.argv[1:]:
    R = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'agr', 'episodes_L_seed' + seed + '.jsonl'))]; arrs, shard, sizes, bad = {}, 0, [], 0
    def flush():
        global shard
        p = os.path.join(OUT, 'layers_seed%s_%d.npz' % (seed, shard)); np.savez_compressed(p, **arrs); sizes.append(round(os.path.getsize(p) / 1e6, 1)); shard += 1
    for r in R:
        f = os.path.join(ROOT, 'data', 'agr', 'layers_seed' + seed, '%d.npy' % r['idx'])
        if not os.path.exists(f): continue
        st = np.load(f).astype(float); fs = max(r['final_start'], 2)
        if len(st) < fs + 1: bad += 1                   # never answered (hit the cap): keep all shifted readings (F5 sensitivity)
        X = st[1:min(fs + 1, len(st))]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); arrs['i%d' % r['idx']] = X.astype(np.float16)
        if len(arrs) == 800: flush(); arrs = {}
    if arrs: flush()
    man[seed] = dict(episodes=len(R), packed=sum(1 for r in R if os.path.exists(os.path.join(ROOT, 'data', 'agr', 'layers_seed' + seed, '%d.npy' % r['idx']))), never_answered_kept_with_last_reading_dropped=bad, shard_mb=sizes)
    print('seed', seed, man[seed], flush=True)
json.dump(man, open(os.path.join(OUT, 'realignment_manifest.json'), 'w'), indent=1)
