#!/usr/bin/env python3
"""Read ONLY PDFs placed in papers_inbox (never ~/Downloads or anywhere else), identify each by title words on its first pages,
file it as papers_inbox/<id>.pdf, then rerun the full-text verification pipeline and print a summary."""
import os, glob, re, shutil, subprocess, time, warnings, logging
logging.disable(logging.WARNING); warnings.filterwarnings('ignore')
from pypdf import PdfReader
KEYS = {'gehring1993': ['error detection and compensation', 'gehring'], 'dehaene1994': ['localization', 'error detection', 'dehaene'],
 'nieuwenhuis2001': ['antisaccade', 'awareness'], 'nambu2002': ['hyperdirect', 'nambu'], 'craig2002': ['interoception', 'how do you feel'],
 'man2019': ['soft robotics', 'feeling machines'], 'scheffer2009': ['early-warning signals', 'critical transitions'],
 'champagne2015': ['responsibility gap', 'automated warfare'], 'robillard2018': ['no such thing as killer robots'],
 'matthias2004': ['responsibility gap', 'learning automata'], 'yeung2004': ['conflict monitoring', 'error-related negativity'],
 'aron2006': ['stop signal', 'subthalamic']}
inbox = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'papers_inbox'); found = {}
for f in sorted(glob.glob(os.path.join(inbox, '*.pdf'))):
    if os.path.splitext(os.path.basename(f))[0] in KEYS: continue
    try: t = ' '.join((p.extract_text() or '') for p in PdfReader(f).pages[:2]).lower()
    except Exception: continue
    t = re.sub(r'\s+', ' ', t)
    for sid, ks in KEYS.items():
        if sid not in found and all(k in t for k in ks):
            shutil.move(f, os.path.join(inbox, sid + '.pdf')); found[sid] = os.path.basename(f); break
for sid in KEYS:
    st = ('filed from ' + found[sid]) if sid in found else ('already in inbox' if os.path.exists(os.path.join(inbox, sid + '.pdf')) else 'MISSING')
    print('%-16s %s' % (sid, st))
subprocess.run(['.venv/bin/python', 'archive/audit/fulltext_verify.py'], cwd=os.path.expanduser('~/Desktop/SAFETY'), stdout=open('/tmp/fv2.log', 'w'), stderr=subprocess.DEVNULL)
print([l for l in open('/tmp/fv2.log').read().splitlines() if l.startswith('SUMMARY')][-1])
