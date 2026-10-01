# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from serial import serial_features, stage_k, parallel_features, STAGES
g = np.random.default_rng(0)
def ep(n=120, fs=100, idx=0):
    return dict(idx=idx, final_start=fs, entropy=list(g.random(n)), margin=list(g.random(n)), p_top1=list(g.random(n)), cat='x')
def t_stage_k():
    r = ep(); assert [stage_k(r, c) for c in STAGES] == [25, 50, 75, 100] and stage_k(dict(final_start=3), 0.25) == 2
def t_serial_no_look_ahead():
    r = ep(); L = np.abs(g.normal(size=(120, 24, 5))); L2 = L.copy(); L2[50:] = 9.0
    assert np.allclose(serial_features(r, L, 0.5), serial_features(r, L2, 0.5))
def t_stage_feature_present():
    r = ep(); L = np.abs(g.normal(size=(120, 24, 5))); assert serial_features(r, L, 0.75)[-1] == 0.75
def t_parallel_equals_serial():
    R = [ep(idx=i) for i in range(6)]; L = {i: np.abs(g.normal(size=(120, 24, 5))) for i in range(6)}
    jobs = [(r, c) for r in R for c in STAGES]
    assert np.allclose(parallel_features(jobs, L, procs=2), np.array([serial_features(r, L[r['idx']], c) for r, c in jobs]))
T = [t_stage_k, t_serial_no_look_ahead, t_stage_feature_present, t_parallel_equals_serial]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
