# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""YB-0001: Homeostatic Heat-Trace Circuit Monitor (H2CM).

Pipeline per input x:
  1. Build the model's *effective connectivity graph* for x: nodes are hidden
     and output units; edge (j -> i) weight = |W[i, j] * a_j(x)|, i.e. how much
     signal actually flowed along that synapse for this input.
  2. Compute the normalized-Laplacian heat trace h(t) = sum_k exp(-t*lambda_k)
     at several diffusion times t (compiled C core).
  3. Score = Mahalanobis distance of log-heat-trace signature from a trusted
     baseline. High score = the network is "thinking in an unusual shape".
  4. Homeostasis: the baseline mean slowly tracks accepted inputs, but its total
     displacement from the anchored set point is capped by a drift budget B.
     Exceeding B raises a DRIFT alarm and freezes adaptation (anti boiling-frog).
"""
import ctypes, os
import numpy as np

_LIB = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libheattrace.so"))
_P = ctypes.POINTER(ctypes.c_double)
_LIB.heat_trace.argtypes = [_P, ctypes.c_int, _P, ctypes.c_int, _P, _P]
_LIB.heat_trace.restype = ctypes.c_int

DEFAULT_TS = np.logspace(-1, 1.5, 8)


def heat_trace(A, ts=DEFAULT_TS, return_eigs=False):
    A = np.ascontiguousarray(A, dtype=np.float64)
    ts = np.ascontiguousarray(ts, dtype=np.float64)
    n = A.shape[0]
    out = np.zeros(len(ts)); ev = np.zeros(n)
    rc = _LIB.heat_trace(A.ctypes.data_as(_P), n, ts.ctypes.data_as(_P), len(ts),
                         out.ctypes.data_as(_P), ev.ctypes.data_as(_P))
    if rc != 0:
        raise MemoryError("heat_trace allocation failed")
    return (out, ev) if return_eigs else out


def effective_connectivity(weights, activations):
    """weights: [W2 (n2 x n1), W3 (C x n2)]; activations: [a1 (n1), a2 (n2)].
    Returns symmetric adjacency over n1 + n2 + C nodes."""
    sizes = [weights[0].shape[1]] + [W.shape[0] for W in weights]
    off = np.concatenate([[0], np.cumsum(sizes)])
    A = np.zeros((off[-1], off[-1]))
    for l, (W, a) in enumerate(zip(weights, activations)):
        F = np.abs(W * a[None, :])                     # flow from layer l to l+1
        A[off[l+1]:off[l+2], off[l]:off[l+1]] = F
    return A + A.T


def signature(weights, activations, ts=DEFAULT_TS, rich=True):
    """v1 (rich=False): log normalized heat trace only (scale-invariant shape).
    v2 (rich=True): adds scale + hub-structure terms the normalized Laplacian
    discards: log total flow per layer, and entropy of the node-strength
    distribution (how concentrated signal routing is on a few hub units)."""
    A = effective_connectivity(weights, activations)
    shape = np.log(heat_trace(A, ts) / A.shape[0])
    if not rich:
        return shape
    flows = [np.log(np.abs(W * a[None, :]).sum() + 1e-12) for W, a in zip(weights, activations)]
    d = A.sum(1); p = d / (d.sum() + 1e-12)
    ent = -(p[p > 0] * np.log(p[p > 0])).sum()
    return np.concatenate([shape, flows, [ent]])


class H2CM:
    def __init__(self, ts=DEFAULT_TS, quantile=0.95, eta=0.01, drift_budget=3.0, shrink=1e-3):
        self.ts, self.q, self.eta, self.B, self.shrink = ts, quantile, eta, drift_budget, shrink

    def fit(self, sigs):
        sigs = np.asarray(sigs)
        self.mu0 = sigs.mean(0); self.mu = self.mu0.copy()
        S = np.cov(sigs.T) + self.shrink * np.eye(sigs.shape[1]) * np.trace(np.cov(sigs.T)) / sigs.shape[1]
        self.P = np.linalg.inv(S)
        self.tau = np.quantile([self._d(s, self.mu0) for s in sigs], self.q)
        self.frozen = False
        return self

    def _d(self, s, m):
        v = s - m
        return float(np.sqrt(v @ self.P @ v))

    def score(self, s):
        return self._d(s, self.mu)

    def drift(self):
        return self._d(self.mu, self.mu0)

    def step(self, s, budgeted=True, adapt=True):
        """Streaming update. Returns (flagged, drift_alarm)."""
        d = self.score(s); flagged = d > self.tau
        if adapt and not flagged and not self.frozen:
            self.mu = self.mu + self.eta * (s - self.mu)
            if budgeted and self.drift() > self.B:
                self.frozen = True
                return flagged, True
        return flagged, self.frozen
