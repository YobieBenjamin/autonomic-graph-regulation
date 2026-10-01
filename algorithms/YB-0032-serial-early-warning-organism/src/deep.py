# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0019: deep layer-graph organism (text-blind). Input per episode: layer tensor (T, 24, 5) over the reasoning
segment; channels: 0 attention-update norm, 1 expert-update norm, 2 residual norm, 3 cos(in, out), 4 router entropy.'''
import ctypes, os
import numpy as np
_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcore.so'))
_P = ctypes.POINTER(ctypes.c_double)
_L.layer_graph_windows.argtypes = [_P, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, _P, ctypes.c_int]
W, S, LAG = 24, 8, 3
METRICS = ['lambda2', 'spectral_entropy', 'total_coupling', 'lambda_max', 'modularity', 'small_community']

def graph_windows(X, w=W, s=S, L=LAG):
    X = np.ascontiguousarray(X, float); T, k = X.shape; maxw = max(1, (T - w) // s + 1); out = np.zeros(maxw * 6)
    n = _L.layer_graph_windows(X.ctypes.data_as(_P), T, k, w, s, L, out.ctypes.data_as(_P), maxw)
    return out[: max(n, 0) * 6].reshape(-1, 6)

def prep(layers):
    '''log-scale the norm channels (they span orders of magnitude); keep cos and entropy as is.'''
    X = np.array(layers, float); X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); return X

def _trend(v):
    '''least-squares slope over window index and the value extrapolated one window past the last.'''
    if len(v) < 2: return 0.0, (float(v[-1]) if len(v) else 0.0)
    t = np.arange(len(v)); a, b = np.polyfit(t, v, 1); return float(a), float(a * len(v) + b)

def deep_features(layers, final_start, upto=None, prepped=False):
    end = final_start if upto is None else min(upto, final_start)
    X = np.array(layers[:max(end, 2)], float) if prepped else prep(layers[:max(end, 2)]); f = []
    for c in range(5):                                   # (a) per-layer mean and RMSSD (layer HRV): 24 x 5 x 2
        x = X[:, :, c]; f.extend(x.mean(0)); f.extend(np.sqrt(np.mean(np.diff(x, axis=0) ** 2, axis=0)) if len(x) > 1 else np.zeros(24))
    for c in (1, 4):                                     # (b) layer graphs: expert-update (A) and router-entropy (B)
        G = graph_windows(X[:, :, c]) if len(X) >= W else np.zeros((0, 6))
        for m in range(6):
            v = G[:, m] if len(G) else np.zeros(1)
            sl, ex = _trend(v); f.extend([v.mean(), v.min(), v.max(), v.std(), sl, ex])
        tc = G[:, 2] if len(G) > 1 else np.zeros(2); f.append(float(np.sqrt(np.mean(np.diff(tc) ** 2))))
    return np.nan_to_num(np.array(f, float))

class DeepOrganism:
    prepped = True   # experiment data are stored already log-scaled (see agr packing)
    def fit(self, R0, L0):
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold, cross_val_predict
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        X = np.array([deep_features(L0[r['idx']], r['final_start'], prepped=self.prepped) for r in R0]); y = np.array([0 if r['correct'] else 1 for r in R0])
        cats = [r['cat'] for r in R0]
        self.stats = {k: (X[[i for i, c in enumerate(cats) if c == k]].mean(0), X[[i for i, c in enumerate(cats) if c == k]].std(0)) for k in set(cats)}
        Z = self.z(X, cats); mk = lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000))
        self.clf = mk().fit(Z, y)
        oof = cross_val_predict(mk(), Z, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method='predict_proba')[:, 1]
        self.threshold = float(np.quantile(oof[y == 0], 0.90)); return self
    def z(self, X, cats):
        Z = X.copy()
        for i, k in enumerate(cats):
            mu, sd = self.stats[k]; Z[i] = (X[i] - mu) / np.where(sd > 0, sd, 1)
        return Z
    def score(self, layers, r, upto=None):
        return float(self.clf.predict_proba(self.z(deep_features(layers, r['final_start'], upto, prepped=self.prepped)[None, :], [r['cat']]))[0, 1])
    def alarm(self, layers, r):
        '''Online action: first checkpoint (every 8 tokens from 24) where the score, or its linear extrapolation one
        checkpoint ahead, exceeds the frozen threshold. Returns the token index or None.'''
        prev = None
        for t in range(W, r['final_start'] + 1, S):
            s = self.score(layers, r, upto=t); nxt = s + (s - prev) if prev is not None else s
            if max(s, nxt) > self.threshold: return t
            prev = s
        return None
