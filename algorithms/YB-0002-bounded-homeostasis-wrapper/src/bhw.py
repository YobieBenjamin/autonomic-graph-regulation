# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""YB-0002: Bounded Homeostatic Wrapper (BHW).

Wraps ANY detector whose score is a Mahalanobis distance of a feature vector s(x)
from an adaptive baseline mean mu. The baseline adapts (gated EWMA) so the monitor
tolerates benign slow change, but the total baseline displacement from its trusted
anchor mu0 is capped by a budget B. Theorems (see README section 3):

  T1  sup_t ||mu_t - mu0||_P <= B + eta*tau            (baseline can never be dragged further)
  T2  every input ever accepted satisfies ||s - mu0||_P <= tau + B + eta*tau
  T3  any drift of the baseline beyond B raises DRIFT after >= ceil(B/(eta*tau)) accepted steps
  C1  (calibration) under a stationary clean stream, D_t^2 ~ approx eta/(2-eta) * chi2_p,
      so B = sqrt(eta/(2-eta) * chi2_p^{-1}(q)) gives a per-step exceedance rate <= 1-q.
  C2  (finite-sample correction) mu0 is estimated from n samples, so the true clean mean sits
      ~ sqrt(chi2_p^{-1}(q)/n) away in P-norm; B_C2 = B_C1 + that term, with tau and P fit on
      disjoint halves of the calibration set (split calibration). Heuristic; validated empirically.
"""
import ctypes, os
import numpy as np
from scipy.stats import chi2

_LIB = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libbhw.so"))
_D, _I = ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)
_LIB.bhw_run.argtypes = [_D, ctypes.c_int, ctypes.c_int, _D, _D, ctypes.c_double, ctypes.c_double,
                         ctypes.c_double, ctypes.c_int, _D, _I, _D, _I]
MODES = {"static": 0, "unbounded": 1, "budgeted": 2}


def budget_rule(eta, p, q=0.999, n=None):
    """C1: B such that the stationary clean-stream drift D exceeds B with per-step prob ~ 1-q.
    C2: if n (samples used to estimate mu0) is given, add the mean-estimation error term."""
    b = float(np.sqrt(eta / (2 - eta) * chi2.ppf(q, p)))
    return b + (float(np.sqrt(chi2.ppf(q, p) / n)) if n else 0.0)


class BHW:
    def __init__(self, eta=0.02, quantile=0.95, budget=None, q_budget=0.999, shrink=1e-3, split=False):
        self.eta, self.q, self.B, self.qb, self.shrink, self.split = eta, quantile, budget, q_budget, shrink, split

    def fit(self, F):
        F = np.atleast_2d(np.asarray(F, float))
        if F.shape[0] == 1: F = F.T
        self.p = F.shape[1]
        Ffit, Fthr = (F[: len(F) // 2], F[len(F) // 2:]) if self.split else (F, F)
        self.mu0 = Ffit.mean(0)
        S = np.atleast_2d(np.cov(Ffit.T))
        S = S + self.shrink * np.trace(S) / self.p * np.eye(self.p)
        self.P = np.linalg.inv(S)
        d = np.sqrt(np.einsum("ij,jk,ik->i", Fthr - self.mu0, self.P, Fthr - self.mu0))
        self.tau = float(np.quantile(d, self.q))
        if self.B is None: self.B = budget_rule(self.eta, self.p, self.qb, len(Ffit) if self.split else None)
        return self

    def run(self, S, mode="budgeted"):
        S = np.ascontiguousarray(np.asarray(S, float).reshape(len(S), self.p))
        T = len(S); sc = np.zeros(T); dr = np.zeros(T)
        fl = np.zeros(T, np.int32); fr = np.zeros(T, np.int32)
        P = np.ascontiguousarray(self.P); mu0 = np.ascontiguousarray(self.mu0)
        rc = _LIB.bhw_run(S.ctypes.data_as(_D), T, self.p, P.ctypes.data_as(_D), mu0.ctypes.data_as(_D),
                          self.tau, self.eta, self.B, MODES[mode], sc.ctypes.data_as(_D),
                          fl.ctypes.data_as(_I), dr.ctypes.data_as(_D), fr.ctypes.data_as(_I))
        if rc: raise MemoryError
        return {"score": sc, "flag": fl.astype(bool), "drift": dr, "frozen": fr.astype(bool)}

    def run_reference(self, S, mode="budgeted"):
        """Pure-Python reference used to test the C core."""
        mu = self.mu0.copy(); frozen = False; out = {k: [] for k in ("score", "flag", "drift", "frozen")}
        n = lambda v: float(np.sqrt(v @ self.P @ v))
        for s in np.asarray(S, float).reshape(len(S), self.p):
            d = n(s - mu); f = d > self.tau
            if mode != "static" and not f and not frozen:
                mu = mu + self.eta * (s - mu)
                if mode == "budgeted" and n(mu - self.mu0) > self.B: frozen = True
            for k, v in zip(out, (d, f, n(mu - self.mu0), frozen)): out[k].append(v)
        return {k: np.array(v) for k, v in out.items()}


def worst_case_attack(mon, T, mode, c=0.99, seed=0):
    """Adaptive adversary with full knowledge: each input sits just inside the acceptance
    radius (c*tau) in a fixed direction, the fastest possible way to drag the baseline."""
    u = np.random.default_rng(seed).normal(size=mon.p)
    L = np.linalg.cholesky(np.linalg.inv(mon.P)); u = L @ u; u /= np.sqrt(u @ mon.P @ u)
    mu = mon.mu0.copy(); S = []; frozen = False
    for _ in range(T):
        s = mu + c * mon.tau * u; S.append(s)
        if mode != "static" and not frozen:
            mu = mu + mon.eta * (s - mu)
            if mode == "budgeted" and np.sqrt((mu - mon.mu0) @ mon.P @ (mu - mon.mu0)) > mon.B: frozen = True
    return np.array(S)
