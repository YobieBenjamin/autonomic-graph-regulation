# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from agr import features, features_ref
from hpa import simulate, simulate_ref
from flagship import reasoning_features, paired_diff
r = np.random.default_rng(0)
def t_vitals_c_equals_reference():
    x = r.normal(size=300); assert np.allclose(features(x), features_ref(x), atol=1e-12)
def t_hpa_c_equals_reference():
    S = np.abs(r.normal(size=200)); assert all(np.allclose(a, b, rtol=1e-9, atol=1e-12) for a, b in zip(simulate(S, burn=200), simulate_ref(S, burn=200)))
def t_prefix_at_answer_equals_full_reasoning():
    ep = dict(entropy=list(r.random(80)), p_top1=list(r.random(80)), margin=list(r.random(80)), final_start=60)
    assert np.allclose(reasoning_features(ep), reasoning_features(ep, upto=60)) and np.allclose(reasoning_features(ep, upto=500), reasoning_features(ep))
def t_reasoning_features_blind_to_answer_tokens():
    ep = dict(entropy=list(r.random(80)), p_top1=list(r.random(80)), margin=list(r.random(80)), final_start=60)
    ep2 = dict(ep, entropy=ep['entropy'][:60] + [9.0] * 20)
    assert np.allclose(reasoning_features(ep), reasoning_features(ep2))
def t_paired_bootstrap_identical_is_zero():
    y = np.r_[np.zeros(50), np.ones(20)]; s = r.random(70); d = paired_diff(y, s, s.copy(), n=200); assert d == [0.0, 0.0, 0.0]
T = [t_vitals_c_equals_reference, t_hpa_c_equals_reference, t_prefix_at_answer_equals_full_reasoning, t_reasoning_features_blind_to_answer_tokens, t_paired_bootstrap_identical_is_zero]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
