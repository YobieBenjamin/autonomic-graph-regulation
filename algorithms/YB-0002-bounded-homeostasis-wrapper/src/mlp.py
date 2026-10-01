# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""Minimal numpy MLP (2 ReLU hidden layers) with Adam and FGSM, for testing YB-0001."""
import numpy as np


class MLP:
    def __init__(self, d, h1, h2, c, seed=0):
        r = np.random.default_rng(seed)
        self.p = {"W1": r.normal(0, np.sqrt(2/d), (h1, d)), "b1": np.zeros(h1),
                  "W2": r.normal(0, np.sqrt(2/h1), (h2, h1)), "b2": np.zeros(h2),
                  "W3": r.normal(0, np.sqrt(2/h2), (c, h2)), "b3": np.zeros(c)}

    def forward(self, X):
        p = self.p
        z1 = X @ p["W1"].T + p["b1"]; a1 = np.maximum(z1, 0)
        z2 = a1 @ p["W2"].T + p["b2"]; a2 = np.maximum(z2, 0)
        return z1, a1, z2, a2, a2 @ p["W3"].T + p["b3"]

    @staticmethod
    def softmax(z):
        e = np.exp(z - z.max(1, keepdims=True)); return e / e.sum(1, keepdims=True)

    def grads(self, X, y):
        p = self.p; z1, a1, z2, a2, lo = self.forward(X)
        n = len(X); g = self.softmax(lo); g[np.arange(n), y] -= 1; g /= n
        G = {"W3": g.T @ a2, "b3": g.sum(0)}
        d2 = (g @ p["W3"]) * (z2 > 0); G["W2"] = d2.T @ a1; G["b2"] = d2.sum(0)
        d1 = (d2 @ p["W2"]) * (z1 > 0); G["W1"] = d1.T @ X; G["b1"] = d1.sum(0)
        dX = d1 @ p["W1"]
        return G, dX

    def train(self, X, y, epochs=60, lr=3e-3, bs=64, seed=0):
        r = np.random.default_rng(seed)
        m = {k: np.zeros_like(v) for k, v in self.p.items()}; v = {k: np.zeros_like(x) for k, x in self.p.items()}
        t = 0
        for _ in range(epochs):
            idx = r.permutation(len(X))
            for i in range(0, len(X), bs):
                b = idx[i:i+bs]; G, _ = self.grads(X[b], y[b]); t += 1
                for k in self.p:
                    m[k] = .9*m[k] + .1*G[k]; v[k] = .999*v[k] + .001*G[k]**2
                    self.p[k] -= lr * (m[k]/(1-.9**t)) / (np.sqrt(v[k]/(1-.999**t)) + 1e-8)

    def predict(self, X):
        return self.forward(X)[-1].argmax(1)

    def fgsm(self, X, y, eps):
        _, dX = self.grads(X, y)
        return np.clip(X + eps * np.sign(dX), 0, 1)
