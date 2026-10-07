# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0042 probe baseline: a standard linear probe on raw hidden states, the text-blind competitor from prior work.
Input at checkpoint t (only tokens before t): at one layer, the hidden state of the last token before t and the mean
hidden state over tokens before t (2 x d_model), plus log t. Same extra inputs and normalization as the regulator:
features are z-scored per (question type, t) with derivation statistics. Model: L2-regularised logistic regression.
Layer and C are chosen by 5-fold cross-validation grouped by episode, on derivation data only.'''
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
LAYERS = (6, 12, 18, 23)
C_GRID = (0.001, 0.01, 0.1)

def feat(H, idx, t, layer):
    '''H: dict idx -> dict of arrays (last_t, mean_t), each (len(LAYERS), d). layer: an element of LAYERS or 'all'.'''
    d = H[idx]; last, mean = d['last_%d' % t].astype(np.float32), d['mean_%d' % t].astype(np.float32)
    if layer == 'all': v = np.concatenate([last.ravel(), mean.ravel()])
    else: k = LAYERS.index(layer); v = np.concatenate([last[k], mean[k]])
    return np.append(v, np.log(t))

class Probe:
    def __init__(self, layer, C): self.layer, self.C = layer, C
    def _design(self, jobs, H):
        return np.stack([feat(H, r['idx'], t, self.layer) for r, t in jobs])
    def _z(self, X, keys, fit):
        if fit:
            self.stats = {}
            for k in set(keys):
                m = np.array([kk == k for kk in keys]); mu = X[m].mean(0); sd = X[m].std(0) + 1e-6; self.stats[k] = (mu, sd)
        out = np.empty_like(X)
        for i, k in enumerate(keys):
            mu, sd = self.stats.get(k, (0.0, 1.0)); out[i] = (X[i] - mu) / sd
        return out
    def fit(self, jobs, H):
        X = self._design(jobs, H); keys = [(r['cat'], t) for r, t in jobs]; y = np.array([0 if r['correct'] else 1 for r, _ in jobs])
        self.clf = LogisticRegression(C=self.C, max_iter=3000).fit(self._z(X, keys, True), y); return self
    def score(self, r, t, H):
        x = feat(H, r['idx'], t, self.layer)[None]; return float(self.clf.predict_proba(self._z(x, [(r['cat'], t)], False))[0, 1])

def cv_auroc(jobs, H, layer, C, folds=5):
    '''Grouped (by episode) cross-validated AUROC on derivation observations; normalization re-fitted inside each fold.'''
    y = np.array([0 if r['correct'] else 1 for r, _ in jobs]); g = np.array([r['idx'] for r, _ in jobs]); pred = np.zeros(len(jobs))
    for tr, te in GroupKFold(folds).split(np.zeros(len(jobs)), y, g):
        P = Probe(layer, C).fit([jobs[i] for i in tr], H)
        pred[te] = [P.score(jobs[i][0], jobs[i][1], H) for i in te]
    return float(roc_auc_score(y, pred)), pred

def select(jobs, H, layers=LAYERS, grid=C_GRID):
    '''Pre-registered selection: the (layer, C) with the highest grouped-CV AUROC on derivation data. Ties: earlier layer, smaller C.'''
    table = {}
    for L in layers:
        for C in grid: table[(L, C)] = cv_auroc(jobs, H, L, C)[0]
    best = max(table, key=lambda k: (table[k], -list(layers).index(k[0]) if k[0] in layers else 0, -k[1]))
    return best, {'%s|%s' % k: round(v, 4) for k, v in table.items()}
