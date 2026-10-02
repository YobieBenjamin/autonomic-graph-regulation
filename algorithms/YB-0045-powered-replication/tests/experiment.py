# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0045 analysis (pre-registered; see docs/PREREGISTRATION.md). Derivation: seeds 2-8 and 10-12 except 9, recorded with telemetry and
hidden states in the same pass. Test: fresh seeds 9, 13, 14 (pooled). Exits cleanly if any test seed is absent. DRY_RUN=1 runs the full pipeline
on synthetic data (docs/dryrun.json).'''
import json, gzip, os, sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, parallel_features, AbsOrganism
from corrected import in_time_max, cap_threshold, boot_diff, evaluate
from probe import Probe, select, cv_auroc, C_GRID
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
COST, T, DRY = 0.005, (48, 96, 192, 384), os.environ.get('DRY_RUN') == '1'
DERIV = ('2', '3', '4', '5', '6', '7', '8', '10', '11', '12'); TEST = ('9', '13', '14')
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]

def load_seed(S, off):
    R = [dict(r, idx=off + r['idx']) for r in ld('data/seed%s_LH.jsonl.gz' % S)]
    z = np.load('data/layers_LH_seed%s_0.npz' % S); L = {off + int(k[1:]): z[k].astype(np.float32) for k in z.files}
    h = np.load('data/hs_seed%s.npz' % S); H = {}
    for k in h.files:
        i, rest = k[1:].split('_', 1); H.setdefault(off + int(i), {})[rest] = h[k]
    return R, L, H

def synth(n, off, rng, d=24):
    R, L, H, J = [], {}, {}, {}
    for i in range(n):
        idx = off + i; cat = ['mul_hard', 'weekday', 'modpow'][i % 3]; wrong = rng.random() < 0.15; fs = int(rng.integers(20, 500))
        lat = [0.02] * (fs + 20); R.append(dict(idx=idx, cat=cat, correct=not wrong, answered=True, final_start=fs, n_tokens=fs + 20, latency=lat))
        X = rng.normal(size=(fs, 24, 5)).astype(np.float32); X[:, 10, 4] += 0.8 * wrong; L[idx] = X; e = {}
        for t in T:
            if t < fs:
                last = rng.normal(size=(4, d)); mean = rng.normal(size=(4, d)); last[2, 0] += 1.0 * wrong
                e['last_%d' % t] = last.astype(np.float16); e['mean_%d' % t] = mean.astype(np.float16)
                J[(idx, t)] = dict(score=float(np.clip(0.5 + 0.2 * wrong + rng.normal(0, 0.2), 0, 1)), compute_s=1.5)
        H[idx] = e
    return R, L, H, J

def in_time(R, fn, cost):
    V = []
    for r in R:
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
        V.append(in_time_max([(fn(r, t), float(lat[:t].sum()), cost(r, t), D) for t in checkpoints(r)]))
    return np.array(V)

def verdict(ci):
    return 'regulator better' if ci[1] > 0 else ('probe better' if ci[2] < 0 else 'not distinguishable')

def boot_auc(y, s, n=1000, seed=0):
    g = np.random.default_rng(seed); a = []
    for _ in range(n):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(y): a.append(roc_auc_score(y[i], s[i]))
    return [round(float(roc_auc_score(y, s)), 4), round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]

def main():
    if DRY:
        rng = np.random.default_rng(1); Rd, Ld, Hd = [], {}, {}
        for k in range(3):
            R, L, H, _ = synth(150, 100000 * (k + 2), rng); Rd += R; Ld.update(L); Hd.update(H)
        R8, L8, H8, PJ = synth(200, 800000, rng)
    else:
        if not all(os.path.exists('data/seed%s_LH.jsonl.gz' % S) for S in TEST):
            print('test seeds not recorded yet: nothing to analyse (pre-registration stage)'); return
        Rd, Ld, Hd = [], {}, {}
        for S in DERIV:
            R, L, H = load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
        R8, L8, H8, PJ = [], {}, {}, {}
        for S in TEST:
            R, L, H = load_seed(S, 100000 * int(S)); R8 += R; L8.update(L); H8.update(H)
            PJ.update({(100000 * int(S) + d['idx'], int(d['f'])): d for d in ld('data/prefix_judge_abs_s%s.jsonl.gz' % S)})
    Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]
    X = parallel_features(jobs, Ld, 4); O = AbsOrganism().fit_from(X, jobs)
    (bl, bc), table = select(jobs, Hd); P = Probe(bl, bc).fit(jobs, Hd)
    all_tab = {C: cv_auroc(jobs, Hd, 'all', C)[0] for C in C_GRID}; Ca = max(all_tab, key=lambda c: (all_tab[c], -c)); PA = Probe('all', Ca).fit(jobs, Hd)
    rate = {c: float(np.mean([0 if r['correct'] else 1 for r in Rd if r['cat'] == c])) for c in set(r['cat'] for r in Rd)}
    ok = lambda r: r['idx'] in L8 and all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r)) and (PJ is None or all((r['idx'], t) in PJ for t in checkpoints(r)))
    A = [r for r in R8 if r['answered'] and ok(r)]; y = np.array([0 if r['correct'] else 1 for r in A]); mon = np.array([len(checkpoints(r)) > 0 for r in A])
    fixed = lambda r, t: COST
    V = dict(regulator=in_time(A, lambda r, t: O.score(r, L8[r['idx']], t), fixed), probe=in_time(A, lambda r, t: P.score(r, t, H8), fixed),
             probe_all_layers=in_time(A, lambda r, t: PA.score(r, t, H8), fixed),
             length_C1=in_time(A, lambda r, t: float(t), lambda r, t: 0.0), type_C3=in_time(A, lambda r, t: rate.get(r['cat'], 0.0), lambda r, t: 0.0))
    if PJ is not None: V['judge'] = in_time(A, lambda r, t: PJ[(r['idx'], t)]['score'], lambda r, t: PJ[(r['idx'], t)]['compute_s'])
    per = {m: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in evaluate(v_, y, mon).items() if k != 'fired'} for m, v_ in V.items()}
    h1 = boot_diff(V['regulator'], V['judge'], y) if 'judge' in V else [None, None, None]
    res = dict(dry_run=DRY, derivation_answered=len(Rd), derivation_observations=len(jobs), probe_selected=dict(layer=bl, C=bc), probe_cv_table=table,
               probe_all_layers_C=Ca, probe_all_layers_cv={str(k): round(v, 4) for k, v in all_tab.items()},
               test_answered=len(A), test_wrong=int(y.sum()), monitors=per,
               population_check=dict(answered=len(A), monitorable=int(mon.sum()), short_correct_included=int(((~mon) & (y == 0)).sum())),
               H1_regulator_minus_judge=h1, H1_supported=bool(h1[1] is not None and h1[1] > 0))
    if 'judge' in V:
        res['S_regulator_minus_probe'] = boot_diff(V['regulator'], V['probe'], y)
        res['S_probe_minus_judge'] = boot_diff(V['probe'], V['judge'], y)
    res['S_regulator_minus_probe_all_layers'] = boot_diff(V['regulator'], V['probe_all_layers'], y)
    res['S_regulator_minus_length'] = boot_diff(V['regulator'], V['length_C1'], y); res['S_regulator_minus_type'] = boot_diff(V['regulator'], V['type_C3'], y)
    ym = y[mon]; res['S_equal_fpr_monitorable'] = {m: dict(caught=int(((v[mon] > cap_threshold(v[mon][ym == 0])) & (ym == 1)).sum())) for m, v in V.items()}
    res['S_equal_fpr_regulator_minus_probe'] = boot_diff(V['regulator'][mon], V['probe'][mon], ym)
    yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); grp = np.array([r['idx'] for r, _ in jobs]); cfo, cfp = np.zeros(len(jobs)), np.zeros(len(jobs))
    for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), yj, grp):
        Ot = AbsOrganism().fit_from(X[tr], [jobs[i] for i in tr]); Pt = Probe(bl, bc).fit([jobs[i] for i in tr], Hd)
        for i in te: r, t = jobs[i]; cfo[i] = Ot.score(r, Ld[r['idx']], t); cfp[i] = Pt.score(r, t, Hd)
    mo = {(r['idx'], t): cfo[i] for i, (r, t) in enumerate(jobs)}; mp = {(r['idx'], t): cfp[i] for i, (r, t) in enumerate(jobs)}
    yd = np.array([0 if r['correct'] else 1 for r in Rd])
    fr = {}
    for m, Vd, Vt in (('regulator', in_time(Rd, lambda r, t: mo[(r['idx'], t)], fixed), V['regulator']), ('probe', in_time(Rd, lambda r, t: mp[(r['idx'], t)], fixed), V['probe'])):
        thr = cap_threshold(Vd[yd == 0]); f = Vt > thr; fr[m] = dict(caught=int((f & (y == 1)).sum()), fpr=round(float(f[y == 0].mean()), 4))
    res['S_frozen_derivation_thresholds'] = fr
    pc = {}
    for t in T:
        idx = [i for i, r in enumerate(A) if t in checkpoints(r)]
        if len(idx) < 20 or y[idx].sum() < 3: continue
        yt = y[idx]; e = {}
        e['regulator'] = boot_auc(yt, np.array([O.score(A[i], L8[A[i]['idx']], t) for i in idx])); e['probe'] = boot_auc(yt, np.array([P.score(A[i], t, H8) for i in idx]))
        e['type'] = boot_auc(yt, np.array([rate.get(A[i]['cat'], 0.0) for i in idx]))
        if PJ is not None: e['judge'] = boot_auc(yt, np.array([PJ[(A[i]['idx'], t)]['score'] for i in idx]))
        pc[str(t)] = dict(episodes=len(idx), wrong=int(yt.sum()), auroc_with_ci=e)
    res['S_per_checkpoint_auroc'] = pc
    U = [r for r in R8 if ok(r)]; yu = np.array([0 if (r['answered'] and r['correct']) else 1 for r in U])
    res['S_sensitivity_never_answered_as_failures'] = dict(episodes=len(U), failures=int(yu.sum()),
        regulator_minus_probe=boot_diff(in_time(U, lambda r, t: O.score(r, L8[r['idx']], t), fixed), in_time(U, lambda r, t: P.score(r, t, H8), fixed), yu))
    out = 'docs/dryrun.json' if DRY else 'docs/results.json'
    json.dump(res, open(out, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print(json.dumps({k: res[k] for k in ('probe_selected', 'test_answered', 'test_wrong', 'population_check', 'H1_regulator_minus_judge', 'H1_supported')}, default=str))

if __name__ == '__main__': main()
