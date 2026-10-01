# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0018 metabolic vitals (answered episodes; ground truth computed; no LLM judge; within question type).
Pre-registered (2026-09-28, written before the power data were analyzed):
 P1 GPU power/energy features predict wrong answers within question type (AUROC 95% CI lower bound > 0.5);
 P2 metabolic features add beyond timing features (metabolic + timing > timing alone).'''
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from metab import load, episode_features
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
ALL = load('data/episodes_power.jsonl.gz'); R = [r for r in ALL if r['answered'] and len([x for x in (r.get('power') or []) if x[1] is not None]) >= 2]
y = np.array([0 if r['correct'] else 1 for r in R]); cats = np.array([r['cat'] for r in R]); F = [episode_features(r) for r in R]
def M(group):
    names = sorted(F[0][group]); X = np.nan_to_num(np.array([[f[group][n] for n in names] for f in F], float))
    for c in set(cats):
        m = cats == c; mu, sd = X[m].mean(0), X[m].std(0); X[m] = (X[m] - mu) / np.where(sd > 0, sd, 1)
    return X
def oof(X):
    k = min(5, int(y.sum()))
    return cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=3000)), X, y,
                             cv=StratifiedKFold(k, shuffle=True, random_state=0), method='predict_proba')[:, 1]
def ci(s):
    g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): b.append(roc_auc_score(y[i], s[i]))
    return [round(roc_auc_score(y, s), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
res = dict(n_recorded=len(ALL), n=len(y), failures=int(y.sum()), excluded_no_answer_or_no_power=len(ALL) - len(y))
if y.sum() < 8: res['warning'] = 'too few failures'; print(res); json.dump(res, open('docs/results.json', 'w'), indent=1); sys.exit(0)
Xm, Xt, Xs = M('metabolic'), M('timing'), M('substrate')
res['auroc_ci95'] = dict(metabolic=ci(oof(Xm)), timing=ci(oof(Xt)), substrate=ci(oof(Xs)), metabolic_plus_timing=ci(oof(np.hstack([Xm, Xt]))),
                         all_three=ci(oof(np.hstack([Xm, Xt, Xs]))))
a = res['auroc_ci95']; res['P1_metabolic_predicts'] = a['metabolic'][1] > 0.5; res['P2_metabolic_adds_beyond_timing'] = a['metabolic_plus_timing'][0] > a['timing'][0]
g = np.array([f['metabolic']['gpu_mean_W'] for f in F]); res['gpu_mean_W_correct_vs_wrong'] = [round(float(np.nanmean(g[y == 0])), 2), round(float(np.nanmean(g[y == 1])), 2)]
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
