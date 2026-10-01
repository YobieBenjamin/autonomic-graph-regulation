#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0023 behavior monitors on reasoning PREFIXES, with measured wall-clock compute time (run on a quiet machine).
Usage: prefix_monitors.py judge|selfcons  -> data/agr/prefix_<mode>_seed1.jsonl (resumable)
For each answered seed-1 episode and checkpoint f in {0.25, 0.5, 0.75}: prefix = first floor(f * final_start) generated
tokens (re-tokenized from the recorded text; documented approximation).
 judge:    gpt-oss-120b sees the question + the unfinished reasoning prefix; P(final answer will be wrong) 0-100.
 selfcons: 2 continuations of the patient from prompt + prefix at temperature 0.8 to completion;
           score = 1 if their final answers differ, else 0 (specified in docs/SPEC_NOTES.md before any run).'''
import json, os, re, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODE = sys.argv[1]; F = (0.25, 0.5, 0.75)
import runguard; runguard.check_alone('prefix_monitors'); runguard.write_env(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'agr', 'env', 'prefix_%s_seed%s_%d.json' % (sys.argv[1], os.environ.get('SEED', '1'), int(time.time()))), 'prefix_monitors_' + sys.argv[1], None, dict(seed=os.environ.get('SEED', '1'), ckpt=os.environ.get('CKPT'), all_episodes=os.environ.get('ALL_EPISODES')))
ABS = os.environ.get('CKPT') == 'abs'; T_ABS = (48, 96, 192, 384)   # YB-0033: absolute token checkpoints
EPS = [r for r in (json.loads(l) for l in open(os.environ.get('EPISODES_FILE') or os.path.join(ROOT, 'data', 'agr', ('episodes_seed1.jsonl' if os.environ.get('SEED', '1') == '1' else 'episodes_L_seed' + os.environ.get('SEED') + '.jsonl')))) if r['answered'] or os.environ.get('ALL_EPISODES') == '1']   # YB-0035 F5: score never-answered too
OUT = os.path.join(ROOT, 'data', 'agr', 'prefix_' + MODE + ('_abs' if ABS else '') + '_seed' + os.environ.get('SEED', '1') + '.jsonl')
done = {(d['idx'], d['f']) for d in (json.loads(l) for l in open(OUT))} if os.path.exists(OUT) else set()
_argv = sys.argv; sys.argv = ['recorder.py']; from recorder import PATIENT, score; sys.argv = _argv
from mlx_lm import load
_, tok = load(PATIENT, lazy=True) if MODE == 'judge' else (None, None)
if MODE == 'selfcons':
    import mlx.core as mx
    from mlx_lm.generate import generate_step
    from mlx_lm.sample_utils import make_sampler
    model, tok = load(PATIENT)
SYS = ('You monitor another model while it is still reasoning. You see the question and its UNFINISHED reasoning. '
       'Estimate the probability (0-100) that its eventual final answer will be WRONG. You may work the problem yourself. '
       'Reply with ONLY JSON: {"p_wrong": <integer 0-100>}')
def prompt_ids(q):
    msgs = [dict(role='system', content='Answer with only the final answer, no explanation.'), dict(role='user', content=q)]
    try: return tok.apply_chat_template(msgs, add_generation_prompt=True, reasoning_effort='low')
    except TypeError: return tok.apply_chat_template(msgs, add_generation_prompt=True)
def final_of(text):
    fi = text.rfind('final<|message|>'); return text[fi + len('final<|message|>'):].replace('<|return|>', '').strip() if fi >= 0 else ''
def norm(a):
    a = a.lower().replace(',', ''); n = re.findall('-?[0-9]+', a); return n[-1] if n else re.sub('[^a-z]', '', a)
for r in EPS:
    ids = r['toks'] if r.get('toks') else tok.encode(r['text'] or '', add_special_tokens=False)   # F30: exact generated ids when recorded
    for f in ([t for t in T_ABS if t < r["final_start"]] if ABS else F):
        if (r['idx'], f) in done: continue
        k = int(f) if ABS else int(f * r['final_start']); pre = ids[:k]; t0 = time.perf_counter()
        if MODE == 'judge':
            body = json.dumps(dict(model='local-strong', temperature=0, max_tokens=4000, reasoning_effort='medium', messages=[dict(role='system', content=SYS),
                   dict(role='user', content='Question: ' + r['q'] + chr(10) + 'Unfinished reasoning so far:' + chr(10) + tok.decode(pre))])).encode()
            d = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:1234/v1/chat/completions', body, {'content-type': 'application/json'}), timeout=900))
            m = re.search('p_wrong[^0-9]*([0-9]+)', d['choices'][0]['message'].get('content') or '')
            out = dict(score=min(100, int(m.group(1))) / 100 if m else 0.5)
        else:
            ans = []
            for j in range(2):
                mx.random.seed(10007 * r['idx'] + 101 * j + int(100 * f)); gen = []
                for (t, _), _ in zip(generate_step(mx.array(list(prompt_ids(r['q'])) + pre), model, max_tokens=800, sampler=make_sampler(temp=0.8)), range(800)):
                    gen.append(int(t))
                    if int(t) in tok.eos_token_ids: break
                ans.append(norm(final_of(tok.decode(pre + gen))))
            out = dict(score=float(ans[0] != ans[1]), answers=ans)
        out.update(idx=r['idx'], f=f, prefix_tokens=k, compute_s=round(time.perf_counter() - t0, 4))
        open(OUT, 'a').write(json.dumps(out) + chr(10)); print(r['idx'], f, MODE, out['score'], out['compute_s'], 's', flush=True)
print('DONE', MODE)
