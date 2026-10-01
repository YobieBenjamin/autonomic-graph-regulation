# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''EXPLORATORY (third audit M5, m2). (1) A type-by-length baseline that uses only what the regulator receives besides
telemetry: the question type and the elapsed token count. Score at checkpoint t = derivation failure rate among episodes
of the same type still reasoning at t (seeds 2-4). Same race rules as the primary analysis (seed 7, answered, <= 10% of
correct episodes alarmed, zero compute cost). (2) Self-consistency compute time per prefix check from committed data.
Writes docs/exploratory_audit3.json.'''
import json, gzip, sys, numpy as np
sys.path.insert(0, 'src')
from corrected import in_time_max, cap_threshold
T = (48, 96, 192, 384)
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]
D = [r for s in ('2', '3', '4') for r in ld('data/seed%s_L.jsonl.gz' % s) if r['answered']]
rate = {}
for c in set(r['cat'] for r in D):
    for t in T:
        m = [r for r in D if r['cat'] == c and t < r['final_start']]
        rate[(c, t)] = float(np.mean([0 if r['correct'] else 1 for r in m])) if m else 0.0
PJ = {(d['idx'], int(d['f'])) for d in ld('data/prefix_judge_abs_s7.jsonl.gz')}
R = [r for r in ld('data/seed7_L.jsonl.gz') if r['answered'] and all((r['idx'], t) in PJ for t in T if t < r['final_start'])]
y = np.array([0 if r['correct'] else 1 for r in R]); V = []
for r in R:
    lat = np.asarray(r['latency'], float); Dl = float(lat[:r['final_start']].sum())
    V.append(in_time_max([(rate[(r['cat'], t)], float(lat[:t].sum()), 0.0, Dl) for t in T if t < r['final_start']]))
V = np.array(V); thr = cap_threshold(V[y == 0]); f = V > thr
S = [d['compute_s'] for d in ld('data/prefix_selfcons_abs_s7.jsonl.gz')]
res = dict(note='EXPLORATORY', type_by_length_baseline=dict(answered=len(y), wrong=int(y.sum()), caught=int((f & (y == 1)).sum()), fpr=round(float(f[y == 0].mean()), 4), threshold=thr),
           selfcons_compute_s=dict(checks=len(S), median=round(float(np.median(S)), 2), p90=round(float(np.percentile(S, 90)), 2)))
json.dump(res, open('docs/exploratory_audit3.json', 'w'), indent=1); print(json.dumps(res))
