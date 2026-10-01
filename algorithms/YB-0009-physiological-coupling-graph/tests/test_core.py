# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from graph import windows, windows_ref
r = np.random.default_rng(0)
def t_c_equals_reference():
    X = r.normal(size=(120, 5)); assert np.allclose(windows(X), windows_ref(X), atol=1e-9)
def t_identical_channels_complete_graph():
    x = r.normal(size=60); X = np.column_stack([x] * 4); Wn = windows(X, w=24, s=12, L=0)
    assert np.allclose(Wn[:, 0], 4 / 3, atol=1e-9) and np.allclose(Wn[:, 2], 6.0, atol=1e-9)
def t_lag_detection():
    x = r.normal(size=200); X = np.column_stack([x[2:], x[:-2], r.normal(size=198)])
    assert windows(X, w=48, s=48, L=2)[:, 2].min() > 0.99 and windows(X, w=48, s=48, L=0)[:, 2].max() < 0.9
def t_independent_channels_weak_coupling():
    X = r.normal(size=(4000, 4)); assert windows(X, w=1000, s=1000, L=3)[:, 2].max() < 6 * 0.15
def t_too_short():
    assert len(windows(r.normal(size=(10, 3)))) == 0
T = [t_c_equals_reference, t_identical_channels_complete_graph, t_lag_detection, t_independent_channels_weak_coupling, t_too_short]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
