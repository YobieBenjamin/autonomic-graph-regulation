# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0012 flagship, executed exactly as docs/PREREGISTRATION.md (committed bd83719 before analysis).'''
import json, os, sys, numpy as np
sys.path.insert(0, 'src')
from flagship import load, Organism, HPAOrganism, auroc, paired_diff
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
R0 = [r for r in load('data/seed0.jsonl.gz') if r['answered']]
R1 = [r for r in load('data/seed1.jsonl.gz') if r['answered']]
J = {m['idx']: m for m in load('data/monitors_judge.jsonl.gz')}; SC = {m['idx']: m for m in load('data/monitors_selfcons.jsonl.gz')}
R1 = [r for r in R1 if r['idx'] in J and r['idx'] in SC]
y = np.array([0 if r['correct'] else 1 for r in R1])
O = Organism().fit(R0); H = HPAOrganism().fit(R0)
S = dict(O_organism=np.array([O.score(r) for r in R1]), O_hpa=np.array([H.score(r) for r in R1]),
         B1_llm_judge=np.array([(J[r['idx']]['b1_p_wrong'] if J[r['idx']]['b1_p_wrong'] is not None else 50) / 100 for r in R1]),
         B2_self_consistency=np.array([SC[r['idx']]['b2_disagree'] for r in R1]),
         B3_answer_confidence=np.array([1 - min(r['p_top1'][min(r['final_start'], len(r['p_top1']) - 1):] or [1]) for r in R1]))
def ci(s):
    g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): b.append(auroc(y[i], s[i]))
    return [round(float(auroc(y, s)), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
def recall10(s, thr=None):
    thr = np.quantile(s[y == 0], 0.9) if thr is None else thr; return round(float((s[y == 1] > thr).mean()), 4)
res = dict(n=len(y), failures=int(y.sum()), seed0_train_episodes=len(R0), auroc_ci95={k: ci(v) for k, v in S.items()},
           recall_at_10fpr={k: recall10(v) for k, v in S.items()}, organism_recall_at_frozen_seed0_threshold=recall10(S['O_organism'], O.threshold))
B = ['B1_llm_judge', 'B2_self_consistency', 'B3_answer_confidence']; best = max(B, key=lambda k: auroc(y, S[k]))
res['paired_O_minus_B'] = {b: paired_diff(y, S['O_organism'], S[b]) for b in B}
res['paired_OHPA_minus_B'] = {b: paired_diff(y, S['O_hpa'], S[b]) for b in B}
d = res['paired_O_minus_B'][best]
res['H1_verdict_vs_best_behavior'] = dict(best_behavior=best, diff_ci=d, verdict='superior' if d[1] > 0 else ('inferior' if d[2] < 0 else 'not distinguishable'))
X = np.column_stack([S['O_organism'], S[best]])
comb = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method='predict_proba')[:, 1]
d3 = paired_diff(y, comb, S[best]); res['H3_O_plus_best_vs_best'] = dict(diff_ci=d3, holds=d3[1] > 0)
leads, lead_ms, detected = [], [], 0
for k, r in enumerate(R1):
    if not y[k] or S['O_organism'][k] <= O.threshold: continue
    detected += 1; fs = r['final_start']; alarm = None
    for t in range(16, fs + 1, 8):
        if O.score(r, upto=t) > O.threshold: alarm = t; break
    alarm = fs if alarm is None else alarm; leads.append(fs - alarm); lead_ms.append(1000 * sum(r['latency'][alarm:fs]))
res['H2_lead_time'] = dict(errors_detected_at_frozen_threshold=detected, median_lead_tokens=float(np.median(leads)) if leads else None,
                           median_lead_ms=round(float(np.median(lead_ms)), 1) if lead_ms else None,
                           share_alarm_before_answer=round(float(np.mean([l > 0 for l in leads])), 4) if leads else None,
                           holds=bool(leads) and float(np.median(leads)) > 0, behavior_monitors_lead='<= 0 by construction (need the completed answer)')
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
