# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0012: the organism (O) is text-blind: reasoning-phase substrate vitals only, trained on seed 0, frozen.'''
import gzip, json, numpy as np
from agr import features, NAMES
from hpa import simulate
CH = ('entropy', 'p_top1', 'margin')

def load(p):
    op = gzip.open if p.endswith('.gz') else open
    return [json.loads(l) for l in op(p, 'rt')]

def reasoning_features(r, upto=None):
    end = r['final_start'] if upto is None else min(upto, r['final_start'])
    end = max(end, 2); v = []
    for ch in CH: v.extend(features(np.array(r[ch][:end], float)))
    return np.nan_to_num(np.array(v))

class Organism:
    def fit(self, R0):
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold, cross_val_predict
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        X = np.array([reasoning_features(r) for r in R0]); y = np.array([0 if r['correct'] else 1 for r in R0]); c = [r['cat'] for r in R0]
        self.stats = {k: (X[[i for i, cc in enumerate(c) if cc == k]].mean(0), X[[i for i, cc in enumerate(c) if cc == k]].std(0)) for k in set(c)}
        Z = self.z(X, c)
        self.clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=3000)).fit(Z, y)
        oof = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=3000)), Z, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method='predict_proba')[:, 1]
        self.threshold = float(np.quantile(oof[y == 0], 0.90))            # 10% FPR on seed-0 correct episodes, out-of-fold
        return self
    def z(self, X, cats):
        Z = X.copy()
        for i, k in enumerate(cats):
            mu, sd = self.stats[k]; Z[i] = (X[i] - mu) / np.where(sd > 0, sd, 1)
        return Z
    def score(self, r, upto=None):
        return float(self.clf.predict_proba(self.z(reasoning_features(r, upto)[None, :], [r['cat']]))[0, 1])

class HPAOrganism:
    def fit(self, R0):
        v = np.concatenate([np.array(r['entropy'][:r['final_start']]) for r in R0 if r['correct'] and r['final_start'] > 1])
        self.mu, self.sd = np.median(v), (np.percentile(v, 75) - np.percentile(v, 25)) or 1.0; return self
    def score(self, r):
        e = np.array(r['entropy'][:max(r['final_start'], 2)], float); return float(simulate(np.maximum((e - self.mu) / self.sd, 0))[2].max())

def auroc(y, s):
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(y, s)

def paired_diff(y, a, b, n=1000, seed=0):
    '''Paired bootstrap of AUROC(a) - AUROC(b) on the same resampled episodes: [diff, lo95, hi95].'''
    g = np.random.default_rng(seed); d = []
    for _ in range(n):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): d.append(auroc(y[i], a[i]) - auroc(y[i], b[i]))
    return [round(float(auroc(y, a) - auroc(y, b)), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]
