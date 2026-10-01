#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Hybrid orchestrator: local-first AI safety algorithm mining.

Each stage is routed to the cheapest capable resource:
  design    cloud Claude (novel math)       -> fallback local
  implement local gpt-oss-120b (free)       -> fallback cloud
  repair    local x MAX_LOCAL_REPAIRS, then cloud x MAX_CLOUD_REPAIRS
  verify    local Docker sandbox, parallel (no network, no secrets)
  review    cloud Claude (claims vs numbers) -> fallback local
  publish   local publish.sh (sandbox-verified)
Usage: ./mine [--max N]      env: LOCAL_ONLY=1, CLOUD_MODEL, CLOUD_DAILY_TOKENS, HYP_CONCURRENCY, ...
'''
import json, os, re, sys, time, shutil, subprocess, threading, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = os.environ.get
NL = chr(10)
CFG = dict(local_url=E('LOCAL_URL', 'http://localhost:1234/v1'), local_model=E('LOCAL_MODEL', 'local-strong'),
           cloud_model=E('CLOUD_MODEL', 'claude-sonnet-5'), cloud_daily=int(E('CLOUD_DAILY_TOKENS', '2000000')),
           local_conc=int(E('LOCAL_CONCURRENCY', '3')), sandbox_conc=int(E('SANDBOX_CONCURRENCY', '8')),
           hyp_conc=int(E('HYP_CONCURRENCY', '4')), local_repairs=int(E('MAX_LOCAL_REPAIRS', '4')),
           cloud_repairs=int(E('MAX_CLOUD_REPAIRS', '1')), publish=E('PUBLISH', '1') == '1')
HYP, LEDGER = os.path.join(ROOT, 'HYPOTHESES.md'), os.path.join(ROOT, 'LEDGER.md')
RUNS, WORK = os.path.join(ROOT, 'orchestrator', 'runs'), os.path.join(ROOT, 'miner', 'sandbox')
REF = os.path.join(ROOT, 'algorithms', 'YB-0002-bounded-homeostasis-wrapper')
os.makedirs(RUNS, exist_ok=True); os.makedirs(WORK, exist_ok=True)
LOCK, PUBLOCK = threading.RLock(), threading.Lock()
LOCAL_SEM, SANDBOX_SEM = threading.Semaphore(CFG['local_conc']), threading.Semaphore(CFG['sandbox_conc'])


def cloud_key():
    if E('LOCAL_ONLY') == '1' or E('USE_API') != '1': return None   # paid API is opt-in (budget: subscription only)
    if E('ANTHROPIC_API_KEY'): return E('ANTHROPIC_API_KEY')
    r = subprocess.run(['security', 'find-generic-password', '-s', 'anthropic-api-key', '-w'], capture_output=True, text=True)
    return r.stdout.strip() or None
KEY = cloud_key()


def workspace_id():
    """Account-level (non-workspace-scoped) keys must name a workspace. Not a secret; per-machine."""
    if E('ANTHROPIC_WORKSPACE_ID'): return E('ANTHROPIC_WORKSPACE_ID')
    r = subprocess.run(['security', 'find-generic-password', '-s', 'anthropic-workspace-id', '-w'], capture_output=True, text=True)
    return r.stdout.strip() or None
WORKSPACE = workspace_id()


def log(ev, **kw):
    rec = dict(t=datetime.datetime.now().isoformat(timespec='seconds'), ev=ev, **kw)
    with LOCK:
        open(os.path.join(RUNS, datetime.date.today().isoformat() + '.jsonl'), 'a').write(json.dumps(rec) + NL)
    print(rec['t'], ev, json.dumps({k: v for k, v in kw.items() if k != 'detail'})[:300], flush=True)


def usage(add=None):
    with LOCK:
        f, today = os.path.join(RUNS, 'usage.json'), datetime.date.today().isoformat()
        try: u = json.load(open(f))
        except Exception: u = {}
        if u.get('date') != today: u = dict(date=today, cloud_in=0, cloud_out=0, local_in=0, local_out=0, cc_calls=0, cc_in=0, cc_out=0)
        for k, v in (add or {}).items(): u[k] = u.get(k, 0) + v
        json.dump(u, open(f, 'w'), indent=1)
        return u


def cloud_left():
    u = usage(); return CFG['cloud_daily'] - u['cloud_in'] - u['cloud_out']


def post(url, body, headers, timeout=3600):
    req = urllib.request.Request(url, json.dumps(body).encode(), {'content-type': 'application/json', **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.load(r)


def call_local(system, user, max_tokens):
    with LOCAL_SEM:
        d = post(CFG['local_url'] + '/chat/completions', dict(model=CFG['local_model'], max_tokens=max_tokens,
                 temperature=0.3, reasoning_effort='high',
                 messages=[dict(role='system', content=system), dict(role='user', content=user)]), {})
    u = d.get('usage', {}); usage(dict(local_in=u.get('prompt_tokens', 0), local_out=u.get('completion_tokens', 0)))
    return d['choices'][0]['message'].get('content') or ''


def call_cloud(system, user, max_tokens):
    d = post('https://api.anthropic.com/v1/messages', dict(model=CFG['cloud_model'], max_tokens=max_tokens, system=system,
             messages=[dict(role='user', content=user)]), {'x-api-key': KEY, 'anthropic-version': '2023-06-01',
             **({'anthropic-workspace-id': WORKSPACE} if WORKSPACE else {})})
    usage(dict(cloud_in=d['usage']['input_tokens'], cloud_out=d['usage']['output_tokens']))
    return ''.join(b.get('text', '') for b in d['content'] if b['type'] == 'text')


CC = dict(bin=shutil.which('claude') or os.path.expanduser('~/.nvm/versions/node/v22.17.1/bin/claude'),
          model=E('CC_MODEL', 'sonnet'), daily=int(E('CC_DAILY_CALLS', '3')), window=E('CC_WINDOW', '1-6'),
          anytime=E('CC_ANYTIME') == '1', disabled=E('LOCAL_ONLY') == '1')


def cc_token():
    if E('CLAUDE_CODE_OAUTH_TOKEN'): return E('CLAUDE_CODE_OAUTH_TOKEN')
    r = subprocess.run(['security', 'find-generic-password', '-s', 'claude-code-oauth-token', '-w'], capture_output=True, text=True)
    return r.stdout.strip() or None


def cc_available():
    if CC['disabled'] or not os.path.exists(CC['bin']) or not cc_token(): return False
    if usage().get('cc_calls', 0) >= CC['daily']: return False
    lo, hi = (int(x) for x in CC['window'].split('-'))
    return CC['anytime'] or lo <= datetime.datetime.now().hour < hi


def call_claude_code(system, user, max_tokens):
    """Claude Code headless on the Max subscription (no API credits). Our system prompt replaces the default
    (avoids ~16.7k tokens of built-in instructions per call); no tools, no MCP."""
    env = {k: v for k, v in os.environ.items() if k != 'ANTHROPIC_API_KEY'}; env['CLAUDE_CODE_OAUTH_TOKEN'] = cc_token()
    r = subprocess.run([CC['bin'], '-p', '--output-format', 'json', '--model', CC['model'], '--strict-mcp-config', '--tools', '',
                        '--system-prompt', system], input=user, capture_output=True, text=True, timeout=900, env=env, cwd='/tmp')
    try: d = json.loads(r.stdout)
    except Exception: raise RuntimeError('claude code: ' + (r.stdout + r.stderr)[-200:])
    u = d.get('usage', {}); usage(dict(cc_calls=1, cc_in=u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0), cc_out=u.get('output_tokens', 0)))
    if d.get('is_error'):
        if 'limit' in str(d.get('result', '')).lower(): CC['disabled'] = True; log('cc_limit_reached', msg=str(d.get('result'))[:120])
        raise RuntimeError('claude code error: ' + str(d.get('result'))[:200])
    return d.get('result') or ''


ROUTES = dict(design=['local', 'cloud'], implement_core=['local', 'cloud'], implement=['local', 'cloud'], repair_local=['local'],
              repair_cloud=['claude_code', 'cloud'], review=['claude_code', 'cloud', 'local'], fix_docs=['local', 'cloud'])


def llm(role, system, user, max_tokens):
    for p in ROUTES[role]:
        if p == 'cloud' and (not KEY or cloud_left() < max_tokens): continue
        if p == 'claude_code' and not cc_available(): continue
        try:
            t = time.time(); out = {'cloud': call_cloud, 'claude_code': call_claude_code, 'local': call_local}[p](system, user, max_tokens)
            log('llm', role=role, provider=p, secs=round(time.time() - t), chars=len(out))
            raw = os.path.join(RUNS, 'raw'); os.makedirs(raw, exist_ok=True)
            open(os.path.join(raw, datetime.datetime.now().strftime('%H%M%S-') + role + '-' + p + '.txt'), 'w').write(out)
            if out.strip(): return out, p
        except Exception as e:
            log('llm_error', role=role, provider=p, err=str(e)[:300])
    return None, None


FILE_RE = re.compile('<<<FILE (.+?)>>>' + NL + '(.*?)' + NL + '<<<END>>>', re.S)


def parse_files(txt):
    return {p.strip(): c + NL for p, c in FILE_RE.findall(txt or '')}


def write_files(box, files):
    for rel, content in files.items():
        p = os.path.normpath(os.path.join(box, rel))
        if not p.startswith(box + os.sep) or rel.endswith('mlp.py'): continue
        os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(content)


def dump(box, skip=('mlp.py', 'results.json', 'DESIGN.md')):
    out = []
    for dp, _, fs in os.walk(box):
        for f in sorted(fs):
            if f.endswith(('.so', '.pyc')) or f in skip or f == '__init__.py': continue
            rel = os.path.relpath(os.path.join(dp, f), box)
            out.append('<<<FILE ' + rel + '>>>' + NL + open(os.path.join(dp, f), errors='replace').read().rstrip(NL) + NL + '<<<END>>>')
    return NL.join(out)


def static_gate(box):
    """Free deterministic checks that catch common LLM code failures before any test runs."""
    import ast
    issues = []
    for dp, _, fs in os.walk(box):
        for f in fs:
            fp = os.path.join(dp, f); rel = os.path.relpath(fp, box)
            if f == 'mlp.py' or not f.endswith(('.py', '.c', '.h')): continue
            src = open(fp, errors='replace').read(); low = src.lower()
            for bad in ('placeholder', 'todo', 'not implemented', 'notimplementederror', 'dummy implementation', 'fill in'):
                if bad in low: issues.append(rel + ': contains stub marker ' + repr(bad))
            if f.endswith('.c') and re.search('int +main *[(]', src): issues.append(rel + ': C core must not define main()')
            if f.endswith('.py'):
                try: tree = ast.parse(src)
                except SyntaxError as e: issues.append(rel + ': syntax error ' + str(e)); continue
                seen = set()
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if node.name in seen: issues.append(rel + ': ' + node.name + ' defined twice (later stub overrides earlier)')
                        seen.add(node.name)
    return issues


def verify(box):
    gate = static_gate(box)
    if gate: return False, 'STATIC QUALITY GATE FAILED (fix these first):' + NL + NL.join(gate)
    with SANDBOX_SEM:
        try:
            r = subprocess.run([os.path.join(ROOT, 'sandbox', 'run.sh'), box, 'all'], capture_output=True, text=True, timeout=1800)
            return r.returncode == 0, (r.stdout + r.stderr)[-6000:]
        except subprocess.TimeoutExpired:
            return False, 'TIMEOUT after 1800s'


CONTRACT = '''You implement AI-safety algorithms as a self-contained directory. Mandatory:
- Compiled core in C: src/*.c, must build with gcc -O2 -Wall -Wextra -Werror -shared -fPIC, called from Python via ctypes.
- src/mlp.py ALREADY EXISTS (do not write it): class MLP(d,h1,h2,c,seed); .train(X,y); .forward(X)->(z1,a1,z2,a2,logits);
  .predict(X); .fgsm(X,y,eps); MLP.softmax(z). Use it as the test subject (sklearn load_digits, train on digits 0-4).
- Makefile targets: build, test, experiment, all (all = test experiment). Only numpy, scipy, scikit-learn. No network.
- tests/test_core.py: correctness tests vs closed forms or a pure-Python reference; prints N/N tests passed.
- tests/experiment.py: deterministic (fixed seeds), >=2 standard baselines, writes docs/results.json (floats rounded to 4).
- README.md sections: 1 Plain English, 2 Technical summary, 3 Mathematics (label each claim Theorem+proof or Conjecture),
  4 Code map, 5 Results (tables from actual output), 6 Honest limitations and prior art. Never claim what numbers do not show.
- Must finish make all in under 20 minutes on 4 CPUs.
Output format: every file as a block exactly like
<<<FILE relative/path>>>
file content
<<<END>>>
and nothing else outside blocks.'''

DESIGN_SYS = '''You are a senior research scientist in AI safety, spectral graph theory and computational neuroscience.
Turn the hypothesis into a concrete, testable research design. Sections: Grounding (the biological mechanism and graph
analogue), Mathematics (definitions; each claim labelled Theorem with proof sketch or Conjecture), Algorithm (pseudo-code),
C core API for src/core.c (exact exported C signatures; Python wrapper is src/algo.py), Correctness tests (closed forms), Experiment (MLP on sklearn digits trained on 0-4;
near-OOD 5-9, noise, FGSM; >=2 baselines such as MSP, energy, activation-Mahalanobis; metrics; seeds), Expected failure modes.
Be precise and concise (under 1500 words). Prefer designs that can falsify the hypothesis.'''

REVIEW_SYS = '''You are a rigorous, skeptical scientific reviewer. Given an algorithm README, its experiment script and its
results.json, check: every number and claim in README matches results.json; results are computed (not hard-coded); baselines
are fair; theorems are proved or labelled conjecture; limitations are honest. Negative results are acceptable if reported
honestly. Reply with ONLY JSON: {\"verdict\": \"accept\" | \"revise\" | \"reject\", \"issues\": [\"...\"], \"headline\": \"one-line result summary\"}.'''


def claim():
    with LOCK:
        text = open(HYP).read()
        for block in re.split('(?m)^(?=## )', text):
            if block.startswith('## ') and 'status: open' in block:
                open(HYP, 'w').write(text.replace(block, block.replace('status: open', 'status: in-progress', 1)))
                return block.split()[1], block
    return None


def set_status(hid, status):
    with LOCK:
        text = open(HYP).read()
        text = re.sub('(## ' + re.escape(hid) + ' [^' + NL + ']*' + NL + ')status: [a-z-]+', lambda m: m.group(1) + 'status: ' + status, text)
        open(HYP, 'w').write(text)


def ledger(hid, name, status, headline, stats):
    with LOCK:
        open(LEDGER, 'a').write('| ' + hid + ' | ' + name + ' | see HYPOTHESES.md | ' + status + ' | ' + headline.replace('|', '/')[:300]
                                + ' (' + ', '.join(k + '=' + str(v) for k, v in stats.items()) + ') |' + NL)


def review(box):
    rd = lambda p: open(os.path.join(box, p), errors='replace').read() if os.path.exists(os.path.join(box, p)) else '(missing)'
    txt, p = llm('review', REVIEW_SYS, 'README.md:' + NL + rd('README.md') + NL + 'tests/experiment.py:' + NL + rd('tests/experiment.py')
                 + NL + 'docs/results.json:' + NL + rd('docs/results.json'), 3000)
    try: return json.loads(txt[txt.index('{'): txt.rindex('}') + 1]), p
    except Exception: return dict(verdict='revise', issues=['review unparseable'], headline=''), p


TAB = chr(9)
MAKEFILE = NL.join(['.PHONY: all build test experiment clean', 'all: test experiment', 'build: src/libcore.so',
    'src/libcore.so: src/core.c', TAB + 'gcc -O2 -Wall -Wextra -Werror -shared -fPIC -o $@ $< -lm',
    'export PYTHONPATH := .:src', 'test: build', TAB + 'python3 -m py_compile src/*.py tests/*.py', TAB + 'python3 tests/test_core.py',
    'experiment: build', TAB + 'mkdir -p docs', TAB + 'python3 tests/experiment.py', 'clean:', TAB + 'rm -f src/libcore.so']) + NL
PLAN = [('src/core.c', 'src/bhw.c', 'C core: the exported functions from the design C API; no main(); must compile with -Wall -Wextra -Werror.'),
        ('src/algo.py', 'src/bhw.py', 'Python module: ctypes binding to libcore.so located next to this file, a pure-Python reference of the core, and the detector used by tests and experiment.'),
        ('tests/test_core.py', 'tests/test_core.py', 'Correctness tests: C core vs pure-Python reference on random inputs plus closed-form cases. Insert ../src into sys.path. Print N/N tests passed; exit non-zero on any failure.'),
        ('tests/experiment.py', 'tests/experiment.py', 'Deterministic evaluation (fixed seeds): MLP(64,32,32,5) from src/mlp.py on sklearn digits trained on digits 0-4; near-OOD digits 5-9, uniform noise, FGSM eps 0.1 and 0.2; compare the new detector with at least MSP and energy (AUROC via sklearn.metrics.roc_auc_score); os.makedirs docs; write docs/results.json with floats rounded to 4; print a table. Under 10 minutes on 4 CPUs.')]
FILE_SYS = ('You are an expert research engineer (C99, numpy, scipy, scikit-learn). Environment: Linux, python3, gcc, NO network. '
            'src/mlp.py already exists: class MLP(d, h1, h2, c, seed); .train(X, y); .forward(X) returns (z1, a1, z2, a2, logits); '
            '.predict(X); .fgsm(X, y, eps); static MLP.softmax(z). The Makefile (fixed) builds src/libcore.so from src/core.c and runs '
            'tests/test_core.py then tests/experiment.py with PYTHONPATH=.:src, so import modules directly: import algo; from mlp import MLP. Write correct, complete, deterministic code: no placeholders, no TODOs.')
FENCE = chr(96) * 3
FILE_SYS += (' READ-ONLY src/mlp.py (use exactly this API; never modify it; it has no other methods):' + NL + FENCE + 'python' + NL
             + open(os.path.join(REF, 'src', 'mlp.py')).read() + FENCE)


def code_of(txt, last=False):
    txt = txt or ''
    i = txt.find(FENCE)
    if i < 0: return None
    start = txt.find(NL, i) + 1
    end = txt.rfind(FENCE) if last else txt.find(FENCE, start)
    return txt[start:end].rstrip(NL) + NL if end > start else None


def gen_file(box, path, refp, job, design):
    user = ('Design:' + NL + design + NL + NL + 'Files already written:' + NL + (dump(box) or '(none)') + NL + NL
            + 'Style reference from a different algorithm (adapt, do not copy):' + NL + FENCE + NL + open(os.path.join(REF, refp)).read()
            + FENCE + NL + NL + 'Write the COMPLETE content of ' + path + '. ' + job + ' Reply with exactly one fenced code block.')
    txt, p = llm('implement_core' if path.startswith('src/') else 'implement', FILE_SYS, user, 16000)
    c = code_of(txt)
    if c: write_files(box, {path: c})
    return p, bool(c)


def repair(box, out, role):
    user = ('make all FAILED. Files:' + NL + dump(box) + NL + 'Log tail:' + NL + out[-4000:] + NL + 'Fix the single file most responsible '
            '(any .c/.h/.py under src/ or tests/; src/mlp.py is read-only, so adapt the callers instead). Reply with a first line FILE: <path>, then one fenced code block with its complete corrected content.')
    txt, p = llm(role, FILE_SYS, user, 16000)
    m = re.search('FILE: *([^ ' + NL + ']+)', txt or ''); c = code_of(txt[txt.find('FILE:'):] if txt and 'FILE:' in txt else txt)
    path = m.group(1).strip(chr(96) + '*') if m else None
    ok_path = path and re.fullmatch('(src|tests)/[A-Za-z0-9_]+[.](c|h|py)', path) and not path.endswith('mlp.py')
    if ok_path and c:
        write_files(box, {path: c}); return path
    return None


def mine(hid, block):
    name = block.splitlines()[0].split(' — ', 1)[-1].strip()
    slug = hid + '-' + re.sub('[^a-z0-9]+', '-', name.lower()).strip('-')[:50]
    box = os.path.join(WORK, slug); st = dict(design='-', impl='-', repairs=0, review='-'); t0 = time.time()
    resume = E('RESUME') == '1' and all(os.path.exists(os.path.join(box, x)) for x in ['docs/DESIGN.md'] + [q[0] for q in PLAN])
    if not resume:
        shutil.rmtree(box, ignore_errors=True)
        for d in ('src', 'tests', 'docs'): os.makedirs(os.path.join(box, d))
    shutil.copy(os.path.join(REF, 'src', 'mlp.py'), os.path.join(box, 'src', 'mlp.py'))
    open(os.path.join(box, 'Makefile'), 'w').write(MAKEFILE); open(os.path.join(box, 'src', '__init__.py'), 'a').close()
    if resume:
        design, st['design'] = open(os.path.join(box, 'docs', 'DESIGN.md')).read(), 'resumed'; log('resumed', hid=hid)
    else:
        design, st['design'] = llm('design', DESIGN_SYS, 'Algorithm ID ' + hid + NL + block, 6000)
        if not design: return finish(hid, name, box, 'failed: no design', '', st)
        open(os.path.join(box, 'docs', 'DESIGN.md'), 'w').write(design)
        for path, refp, job in PLAN:
            st['impl'], okf = gen_file(box, path, refp, job, design); log('generated', hid=hid, file=path, ok=okf)
    ok, out = verify(box)
    for i in range(CFG['local_repairs'] + CFG['cloud_repairs']):
        if ok: break
        role = 'repair_local' if i < CFG['local_repairs'] else 'repair_cloud'
        fixed = repair(box, out, role); st['repairs'] += 1; ok, out = verify(box)
        log('repair', hid=hid, attempt=i + 1, role=role, fixed=fixed, ok=ok)
    if not ok: return finish(hid, name, box, 'failed build/test', out.strip().splitlines()[-1][:150] if out.strip() else '', st)
    res = open(os.path.join(box, 'docs', 'results.json')).read()
    txt, _ = llm('implement', FILE_SYS, CONTRACT + NL + NL + 'Design:' + NL + design + NL + 'Code:' + NL + dump(box) + NL + 'docs/results.json:'
                 + NL + res + NL + 'Test/experiment output tail:' + NL + out[-2500:] + NL + 'Write README.md with the contract sections, every number '
                 'taken from results.json. Reply with one fenced markdown block.', 8000)
    c = code_of(txt, last=True)
    if c: write_files(box, {'README.md': c})
    for rnd in range(2):
        rv, st['review'] = review(box); log('review', hid=hid, round=rnd + 1, verdict=rv.get('verdict'), issues=rv.get('issues', [])[:5])
        if rv.get('verdict') != 'revise' or rnd == 1: break
        fix, _ = llm('fix_docs', FILE_SYS, 'Reviewer issues:' + NL + json.dumps(rv.get('issues')) + NL + 'README.md:' + NL + open(os.path.join(box, 'README.md')).read()
                     + NL + 'docs/results.json:' + NL + res + NL + 'Return the corrected complete README.md as one fenced markdown block.', 8000)
        c = code_of(fix, last=True)
        if c: write_files(box, {'README.md': c})
    st['minutes'] = round((time.time() - t0) / 60, 1)
    verdict = rv.get('verdict')
    if verdict == 'reject': return finish(hid, name, box, 'rejected in review', '; '.join(rv.get('issues', []))[:200], st)
    return finish(hid, name, box, 'tested' + ('' if verdict == 'accept' else ' (review: ' + str(verdict) + ')'), rv.get('headline', ''), st, promote=True)


def finish(hid, name, box, status, headline, st, promote=False):
    if promote:
        for so in __import__('glob').glob(os.path.join(box, 'src', '*.so')): os.remove(so)
        dest = os.path.join(ROOT, 'algorithms', os.path.basename(box)); shutil.rmtree(dest, ignore_errors=True); shutil.move(box, dest)
    set_status(hid, 'tested' if promote else 'failed'); ledger(hid, name, status, headline, st); log('finished', hid=hid, status=status, **st)
    if promote and CFG['publish']:
        with PUBLOCK:
            r = subprocess.run([os.path.join(ROOT, 'publish.sh'), 'Mined ' + hid + ': ' + name], capture_output=True, text=True)
            log('published' if r.returncode == 0 else 'publish_failed', hid=hid, tail=(r.stdout + r.stderr)[-200:])
    return hid + ': ' + status


def safe_mine(hid, block):
    try: return mine(hid, block)
    except Exception as e:
        log('crash', hid=hid, err=repr(e)[:300]); set_status(hid, 'open'); return hid + ': crashed, returned to backlog'


def main():
    os.makedirs(RUNS, exist_ok=True); os.makedirs(WORK, exist_ok=True)
    maxn = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 99
    with LOCK:
        text = open(HYP).read()                     # read fully BEFORE opening for write
        if 'status: in-progress' in text: open(HYP, 'w').write(text.replace('status: in-progress', 'status: open'))
    if subprocess.run([os.path.join(ROOT, 'sandbox', 'ensure_docker.sh')]).returncode:
        sys.exit('Docker sandbox unavailable; refusing to run model-written code.')
    try: post(CFG['local_url'] + '/chat/completions', dict(model=CFG['local_model'], max_tokens=5, messages=[dict(role='user', content='ok')]), {}, 300); local = True
    except Exception: local = False
    log('start', api=bool(KEY), claude_code=cc_available(), local=local, cc_cfg={k: v for k, v in CC.items() if k != 'bin'}, cfg=CFG)
    if not (local or KEY or cc_available()): sys.exit('No local model, Claude Code or API available.')
    with ThreadPoolExecutor(CFG['hyp_conc']) as ex:
        futs = []
        for _ in range(maxn):
            job = claim()
            if not job: break
            futs.append(ex.submit(safe_mine, *job))
        res = [f.result() for f in futs]
    log('done', results=res, usage=usage())


if __name__ == '__main__':
    main()
