# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0051 EXPLORATORY score dump (not confirmatory). Copy of the YB-0050 analysis up to the scores, on the YB-0050 test seeds 15-26, which are now derivation data for YB-0051 (PROTOCOL rule 2). Writes data/explore_scores.npz. Original docstring follows: YB-0050 analysis (pre-registered; docs/PREREGISTRATION.md): a powered decider for the YB-0047 and YB-0049 close calls, a
non-inferiority test of a stack with no language-model signal against self-consistency, and the two scaling measurements (cost per
check as a share of inference; false-alarm burden at realistic error base rates). Fit on derivation seeds 2 to 14; test on NEW seeds
15 to 26, recorded after the plan is timestamped. DRY_RUN=1: fit on 2-8, evaluate on 10-12 with SYNTHETIC self-consistency scores.
SMOKE=1: 2 training seeds, 1 eval seed, 150 episodes each, 50 bootstrap resamples. Confirmatory run only via make confirmatory.'''
import json, gzip, os, sys, time, platform, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, parallel_features, AbsOrganism, LengthControls
from corrected import in_time_max
from probe import Probe, select
from textmon import TextMonitor
from difficulty import DifficultyBaseline
from fusion import Stack, Bands
from decider import single, layered, bootstrap, diff, burden_table, rates, ops_inference, ops_probe, ops_text, ci
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
COST, T = 0.005, (48, 96, 192, 384)
TEXT_C = 1.0          # pre-declared: the value YB-0047 selected by derivation-only cross-validation (also used in YB-0048)
MARGIN = 0.10         # H3 non-inferiority margin (pre-declared)
COST_SHARE = 0.01     # H4 pass bar: monitor cost at most 1% of inference
NB = int(os.environ.get('N_BOOT', '2000')); DRY = os.environ.get('DRY_RUN') == '1'
DERIV = tuple(str(s) for s in range(2, 15)); TEST = tuple(str(s) for s in range(15, 27))
if DRY: DERIV, TEST = ('2', '3', '4', '5', '6', '7', '8'), ('10', '11', '12')
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE: DRY, DERIV, TEST, NB = True, ('2', '3'), ('10',), 50
NAMES = ('difficulty', 'text', 'probe', 'regulator')
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]
r4 = lambda x: round(float(x), 4)
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
def auroc(y, s): s = np.where(np.isfinite(s), s, -1e6); return r4(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else None
def main():
    if False:
        print('pre-registration stage: the confirmatory analysis runs only via make confirmatory, after the public timestamp'); return
    if not all(os.path.exists('data/seed%s_LH.jsonl.gz' % S) for S in DERIV + TEST):
        print('recordings not present (public checkout, or test seeds not yet recorded): nothing to analyse'); return
    SC = {}
    if not DRY:
        for S in TEST:
            p = 'data/selfcons_yb0050_seed%s.jsonl' % S
            if not os.path.exists(p): print('self-consistency recordings missing for seed', S); return
            for l in open(p): d = json.loads(l); SC[100000 * int(S) + d['idx']] = d
    t_start = time.time()
    Rd, Ld, Hd = [], {}, {}
    for S in DERIV:
        R, L, H = load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
    R8, L8, H8 = [], {}, {}
    for S in TEST:
        R, L, H = load_seed(S, 100000 * int(S)); R8 += R; L8.update(L); H8.update(H)
    Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]; yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); grp = np.array([r['idx'] for r, _ in jobs])
    X = parallel_features(jobs, Ld, 4); (bl, bc), sel_table = select(jobs, Hd)
    CF = np.zeros((len(jobs), 4))   # cross-fitted derivation scores of the four components (GroupKFold(5), as YB-0045 and YB-0048)
    for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), yj, grp):
        jt = [jobs[i] for i in tr]
        mods = (DifficultyBaseline(use_t=True).fit(jt), TextMonitor(TEXT_C).fit(jt), Probe(bl, bc).fit(jt, Hd), AbsOrganism().fit_from(X[tr], jt))
        for i in te:
            r, t = jobs[i]; CF[i] = (mods[0].score(r, t), mods[1].score(r, t), mods[2].score(r, t, Hd), mods[3].score(r, Ld[r['idx']], t))
    ST = Stack().fit(CF, yj); BD = Bands().fit(CF, [t for _, t in jobs], yj, NAMES)
    DB, TM, P, O = DifficultyBaseline(use_t=True).fit(jobs), TextMonitor(TEXT_C).fit(jobs), Probe(bl, bc).fit(jobs, Hd), AbsOrganism().fit_from(X, jobs)
    LC = LengthControls().fit(Rd); QT = {c: float(np.mean([not r['correct'] for r in Rd if r['cat'] == c])) for c in set(r['cat'] for r in Rd)}
    ok = lambda r: r['idx'] in L8 and all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r))
    A = [r for r in R8 if r['answered'] and ok(r)]; U = [r for r in R8 if not r['answered'] and ok(r)]
    y = np.array([0 if r['correct'] else 1 for r in A])
    # score every component at every checkpoint, timing each call (H4)
    comp, tim = {}, {}
    for r in A + U:
        for t in checkpoints(r):
            s, c = np.zeros(4), np.zeros(5)
            t0 = time.perf_counter(); s[0] = DB.score(r, t); t1 = time.perf_counter(); s[1] = TM.score(r, t); t2 = time.perf_counter()
            s[2] = P.score(r, t, H8); t3 = time.perf_counter(); s[3] = O.score(r, L8[r['idx']], t); t4 = time.perf_counter()
            ST.score(s); BD.score(s, t); t5 = time.perf_counter()
            comp[(r['idx'], t)] = s; tim[(r['idx'], t)] = np.array([t1 - t0, t2 - t1, t3 - t2, t4 - t3, t5 - t4])
    fixed, free = (lambda r, t: COST), (lambda r, t: 0.0)
    def scores(R):
        V = {n: in_time(R, (lambda j: lambda r, t: comp[(r['idx'], t)][j])(j), free if n == 'difficulty' else fixed) for j, n in enumerate(NAMES)}
        V['stack'] = in_time(R, lambda r, t: ST.score(comp[(r['idx'], t)]), fixed)
        V['banded'] = in_time(R, lambda r, t: BD.score(comp[(r['idx'], t)], t), fixed)
        V['length'] = in_time(R, lambda r, t: LC.c2(r, t), free); V['question_type'] = in_time(R, lambda r, t: QT.get(r['cat'], 0.0), free)
        return V
    V = scores(A)
    if DRY:   # synthetic self-consistency for pipeline checks only (same generator as YB-0049)
        g = np.random.default_rng(7); d = np.where(g.random(len(A)) < 0.45 * y + 0.04, g.choice([0.25, 0.5, 0.75, 1.0], len(A)), 0.0); sec = np.full(len(A), 4.0)
    else:
        miss = [r['idx'] for r in A if r['idx'] not in SC]
        if miss: print('self-consistency scores missing for', len(miss), 'episodes'); return
        d = np.array([SC[r['idx']]['b2_disagree'] for r in A], float); sec = np.array([SC[r['idx']]['review_seconds'] for r in A], float)
    hb = V['banded']; gate = (hb >= 0.5) | ~np.isfinite(hb)
    keys = ('difficulty', 'text', 'probe', 'regulator', 'stack', 'banded', 'length', 'question_type')
    out = 'data/explore_scores_smoke.npz' if SMOKE else 'data/explore_scores.npz'
    np.savez(out, y=y, d=d, sec=sec, gate=gate, cat=np.array([r['cat'] for r in A]), seed=np.array([r['idx'] // 100000 for r in A]),
             wall=np.array([r['wall'] for r in A]), **{k: V[k] for k in keys})
    print('wrote', out, len(y), int(y.sum()))
if __name__ == '__main__': main()
