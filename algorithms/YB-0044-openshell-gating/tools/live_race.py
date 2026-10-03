# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0044 live race (pre-registered; docs/PREREGISTRATION.md). Usage: live_race.py <arm B|C> [max_episodes].
For each replay-plan episode, an agent inside OpenShell sandbox agr-py signals start (GET /health), waits D seconds (the
recorded answer time), then commits (POST /transfer with the episode id). Time zero = arrival of the start signal at the mock
service (Mac clock), so sandbox start-up delay cannot bias the race. Arm B (reactive block): policy allow; at t_alarm the host
issues policy set deny (no wait); the agent makes one attempt. Arm C (hold until cleared): policy deny by default; at D the host
releases with policy set allow --wait only if there was no alarm; the agent retries every 50 ms for up to 12 s.
Ground truth: the mock service log. Writes docs/live_<arm>.jsonl (one row per episode, appended; resumable).'''
import json, os, subprocess, sys, time, base64
ARM = sys.argv[1]; MAXN = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
SB, LOG = 'agr-py', '/tmp/mock_commit.jsonl'
ENV = dict(os.environ, PATH='/opt/homebrew/bin:' + os.path.expanduser('~/.local/bin') + ':/usr/local/bin:/usr/bin:/bin')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAN = json.load(open('docs/replay_plan.json'))['episodes'][:MAXN]; OUT = 'docs/live_%s.jsonl' % ARM
done = {json.loads(l)['idx'] for l in open(OUT)} if os.path.exists(OUT) else set()
AGENT = ('import json, sys, time, urllib.request\n'
         'ep, D, retry = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3] == "1"\n'
         'U = "http://host.openshell.internal:18080"\n'
         'try: urllib.request.urlopen(U + "/health", timeout=5).read()\n'
         'except Exception: pass\n'
         'time.sleep(D); end = time.time() + 12\n'
         'while True:\n'
         '    try:\n'
         '        urllib.request.urlopen(urllib.request.Request(U + "/transfer", data=json.dumps(dict(ep=ep)).encode(), method="POST"), timeout=2).read(); break\n'
         '    except Exception:\n'
         '        if not retry or time.time() > end: break\n'
         '        time.sleep(0.05)\n')
B64 = base64.b64encode(AGENT.encode()).decode()
def setpol(mode, wait=True):
    a = ['openshell', 'policy', 'set', SB, '--policy', 'policies/%s.yaml' % mode] + (['--wait'] if wait else [])
    return subprocess.run(a, env=ENV, capture_output=True, text=True, timeout=120) if wait else subprocess.Popen(a, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def log_rows(since):
    return [json.loads(l) for l in open(LOG) if json.loads(l)['t'] > since]
subprocess.run(['openshell', 'sandbox', 'exec', '-n', SB, '--no-login-shell', '--', 'sh', '-c', 'echo ' + B64 + ' | base64 -d > /tmp/agent.py'], env=ENV, capture_output=True, timeout=60)
state = None
for e in PLAN:
    if e['idx'] in done: continue
    want = 'allow' if ARM == 'B' else 'deny'
    if state != want: setpol(want); state = want
    tl = time.time()
    p = subprocess.Popen(['openshell', 'sandbox', 'exec', '-n', SB, '--no-login-shell', '--', 'python3', '/tmp/agent.py', str(e['idx']), str(e['D']), '1' if ARM == 'C' else '0'], env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = None
    while t0 is None and time.time() - tl < 30:
        h = [r for r in log_rows(tl) if r['path'].startswith('/health')]
        t0 = h[0]['t'] if h else None; time.sleep(0.01)
    act = None
    if t0 is not None:
        if ARM == 'B' and e['t_alarm'] is not None:
            while time.time() < t0 + e['t_alarm']: time.sleep(0.001)
            act = time.time(); setpol('deny', wait=False); state = 'deny?'
        if ARM == 'C' and e['t_alarm'] is None:
            while time.time() < t0 + e['D']: time.sleep(0.001)
            act = time.time(); setpol('allow'); state = 'allow'
    try: p.wait(timeout=e['D'] + 40)
    except subprocess.TimeoutExpired: p.kill()
    time.sleep(0.5)
    c = [r for r in log_rows(tl) if r['path'] == '/transfer' and isinstance(r['body'], dict) and r['body'].get('ep') == e['idx']]
    row = dict(idx=e['idx'], correct=e['correct'], D=e['D'], t_alarm=e['t_alarm'], arm=ARM, started=t0 is not None,
               committed=bool(c), commit_delay_s=round(c[0]['t'] - (t0 + e['D']), 3) if (c and t0) else None, action_s=round(act - t0, 3) if (act and t0) else None)
    with open(OUT, 'a') as f: f.write(json.dumps(row) + chr(10))
    print(json.dumps(row), flush=True)
    if ARM == 'C' and state == 'allow': setpol('deny'); state = 'deny'
    if ARM == 'B' and state == 'deny?': setpol('allow'); state = 'allow'
print('ARM_DONE', ARM)
