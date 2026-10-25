# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0017: HPA-axis organism. External, deterministic, text-blind regulator: it only ever sees numbers.
ctypes binding to libcore.so + pure-Python reference (same RK4) + analytic bounds.'''
import ctypes, os
import numpy as np
_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcore.so'))
_P = ctypes.POINTER(ctypes.c_double)
_L.hpa_simulate.argtypes = [_P, ctypes.c_int, _P, ctypes.c_int, ctypes.c_int, _P, _P, _P]
DEFAULT = dict(b=0.1, k1=1.0, k2=1.0, k3=1.0, w1=0.5, w2=0.3, w3=0.05, Ki=1.0, n=2.0)
KEYS = ['b', 'k1', 'k2', 'k3', 'w1', 'w2', 'w3', 'Ki', 'n']

def simulate(S, params=None, sub=4, burn=2000):
    p = np.array([(params or DEFAULT).get(k, DEFAULT[k]) for k in KEYS], float)
    S = np.ascontiguousarray(S, float); T = len(S); H, A, C = np.zeros(T), np.zeros(T), np.zeros(T)
    if _L.hpa_simulate(S.ctypes.data_as(_P), T, p.ctypes.data_as(_P), sub, burn, H.ctypes.data_as(_P), A.ctypes.data_as(_P), C.ctypes.data_as(_P)): raise ValueError
    return H, A, C

def simulate_ref(S, params=None, sub=4, burn=2000):
    q = dict(DEFAULT, **(params or {}))
    def f(x, s):
        fb = 1 / (1 + (max(x[2], 0) / q['Ki']) ** q['n'])
        return np.array([q['b'] + q['k1'] * s * fb - q['w1'] * x[0], q['k2'] * x[0] * fb - q['w2'] * x[1], q['k3'] * x[1] - q['w3'] * x[2]])
    def st(x, s):
        h = 1 / sub
        for _ in range(sub):
            a = f(x, s); b = f(x + h / 2 * a, s); c = f(x + h / 2 * b, s); d = f(x + h * c, s); x = x + h / 6 * (a + 2 * b + 2 * c + d)
        return x
    x = np.zeros(3)
    for _ in range(burn): x = st(x, 0.0)
    out = []
    for s in S: x = st(x, max(s, 0)); out.append(x.copy())
    out = np.array(out); return out[:, 0], out[:, 1], out[:, 2]

def bounds(Smax, params=None):
    '''T2: invariant box for S <= Smax (from fb <= 1), assuming the state starts inside it.'''
    q = dict(DEFAULT, **(params or {})); H = (q['b'] + q['k1'] * Smax) / q['w1']; A = q['k2'] * H / q['w2']; return H, A, q['k3'] * A / q['w3']
