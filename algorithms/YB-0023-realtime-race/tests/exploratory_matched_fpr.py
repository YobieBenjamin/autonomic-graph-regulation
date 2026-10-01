# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''EXPLORATORY (not pre-registered; added after seeing that the pre-registered rule did not control false alarms).
Every monitor gets ONE threshold chosen so that at most 10% of CORRECT episodes receive any in-time alarm; then compare
recall of wrong answers alarmed before the deadline (compute time included). In-time score of an episode = max score over
checkpoints whose alarm would finish before the answer is emitted.'''
import json, sys, time, numpy as np
sys.path.insert(0, 'src')
from flagship import load, Organism
from deep import DeepOrganism
from race import F, checkpoint_token, times
def layers(p): z = np.load(p); return {int(k[1:]): z[k].astype(float) for k in z.files}
R0 = [r for r in load('data/seed0_L.jsonl.gz') if r['answered']]; L0 = layers('data/layers_seed0.npz'); L1 = layers('data/layers_seed1.npz')
orig = {r['idx']: r for r in load('data/seed1_original.jsonl.gz')}
PJ = {(d['idx'], d['f']): d for d in load('data/prefix_judge.jsonl.gz')}; PS = {(d['idx'], d['f']): d for d in load('data/prefix_selfcons.jsonl.gz')}
R1 = [r for r in load('data/seed1_L.jsonl.gz') if r['answered'] and all((r['idx'], f) in PJ and (r['idx'], f) in PS for f in F) and r['idx'] in L1]
y = np.array([0 if r['correct'] else 1 for r in R1]); Ot = Organism().fit(R0); Od = DeepOrganism().fit(R0, L0)
M = {m: np.full(len(R1), -np.inf) for m in ('O_deep', 'O_token', 'B1_judge_prefix', 'B2_selfcons_prefix')}; when = {m: {} for m in M}
for i, r in enumerate(R1):
    lat = orig[r['idx']]['latency']
    for f in F:
        k = checkpoint_token(r['final_start'], f); t, d = times(lat, r['final_start'], k)
        t0 = time.perf_counter(); sd = Od.score(L1[r['idx']], r, upto=k); cd = time.perf_counter() - t0
        t0 = time.perf_counter(); st = Ot.score(r, upto=k); ct = time.perf_counter() - t0
        for m, s, c in (('O_deep', sd, cd), ('O_token', st, ct), ('B1_judge_prefix', PJ[(r['idx'], f)]['score'], PJ[(r['idx'], f)]['compute_s']),
                        ('B2_selfcons_prefix', PS[(r['idx'], f)]['score'], PS[(r['idx'], f)]['compute_s'])):
            if t + c <= d and s > M[m][i]: M[m][i] = s; when[m][i] = d - (t + c)
res = {}
fired = {}
for m, v in M.items():
    c = v[y == 0]; fin = np.sort(c[np.isfinite(c)])
    thr = np.quantile(np.where(np.isfinite(c), c, -1e9), 0.90)
    fired[m] = v > thr; fired[m][~np.isfinite(v)] = False
    lead = [when[m][i] for i in np.where(fired[m] & (y == 1))[0]]
    res[m] = dict(threshold=round(float(thr), 4), false_alarm_rate=round(float(fired[m][y == 0].mean()), 4), recall_before_deadline=round(float(fired[m][y == 1].mean()), 4),
                  caught=int((fired[m] & (y == 1)).sum()), median_seconds_to_spare=round(float(np.median(lead)), 3) if lead else None)
best = max(('B1_judge_prefix', 'B2_selfcons_prefix'), key=lambda b: fired[b][y == 1].mean())
g = np.random.default_rng(0); w = np.where(y == 1)[0]; a, b = fired['O_deep'].astype(float), fired[best].astype(float); dd = []
for _ in range(1000):
    j = g.choice(w, len(w)); dd.append(a[j].mean() - b[j].mean())
res['O_deep_minus_best_behavior'] = dict(best=best, recall_diff=[round(float(a[w].mean() - b[w].mean()), 4), round(float(np.percentile(dd, 2.5)), 4), round(float(np.percentile(dd, 97.5)), 4)])
json.dump(res, open('docs/exploratory_matched_fpr.json', 'w'), indent=1); print(json.dumps(res))
