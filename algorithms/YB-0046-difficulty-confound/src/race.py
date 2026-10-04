# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0023 race rules (pure functions, tested). A monitor alarm at checkpoint k counts only if the monitor finishes
computing before the answer is emitted: t_checkpoint + compute_s <= deadline (wall clock, original recording).'''
import numpy as np
F = (0.25, 0.5, 0.75)

def checkpoint_token(final_start, f): return int(f * final_start)

def times(latency, final_start, k):
    '''(time at checkpoint, deadline) in seconds from generation start.'''
    lat = np.asarray(latency, float); return float(lat[:k].sum()), float(lat[:final_start].sum())

def valid_alarm(score, threshold, t_ck, compute_s, deadline):
    return bool(score > threshold and t_ck + compute_s <= deadline)

def first_valid(checks):
    '''checks: list of (f, score, threshold, t_ck, compute_s, deadline) in time order -> (fired, f, alarm_time) earliest valid.'''
    for f, s, th, t, c, d in checks:
        if valid_alarm(s, th, t, c, d): return True, f, t + c
    return False, None, None
