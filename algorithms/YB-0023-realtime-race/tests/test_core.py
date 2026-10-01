# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from race import checkpoint_token, times, valid_alarm, first_valid
from deep import deep_features
def t_checkpoints():
    assert [checkpoint_token(200, f) for f in (0.25, 0.5, 0.75)] == [50, 100, 150]
def t_times():
    t, d = times([0.1] * 300, 200, 50); assert abs(t - 5.0) < 1e-9 and abs(d - 20.0) < 1e-9
def t_deadline_rule():
    assert valid_alarm(0.9, 0.5, 18.0, 1.9, 20.0) and not valid_alarm(0.9, 0.5, 18.0, 2.1, 20.0) and not valid_alarm(0.4, 0.5, 1.0, 0.0, 20.0)
def t_first_valid_is_earliest():
    fired, f, at = first_valid([(0.25, 0.9, 0.5, 5.0, 16.0, 20.0), (0.5, 0.9, 0.5, 10.0, 1.0, 20.0), (0.75, 0.9, 0.5, 15.0, 0.1, 20.0)])
    assert fired and f == 0.5 and abs(at - 11.0) < 1e-9
def t_prefix_blind_to_future():
    L = np.abs(np.random.default_rng(0).normal(size=(120, 24, 5))) + 1; L2 = L.copy(); L2[60:] = 50.0
    assert np.allclose(deep_features(L, 100, upto=60), deep_features(L2, 100, upto=60))
T = [t_checkpoints, t_times, t_deadline_rule, t_first_valid_is_earliest, t_prefix_blind_to_future]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
