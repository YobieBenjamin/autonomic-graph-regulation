# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0015: signal tiers for the contamination test. ctypes binding to libcore.so + pure-Python reference.
tier 0 (physical): per-token latency (prefill excluded), effort = tokens spent, wall time
tier 2 (substrate): entropy, top-1 probability, top1-top2 margin over the answer segment and the whole generation'''
import ctypes, gzip, json, os
import numpy as np
_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcore.so'))
_P = ctypes.POINTER(ctypes.c_double)
_L.series_features.argtypes = [_P, ctypes.c_int, _P]
NAMES = ['mean', 'std', 'rmssd', 'max', 'min', 'slope', 'spikes']

def features(x):
    x = np.ascontiguousarray(x, dtype=np.float64); out = np.zeros(7)
    if _L.series_features(x.ctypes.data_as(_P), len(x), out.ctypes.data_as(_P)): return np.full(7, np.nan)
    return out

def features_ref(x):
    x = np.asarray(x, float); n = len(x); m = x.mean(); sd = x.std(); t = np.arange(n) - (n - 1) / 2
    return np.array([m, sd, np.sqrt(np.mean(np.diff(x) ** 2)), x.max(), x.min(), (t * (x - m)).sum() / (t * t).sum(), np.mean(x > m + 2 * sd)])

def load(path):
    op = gzip.open if path.endswith('.gz') else open
    return [json.loads(l) for l in op(path, 'rt')]

def episode_features(r):
    '''Returns dict tier -> {name: value}. Answer segment = tokens after the final-channel marker (>= 2 tokens).'''
    fs = min(r['final_start'], len(r['entropy']) - 2)
    t2, t0 = {}, {}
    for ch in ('entropy', 'p_top1', 'margin'):
        whole, ans = features(r[ch]), features(r[ch][fs:])
        for k, nm in enumerate(NAMES):
            t2[ch + '_all_' + nm] = whole[k]; t2[ch + '_ans_' + nm] = ans[k]
    lat = features(r['latency'][1:])
    for k, nm in enumerate(NAMES): t0['latency_' + nm] = lat[k]
    t0['effort_tokens'] = float(r['n_tokens']); t0['wall'] = float(r['wall']); t0['reasoning_tokens'] = float(r['final_start'])
    return {'tier0_physical': t0, 'tier2_substrate': t2}
