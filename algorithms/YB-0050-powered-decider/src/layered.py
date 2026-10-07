# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0049: two-stage (stage-diverse) layered alarm. Stage 1: pre-answer in-time score v1 (probe). Stage 2: post-answer self-consistency
disagreement d in {0, .25, .5, .75, 1}. Alarm if v1 > tau1 OR d >= delta. Pre-declared allocation: tau1 is the tightest threshold with at most
ALPHA1 of correct episodes alarmed by stage 1; delta is the smallest value in D_GRID whose union false-alarm rate is at most CAP (stage 2 off if
none). Never-monitored episodes have v1 = -inf (never alarmed by stage 1) but can still be alarmed by stage 2.'''
import numpy as np
D_GRID = (0.25, 0.5, 0.75, 1.0)
def tight(v0, cap):
    '''Tightest threshold tau with mean(v0 > tau) <= cap (v0: scores of correct episodes; -inf allowed).'''
    v = np.sort(np.where(np.isfinite(v0), v0, -1e18))[::-1]; k = int(np.floor(cap * len(v)))
    if k >= len(v): return -1e18
    return float(v[k])
def choose(v1, d, y, alpha1=0.05, cap=0.10):
    c = y == 0; t1 = tight(v1[c], alpha1); s1 = np.where(np.isfinite(v1), v1, -1e18) > t1
    for dl in D_GRID:
        if np.mean((s1 | (d >= dl))[c]) <= cap: return t1, dl
    return t1, None
def alarm(v1, d, t1, dl):
    s1 = np.where(np.isfinite(v1), v1, -1e18) > t1
    return s1 | (d >= dl) if dl is not None else s1
def recall_layered(v1, d, y, alpha1=0.05, cap=0.10):
    t1, dl = choose(v1, d, y, alpha1, cap); a = alarm(v1, d, t1, dl)
    return float(a[y == 1].mean()), float(a[y == 0].mean()), t1, dl
def recall_single(v, y, cap=0.10):
    t = tight(v[y == 0], cap); a = np.where(np.isfinite(v), v, -1e18) > t
    return float(a[y == 1].mean()), float(a[y == 0].mean()), t
def boot(v1, d, y, n=1000, seed=0, alpha1=0.05, cap=0.10):
    '''Paired bootstrap of layered minus probe-alone recall; all thresholds re-set inside every resample.'''
    g = np.random.default_rng(seed); out = []
    for _ in range(n):
        i = g.integers(0, len(y), len(y)); yi = y[i]
        if yi.sum() == 0 or yi.sum() == len(yi): continue
        out.append(recall_layered(v1[i], d[i], yi, alpha1, cap)[0] - recall_single(v1[i], yi, cap)[0])
    pt = recall_layered(v1, d, y, alpha1, cap)[0] - recall_single(v1, y, cap)[0]
    return [round(pt, 4), round(float(np.percentile(out, 2.5)), 4), round(float(np.percentile(out, 97.5)), 4)]
