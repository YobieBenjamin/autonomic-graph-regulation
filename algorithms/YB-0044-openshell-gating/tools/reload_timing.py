# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0044 exploratory engineering measurement (informs the design; not a hypothesis test): how long a hot-reloaded OpenShell
network policy takes to take effect on a running sandbox. A client inside sandbox agr-py POSTs to the mock commit service
every 50 ms. The host alternates policies deny.yaml / allow.yaml (identical except one allow rule) with openshell policy set
--wait. Ground truth is the mock service's arrival log (Mac clock). Per flip: command duration, and the effective latency =
last arrival after a deny command (block) or first arrival after an allow command (unblock). Writes docs/reload_timing.json.'''
import json, os, subprocess, sys, time, base64, statistics
SB, N, LOG = 'agr-py', int(sys.argv[1]) if len(sys.argv) > 1 else 20, '/tmp/mock_commit.jsonl'   # the running mock service on 18080 (started before its tunnel; see docs)
ENV = dict(os.environ, PATH='/opt/homebrew/bin:' + os.path.expanduser('~/.local/bin') + ':/usr/local/bin:/usr/bin:/bin')
HERE = os.path.dirname(os.path.abspath(__file__)); POL = os.path.join(os.path.dirname(HERE), 'policies')
os.chdir(os.path.dirname(HERE))
CLIENT = ('import json, time, urllib.request\n'
          'i = 0\n'
          'while True:\n'
          '    i += 1\n'
          '    try:\n'
          '        urllib.request.urlopen(urllib.request.Request("http://host.openshell.internal:18080/transfer", data=json.dumps(dict(seq=i)).encode(), method="POST"), timeout=2).read()\n'
          '    except Exception:\n'
          '        pass\n'
          '    time.sleep(0.05)\n')
def sh(args, timeout=120): return subprocess.run(args, env=ENV, capture_output=True, text=True, timeout=timeout)
def arrivals(): return [json.loads(l)['t'] for l in open(LOG) if '/transfer' in l] if os.path.exists(LOG) else []
b64 = base64.b64encode(CLIENT.encode()).decode()
sh(['openshell', 'policy', 'set', SB, '--policy', os.path.join(POL, 'allow.yaml'), '--wait'])
cli = subprocess.Popen(['openshell', 'sandbox', 'exec', '-n', SB, '--no-login-shell', '--', 'sh', '-c', 'echo ' + b64 + ' | base64 -d > /tmp/loop.py && exec python3 /tmp/loop.py'], env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
rows = []
for k in range(N):
    for mode in ('deny', 'allow'):
        t0 = time.time(); r = sh(['openshell', 'policy', 'set', SB, '--policy', os.path.join(POL, mode + '.yaml'), '--wait']); t1 = time.time()
        time.sleep(6 if mode == 'deny' else 4)
        a = arrivals(); after = [x for x in a if x > t0]
        if mode == 'deny':
            last = max(after) if after else None; eff = round(last - t0, 3) if last else 0.0
        else:
            first = min(after) if after else None; eff = round(first - t0, 3) if first else None
        rows.append(dict(cycle=k, mode=mode, command_s=round(t1 - t0, 3), effective_s=eff, ok=r.returncode == 0, arrivals_after_command=len(after)))
        print(json.dumps(rows[-1]), flush=True)
cli.terminate()
def summ(xs):
    xs = [x for x in xs if x is not None]
    return dict(n=len(xs), median=round(statistics.median(xs), 3), min=round(min(xs), 3), max=round(max(xs), 3)) if xs else None
out = dict(note='EXPLORATORY engineering measurement for YB-0044 design; OpenShell 0.1.2 on Colima (see docs/OPENSHELL_SETUP.md); client every 50 ms',
           block=dict(command=summ([r['command_s'] for r in rows if r['mode'] == 'deny']), effective=summ([r['effective_s'] for r in rows if r['mode'] == 'deny'])),
           unblock=dict(command=summ([r['command_s'] for r in rows if r['mode'] == 'allow']), effective=summ([r['effective_s'] for r in rows if r['mode'] == 'allow'])),
           failures=sum(1 for r in rows if not r['ok']), rows=rows)
json.dump(out, open('docs/reload_timing.json', 'w'), indent=1); print('SUMMARY', json.dumps({k: out[k] for k in ('block', 'unblock', 'failures')}))
