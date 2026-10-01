# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0009 experiment (answered episodes; ground truth computed; no LLM judge).
Pre-registered (2026-09-28, before data): coupling-graph topology predicts wrong answers (AUROC 95% CI lower bound
> 0.5) and adds information beyond raw per-channel statistics (combined > raw). Within-category normalization
controls for question type.'''
import gzip, json, os, sys, numpy as np
sys.path.insert(0, 'src')
from graph import episode_graph_features, channels
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
R = [r for r in (json.loads(l) for l in gzip.open('data/episodes.jsonl.gz', 'rt')) if r['answered']]
y = np.array([0 if r['correct'] else 1 for r in R]); cats = np.array([r['cat'] for r in R])
def within(X):
    X = np.nan_to_num(np.array(X, float))
    for c in set(cats):
        m = cats == c; mu, sd = X[m].mean(0), X[m].std(0); X[m] = (X[m] - mu) / np.where(sd > 0, sd, 1)
    return X
def oof(X):
    clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=3000))
    return cross_val_predict(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method='predict_proba')[:, 1]
def ci(s):
    g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): b.append(roc_auc_score(y[i], s[i]))
    return [round(roc_auc_score(y, s), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
def feats(which):
    F = [episode_graph_features(r, which) for r in R]; names = sorted(F[0]); return within([[f[n] for n in names] for f in F])
raw = within([np.r_[channels(r).mean(0), channels(r).std(0)] for r in R])
G_mixed, G_sub = feats('mixed'), feats('substrate')
res = dict(n=len(y), failures=int(y.sum()), auroc_ci95=dict(
    graph_mixed_nodes=ci(oof(G_mixed)), graph_substrate_nodes=ci(oof(G_sub)), raw_channel_stats=ci(oof(raw)),
    raw_plus_graph=ci(oof(np.hstack([raw, G_mixed])))))
a = res['auroc_ci95']
res['prediction_graph_predicts'] = a['graph_mixed_nodes'][1] > 0.5
res['prediction_graph_adds_beyond_raw'] = a['raw_plus_graph'][0] > a['raw_channel_stats'][0]
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
