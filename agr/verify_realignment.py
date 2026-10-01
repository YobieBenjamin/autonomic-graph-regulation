# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''B2 proof: re-record episodes with the FIXED tap and check new[t] == old_stored[t+1] (the verified one-step shift),
and that tokens are identical. If this holds, realigning old recordings by one step is exact.'''
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
SEED, N_EP = int(sys.argv[1]), int(sys.argv[2])
_a = sys.argv; sys.argv = ['recorder.py', '800', '800']; import recorder; sys.argv = _a; recorder.N = 800
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
import layertap
model, tok = load(recorder.PATIENT); layertap.install()
old = {r['idx']: r for r in (json.loads(l) for l in open(os.path.join(ROOT, 'data', 'agr', 'episodes_L_seed%d.jsonl' % SEED)))}
E = recorder.episodes(SEED); worst, same_tok = 0.0, 0
for idx in range(N_EP):
    cat, q, truth = E[idx]
    ids = tok.apply_chat_template([dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content=q)], add_generation_prompt=True, reasoning_effort='low')
    layertap.reset(); lay, toks = [], []
    for (t, _), _ in zip(generate_step(mx.array(ids), model, max_tokens=800), range(800)):
        toks.append(int(t)); lay.append(layertap.pop())
        if int(t) in tok.eos_token_ids: break
    new = np.stack(lay); st = np.load(os.path.join(ROOT, 'data', 'agr', 'layers_seed%d' % SEED, '%d.npy' % idx))
    same_tok += int(len(toks) == old[idx]['n_tokens'])
    n = min(len(new), len(st) - 1); d = float(np.max(np.abs(new[:n] - st[1:n + 1]) / (np.abs(st[1:n + 1]) + 1e-6)))
    worst = max(worst, d); print(idx, cat, 'tokens', len(toks), 'vs', old[idx]['n_tokens'], '| max rel diff new[t] vs old[t+1]: %.2e' % d, flush=True)
print('SUMMARY: episodes', N_EP, '| identical token counts', same_tok, '| worst relative difference %.2e' % worst)
