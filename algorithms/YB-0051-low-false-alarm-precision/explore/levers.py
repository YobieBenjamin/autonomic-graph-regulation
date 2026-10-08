# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0051 EXPLORATORY lever comparison at low false-alarm rates (not confirmatory; the data are the YB-0050 test seeds, now derivation).
Candidates that learn anything from labels are cross-fitted (5 folds by episode), so no episode is scored by a rule fitted on it.
Writes docs/explore.json. Every number here is a hypothesis generator for the YB-0051 pre-registration, never a result.'''
import json, sys, numpy as np
sys.path.insert(0, 'src')
from decider import single, bootstrap, burden_table
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve
Z = np.load('data/explore_scores.npz', allow_pickle=True); y = Z['y']; d = Z['d']; cat = Z['cat']; N = len(y)
fin = lambda v: np.where(np.isfinite(v), v, np.nanmin(np.where(np.isfinite(v), v, np.nan)) - 1.0)
def rank01(v): v = fin(v); return (np.argsort(np.argsort(v, kind='stable'), kind='stable') + 0.5) / len(v)
S = {k: Z[k] for k in ('probe', 'text', 'stack', 'banded', 'difficulty')}; S['self_consistency'] = d
# 1. self-consistency with a continuous tie-break inside each disagreement level (no fitting)
S['sc_tiebreak_probe'] = d + 0.2 * rank01(Z['probe']); S['sc_tiebreak_stack'] = d + 0.2 * rank01(Z['stack'])
# 2. rank average of self-consistency and the stack (no fitting)
S['rank_mean_sc_stack'] = rank01(d + 1e-6 * rank01(Z['stack'])) + rank01(Z['stack'])
# 3. cross-fitted logistic combination of self-consistency and the non-LLM components
X = np.c_[d, rank01(Z['stack']), rank01(Z['probe']), rank01(Z['text']), rank01(Z['difficulty']), np.isfinite(Z['probe']).astype(float)]
def crossfit(X, w=None):
    out = np.zeros(N)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y):
        m = LogisticRegression(C=1.0, max_iter=5000, class_weight=w).fit(X[tr], y[tr]); out[te] = m.predict_proba(X[te])[:, 1]
    return out
S['logit_sc_plus_nonllm'] = crossfit(X)
S['logit_nonllm_only'] = crossfit(X[:, 1:])
# 4. per-task calibration: each score mapped to its within-task-type percentile among CORRECT episodes of the training folds
def per_task(v):
    v = fin(v); out = np.zeros(N)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=1).split(v[:, None], y):
        for c in set(cat):
            ref = np.sort(v[tr][(cat[tr] == c) & (y[tr] == 0)]); m = te[cat[te] == c]
            out[m] = np.searchsorted(ref, v[m], side='right') / max(1, len(ref)) if len(ref) else 0.5
    return out + 1e-9 * v
S['probe_per_task'] = per_task(Z['probe']); S['stack_per_task'] = per_task(Z['stack'])
S['sc_tb_stack_per_task'] = per_task(S['sc_tiebreak_stack'])
# 5. conjunction (both must fire): a high-precision rule, shown as a grid because its two thresholds are tuned here
conj = {}
for qs in (0.80, 0.90, 0.95):
    for dl in (0.25, 0.5, 0.75, 1.0):
        a = (fin(Z['stack']) > np.quantile(fin(Z['stack'])[y == 0], qs)) & (d >= dl)
        conj['stack_q%.2f_and_d>=%.2f' % (qs, dl)] = dict(recall=round(float(a[y == 1].mean()), 4), fpr=round(float(a[y == 0].mean()), 4), caught=int(a[y == 1].sum()))
def pauc(v, cap=0.01):
    f, t, _ = roc_curve(y, fin(v)); m = f <= cap; f2 = np.r_[f[m], cap]; t2 = np.r_[t[m], np.interp(cap, f, t)]
    return round(float(np.trapezoid(t2, f2) / cap), 4)
rules = {k: single(fin(v)) for k, v in S.items()}
pt, bs = bootstrap(rules, y, caps=(0.10, 0.02, 0.01, 0.005), n=1000)
res = dict(note='EXPLORATORY: YB-0050 test seeds 15-26 reused as derivation data; selection only, not evidence', episodes=N, wrong=int(y.sum()),
           correct=int((y == 0).sum()), table={k: {('fa_%g' % c): dict(caught=int(round(pt[(k, c)][0] * y.sum())), recall=round(pt[(k, c)][0], 4), fpr=round(pt[(k, c)][1], 4)) for c in (0.10, 0.02, 0.01, 0.005)} for k in S},
           partial_auroc_to_1pct={k: pauc(v) for k, v in S.items()},
           burden_at_1pct_fa={k: burden_table(pt, bs, k, 0.01)['p=0.01'] for k in S}, recall_ci_at_1pct={k: burden_table(pt, bs, k, 0.01)['recall'] for k in S},
           conjunction_grid=conj)
json.dump(res, open('docs/explore.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
for k in S: print('%-24s 1%%: %3d (%.3f)  0.5%%: %3d  2%%: %3d  10%%: %3d  pAUC1%%: %.3f' % (k, res['table'][k]['fa_0.01']['caught'], res['table'][k]['fa_0.01']['recall'], res['table'][k]['fa_0.005']['caught'], res['table'][k]['fa_0.02']['caught'], res['table'][k]['fa_0.1']['caught'], res['partial_auroc_to_1pct'][k]))
