# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Pre-freeze derivation check of C4 against C2 on the reference only (cross-fitted). Writes docs/c4_derivation_check.json.'''
import json, os, sys, numpy as np
sys.path.insert(0, 'tests'); from candidates import derivation_check
if not os.path.exists('data/explore_scores.npz'): print('no reference data'); sys.exit(0)
Z = np.load('data/explore_scores.npz', allow_pickle=True); out = derivation_check({k: Z[k] for k in Z.files})
json.dump(out, open('docs/c4_derivation_check.json', 'w'), indent=1); print('C4 derivation check:', out)
