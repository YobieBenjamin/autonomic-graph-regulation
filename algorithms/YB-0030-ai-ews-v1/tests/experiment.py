# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0030 AI-EWS v1, exactly as pre-registered in HYPOTHESES.md (commit cb72e92, before analysis).'''
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from flagship import load, auroc, paired_diff
from aiews import AIEWS, VITALS, LEVELS, vitals
from scipy.stats import mannwhitneyu
def layers(p): z = np.load(p); return {int(k[1:]): z[k].astype(float) for k in z.files}
R0 = [r for r in load('data/seed0_L.jsonl.gz') if r['answered']]; L0 = layers('data/layers_seed0.npz'); L1 = layers('data/layers_seed1.npz')
deep = json.load(open('data/deep_organism_scores_seed1.json'))
R1 = [r for r in load('data/seed1_L.jsonl.gz') if r['answered'] and str(r['idx']) in deep and r['idx'] in L1]
y0 = np.array([0 if r['correct'] else 1 for r in R0]); y1 = np.array([0 if r['correct'] else 1 for r in R1])
e = np.concatenate([np.array(r['entropy'][:max(r['final_start'], 2)]) for r in R0 if r['correct']])
cal = (float(np.median(e)), float(np.percentile(e, 75) - np.percentile(e, 25)) or 1.0)
V0 = np.array([vitals(r, L0[r['idx']], hpa_cal=cal) for r in R0]); A = AIEWS().fit(V0, y0)
F = (0.25, 0.5, 0.75, 1.0); S1 = {f: [] for f in F}; lv = []; pts = []
for r in R1:
    for f in F:
        s, l, p = A.score(vitals(r, L1[r['idx']], upto=max(int(f * r['final_start']), 2), hpa_cal=cal)); S1[f].append(s)
        if f == 1.0: lv.append(l); pts.append(p)
S = np.array(S1[1.0], float); od = np.array([deep[str(r['idx'])]['O_deep'] for r in R1])
def ci(s):
    g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(y1), len(y1))
        if 0 < y1[i].sum() < len(i): b.append(auroc(y1[i], s[i]))
    return [round(float(auroc(y1, s)), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
lvl_rate = {L: [int(sum(1 for a, b in zip(lv, y1) if a == L and b)), int(sum(1 for a in lv if a == L))] for L in LEVELS}
rates = [lvl_rate[L][0] / lvl_rate[L][1] for L in LEVELS if lvl_rate[L][1] > 0]
slope = np.array([np.polyfit(F, [S1[f][i] for f in F], 1)[0] for i in range(len(R1))])
d3 = paired_diff(y1, S, od)
res = dict(n=len(y1), failures=int(y1.sum()), derivation_n=len(y0), hpa_calibration=cal,
           derivation=dict(direction=dict(zip(VITALS, A.direction.tolist())), bands=dict(zip(VITALS, np.round(A.bands, 5).tolist()))),
           H1_auroc_ci95=ci(S), H1_holds=ci(S)[1] > 0.5,
           H2_levels_failure_rate={L: dict(failures=v[0], episodes=v[1], rate=round(v[0] / v[1], 4) if v[1] else None) for L, v in lvl_rate.items()},
           H2_monotonic=all(a <= b for a, b in zip(rates, rates[1:])),
           H3_aiews_minus_deep_organism=dict(diff_ci=d3, not_significantly_worse=d3[2] >= 0),
           H4_trajectory=dict(median_slope_failures=round(float(np.median(slope[y1 == 1])), 3), median_slope_successes=round(float(np.median(slope[y1 == 0])), 3),
                              mannwhitney_p_failures_gt_successes=round(float(mannwhitneyu(slope[y1 == 1], slope[y1 == 0], alternative='greater').pvalue), 4),
                              holds=float(np.median(slope[y1 == 1])) > 0),
           mean_score_by_checkpoint=dict(failures=[round(float(np.mean(np.array(S1[f])[y1 == 1])), 3) for f in F], successes=[round(float(np.mean(np.array(S1[f])[y1 == 0])), 3) for f in F]),
           points_most_often_raised_on_failures={v: int(sum(p[v] for p, b in zip(pts, y1) if b)) for v in VITALS})
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1)
json.dump([dict(idx=r['idx'], cat=r['cat'], wrong=int(y1[i]), S=[S1[f][i] for f in F]) for i, r in enumerate(R1)], open('docs/trajectories.json', 'w'))
print(json.dumps(res, indent=1))
