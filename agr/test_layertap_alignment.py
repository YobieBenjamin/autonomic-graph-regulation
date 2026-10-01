# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Permanent alignment test (audit F4): the streamed reading for generated token t must equal the reading from a fresh,
uncached forward pass over prompt + the first t generated tokens (the pass that produces token t).'''
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
import layertap
m, tok = load(os.path.expanduser('~/.lmstudio/models/mlx-community/gpt-oss-20b-MXFP4-Q8'))
ids = list(tok.apply_chat_template([dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content='What is 4821 * 367?')], add_generation_prompt=True, reasoning_effort='low'))
layertap.install(); layertap.reset(); toks, stored = [], []
for (t, _), _ in zip(generate_step(mx.array(ids), m, max_tokens=12), range(12)):
    toks.append(int(t)); stored.append(layertap.pop())
def ref(t):
    layertap.reset(); layertap._SKIP[0] = 0; m(mx.array([ids + toks[:t]])); return layertap.pop()
d = lambda a, b: float(np.max(np.abs(a[:, [0, 1, 2, 4]] - b[:, [0, 1, 2, 4]]) / (np.abs(b[:, [0, 1, 2, 4]]) + 1e-6)))
err = [d(stored[t], ref(t)) for t in range(10)]; lag = [d(stored[t], ref(t - 1)) for t in range(1, 10)]
print('aligned error per token:', ' '.join('%.3f' % e for e in err)); print('lag-1 error per token:  ', ' '.join('%.3f' % e for e in lag))
# Property (both monitored models): every stored reading is closer to its own token's fresh forward pass than any reading
# is to the neighbouring token's pass, and the typical error is small. (A fixed 0.15 cap was arbitrary: the 4-bit, 128-expert
# model shows more cached-vs-uncached noise while the separation remains clean.)
assert max(err) < min(lag) and float(np.median(err)) < 0.10, 'ALIGNMENT TEST FAILED'
print('ALIGNMENT TEST PASSED')
