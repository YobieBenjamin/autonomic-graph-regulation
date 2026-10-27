# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0033: real-time-knowable checkpoints. Observations exist at absolute token counts t in T while the episode is
still reasoning (t < answer start). Nothing derived from the total reasoning length is used.'''
import numpy as np
import multiprocessing as mp
from deep import deep_features
from aiews import AIEWS, vitals_v2
T = (48, 96, 192, 384)
_G = {}

def checkpoints(r): return [t for t in T if t < r['final_start']]

def abs_features(r, L, t): return np.append(deep_features(L, r['final_start'], upto=t, prepped=True), np.log(t))

def _work(i):
    r, t = _G['jobs'][i]; return abs_features(r, _G['L'][r['idx']], t)

def parallel_features(jobs, L, procs=4):
    _G['jobs'], _G['L'] = jobs, L
    with mp.get_context('fork').Pool(procs) as p: return np.array(p.map(_work, range(len(jobs)), chunksize=64))

class AbsOrganism:
    def fit_from(self, X, jobs):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        y = np.array([0 if r['correct'] else 1 for r, _ in jobs]); key = [(r['cat'], t) for r, t in jobs]; self.stats = {}
        for k in set(key):
            m = np.array([q == k for q in key]); self.stats[k] = (X[m].mean(0), X[m].std(0))
        self.clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(self._z(X, key), y); return self
    def _z(self, X, key):
        Z = X.copy()
        for i, k in enumerate(key):
            mu, sd = self.stats.get(k, (0, 1)); Z[i] = (X[i] - mu) / np.where(np.asarray(sd) > 0, sd, 1)
        return Z
    def score(self, r, L, t):
        return float(self.clf.predict_proba(self._z(abs_features(r, L, t)[None, :], [(r['cat'], t)]))[0, 1])

class AbsAIEWS:
    '''Bands per checkpoint t from derivation correct episodes still reasoning at t; directions at the largest t with >= 20 failures.'''
    def fit(self, R, L, cal):
        self.cal = cal; V, Y = {}, {}
        for t in T:
            Rt = [r for r in R if t < r['final_start']]
            V[t] = np.array([vitals_v2(r, L[r['idx']], upto=t, hpa_cal=cal) for r in Rt]); Y[t] = np.array([0 if r['correct'] else 1 for r in Rt])
        tdir = max([t for t in T if Y[t].sum() >= 20] or [T[0]]); ref = AIEWS().fit(V[tdir], Y[tdir]); self.tdir = tdir; self.by_t = {}
        for t in T:
            a = AIEWS().fit(V[t], Y[t]); a.direction = ref.direction; ok = V[t][Y[t] == 0]; q = lambda j, p: np.nanpercentile(ok[:, j], p)
            a.bands = np.array([[q(j, 90), q(j, 95), q(j, 99)] if ref.direction[j] > 0 else [q(j, 10), q(j, 5), q(j, 1)] for j in range(ok.shape[1])])
            self.by_t[t] = a
        return self
    def score(self, r, L, t): return self.by_t[t].score(vitals_v2(r, L, upto=t, hpa_cal=self.cal))

class LengthControls:
    '''C1 = t (still reasoning at t); C2 = derivation percentile of t among episodes of the same question type.'''
    def fit(self, R):
        self.lens = {c: np.sort([r['final_start'] for r in R if r['cat'] == c]) for c in set(r['cat'] for r in R)}; return self
    def c1(self, r, t): return float(t)
    def c2(self, r, t):
        a = self.lens.get(r['cat']); return float(np.searchsorted(a, t, side='right') / len(a)) if a is not None and len(a) else 0.0
