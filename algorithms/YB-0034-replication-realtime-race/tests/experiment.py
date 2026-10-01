# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0033, exactly per docs/PREREGISTRATION.md (YB-0034 pre-registration; design identical to YB-0033 (300f037)). DRY_RUN=1: derivation subset, seed-4 stand-in test with
seeded random stand-in behavior scores; writes docs/dryrun.json; never reads seed 5.'''
import json, os, sys, time, glob, numpy as np
sys.path.insert(0, 'src')
from flagship import load, auroc
from absrace import T, checkpoints, parallel_features, AbsOrganism, AbsAIEWS, LengthControls
DRY = os.environ.get('DRY_RUN') == '1'; J = lambda o: o.item() if hasattr(o, 'item') else str(o)
def layers(pattern, off=0):
    out = {}
    for p in sorted(glob.glob(pattern)):
        z = np.load(p); out.update({off + int(k[1:]): z[k].astype(np.float32) for k in z.files})
    return out
def eps(seed, off, L):
    return [dict(r, idx=off + r['idx']) for r in load('data/seed' + seed + '_L.jsonl.gz') if r['answered'] and off + r['idx'] in L]
if DRY:
    Ld = layers('data/layers_seed2_0.npz'); Rd = eps('2', 0, Ld)[:300]
    Lt = layers('data/layers_seed4_*.npz', 400000); Rt = eps('4', 400000, Lt)[:150]
    g0 = np.random.default_rng(1)
    PJ = {(r['idx'], t): dict(score=float(g0.random()), compute_s=1.5) for r in Rt for t in checkpoints(r)}
    PS = {(r['idx'], t): dict(score=float(g0.random() < 0.1), compute_s=2.4) for r in Rt for t in checkpoints(r)}
else:
    Ld = {}; Rd = []
    for s, off in (('2', 0), ('3', 100000), ('4', 200000)):
        Ls = layers('data/layers_seed' + s + '_*.npz', off); Ld.update(Ls); Rd += eps(s, off, Ls)
    Lt = layers('data/layers_seed6_*.npz'); Rt = eps('6', 0, Lt)
    PJ = {(d['idx'], int(d['f'])): d for d in load('data/prefix_judge_abs_s6.jsonl.gz')}; PS = {(d['idx'], int(d['f'])): d for d in load('data/prefix_selfcons_abs_s6.jsonl.gz')}
Rt = [r for r in Rt if all((r['idx'], t) in PJ and (r['idx'], t) in PS for t in checkpoints(r))]
yd = np.array([0 if r['correct'] else 1 for r in Rd]); y = np.array([0 if r['correct'] else 1 for r in Rt])
jobs = [(r, t) for r in Rd for t in checkpoints(r)]; t0 = time.time(); X = parallel_features(jobs, Ld, 4); fmin = round((time.time() - t0) / 60, 1)
O = AbsOrganism().fit_from(X, jobs)
e = np.concatenate([np.array(r['entropy'][:max(r['final_start'], 2)]) for r in Rd if r['correct']]); cal = (float(np.median(e)), float(np.percentile(e, 75) - np.percentile(e, 25)) or 1.0)
E = AbsAIEWS().fit(Rd, Ld, cal); C = LengthControls().fit(Rd)
names = ('organism', 'aiews_v4', 'length_C1', 'length_C2', 'judge_prefix', 'selfcons_prefix')
M = {m: np.full(len(Rt), -np.inf) for m in names}; spare = {m: {} for m in names}; ctime = {m: [] for m in names}; perck = {m: {t: [] for t in T} for m in names}; yck = {t: [] for t in T}
for i, r in enumerate(Rt):
    L = Lt[r['idx']]; lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
    for t in checkpoints(r):
        tc = float(lat[:t].sum()); yck[t].append(y[i]); vals = {}
        for m, fn in (('organism', lambda: O.score(r, L, t)), ('aiews_v4', lambda: float(E.score(r, L, t)[0])), ('length_C1', lambda: C.c1(r, t)), ('length_C2', lambda: C.c2(r, t))):
            t1 = time.perf_counter(); v = fn(); vals[m] = (v, time.perf_counter() - t1)
        vals['judge_prefix'] = (PJ[(r['idx'], t)]['score'], PJ[(r['idx'], t)]['compute_s']); vals['selfcons_prefix'] = (PS[(r['idx'], t)]['score'], PS[(r['idx'], t)]['compute_s'])
        for m, (s, c) in vals.items():
            ctime[m].append(c); perck[m][t].append(s)
            if tc + c <= D and s > M[m][i]: M[m][i] = s; spare[m][i] = D - (tc + c)
fired, race = {}, {}
for m, v in M.items():
    c = v[y == 0]; thr = float(np.quantile(np.where(np.isfinite(c), c, -1e9), 0.90)); f_ = (v > thr) & np.isfinite(v); fired[m] = f_
    lead = [spare[m][i] for i in np.where(f_ & (y == 1))[0]]
    race[m] = dict(caught=int((f_ & (y == 1)).sum()), recall_in_time=round(float(f_[y == 1].mean()), 4) if y.sum() else None, false_alarm_rate=round(float(f_[y == 0].mean()), 4),
                   median_seconds_to_spare=round(float(np.median(lead)), 3) if lead else None, median_compute_s=round(float(np.median(ctime[m])), 5) if ctime[m] else None)
g = np.random.default_rng(0)
def rdiff(a, b, sub=None):
    w = np.where((y == 1) & (sub if sub is not None else True))[0]
    if len(w) == 0: return [None, None, None]
    A, B = fired[a].astype(float), fired[b].astype(float); dd = [A[j].mean() - B[j].mean() for j in (g.choice(w, len(w)) for _ in range(1000))]
    return [round(float(A[w].mean() - B[w].mean()), 4), round(float(np.percentile(dd, 2.5)), 4), round(float(np.percentile(dd, 97.5)), 4)]
best_b = max(('judge_prefix', 'selfcons_prefix'), key=lambda b: fired[b][y == 1].mean()); best_c = max(('length_C1', 'length_C2'), key=lambda b: fired[b][y == 1].mean())
d_b, d_c = rdiff('organism', best_b), rdiff('organism', best_c); d_e = rdiff('aiews_v4', best_c)
lenfree = []
for cat in sorted(set(r['cat'] for r in Rd)):
    m = [r for r in Rd if r['cat'] == cat]; yy = np.array([0 if r['correct'] else 1 for r in m])
    if 0 < yy.sum() < len(yy) and auroc(yy, np.array([r['final_start'] for r in m], float)) < 0.6: lenfree.append(cat)
sub = np.array([r['cat'] in lenfree for r in Rt]); d3 = rdiff('organism', best_b, sub)
slip = np.array([r['cat'] in ('mul_easy', 'mul_hard', 'modpow') for r in Rt])
res = dict(dry_run=DRY, derivation_answered=len(Rd), derivation_wrong=int(yd.sum()), serial_observations=len(jobs), feature_minutes=fmin, test_answered=len(Rt), test_wrong=int(y.sum()),
           test_wrong_with_any_checkpoint=int(sum(1 for i, r in enumerate(Rt) if y[i] and checkpoints(r))), race=race, best_behavior=best_b, best_length_control=best_c,
           H1=dict(organism_minus_best_behavior=d_b, organism_minus_best_length=d_c, holds=bool(d_b[1] is not None and d_b[1] > 0 and d_c[1] > 0)),
           H2=dict(aiews_minus_best_length=d_e, holds=bool(d_e[1] is not None and d_e[1] > 0)),
           H3=dict(length_free_types=lenfree, wrong_in_subset=int((sub & (y == 1)).sum()), organism_minus_best_behavior=d3, holds=bool(d3[1] is not None and d3[1] > 0)),
           per_checkpoint_auroc={m: {str(t): (round(float(auroc(np.array(yck[t]), np.array(perck[m][t]))), 4) if 0 < sum(yck[t]) < len(yck[t]) else None) for t in T} for m in names},
           per_checkpoint_n={str(t): [int(sum(yck[t])), len(yck[t])] for t in T},
           silent_slip_recall_in_time={m: round(float(fired[m][slip & (y == 1)].mean()), 4) if (slip & (y == 1)).any() else None for m in names})
res['EUREKA'] = (not DRY) and res['H1']['holds']
os.makedirs('docs', exist_ok=True); out = 'docs/dryrun.json' if DRY else 'docs/results.json'
json.dump(res, open(out, 'w'), indent=1, default=J); print(json.dumps(res, indent=1, default=J)[:2500])
