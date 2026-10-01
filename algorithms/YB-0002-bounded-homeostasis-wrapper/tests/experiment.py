# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""YB-0002 evaluation. Wrap two strong baseline detectors (Energy, activation-Mahalanobis)
with static / unbounded-homeostatic / budgeted (BHW) baselines. B is set by the C1 rule,
not tuned. Deterministic; writes docs/results.json."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from sklearn.datasets import load_digits
from mlp import MLP
from bhw import BHW, worst_case_attack

r = np.random.default_rng(0)
X, y = load_digits(return_X_y=True); X = X / 16.0
idx = r.permutation(len(X)); X, y = X[idx], y[idx]
ind = y < 5; Xi, yi, Xo = X[ind], y[ind], X[~ind]; n = len(Xi)
Xtr, ytr, Xcal, Xte = Xi[:n//2], yi[:n//2], Xi[n//2:3*n//4], Xi[3*n//4:]
net = MLP(64, 32, 32, 5, seed=0); net.train(Xtr, ytr)

def feat(Xs, kind):
    _, a1, _, a2, lo = net.forward(Xs)
    return -np.log(np.exp(lo).sum(1))[:, None] if kind == "energy" else np.hstack([a1, a2])

T, SEEDS, ETA = 3000, 10, 0.02
alpha = np.clip((np.arange(T) - 500) / 2000, 0, 1)
res = {"eta": ETA, "seeds": SEEDS, "detectors": {}}
for kind, split in (("energy", False), ("act-mahalanobis", False), ("energy", True), ("act-mahalanobis", True)):
    m = BHW(eta=ETA, split=split).fit(feat(Xcal, kind)); kind_label = kind + (" [C2 split-cal]" if split else " [C1]")
    R = {"p": m.p, "tau": m.tau, "B_rule_q0.999": m.B, "bound_T1": m.B + ETA * m.tau}
    agg = {md: {"final500_flag": [], "clean_first500_flag": [], "alarm_alpha": [], "clean_false_alarm": 0}
           for md in ("static", "unbounded", "budgeted")}
    for sd in range(SEEDS):
        rr = np.random.default_rng(100 + sd)
        a_i, b_i = rr.integers(0, len(Xte), T), rr.integers(0, len(Xo), T)
        drift = feat((1 - alpha)[:, None] * Xte[a_i] + alpha[:, None] * Xo[b_i], kind)
        clean = feat(np.clip(Xte[rr.integers(0, len(Xte), T)] + rr.normal(0, .02, (T, 64)), 0, 1), kind)
        for md in agg:
            o = m.run(drift, md); c = m.run(clean, md)
            agg[md]["final500_flag"].append(o["flag"][-500:].mean())
            agg[md]["clean_first500_flag"].append(o["flag"][:500].mean())
            if o["frozen"].any(): agg[md]["alarm_alpha"].append(float(alpha[np.argmax(o["frozen"])]))
            agg[md]["clean_false_alarm"] += int(c["frozen"].any())
    for md, v in agg.items():
        R[md] = {"final500_flag_rate_mean": float(np.mean(v["final500_flag"])),
                 "clean_segment_flag_rate_mean": float(np.mean(v["clean_first500_flag"])),
                 "drift_detected": f"{len(v['alarm_alpha'])}/{SEEDS}",
                 "alarm_at_alpha_mean": float(np.mean(v["alarm_alpha"])) if v["alarm_alpha"] else None,
                 "clean_false_alarms": f"{v['clean_false_alarm']}/{SEEDS}"}
    # worst-case adaptive attacker in feature space
    A = {}
    for md in ("unbounded", "budgeted"):
        o = m.run(worst_case_attack(m, 20000, md), md)
        A[md] = {"max_baseline_displacement": float(o["drift"].max()),
                 "inputs_flagged": int(o["flag"].sum()),
                 "alarm_step": int(np.argmax(o["frozen"])) + 1 if o["frozen"].any() else None}
    A["budgeted"]["T3_predicted_alarm_step"] = float(m.B / (ETA * 0.99 * m.tau))
    R["worst_case_attack_20000_steps"] = A
    # C1 calibration check: empirical per-step exceedance of B on long clean unbounded run
    long_clean = feat(np.clip(Xte[r.integers(0, len(Xte), 20000)] + r.normal(0, .02, (20000, 64)), 0, 1), kind)
    d = m.run(long_clean, "unbounded")["drift"][500:]
    R["calibration_check"] = {"predicted_exceed_rate": 0.001, "empirical_exceed_rate": float((d > m.B).mean())}
    res["detectors"][kind_label] = R

for k, R in res["detectors"].items():
    print(f"\n=== {k} (p={R['p']}, B={R['B_rule_q0.999']:.3f}, T1 bound={R['bound_T1']:.3f}) ===")
    for md in ("static", "unbounded", "budgeted"): print(f"  {md:10s}", R[md])
    print("  worst-case attack:", R["worst_case_attack_20000_steps"])
    print("  calibration:", R["calibration_check"])
def rnd(o):
    if isinstance(o, float): return round(o, 4)
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list): return [rnd(v) for v in o]
    return o
json.dump(rnd(res), open(os.path.join(os.path.dirname(__file__), "..", "docs", "results.json"), "w"), indent=2)
