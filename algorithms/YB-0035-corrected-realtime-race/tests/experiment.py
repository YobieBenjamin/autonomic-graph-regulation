# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0035 corrected real-time race, per docs/PREREGISTRATION.md (committed with this code before seed 7 exists).
Primary: seed 7 (fixed tap, answered episodes). Sensitivity (F5): seed 7 incl. never-answered as failures.
Secondary: seeds 5 and 6 re-analysed on realigned data; pooled 5+6+7 (R3). DRY_RUN=1: plumbing check on derivation data.'''
import json, os, sys, glob, numpy as np
sys.path.insert(0, 'src')
from flagship import load, auroc
from absrace import T, checkpoints, parallel_features, AbsOrganism, AbsAIEWS, LengthControls
from corrected import FIXED_COST, in_time_max, first_crossing_spare, evaluate, boot_diff, cap_threshold
DRY = os.environ.get('DRY_RUN') == '1'; J = lambda o: o.item() if hasattr(o, 'item') else str(o)
if not DRY and not os.path.exists('data/seed7_L.jsonl.gz'):
    print('YB-0035: awaiting seed 7 test data (pre-registration stage); nothing to analyse yet.'); sys.exit(0)
def layers(pattern, off=0):
    out = {}
    for p in sorted(glob.glob(pattern)):
        z = np.load(p); out.update({off + int(k[1:]): z[k].astype(np.float32) for k in z.files})
    return out
def eps(seed, off, L, answered_only=True):
    return [dict(r, idx=off + r['idx']) for r in load('data/seed' + seed + '_L.jsonl.gz') if (r['answered'] or not answered_only) and off + r['idx'] in L]
# ---- derivation (seeds 2-4, realigned, answered) ----
Ld, Rd = {}, []
for s, off in ((('2', 0),) if DRY else (('2', 0), ('3', 100000), ('4', 200000))):
    Ls = layers('data/layers_seed' + s + '_0.npz' if DRY else 'data/layers_seed' + s + '_*.npz', off); Ld.update(Ls); Rd += eps(s, off, Ls)
if DRY: Rd = Rd[:300]
jobs = [(r, t) for r in Rd for t in checkpoints(r)]; O = AbsOrganism().fit_from(parallel_features(jobs, Ld, 4), jobs)
e = np.concatenate([np.array(r['entropy'][:max(r['final_start'], 2)]) for r in Rd if r['correct']]); cal = (float(np.median(e)), float(np.percentile(e, 75) - np.percentile(e, 25)) or 1.0)
E = AbsAIEWS().fit(Rd, Ld, cal); C = LengthControls().fit(Rd)
NAMES = ('organism', 'aiews_v4', 'length_C1', 'length_C2', 'judge_prefix', 'selfcons_prefix')
def analyse(R, L, PJ, PS, label):
    y = np.array([0 if (r['answered'] and r['correct']) else 1 for r in R]); checks = {m: [] for m in NAMES}; perck = {m: {t: [] for t in T} for m in ('organism', 'judge_prefix')}; yck = {t: [] for t in T}
    for i, r in enumerate(R):
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum()) if r['answered'] else float(lat.sum())
        row = {m: [] for m in NAMES}
        for t in checkpoints(r):
            tc = float(lat[:t].sum()); yck[t].append(y[i])
            so = O.score(r, L[r['idx']], t); perck['organism'][t].append(so)
            vals = dict(organism=(so, FIXED_COST['organism']), aiews_v4=(float(E.score(r, L[r['idx']], t)[0]), FIXED_COST['aiews_v4']),
                        length_C1=(C.c1(r, t), 0.0), length_C2=(C.c2(r, t), 0.0))
            for m, P in (('judge_prefix', PJ), ('selfcons_prefix', PS)):
                d = P.get((r['idx'], t)); vals[m] = (d['score'], d['compute_s']) if d else (-np.inf, 0.0)
            perck['judge_prefix'][t].append(vals['judge_prefix'][0])
            for m, (s, c) in vals.items(): row[m].append((s, tc, c, D))
        for m in NAMES: checks[m].append(row[m])
    V = {m: np.array([in_time_max(c) for c in checks[m]]) for m in NAMES}; mon = np.array([len(checkpoints(r)) > 0 for r in R])
    ev = {m: evaluate(V[m], y, mon) for m in NAMES}
    out = dict(label=label, episodes=len(R), wrong=int(y.sum()), monitorable_wrong=int((mon & (y == 1)).sum()), monitorable_correct=int((mon & (y == 0)).sum()), monitors={})
    for m in NAMES:
        sp = [first_crossing_spare(checks[m][i], ev[m]['threshold']) for i in np.where(ev[m]['fired'] & (y == 1))[0]]; sp = [x for x in sp if x is not None]
        out['monitors'][m] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ev[m].items() if k != 'fired'}
        out['monitors'][m]['median_seconds_to_spare_first_crossing'] = round(float(np.median(sp)), 3) if sp else None
    bb = max(('judge_prefix', 'selfcons_prefix'), key=lambda b: ev[b]['recall'] or 0); bc = max(('length_C1', 'length_C2'), key=lambda b: ev[b]['recall'] or 0)
    d1, d2 = boot_diff(V['organism'], V[bb], y), boot_diff(V['organism'], V[bc], y)
    out.update(best_behavior=bb, best_length=bc, organism_minus_best_behavior=d1, organism_minus_best_length=d2, H1_holds=bool(d1[1] > 0 and d2[1] > 0),
               aiews_minus_best_length=boot_diff(V['aiews_v4'], V[bc], y),
               per_checkpoint_auroc={m: {str(t): (round(float(auroc(np.array(yck[t]), np.array(perck[m][t]))), 4) if 0 < sum(yck[t]) < len(yck[t]) else None) for t in T} for m in perck})
    return out, V, y
def behavior(seed):
    f = lambda k: {(d['idx'], int(d['f'])): d for d in load('data/prefix_%s_abs_s%s.jsonl.gz' % (k, seed))}
    return f('judge'), f('selfcons')
res = dict(dry_run=DRY, derivation_answered=len(Rd), derivation_wrong=int(sum(0 if r['correct'] else 1 for r in Rd)), fixed_compute_cost_s=FIXED_COST)
if DRY:
    L4 = layers('data/layers_seed4_*.npz'); R4 = eps('4', 0, L4)[:150]; g = np.random.default_rng(1)
    PJ = {(r['idx'], t): dict(score=float(g.random()), compute_s=1.5) for r in R4 for t in checkpoints(r)}; PS = {(r['idx'], t): dict(score=float(g.random() < 0.1), compute_s=2.4) for r in R4 for t in checkpoints(r)}
    res['dry'], _, _ = analyse(R4, L4, PJ, PS, 'dry run (seed-4 stand-in, random behavior scores)')
else:
    L7 = layers('data/layers_seed7_*.npz'); PJ7, PS7 = behavior('7')
    res['primary_seed7'], V7, y7 = analyse(eps('7', 0, L7), L7, PJ7, PS7, 'PRIMARY: seed 7, fixed tap, answered episodes')
    res['sensitivity_seed7_incl_unanswered'], _, _ = analyse(eps('7', 0, L7, answered_only=False), L7, PJ7, PS7, 'SENSITIVITY (F5): seed 7 incl. never-answered as failures')
    pool_V, pool_y = [V7], [y7]
    for s in ('5', '6'):
        Ls = layers('data/layers_seed%s_*.npz' % s); PJs, PSs = behavior(s)
        res['secondary_seed' + s], Vs, ys = analyse(eps(s, 0, Ls), Ls, PJs, PSs, 'SECONDARY: seed %s, realigned, answered' % s); pool_V.append(Vs); pool_y.append(ys)
    Vp = {m: np.concatenate([v[m] for v in pool_V]) for m in NAMES}; yp = np.concatenate(pool_y)
    bb = max(('judge_prefix', 'selfcons_prefix'), key=lambda b: float((Vp[b] > cap_threshold(Vp[b][yp == 0]))[yp == 1].mean()))
    bc = max(('length_C1', 'length_C2'), key=lambda b: float((Vp[b] > cap_threshold(Vp[b][yp == 0]))[yp == 1].mean()))
    res['R3_pooled_5_6_7'] = dict(episodes=len(yp), wrong=int(yp.sum()), best_behavior=bb, best_length=bc,
                                  organism_minus_best_behavior=boot_diff(Vp['organism'], Vp[bb], yp), organism_minus_best_length=boot_diff(Vp['organism'], Vp[bc], yp))
    res['CONFIRMED'] = res['primary_seed7']['H1_holds']
os.makedirs('docs', exist_ok=True); out = 'docs/dryrun.json' if DRY else 'docs/results.json'
json.dump(res, open(out, 'w'), indent=1, default=J); print(json.dumps(res, indent=1, default=J)[:2500])
