# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Unit tests for the YB-0047 text monitor.'''
import sys, numpy as np; sys.path.insert(0, 'src')
from textmon import TextMonitor, doc, select_C
rng = np.random.default_rng(0); jobs = []
for i in range(300):
    wrong = i % 4 == 0; toks = list(rng.integers(0, 50, 60)) + ([999] * 5 if wrong else [998] * 5)
    jobs.append((dict(idx=i, cat='mul_hard', toks=toks, correct=not wrong), 64))
assert doc(jobs[0][0], 3).count('t') == 3
m = TextMonitor(1.0).fit(jobs[:200]); s_w = np.mean([m.score(r, t) for r, t in jobs[200:] if not r['correct']]); s_c = np.mean([m.score(r, t) for r, t in jobs[200:] if r['correct']])
assert s_w > s_c, (s_w, s_c)                                   # learns the planted text signal
m2 = TextMonitor(1.0).fit([(r, 30) for r, _ in jobs[:200]]); s2 = [m2.score(r, 30) for r, _ in jobs[200:]]
assert max(s2) - min(s2) < 0.5                                  # signal after token 30 is invisible at t=30: no peeking past t
C, tab = select_C(jobs); assert C in tab and len(tab) == 3
print('test_textmon: all assertions passed')
