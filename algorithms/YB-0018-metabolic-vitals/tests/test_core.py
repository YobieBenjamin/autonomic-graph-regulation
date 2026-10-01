# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from metab import power_features, power_features_ref
r = np.random.default_rng(0)
def t_c_equals_reference():
    for n in (2, 5, 60):
        t = np.cumsum(r.uniform(0.05, 0.2, n)); p = r.uniform(1000, 40000, n); assert np.allclose(power_features(t, p), power_features_ref(t, p), rtol=1e-12)
def t_constant_power_energy():
    t = np.linspace(0, 2.0, 21); f = power_features(t, np.full(21, 15000.0))
    assert abs(f[0] - 30.0) < 1e-9 and abs(f[1] - 15.0) < 1e-9 and f[3] == 0 and abs(f[4] - 2.0) < 1e-12   # 15 W x 2 s = 30 J
def t_linear_ramp_trapezoid_exact():
    t = np.linspace(0, 1, 11); p = 1000 * 10 * t; assert abs(power_features(t, p)[0] - 5.0) < 1e-9     # integral of 10t W over [0,1] = 5 J
def t_short():
    assert np.isnan(power_features([0.0], [1.0])).all()
T = [t_c_equals_reference, t_constant_power_energy, t_linear_ramp_trapezoid_exact, t_short]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
