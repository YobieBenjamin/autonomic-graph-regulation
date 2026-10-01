#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Pack layer telemetry for YB-0019: reasoning segment only (the organism may not see answer tokens), norm channels
log1p-scaled (same transform as deep.prep), float16, one compressed npz per seed. Keys: i<idx>.'''
import json, os, sys, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seed, out = sys.argv[1], sys.argv[2]
R = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'agr', 'episodes_L_seed' + seed + '.jsonl'))]
arrs = {}
for r in R:
    f = os.path.join(ROOT, 'data', 'agr', 'layers_seed' + seed, str(r['idx']) + '.npy')
    if not os.path.exists(f): continue
    X = np.load(f).astype(float)[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0))
    arrs['i' + str(r['idx'])] = X.astype(np.float16)
np.savez_compressed(out, **arrs); print('packed', len(arrs), 'episodes ->', out, round(os.path.getsize(out) / 1e6, 1), 'MB')
