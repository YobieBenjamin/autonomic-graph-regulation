# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0047 analysis (pre-registered; docs/PREREGISTRATION.md). Part A: internal state vs a TRAINED text monitor on the same reasoning prefixes.
Part B: leave-one-task-out transfer. Secondary analysis of YB-0045 recordings (test seeds 9, 13, 14 previously analysed). DRY_RUN=1 fits on seeds
2-8 and evaluates on 10-12 only.'''
import json, gzip, os, sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, parallel_features, AbsOrganism
from corrected import in_time_max, boot_diff, evaluate
from probe import Probe, select
from textmon import TextMonitor, select_C
from sklearn.metrics import roc_auc_score
COST, T, DRY = 0.005, (48, 96, 192, 384), os.environ.get('DRY_RUN') == '1'
DERIV = ('2', '3', '4', '5', '6', '7', '8', '10', '11', '12'); TEST = ('9', '13', '14')
if DRY: DERIV, TEST = ('2', '3', '4', '5', '6', '7', '8'), ('10', '11', '12')
SMOKE = os.environ.get('SMOKE') == '1'   # fast end-to-end check of every code path: 2 training seeds, 1 eval seed, 150 episodes each; never reads test seeds
if SMOKE: DRY, DERIV, TEST = True, ('2', '3'), ('10',)
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]
def load_seed(S, off):
    R = [dict(r, idx=off + r['idx']) for r in ld('data/seed%s_LH.jsonl.gz' % S)]
    if SMOKE: R = R[:150]
    z = np.load('data/layers_LH_seed%s_0.npz' % S); L = {off + int(k[1:]): z[k].astype(np.float32) for k in z.files}
    h = np.load('data/hs_seed%s.npz' % S); H = {}
    for k in h.files:
        i, rest = k[1:].split('_', 1); H.setdefault(off + int(i), {})[rest] = h[k]
    return R, L, H
def in_time(R, fn, cost):
    V = []
    for r in R:
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
        V.append(in_time_max([(fn(r, t), float(lat[:t].sum()), cost(r, t), D) for t in checkpoints(r)]))
    return np.array(V)
def boot_auc(y, s, n=1000, seed=0):
    s = np.where(np.isfinite(s), s, -1e6)   # episodes with no in-time checkpoint are never alarmed: lowest score (pre-registered rule)
    g = np.random.default_rng(seed); a = []
    for _ in range(n):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(y): a.append(roc_auc_score(y[i], s[i]))
    return [round(float(roc_auc_score(y, s)), 4), round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]
def main():
    if not DRY and os.environ.get('RUN_CONFIRMATORY') != '1':
        print('pre-registration stage: the confirmatory analysis runs only via make confirmatory, after the public timestamp'); return
    if not all(os.path.exists('data/seed%s_LH.jsonl.gz' % S) for S in DERIV + TEST):
        print('YB-0045 recordings not present (public checkout): nothing to analyse'); return
    Rd, Ld, Hd = [], {}, {}
    for S in DERIV:
        R, L, H = load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
    R8, L8, H8 = [], {}, {}
    for S in TEST:
        R, L, H = load_seed(S, 100000 * int(S)); R8 += R; L8.update(L); H8.update(H)
    Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]
    X = parallel_features(jobs, Ld, 4); O = AbsOrganism().fit_from(X, jobs)
    (bl, bc), _ = select(jobs, Hd); P = Probe(bl, bc).fit(jobs, Hd)
    Ct, ctab = select_C(jobs); TM = TextMonitor(Ct).fit(jobs)
    ok = lambda r: r['idx'] in L8 and all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r))
    A = [r for r in R8 if r['answered'] and ok(r)]; y = np.array([0 if r['correct'] else 1 for r in A]); mon = np.array([len(checkpoints(r)) > 0 for r in A])
    fixed = lambda r, t: COST
    V = dict(regulator=in_time(A, lambda r, t: O.score(r, L8[r['idx']], t), fixed), probe=in_time(A, lambda r, t: P.score(r, t, H8), fixed),
             text_trained=in_time(A, lambda r, t: TM.score(r, t), fixed))
    per = {m: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in evaluate(v_, y, mon).items() if k != 'fired'} for m, v_ in V.items()}
    h1 = boot_diff(V['probe'], V['text_trained'], y); h2 = boot_diff(V['regulator'], V['text_trained'], y)
    res = dict(dry_run=DRY, deriv_seeds=DERIV, eval_seeds=TEST, derivation_answered=len(Rd), derivation_observations=len(jobs), probe_selected=dict(layer=bl, C=bc),
               text_C=Ct, text_cv_auroc=ctab, eval_answered=len(A), eval_wrong=int(y.sum()), monitors=per,
               H1_probe_minus_text=h1, H1_supported=bool(h1[1] > 0), H2_regulator_minus_text=h2, H2_supported=bool(h2[1] > 0))
    pc = {}
    for t in T:
        idx = [i for i, r in enumerate(A) if t in checkpoints(r)]
        if len(idx) < 20 or y[idx].sum() < 3: continue
        yt = y[idx]; pc[str(t)] = dict(episodes=len(idx), wrong=int(yt.sum()), auroc_with_ci=dict(
            regulator=boot_auc(yt, np.array([O.score(A[i], L8[A[i]['idx']], t) for i in idx])), probe=boot_auc(yt, np.array([P.score(A[i], t, H8) for i in idx])),
            text_trained=boot_auc(yt, np.array([TM.score(A[i], t) for i in idx]))))
    res['S_per_checkpoint_auroc'] = pc
    # Part B: leave-one-task-out transfer (H3). For each held-out category, refit all three monitors without it; score its evaluation episodes.
    lo = {m: np.full(len(A), np.nan) for m in ('regulator', 'probe', 'text_trained')}; cats = sorted(set(r['cat'] for r in A)); detail = {}
    for c in cats:
        tr = [i for i, (r, _) in enumerate(jobs) if r['cat'] != c]; jt = [jobs[i] for i in tr]
        Oc = AbsOrganism().fit_from(X[tr], jt); Pc = Probe(bl, bc).fit(jt, Hd); Tc = TextMonitor(Ct).fit(jt)
        # label-free normalisation for the unseen type: per-(type, t) feature statistics from its derivation episodes, no labels used
        hc = [i for i, (r, _) in enumerate(jobs) if r['cat'] == c]; jc = [jobs[i] for i in hc]; kc = [(r['cat'], t) for r, t in jc]
        norm_used = len(jc) > 0
        Xp = Pc._design(jc, Hd) if norm_used else None
        for k in (set(kc) if norm_used else ()):
            m = np.array([kk == k for kk in kc]); Oc.stats[k] = (X[hc][m].mean(0), X[hc][m].std(0)); Pc.stats[k] = (Xp[m].mean(0), Xp[m].std(0) + 1e-6)
        ii = [i for i, r in enumerate(A) if r['cat'] == c]; sub = [A[i] for i in ii]
        for m, f in (('regulator', lambda r, t: Oc.score(r, L8[r['idx']], t)), ('probe', lambda r, t: Pc.score(r, t, H8)), ('text_trained', lambda r, t: Tc.score(r, t))):
            lo[m][ii] = in_time(sub, f, fixed)
        yc = y[ii]; detail[c] = dict(episodes=len(ii), wrong=int(yc.sum()), label_free_normalisation=norm_used, derivation_episodes=len(set(r['idx'] for r, _ in jc)))
        if 10 <= yc.sum() < len(yc):
            detail[c]['heldout_auroc'] = {m: boot_auc(yc, lo[m][ii]) for m in lo}; detail[c]['in_task_auroc'] = {m: boot_auc(yc, V[m][ii]) for m in lo}
    keep = [i for i, r in enumerate(A) if detail[r['cat']]['wrong'] >= 1]
    pooled = {m: boot_auc(y[keep], lo[m][keep]) for m in lo}
    res['H3_pooled_leave_one_task_out_auroc'] = pooled; res['H3_supported_probe'] = bool(pooled['probe'][1] > 0.5)
    res['H3_supported_regulator'] = bool(pooled['regulator'][1] > 0.5); res['S_transfer_by_task'] = detail
    out = 'docs/smoke.json' if SMOKE else ('docs/dryrun.json' if DRY else 'docs/results.json')
    json.dump(res, open(out, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print(json.dumps({k: res[k] for k in ('eval_answered', 'eval_wrong', 'text_C', 'H1_probe_minus_text', 'H1_supported', 'H2_regulator_minus_text', 'H2_supported', 'H3_pooled_leave_one_task_out_auroc')}, default=str))
if __name__ == '__main__': main()
