# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0018: metabolic vitals (tier 0, pure physics): GPU/CPU power from powermetrics aligned to each episode.
ctypes binding + NumPy reference + per-episode features (power, energy per token, timing for comparison).'''
import ctypes, gzip, json, os
import numpy as np
_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcore.so'))
_P = ctypes.POINTER(ctypes.c_double)
_L.power_features.argtypes = [_P, _P, ctypes.c_int, _P]

def power_features(t, p):
    t, p = np.ascontiguousarray(t, float), np.ascontiguousarray(p, float); out = np.zeros(5)
    return np.full(5, np.nan) if _L.power_features(t.ctypes.data_as(_P), p.ctypes.data_as(_P), len(t), out.ctypes.data_as(_P)) else out

def power_features_ref(t, p):
    t, p = np.asarray(t, float), np.asarray(p, float); E = np.sum(0.5 * (p[1:] + p[:-1]) * np.diff(t)); d = t[-1] - t[0]
    return np.array([E / 1000, E / d / 1000, p.max() / 1000, np.sqrt(np.mean(np.diff(p) ** 2)) / 1000, d])

def load(path): return [json.loads(l) for l in gzip.open(path, 'rt')]

def episode_features(r):
    pw = [x for x in (r.get('power') or []) if x[1] is not None]
    t = [x[0] for x in pw]; g = [x[1] for x in pw]; c = [x[2] or 0.0 for x in pw]
    fg, fc = power_features(t, g), power_features(t, c)
    n = max(r['n_tokens'], 1)
    metab = dict(gpu_energy_J=fg[0], gpu_mean_W=fg[1], gpu_peak_W=fg[2], gpu_rmssd_W=fg[3], cpu_mean_W=fc[1], cpu_rmssd_W=fc[3],
                 gpu_J_per_token=fg[0] / n, gpu_cpu_ratio=(fg[1] / fc[1]) if fc[1] and fc[1] > 0 else np.nan, samples=float(len(pw)))
    lat = np.array(r['latency'][1:] or [0.0])
    timing = dict(lat_mean=lat.mean(), lat_std=lat.std(), lat_rmssd=float(np.sqrt(np.mean(np.diff(lat) ** 2))) if len(lat) > 1 else 0.0,
                  effort_tokens=float(r['n_tokens']), wall=float(r['wall']))
    e = np.array(r['entropy']); substrate = dict(ent_mean=e.mean(), ent_max=e.max(), ent_std=e.std())
    return dict(metabolic=metab, timing=timing, substrate=substrate)
