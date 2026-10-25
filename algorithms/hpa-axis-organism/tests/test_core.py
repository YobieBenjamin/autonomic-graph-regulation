# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import sys, numpy as np
sys.path.insert(0, 'src')
from hpa import simulate, simulate_ref, bounds, DEFAULT
r = np.random.default_rng(0)
def t_c_equals_reference():
    S = np.abs(r.normal(size=300)) * 3
    for a, b in zip(simulate(S, burn=300), simulate_ref(S, burn=300)): assert np.allclose(a, b, rtol=1e-9, atol=1e-12)
def t_T1_positivity():
    for _ in range(20):
        S = np.abs(r.standard_cauchy(size=400)); assert min(x.min() for x in simulate(S)) >= -1e-12
def t_T2_boundedness():
    Smax = 5.0; Hb, Ab, Cb = bounds(Smax)
    for S in (np.full(4000, Smax), np.tile([Smax] * 50 + [0] * 50, 40), r.uniform(0, Smax, 4000)):
        H, A, C = simulate(S); assert H.max() <= Hb + 1e-9 and A.max() <= Ab + 1e-9 and C.max() <= Cb + 1e-9
def t_T3_unique_equilibrium():
    a = simulate(np.full(8000, 2.0))[2][-1]
    b = simulate(np.r_[np.full(300, 30.0), np.full(8000, 2.0)])[2][-1]
    assert abs(a - b) < 1e-6 * max(1, a), (a, b)
def t_T4_feedback_desensitization():
    pulse = np.full(20, 10.0)
    fresh = simulate(np.r_[np.zeros(50), pulse, np.zeros(50)])[0]
    chronic = simulate(np.r_[np.full(2000, 3.0), pulse, np.full(50, 3.0)])[0]
    rise_fresh = fresh[50:70].max() - fresh[49]; rise_chronic = chronic[2000:2020].max() - chronic[1999]
    assert rise_chronic < rise_fresh, (rise_chronic, rise_fresh)
T = [t_c_equals_reference, t_T1_positivity, t_T2_boundedness, t_T3_unique_equilibrium, t_T4_feedback_desensitization]
for t in T: t(); print('PASS', t.__name__)
print(f'{len(T)}/{len(T)} tests passed')
