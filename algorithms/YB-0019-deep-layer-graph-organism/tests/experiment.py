# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0019 experiment, exactly as docs/PREREGISTRATION.md (commit 5c9b9fb, before analysis).'''
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from flagship import load, Organism, auroc, paired_diff
from deep import DeepOrganism
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
def layers(p): z = np.load(p); return {int(k[1:]): z[k].astype(float) for k in z.files}
R0 = [r for r in load('data/seed0_L.jsonl.gz') if r['answered']]; L0 = layers('data/layers_seed0.npz')
orig1 = {r['idx']: r for r in load('data/seed1_original.jsonl.gz')}
J = {m['idx']: m for m in load('data/monitors_judge.jsonl.gz')}; SC = {m['idx']: m for m in load('data/monitors_selfcons.jsonl.gz')}
L1 = layers('data/layers_seed1.npz'); R1all = [r for r in load('data/seed1_L.jsonl.gz') if r['answered'] and r['idx'] in J and r['idx'] in SC]
same = lambda r: r['idx'] in orig1 and orig1[r['idx']]['final'] == r['final'] and orig1[r['idx']]['n_tokens'] == r['n_tokens']
R1 = [r for r in R1all if same(r)]; mismatched = [r['idx'] for r in R1all if not same(r)]
y = np.array([0 if r['correct'] else 1 for r in R1])
Ot = Organism().fit(R0); Od = DeepOrganism().fit(R0, L0)
S = dict(O_deep=np.array([Od.score(L1[r['idx']], r) for r in R1]), O_token=np.array([Ot.score(r) for r in R1]),
         B1_llm_judge=np.array([(J[r['idx']]['b1_p_wrong'] if J[r['idx']]['b1_p_wrong'] is not None else 50) / 100 for r in R1]),
         B2_self_consistency=np.array([SC[r['idx']]['b2_disagree'] for r in R1]),
         B3_answer_confidence=np.array([1 - min(r['p_top1'][min(r['final_start'], len(r['p_top1']) - 1):] or [1]) for r in R1]))
def ci(s):
    g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): b.append(auroc(y[i], s[i]))
    return [round(float(auroc(y, s)), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
res = dict(n=len(y), failures=int(y.sum()), train_episodes=len(R0), deviation_excluded_nonidentical_rerecording=mismatched,
           auroc_ci95={k: ci(v) for k, v in S.items()},
           recall_at_10fpr={k: round(float((v[y == 1] > np.quantile(v[y == 0], 0.9)).mean()), 4) for k, v in S.items()})
d0 = paired_diff(y, S['O_deep'], S['O_token']); res['H0_deeper_helps'] = dict(diff_ci=d0, holds=d0[1] > 0)
B = ['B1_llm_judge', 'B2_self_consistency', 'B3_answer_confidence']; best = max(B, key=lambda k: auroc(y, S[k]))
res['paired_Odeep_minus_B'] = {b: paired_diff(y, S['O_deep'], S[b]) for b in B}
d = res['paired_Odeep_minus_B'][best]
res['H1_vs_best_behavior'] = dict(best=best, diff_ci=d, verdict='superior' if d[1] > 0 else ('inferior' if d[2] < 0 else 'not distinguishable'))
comb = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)), np.column_stack([S['O_deep'], S[best]]), y,
                         cv=StratifiedKFold(5, shuffle=True, random_state=0), method='predict_proba')[:, 1]
d3 = paired_diff(y, comb, S[best]); res['H3_Odeep_plus_best_vs_best'] = dict(diff_ci=d3, holds=d3[1] > 0)
leads, ms = [], []
for k, r in enumerate(R1):
    if not y[k] or S['O_deep'][k] <= Od.threshold: continue
    t = Od.alarm(L1[r['idx']], r); t = r['final_start'] if t is None else t
    leads.append(r['final_start'] - t); ms.append(1000 * sum(orig1[r['idx']]['latency'][t:r['final_start']]))
res['H2_lead_time'] = dict(errors_detected=len(leads), median_lead_tokens=float(np.median(leads)) if leads else None,
                           median_lead_ms=round(float(np.median(ms)), 1) if ms else None,
                           share_before_answer=round(float(np.mean([l > 0 for l in leads])), 4) if leads else None, holds=bool(leads) and float(np.median(leads)) > 0)
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1)
json.dump({str(r['idx']): dict(O_deep=float(S['O_deep'][k]), O_token=float(S['O_token'][k]), y=int(y[k])) for k, r in enumerate(R1)}, open('docs/scores_seed1.json', 'w'))
print(json.dumps(res, indent=1))
