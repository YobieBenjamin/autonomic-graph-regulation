# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''EXPLORATORY robustness check (not pre-registered): re-threshold the organism so its realized false-alarm rate on
seed-5 correct episodes is <= each competitor's realized rate, then compare in-time recall (paired bootstrap).'''
import json, sys, time, glob, numpy as np
sys.path.insert(0, 'src')
from flagship import load
from absrace import T, checkpoints, parallel_features, AbsOrganism, LengthControls
def layers(pattern, off=0):
    out = {}
    for p in sorted(glob.glob(pattern)):
        z = np.load(p); out.update({off + int(k[1:]): z[k].astype(np.float32) for k in z.files})
    return out
def eps(seed, off, L): return [dict(r, idx=off + r['idx']) for r in load('data/seed' + seed + '_L.jsonl.gz') if r['answered'] and off + r['idx'] in L]
Ld, Rd = {}, []
for s, off in (('2', 0), ('3', 100000), ('4', 200000)):
    Ls = layers('data/layers_seed' + s + '_*.npz', off); Ld.update(Ls); Rd += eps(s, off, Ls)
Lt = layers('data/layers_seed5_*.npz'); Rt = eps('5', 0, Lt)
PJ = {(d['idx'], int(d['f'])): d for d in load('data/prefix_judge_abs_s5.jsonl.gz')}
Rt = [r for r in Rt if all((r['idx'], t) in PJ for t in checkpoints(r))]; y = np.array([0 if r['correct'] else 1 for r in Rt])
jobs = [(r, t) for r in Rd for t in checkpoints(r)]; O = AbsOrganism().fit_from(parallel_features(jobs, Ld, 4), jobs); C = LengthControls().fit(Rd)
M = {m: np.full(len(Rt), -np.inf) for m in ('organism', 'judge', 'length_C1')}
for i, r in enumerate(Rt):
    lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
    for t in checkpoints(r):
        tc = float(lat[:t].sum()); t1 = time.perf_counter(); so = O.score(r, Lt[r['idx']], t); co = time.perf_counter() - t1
        for m, s, c in (('organism', so, co), ('judge', PJ[(r['idx'], t)]['score'], PJ[(r['idx'], t)]['compute_s']), ('length_C1', C.c1(r, t), 0.0)):
            if tc + c <= D and s > M[m][i]: M[m][i] = s
def fire(v, fpr):
    c = np.sort(np.where(np.isfinite(v[y == 0]), v[y == 0], -1e9))
    for q in np.unique(c)[::-1]:
        pass
    cand = sorted(set(np.where(np.isfinite(v), v, -1e9)))
    best = None
    for thr in cand:
        f = (v > thr) & np.isfinite(v)
        if f[y == 0].mean() <= fpr + 1e-12: best = f; break
    return best if best is not None else np.zeros(len(v), bool)
def std_fire(v):
    c = v[y == 0]; thr = float(np.quantile(np.where(np.isfinite(c), c, -1e9), 0.90)); return (v > thr) & np.isfinite(v)
g = np.random.default_rng(0); w = np.where(y == 1)[0]; out = {}
for comp in ('judge', 'length_C1'):
    fc = std_fire(M[comp]); fpr = float(fc[y == 0].mean()); fo = fire(M['organism'], fpr)
    A, B = fo.astype(float), fc.astype(float); dd = [A[j].mean() - B[j].mean() for j in (g.choice(w, len(w)) for _ in range(1000))]
    out[comp] = dict(competitor_fpr=round(fpr, 4), competitor_caught=int(fc[y == 1].sum()), organism_fpr=round(float(fo[y == 0].mean()), 4), organism_caught=int(fo[y == 1].sum()),
                     diff_ci=[round(float(A[w].mean() - B[w].mean()), 4), round(float(np.percentile(dd, 2.5)), 4), round(float(np.percentile(dd, 97.5)), 4)])
json.dump(out, open('docs/exploratory_equal_fpr.json', 'w'), indent=1); print(json.dumps(out))
