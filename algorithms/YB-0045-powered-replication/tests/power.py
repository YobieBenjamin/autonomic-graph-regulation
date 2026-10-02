# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Power calculation behind the YB-0045 pre-registration (seventh audit m4: commit the computation). Normal approximation:
the 95% CI half-width of the regulator-minus-judge recall difference scales as 1/sqrt(wrong answers), anchored on YB-0035
(half-width about 0.22 at 40 wrong answers); power = P(lower bound > 0) for a true difference d. Approximate by design.
Writes docs/power.json.'''
import json, math
def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
HW40, N = 0.22, 120
hw = HW40 * math.sqrt(40 / N); se = hw / 1.96
out = dict(method='normal approximation, half-width scaled as 1/sqrt(n_wrong) from YB-0035', anchor_half_width_at_40=HW40, planned_wrong=N,
           half_width=round(hw, 3), power={str(d): round(Phi(d / se - 1.96), 2) for d in (0.175, 0.20, 0.30)})
json.dump(out, open('docs/power.json', 'w'), indent=1); print(json.dumps(out))
