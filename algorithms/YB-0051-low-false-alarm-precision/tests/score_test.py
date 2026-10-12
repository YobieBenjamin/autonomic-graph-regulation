# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0051 test scoring (pre-registered; docs/PREREGISTRATION.md). The non-LLM monitors are fitted on derivation seeds 2-14 EXACTLY as
in explore/dump_scores.py (the code that produced the reference data/explore_scores.npz, itself a copy of the YB-0050 analysis), then
score the NEW test seeds 27-38, so test scores and reference scores come from the same fitted monitors. Self-consistency comes from
agr/selfcons_yb0051.py (k = 8; d4 = the first 4 samples, identical to the YB-0050 k = 4 procedure).
  RUN_CONFIRMATORY=1 -> data/test_scores.npz        (derivation 2-14, test 27-38)
  DRY_RUN=1          -> data/test_scores_dry.npz    (derivation 2-8, evaluation 10-12, SYNTHETIC self-consistency)
  SMOKE=1            -> data/test_scores_smoke.npz  (derivation 2-3, evaluation 10, 150 episodes each, SYNTHETIC self-consistency)'''
import json, gzip, os, sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, parallel_features, AbsOrganism, LengthControls
from corrected import in_time_max
from probe import Probe, select
from textmon import TextMonitor
from difficulty import DifficultyBaseline
from fusion import Stack, Bands
from sklearn.model_selection import GroupKFold
COST = 0.005; TEXT_C = 1.0
SMOKE, DRY, CONF = (os.environ.get(k) == '1' for k in ('SMOKE', 'DRY_RUN', 'RUN_CONFIRMATORY'))
DERIV = tuple(str(s) for s in range(2, 15)); TEST = tuple(str(s) for s in range(27, 39))
if DRY: DERIV, TEST = ('2', '3', '4', '5', '6', '7', '8'), ('10', '11', '12')
if SMOKE: DERIV, TEST = ('2', '3'), ('10',)
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
def synthetic_sc(y, seed=7):
    '''Pipeline-check self-consistency: a flagged episode's 8 samples each differ with probability 0.6, others with 0.01; d4 is the
    mean of the first 4 samples, d8 of all 8 (nested, as in the real recorder). Never used for any result.'''
    g = np.random.default_rng(seed); flag = g.random(len(y)) < 0.45 * y + 0.04
    X = g.random((len(y), 8)) < np.where(flag, 0.6, 0.01)[:, None]
    return X[:, :4].mean(1), X.mean(1), np.full(len(y), 4.0), np.full(len(y), 8.0)
def main():
    if not (SMOKE or DRY or CONF):
        print('YB-0051: test scoring runs only via make confirmatory / dryrun / smoke'); return 0
    if not all(os.path.exists('data/seed%s_LH.jsonl.gz' % S) for S in DERIV + TEST):
        print('recordings not present (public checkout, or test seeds not yet recorded)'); return 1
    SC = {}
    if CONF:
        for S in TEST:
            p = 'data/selfcons_yb0051_seed%s.jsonl' % S
            if not os.path.exists(p): print('self-consistency recordings missing for seed', S); return 1
            for l in open(p): d = json.loads(l); SC[100000 * int(S) + d['idx']] = d
    Rd, Ld, Hd = [], {}, {}
    for S in DERIV:
        R, L, H = load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
    R8, L8, H8 = [], {}, {}
    for S in TEST:
        R, L, H = load_seed(S, 100000 * int(S)); R8 += R; L8.update(L); H8.update(H)
    # ---- from here to the scores: identical to explore/dump_scores.py (YB-0050 analysis) ----
    Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]; yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); grp = np.array([r['idx'] for r, _ in jobs])
    X = parallel_features(jobs, Ld, 4); (bl, bc), sel_table = select(jobs, Hd)
    CF = np.zeros((len(jobs), 4))
    for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), yj, grp):
        jt = [jobs[i] for i in tr]
        mods = (DifficultyBaseline(use_t=True).fit(jt), TextMonitor(TEXT_C).fit(jt), Probe(bl, bc).fit(jt, Hd), AbsOrganism().fit_from(X[tr], jt))
        for i in te:
            r, t = jobs[i]; CF[i] = (mods[0].score(r, t), mods[1].score(r, t), mods[2].score(r, t, Hd), mods[3].score(r, Ld[r['idx']], t))
    ST = Stack().fit(CF, yj); BD = Bands().fit(CF, [t for _, t in jobs], yj, NAMES)
    DB, TM, P, O = DifficultyBaseline(use_t=True).fit(jobs), TextMonitor(TEXT_C).fit(jobs), Probe(bl, bc).fit(jobs, Hd), AbsOrganism().fit_from(X, jobs)
    LC = LengthControls().fit(Rd); QT = {c: float(np.mean([not r['correct'] for r in Rd if r['cat'] == c])) for c in set(r['cat'] for r in Rd)}
    ok = lambda r: r['idx'] in L8 and all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r))
    A = [r for r in R8 if r['answered'] and ok(r)]
    y = np.array([0 if r['correct'] else 1 for r in A])
    comp = {}
    for r in A:
        for t in checkpoints(r):
            comp[(r['idx'], t)] = np.array([DB.score(r, t), TM.score(r, t), P.score(r, t, H8), O.score(r, L8[r['idx']], t)])
    fixed, free = (lambda r, t: COST), (lambda r, t: 0.0)
    V = {n: in_time(A, (lambda j: lambda r, t: comp[(r['idx'], t)][j])(j), free if n == 'difficulty' else fixed) for j, n in enumerate(NAMES)}
    V['stack'] = in_time(A, lambda r, t: ST.score(comp[(r['idx'], t)]), fixed)
    V['banded'] = in_time(A, lambda r, t: BD.score(comp[(r['idx'], t)], t), fixed)
    V['length'] = in_time(A, lambda r, t: LC.c2(r, t), free); V['question_type'] = in_time(A, lambda r, t: QT.get(r['cat'], 0.0), free)
    # ---- self-consistency ----
    if CONF:
        answered = [r['idx'] for r in R8 if r['answered']]; miss = [i for i in answered if i not in SC]
        if miss: print('self-consistency scores missing for', len(miss), 'answered episodes'); return 1
        d4, d8, s4, s8 = (np.array([SC[r['idx']][k] for r in A], float) for k in ('d4', 'd8', 'review_seconds_k4', 'review_seconds_k8'))
    else:
        d4, d8, s4, s8 = synthetic_sc(y)
    out = 'data/test_scores_smoke.npz' if SMOKE else 'data/test_scores_dry.npz' if DRY else 'data/test_scores.npz'
    np.savez(out, y=y, d4=d4, d8=d8, sec4=s4, sec8=s8, cat=np.array([r['cat'] for r in A]), seed=np.array([r['idx'] // 100000 for r in A]),
             wall=np.array([r['wall'] for r in A]), n_unmonitorable_answered=np.array(sum(1 for r in R8 if r['answered'] and not ok(r))),
             **{k: V[k] for k in ('difficulty', 'text', 'probe', 'regulator', 'stack', 'banded', 'length', 'question_type')})
    print('wrote', out, len(y), int(y.sum())); return 0
if __name__ == '__main__': sys.exit(main())
