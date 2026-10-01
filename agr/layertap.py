# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Layer telemetry for the patient (gpt-oss, mlx_lm TransformerBlock). Wraps the block's forward so it computes exactly
the same output, and additionally records, for the newest token at each of the 24 layers:
  [0] ||attention update||  [1] ||expert (MoE) update||  [2] ||residual out||  [3] cos(residual in, out)  [4] router entropy
Usage: import layertap; layertap.install(); after each generated token call layertap.pop() -> (24, 5) float32 array.'''
import numpy as np
import mlx.core as mx
from mlx_lm.models import gpt_oss
_REC = []
_ORIG = gpt_oss.TransformerBlock.__call__

def _tapped(self, x, mask, cache=None):
    r1 = x
    a = self.self_attn(self.input_layernorm(x), mask, cache)
    x1 = r1 + a
    h2 = self.post_attention_layernorm(x1)
    m = self.mlp(h2)
    out = x1 + m
    f = lambda t: t[:, -1, :].astype(mx.float32)
    xi, xo = f(r1), f(out)
    lg = f(self.mlp.router(h2)); p = mx.softmax(lg, axis=-1)
    ent = -(p * mx.log(p + 1e-12)).sum(-1)
    cos = (xi * xo).sum(-1) / (mx.linalg.norm(xi, axis=-1) * mx.linalg.norm(xo, axis=-1) + 1e-9)
    _REC.append(mx.concatenate([mx.linalg.norm(f(a), axis=-1), mx.linalg.norm(f(m), axis=-1), mx.linalg.norm(xo, axis=-1), cos, ent]))
    return out

def install(): gpt_oss.TransformerBlock.__call__ = _tapped
def uninstall(): gpt_oss.TransformerBlock.__call__ = _ORIG
_SKIP = [0]

def reset():
    '''Clear the buffer and arrange to discard the prompt (prefill) pass. Fix for audit finding F4: mlx_lm runs the
    prompt through the model before the pass that produces token 0, so the first N_LAYERS records belong to the prompt,
    not to any generated token. Without this, reading t came from the pass that produced token t-1.'''
    _REC.clear(); _SKIP[0] = 1
N_LAYERS = 24

def pop():
    '''Telemetry for the OLDEST computed step: (24, 5). mlx_lm pre-computes the next token before yielding the
    current one, so the buffer may hold one extra step; taking the oldest 24 records keeps token alignment exact.'''
    if _SKIP[0] and len(_REC) >= N_LAYERS: del _REC[:N_LAYERS]; _SKIP[0] = 0   # discard the prompt pass (F4)
    if len(_REC) < N_LAYERS: return None
    step = _REC[:N_LAYERS]; del _REC[:N_LAYERS]
    mx.eval(step); return np.array(mx.stack(step)).reshape(N_LAYERS, 5)
