# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0031 confirmatory analysis, exactly per docs/PREREGISTRATION.md (commit b177662). Derive on seed 2; test once on seed 3.'''
import json, os, sys, time, glob, numpy as np
sys.path.insert(0, 'src')
from flagship import load, auroc, paired_diff
from deep import DeepOrganism
from aiews import AIEWS, VITALS_V2, LEVELS, vitals_v2
from race import F, checkpoint_token, times
from scipy.stats import mannwhitneyu
def layers(pattern):
    out = {}
    for p in sorted(glob.glob(pattern)):
        z = np.load(p); out.update({int(k[1:]): z[k].astype(float) for k in z.files})
    return out
R2 = [r for r in load('data/seed2_L.jsonl.gz') if r['answered']]; L2 = layers('data/layers_seed2_*.npz')
R3a = [r for r in load('data/seed3_L.jsonl.gz') if r['answered']]; L3 = layers('data/layers_seed3_*.npz')
J = {m['idx']: m for m in load('data/monitors_judge.jsonl.gz')}; SC = {m['idx']: m for m in load('data/monitors_selfcons.jsonl.gz')}
PJ = {(d['idx'], d['f']): d for d in load('data/prefix_judge.jsonl.gz')}; PS = {(d['idx'], d['f']): d for d in load('data/prefix_selfcons.jsonl.gz')}
R2 = [r for r in R2 if r['idx'] in L2]
R3 = [r for r in R3a if r['idx'] in L3 and r['idx'] in J and r['idx'] in SC and all((r['idx'], f) in PJ and (r['idx'], f) in PS for f in F)]
y2 = np.array([0 if r['correct'] else 1 for r in R2]); y = np.array([0 if r['correct'] else 1 for r in R3])
# ---- derivation (seed 2 only) ----
Od = DeepOrganism().fit(R2, L2)
e = np.concatenate([np.array(r['entropy'][:max(r['final_start'], 2)]) for r in R2 if r['correct']]); cal = (float(np.median(e)), float(np.percentile(e, 75) - np.percentile(e, 25)) or 1.0)
V2 = np.array([vitals_v2(r, L2[r['idx']], hpa_cal=cal) for r in R2]); A = AIEWS().fit(V2, y2)
# ---- test (seed 3, touched once) ----
od = np.array([Od.score(L3[r['idx']], r) for r in R3])
ews = [A.score(vitals_v2(r, L3[r['idx']], hpa_cal=cal)) for r in R3]; S = np.array([s[0] for s in ews], float); lv = [s[1] for s in ews]
B1 = np.array([(J[r['idx']]['b1_p_wrong'] if J[r['idx']]['b1_p_wrong'] is not None else 50) / 100 for r in R3]); B2 = np.array([SC[r['idx']]['b2_disagree'] for r in R3])
B3 = np.array([1 - min(r['p_top1'][min(r['final_start'], len(r['p_top1']) - 1):] or [1]) for r in R3])
def ci(s, yy=None):
    yy = y if yy is None else yy; g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(yy), len(yy))
        if 0 < yy[i].sum() < len(i): b.append(auroc(yy[i], s[i]))
    return [round(float(auroc(yy, s)), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
res = dict(derivation_answered=len(R2), derivation_wrong=int(y2.sum()), test_answered=len(R3), test_wrong=int(y.sum()),
           deviation=['hunch field (YB-0027) listed as a monitor but not implemented; no hypothesis depends on it'])
# ---- H1: real-time race at matched 10% false alarms ----
M = {m: np.full(len(R3), -np.inf) for m in ('deep_organism', 'judge_prefix', 'selfcons_prefix', 'aiews_v2')}; spare = {m: {} for m in M}; ctime = {m: [] for m in M}
for i, r in enumerate(R3):
    for f in F:
        k = checkpoint_token(r['final_start'], f); t, d = times(r['latency'], r['final_start'], k)
        t0 = time.perf_counter(); s_o = Od.score(L3[r['idx']], r, upto=k); c_o = time.perf_counter() - t0
        t0 = time.perf_counter(); s_a = float(A.score(vitals_v2(r, L3[r['idx']], upto=max(k, 2), hpa_cal=cal))[0]); c_a = time.perf_counter() - t0
        for m, s, c in (('deep_organism', s_o, c_o), ('aiews_v2', s_a, c_a), ('judge_prefix', PJ[(r['idx'], f)]['score'], PJ[(r['idx'], f)]['compute_s']),
                        ('selfcons_prefix', PS[(r['idx'], f)]['score'], PS[(r['idx'], f)]['compute_s'])):
            ctime[m].append(c)
            if t + c <= d and s > M[m][i]: M[m][i] = s; spare[m][i] = d - (t + c)
fired = {}; race = {}
for m, v in M.items():
    c = v[y == 0]; thr = float(np.quantile(np.where(np.isfinite(c), c, -1e9), 0.90)); f_ = (v > thr) & np.isfinite(v); fired[m] = f_
    lead = [spare[m][i] for i in np.where(f_ & (y == 1))[0]]
    race[m] = dict(recall_in_time=round(float(f_[y == 1].mean()), 4), caught=int((f_ & (y == 1)).sum()), false_alarm_rate=round(float(f_[y == 0].mean()), 4),
                   median_seconds_to_spare=round(float(np.median(lead)), 3) if lead else None, median_compute_s=round(float(np.median(ctime[m])), 5))
best = max(('judge_prefix', 'selfcons_prefix'), key=lambda b: fired[b][y == 1].mean())
g = np.random.default_rng(0); w = np.where(y == 1)[0]; a, b = fired['deep_organism'].astype(float), fired[best].astype(float); dd = []
for _ in range(1000):
    j = g.choice(w, len(w)); dd.append(a[j].mean() - b[j].mean())
d1 = [round(float(a[w].mean() - b[w].mean()), 4), round(float(np.percentile(dd, 2.5)), 4), round(float(np.percentile(dd, 97.5)), 4)]
res['H1_realtime_race'] = dict(monitors=race, best_behavior=best, deep_minus_best_recall=d1, verdict='SUPERIOR' if d1[1] > 0 else ('inferior' if d1[2] < 0 else 'not distinguishable'))
# ---- H2: accuracy (full answers) ----
res['H2_accuracy'] = dict(auroc=dict(deep_organism=ci(od), llm_judge=ci(B1), self_consistency=ci(B2), answer_confidence=ci(B3), aiews_v2=ci(S)),
                          deep_minus_judge=paired_diff(y, od, B1), deep_minus_selfcons=paired_diff(y, od, B2))
for k in ('deep_minus_judge', 'deep_minus_selfcons'):
    d = res['H2_accuracy'][k]; res['H2_accuracy'][k + '_verdict'] = 'superior' if d[1] > 0 else ('inferior' if d[2] < 0 else 'not distinguishable')
# ---- H3: AI-EWS v2 ----
lr = {L: [int(sum(1 for q, t in zip(lv, y) if q == L and t)), int(sum(1 for q in lv if q == L))] for L in LEVELS}; rates = [v[0] / v[1] for v in lr.values() if v[1]]
res['H3_aiews_v2'] = dict(levels={L: dict(wrong=v[0], episodes=v[1], rate=round(v[0] / v[1], 4) if v[1] else None) for L, v in lr.items()},
                          ordered=all(p <= q for p, q in zip(rates, rates[1:])), auroc=ci(S), holds=all(p <= q for p, q in zip(rates, rates[1:])) and ci(S)[1] > 0.5)
# ---- H4: silent slips ----
slip = np.array([r['cat'] in ('mul_easy', 'mul_hard', 'modpow') for r in R3]); thr = np.quantile(od[y == 0], 0.9); caught = od > thr; ws = np.where(slip & (y == 1))[0]
bs = [caught[g.choice(ws, len(ws))].mean() for _ in range(1000)] if len(ws) else [0]
res['H4_silent_slips'] = dict(slip_errors=len(ws), recall=round(float(caught[ws].mean()), 4) if len(ws) else None, ci=[round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
                              holds=bool(len(ws)) and caught[ws].mean() > 0.25 and np.percentile(bs, 2.5) > 0.10)
# ---- H5: settling ----
v8 = np.array([vitals_v2(r, L3[r['idx']], hpa_cal=cal)[7] for r in R3]); alt = 'greater' if A.direction[7] > 0 else 'less'
p5 = float(mannwhitneyu(v8[y == 1], v8[y == 0], alternative=alt).pvalue)
res['H5_failure_to_settle'] = dict(direction_from_seed2=int(A.direction[7]), median_wrong=round(float(np.median(v8[y == 1])), 4), median_correct=round(float(np.median(v8[y == 0])), 4), p=round(p5, 6), holds=p5 < 0.05)
res['EUREKA'] = res['H1_realtime_race']['verdict'] == 'SUPERIOR'
os.makedirs('docs', exist_ok=True); J = lambda o: o.item() if hasattr(o, 'item') else str(o)
json.dump(res, open('docs/results.json', 'w'), indent=1, default=J); print(json.dumps(res, indent=1, default=J))
