# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Unit tests for YB-0050 decider (proofs as tests).'''
import sys, numpy as np; sys.path.insert(0, 'src')
from corrected import cap_threshold
from layered import recall_layered
from decider import threshold, single, layered, rates, burden, bootstrap, diff, burden_table, ops_probe, ops_inference, NEG
rng = np.random.default_rng(1)
# fast threshold equals the YB-0035 reference on continuous, tied, discrete and -inf data, at several caps
for trial in range(300):
    n = int(rng.integers(5, 300)); kind = trial % 4
    v = rng.normal(0, 1, n) if kind == 0 else (rng.integers(0, 5, n).astype(float) if kind == 1 else rng.choice([0, .25, .5, .75, 1.], n))
    if kind == 3: v = rng.normal(0, 1, n); v[rng.random(n) < 0.3] = -np.inf
    for cap in (0.0, 0.01, 0.05, 0.10, 0.5):
        assert threshold(v, cap) == cap_threshold(v, cap), (trial, cap)
        assert np.mean(v > threshold(v, cap)) <= cap + 1e-12
n = 4000; y = (rng.random(n) < 0.1).astype(int); full = np.arange(n)
v1 = rng.normal(0, 1, n) + 1.5 * y; v1[:400] = -np.inf; d = np.where(rng.random(n) < 0.5 * y + 0.03, 0.75, 0.0)
# layered rule with no gate reproduces the YB-0049 layered recall exactly
a = layered(v1, d)(full, y, 0.10); assert abs(rates(a, y)[0] - recall_layered(v1, d, y)[0]) < 1e-12
for cap in (0.10, 0.01):
    assert rates(layered(v1, d)(full, y, cap), y)[1] <= cap + 1e-12
    assert rates(single(v1)(full, y, cap), y)[1] <= cap + 1e-12
# gating: an all-False gate turns stage 2 off; an all-True gate equals no gate; a partial gate respects the cap
off = layered(v1, d, gate=np.zeros(n, bool))(full, y, 0.10); s1 = layered(v1, np.zeros(n))(full, y, 0.10); assert (off == s1).all()
assert (layered(v1, d, gate=np.ones(n, bool))(full, y, 0.10) == a).all()
assert rates(layered(v1, d, gate=rng.random(n) < 0.5)(full, y, 0.10), y)[1] <= 0.10 + 1e-12
# never-monitored episodes are never alarmed by a single in-time rule
assert not single(v1)(full, y, 0.10)[~np.isfinite(v1)].any()
# burden arithmetic
pp, al = burden(0.8, 0.1, 0.01); assert abs(pp - 0.008 / (0.008 + 0.099)) < 1e-12 and abs(al - 1e6 * 0.107) < 1e-6
assert burden(1.0, 0.0, 0.001)[0] == 1.0
# bootstrap: intervals bracket the point estimate for a clear difference, and the differences are paired
pt, bs = bootstrap({'a': single(v1), 'l': layered(v1, d)}, y, n=200)
dl = diff(pt, bs, 'l', 'a'); assert dl[1] <= dl[0] <= dl[2] and dl[1] > 0
bt = burden_table(pt, bs, 'a', 0.10); assert bt['p=0.01']['precision'][1] <= bt['p=0.01']['precision'][0] <= bt['p=0.01']['precision'][2]
from decider import ci
assert ci([np.nan, np.nan]) == [None, None] and ci([1.0, 2.0, np.nan])[0] >= 1.0
assert ops_probe(2880, 384, 4) / ops_inference(400) < 1e-5
print('test_decider: all assertions passed')
