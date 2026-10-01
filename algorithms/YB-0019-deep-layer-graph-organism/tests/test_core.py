# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from deep import graph_windows, deep_features
r = np.random.default_rng(0)
def ref_windows(X, w=24, s=8, L=3):
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
        pos = np.clip(ev, 0, None); p = pos / pos.sum()
        B = Wm - np.outer(d, d) / d.sum(); lam, V = np.linalg.eigh(B); v = V[:, -1]
        if lam[-1] > 1e-12:
            sg = np.where(v >= 0, 1.0, -1.0); Q = sg @ B @ sg / (2 * d.sum()); sm = min((sg > 0).sum(), (sg < 0).sum())
        else: Q, sm = 0.0, 0
        res.append([ev[1], -(p[p > 0] * np.log(p[p > 0])).sum(), Wm[np.triu_indices(k, 1)].sum(), ev[-1], Q, sm])
    return np.array(res)
def t_c_equals_reference_24_nodes():
    X = r.normal(size=(96, 24)); assert np.allclose(graph_windows(X), ref_windows(X), atol=1e-7)
def t_two_modules_modularity_half():
    # exactly uncorrelated module signals (sin/cos over whole periods), so cross-module coupling is ~0 and Q -> 1/2
    t = np.arange(200); a, b = np.sin(2 * np.pi * 3 * t / 200), np.cos(2 * np.pi * 5 * t / 200)
    X = np.column_stack([a + 1e-6 * r.normal(size=200) for _ in range(6)] + [b + 1e-6 * r.normal(size=200) for _ in range(6)])
    G = graph_windows(X, w=200, s=200, L=0); assert abs(G[0, 4] - 0.5) < 0.02 and G[0, 5] == 6, G
def t_single_module_no_split():
    a = r.normal(size=200); X = np.column_stack([a + 1e-3 * r.normal(size=200) for _ in range(8)])
    assert abs(graph_windows(X, w=200, s=200, L=0)[0, 4]) < 0.02
def t_blind_to_answer_tokens():
    Lr = np.abs(r.normal(size=(120, 24, 5))) + 1; L2 = Lr.copy(); L2[80:] = 99.0
    assert np.allclose(deep_features(Lr, 80), deep_features(L2, 80))
def t_prefix_consistency():
    Lr = np.abs(r.normal(size=(120, 24, 5))) + 1; assert np.allclose(deep_features(Lr, 80, upto=80), deep_features(Lr, 80)) and np.allclose(deep_features(Lr, 80, upto=500), deep_features(Lr, 80))
T = [t_c_equals_reference_24_nodes, t_two_modules_modularity_half, t_single_module_no_split, t_blind_to_answer_tokens, t_prefix_consistency]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
