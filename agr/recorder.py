#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''AGR vitals recorder (TRUSTED host code; MLX needs the Apple GPU). Runs the patient model on episodes with
machine-verifiable answers and records per-token vitals. No LLM judges anything: correctness is computed.
  tier 0 (physical): per-token latency, effort (tokens spent)   tier 2 (substrate): entropy, top-1 prob, top1-top2 margin
Usage: recorder.py [N_PER_CATEGORY] [MAX_TOKENS]   ->  data/agr/episodes.jsonl'''
import json, os, sys, time, random, datetime, re
import numpy as np
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATIENT = os.path.expanduser('~/.lmstudio/models/mlx-community/gpt-oss-20b-MXFP4-Q8')
SEED = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--seed=')), '0')); sys.argv = [a for a in sys.argv if not a.startswith('--seed=')]
LAYERS = '--layers' in sys.argv; sys.argv = [a for a in sys.argv if a != '--layers']
POWER = '--power' in sys.argv; sys.argv = [a for a in sys.argv if a != '--power']
HS = '--hs' in sys.argv; sys.argv = [a for a in sys.argv if a != '--hs']   # YB-0042: also capture hidden states (requires --layers)
N, MAXT = (int(sys.argv[1]) if len(sys.argv) > 1 else 40), (int(sys.argv[2]) if len(sys.argv) > 2 else 400)
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def episodes(seed=0):
    r = random.Random(seed); E = []
    for i in range(N):
        a, b = r.randint(10 ** 2, 10 ** 3 - 1), r.randint(10, 99); E.append(('mul_easy', f'What is {a} * {b}?', str(a * b)))
        a, b = r.randint(10 ** 4, 10 ** 6 - 1), r.randint(10 ** 4, 10 ** 6 - 1); E.append(('mul_hard', f'What is {a} * {b}?', str(a * b)))
        s = ''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(30, 70))); c = r.choice(s)
        E.append(('count', f'How many times does the letter {c} appear in the string {s}?', str(s.count(c))))
        d = datetime.date(1600, 1, 1) + datetime.timedelta(days=r.randint(0, 292000))
        E.append(('weekday', f'What day of the week was {d.isoformat()}?', DAYS[d.weekday()]))
        a, k, m = r.randint(2, 500), r.randint(20, 300), r.randint(97, 9973); E.append(('modpow', f'What is {a}^{k} mod {m}?', str(pow(a, k, m))))
        a, b = r.randint(10 ** 5, 10 ** 6 - 1), r.randint(10 ** 5, 10 ** 6 - 1); E.append(('add_hard', f'What is {a} + {b}?', str(a + b)))
    return E

def score(final, truth):
    f = final.lower().replace(',', '')
    if truth.isalpha(): return truth in f and sum(d in f for d in DAYS) == 1
    nums = re.findall('-?[0-9]+', f); return bool(nums) and nums[-1] == truth

def main():
    import runguard; runguard.check_alone('recorder'); runguard.write_env(os.path.join(ROOT, 'data', 'agr', 'env', 'recorder_seed%d_%d.json' % (SEED, int(time.time()))), 'recorder', PATIENT, dict(seed=SEED, layers=LAYERS))
    model, tok = load(PATIENT); out = os.path.join(ROOT, 'data', 'agr', ('episodes_power.jsonl' if POWER else 'episodes.jsonl') if SEED == 0 else 'episodes_seed' + str(SEED) + '.jsonl')
    ps = None
    if LAYERS:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import layertap; layertap.install()
        out = os.path.join(ROOT, 'data', 'agr', 'episodes_L_seed' + str(SEED) + '.jsonl'); LD = os.path.join(ROOT, 'data', 'agr', 'layers_seed' + str(SEED)); os.makedirs(LD, exist_ok=True)
        done = sum(1 for _ in open(out)) if os.path.exists(out) else 0
    if HS:
        import hstap; hstap.install(); HD = os.path.join(ROOT, 'data', 'agr', 'hs_seed' + str(SEED)); os.makedirs(HD, exist_ok=True)
        out = os.path.join(ROOT, 'data', 'agr', 'episodes_LH_seed' + str(SEED) + '.jsonl'); LD = os.path.join(ROOT, 'data', 'agr', 'layers_LH_seed' + str(SEED)); os.makedirs(LD, exist_ok=True)   # new files: never mixes with earlier recordings
    if POWER:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from power import PowerSampler; ps = PowerSampler(); time.sleep(1.0)
    done = sum(1 for _ in open(out)) if os.path.exists(out) else 0
    E = episodes(SEED); print('episodes', len(E), 'already done', done, flush=True)
    for idx, (cat, q, truth) in enumerate(E):
        if idx < done: continue
        msgs = [dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content=q)]
        try: ids = tok.apply_chat_template(msgs, add_generation_prompt=True, reasoning_effort='low')
        except TypeError: ids = tok.apply_chat_template(msgs, add_generation_prompt=True)
        ent, p1, marg, lat, toks, lay = [], [], [], [], [], []; t0 = time.perf_counter(); prev = t0
        if LAYERS: layertap.reset()
        if HS: hstap.reset(); hsl = []
        for (token, logprobs), _ in zip(generate_step(mx.array(ids), model, max_tokens=MAXT), range(MAXT)):
            p = mx.exp(logprobs); top = mx.topk(logprobs, 2)
            e, a, b = float(-(p * logprobs).sum()), float(mx.max(logprobs)), float(mx.min(top))
            now = time.perf_counter(); lat.append(now - prev); prev = now
            if LAYERS: lay.append(layertap.pop())
            if HS: hsl.append(hstap.pop())
            ent.append(round(e, 5)); p1.append(round(float(mx.exp(mx.array(a))), 5)); marg.append(round(a - b, 5)); toks.append(int(token))
            if int(token) in tok.eos_token_ids: break
        text = tok.decode(toks); fi = text.rfind('final<|message|>')
        final = text[fi + len('final<|message|>'):].replace('<|return|>', '').strip() if fi >= 0 else ''
        fstart = len(tok.encode(text[:fi + len('final<|message|>')], add_special_tokens=False)) if fi >= 0 else len(toks)
        t_end = time.perf_counter()
        pw = ps.window(t0, t_end) if ps else []
        rec = dict(toks=toks, idx=idx, t_unix=round(time.time() - (t_end - t0), 3), cat=cat, q=q, truth=truth, final=final[:200], text=text if SEED else None, answered=fi >= 0, correct=(fi >= 0 and score(final, truth)),
                   n_tokens=len(toks), final_start=min(fstart, len(toks)), wall=round(time.perf_counter() - t0, 4),
                   entropy=ent, p_top1=p1, margin=marg, latency=[round(x, 5) for x in lat],
                   power=[[round(t - t0, 4), g, c] for t, g, c in pw] if ps else None)
        if LAYERS: np.save(os.path.join(LD, str(idx) + '.npy'), np.stack(lay).astype(np.float32))
        if HS:   # probe inputs at each checkpoint t: the reading for the last token before t, and the mean over tokens before t
            Hs = np.stack(hsl).astype(np.float32); snap = {}
            for t in (48, 96, 192, 384):
                if t < len(hsl): snap['last_%d' % t] = Hs[t - 1].astype(np.float16); snap['mean_%d' % t] = Hs[:t].mean(0).astype(np.float16)
            np.savez_compressed(os.path.join(HD, str(idx) + '.npz'), **snap)
        open(out, 'a').write(json.dumps(rec) + chr(10))
        if ps and ps.error: print('POWER SAMPLER ERROR', ps.error, flush=True)
        print(idx, cat, 'correct' if rec['correct'] else ('WRONG' if rec['answered'] else 'NO-ANSWER'), len(toks), 'tok', rec['wall'], 's', flush=True)

if __name__ == '__main__': main()
