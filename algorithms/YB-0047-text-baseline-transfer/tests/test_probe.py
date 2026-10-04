# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Tests for the YB-0042 probe (src/probe.py), on synthetic hidden states with a planted signal.'''
import sys, numpy as np
sys.path.insert(0, 'src')
from probe import feat, Probe, cv_auroc, select, LAYERS
from sklearn.metrics import roc_auc_score
D = 16; rng = np.random.default_rng(0)

def synth(n, signal_layer=12, strength=1.5, seed=0):
    r = np.random.default_rng(seed); R, H = [], {}
    for i in range(n):
        wrong = r.random() < 0.3; cat = ['a', 'b'][i % 2]; e = {}
        for t in (48, 96):
            last = r.normal(size=(len(LAYERS), D)); mean = r.normal(size=(len(LAYERS), D))
            if wrong: last[LAYERS.index(signal_layer), 0] += strength; mean[LAYERS.index(signal_layer), 1] += strength
            e['last_%d' % t] = last.astype(np.float16); e['mean_%d' % t] = mean.astype(np.float16)
        H[i] = e; R.append(dict(idx=i, cat=cat, correct=not wrong, final_start=200))
    return R, H

def test_feature_shapes():
    R, H = synth(4)
    assert feat(H, 0, 48, 12).shape == (2 * D + 1,) and feat(H, 0, 48, 'all').shape == (2 * D * len(LAYERS) + 1,)

def test_probe_learns_planted_signal():
    R, H = synth(400); jobs = [(r, t) for r in R for t in (48, 96)]
    auc, _ = cv_auroc(jobs, H, 12, 0.1); assert auc > 0.8, auc
    auc_noise, _ = cv_auroc(jobs, H, 6, 0.1); assert auc_noise < 0.65, auc_noise

def test_selection_finds_informative_layer():
    R, H = synth(400, signal_layer=18); jobs = [(r, t) for r in R for t in (48, 96)]
    (L, C), table = select(jobs, H); assert L == 18, (L, table)

def test_normalization_uses_training_statistics_only():
    R, H = synth(200); jobs = [(r, t) for r in R for t in (48, 96)]
    P = Probe(12, 0.1).fit(jobs[:200], H); before = dict((k, v[0].copy()) for k, v in P.stats.items())
    _ = [P.score(r, t, H) for r, t in jobs[200:]]
    assert all(np.array_equal(before[k], P.stats[k][0]) for k in before), 'scoring must not change stored statistics'

if __name__ == '__main__':
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_'): fn(); n += 1; print('PASS', name)
    print('%d/%d probe tests passed' % (n, n))
