# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Unit tests for the YB-0051 candidates and the end-to-end analysis on synthetic data (no recordings needed).'''
import os, sys, json, tempfile, importlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, HERE)
from candidates import pct, c1, fit_c2, c2, c4_reference, c4, c3, derivation_check, neg
CATS = np.array(['add_hard', 'count', 'modpow', 'mul_easy', 'mul_hard', 'weekday'])
def synth(n, seed, k=4, with_d8=False):
    g = np.random.default_rng(seed); y = (g.random(n) < 0.09).astype(int); cat = CATS[g.integers(0, 6, n)]
    mon = g.random(n) > 0.35; base = lambda s: np.where(mon, g.normal(s * y, 1.0), -np.inf)
    flag = g.random(n) < 0.45 * y + 0.04; X = g.random((n, 8)) < np.where(flag, 0.6, 0.01)[:, None]
    Z = dict(y=y, cat=cat, probe=base(1.5), stack=base(1.6), text=base(0.8), difficulty=g.normal(0.5 * y, 1.0), d=X[:, :4].mean(1),
             d4=X[:, :4].mean(1), d8=X.mean(1), seed=np.full(n, seed), sec4=np.full(n, 4.0), sec8=np.full(n, 8.0), wall=np.full(n, 20.0),
             regulator=g.normal(size=n), banded=g.normal(size=n), length=g.normal(size=n), question_type=g.random(n))
    return Z
def test_pct_midrank_ties_and_never_monitored():
    ref = np.array([1., 2., 2., 3., -np.inf])
    assert np.allclose(pct(np.array([2.0, 0.5, 10.0, -np.inf]), ref), [0.6, 0.2, 1.0, 0.1])
    v = np.sort(np.random.default_rng(0).normal(size=50)); assert np.all(np.diff(pct(v, v)) > 0)
def test_c1_never_crosses_a_level():
    R = synth(3000, 1); Z = synth(2000, 2)
    for k, d in ((4, Z['d4']), (8, Z['d8'])):
        s = c1(Z, R, d, k); lev = np.round(d * k).astype(int)
        for a in range(k):
            if (lev == a).any() and (lev == a + 1).any(): assert s[lev == a].max() < s[lev == a + 1].min()
def test_c2_uses_reference_scale_and_is_deterministic():
    R = synth(4000, 3); Z = synth(1500, 4); m1, m2 = fit_c2(R), fit_c2(R)
    assert np.allclose(c2(m1, Z, R, Z['d4']), c2(m2, Z, R, Z['d4']))
    assert m1.coef_[0][0] > 0 and m1.coef_[0][1] > 0          # disagreement and stack both point toward errors
def test_c4_is_continuous_and_handles_unseen_task():
    R = synth(4000, 5); Z = synth(1500, 6); Z['cat'][:20] = 'new_task'; m = fit_c2(R); ref = c4_reference(m, R)
    s = c4(m, ref, Z, R, Z['d4']); top = np.sort(s)[::-1][:30]
    assert np.all(np.isfinite(s)) and len(np.unique(top)) == len(top)   # no ties at the top (the exploratory fault)
def test_c3_operating_point():
    R = synth(4000, 7); a = c3(R, R, R['d4']); q = np.quantile(neg(R['stack'])[R['y'] == 0], 0.9)
    assert np.array_equal(a, (neg(R['stack']) > q) & (R['d4'] >= 0.75))
def test_derivation_check_runs():
    out = derivation_check(synth(3000, 8)); assert out['C4']['distinct_top2pct'] > 1 and out['C2']['caught_1pct'] >= 0
def test_experiment_end_to_end_on_synthetic():
    old = os.getcwd(); tmp = tempfile.mkdtemp(); os.makedirs(os.path.join(tmp, 'data')); os.makedirs(os.path.join(tmp, 'docs'))
    np.savez(os.path.join(tmp, 'data', 'explore_scores.npz'), **{k: v for k, v in synth(3000, 9).items() if k not in ('d4', 'd8')})
    np.savez(os.path.join(tmp, 'data', 'test_scores_smoke.npz'), **synth(1500, 10))
    os.environ['SMOKE'] = '1'
    try:
        os.chdir(tmp); import experiment; importlib.reload(experiment); assert experiment.main() == 0
        r = json.load(open('docs/smoke.json')); assert r['episodes'] == 1500 and set(r['H1']) >= {'estimate_ci', 'supported'}
        assert r['table']['C2']['fa_0.01']['fpr'] <= 0.01 + 1e-9
    finally:
        os.chdir(old); os.environ.pop('SMOKE')
if __name__ == '__main__':
    fns = [v for k, v in dict(globals()).items() if k.startswith('test_')]
    for f in fns: f(); print('PASS', f.__name__)
    print('%d/%d tests passed' % (len(fns), len(fns)))
