# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0051 confirmatory analysis (pre-registered; docs/PREREGISTRATION.md): precision at low false-alarm rates.
Inputs: data/explore_scores.npz (reference R, derivation) and the test scores written by tests/score_test.py:
  RUN_CONFIRMATORY=1 -> data/test_scores.npz (NEW seeds 27-38)          -> docs/results.json
  DRY_RUN=1          -> data/test_scores_dry.npz (derivation, synthetic d) -> docs/dryrun.json
  SMOKE=1            -> data/test_scores_smoke.npz (tiny, synthetic d)     -> docs/smoke.json   (50 resamples)
Without one of these the script does nothing (PROTOCOL rule 14).'''
import json, os, sys, time, numpy as np
sys.path.insert(0, 'src'); sys.path.insert(0, 'tests')
from decider import single, bootstrap, diff, burden_table, ci
from candidates import neg, c1, fit_c2, c2, c4_reference, c4, c3
from sklearn.metrics import roc_curve
SMOKE, DRY, CONF = (os.environ.get(k) == '1' for k in ('SMOKE', 'DRY_RUN', 'RUN_CONFIRMATORY'))
CAPS = (0.10, 0.02, 0.01, 0.005); NB = 50 if SMOKE else int(os.environ.get('N_BOOT', '2000'))
TEST_SEEDS = tuple(range(27, 39))
r4 = lambda x: round(float(x), 4)
def pauc(y, v, cap=0.01):
    f, t, _ = roc_curve(y, np.where(np.isfinite(v), v, -1e18)); m = f <= cap
    return r4(np.trapezoid(np.r_[t[m], np.interp(cap, f, t)], np.r_[f[m], cap]) / cap)
def exact(y, v, cap):
    '''Point operating point at a tiny cap, with exact event counts (descriptive only).'''
    v = neg(v); n0 = int((y == 0).sum()); k = int(np.floor(cap * n0 + 1e-9)); thr = np.sort(v[y == 0])[::-1][k]
    a = v > thr; return dict(caught=int(a[y == 1].sum()), false_alarms=int(a[y == 0].sum()), correct=n0, wrong=int(y.sum()))
def main():
    if not (SMOKE or DRY or CONF):
        print('YB-0051: the confirmatory analysis runs only via make confirmatory, after the public timestamp (rule 14)'); return 0
    src = 'data/test_scores_smoke.npz' if SMOKE else 'data/test_scores_dry.npz' if DRY else 'data/test_scores.npz'
    out = 'docs/smoke.json' if SMOKE else 'docs/dryrun.json' if DRY else 'docs/results.json'
    if not os.path.exists(src): print('missing', src, '(run tests/score_test.py first)'); return 1
    t0 = time.time(); Rz = np.load('data/explore_scores.npz', allow_pickle=True); R = {k: Rz[k] for k in Rz.files}
    Zz = np.load(src, allow_pickle=True); Z = {k: Zz[k] for k in Zz.files}; y = np.asarray(Z['y'])
    if CONF: assert sorted(set(Z['seed'].tolist())) == list(TEST_SEEDS), 'confirmatory run needs every test seed 27-38'
    assert np.all((Z['d4'] * 4) % 1 == 0) and np.all((Z['d8'] * 8) % 1 == 0), 'self-consistency levels must be k-sample fractions'
    m = fit_c2(R); ref4 = c4_reference(m, R)
    S = dict(probe=neg(Z['probe']), stack=neg(Z['stack']), self_consistency_k4=Z['d4'], self_consistency_k8=Z['d8'],
             C1_k4=c1(Z, R, Z['d4']), C1_k8=c1(Z, R, Z['d8'], 8), C2=c2(m, Z, R, Z['d4']), C4=c4(m, ref4, Z, R, Z['d4']))
    pt, bs = bootstrap({k: single(v) for k, v in S.items()}, y, caps=CAPS, n=NB)
    caught = lambda k, c: int(round(pt[(k, c)][0] * y.sum()))
    H1 = diff(pt, bs, 'C2', 'probe', 0.01); B2 = burden_table(pt, bs, 'C2', 0.01)['p=0.01']['precision']; H3 = diff(pt, bs, 'C1_k8', 'C1_k4', 0.01)
    supp = lambda lb, bar, strict=True: None if lb is None else bool(lb > bar if strict else lb >= bar)
    a3, a3k8 = c3(Z, R, Z['d4']), c3(Z, R, Z['d8'])
    res = dict(stage='smoke' if SMOKE else 'dry run (synthetic self-consistency; derivation seeds)' if DRY else 'confirmatory',
               source=src, reference='data/explore_scores.npz (seeds 15-26, monitors fitted on seeds 2-14)', bootstrap_resamples=NB,
               episodes=int(len(y)), wrong=int(y.sum()), correct=int((y == 0).sum()), seeds=sorted(set(Z['seed'].tolist())),
               C2_coefficients=dict(zip(('d4', 'pct_stack', 'pct_probe', 'pct_text', 'pct_difficulty', 'monitored'), [r4(c) for c in m.coef_[0]]), intercept=r4(m.intercept_[0])),
               H1=dict(test='recall(C2) - recall(probe) at 1% false alarms', estimate_ci=H1, caught=[caught('C2', 0.01), caught('probe', 0.01)], supported=supp(H1[1], 0.0)),
               H2=dict(test='precision of C2 at 1% false alarms and a 1% error base rate >= 0.33', estimate_ci=B2, supported=supp(B2[1], 0.33, strict=False)),
               H3=dict(test='recall(C1 k=8) - recall(C1 k=4) at 1% false alarms', estimate_ci=H3, caught=[caught('C1_k8', 0.01), caught('C1_k4', 0.01)], supported=supp(H3[1], 0.0)),
               table={k: {('fa_%g' % c): dict(caught=caught(k, c), recall=r4(pt[(k, c)][0]), fpr=r4(pt[(k, c)][1]), recall_ci=ci(bs[(k, c)][:, 0])) for c in CAPS} for k in S},
               partial_auroc_to_1pct={k: pauc(y, v) for k, v in S.items()},
               burden_1pct_fa={k: burden_table(pt, bs, k, 0.01) for k in S}, burden_10pct_fa={k: burden_table(pt, bs, k, 0.10) for k in S},
               C4_minus_C2_1pct=diff(pt, bs, 'C4', 'C2', 0.01), C2_minus_C1k4_1pct=diff(pt, bs, 'C2', 'C1_k4', 0.01),
               C3=dict(rule='stack > reference 90th pct on correct AND d >= 0.75', k4=dict(caught=int(a3[y == 1].sum()), recall=r4(a3[y == 1].mean()), false_alarms=int(a3[y == 0].sum()), fpr=r4(a3[y == 0].mean())),
                       k8=dict(caught=int(a3k8[y == 1].sum()), recall=r4(a3k8[y == 1].mean()), false_alarms=int(a3k8[y == 0].sum()), fpr=r4(a3k8[y == 0].mean()))),
               exact_0p1pct={k: exact(y, v, 0.001) for k, v in S.items()},
               review_cost=dict(mean_seconds_k4=r4(np.mean(Z['sec4'])), mean_seconds_k8=r4(np.mean(Z['sec8'])), mean_generation_seconds=r4(np.mean(Z['wall'])),
                                k4_share_of_generation=r4(np.mean(Z['sec4']) / np.mean(Z['wall'])), k8_share_of_generation=r4(np.mean(Z['sec8']) / np.mean(Z['wall']))),
               seconds=round(time.time() - t0, 1))
    json.dump(res, open(out, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print('%s: %d episodes, %d wrong' % (res['stage'], res['episodes'], res['wrong']))
    for k in S: print('  %-20s 1%%: %4d  0.5%%: %4d  2%%: %4d  10%%: %4d  pAUC1%%: %.3f' % (k, caught(k, 0.01), caught(k, 0.005), caught(k, 0.02), caught(k, 0.10), res['partial_auroc_to_1pct'][k]))
    print('  H1', H1, res['H1']['supported'], ' H2', B2, res['H2']['supported'], ' H3', H3, res['H3']['supported']); print('wrote', out)
    return 0
if __name__ == '__main__': sys.exit(main())
