#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Dependency-free .docx -> Markdown for the book: Heading 2/3 -> ##/###, chapter lines -> #,
Consolas paragraphs -> fenced code blocks, bold/italic runs, lists, tables. Usage: docx2md.py in.docx out.md'''
import zipfile, re, sys, xml.etree.ElementTree as ET
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NL, FENCE = chr(10), chr(96) * 3
z = zipfile.ZipFile(sys.argv[1])
names = {s.get(W + 'styleId'): (s.find(W + 'name').get(W + 'val').lower() if s.find(W + 'name') is not None else '')
         for s in ET.fromstring(z.read('word/styles.xml')).iter(W + 'style')}
out, code = [], []
def flush():
    if code: out.append(FENCE + 'python' + NL + NL.join(code) + NL + FENCE); code.clear()
for el in ET.fromstring(z.read('word/document.xml')).find(W + 'body'):
    if el.tag == W + 'tbl':
        flush(); rows = [[''.join(t.text or '' for t in c.iter(W + 't')).strip() for c in r.iter(W + 'tc')] for r in el.iter(W + 'tr')]
        for k, r in enumerate(rows):
            out.append('| ' + ' | '.join(r) + ' |')
            if k == 0: out.append('|' + ' --- |' * len(r))
        continue
    if el.tag != W + 'p': continue
    ps = el.find(W + 'pPr/' + W + 'pStyle'); sn = names.get(ps.get(W + 'val'), '') if ps is not None else ''
    f = el.find('.//' + W + 'rFonts'); mono = f is not None and (f.get(W + 'ascii') or '').lower() in ('consolas', 'courier new', 'menlo')
    raw = ''.join((x.text or '') if x.tag == W + 't' else (chr(9) if x.tag == W + 'tab' else '') for x in el.iter() if x.tag in (W + 't', W + 'tab'))
    if mono:
        code.append(raw.rstrip()); continue
    flush()
    runs = []
    for r in el.iter(W + 'r'):
        t = ''.join((x.text or '') if x.tag == W + 't' else chr(9) for x in r if x.tag in (W + 't', W + 'tab'))
        if not t.strip(): runs.append(t); continue
        rp = r.find(W + 'rPr'); b = rp is not None and rp.find(W + 'b') is not None; i = rp is not None and rp.find(W + 'i') is not None
        runs.append('**' + t + '**' if b else ('*' + t + '*' if i else t))
    txt = re.sub('[*]{4}', '', ''.join(runs)).strip()
    if not txt: continue
    plain = txt.replace('*', '')
    m = re.search('heading ?([1-6])', sn)
    if m: txt = '#' * int(m.group(1)) + ' ' + plain
    elif sn == 'title' or re.match('(chapter|part|prologue|epilogue|introduction|preface|appendix|afterword|conclusion)[ :0-9ivx]', plain, re.I) and len(plain) < 120:
        txt = '# ' + plain
    elif el.find(W + 'pPr/' + W + 'numPr') is not None: txt = '- ' + txt
    out.append(txt)
flush()
md = (NL + NL).join(out) + NL
open(sys.argv[2], 'w').write(md)
print('words', len(md.split()), '| code blocks', md.count(FENCE) // 2, '| h1', sum(l.startswith('# ') for l in out), '| h2', sum(l.startswith('## ') for l in out), '| h3', sum(l.startswith('### ') for l in out))
