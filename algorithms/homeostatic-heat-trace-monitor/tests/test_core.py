# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from h2cm import heat_trace, effective_connectivity, H2CM

def ref_eigs(A):
    d = A.sum(1); inv = np.where(d > 0, 1/np.sqrt(np.where(d > 0, d, 1)), 0)
    L = np.diag((d > 0).astype(float)) - inv[:, None] * A * inv[None, :]
    return np.sort(np.linalg.eigvalsh(L))

def test_matches_numpy_reference():
    r = np.random.default_rng(1)
    for n in [2, 5, 17, 60]:
        A = np.abs(r.normal(size=(n, n))); A = A + A.T; np.fill_diagonal(A, 0)
        tr, ev = heat_trace(A, return_eigs=True)
        assert np.allclose(np.sort(ev), ref_eigs(A), atol=1e-9)

def test_spectrum_in_0_2_and_heat_trace_identities():
    r = np.random.default_rng(2)
    A = np.abs(r.normal(size=(30, 30))); A = A + A.T
    tr, ev = heat_trace(A, ts=np.array([0.0, 1e6]), return_eigs=True)
    assert ev.min() > -1e-9 and ev.max() < 2 + 1e-9
    assert abs(tr[0] - 30) < 1e-9                  # h(0) = n
    assert abs(tr[1] - 1) < 1e-6                   # h(inf) = #connected components = 1

def test_components_counted():
    A = np.zeros((6, 6)); A[0,1]=A[1,0]=1; A[2,3]=A[3,2]=1; A[4,5]=A[5,4]=1
    assert abs(heat_trace(A, ts=np.array([1e6]))[0] - 3) < 1e-6

def test_known_graph_complete_K4():
    A = np.ones((4, 4)) - np.eye(4)                # eigs: 0, 4/3, 4/3, 4/3
    assert np.allclose(np.sort(heat_trace(A, return_eigs=True)[1]), [0, 4/3, 4/3, 4/3])

def test_effective_connectivity_shape_and_symmetry():
    W2, W3 = np.ones((3, 4)), np.ones((2, 3))
    A = effective_connectivity([W2, W3], [np.array([1., 0, 2, 0]), np.ones(3)])
    assert A.shape == (9, 9) and np.allclose(A, A.T) and A[4, 1] == 0 and A[4, 2] == 2

def test_drift_budget_freezes():
    r = np.random.default_rng(3)
    m = H2CM(eta=0.2, drift_budget=1.0).fit(r.normal(size=(500, 4)))
    froze = False
    for k in range(2000):
        _, froze = m.step(np.full(4, 0.001 * k) + 0.1 * r.normal(size=4))
        if froze: break
    assert froze and m.drift() <= 1.0 + 1.0     # stops within one step of budget

if __name__ == "__main__":
    fns = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for f in fns: f(); print("PASS", f.__name__)
    print(f"{len(fns)}/{len(fns)} tests passed")
