# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0023 real-time race, per docs/PREREGISTRATION.md (5c9b9fb) and docs/SPEC_NOTES.md (committed before any run).
Primary (R2, deadline): recall of wrong answers alarmed before the answer is emitted, compute time included.
Secondary (R1, information-matched): AUROC per checkpoint, compute time ignored.'''
import json, os, sys, time, numpy as np
sys.path.insert(0, 'src')
from flagship import load, Organism, auroc
from deep import DeepOrganism
from race import F, checkpoint_token, times, first_valid
def layers(p): z = np.load(p); return {int(k[1:]): z[k].astype(float) for k in z.files}
R0 = [r for r in load('data/seed0_L.jsonl.gz') if r['answered']]; L0 = layers('data/layers_seed0.npz'); L1 = layers('data/layers_seed1.npz')
orig = {r['idx']: r for r in load('data/seed1_original.jsonl.gz')}
PJ = {(d['idx'], d['f']): d for d in load('data/prefix_judge.jsonl.gz')}; PS = {(d['idx'], d['f']): d for d in load('data/prefix_selfcons.jsonl.gz')}
R1 = [r for r in load('data/seed1_L.jsonl.gz') if r['answered'] and all((r['idx'], f) in PJ and (r['idx'], f) in PS for f in F) and r['idx'] in L1]
y = np.array([0 if r['correct'] else 1 for r in R1])
Ot = Organism().fit(R0); Od = DeepOrganism().fit(R0, L0)
score = {m: {f: np.zeros(len(R1)) for f in F} for m in ('O_deep', 'O_token', 'B1_judge_prefix', 'B2_selfcons_prefix')}
comp = {m: {f: np.zeros(len(R1)) for f in F} for m in score}
for i, r in enumerate(R1):
    for f in F:
        k = checkpoint_token(r['final_start'], f)
        t0 = time.perf_counter(); score['O_deep'][f][i] = Od.score(L1[r['idx']], r, upto=k); comp['O_deep'][f][i] = time.perf_counter() - t0
        t0 = time.perf_counter(); score['O_token'][f][i] = Ot.score(r, upto=k); comp['O_token'][f][i] = time.perf_counter() - t0
        score['B1_judge_prefix'][f][i] = PJ[(r['idx'], f)]['score']; comp['B1_judge_prefix'][f][i] = PJ[(r['idx'], f)]['compute_s']
        score['B2_selfcons_prefix'][f][i] = PS[(r['idx'], f)]['score']; comp['B2_selfcons_prefix'][f][i] = PS[(r['idx'], f)]['compute_s']
thr = {'O_deep': {f: Od.threshold for f in F}, 'O_token': {f: Ot.threshold for f in F}}
for b in ('B1_judge_prefix', 'B2_selfcons_prefix'): thr[b] = {f: float(np.quantile(score[b][f][y == 0], 0.9)) for f in F}
fired = {m: np.zeros(len(R1), bool) for m in score}; alarm_lead = {m: [] for m in score}
for i, r in enumerate(R1):
    lat = orig[r['idx']]['latency']
    for m in score:
        checks = []
        for f in F:
            k = checkpoint_token(r['final_start'], f); t, d = times(lat, r['final_start'], k); checks.append((f, score[m][f][i], thr[m][f], t, comp[m][f][i], d))
        ok, f, at = first_valid(checks); fired[m][i] = ok
        if ok and y[i]: alarm_lead[m].append(checks[0][5] - at)
def boot_diff(a, b, n=1000):
    g = np.random.default_rng(0); d = []; w = np.where(y == 1)[0]
    for _ in range(n):
        j = g.choice(w, len(w)); d.append(a[j].mean() - b[j].mean())
    return [round(float(a[w].mean() - b[w].mean()), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]
R2 = {m: dict(recall_before_deadline=round(float(fired[m][y == 1].mean()), 4), false_alarm_rate_any_checkpoint=round(float(fired[m][y == 0].mean()), 4),
              median_seconds_before_answer=round(float(np.median(alarm_lead[m])), 3) if alarm_lead[m] else None,
              median_compute_s=round(float(np.median(np.concatenate([comp[m][f] for f in F]))), 5)) for m in score}
best = max(('B1_judge_prefix', 'B2_selfcons_prefix'), key=lambda b: fired[b][y == 1].mean())
d = boot_diff(fired['O_deep'].astype(float), fired[best].astype(float))
res = dict(n=len(y), failures=int(y.sum()), R2_deadline=R2, thresholds={m: {str(f): round(v, 4) for f, v in thr[m].items()} for m in thr},
           H1_RT=dict(organism='O_deep', best_behavior=best, recall_diff_ci=d, verdict='organism wins' if d[1] > 0 else ('behavior wins' if d[2] < 0 else 'not distinguishable')),
           R1_information_matched_auroc={m: {str(f): round(float(auroc(y, score[m][f])), 4) for f in F} for m in score})
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
