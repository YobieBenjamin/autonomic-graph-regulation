# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""Offline test of the miner against a mock Claude API (no tokens spent).
Part 1 (no Docker): the naming rule in miner/names.py. New hypotheses get descriptive names (EXPERIMENT- plus 2 to 5
title words), unique against HYPOTHESES.md, LEDGER.md and algorithms/, with a more specific wording when taken and
never a number.
Part 2 (end to end): triage skip, build, broken build -> patch-only repair -> pass in the real sandbox,
recursive hypothesis proposal with a per-run cap and descriptive names, prompt-caching fields, budget accounting.
Run: python3 miner/test_miner.py   (needs Docker; uses a throwaway copy of the repo. MINER_SANDBOX=host runs part 2
without Docker, directly on this machine, for a quick local check of mock code only.)"""
import json, os, re, shutil, subprocess, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SRC, 'miner'))
import names

# ---------------- part 1: naming rule (pure functions on a scratch catalog) ----------------
UNIT = {}
NAME_OK = re.compile(r'^EXPERIMENT(-[A-Z]+){2,5}$')      # 2 to 5 capital words, no digits
cat = tempfile.mkdtemp(); os.makedirs(os.path.join(cat, 'algorithms', 'cortisol-integrator-feedback'))
open(os.path.join(cat, 'HYPOTHESES.md'), 'w').write('# Backlog' + chr(10) + chr(10) + '## EXPERIMENT-IMMUNE-NEGATIVE-SELECTION: Immune negative-selection over activation motifs' + chr(10) + 'status: deferred' + chr(10))
open(os.path.join(cat, 'LEDGER.md'), 'w').write('| ID | Name |' + chr(10) + '| EXPERIMENT-SOMATIC-MARKER-INSTINCT | Somatic-marker instinct | x | tested | y |' + chr(10))
n1 = names.new_name('Transformer heart-rate variability under stress', cat)
UNIT['name is EXPERIMENT- plus the first three title words'] = n1 == 'EXPERIMENT-TRANSFORMER-HEART-RATE'
UNIT['folder is the name in lowercase without the prefix'] = names.folder_for(n1) == 'transformer-heart-rate'
UNIT['linking words and words with digits are left out (no v2, no 768)'] = names.new_name('Expert assembly v2 connectome (768 nodes)', cat) == 'EXPERIMENT-EXPERT-ASSEMBLY-CONNECTOME'
UNIT['taken in HYPOTHESES.md -> one more title word, not a number'] = names.new_name('Immune negative selection over attention heads', cat) == 'EXPERIMENT-IMMUNE-NEGATIVE-SELECTION-ATTENTION'
UNIT['taken in LEDGER.md -> one more title word'] = names.new_name('Somatic marker instinct for agents', cat) == 'EXPERIMENT-SOMATIC-MARKER-INSTINCT-AGENTS'
UNIT['existing folder counts as taken'] = names.new_name('Cortisol integrator with feedback loop', cat) == 'EXPERIMENT-CORTISOL-INTEGRATOR-FEEDBACK-LOOP'
UNIT['every wording taken -> None (never an appended number)'] = names.new_name('Immune negative selection', cat) is None
UNIT['too few title words -> None'] = names.new_name('v1 of the 2', cat) is None
UNIT['produced names have 2 to 5 words and no digits'] = all(NAME_OK.match(x) for x in (n1, 'EXPERIMENT-EXPERT-ASSEMBLY-CONNECTOME'))
_t, _given = names.ensure_named(open(os.path.join(cat, 'HYPOTHESES.md')).read() + chr(10) + '## Lateral inhibition sparsity check' + chr(10) + 'status: open' + chr(10), cat)
UNIT['open hypothesis without a name is named in its heading'] = _given == ['EXPERIMENT-LATERAL-INHIBITION-SPARSITY'] and \
    '## EXPERIMENT-LATERAL-INHIBITION-SPARSITY: Lateral inhibition sparsity check' in open(os.path.join(cat, 'HYPOTHESES.md')).read()
UNIT['headings and ledger rows are parsed by name'] = names.parse_heading('## EXPERIMENT-TELEMETRY-PROTOCOL-FORMAL-MODEL (extension): t' + chr(10)) == ('EXPERIMENT-TELEMETRY-PROTOCOL-FORMAL-MODEL', 't') and \
    names.LEDGER_ROW_RE.match('| WAVE-CHIP-VISIBLE-VITALS | x |') is not None and names.parse_heading('## Data requirement' + chr(10)) == (None, None)
shutil.rmtree(cat, ignore_errors=True)
for k, v in UNIT.items(): print(('PASS ' if v else 'FAIL ') + 'naming: ' + k)
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
            # the triage prompt names the hypothesis by its catalog name; this one is scored low so it is skipped
            out = {'novelty': 1, 'feasibility': 1, 'duplicate_of': None, 'reason': 'mock low'} if 'HYPOTHESIS EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR:' in last \
                  else {'novelty': 8, 'feasibility': 8, 'duplicate_of': None, 'reason': 'mock ok'}
        elif 'Propose' in last:
            # two proposals with the SAME title: the first name is taken by the fixture (EXPERIMENT-IMMUNE-NEGATIVE-SELECTION),
            # so the miner must pick ...-ATTENTION and then ...-ATTENTION-HEADS, never a number
            out = {'hypotheses': [{'name': 'Immune negative selection over attention heads', 'foundation': 'f', 'hypothesis': 'h', 'test': 't'} for i in range(2)]}
        elif 'make all failed' in last:
            out = {'files': {'tests/test_core.py': GOOD_TEST}, 'summary': 'repaired'}
        # the build prompt starts "Algorithm ID <name>."; this hypothesis gets a broken build first, to exercise repair
        elif 'Algorithm ID EXPERIMENT-IMMUNE-NEGATIVE-SELECTION.' in last:
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
# Fixture isolation: the live research backlog evolves (the MLP-testbed hypotheses from
# EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR, EXPERIMENT-IMMUNE-NEGATIVE-SELECTION, EXPERIMENT-SCALABLE-TRANSFORMER-HEAT-TRACE, EXPERIMENT-AMYGDALA-LOW-ROAD-BREAKER and EXPERIMENT-DRIFT-BUDGET-CALIBRATION were deferred when the program
# refocused on the biological thesis). This test needs EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR and
# EXPERIMENT-IMMUNE-NEGATIVE-SELECTION open, so reset them in the throwaway copy only. Headings are found by name.
_hp = os.path.join(repo, 'HYPOTHESES.md'); _h = open(_hp).read()
FIXTURE = ('EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR', 'EXPERIMENT-IMMUNE-NEGATIVE-SELECTION')
for _hid in FIXTURE:
    _h = re.sub('(## ' + _hid + '(?=[ :(])[^' + chr(10) + ']*' + chr(10) + ')status: [^' + chr(10) + ']*', lambda m: m.group(1) + 'status: open', _h)
open(_hp, 'w').write(_h)
# a pre-registered experiment that is open but whose folder exists: the miner must leave it alone
PREREG = 'EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING'
_prereg_files = sorted(os.listdir(os.path.join(repo, 'algorithms', names.folder_for(PREREG))))
_prereg_rows = open(os.path.join(repo, 'LEDGER.md')).read().count('| ' + PREREG + ' | ')   # its existing ledger rows
env = {**os.environ, 'ANTHROPIC_API_KEY': 'mock', 'MINER_API_URL': 'http://127.0.0.1:%d' % srv.server_port,
       'MINER_WORKERS': '1', 'MINER_MAX_NEW': '2', 'MINER_DAILY_TOKENS': '1000000'}
r = subprocess.run([sys.executable, os.path.join(repo, 'miner', 'mine.py')], env=env, capture_output=True, text=True, timeout=3600)
print(r.stdout[-1500:], r.stderr[-800:])
H, L = open(os.path.join(repo, 'HYPOTHESES.md')).read(), open(os.path.join(repo, 'LEDGER.md')).read()
checks = {
 'triage skipped low scorer (by name)': '| EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR | ' in L and 'skipped at triage' in L,
 # the repaired build is promoted to the folder named after the hypothesis: algorithms/immune-negative-selection
 'broken build repaired with patch-only resend, folder named after the hypothesis':
     os.path.isfile(os.path.join(repo, 'algorithms', 'immune-negative-selection', 'Makefile')),
 'repair request carried only the log tail + patch instruction': any('Send ONLY the files you change' in str(s['messages'][-1]['content']) for s in SEEN),
 'recursive proposals appended, capped at 2': H.count('origin: proposed by miner') == 2,
 # the two proposals got descriptive, unique names (a more specific wording for the second), recorded as
 # HYPOTHESES.md headings and LEDGER.md rows, and were mined into folders of the same names
 'proposals named from their title, unique, no number':
     '## EXPERIMENT-IMMUNE-NEGATIVE-SELECTION-ATTENTION: ' in H and '## EXPERIMENT-IMMUNE-NEGATIVE-SELECTION-ATTENTION-HEADS: ' in H,
 'proposed hypotheses were mined too (ledger rows and folders)':
     '| EXPERIMENT-IMMUNE-NEGATIVE-SELECTION-ATTENTION | ' in L and '| EXPERIMENT-IMMUNE-NEGATIVE-SELECTION-ATTENTION-HEADS | ' in L and
     os.path.isdir(os.path.join(repo, 'algorithms', 'immune-negative-selection-attention')) and
     os.path.isdir(os.path.join(repo, 'algorithms', 'immune-negative-selection-attention-heads')),
 'no new heading or ledger row uses a letter-number code':
     not re.search(r'(?m)^(## |[|] )[A-Z]{1,4}-[0-9]', H + L),
 'open hypothesis with an existing folder was not mined or overwritten':
     L.count('| ' + PREREG + ' | ') == _prereg_rows and sorted(os.listdir(os.path.join(repo, 'algorithms', names.folder_for(PREREG)))) == _prereg_files,
 'system prompt cached with 1h TTL': all(s['system'][0].get('cache_control', {}).get('ttl') == '1h' for s in SEEN if 'haiku' not in s['model']),
 'conversation auto-cache on build calls': all('cache_control' in s for s in SEEN if 'haiku' not in s['model']),
 'triage uses cheap model, no cache overhead': all('cache_control' not in s for s in SEEN if 'haiku' in s['model']),
 'budget counts cache reads at 0.1x': json.load(open(os.path.join(repo, 'miner', 'state.json')))['used'] == 250 * len(SEEN),
 'run terminated on its own': r.returncode == 0 and 'Mining run complete' in r.stdout,
}
checks.update({'naming: ' + k: v for k, v in UNIT.items()})
for k, v in checks.items(): print(('PASS ' if v else 'FAIL ') + k)
if not all(checks.values()):
    logs = [str(s['messages'][-1]['content']) for s in SEEN if 'make all failed' in str(s['messages'][-1]['content'])]
    print('--- last sandbox failure log ---' + chr(10) + (logs[-1][-2500:] if logs else 'none'))
print('%d/%d miner checks passed, %d mock API calls' % (sum(checks.values()), len(checks), len(SEEN)))
shutil.rmtree(work, ignore_errors=True); sys.exit(0 if all(checks.values()) else 1)
