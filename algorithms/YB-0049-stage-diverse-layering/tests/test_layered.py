# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Unit tests for YB-0049 layered thresholds (proofs as tests).'''
import sys, numpy as np; sys.path.insert(0, 'src')
from layered import tight, choose, alarm, recall_layered, recall_single, boot
v0 = np.array([0.1 * k for k in range(10)]); t = tight(v0, 0.10); assert np.mean(v0 > t) <= 0.10 and np.mean(v0 >= t) > 0.10
assert np.mean(np.array([-np.inf, 1, 2]) > tight(np.array([-np.inf, 1, 2]), 0.34)) <= 0.34
rng = np.random.default_rng(0); n = 3000; y = (rng.random(n) < 0.1).astype(int)
v1 = rng.normal(0, 1, n) + 1.5 * y; v1[:300] = -np.inf                       # 10% never monitored
d = np.where(rng.random(n) < 0.5 * y + 0.03, 0.75, 0.0)                      # stage 2 catches some errors, incl. never-monitored
t1, dl = choose(v1, d, y); a = alarm(v1, d, t1, dl)
assert a[y == 0].mean() <= 0.10 + 1e-12                                      # union cap respected
assert np.isfinite(v1).sum() < n and a[(~np.isfinite(v1)) & (y == 1)].sum() > 0   # stage 2 reaches never-monitored errors
rl = recall_layered(v1, d, y)[0]; rs = recall_single(v1, y)[0]; assert rl > rs  # here layering helps by construction
b = boot(v1, d, y, n=200); assert b[1] <= b[0] <= b[2]
d0 = np.zeros(n); assert abs(recall_layered(v1, d0, y)[0] - recall_single(v1, y, 0.05)[0]) < 1e-12   # useless stage 2 = stage 1 at 5%
print('test_layered: all assertions passed')
