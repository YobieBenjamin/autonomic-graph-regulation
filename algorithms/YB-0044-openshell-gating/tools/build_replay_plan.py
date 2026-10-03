# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0044 replay plan. Reuses YB-0045 code and data unchanged: regulator fitted on the YB-0045 derivation seeds; alarm
threshold FROZEN from 5-fold cross-fitted derivation scores (at most 10% of derivation correct episodes alarmed), never set on
test labels. For each selected test episode (YB-0045 seeds 9, 13, 14, answered): D = answer emission time (s from start of
generation) and t_alarm = earliest checkpoint time + 5 ms with score above the threshold that is still before D, else null.
Selection: all wrong answers plus an equal number of correct answers drawn uniformly (numpy seed 44). Writes docs/replay_plan.json.
Run in the sandbox with the YB-0045 folder at /src45 (read-only) and this folder at /work.'''
import json, sys, numpy as np
sys.path.insert(0, '/tmp/s45/src'); sys.path.insert(0, '/tmp/s45/tests')
import experiment as E
from absrace import checkpoints, parallel_features, AbsOrganism
from corrected import cap_threshold
from sklearn.model_selection import GroupKFold
import os; os.chdir('/tmp/s45')
Rd, Ld, Hd = [], {}, {}
for S in E.DERIV:
    R, L, H = E.load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
jobs = [(r, t) for r in Rd for t in checkpoints(r)]; X = parallel_features(jobs, Ld, 4); O = AbsOrganism().fit_from(X, jobs)
yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); g = np.array([r['idx'] for r, _ in jobs]); cf = np.zeros(len(jobs))
for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), yj, g):
    Ot = AbsOrganism().fit_from(X[tr], [jobs[i] for i in tr])
    for i in te: r, t = jobs[i]; cf[i] = Ot.score(r, Ld[r['idx']], t)
m = {(r['idx'], t): cf[i] for i, (r, t) in enumerate(jobs)}; yd = np.array([0 if r['correct'] else 1 for r in Rd])
Vd = E.in_time(Rd, lambda r, t: m[(r['idx'], t)], lambda r, t: E.COST); thr = float(cap_threshold(Vd[yd == 0]))
eps = []
for S in E.TEST:
    R, L, H = E.load_seed(S, 100000 * int(S))
    for r in R:
        if not (r['answered'] and r['idx'] in L): continue
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum()); ta = None
        for t in checkpoints(r):
            tc = float(lat[:t].sum()) + E.COST
            if tc <= D and O.score(r, L[r['idx']], t) > thr: ta = round(tc, 4); break
        eps.append(dict(idx=int(r['idx']), seed=S, cat=r['cat'], correct=bool(r['correct']), D=round(D, 4), t_alarm=ta))
rng = np.random.default_rng(44); W = [e for e in eps if not e['correct']]; C = [e for e in eps if e['correct']]
sel = W + [C[i] for i in sorted(rng.choice(len(C), size=len(W), replace=False))]
out = dict(threshold_frozen=thr, test_answered=len(eps), selected=len(sel), wrong=len(W), alarms_on_wrong=sum(1 for e in W if e['t_alarm'] is not None),
           alarms_on_selected_correct=sum(1 for e in sel if e['correct'] and e['t_alarm'] is not None), episodes=sel)
json.dump(out, open('/work/docs/replay_plan.json', 'w'), indent=1); print(json.dumps({k: v for k, v in out.items() if k != 'episodes'}))
