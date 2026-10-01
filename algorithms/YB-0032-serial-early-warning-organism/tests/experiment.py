# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0032, exactly per docs/PREREGISTRATION.md (commit f0fe5cc). DRY_RUN=1: small derivation subset, seed 3 as a stand-in
test (already analyzed data), writes docs/dryrun.json only; seed 4 is never read in a dry run.'''
import json, os, sys, time, glob, numpy as np
sys.path.insert(0, 'src')
from flagship import load, auroc, paired_diff
from deep import deep_features
from serial import SerialOrganism, SerialAIEWS, parallel_features, STAGES, stage_k
from race import F, checkpoint_token, times
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
DRY = os.environ.get('DRY_RUN') == '1'; J = lambda o: o.item() if hasattr(o, 'item') else str(o)
def layers(pattern):
    out = {}
    for p in sorted(glob.glob(pattern)):
        z = np.load(p); out.update({int(k[1:]): z[k].astype(np.float32) for k in z.files})
    return out
if DRY:
    Rd = [r for r in load('data/seed2_L.jsonl.gz') if r['answered']][:300]; Ld = layers('data/layers_seed2_0.npz'); Rd = [r for r in Rd if r['idx'] in Ld]
    Rt = [r for r in load('data/seed3_L.jsonl.gz') if r['answered']][:120]; Lt = layers('data/layers_seed3_*.npz'); pj, ps = 'data/prefix_judge_s3.jsonl.gz', 'data/prefix_selfcons_s3.jsonl.gz'
else:
    Rd = [r for s in ('2', '3') for r in load('data/seed' + s + '_L.jsonl.gz') if r['answered']]
    Ld = layers('data/layers_seed2_*.npz'); L3 = layers('data/layers_seed3_*.npz')
    Rd = [dict(r, idx=r['idx']) for r in Rd]
    # seeds 2 and 3 share index ranges: key layers by (seed, idx) via an offset
    R2 = [r for r in load('data/seed2_L.jsonl.gz') if r['answered'] and r['idx'] in Ld]
    R3 = [dict(r, idx=100000 + r['idx']) for r in load('data/seed3_L.jsonl.gz') if r['answered'] and r['idx'] in L3]
    Ld.update({100000 + k: v for k, v in L3.items()}); Rd = R2 + R3
    Rt = [r for r in load('data/seed4_L.jsonl.gz') if r['answered']]; Lt = layers('data/layers_seed4_*.npz'); pj, ps = 'data/prefix_judge_s4.jsonl.gz', 'data/prefix_selfcons_s4.jsonl.gz'
PJ = {(d['idx'], d['f']): d for d in load(pj)}; PS = {(d['idx'], d['f']): d for d in load(ps)}
Rt = [r for r in Rt if r['idx'] in Lt and all((r['idx'], f) in PJ and (r['idx'], f) in PS for f in F)]
yd = np.array([0 if r['correct'] else 1 for r in Rd]); y = np.array([0 if r['correct'] else 1 for r in Rt])
t0 = time.time(); jobs = [(r, c) for r in Rd for c in STAGES]; X = parallel_features(jobs, Ld, 4); feat_min = round((time.time() - t0) / 60, 1)
S = SerialOrganism().fit_from(X, jobs)
full = np.array([c == 1.0 for _, c in jobs]); Xr = X[full][:, :-1]; cats = [r['cat'] for r, c in jobs if c == 1.0]
st = {k: (Xr[[i for i, q in enumerate(cats) if q == k]].mean(0), Xr[[i for i, q in enumerate(cats) if q == k]].std(0)) for k in set(cats)}
zr = lambda x, k: (x - st[k][0]) / np.where(st[k][1] > 0, st[k][1], 1)
ref = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(np.array([zr(x, k) for x, k in zip(Xr, cats)]), yd)
ref_score = lambda r, L, k: float(ref.predict_proba(zr(deep_features(L, r['final_start'], upto=k, prepped=True), r['cat'])[None, :])[0, 1])
e = np.concatenate([np.array(r['entropy'][:max(r['final_start'], 2)]) for r in Rd if r['correct']]); cal = (float(np.median(e)), float(np.percentile(e, 75) - np.percentile(e, 25)) or 1.0)
E = SerialAIEWS().fit(Rd, Ld, cal)
M = {m: np.full(len(Rt), -np.inf) for m in ('serial_organism', 'reference_complete', 'aiews_v3', 'judge_prefix', 'selfcons_prefix')}; spare = {m: {} for m in M}; ctime = {m: [] for m in M}
for i, r in enumerate(Rt):
    L = Lt[r['idx']]
    for f in F:
        k = checkpoint_token(r['final_start'], f); t, d = times(r['latency'], r['final_start'], k)
        t1 = time.perf_counter(); so = S.score(r, L, f); c1 = time.perf_counter() - t1
        t1 = time.perf_counter(); rf = ref_score(r, L, k); c2 = time.perf_counter() - t1
        t1 = time.perf_counter(); ae = float(E.score(r, L, f)[0]); c3 = time.perf_counter() - t1
        for m, s, c in (('serial_organism', so, c1), ('reference_complete', rf, c2), ('aiews_v3', ae, c3),
                        ('judge_prefix', PJ[(r['idx'], f)]['score'], PJ[(r['idx'], f)]['compute_s']), ('selfcons_prefix', PS[(r['idx'], f)]['score'], PS[(r['idx'], f)]['compute_s'])):
            ctime[m].append(c)
            if t + c <= d and s > M[m][i]: M[m][i] = s; spare[m][i] = d - (t + c)
fired, race = {}, {}
for m, v in M.items():
    c = v[y == 0]; thr = float(np.quantile(np.where(np.isfinite(c), c, -1e9), 0.90)); f_ = (v > thr) & np.isfinite(v); fired[m] = f_
    lead = [spare[m][i] for i in np.where(f_ & (y == 1))[0]]
    race[m] = dict(recall_in_time=round(float(f_[y == 1].mean()), 4) if y.sum() else None, caught=int((f_ & (y == 1)).sum()), false_alarm_rate=round(float(f_[y == 0].mean()), 4),
                   median_seconds_to_spare=round(float(np.median(lead)), 3) if lead else None, median_compute_s=round(float(np.median(ctime[m])), 5))
g = np.random.default_rng(0); w = np.where(y == 1)[0]
def rdiff(a, b):
    a, b = fired[a].astype(float), fired[b].astype(float); dd = [a[j].mean() - b[j].mean() for j in (g.choice(w, len(w)) for _ in range(1000))]
    return [round(float(a[w].mean() - b[w].mean()), 4), round(float(np.percentile(dd, 2.5)), 4), round(float(np.percentile(dd, 97.5)), 4)]
best = max(('judge_prefix', 'selfcons_prefix'), key=lambda b: fired[b][y == 1].mean())
d1 = rdiff('serial_organism', best); d2 = rdiff('serial_organism', 'reference_complete')
lvl = {c: [E.score(r, Lt[r['idx']], c)[1] for r in Rt] for c in STAGES}; LV = ['stable', 'watch', 'concern', 'urgent']
def ordered(c):
    rates = [np.mean([y[i] for i in range(len(Rt)) if lvl[c][i] == L]) for L in LV if sum(1 for q in lvl[c] if q == L) >= 5]; return all(a <= b for a, b in zip(rates, rates[1:]))
ae_boot = [fired['aiews_v3'][g.choice(w, len(w))].mean() for _ in range(1000)]
s100 = np.array([S.score(r, Lt[r['idx']], 1.0) for r in Rt]); r100 = np.array([ref_score(r, Lt[r['idx']], r['final_start']) for r in Rt]); d4 = paired_diff(y, s100, r100)
slip = np.array([r['cat'] in ('mul_easy', 'mul_hard', 'modpow') for r in Rt]); ws = np.where(slip & (y == 1))[0]
sb = [fired['serial_organism'][g.choice(ws, len(ws))].mean() for _ in range(1000)] if len(ws) else [0]
res = dict(dry_run=DRY, derivation_answered=len(Rd), derivation_wrong=int(yd.sum()), serial_observations=len(jobs), feature_minutes=feat_min, test_answered=len(Rt), test_wrong=int(y.sum()),
           H1_race=dict(monitors=race, best_behavior=best, serial_minus_best=d1, verdict='SUPERIOR' if d1[1] > 0 else ('inferior' if d1[2] < 0 else 'not distinguishable')),
           H2_serial_minus_reference=dict(diff=d2, holds=d2[1] > 0),
           H3_aiews_v3=dict(levels_by_stage={str(c): {L: [int(sum(1 for i in range(len(Rt)) if lvl[c][i] == L and y[i])), int(sum(1 for q in lvl[c] if q == L))] for L in LV} for c in STAGES},
                            ordered_every_stage=all(ordered(c) for c in STAGES), in_time_recall_ci=[round(float(np.percentile(ae_boot, 2.5)), 4), round(float(np.percentile(ae_boot, 97.5)), 4)],
                            holds=all(ordered(c) for c in STAGES) and np.percentile(ae_boot, 2.5) > 0),
           H4_auroc_at_100=dict(serial=round(float(auroc(y, s100)), 4), reference=round(float(auroc(y, r100)), 4), diff=d4, holds=d4[2] >= 0),
           H5_slips_in_time=dict(slip_errors=len(ws), recall=round(float(fired['serial_organism'][ws].mean()), 4) if len(ws) else None, ci=[round(float(np.percentile(sb, 2.5)), 4), round(float(np.percentile(sb, 97.5)), 4)],
                                 holds=bool(len(ws)) and fired['serial_organism'][ws].mean() > 0.20 and np.percentile(sb, 2.5) > 0.05),
           per_stage_auroc={m: {str(c): round(float(auroc(y, np.array([S.score(r, Lt[r['idx']], c) if m == 'serial' else ref_score(r, Lt[r['idx']], stage_k(r, c)) for r in Rt]))), 4) for c in STAGES} for m in ('serial', 'reference')})
res['EUREKA'] = (not DRY) and res['H1_race']['verdict'] == 'SUPERIOR'
os.makedirs('docs', exist_ok=True); out = 'docs/dryrun.json' if DRY else 'docs/results.json'
json.dump(res, open(out, 'w'), indent=1, default=J); print(json.dumps(res, indent=1, default=J)[:3000])
