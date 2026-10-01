# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from bhw import BHW, budget_rule, worst_case_attack

R = np.random.default_rng(0)
def mon(p=5, eta=0.05):
    return BHW(eta=eta).fit(R.normal(size=(2000, p)) @ R.normal(size=(p, p)))

def test_c_matches_python_reference():
    m = mon(); S = m.mu0 + R.normal(size=(800, 5)) * 1.5 + np.linspace(0, 3, 800)[:, None]
    for mode in ("static", "unbounded", "budgeted"):
        a, b = m.run(S, mode), m.run_reference(S, mode)
        for k in a: assert np.allclose(a[k], b[k]), (mode, k)

def test_T1_T2_bound_holds_under_worst_case_attack():
    for eta in (0.01, 0.05, 0.2):
        m = mon(eta=eta); T = int(5 * m.B / (eta * m.tau)) + 50
        out = m.run(worst_case_attack(m, T, "budgeted"), "budgeted")
        assert out["drift"].max() <= m.B + eta * m.tau + 1e-9          # T1
        acc = ~out["flag"]; S = worst_case_attack(m, T, "budgeted")
        dist = np.sqrt(np.einsum("ij,jk,ik->i", S - m.mu0, m.P, S - m.mu0))
        assert dist[acc].max() <= m.tau + m.B + eta * m.tau + 1e-9      # T2
        assert out["frozen"][-1]

def test_T3_alarm_step_matches_theory():
    m = mon(eta=0.05); c = 0.99
    out = m.run(worst_case_attack(m, 5000, "budgeted", c), "budgeted")
    t_alarm = int(np.argmax(out["frozen"])) + 1
    assert t_alarm == math.ceil(m.B / (m.eta * c * m.tau) + 1e-12) or abs(t_alarm - m.B / (m.eta * c * m.tau)) <= 1

def test_unbounded_is_unbounded():
    m = mon(eta=0.05); T = 4000
    out = m.run(worst_case_attack(m, T, "unbounded"), "unbounded")
    assert out["flag"].sum() == 0 and out["drift"][-1] > 20 * (m.B + m.eta * m.tau)

def test_budget_rule_monotone_and_1d_closed_form():
    assert budget_rule(0.02, 64) > budget_rule(0.02, 1) and budget_rule(0.1, 4) > budget_rule(0.01, 4)
    from scipy.stats import norm
    assert abs(budget_rule(0.02, 1, 0.99) - math.sqrt(0.02 / 1.98) * norm.ppf(0.995)) < 1e-9

if __name__ == "__main__":
    fns = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for f in fns: f(); print("PASS", f.__name__)
    print(f"{len(fns)}/{len(fns)} tests passed")
