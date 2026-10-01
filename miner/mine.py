#!/usr/bin/env python3
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""Algorithm miner v2: agents turn hypotheses into tested, documented algorithms, recursively.

  python3 miner/mine.py                  # mine until backlog + new-idea cap or daily budget is spent
  MINER_DRY_RUN=1 python3 miner/mine.py  # parse backlog, no API calls

Loop: triage (cheap model) -> build (strong model, cached context) -> sandboxed make all ->
patch-only repair loop -> promote to algorithms/ or record the failure. When the backlog is empty,
propose new hypotheses from the foundation + ledger (recursive mining), capped per run.

Token optimizations:
  1 Prompt caching: spec + reference implementation in a 1-hour cached system block (~0.1x on reuse);
    automatic caching of the growing repair conversation.
  2 Triage gate: a cheap model scores novelty/feasibility vs the ledger; low scorers are skipped
    before any expensive generation.
  3 Patch-only repairs: the model resends only files it changes, not the whole algorithm.
  4 Trimmed feedback: only the tail of build/test logs is fed back.
  5 Budget accounting weighted by price (cache reads count 0.1x); hard stop at the daily cap.

Env: ANTHROPIC_API_KEY (required), MINER_MODEL (claude-sonnet-5), MINER_TRIAGE_MODEL
(claude-haiku-4-5-20251001), MINER_DAILY_TOKENS (2000000), MINER_WORKERS (2), MINER_REPAIRS (2),
MINER_MIN_SCORE (12 of 20), MINER_MAX_NEW (3 new hypotheses per run), MINER_PUBLISH=1.

SECURITY: model-written code is built/run ONLY inside the Docker sandbox (sandbox/run.sh):
no network, no secrets, non-root, capped. MINER_SANDBOX=host disables this (unsafe).
"""
import json, os, re, shutil, subprocess, sys, threading, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HYP, LEDGER = os.path.join(ROOT, 'HYPOTHESES.md'), os.path.join(ROOT, 'LEDGER.md')
STATE, SANDBOX_DIR = os.path.join(ROOT, 'miner', 'state.json'), os.path.join(ROOT, 'miner', 'sandbox')
REF_DIR = os.path.join(ROOT, 'algorithms', 'YB-0002-bounded-homeostasis-wrapper')
MODEL = os.environ.get('MINER_MODEL', 'claude-sonnet-5')
TRIAGE_MODEL = os.environ.get('MINER_TRIAGE_MODEL', 'claude-haiku-4-5-20251001')
BUDGET = int(os.environ.get('MINER_DAILY_TOKENS', 2_000_000))
WORKERS = int(os.environ.get('MINER_WORKERS', 2))
REPAIRS = int(os.environ.get('MINER_REPAIRS', 2))
MIN_SCORE = int(os.environ.get('MINER_MIN_SCORE', 12))
MAX_NEW = int(os.environ.get('MINER_MAX_NEW', 3))
DRY = os.environ.get('MINER_DRY_RUN') == '1'
SANDBOX = os.environ.get('MINER_SANDBOX', 'docker')
API_URL = os.environ.get('MINER_API_URL', 'https://api.anthropic.com/v1/messages')
LOCK = threading.RLock()   # re-entrant: propose() holds it while call() -> spend() re-acquires
NEW_COUNT = [0]

FOUNDATION = '''Research program: net-new AI-safety algorithms grounded in graph theory, neuroscience and
biological behavior (homeostasis, immune self/non-self, lateral inhibition, dual-pathway threat
processing, synaptic plasticity limits, etc.), in the spirit of the book Garbage In, Gospel Out.
Standard: every claim is tested against strong baselines; negative results are recorded, never hidden.'''

SPEC = FOUNDATION + '''

Implement the hypothesis you are given as a self-contained algorithm directory. Mandatory:
- A compiled core in C (src/*.c, builds with gcc -O2 -Wall -Wextra -Werror) called from Python via ctypes.
- Makefile with targets build, test, experiment, all (all = test + experiment). Only numpy, scipy, scikit-learn.
  No network access exists at run time. sklearn load_digits is available offline.
- tests/test_core.py: correctness tests against independent references, closed forms, or stated theorems.
- tests/experiment.py: deterministic evaluation vs at least two standard baselines; writes docs/results.json
  (round floats to 4 decimals). Whole run under 10 minutes on 4 CPUs.
- README.md: 1 Plain English, 2 Technical summary, 3 Mathematics (definitions; claims proved or labelled
  conjecture), 4 Code map, 5 Results (tables from actual output), 6 Honest limitations and prior art.
Never claim a win the numbers do not show. Reply with ONLY a JSON object:
{"files": {"relative/path": "content"}, "summary": "one-line headline result"}
When asked to repair, include ONLY the files you change.

REFERENCE IMPLEMENTATION (style, structure, rigor; do not copy its topic):
'''


def reference_context():
    parts = []
    for rel in ('src/bhw.c', 'src/bhw.py', 'tests/test_core.py', 'Makefile', 'README.md'):
        p = os.path.join(REF_DIR, rel)
        if os.path.exists(p):
            parts.append('=== ' + rel + ' ===' + chr(10) + open(p).read())
    return chr(10).join(parts)


SYSTEM = [{'type': 'text', 'text': SPEC + reference_context(), 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}]


# ---------------- budget + state ----------------
def load_state():
    today = datetime.date.today().isoformat()
    try:
        s = json.load(open(STATE))
        return s if s.get('date') == today else {'date': today, 'used': 0, 'raw': {}}
    except (FileNotFoundError, json.JSONDecodeError):
        return {'date': today, 'used': 0, 'raw': {}}


def spend(usage):
    w = (usage.get('input_tokens', 0) + usage.get('output_tokens', 0) + usage.get('cache_creation_input_tokens', 0)
         + 0.1 * usage.get('cache_read_input_tokens', 0))
    with LOCK:
        s = load_state(); s['used'] += int(w)
        for k, v in usage.items():
            if isinstance(v, int): s['raw'][k] = s['raw'].get(k, 0) + v
        json.dump(s, open(STATE, 'w')); return int(w)


def budget_left():
    return BUDGET - load_state()['used']


# ---------------- backlog + ledger ----------------
def blocks(text):
    return [b for b in re.split(r'(?m)^(?=## )', text) if b.startswith('## ')]


def claim():
    with LOCK:
        text = open(HYP).read()
        for block in blocks(text):
            if 'status: open' in block:
                hid = block.split()[1]
                open(HYP, 'w').write(text.replace(block, block.replace('status: open', 'status: in-progress', 1)))
                return hid, block
    return None


def set_status(hid, status):
    with LOCK:
        text = open(HYP).read()
        text = re.sub(r'(## ' + re.escape(hid) + r'\b[^\n]*\n)status: \S+', r'\g<1>status: ' + status, text)
        open(HYP, 'w').write(text)


def ledger(hid, name, status, headline):
    with LOCK:
        open(LEDGER, 'a').write('| ' + ' | '.join([hid, name, 'see HYPOTHESES.md', status, headline]) + ' |' + chr(10))


def next_id():
    ids = [int(x) for x in re.findall(r'YB-(\d{4})', open(HYP).read() + open(LEDGER).read())]
    return 'YB-%04d' % (max(ids + [0]) + 1)


# ---------------- API ----------------
def call(messages, model=MODEL, max_tokens=32000, system=None, cache=True):
    body = {'model': model, 'max_tokens': max_tokens, 'system': system if system is not None else SYSTEM,
            'messages': messages}
    if cache: body['cache_control'] = {'type': 'ephemeral'}
    req = urllib.request.Request(API_URL, json.dumps(body).encode(), {
        'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01',
        'content-type': 'application/json'})
    with urllib.request.urlopen(req, timeout=900) as r:
        d = json.load(r)
    spend(d.get('usage', {}))
    text = ''.join(b.get('text', '') for b in d['content'] if b['type'] == 'text')
    m = re.search(r'\{.*\}', text, re.S)
    return text, json.loads(m.group(0) if m else text)


def ledger_digest(limit=4000):
    rows = [l for l in open(LEDGER).read().splitlines() if l.startswith('| YB-')]
    return chr(10).join(rows)[-limit:]


# ---------------- stages ----------------
def triage(hid, block):
    """Cheap model: is this worth the expensive build? Returns (score 0-20, reason)."""
    sysmsg = [{'type': 'text', 'text': FOUNDATION + chr(10) + 'You gate an expensive research pipeline. Score the '
               'hypothesis: novelty 0-10 (vs the ledger and known literature) and feasibility 0-10 (testable in '
               'the stated toy setting in <10 min). Reply ONLY JSON {"novelty":n,"feasibility":n,"duplicate_of":null,"reason":"..."}'}]
    msg = 'LEDGER:' + chr(10) + ledger_digest() + chr(10) + chr(10) + 'HYPOTHESIS ' + hid + ':' + chr(10) + block
    _, out = call([{'role': 'user', 'content': msg}], model=TRIAGE_MODEL, max_tokens=400, system=sysmsg, cache=False)
    if out.get('duplicate_of'): return 0, 'duplicate of ' + str(out['duplicate_of'])
    return int(out.get('novelty', 0)) + int(out.get('feasibility', 0)), str(out.get('reason', ''))[:160]


def propose():
    """Recursive step: new hypotheses from the foundation + ledger (open problems first)."""
    with LOCK:
        if NEW_COUNT[0] >= MAX_NEW: return False
        n = min(2, MAX_NEW - NEW_COUNT[0])
        prompt = ('LEDGER so far:' + chr(10) + ledger_digest() + chr(10) + chr(10) + 'Propose ' + str(n) +
                  ' NEW testable hypotheses that follow from the results (prioritize open problems and failure modes) '
                  'or open a new biological mechanism. Reply ONLY JSON {"hypotheses":[{"name":"...",'
                  '"foundation":"...","hypothesis":"...","test":"..."}]}')
        _, out = call([{'role': 'user', 'content': prompt}], max_tokens=2000)
        added = 0
        for h in out.get('hypotheses', [])[:n]:
            hid = next_id()
            entry = (chr(10) + '## ' + hid + ' \u2014 ' + h['name'] + chr(10) + 'status: open' + chr(10) + 'foundation: '
                     + h['foundation'] + chr(10) + 'hypothesis: ' + h['hypothesis'] + chr(10) + 'test: ' + h['test']
                     + chr(10) + 'origin: proposed by miner' + chr(10))
            open(HYP, 'a').write(entry); added += 1
        NEW_COUNT[0] += added
        return added > 0


def write(dirpath, files):
    for rel, content in files.items():
        p = os.path.normpath(os.path.join(dirpath, rel))
        if not p.startswith(dirpath + os.sep):
            raise ValueError('path escapes sandbox: ' + rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(content)


def run_tests(d):
    cmd = [os.path.join(ROOT, 'sandbox', 'run.sh'), d, 'all'] if SANDBOX == 'docker' else ['make', '-C', d, 'all']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        return r.returncode == 0, (r.stdout + r.stderr)[-3000:]
    except subprocess.TimeoutExpired:
        return False, 'TIMEOUT after 1800s'


def mine_one(hid, block):
    name = block.splitlines()[0].split('\u2014', 1)[-1].strip()
    start = load_state()['used']
    score, why = triage(hid, block)
    if score < MIN_SCORE:
        set_status(hid, 'skipped'); ledger(hid, name, 'skipped at triage', 'score %d/20: %s' % (score, why))
        return hid + ': SKIPPED (score %d) %s' % (score, why)
    slug = hid + '-' + re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:50]
    box = os.path.join(SANDBOX_DIR, slug); shutil.rmtree(box, ignore_errors=True); os.makedirs(box)
    msgs = [{'role': 'user', 'content': 'Algorithm ID ' + hid + '.' + chr(10) + block}]
    log, out = '', {}
    for attempt in range(REPAIRS + 1):
        if budget_left() <= 0:
            set_status(hid, 'open'); return hid + ': budget exhausted, returned to backlog'
        try:
            raw, out = call(msgs)
            write(box, out['files'])
        except Exception as e:
            log = 'generation error: ' + str(e)[:500]
            msgs += [{'role': 'user', 'content': log + '. Resend valid JSON.'}]; continue
        ok, log = run_tests(box)
        cost = load_state()['used'] - start
        if ok:
            dest = os.path.join(ROOT, 'algorithms', slug); shutil.rmtree(dest, ignore_errors=True)
            shutil.move(box, dest); set_status(hid, 'tested')
            ledger(hid, name, 'tested', out.get('summary', '')[:200] + ' (%s tokens)' % format(cost, ','))
            if os.environ.get('MINER_PUBLISH') == '1':
                subprocess.run([os.path.join(ROOT, 'publish.sh'), 'Mined ' + hid], cwd=ROOT)
            return hid + ': PASS - ' + out.get('summary', '') + ' (%s tokens)' % format(cost, ',')
        msgs += [{'role': 'assistant', 'content': raw},
                 {'role': 'user', 'content': 'make all failed (log tail below). Send ONLY the files you change.' + chr(10) + log}]
    cost = load_state()['used'] - start
    set_status(hid, 'failed')
    ledger(hid, name, 'failed build/test', (log.splitlines() or [''])[-1][:160] + ' (%s tokens)' % format(cost, ','))
    return hid + ': FAILED after %d attempts' % (REPAIRS + 1)


def worker(_):
    results = []
    while budget_left() > 0:
        job = claim()
        if not job:
            if not propose(): break
            continue
        results.append(mine_one(*job))
        print(results[-1], '| used today: %s/%s' % (format(load_state()['used'], ','), format(BUDGET, ',')), flush=True)
    return results


def macos_sdk():
    if sys.platform != 'darwin' or os.environ.get('SDKROOT'): return
    import glob, tempfile
    src = os.path.join(tempfile.gettempdir(), '_sdk_probe.c'); open(src, 'w').write('double f(double x){return x;}')
    probe = lambda env: subprocess.run(['gcc', '-shared', '-fPIC', '-o', src + '.so', src, '-lm'], env=env,
                                       capture_output=True).returncode == 0
    if probe(os.environ): return
    for sdk in ['/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk'] + \
               sorted(glob.glob('/Library/Developer/CommandLineTools/SDKs/MacOSX*.sdk'), reverse=True):
        if probe({**os.environ, 'SDKROOT': sdk}):
            os.environ['SDKROOT'] = sdk; return


if __name__ == '__main__':
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    if DRY:
        opened = [b.split()[1] for b in blocks(open(HYP).read()) if 'status: open' in b]
        print('DRY RUN: %d open hypotheses: %s; budget left %s; cached context ~%d tokens'
              % (len(opened), opened, format(budget_left(), ','), len(SYSTEM[0]['text']) // 4)); sys.exit(0)
    if 'ANTHROPIC_API_KEY' not in os.environ:
        sys.exit('ANTHROPIC_API_KEY not set')
    if SANDBOX == 'docker':
        if subprocess.run([os.path.join(ROOT, 'sandbox', 'ensure_docker.sh')]).returncode:
            sys.exit('Refusing to run model-written code without the Docker sandbox.')
    else:
        print('WARNING: MINER_SANDBOX=host, model-written code will run directly on this machine.'); macos_sdk()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(worker, range(WORKERS)))
    s = load_state()
    print('Mining run complete. Weighted tokens used today: %s; raw usage: %s' % (format(s['used'], ','), s['raw']))
