'''Phase C artifacts (audit F16, F21; self S3). Run from the repo root: .venv/bin/python archive/audit/artifacts/baselines_and_breakdowns.py
Writes archive/audit/artifacts/baselines_and_breakdowns.json. Uses only committed data.'''
import json, gzip, sys, numpy as np
from sklearn.metrics import roc_auc_score
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]
out = {}
def baselines(train, test, name, organism_auroc):
    '''Question-type baseline: derivation failure rate of the episode's type. Length baseline: reasoning length (final_start).'''
    y = np.array([0 if r['correct'] else 1 for r in test]); rate = {}
    for c in set(r['cat'] for r in train):
        m = [r for r in train if r['cat'] == c]; rate[c] = np.mean([0 if r['correct'] else 1 for r in m])
    typ = np.array([rate.get(r['cat'], 0.0) for r in test]); L = np.array([r['final_start'] for r in test], float)
    out[name] = dict(test_answered=len(test), wrong=int(y.sum()), organism_auroc_reported=organism_auroc,
                     question_type_baseline_auroc=round(float(roc_auc_score(y, typ)), 4), length_baseline_auroc=round(float(roc_auc_score(y, L)), 4),
                     type_plus_length_rank_auroc=round(float(roc_auc_score(y, typ * 1e4 + L)), 4))
F = 'algorithms/YB-0012-vitals-vs-behavior-flagship/data/'
s0 = [r for r in ld(F + 'seed0.jsonl.gz') if r['answered']]; s1 = [r for r in ld(F + 'seed1.jsonl.gz') if r['answered']]
for n, a in (('YB-0012 (seed 1)', 0.720), ('YB-0019 (seed 1)', 0.765), ('YB-0030 (seed 1)', 0.725)): baselines(s0, s1, n, a)
G = 'algorithms/YB-0031-confirmatory-deep-program/data/'
baselines([r for r in ld(G + 'seed2_L.jsonl.gz') if r['answered']], [r for r in ld(G + 'seed3_L.jsonl.gz') if r['answered']], 'YB-0031 (seed 3)', 0.890)
# F21: YB-0032 length-only control, reproducibly (seed 4 test, derivation seeds 2+3, answered episodes with all 3 fractional checkpoints judged)
H = 'algorithms/YB-0032-serial-early-warning-organism/data/'
D = [r for s in ('2', '3') for r in ld(H + 'seed%s_L.jsonl.gz' % s) if r['answered']]
PJ = {(d['idx'], d['f']) for d in ld(H + 'prefix_judge_s4.jsonl.gz')}
T = [r for r in ld(H + 'seed4_L.jsonl.gz') if r['answered'] and all((r['idx'], f) in PJ for f in (0.25, 0.5, 0.75))]
y = np.array([0 if r['correct'] else 1 for r in T]); L = np.array([r['final_start'] for r in T], float)
ref = {c: np.sort([r['final_start'] for r in D if r['cat'] == c and r['correct']]) for c in set(r['cat'] for r in D)}
pct = np.array([np.searchsorted(ref[r['cat']], r['final_start']) / len(ref[r['cat']]) for r in T])
def caught(s):
    thr = np.quantile(s[y == 0], 0.9); f = s > thr; return int((f & (y == 1)).sum()), round(float(f[y == 0].mean()), 4)
out['YB-0032 length-only control'] = dict(test_answered=len(T), wrong=int(y.sum()), raw_length_auroc=round(float(roc_auc_score(y, L)), 4), raw_length_caught_and_fpr=caught(L),
    within_type_percentile_auroc=round(float(roc_auc_score(y, pct)), 4), within_type_percentile_caught_and_fpr=caught(pct),
    note='Previously reported (ad hoc): raw 0.773, 15/46; within-type 0.578, 11/46. This script is the reproducible record.')
# S3: YB-0012 per-type breakdown of the token organism at its frozen seed-0 threshold
sys.path.insert(0, 'algorithms/YB-0012-vitals-vs-behavior-flagship/src')
from flagship import Organism
O = Organism().fit(s0); caughtd = {}
for r in s1:
    if r['correct']: continue
    c = caughtd.setdefault(r['cat'], [0, 0]); c[0] += 1; c[1] += int(O.score(r) > O.threshold)
out['YB-0012 per-type breakdown (errors, caught at frozen threshold)'] = caughtd
json.dump(out, open('archive/audit/artifacts/baselines_and_breakdowns.json', 'w'), indent=1); print(json.dumps(out, indent=1))
