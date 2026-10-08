# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0048: multi-level fusion of non-LLM monitors. (1) Stack: logistic regression on the logits of the component scores, fitted on
cross-fitted derivation scores. (2) Hospital (NEWS2-style) banded score: each component earns 0-3 points at a checkpoint t, one point for
each of the 90th, 95th and 99th percentiles of that component's cross-fitted scores on CORRECT derivation observations at the same t, that
it exceeds; points are summed. Fully explainable: every point traces to one component and one band.'''
import numpy as np
from sklearn.linear_model import LogisticRegression
def logit(p): p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6); return np.log(p / (1 - p))
class Stack:
    def fit(self, S, y):
        X = logit(S); self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        self.lr = LogisticRegression(C=1.0, max_iter=5000).fit((X - self.mu) / self.sd, y); return self
    def score(self, s): return float(self.lr.predict_proba(((logit(np.asarray(s)[None]) - self.mu) / self.sd))[0, 1])
class Bands:
    '''bands[(m, t)] = (p90, p95, p99) of component m on correct derivation observations at checkpoint t.'''
    def fit(self, S, ts, y, names):
        self.names, self.b = names, {}
        for t in sorted(set(ts)):
            m = (np.asarray(ts) == t) & (np.asarray(y) == 0)
            for j, n in enumerate(names): self.b[(n, t)] = tuple(np.percentile(S[m, j], (90, 95, 99)))
        return self
    def points(self, s, t): return [int(sum(v > q for q in self.b[(n, t)])) for n, v in zip(self.names, s)]
    def score(self, s, t): return float(sum(self.points(s, t)))
