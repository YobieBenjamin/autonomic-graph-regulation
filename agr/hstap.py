# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Hidden-state capture for YB-0042 (probe baseline). Wraps layertap's tapped forward WITHOUT changing it: the wrapper
calls layertap._tapped (so the five telemetry channels are computed exactly as before) and keeps the newest token's
residual-stream output at the selected layers. Alignment is identical to layertap (prompt pass discarded; the reading
for generated token t comes from the pass over prompt + the first t generated tokens). Values stored as float16.
Usage: import layertap, hstap; layertap.install(); hstap.install(); per episode hstap.reset(); per token hstap.pop().'''
import numpy as np
import mlx.core as mx
from mlx_lm.models import gpt_oss
import layertap
LAYERS = (6, 12, 18, 23)
N_LAYERS = layertap.N_LAYERS
_HS, _CNT, _SKIP = [], [0], [0]

def _wrap(self, x, mask, cache=None):
    out = layertap._tapped(self, x, mask, cache)
    l = _CNT[0] % N_LAYERS; _CNT[0] += 1
    if l in LAYERS: _HS.append(out[:, -1, :].astype(mx.float16))
    return out

def install(): gpt_oss.TransformerBlock.__call__ = _wrap

def reset():
    _HS.clear(); _CNT[0] = 0; _SKIP[0] = 1

def pop():
    '''Hidden states for the OLDEST computed step: (len(LAYERS), d_model) float16, aligned like layertap.pop().'''
    k = len(LAYERS)
    if _SKIP[0] and len(_HS) >= k: del _HS[:k]; _SKIP[0] = 0
    if len(_HS) < k: return None
    step = _HS[:k]; del _HS[:k]
    mx.eval(step); return np.array(mx.stack(step)).reshape(k, -1)
