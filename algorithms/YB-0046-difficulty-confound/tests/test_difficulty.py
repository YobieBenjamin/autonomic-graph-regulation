# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Unit tests for the YB-0046 difficulty features (proofs as tests).'''
import sys; sys.path.insert(0, 'src')
from difficulty import add_carries, mul_carries, features, DifficultyBaseline
assert add_carries(1, 2) == (0, 0); assert add_carries(5, 5) == (1, 1); assert add_carries(999, 1) == (3, 3); assert add_carries(195, 5) == (2, 2)
assert add_carries(320085, 515805) == (1, 1)
assert mul_carries(2, 3) == (0, 0.0); n, m = mul_carries(9, 9); assert n == 1 and abs(m - 2.1972246) < 1e-6          # 81: one carry of 8, log1p(8)
assert mul_carries(10, 10)[0] == 0                                                                                       # 100: no carries
f = features('mul_easy', 'What is 574 * 88?', '50512'); assert f[:2] == [3, 2] and f[-1] == 5 and len(f) == 8
assert features('add_hard', 'What is 320085 + 515805?', '835890') == [6, 6, 1, 1, 6]
assert features('count', 'How many times does the letter m appear in the string fvakqmzx?', '1') == [8, 1, 8]
w = features('weekday', 'What day of the week was 2205-05-30?', 'thursday'); assert w[1] == 22 and w[2] == 0 and w[3] == 5
p = features('modpow', 'What is 457^64 mod 4467?', '1912'); assert p[1] == 64 and p[3] == 1 and p[4] == 4
assert features('unknown', 'x', 'y') == []
mk = lambda i, c, q, tr, ok: dict(idx=i, cat=c, q=q, truth=tr, correct=ok)
jobs = [(mk(i, 'add_hard', 'What is %d + %d?' % (10 ** 5 + i * 7919, 99999 - i), '0', i % 3 != 0), 96) for i in range(60)]
B = DifficultyBaseline().fit(jobs); s = B.score(jobs[0][0], 96); assert 0.0 <= s <= 1.0
jobs2 = [(mk(i, 'weekday', 'What day of the week was 2001-01-0%d?' % (1 + i % 9), 'x', True), 48) for i in range(20)]
B2 = DifficultyBaseline().fit(jobs2); assert B2.score(jobs2[0][0], 48) == 0.0                                            # no errors: rate fallback
print('test_difficulty: all assertions passed')
