# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0009: physiological coupling graph. Vital channels are nodes; lagged |correlation| over sliding windows are
edges; each window's graph is summarized by normalized-Laplacian topology. ctypes binding + numpy reference.'''
import ctypes, os
import numpy as np
_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcore.so'))
_P = ctypes.POINTER(ctypes.c_double)
_L.coupling_windows.argtypes = [_P, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, _P, ctypes.c_int]
METRICS = ['lambda2', 'spectral_entropy', 'total_coupling', 'lambda_max']

def windows(X, w=24, s=8, L=3):
    X = np.ascontiguousarray(X, float); T, k = X.shape; maxw = max(1, (T - w) // s + 1)
    out = np.zeros(maxw * 4); n = _L.coupling_windows(X.ctypes.data_as(_P), T, k, w, s, L, out.ctypes.data_as(_P), maxw)
    return out[: max(n, 0) * 4].reshape(-1, 4)

def windows_ref(X, w=24, s=8, L=3):
    T, k = X.shape; res = []
    def c(a, b):
        a, b = a - a.mean(), b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum()); return 0.0 if d < 1e-12 else float((a * b).sum() / d)
    for t0 in range(0, T - w + 1, s):
        Wm = np.zeros((k, k))
        for i in range(k):
            for j in range(i + 1, k):
                Wm[i, j] = Wm[j, i] = max(max(abs(c(X[t0:t0 + w - g, i], X[t0 + g:t0 + w, j])), abs(c(X[t0:t0 + w - g, j], X[t0 + g:t0 + w, i]))) for g in range(L + 1))
        d = Wm.sum(1); inv = np.where(d > 0, 1 / np.sqrt(np.where(d > 0, d, 1)), 0)
        ev = np.sort(np.linalg.eigvalsh(np.diag((d > 0).astype(float)) - inv[:, None] * Wm * inv[None, :]))
        pos = np.clip(ev, 0, None); p = pos / pos.sum() if pos.sum() > 0 else pos
        res.append([ev[1], -(p[p > 0] * np.log(p[p > 0])).sum(), Wm[np.triu_indices(k, 1)].sum(), ev[-1]])
    return np.array(res).reshape(-1, 4)

def channels(r, which='mixed'):
    e, p1, m, lat = (np.array(r[c][1:], float) for c in ('entropy', 'p_top1', 'margin', 'latency'))
    de, dl = np.abs(np.diff(e, prepend=e[0])), np.abs(np.diff(lat, prepend=lat[0]))
    return np.column_stack([e, p1, m, de] + ([lat, dl] if which == 'mixed' else []))

def episode_graph_features(r, which='mixed'):
    Wn = windows(channels(r, which)) if len(r['entropy']) > 30 else np.zeros((0, 4))
    f = {'n_windows': float(len(Wn))}
    for k, nm in enumerate(METRICS):
        col = Wn[:, k] if len(Wn) else np.zeros(1)
        f[nm + '_mean'], f[nm + '_min'], f[nm + '_max'], f[nm + '_std'] = col.mean(), col.min(), col.max(), col.std()
    tc = Wn[:, 2] if len(Wn) > 1 else np.zeros(2)
    f['graph_hrv_rmssd_total_coupling'] = float(np.sqrt(np.mean(np.diff(tc) ** 2)))
    return f
