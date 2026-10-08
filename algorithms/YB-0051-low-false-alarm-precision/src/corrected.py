# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0035 corrected race statistics (audit fixes F8, F9, F10, F28, F29). Pure functions, tested in tests/test_core.py.
An episode's checks for one monitor: list of (score, t_clock, compute_s, deadline) in time order.'''
import numpy as np
CAP = 0.10
FIXED_COST = {'organism': 0.005, 'aiews_v4': 0.005, 'length_C1': 0.0, 'length_C2': 0.0}   # F29: fixed, conservative (s)

def in_time_max(checks):
    '''Highest score among checks whose alarm would finish before the deadline; -inf if none.'''
    v = [s for s, t, c, d in checks if t + c <= d]; return max(v) if v else -np.inf

def cap_threshold(v_correct, cap=CAP):
    '''F8: smallest threshold with at most cap of correct episodes alarmed (score > threshold). Always satisfies the cap.'''
    v = np.asarray(v_correct, float); cands = np.concatenate(([-np.inf], np.unique(v[np.isfinite(v)])))
    for thr in cands:
        if np.mean(v > thr) <= cap + 1e-12: return float(thr)
    return float(np.inf)

def first_crossing_spare(checks, thr):
    '''F28: seconds to spare at the FIRST in-time check whose score exceeds the threshold; None if none.'''
    for s, t, c, d in checks:
        if t + c <= d and s > thr: return d - (t + c)
    return None

def evaluate(V, y, monitorable):
    '''V: in-time max scores. Returns threshold, fired mask and rates (F8, F9).'''
    thr = cap_threshold(V[y == 0]); f = V > thr
    mw, mc = monitorable & (y == 1), monitorable & (y == 0)
    return dict(threshold=thr, fired=f, recall=float(f[y == 1].mean()) if (y == 1).any() else None, caught=int((f & (y == 1)).sum()),
                fpr=float(f[y == 0].mean()), fpr_monitorable=float(f[mc].mean()) if mc.any() else None, recall_monitorable=float(f[mw].mean()) if mw.any() else None)

def boot_diff(Va, Vb, y, n=1000, seed=0):
    '''F10: resample ALL episodes; re-set both thresholds on each resample's correct episodes; recall difference on its wrong ones.'''
    g = np.random.default_rng(seed); d = []; N = len(y)
    for _ in range(n):
        i = g.integers(0, N, N); yy = y[i]
        if yy.sum() == 0 or yy.sum() == N: continue
        a = Va[i] > cap_threshold(Va[i][yy == 0]); b = Vb[i] > cap_threshold(Vb[i][yy == 0]); d.append(a[yy == 1].mean() - b[yy == 1].mean())
    ea, eb = Va > cap_threshold(Va[y == 0]), Vb > cap_threshold(Vb[y == 0])
    return [round(float(ea[y == 1].mean() - eb[y == 1].mean()), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]
