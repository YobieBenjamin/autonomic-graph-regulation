#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0051 post-answer review recorder (copy of agr/selfcons_yb0050.py; changes: 8 samples instead of 4, seeds 27 to 38, file names,
an optional --seed). Self-consistency exactly as agr/monitors.py (YB-0012): extra samples of the monitored model at temperature 0.8,
system prompt "Answer with only the final answer, no explanation.", reasoning effort low, at most 800 tokens; disagreement = fraction of
samples whose normalised answer differs from the original greedy answer (an empty answer counts as different). Sample k uses random
seed 1000*idx + k, so samples 0-3 are exactly the YB-0050 k = 4 procedure: d4 = disagreement over samples 0-3, d8 over samples 0-7.
Wall-clock seconds are recorded after sample 3 (k = 4 cost) and after sample 7 (k = 8 cost). Resumable.
Usage: selfcons_yb0051.py [--seed S] [--limit N]  -> data/agr/selfcons_yb0051_seed<S>.jsonl'''
import json, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
LIMIT = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else None
ONE = sys.argv[sys.argv.index('--seed') + 1] if '--seed' in sys.argv else None
SMOKE = os.environ.get('SMOKE_SEED')   # smoke test on a derivation seed only, never a test seed, before the plan is timestamped
TEST = tuple(str(s) for s in range(27, 39)); K = 8
SEEDS = (SMOKE,) if SMOKE else (ONE,) if ONE else TEST
assert not SMOKE or SMOKE not in TEST
assert not ONE or ONE in TEST
import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import generate_step
from mlx_lm.sample_utils import make_sampler
_argv = sys.argv; sys.argv = ['recorder.py']; from recorder import PATIENT; sys.argv = _argv
model, tok = load(PATIENT)
def sample_answer(q, seed):                                   # verbatim from agr/monitors.py
    mx.random.seed(seed)
    msgs = [dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content=q)]
    try: ids = tok.apply_chat_template(msgs, add_generation_prompt=True, reasoning_effort='low')
    except TypeError: ids = tok.apply_chat_template(msgs, add_generation_prompt=True)
    toks = []
    for (t, _), _ in zip(generate_step(mx.array(ids), model, max_tokens=800, sampler=make_sampler(temp=0.8)), range(800)):
        toks.append(int(t))
        if int(t) in tok.eos_token_ids: break
    text = tok.decode(toks); fi = text.rfind('final<|message|>')
    return text[fi + len('final<|message|>'):].replace('<|return|>', '').strip() if fi >= 0 else ''
def norm(a):                                                  # verbatim from agr/monitors.py
    a = a.lower().replace(',', ''); n = re.findall('-?[0-9]+', a)
    return n[-1] if n else re.sub('[^a-z]', '', a)
for S in SEEDS:
    src = os.path.join(ROOT, 'data', 'agr', 'episodes_LH_seed%s.jsonl' % S); out = os.path.join(ROOT, 'data', 'agr', ('selfcons_yb0051_smoke_seed%s.jsonl' if SMOKE else 'selfcons_yb0051_seed%s.jsonl') % S)
    done = set(); n = 0
    if os.path.exists(out):   # tolerate a truncated last line from a power loss: drop it, keep every complete record
        good = []
        for l in open(out):
            try: done.add(json.loads(l)['idx']); good.append(l if l.endswith(chr(10)) else l + chr(10))
            except ValueError: print('dropping truncated line in', out, flush=True)
        open(out, 'w').writelines(good)
    for l in open(src):
        r = json.loads(l)
        if not r['answered'] or r['idx'] in done: continue
        if LIMIT is not None and n >= LIMIT: break
        t0 = time.time(); ans = []
        for k in range(K):
            ans.append(sample_answer(r['q'], 1000 * r['idx'] + k))
            if k == 3: w4 = time.time() - t0
        w8 = time.time() - t0; base = norm(r['final']); dif = [norm(a) != base for a in ans]
        rec = dict(idx=r['idx'], seed=S, answers=[a[:40] for a in ans], d4=sum(dif[:4]) / 4.0, d8=sum(dif) / 8.0,
                   review_seconds_k4=round(w4, 3), review_seconds_k8=round(w8, 3))
        open(out, 'a').write(json.dumps(rec) + chr(10)); n += 1
        print(S, r['idx'], rec['d4'], rec['d8'], rec['review_seconds_k8'], 's', flush=True)
print('DONE')
