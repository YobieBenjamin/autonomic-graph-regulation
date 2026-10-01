# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0015 contamination test. Pre-registered (2026-09-28, before data were seen):
 P1 a meaningful share of errors is delivered confidently, and the substrate tier misses them at 10% FPR;
 P2 the physical tier catches a meaningful share of the errors the substrate tier misses.
Ground truth is computed (no LLM judge). Primary analysis: answered episodes, failure = wrong answer. Episodes that hit the token cap without answering are excluded and counted separately (they would trivially favor the effort signal).'''
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from agr import load, episode_features
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
ALL = load('data/episodes.jsonl.gz'); R = [r for r in ALL if r['answered']]   # primary: answered episodes only (cap-hit NO-ANSWER would trivially favor effort)
y = np.array([0 if r['correct'] else 1 for r in R]); cats = np.array([r['cat'] for r in R])
F = [episode_features(r) for r in R]; tiers = list(F[0])
def matrix(tier, within):
    names = sorted(F[0][tier]); X = np.array([[f[tier][n] for n in names] for f in F], float)
    X = np.nan_to_num(X, nan=0.0)
    if within:
        for c in set(cats):
            m = cats == c; mu, sd = X[m].mean(0), X[m].std(0); X[m] = (X[m] - mu) / np.where(sd > 0, sd, 1)
    return X
def oof(X):
    k = min(5, int(min(y.sum(), (1 - y).sum())))
    clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000))
    return cross_val_predict(clf, X, y, cv=StratifiedKFold(k, shuffle=True, random_state=0), method='predict_proba')[:, 1]
def auc_ci(s):
    r = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = r.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): b.append(roc_auc_score(y[i], s[i]))
    return [round(roc_auc_score(y, s), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
def recall_at_fpr(s, fpr=0.10):
    thr = np.quantile(s[y == 0], 1 - fpr); return s > thr
res = dict(scope='answered episodes only; failure = wrong answer', no_answer_excluded=len(ALL) - len(R), n=len(y), failures=int(y.sum()), by_category={c: [int(y[cats == c].sum()), int((cats == c).sum())] for c in sorted(set(cats))})
if y.sum() < 10 or (1 - y).sum() < 10:
    res['warning'] = 'too few failures or successes for a reliable test'; print(res); json.dump(res, open('docs/results.json', 'w'), indent=1); sys.exit(0)
scores = {}
for within in (False, True):
    tag = 'within_category' if within else 'raw'; res[tag] = {}
    for t in tiers + ['combined']:
        X = np.hstack([matrix(tt, within) for tt in tiers]) if t == 'combined' else matrix(t, within)
        s = oof(X); scores[(tag, t)] = s; res[tag][t] = dict(auroc_ci95=auc_ci(s))
# gospel regime: errors whose answer tokens were all delivered with p_top1 >= 0.9
conf = np.array([min(r['p_top1'][min(r['final_start'], len(r['p_top1']) - 1):] or [0]) >= 0.9 for r in R])
res['gospel'] = dict(errors=int(y.sum()), confident_errors=int((conf & (y == 1)).sum()), share_confident=round(float((conf & (y == 1)).sum() / y.sum()), 4))
for tag in ('raw', 'within_category'):
    sub, phy = recall_at_fpr(scores[(tag, 'tier2_substrate')]), recall_at_fpr(scores[(tag, 'tier0_physical')])
    missed = (y == 1) & ~sub
    res['gospel'][tag] = dict(substrate_recall_at_10fpr=round(float(sub[y == 1].mean()), 4), substrate_missed_errors=int(missed.sum()),
        physical_recall_at_10fpr=round(float(phy[y == 1].mean()), 4),
        physical_catches_of_substrate_misses=[int((phy & missed).sum()), int(missed.sum())],
        substrate_recall_on_confident_errors=round(float(sub[conf & (y == 1)].mean()), 4) if (conf & (y == 1)).any() else None,
        physical_recall_on_confident_errors=round(float(phy[conf & (y == 1)].mean()), 4) if (conf & (y == 1)).any() else None)
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1)
np.save('docs/oof_scores.npy', np.array([scores[('within_category', t)] for t in tiers + ['combined']]))
print(json.dumps(res, indent=1))
