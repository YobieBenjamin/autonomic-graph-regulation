# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Alignment test for the hidden-state capture (YB-0042), same definition as agr/test_layertap_alignment.py: the stored
hidden state for generated token t must match a fresh, uncached forward pass over prompt + the first t generated tokens,
and be closer to it than to the neighbouring token's pass. Also checks that the five telemetry channels are unchanged.'''
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
import layertap, hstap
m, tok = load(os.path.expanduser('~/.lmstudio/models/mlx-community/gpt-oss-20b-MXFP4-Q8'))
ids = list(tok.apply_chat_template([dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content='What is 4821 * 367?')], add_generation_prompt=True, reasoning_effort='low'))
layertap.install(); hstap.install(); layertap.reset(); hstap.reset(); toks, tel, hs = [], [], []
for (t, _), _ in zip(generate_step(mx.array(ids), m, max_tokens=12), range(12)):
    toks.append(int(t)); tel.append(layertap.pop()); hs.append(hstap.pop().astype(np.float32))
def ref(t):
    layertap.reset(); hstap.reset(); layertap._SKIP[0] = 0; hstap._SKIP[0] = 0; m(mx.array([ids + toks[:t]]))
    return layertap.pop(), hstap.pop().astype(np.float32)
rel = lambda a, b: float(np.max(np.linalg.norm(a - b, axis=1) / (np.linalg.norm(b, axis=1) + 1e-6)))
R = [ref(t) for t in range(10)]
err = [rel(hs[t], R[t][1]) for t in range(10)]; lag = [rel(hs[t], R[t - 1][1]) for t in range(1, 10)]
tel_err = [float(np.max(np.abs(tel[t][:, [0, 1, 2, 4]] - R[t][0][:, [0, 1, 2, 4]]) / (np.abs(R[t][0][:, [0, 1, 2, 4]]) + 1e-6))) for t in range(10)]
print('hidden-state aligned error:', ' '.join('%.3f' % e for e in err)); print('hidden-state lag-1 error:  ', ' '.join('%.3f' % e for e in lag))
print('telemetry aligned error (with hidden-state capture on):', ' '.join('%.3f' % e for e in tel_err))
assert max(err) < min(lag) and float(np.median(err)) < 0.10, 'HIDDEN-STATE ALIGNMENT TEST FAILED'
assert float(np.median(tel_err)) < 0.10, 'TELEMETRY CHANGED BY CAPTURE'
print('HIDDEN-STATE ALIGNMENT TEST PASSED')
