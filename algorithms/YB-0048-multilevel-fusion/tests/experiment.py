# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0048 analysis (pre-registered; docs/PREREGISTRATION.md): does a multi-level combination of non-LLM monitors beat its best single
component, and do the components catch different errors? Secondary analysis of YB-0045 recordings. DRY_RUN=1: fit on 2-8, evaluate on 10-12.
SMOKE=1: 2 training seeds, 1 eval seed, 150 episodes each. Confirmatory run only via make confirmatory (RUN_CONFIRMATORY=1).'''
import json, gzip, os, sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, parallel_features, AbsOrganism
from corrected import in_time_max, boot_diff, evaluate, cap_threshold
from probe import Probe, select
from textmon import TextMonitor
from difficulty import DifficultyBaseline
from fusion import Stack, Bands
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
COST, T, DRY = 0.005, (48, 96, 192, 384), os.environ.get('DRY_RUN') == '1'
TEXT_C = 1.0   # pre-declared: the value YB-0047 selected by derivation-only cross-validation
DERIV = ('2', '3', '4', '5', '6', '7', '8', '10', '11', '12'); TEST = ('9', '13', '14')
if DRY: DERIV, TEST = ('2', '3', '4', '5', '6', '7', '8'), ('10', '11', '12')
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE: DRY, DERIV, TEST = True, ('2', '3'), ('10',)
NAMES = ('difficulty', 'text', 'probe', 'regulator')
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
    s = np.where(np.isfinite(s), s, -1e6)   # never-monitored episodes: lowest score (pre-registered rule)
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
    R8, L8, H8, PJ = [], {}, {}, {}
    for S in TEST:
        R, L, H = load_seed(S, 100000 * int(S)); R8 += R; L8.update(L); H8.update(H)
        p = 'data/prefix_judge_abs_s%s.jsonl.gz' % S
        if os.path.exists(p): PJ.update({(100000 * int(S) + d['idx'], int(d['f'])): d for d in ld(p)})
    Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]; yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); grp = np.array([r['idx'] for r, _ in jobs])
    X = parallel_features(jobs, Ld, 4); (bl, bc), _ = select(jobs, Hd)
    # cross-fitted derivation scores of all four components (same GroupKFold(5) as YB-0045)
    CF = np.zeros((len(jobs), 4))
    for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), yj, grp):
        jt = [jobs[i] for i in tr]
        mods = (DifficultyBaseline(use_t=True).fit(jt), TextMonitor(TEXT_C).fit(jt), Probe(bl, bc).fit(jt, Hd), AbsOrganism().fit_from(X[tr], jt))
        for i in te:
            r, t = jobs[i]; CF[i] = (mods[0].score(r, t), mods[1].score(r, t), mods[2].score(r, t, Hd), mods[3].score(r, Ld[r['idx']], t))
    ST = Stack().fit(CF, yj); BD = Bands().fit(CF, [t for _, t in jobs], yj, NAMES)
    DB, TM, P, O = DifficultyBaseline(use_t=True).fit(jobs), TextMonitor(TEXT_C).fit(jobs), Probe(bl, bc).fit(jobs, Hd), AbsOrganism().fit_from(X, jobs)
    havej = len(PJ) > 0
    ok = lambda r: r['idx'] in L8 and all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r)) and (not havej or all((r['idx'], t) in PJ for t in checkpoints(r)))
    A = [r for r in R8 if r['answered'] and ok(r)]; y = np.array([0 if r['correct'] else 1 for r in A]); mon = np.array([len(checkpoints(r)) > 0 for r in A])
    comp = {}
    for r in A:
        for t in checkpoints(r): comp[(r['idx'], t)] = np.array([DB.score(r, t), TM.score(r, t), P.score(r, t, H8), O.score(r, L8[r['idx']], t)])
    fixed = lambda r, t: COST; free = lambda r, t: 0.0
    V = {n: in_time(A, (lambda j: lambda r, t: comp[(r['idx'], t)][j])(j), free if n == 'difficulty' else fixed) for j, n in enumerate(NAMES)}
    V['stack'] = in_time(A, lambda r, t: ST.score(comp[(r['idx'], t)]), fixed)
    V['hospital_banded'] = in_time(A, lambda r, t: BD.score(comp[(r['idx'], t)], t), fixed)
    if havej: V['judge'] = in_time(A, lambda r, t: PJ[(r['idx'], t)]['score'], lambda r, t: PJ[(r['idx'], t)]['compute_s'])
    per = {m: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in evaluate(v_, y, mon).items() if k != 'fired'} for m, v_ in V.items()}
    h1 = boot_diff(V['stack'], V['probe'], y); h2 = boot_diff(V['hospital_banded'], V['probe'], y)
    res = dict(dry_run=DRY, smoke=SMOKE, deriv_seeds=DERIV, eval_seeds=TEST, derivation_answered=len(Rd), derivation_observations=len(jobs), probe_selected=dict(layer=bl, C=bc),
               text_C=TEXT_C, stack_weights=dict(zip(NAMES, [round(float(w), 4) for w in ST.lr.coef_[0]])), eval_answered=len(A), eval_wrong=int(y.sum()), monitors=per,
               H1_stack_minus_probe=h1, H1_supported=bool(h1[1] > 0),
               H2_hospital_minus_probe=h2, H2_noninferior_at_minus_0_05=bool(h2[1] > -0.05))
    # H3 (descriptive): which errors each component catches at its own 10% false-alarm threshold
    caught = {}
    for n in NAMES:
        v = V[n]; thr = cap_threshold(np.where(np.isfinite(v[y == 0]), v[y == 0], -1e6)); caught[n] = (np.where(np.isfinite(v), v, -1e6) > thr) & (y == 1)
    ov = {}
    for a_ in NAMES:
        for b_ in NAMES:
            if a_ < b_: ov['%s|%s' % (a_, b_)] = dict(both=int((caught[a_] & caught[b_]).sum()), only_first=int((caught[a_] & ~caught[b_]).sum()), only_second=int((~caught[a_] & caught[b_]).sum()))
    res['H3_overlap_of_caught_errors'] = ov; res['H3_caught_by_any_component'] = int(np.any([caught[n] for n in NAMES], axis=0).sum())
    if havej: res['S_stack_minus_judge'] = boot_diff(V['stack'], V['judge'], y); res['S_hospital_minus_judge'] = boot_diff(V['hospital_banded'], V['judge'], y)
    # NEWS2-style table: failure rate by banded level (in-time max points)
    hb = V['hospital_banded']; lv = {}
    for name, lo, hi in (('stable 0', -1, 0.5), ('watch 1-2', 0.5, 2.5), ('concern 3-5', 2.5, 5.5), ('urgent 6-12', 5.5, 99)):
        m = mon & (hb > lo) & (hb < hi); lv[name] = dict(episodes=int(m.sum()), wrong=int(y[m].sum()), failure_rate=round(float(y[m].mean()), 4) if m.sum() else None)
    res['S_banded_levels'] = lv
    pc = {}
    for t in T:
        idx = [i for i, r in enumerate(A) if t in checkpoints(r)]
        if len(idx) < 20 or y[idx].sum() < 3: continue
        yt = y[idx]; e = {n: boot_auc(yt, np.array([comp[(A[i]['idx'], t)][j] for i in idx])) for j, n in enumerate(NAMES)}
        e['stack'] = boot_auc(yt, np.array([ST.score(comp[(A[i]['idx'], t)]) for i in idx])); e['hospital_banded'] = boot_auc(yt, np.array([BD.score(comp[(A[i]['idx'], t)], t) for i in idx]))
        pc[str(t)] = dict(episodes=len(idx), wrong=int(yt.sum()), auroc_with_ci=e)
    res['S_per_checkpoint_auroc'] = pc
    out = 'docs/smoke.json' if SMOKE else ('docs/dryrun.json' if DRY else 'docs/results.json')
    json.dump(res, open(out, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print(json.dumps({k: res[k] for k in ('eval_answered', 'eval_wrong', 'stack_weights', 'H1_stack_minus_probe', 'H1_supported', 'H2_hospital_minus_probe', 'H2_noninferior_at_minus_0_05', 'H3_caught_by_any_component')}, default=str))
if __name__ == '__main__': main()
