# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from aiews import AIEWS, settle
from race import valid_alarm, first_valid
from deep import deep_features
g = np.random.default_rng(0)
V = g.normal(size=(600, 8)); y = (g.random(600) < 0.1).astype(int); V[y == 1, 7] += 2
A = AIEWS().fit(V, y)
def t_bounded_8_vitals():
    assert all(0 <= A.score(g.normal(scale=9, size=8))[0] <= 24 for _ in range(300))
def t_monotonic_v8():
    base = np.nanmedian(V[y == 0], 0); prev = -1
    for s in np.linspace(0, 6, 25):
        v = base.copy(); v[7] += A.direction[7] * s; S = A.score(v)[0]; assert S >= prev; prev = S
def t_settle_closed_form():
    r = dict(entropy=[3.0] * 30 + [2.0] * 30 + [1.0] * 30, final_start=90); assert abs(settle(r) - (1.0 - 3.0)) < 1e-12
    r2 = dict(entropy=[1.0] * 45 + [2.0] * 45, final_start=90); assert settle(r2) > 0
def t_settle_prefix_blind():
    r = dict(entropy=list(g.random(100)), final_start=100); r2 = dict(r, entropy=r['entropy'][:60] + [9.0] * 40)
    assert abs(settle(r, 60) - settle(r2, 60)) < 1e-12
def t_race_rules():
    assert valid_alarm(0.9, 0.5, 1.0, 0.5, 2.0) and not valid_alarm(0.9, 0.5, 1.9, 0.2, 2.0)
    assert first_valid([(0.25, 0.1, 0.5, 1, 0, 9), (0.5, 0.9, 0.5, 2, 0, 9)])[1] == 0.5
def t_deep_prefix_blind():
    L = np.abs(g.normal(size=(120, 24, 5))) + 1; L2 = L.copy(); L2[60:] = 50.0
    assert np.allclose(deep_features(L, 100, upto=60), deep_features(L2, 100, upto=60))
T = [t_bounded_8_vitals, t_monotonic_v8, t_settle_closed_form, t_settle_prefix_blind, t_race_rules, t_deep_prefix_blind]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
