#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Second patient (external validation): Qwen3-VL-30B-A3B text model, 48 layers, 128 experts, with layertap_qwen.
Same questions and grader as agr/recorder.py. The model is asked to reason step by step and end with 'Final answer:';
the reasoning segment is every token before that marker. Usage: recorder_qwen.py N MAXT --seed=S
Output: data/agr/episodes_Q_seed<S>.jsonl and data/agr/layers_Q_seed<S>/<idx>.npy (resumable).'''
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
N, MAXT = int(sys.argv[1]), int(sys.argv[2]); SEED = int(next(a.split('=')[1] for a in sys.argv if a.startswith('--seed=')))
_a = sys.argv; sys.argv = ['recorder.py', str(N), str(MAXT)]; import recorder; sys.argv = _a
recorder.N = N
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
import layertap_qwen as tap
PATIENT2 = os.path.expanduser('~/.lmstudio/models/lmstudio-community/Qwen3-VL-30B-A3B-Instruct-MLX-4bit')
MARK = 'Final answer:'
def main():
    import runguard; runguard.check_alone('recorder_qwen'); runguard.write_env(os.path.join(ROOT, 'data', 'agr', 'env', 'recorder_qwen_seed%d_%d.json' % (SEED, int(time.time()))), 'recorder_qwen', PATIENT2, dict(seed=SEED))
    model, tok = load(PATIENT2); tap.install()
    out = os.path.join(ROOT, 'data', 'agr', 'episodes_Q_seed' + str(SEED) + '.jsonl'); LD = os.path.join(ROOT, 'data', 'agr', 'layers_Q_seed' + str(SEED)); os.makedirs(LD, exist_ok=True)
    done = sum(1 for _ in open(out)) if os.path.exists(out) else 0; E = recorder.episodes(SEED); print('episodes', len(E), 'already done', done, flush=True)
    for idx, (cat, q, truth) in enumerate(E):
        if idx < done: continue
        ids = tok.apply_chat_template([dict(role='user', content=q + ' Think step by step, then end with a line: ' + MARK + ' <answer>')], add_generation_prompt=True)
        ent, p1, marg, lat, toks, lay = [], [], [], [], [], []; t0 = time.perf_counter(); prev = t0; tap.reset()
        for (token, logprobs), _ in zip(generate_step(mx.array(ids), model, max_tokens=MAXT), range(MAXT)):
            p = mx.exp(logprobs); top = mx.topk(logprobs, 2); e, a, b = float(-(p * logprobs).sum()), float(mx.max(logprobs)), float(mx.min(top))
            now = time.perf_counter(); lat.append(now - prev); prev = now; lay.append(tap.pop())
            ent.append(round(e, 5)); p1.append(round(float(mx.exp(mx.array(a))), 5)); marg.append(round(a - b, 5)); toks.append(int(token))
            if int(token) in tok.eos_token_ids: break
        text = tok.decode(toks); fi = text.rfind(MARK)
        final = text[fi + len(MARK):].replace('<|im_end|>', '').strip() if fi >= 0 else ''
        fstart = len(tok.encode(text[:fi], add_special_tokens=False)) if fi >= 0 else len(toks)
        t_end = time.perf_counter()
        rec = dict(idx=idx, t_unix=round(time.time() - (t_end - t0), 3), cat=cat, q=q, truth=truth, final=final[:200], text=text, answered=fi >= 0,
                   correct=(fi >= 0 and recorder.score(final, truth)), n_tokens=len(toks), final_start=min(fstart, len(toks)), wall=round(t_end - t0, 4),
                   entropy=ent, p_top1=p1, margin=marg, latency=[round(x, 5) for x in lat], patient='qwen3-vl-30b-a3b')
        np.save(os.path.join(LD, str(idx) + '.npy'), np.stack(lay).astype(np.float32)); open(out, 'a').write(json.dumps(rec) + chr(10))
        print(idx, cat, 'correct' if rec['correct'] else ('WRONG' if rec['answered'] else 'NO-ANSWER'), len(toks), 'tok', rec['wall'], 's', flush=True)
if __name__ == '__main__': main()
