# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''EXPLORATORY (not pre-registered for YB-0035; added after the second audit, findings B6 and B8). Seed 7, answered episodes.
(a) Thresholds equalized among MONITORABLE episodes: each monitor's threshold is the tightest with at most 10% of the correct
    episodes that have at least one checkpoint alarmed. (b) A question-type baseline C3 (derivation failure rate of the
    episode's question type, known at every checkpoint, zero cost). (c) Frozen thresholds from derivation data (seeds 2-4,
    5-fold cross-fitted regulator scores; length C1 and type C3 directly) at 10% false alarms on derivation correct episodes;
    the judge has no derivation runs, so it has no frozen variant. Writes docs/exploratory_audit2.json.'''
import json, sys, glob, numpy as np
sys.path.insert(0, 'src')
from flagship import load
from absrace import checkpoints, parallel_features, AbsOrganism, LengthControls
from corrected import in_time_max, cap_threshold, boot_diff
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
COST = 0.005
def layers(pattern, off=0):
    out = {}
    for p in sorted(glob.glob(pattern)):
        z = np.load(p); out.update({off + int(k[1:]): z[k].astype(np.float32) for k in z.files})
    return out
def eps(seed, off, L): return [dict(r, idx=off + r['idx']) for r in load('data/seed' + seed + '_L.jsonl.gz') if r['answered'] and off + r['idx'] in L]
Ld, Rd = {}, []
for s, off in (('2', 0), ('3', 100000), ('4', 200000)):
    Ls = layers('data/layers_seed' + s + '_*.npz', off); Ld.update(Ls); Rd += eps(s, off, Ls)
jobs = [(r, t) for r in Rd for t in checkpoints(r)]; X = parallel_features(jobs, Ld, 4); O = AbsOrganism().fit_from(X, jobs); C = LengthControls().fit(Rd)
rate = {c: float(np.mean([0 if r['correct'] else 1 for r in Rd if r['cat'] == c])) for c in set(r['cat'] for r in Rd)}
# cross-fitted derivation regulator scores (grouped by episode) for the frozen threshold
yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); grp = np.array([r['idx'] for r, _ in jobs]); key = [(r['cat'], t) for r, t in jobs]
Z = O._z(X, key); cf = np.zeros(len(jobs))
for tr, te in GroupKFold(5).split(Z, yj, grp):
    cf[te] = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(Z[tr], yj[tr]).predict_proba(Z[te])[:, 1]
def intime(R, score):
    V = []
    for r in R:
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
        V.append(in_time_max([(score(r, t), float(lat[:t].sum()), COST, D) for t in checkpoints(r)]))
    return np.array(V)
cfmap = {(r['idx'], t): cf[i] for i, (r, t) in enumerate(jobs)}
Vd_org = intime(Rd, lambda r, t: cfmap[(r['idx'], t)]); yd = np.array([0 if r['correct'] else 1 for r in Rd])
Vd_c1 = intime(Rd, lambda r, t: float(t)); Vd_c3 = intime(Rd, lambda r, t: rate[r['cat']])
frozen = dict(organism=cap_threshold(Vd_org[yd == 0]), length_C1=cap_threshold(Vd_c1[yd == 0]), type_C3=cap_threshold(Vd_c3[yd == 0]))
L7 = layers('data/layers_seed7_*.npz'); R7 = eps('7', 0, L7); PJ = {(d['idx'], int(d['f'])): d for d in load('data/prefix_judge_abs_s7.jsonl.gz')}
R7 = [r for r in R7 if all((r['idx'], t) in PJ for t in checkpoints(r))]; y = np.array([0 if r['correct'] else 1 for r in R7]); mon = np.array([len(checkpoints(r)) > 0 for r in R7])
V = {}
for m, fn, cost in (('organism', lambda r, t: O.score(r, L7[r['idx']], t), COST), ('judge_prefix', lambda r, t: PJ[(r['idx'], t)]['score'], None),
                    ('length_C1', lambda r, t: float(t), 0.0), ('type_C3', lambda r, t: rate[r['cat']], 0.0)):
    vals = []
    for r in R7:
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
        vals.append(in_time_max([(fn(r, t), float(lat[:t].sum()), PJ[(r['idx'], t)]['compute_s'] if cost is None else cost, D) for t in checkpoints(r)]))
    V[m] = np.array(vals)
ym = y[mon]; Vm = {m: v[mon] for m, v in V.items()}
res = dict(note='EXPLORATORY; not pre-registered for YB-0035', seed7_answered=len(y), wrong=int(y.sum()), monitorable=int(mon.sum()), monitorable_wrong=int(ym.sum()), monitorable_correct=int((ym == 0).sum()),
           derivation_answered=len(yd), frozen_thresholds_from_derivation=frozen)
eq = {}
for m, v in Vm.items():
    thr = cap_threshold(v[ym == 0]); f = v > thr; eq[m] = dict(caught=int((f & (ym == 1)).sum()), fpr_monitorable=round(float(f[ym == 0].mean()), 4))
res['a_equal_fpr_among_monitorable'] = dict(per_monitor=eq, organism_minus_judge=boot_diff(Vm['organism'], Vm['judge_prefix'], ym), organism_minus_length_C1=boot_diff(Vm['organism'], Vm['length_C1'], ym), organism_minus_type_C3=boot_diff(Vm['organism'], Vm['type_C3'], ym))
res['b_type_baseline_primary_protocol'] = dict(type_C3_caught=int(((V['type_C3'] > cap_threshold(V['type_C3'][y == 0])) & (y == 1)).sum()), type_C3_fpr=round(float((V['type_C3'] > cap_threshold(V['type_C3'][y == 0]))[y == 0].mean()), 4), organism_minus_type_C3=boot_diff(V['organism'], V['type_C3'], y))
fz = {}
for m in ('organism', 'length_C1', 'type_C3'):
    f = V[m] > frozen[m]; fz[m] = dict(caught=int((f & (y == 1)).sum()), fpr_all=round(float(f[y == 0].mean()), 4), fpr_monitorable=round(float(f[(y == 0) & mon].mean()), 4))
res['c_frozen_thresholds'] = fz
J = lambda o: o.item() if hasattr(o, 'item') else str(o)
json.dump(res, open('docs/exploratory_audit2.json', 'w'), indent=1, default=J); print(json.dumps(res, default=J))
