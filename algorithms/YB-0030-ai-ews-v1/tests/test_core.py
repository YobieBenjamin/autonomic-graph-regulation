# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from aiews import AIEWS, VITALS
g = np.random.default_rng(0)
V = g.normal(size=(400, 7)); y = (g.random(400) < 0.15).astype(int); V[y == 1, 0] += 1.5; V[y == 1, 1] -= 1.5
A = AIEWS().fit(V, y)
def t_direction_and_mirror():
    assert A.direction[0] == 1 and A.direction[1] == -1 and A.bands[1][0] > A.bands[1][2]
def t_monotonic():
    for j in range(7):
        base = np.nanmedian(V[y == 0], 0); prev = -1
        for step in np.linspace(0, 6, 25):
            v = base.copy(); v[j] = base[j] + A.direction[j] * step; S = A.score(v)[0]; assert S >= prev; prev = S
def t_bounded():
    for _ in range(500):
        S = A.score(g.normal(scale=10, size=7))[0]; assert 0 <= S <= 21
def t_explainable():
    v = g.normal(size=7); S, lvl, pts = A.score(v); assert sum(pts.values()) == S and set(pts) == set(VITALS)
def t_red_flag_escalates():
    v = np.nanmedian(V[y == 0], 0).copy(); v[0] = A.bands[0][2] + 1; S, lvl, pts = A.score(v); assert pts['V1_entropy'] == 3 and lvl != 'stable'
def t_nan_scores_zero():
    v = np.full(7, np.nan); assert A.score(v)[0] == 0
T = [t_direction_and_mirror, t_monotonic, t_bounded, t_explainable, t_red_flag_escalates, t_nan_scores_zero]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
