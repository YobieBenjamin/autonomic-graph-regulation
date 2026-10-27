# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0046: intrinsic difficulty features computed ONLY from the question text and the true answer (never from the model output),
and a difficulty-plus-elapsed-length baseline monitor fitted per task category. See docs/PREREGISTRATION.md.'''
import re, datetime, numpy as np
from sklearn.linear_model import LogisticRegression

def _digits(n): return [int(c) for c in str(n)]

def add_carries(a, b):
    '''Carries in schoolbook addition: (number of carries, longest consecutive carry chain).'''
    da, db = _digits(a)[::-1], _digits(b)[::-1]; c = n = run = best = 0
    for k in range(max(len(da), len(db))):
        s = (da[k] if k < len(da) else 0) + (db[k] if k < len(db) else 0) + c
        c = 1 if s >= 10 else 0; n += c; run = run + 1 if c else 0; best = max(best, run)
    return n, best

def mul_carries(a, b):
    '''Schoolbook long multiplication by columns: (columns that produce a carry, log1p of total carry mass).'''
    da, db = _digits(a)[::-1], _digits(b)[::-1]; col = [0] * (len(da) + len(db) + 1)
    for i, x in enumerate(da):
        for j, y in enumerate(db): col[i + j] += x * y
    c = n = mass = 0
    for k in range(len(col)):
        s = col[k] + c; c = s // 10; n += c > 0; mass += c
    return n, float(np.log1p(mass))

def features(cat, q, truth):
    '''Fixed, pre-declared feature list per category. Returns a list of floats.'''
    if cat in ('mul_easy', 'mul_hard'):
        a, b = map(int, re.findall(r'\d+', q)[:2]); na, nb = sum(d > 0 for d in _digits(a)), sum(d > 0 for d in _digits(b)); n, m = mul_carries(a, b)
        return [len(str(a)), len(str(b)), na, nb, na * nb, n, m, len(str(a * b))]
    if cat == 'add_hard':
        a, b = map(int, re.findall(r'\d+', q)[:2]); n, run = add_carries(a, b)
        return [len(str(a)), len(str(b)), n, run, len(str(a + b))]
    if cat == 'count':
        m = re.search(r'letter (\w) appear in the string (\w+)', q); s = m.group(2)
        return [len(s), int(truth), len(set(s))]
    if cat == 'weekday':
        y, mo, d = map(int, re.search(r'(\d{4})-(\d{2})-(\d{2})', q).groups())
        leap = int(y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))
        return [abs(y - 2000) / 100.0, y // 100, leap, mo, d, mo <= 2]
    if cat == 'modpow':
        b, e, m = map(int, re.findall(r'\d+', q)[:3])
        return [len(str(b)), e, float(np.log2(max(e, 1))), bin(e).count('1'), len(str(m))]
    return []

class DifficultyBaseline:
    '''Per-category L2 logistic regression on difficulty features (+ log t when use_t). Categories with fewer than 5 errors in the
    training data fall back to their training error rate. Standardisation uses training statistics only. C = 1.0 (pre-declared).'''
    def __init__(self, use_t=True, C=1.0): self.use_t, self.C, self.m = use_t, C, {}
    def _x(self, r, t):
        f = features(r['cat'], r['q'], r['truth'])
        return np.array(f + ([np.log(t)] if self.use_t else []), float)
    def fit(self, jobs):
        by = {}
        for r, t in jobs: by.setdefault(r['cat'], []).append((r, t))
        for c, J in by.items():
            y = np.array([0 if r['correct'] else 1 for r, _ in J]); rate = float(y.mean())
            if y.sum() < 5 or y.sum() == len(y): self.m[c] = ('rate', rate); continue
            X = np.array([self._x(r, t) for r, t in J]); mu, sd = X.mean(0), X.std(0) + 1e-9
            lr = LogisticRegression(C=self.C, max_iter=5000).fit((X - mu) / sd, y); self.m[c] = ('lr', lr, mu, sd)
        return self
    def score(self, r, t):
        m = self.m.get(r['cat'])
        if m is None: return 0.0
        if m[0] == 'rate': return m[1]
        _, lr, mu, sd = m; return float(lr.predict_proba(((self._x(r, t) - mu) / sd)[None])[0, 1])
