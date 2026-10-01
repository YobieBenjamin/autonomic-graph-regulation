# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""Offline end-to-end test of the miner against a mock Claude API (no tokens spent).
Covers: triage skip, build, broken build -> patch-only repair -> pass in the real sandbox,
recursive hypothesis proposal with a per-run cap, prompt-caching fields, budget accounting.
Run: python3 miner/test_miner.py   (needs Docker; uses a throwaway copy of the repo)"""
import json, os, shutil, subprocess, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = chr(10); TAB = chr(9)
MAKE = ('all: test experiment' + NL + 'build: src/libt.so' + NL + 'src/libt.so: src/t.c' + NL + TAB +
        'gcc -O2 -Wall -Wextra -Werror -shared -fPIC -o $@ $< -lm' + NL + 'test: build' + NL + TAB +
        'python3 tests/test_core.py' + NL + 'experiment: build' + NL + TAB + 'python3 tests/experiment.py' + NL)
GOOD_TEST = 'import ctypes,os' + NL + 'L=ctypes.CDLL(os.path.join(os.path.dirname(__file__),"..","src","libt.so"))' + NL + \
            'L.sq.restype=ctypes.c_double; L.sq.argtypes=[ctypes.c_double]' + NL + 'assert L.sq(3.0)==9.0; print("1/1 tests passed")' + NL
BAD_TEST = GOOD_TEST.replace('==9.0', '==10.0')
EXP = 'import json,os' + NL + 'os.makedirs(os.path.join(os.path.dirname(__file__),"..","docs"),exist_ok=True)' + NL + \
      'json.dump({"ok":1},open(os.path.join(os.path.dirname(__file__),"..","docs","results.json"),"w"))' + NL
def algo(test): return {'src/t.c': 'double sq(double x){return x*x;}' + NL, 'Makefile': MAKE, 'tests/test_core.py': test,
                        'tests/experiment.py': EXP, 'README.md': '# mock' + NL}
SEEN = []

class API(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers['content-length']))); SEEN.append(b)
        last = b['messages'][-1]['content']
        if 'haiku' in b['model']:
            out = {'novelty': 1, 'feasibility': 1, 'duplicate_of': None, 'reason': 'mock low'} if 'HYPOTHESIS YB-0003:' in last \
                  else {'novelty': 8, 'feasibility': 8, 'duplicate_of': None, 'reason': 'mock ok'}
        elif 'Propose' in last:
            out = {'hypotheses': [{'name': 'Mock proposal ' + str(i), 'foundation': 'f', 'hypothesis': 'h', 'test': 't'} for i in range(2)]}
        elif 'make all failed' in last:
            out = {'files': {'tests/test_core.py': GOOD_TEST}, 'summary': 'repaired'}
        elif 'Algorithm ID YB-0004.' in last:
            out = {'files': algo(BAD_TEST), 'summary': 'first try'}
        else:
            out = {'files': algo(GOOD_TEST), 'summary': 'mock pass'}
        resp = {'content': [{'type': 'text', 'text': json.dumps(out)}],
                'usage': {'input_tokens': 100, 'output_tokens': 50, 'cache_read_input_tokens': 1000, 'cache_creation_input_tokens': 0}}
        data = json.dumps(resp).encode(); self.send_response(200); self.send_header('content-length', str(len(data)))
        self.end_headers(); self.wfile.write(data)

srv = HTTPServer(('127.0.0.1', 0), API); threading.Thread(target=srv.serve_forever, daemon=True).start()
work = tempfile.mkdtemp(); repo = os.path.join(work, 'safety')
shutil.copytree(SRC, repo, ignore=shutil.ignore_patterns('.venv', '.git', '*.so', 'sandbox_*', 'state.json'))
shutil.rmtree(os.path.join(repo, 'miner', 'sandbox'), ignore_errors=True)
# Fixture isolation: the live research backlog evolves (e.g. YB-0003..0007 deferred when the program refocused on the
# biological thesis). This test needs YB-0003 and YB-0004 open, so reset them in the throwaway copy only.
import re as _re
_hp = os.path.join(repo, 'HYPOTHESES.md'); _h = open(_hp).read()
for _hid in ('YB-0003', 'YB-0004'):
    _h = _re.sub('(## ' + _hid + ' [^' + chr(10) + ']*' + chr(10) + ')status: [^' + chr(10) + ']*', lambda m: m.group(1) + 'status: open', _h)
open(_hp, 'w').write(_h)
env = {**os.environ, 'ANTHROPIC_API_KEY': 'mock', 'MINER_API_URL': 'http://127.0.0.1:%d' % srv.server_port,
       'MINER_WORKERS': '1', 'MINER_MAX_NEW': '2', 'MINER_DAILY_TOKENS': '1000000'}
r = subprocess.run([sys.executable, os.path.join(repo, 'miner', 'mine.py')], env=env, capture_output=True, text=True, timeout=1200)
print(r.stdout[-1500:], r.stderr[-800:])
H, L = open(os.path.join(repo, 'HYPOTHESES.md')).read(), open(os.path.join(repo, 'LEDGER.md')).read()
checks = {
 'triage skipped low scorer (YB-0003)': 'YB-0003' in L and 'skipped at triage' in L,
 'broken build repaired with patch-only resend (YB-0004)': os.path.isdir(os.path.join(repo, 'algorithms')) and
     any(d.startswith('YB-0004') for d in os.listdir(os.path.join(repo, 'algorithms'))),
 'repair request carried only the log tail + patch instruction': any('Send ONLY the files you change' in str(s['messages'][-1]['content']) for s in SEEN),
 'recursive proposals appended, capped at 2': H.count('origin: proposed by miner') == 2,
 'proposed hypotheses were mined too': 'YB-0009' in L,
 'system prompt cached with 1h TTL': all(s['system'][0].get('cache_control', {}).get('ttl') == '1h' for s in SEEN if 'haiku' not in s['model']),
 'conversation auto-cache on build calls': all('cache_control' in s for s in SEEN if 'haiku' not in s['model']),
 'triage uses cheap model, no cache overhead': all('cache_control' not in s for s in SEEN if 'haiku' in s['model']),
 'budget counts cache reads at 0.1x': json.load(open(os.path.join(repo, 'miner', 'state.json')))['used'] == 250 * len(SEEN),
 'run terminated on its own': r.returncode == 0 and 'Mining run complete' in r.stdout,
}
for k, v in checks.items(): print(('PASS ' if v else 'FAIL ') + k)
if not all(checks.values()):
    logs = [str(s['messages'][-1]['content']) for s in SEEN if 'make all failed' in str(s['messages'][-1]['content'])]
    print('--- last sandbox failure log ---' + chr(10) + (logs[-1][-2500:] if logs else 'none'))
print('%d/%d miner checks passed, %d mock API calls' % (sum(checks.values()), len(checks), len(SEEN)))
shutil.rmtree(work, ignore_errors=True); sys.exit(0 if all(checks.values()) else 1)
