# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, abs_features, parallel_features, LengthControls, T
g = np.random.default_rng(0)
def ep(fs=300, idx=0, cat='x', correct=True):
    n = fs + 20; return dict(idx=idx, final_start=fs, entropy=list(g.random(n)), margin=list(g.random(n)), p_top1=list(g.random(n)), cat=cat, correct=correct)
def t_checkpoints_only_while_reasoning():
    assert checkpoints(ep(300)) == [48, 96, 192] and checkpoints(ep(40)) == [] and checkpoints(ep(385)) == [48, 96, 192, 384]
def t_features_independent_of_total_length():
    '''Same first t tokens, different total length -> identical features (the YB-0032 leak cannot recur).'''
    L = np.abs(g.normal(size=(500, 24, 5))); a, b = ep(200), ep(450)
    assert np.allclose(abs_features(a, L, 96), abs_features(b, L, 96))
def t_no_look_ahead():
    L = np.abs(g.normal(size=(400, 24, 5))); L2 = L.copy(); L2[96:] = 9.0; r = ep(350)
    assert np.allclose(abs_features(r, L, 96), abs_features(r, L2, 96))
def t_parallel_equals_serial():
    R = [ep(300, i) for i in range(4)]; L = {i: np.abs(g.normal(size=(320, 24, 5))) for i in range(4)}
    jobs = [(r, t) for r in R for t in checkpoints(r)]
    assert np.allclose(parallel_features(jobs, L, 2), np.array([abs_features(r, L[r['idx']], t) for r, t in jobs]))
def t_length_controls():
    C = LengthControls().fit([ep(100, cat='a'), ep(200, cat='a'), ep(300, cat='a'), ep(400, cat='a')])
    r = ep(999, cat='a'); assert C.c1(r, 96) == 96 and C.c2(r, 96) == 0.0 and C.c2(r, 192) == 0.25 and C.c2(r, 384) == 0.75
T_ = [t_checkpoints_only_while_reasoning, t_features_independent_of_total_length, t_no_look_ahead, t_parallel_equals_serial, t_length_controls]
for t in T_: t(); print('PASS', t.__name__)
print(f'{len(T_)}/{len(T_)} tests passed')
