# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Unit tests for YB-0048 fusion (proofs as tests).'''
import sys, numpy as np; sys.path.insert(0, 'src')
from fusion import Stack, Bands, logit
rng = np.random.default_rng(0); n = 4000; y = (rng.random(n) < 0.1).astype(int); ts = rng.choice([48, 96], n)
a = np.clip(0.1 + 0.3 * y + rng.normal(0, 0.1, n), 0.01, 0.99); b = np.clip(0.1 + rng.normal(0, 0.1, n), 0.01, 0.99)
S = np.c_[a, b]; st = Stack().fit(S, y); assert st.score([0.5, 0.1]) > st.score([0.1, 0.1])
B = Bands().fit(S, ts, y, ['a', 'b'])
assert B.points([0.0, 0.0], 48) == [0, 0]; assert B.points([1.0, 1.0], 96) == [3, 3]; assert B.score([1.0, 0.0], 48) == 3.0
p = B.b[('a', 48)]; assert p[0] <= p[1] <= p[2]
assert abs(logit(0.5)) < 1e-12
print('test_fusion: all assertions passed')
