# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Invisibility check: greedy generation with and without the tap must produce identical tokens.'''
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
import layertap_qwen as tap
m, tok = load(os.path.expanduser('~/.lmstudio/models/lmstudio-community/Qwen3-VL-30B-A3B-Instruct-MLX-4bit'))
Q = ['What is 4821 * 367? Think step by step, then end with a line: Final answer: <number>',
     'How many times does the letter r appear in qrtrrbxrwr? Think step by step, then end with a line: Final answer: <number>']
def run(q, tapped, n=160):
    ids = tok.apply_chat_template([dict(role='user', content=q)], add_generation_prompt=True); out, lay = [], []
    if tapped: tap.install(); tap.reset()
    for (t, _), _ in zip(generate_step(mx.array(ids), m, max_tokens=n), range(n)):
        out.append(int(t))
        if tapped: lay.append(tap.pop())
        if int(t) in tok.eos_token_ids: break
    if tapped: tap.uninstall()
    return out, lay
for q in Q:
    a, _ = run(q, False); b, L = run(q, True)
    Ls = np.stack(L); print('identical tokens:', a == b, '| tokens', len(a), '| telemetry', Ls.shape, '| finite', bool(np.isfinite(Ls).all()), '| router entropy L0/L47 %.2f/%.2f' % (Ls[:, 0, 4].mean(), Ls[:, 47, 4].mean()))
print('TEXT:', tok.decode(b)[-160:].replace(chr(10), ' '))
