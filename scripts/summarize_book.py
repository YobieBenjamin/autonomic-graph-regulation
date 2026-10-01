#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Summarize the book with the LOCAL model (free): ~25k-char chunks aligned to ## sections.
Writes docs/book/SUMMARY.md. Focus: the author's theses, biology/brain/stress/instinct content, safety claims, math.'''
import json, os, re, sys, urllib.request, time
NL = chr(10); src, dst = 'docs/book/Garbage_In_Gospel_Out.md', 'docs/book/SUMMARY.md'
text = open(src).read(); parts = re.split('(?m)^(?=## )', text); chunks, cur = [], ''
for p in parts:
    if len(cur) + len(p) > 25000 and cur: chunks.append(cur); cur = ''
    cur += p
chunks.append(cur)
SYS = ('You summarize one chunk of the book Garbage In, Gospel Out (about large language models) for its author, an AI-safety researcher. '
       'Be faithful: only what the text says. Output markdown with these headings: Sections covered (list the ## titles); '
       'Summary (5-8 sentences); Author theses and opinions (bullets, near-verbatim where short); '
       'Biology / brain / human cognition analogies (bullets, or None); Safety and alignment claims (bullets, or None); '
       'Key math or algorithms (bullets, or None). Under 450 words. Skip code details.')
out = ['# Garbage In, Gospel Out: chunk summaries (local model, gpt-oss-120b)', '']
for i, c in enumerate(chunks, 1):
    body = json.dumps(dict(model='local-strong', max_tokens=3000, temperature=0.2, reasoning_effort='low',
                           messages=[dict(role='system', content=SYS), dict(role='user', content=c)])).encode()
    t = time.time()
    d = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:1234/v1/chat/completions', body, {'content-type': 'application/json'}), timeout=1800))
    out += ['## Chunk ' + str(i) + ' of ' + str(len(chunks)), d['choices'][0]['message']['content'] or '(empty)', '']
    open(dst, 'w').write(NL.join(out)); print('chunk', i, '/', len(chunks), round(time.time() - t), 's', flush=True)
print('DONE', dst)
