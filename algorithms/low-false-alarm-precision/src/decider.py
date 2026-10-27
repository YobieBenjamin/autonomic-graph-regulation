# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0050: alarm rules, one paired bootstrap for every comparison, and the scaling arithmetic (cost share, false-alarm burden).
A RULE is a function rule(i, y, cap) -> boolean alarm mask over the episodes i (an index array, with repeats in a bootstrap
resample). Every threshold inside a rule is set only from the correct episodes of that resample (y == 0), so thresholds are
re-set in every resample (PROTOCOL rule 5). Never-monitored episodes carry score -inf and are never alarmed by an in-time rule.'''
import numpy as np
from layered import tight, D_GRID
NEG = -1e18
def fin(v): return np.where(np.isfinite(v), v, NEG)
def threshold(v0, cap):
    '''Same value as corrected.cap_threshold (smallest candidate threshold with mean(v0 > thr) <= cap; candidates are -inf and the
    unique finite values of v0), computed by sorting instead of scanning. Proved equal in tests/test_decider.py.'''
    v = np.asarray(v0, float); n = len(v); k = int(np.floor((cap + 1e-12) * n))
    if k >= n: return -np.inf
    s = np.sort(v)[::-1]; thr = s[k]
    return float(thr) if np.isfinite(thr) else -np.inf
def single(v):
    '''One monitor alone: alarm if its in-time score exceeds the cap threshold.'''
    v = np.asarray(v, float)
    def rule(i, y, cap):
        s = v[i]; return s > threshold(s[y == 0], cap)
    return rule
def layered(v1, d, gate=None, share1=0.5):
    '''YB-0049 rule, generalised: stage 1 (in-time score v1) gets share1 of the cap (5% of 10%); stage 2 alarms if d >= delta, with
    delta the smallest value in D_GRID whose union false-alarm rate is <= cap (stage 2 off if none). gate (optional, boolean): stage 2
    is consulted only where gate is True (the gated, cheaper variant).'''
    v1 = fin(np.asarray(v1, float)); d = np.asarray(d, float); g = np.ones(len(d), bool) if gate is None else np.asarray(gate, bool)
    def rule(i, y, cap):
        c = y == 0; s1 = v1[i] > tight(v1[i][c], cap * share1); di, gi = d[i], g[i]
        for dl in D_GRID:
            a = s1 | (gi & (di >= dl))
            if a[c].mean() <= cap + 1e-12: return a
        return s1
    return rule
def rates(a, y):
    return float(a[y == 1].mean()), float(a[y == 0].mean())
def burden(tpr, fpr, p):
    '''Error base rate p: precision (PPV) and alarms per million actions.'''
    hit, fa = tpr * p, fpr * (1 - p)
    return (hit / (hit + fa) if hit + fa > 0 else float('nan')), 1e6 * (hit + fa)
def ci(x):
    '''95% percentile interval over finite resample values; [None, None] when none is finite (e.g. no alarms in any resample).'''
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [round(float(np.percentile(x, 2.5)), 4), round(float(np.percentile(x, 97.5)), 4)] if len(x) else [None, None]
def bootstrap(rules, y, caps=(0.10, 0.01), n=2000, seed=0, base_rates=(0.10, 0.01, 0.001)):
    '''One paired bootstrap over episodes for all rules and caps. Returns point values and per-resample TPR/FPR arrays.'''
    y = np.asarray(y); N = len(y); full = np.arange(N); g = np.random.default_rng(seed)
    pt = {(m, c): rates(r(full, y, c), y) for m, r in rules.items() for c in caps}
    bs = {k: [] for k in pt}
    for _ in range(n):
        i = g.integers(0, N, N); yi = y[i]
        if yi.sum() == 0 or yi.sum() == N: continue
        for m, r in rules.items():
            for c in caps: bs[(m, c)].append(rates(r(i, yi, c), yi))
    bs = {k: np.array(v) for k, v in bs.items()}
    return pt, bs
def diff(pt, bs, a, b, cap=0.10):
    '''Paired difference in recall (TPR), point estimate and 95% percentile interval.'''
    x = bs[(a, cap)][:, 0] - bs[(b, cap)][:, 0]
    return [round(pt[(a, cap)][0] - pt[(b, cap)][0], 4)] + ci(x)
def burden_table(pt, bs, m, cap, base_rates=(0.10, 0.01, 0.001)):
    tp, fp = pt[(m, cap)]; T, F = bs[(m, cap)][:, 0], bs[(m, cap)][:, 1]; out = dict(recall=[round(tp, 4)] + ci(T), false_alarm_rate=[round(fp, 4)] + ci(F))
    for p in base_rates:
        pp, al = burden(tp, fp, p); PP = np.array([burden(a, b, p)[0] for a, b in zip(T, F)]); AL = np.array([burden(a, b, p)[1] for a, b in zip(T, F)])
        out['p=%g' % p] = dict(precision=[round(pp, 4)] + ci(PP), alarms_per_million=[round(al, 1)] + ci(AL), false_per_true=round((1 - pp) / pp, 2) if pp > 0 else None)
    return out
# ---- analytic operation counts (per episode), H4. Inference: 2 x active parameters per generated token (multiply-add = 2 ops).
ACTIVE_PARAMS = 3.6e9      # gpt-oss-20b active parameters per token (OpenAI gpt-oss model card: 21B total, 3.6B active)
def ops_inference(n_tokens): return 2.0 * ACTIVE_PARAMS * n_tokens
def ops_probe(d_model, t_last, n_ckpt):
    '''Running mean of one layer's hidden state over tokens up to the last checkpoint (d adds per token), then per checkpoint a z-score
    and a logistic dot product over 2d + 1 features (about 3 ops per feature: subtract, divide, multiply-add).'''
    return float(d_model * t_last + n_ckpt * 3 * (2 * d_model + 1))
def ops_text(ts):
    '''Per checkpoint t: about 2t unigram+bigram lookups and a sparse dot product over at most 2t non-zeros (about 4t ops).'''
    return float(sum(4 * t + 7 for t in ts))
