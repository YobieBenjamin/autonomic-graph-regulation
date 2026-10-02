# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''POST HOC (deviation: the pre-registration listed per-test-seed results as secondary, but tests/experiment.py does not
compute them). Reuses the pre-registered functions unchanged: same derivation data, same monitors, same race rules, same
population; reports regulator, probe and judge per test seed with the threshold-resampling bootstrap. Writes
docs/posthoc_per_seed.json. The pre-registered pooled result (docs/results.json) is the primary result.'''
import json, sys, numpy as np
sys.path.insert(0, 'src'); sys.path.insert(0, 'tests')
import experiment as E
from absrace import checkpoints, parallel_features, AbsOrganism
from probe import Probe
from corrected import evaluate, boot_diff
Rd, Ld, Hd = [], {}, {}
for S in E.DERIV:
    R, L, H = E.load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
jobs = [(r, t) for r in Rd for t in checkpoints(r)]
O = AbsOrganism().fit_from(parallel_features(jobs, Ld, 4), jobs)
res0 = json.load(open('docs/results.json')); P = Probe(res0['probe_selected']['layer'], res0['probe_selected']['C']).fit(jobs, Hd)
out = dict(note='POST HOC; not pre-registered as computed', probe=res0['probe_selected'])
fixed = lambda r, t: E.COST
for S in E.TEST:
    R, L, H = E.load_seed(S, 100000 * int(S))
    PJ = {(100000 * int(S) + d['idx'], int(d['f'])): d for d in E.ld('data/prefix_judge_abs_s%s.jsonl.gz' % S)}
    A = [r for r in R if r['answered'] and r['idx'] in L and all(('last_%d' % t) in H.get(r['idx'], {}) for t in checkpoints(r)) and all((r['idx'], t) in PJ for t in checkpoints(r))]
    y = np.array([0 if r['correct'] else 1 for r in A]); mon = np.array([len(checkpoints(r)) > 0 for r in A])
    V = dict(regulator=E.in_time(A, lambda r, t: O.score(r, L[r['idx']], t), fixed), probe=E.in_time(A, lambda r, t: P.score(r, t, H), fixed),
             judge=E.in_time(A, lambda r, t: PJ[(r['idx'], t)]['score'], lambda r, t: PJ[(r['idx'], t)]['compute_s']))
    out['seed ' + S] = dict(answered=len(A), wrong=int(y.sum()), caught={m: evaluate(v, y, mon)['caught'] for m, v in V.items()},
                            regulator_minus_judge=boot_diff(V['regulator'], V['judge'], y), probe_minus_judge=boot_diff(V['probe'], V['judge'], y))
json.dump(out, open('docs/posthoc_per_seed.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)); print(json.dumps(out, default=str))
