# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0017 experiment. The HPA organism receives per-token stress drive computed from the same recorded vitals as
YB-0015 (answered episodes only; ground truth computed, no LLM judge). Stress drive = positive part of the z-score
of a channel against CORRECT calibration episodes (2-fold split by index parity; no leakage).
Pre-registered (2026-09-28, before analysis), author's prediction: the organism and the raw signals differ in
variance but trend the same way -> Spearman rho(organism peak cortisol, raw accumulated drive) > 0.7 per tier.
Also reported: AUROC of peak cortisol vs raw scores, alarm-band occupancy, and an oscillation sweep over feedback steepness n.'''
import gzip, json, os, sys, numpy as np
sys.path.insert(0, 'src')
from hpa import simulate
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
R = [r for r in (json.loads(l) for l in gzip.open('data/episodes.jsonl.gz', 'rt')) if r['answered']]
y = np.array([0 if r['correct'] else 1 for r in R]); idx = np.array([r['idx'] for r in R])
CH = {'tier2_entropy': lambda r: np.array(r['entropy']), 'tier0_latency': lambda r: np.array(r['latency'][1:] or [0.0])}
def ci(s):
    g = np.random.default_rng(0); b = []
    for _ in range(1000):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i): b.append(roc_auc_score(y[i], s[i]))
    return [round(roc_auc_score(y, s), 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]
res = dict(n=len(y), failures=int(y.sum()), tiers={})
for name, get in CH.items():
    peak, final, raw_sum, raw_mean = np.zeros(len(R)), np.zeros(len(R)), np.zeros(len(R)), np.zeros(len(R))
    for fold in (0, 1):
        cal = [get(r) for r, i, yy in zip(R, idx, y) if i % 2 == fold and yy == 0]
        v = np.concatenate(cal); mu, sd = np.median(v), (np.percentile(v, 75) - np.percentile(v, 25)) or 1.0
        for k, r in enumerate(R):
            if idx[k] % 2 == fold: continue
            S = np.maximum((get(r) - mu) / sd, 0); H, A, C = simulate(S)
            peak[k], final[k], raw_sum[k], raw_mean[k] = C.max(), C[-1], S.sum(), S.mean()
    rho = spearmanr(peak, raw_sum).correlation
    cv = lambda a: round(float(a.std() / a.mean()), 4) if a.mean() else None
    bands = np.digitize(peak, np.quantile(peak[y == 0], [0.5, 0.9, 0.99]))
    res['tiers'][name] = dict(auroc_ci95=dict(organism_peak_cortisol=ci(peak), organism_final_cortisol=ci(final), raw_accumulated_drive=ci(raw_sum), raw_mean_drive=ci(raw_mean)),
        trend_hypothesis=dict(spearman_rho_peak_vs_raw=round(float(rho), 4), predicted='> 0.7', holds=bool(rho > 0.7)),
        variance=dict(cv_organism=cv(peak), cv_raw=cv(raw_sum)),
        alarm_bands_failures=np.bincount(bands[y == 1], minlength=4).tolist(), alarm_bands_correct=np.bincount(bands[y == 0], minlength=4).tolist())
sweep = {}
for n in (1, 2, 4, 8, 16, 32):
    C = simulate(np.full(6000, 3.0), dict(n=float(n)))[2][-2000:]; sweep[str(n)] = round(float(C.std() / C.mean()), 6)
res['oscillation_sweep_cv_late_cortisol_by_n'] = sweep
os.makedirs('docs', exist_ok=True); json.dump(res, open('docs/results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
