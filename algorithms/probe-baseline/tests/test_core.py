# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from corrected import cap_threshold, in_time_max, first_crossing_spare, evaluate, boot_diff
from absrace import checkpoints, abs_features
g = np.random.default_rng(0)
def t_cap_never_exceeded():
    for _ in range(300):
        v = np.where(g.random(200) < 0.2, -np.inf, np.round(g.random(200), int(g.integers(0, 3))))
        thr = cap_threshold(v); assert np.mean(v > thr) <= 0.10 + 1e-12
def t_cap_is_tightest():
    v = np.arange(100, dtype=float); thr = cap_threshold(v); assert np.mean(v > thr) == 0.10 and thr == 89.0
def t_ties_do_not_break_cap():
    v = np.array([1.0] * 50 + [0.0] * 50); thr = cap_threshold(v); assert np.mean(v > thr) <= 0.10 and thr == 1.0
def t_in_time_max_respects_deadline():
    assert in_time_max([(0.9, 1.0, 0.5, 1.2), (0.4, 0.5, 0.1, 1.2)]) == 0.4 and in_time_max([(0.9, 2.0, 0, 1.0)]) == -np.inf
def t_first_crossing_is_earliest():
    ch = [(0.2, 1.0, 0.0, 10.0), (0.8, 2.0, 0.0, 10.0), (0.9, 3.0, 0.0, 10.0)]; assert first_crossing_spare(ch, 0.5) == 8.0
def t_monitorable_rates():
    # 20 correct (18 monitorable, scores 0.00-0.17; 2 unmonitorable), 2 wrong (1 monitorable at 0.9, 1 unmonitorable)
    V = np.array([0.9, -np.inf] + [i / 100 for i in range(18)] + [-np.inf, -np.inf]); y = np.array([1, 1] + [0] * 20); mon = np.isfinite(V)
    e = evaluate(V, y, mon)
    assert e['fpr'] <= 0.10 and e['recall'] == 0.5 and e['recall_monitorable'] == 1.0 and abs(e['fpr_monitorable'] - e['fpr'] * 20 / 18) < 1e-12
def t_bootstrap_identical_monitors_zero():
    V = g.random(300); y = (g.random(300) < 0.15).astype(int); d = boot_diff(V, V.copy(), y, n=200); assert d == [0.0, 0.0, 0.0]
def t_features_independent_of_total_length():
    L = np.abs(g.normal(size=(500, 24, 5))); a, b = dict(final_start=200), dict(final_start=450)
    assert np.allclose(abs_features(a, L, 96), abs_features(b, L, 96))
T = [t_cap_never_exceeded, t_cap_is_tightest, t_ties_do_not_break_cap, t_in_time_max_respects_deadline, t_first_crossing_is_earliest,
     t_monitorable_rates, t_bootstrap_identical_monitors_zero, t_features_independent_of_total_length]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
