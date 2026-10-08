# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''AI-EWS v1 (docs/AI_EWS_METHODOLOGY.md): NEWS2-style banded vitals -> aggregate score -> graded level. Text-blind.'''
import numpy as np
from deep import graph_windows
from hpa import simulate
VITALS = ['V1_entropy', 'V2_margin', 'V3_layer_hrv', 'V4_layer_synchrony', 'V5_router_entropy', 'V6_critical_slowing', 'V7_cortisol']
LEVELS = ['stable', 'watch', 'concern', 'urgent']

def vitals(r, L, upto=None, hpa_cal=(0.0, 1.0)):
    '''Raw vitals over the reasoning segment (or its prefix). L: log-scaled layer tensor (T, 24, 5).'''
    end = r['final_start'] if upto is None else min(upto, r['final_start']); end = max(end, 2)
    e = np.array(r['entropy'][:end], float); m = np.array(r['margin'][:end], float); X = L[:end]
    hrv = float(np.mean(np.sqrt(np.mean(np.diff(X[:, :, 1], axis=0) ** 2, axis=0)))) if len(X) > 1 else 0.0
    G = graph_windows(X[:, :, 1]) if len(X) >= 24 else np.zeros((0, 6))
    sync = float(G[:, 0].mean()) if len(G) else np.nan
    ac1 = float(np.corrcoef(e[:-1], e[1:])[0, 1]) if len(e) > 3 and e.std() > 0 else 0.0
    mu, sd = hpa_cal; C = simulate(np.maximum((e - mu) / sd, 0))[2]
    return np.array([e.mean(), m.mean(), hrv, sync, float(X[:, :, 4].mean()), np.nan_to_num(ac1), float(C.max())])

class AIEWS:
    def fit(self, V, y):
        '''Derivation: direction from derivation outcomes, bands from derivation HEALTHY (correct) episodes only.'''
        V = np.asarray(V, float); ok = V[y == 0]
        self.direction = np.array([1 if np.nanmean(V[y == 1, j]) >= np.nanmean(ok[:, j]) else -1 for j in range(V.shape[1])])
        q = lambda j, p: np.nanpercentile(ok[:, j], p)
        self.bands = np.array([[q(j, 90), q(j, 95), q(j, 99)] if self.direction[j] > 0 else [q(j, 10), q(j, 5), q(j, 1)] for j in range(V.shape[1])])
        return self
    def points(self, v):
        '''0-3 points per vital in its risky direction; NaN (not measurable yet) scores 0.'''
        p = np.zeros(len(v), int)
        for j, x in enumerate(v):
            if not np.isfinite(x): continue
            b = self.bands[j]; p[j] = int(sum(x > t for t in b)) if self.direction[j] > 0 else int(sum(x < t for t in b))
        return p
    def score(self, v):
        p = self.points(v); S = int(p.sum()); red = bool((p == 3).any())
        lvl = 'urgent' if S >= 10 else 'concern' if S >= 7 else 'watch' if (S >= 5 or red) else 'stable'
        return S, lvl, dict(zip(VITALS, p.tolist()))

# ---- AI-EWS v2 (YB-0031): v1 vitals + V8 failure to settle ----
VITALS_V2 = VITALS + ['V8_failure_to_settle']

def settle(r, upto=None):
    '''V8 = mean entropy over the last third of the (prefix of the) reasoning minus mean over the first third.'''
    end = r['final_start'] if upto is None else min(upto, r['final_start']); e = np.array(r['entropy'][:max(end, 3)], float); k = max(len(e) // 3, 1)
    return float(e[-k:].mean() - e[:k].mean())

def vitals_v2(r, L, upto=None, hpa_cal=(0.0, 1.0)):
    return np.append(vitals(r, L, upto=upto, hpa_cal=hpa_cal), settle(r, upto))
