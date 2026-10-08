# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0047: a TRAINED text-side monitor. Reads only the reasoning tokens before checkpoint t (token-id unigrams and bigrams; the ids are the
text, undecoded, because the sandbox has no network to fetch the tokenizer) plus task category and log t. L2 logistic regression; C chosen by
grouped 5-fold CV on derivation data only. It sees exactly what a text judge sees, but is trained on the same labels as the probe.'''
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
CATS = ('add_hard', 'count', 'modpow', 'mul_easy', 'mul_hard', 'weekday'); C_GRID = (0.1, 1.0, 10.0)
def doc(r, t): return ' '.join('t%d' % x for x in r['toks'][:t])
def side(jobs): return csr_matrix(np.array([[np.log(t)] + [float(r['cat'] == c) for c in CATS] for r, t in jobs]))
class TextMonitor:
    def __init__(self, C=1.0): self.C = C
    def fit(self, jobs):
        self.v = TfidfVectorizer(token_pattern=r'\S+', ngram_range=(1, 2), min_df=3, max_features=50000, sublinear_tf=True)
        X = hstack([self.v.fit_transform([doc(r, t) for r, t in jobs]), side(jobs)]).tocsr(); y = np.array([0 if r['correct'] else 1 for r, _ in jobs])
        self.lr = LogisticRegression(C=self.C, max_iter=5000).fit(X, y); return self
    def score(self, r, t): return float(self.lr.predict_proba(hstack([self.v.transform([doc(r, t)]), side([(r, t)])]).tocsr())[0, 1])
def select_C(jobs):
    y = np.array([0 if r['correct'] else 1 for r, _ in jobs]); g = np.array([r['idx'] for r, _ in jobs]); tab = {}
    for C in C_GRID:
        s = np.zeros(len(jobs))
        for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), y, g):
            m = TextMonitor(C).fit([jobs[i] for i in tr])
            for i in te: s[i] = m.score(*jobs[i])
        tab[C] = round(float(roc_auc_score(y, s)), 4)
    return max(tab, key=lambda c: (tab[c], -c)), tab
