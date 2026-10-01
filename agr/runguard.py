# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Run-alone guard and environment provenance (Phase D; self-finding S1: GPU sharing changed greedy outputs across
sessions). check_alone() aborts if another heavy job is running (override: ALLOW_SHARED=1, which is recorded).
write_env() saves an environment snapshot next to the data it describes.'''
import json, os, platform, subprocess, sys, time
HEAVY = ('agr/recorder.py', 'agr/recorder_qwen.py', 'agr/prefix_monitors.py', 'agr/monitors.py', 'sandbox/run.sh')

def _others():
    me = {os.getpid(), os.getppid()}
    try: out = subprocess.run(['ps', '-Ao', 'pid=,command='], capture_output=True, text=True).stdout
    except Exception: return []
    found = []
    for line in out.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and int(parts[0]) not in me and any(h in parts[1] for h in HEAVY) and 'grep' not in parts[1]:
            found.append(parts[1][:120])
    return found

def check_alone(role):
    others = _others()
    if others and os.environ.get('ALLOW_SHARED') != '1':
        sys.exit('RUN-ALONE GUARD (%s): other heavy jobs are running; refusing to start so results are not perturbed:\n  ' % role + '\n  '.join(others) + '\nSet ALLOW_SHARED=1 to override (the override is recorded).')
    return others

def _ver(mod):
    try: return __import__(mod).__version__
    except Exception:
        try:
            from importlib.metadata import version; return version(mod.replace('_', '-'))
        except Exception: return None

def write_env(path, role, model=None, extra=None):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try: commit = subprocess.run(['git', '-C', root, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except Exception: commit = None
    env = dict(role=role, started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), git_commit=commit, model=model,
               python=platform.python_version(), macos=platform.mac_ver()[0], machine=platform.machine(),
               mlx=_ver('mlx'), mlx_lm=_ver('mlx_lm'), mlx_metal=_ver('mlx_metal'), numpy=_ver('numpy'),
               concurrent_heavy_jobs=_others(), allow_shared=os.environ.get('ALLOW_SHARED') == '1')
    if extra: env.update(extra)
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(env, open(path, 'w'), indent=1); return env
