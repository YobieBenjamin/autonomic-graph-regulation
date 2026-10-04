# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0032: serial-observation early warning (NEWS2 method). Observations at stages c in {0.25, 0.5, 0.75, 1.0} of the
reasoning; normalization and bands are stage-specific; one frozen model across stages. Text-blind, no look-ahead.'''
import numpy as np
import multiprocessing as mp
from deep import deep_features
from aiews import AIEWS, vitals_v2
STAGES = (0.25, 0.5, 0.75, 1.0)
_G = {}

def stage_k(r, c): return max(int(c * r['final_start']), 2)

def serial_features(r, L, c):
    return np.append(deep_features(L, r['final_start'], upto=stage_k(r, c), prepped=True), c)

def _work(i):
    r, c = _G['jobs'][i]; return serial_features(r, _G['L'][r['idx']], c)

def parallel_features(jobs, L, procs=4):
    '''Fork-based pool: workers inherit the layer dict without pickling it.'''
    _G['jobs'], _G['L'] = jobs, L
    with mp.get_context('fork').Pool(procs) as p: return np.array(p.map(_work, range(len(jobs)), chunksize=64))

class SerialOrganism:
    def fit(self, R, L, procs=4):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        jobs = [(r, c) for r in R for c in STAGES]; return self.fit_from(parallel_features(jobs, L, procs), jobs)
    def fit_from(self, X, jobs):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        y = np.array([0 if r['correct'] else 1 for r, _ in jobs]); key = [(r['cat'], c) for r, c in jobs]
        self.stats = {}
        for k in set(key):
            m = np.array([q == k for q in key]); self.stats[k] = (X[m].mean(0), X[m].std(0))
        self.clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(self._z(X, key), y); return self
    def _z(self, X, key):
        Z = X.copy()
        for i, k in enumerate(key):
            mu, sd = self.stats[k]; Z[i] = (X[i] - mu) / np.where(sd > 0, sd, 1)
        return Z
    def score(self, r, L, c):
        x = serial_features(r, L, c)[None, :]; return float(self.clf.predict_proba(self._z(x, [(r['cat'], c)]))[0, 1])

class SerialAIEWS:
    '''Per-stage bands (from correct derivation episodes at that stage); directions learned at stage 1.0.'''
    def fit(self, R, L, cal):
        y = np.array([0 if r['correct'] else 1 for r in R]); self.cal = cal; self.by_stage = {}
        V = {c: np.array([vitals_v2(r, L[r['idx']], upto=stage_k(r, c), hpa_cal=cal) for r in R]) for c in STAGES}
        ref = AIEWS().fit(V[1.0], y)
        for c in STAGES:
            a = AIEWS().fit(V[c], y); a.direction = ref.direction; ok = V[c][y == 0]; q = lambda j, p: np.nanpercentile(ok[:, j], p)
            a.bands = np.array([[q(j, 90), q(j, 95), q(j, 99)] if ref.direction[j] > 0 else [q(j, 10), q(j, 5), q(j, 1)] for j in range(ok.shape[1])])
            self.by_stage[c] = a
        return self
    def score(self, r, L, c):
        return self.by_stage[c].score(vitals_v2(r, L, upto=stage_k(r, c), hpa_cal=self.cal))
