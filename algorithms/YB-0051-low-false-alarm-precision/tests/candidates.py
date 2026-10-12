# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0051 candidate scores, frozen before the test data exist (docs/PREREGISTRATION.md).

REFERENCE R = data/explore_scores.npz: the YB-0050 test seeds 15-26 (now derivation), scored by the non-LLM monitors fitted on seeds
2-14, with self-consistency d (k = 4). Test seeds 27-38 are scored by the SAME monitors (fitted on seeds 2-14, tests/score_test.py), so
every test score lives on the same scale as the reference. Nothing here ever looks at a test label.

  pct(v; ref)   mid-rank percentile of v within the reference values ref (ties count half), non-finite = -inf (never monitored).
  C1(d, k)      d + (0.8 / k) * pct(stack): 0.2 for k = 4, 0.1 for k = 8, always below one level step 1/k, so the tie-break orders
                episodes inside a self-consistency level and never moves one across levels (no fitting)
  C2            L2 logistic regression (C = 1) on [d4, pct(stack), pct(probe), pct(text), pct(difficulty), monitored], fitted once on R
  C3            stack > 90th percentile of reference stack on correct episodes AND d >= 0.75   (binary rule, fixed operating point)
  C4            C2 mapped to its within-task-type mid-rank percentile among CORRECT reference episodes, plus 1e-3 * C2 (continuous
                tie-break so scores above every reference value stay ordered instead of tying at 1, the fault seen in exploration)
'''
import numpy as np
from sklearn.linear_model import LogisticRegression
FEATS = ('stack', 'probe', 'text', 'difficulty')
def neg(v): v = np.asarray(v, float); return np.where(np.isfinite(v), v, -np.inf)
def pct(v, ref):
    r = np.sort(neg(ref)); v = neg(v)
    return (np.searchsorted(r, v, 'left') + np.searchsorted(r, v, 'right')) / (2.0 * len(r))
def features(Z, R, d):
    '''Design matrix for C2: d, percentiles against the reference R, monitored flag (probe finite).'''
    return np.c_[np.asarray(d, float), np.column_stack([pct(Z[k], R[k]) for k in FEATS]), np.isfinite(np.asarray(Z['probe'], float)).astype(float)]
def c1(Z, R, d, k=4): return np.asarray(d, float) + (0.8 / k) * pct(Z['stack'], R['stack'])
def fit_c2(R): return LogisticRegression(C=1.0, max_iter=5000).fit(features(R, R, R['d']), np.asarray(R['y']))
def c2(model, Z, R, d): return model.predict_proba(features(Z, R, d))[:, 1]
def c4_reference(model, R):
    '''Per task type: sorted C2 scores of the CORRECT reference episodes; key None pools all correct episodes (unseen task types).'''
    s = c2(model, R, R, R['d']); y = np.asarray(R['y']); cat = np.asarray(R['cat'])
    ref = {c: np.sort(s[(cat == c) & (y == 0)]) for c in set(cat.tolist())}; ref[None] = np.sort(s[y == 0]); return ref
def c4(model, ref, Z, R, d):
    s = c2(model, Z, R, d); cat = np.asarray(Z['cat']); out = np.zeros(len(s))
    for c in set(cat.tolist()):
        m = cat == c; r = ref.get(c) if len(ref.get(c, [])) else ref[None]
        out[m] = (np.searchsorted(r, s[m], 'left') + np.searchsorted(r, s[m], 'right')) / (2.0 * len(r))
    return out + 1e-3 * s
def c3(Z, R, d):
    q = np.quantile(neg(R['stack'])[np.asarray(R['y']) == 0], 0.90)
    return (neg(Z['stack']) > q) & (np.asarray(d, float) >= 0.75)
def derivation_check(R, folds=5, seed=0):
    '''Pre-freeze check of C4 against C2 on the reference only (cross-fitted by episode): recall at 1% and 0.5% false alarms and the
    number of distinct values among the top 2% of scores (degeneracy check). Selection evidence, never a result.'''
    from sklearn.model_selection import StratifiedKFold
    y = np.asarray(R['y']); N = len(y); S2, S4 = np.zeros(N), np.zeros(N)
    for tr, te in StratifiedKFold(folds, shuffle=True, random_state=seed).split(np.zeros(N), y):
        Rt = {k: np.asarray(R[k])[tr] for k in R}; Re = {k: np.asarray(R[k])[te] for k in R}
        m = fit_c2(Rt); S2[te] = c2(m, Re, Rt, Re['d']); S4[te] = c4(m, c4_reference(m, Rt), Re, Rt, Re['d'])
    def rec(s, cap):
        k = int(np.floor(cap * (y == 0).sum() + 1e-9)); thr = np.sort(s[y == 0])[::-1][k]; return int((s[y == 1] > thr).sum())
    top = lambda s: int(len(np.unique(np.round(s[np.argsort(s)[::-1][:max(1, N // 50)]], 12))))
    return dict(episodes=N, wrong=int(y.sum()), C2=dict(caught_1pct=rec(S2, 0.01), caught_0p5pct=rec(S2, 0.005), distinct_top2pct=top(S2)),
                C4=dict(caught_1pct=rec(S4, 0.01), caught_0p5pct=rec(S4, 0.005), distinct_top2pct=top(S4)), top2pct_size=max(1, N // 50))
