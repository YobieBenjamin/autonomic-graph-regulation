# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Audit B9: complete verification of the one-step resynchronization of old recordings (agr/pack_realigned.py).
Re-records seed-2 episodes 0..N-1 with the FIXED tap and compares each new reading new[t] with the old stored readings
old[t+1] (the claimed shift) and old[t] (no shift). Episodes whose re-recording diverged from the original generation
(different token count or entropy trace; see CORRECTIONS S1) are reported and excluded from the shift statistics.
Errors are in units of each channel's standard deviation over the episode. Writes archive/audit/artifacts/shift_verification.json.'''
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
N_EP = int(sys.argv[1]) if len(sys.argv) > 1 else 20
import runguard; runguard.check_alone('verify_shift')
_a = sys.argv; sys.argv = ['recorder.py', '800', '800']; import recorder; sys.argv = _a; recorder.N = 800
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
import layertap
model, tok = load(recorder.PATIENT); layertap.install(); E = recorder.episodes(2)
old = {r['idx']: r for r in (json.loads(l) for l in open(os.path.join(ROOT, 'data', 'agr', 'episodes_L_seed2.jsonl')))}
rows = []
for idx in range(N_EP):
    ids = tok.apply_chat_template([dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content=E[idx][1])], add_generation_prompt=True, reasoning_effort='low')
    layertap.reset(); toks, lay, ent = [], [], []
    for (t, lp), _ in zip(generate_step(mx.array(ids), model, max_tokens=800), range(800)):
        toks.append(int(t)); lay.append(layertap.pop()); p = mx.exp(lp); ent.append(float(-(p * lp).sum()))
        if int(t) in tok.eos_token_ids: break
    new = np.stack(lay); st = np.load(os.path.join(ROOT, 'data', 'agr', 'layers_seed2', '%d.npy' % idx)); o = old[idx]
    # Same generation = identical generated text (the original recording saved it). An earlier version compared entropy traces
    # within 1e-3; that failed on every episode because this script computes entropy differently and cross-session numeric
    # noise (CORRECTIONS S1) exceeds 1e-3 even when the tokens are identical.
    same = tok.decode(toks) == (o.get('text') or '')
    row = dict(idx=idx, cat=E[idx][0], new_tokens=len(toks), old_tokens=o['n_tokens'], same_generation=bool(same))
    if same:
        n = len(new) - 1; sc = st[:n + 1].reshape(-1, 120).std(0) + 1e-9
        e1 = np.abs((new[:n] - st[1:n + 1]).reshape(n, 120)) / sc; e0 = np.abs((new[:n] - st[:n]).reshape(n, 120)) / sc
        row.update(shift_median=float(np.median(e1)), shift_p99=float(np.percentile(e1, 99)), shift_max=float(e1.max()), noshift_median=float(np.median(e0)))
    rows.append(row); print(json.dumps(row), flush=True)
ok = [r for r in rows if r['same_generation']]
summary = dict(episodes=len(rows), same_generation=len(ok), diverged=[r['idx'] for r in rows if not r['same_generation']],
               shift_median_of_medians=float(np.median([r['shift_median'] for r in ok])) if ok else None,
               shift_worst_p99=float(max(r['shift_p99'] for r in ok)) if ok else None, shift_worst_max=float(max(r['shift_max'] for r in ok)) if ok else None,
               noshift_median_of_medians=float(np.median([r['noshift_median'] for r in ok])) if ok else None,
               shift_better_than_noshift_in_every_episode=all(r['shift_median'] < r['noshift_median'] for r in ok))
os.makedirs(os.path.join(ROOT, 'archive', 'audit', 'artifacts'), exist_ok=True)
json.dump(dict(summary=summary, episodes=rows), open(os.path.join(ROOT, 'archive', 'audit', 'artifacts', 'shift_verification.json'), 'w'), indent=1)
print('SUMMARY', json.dumps(summary))
