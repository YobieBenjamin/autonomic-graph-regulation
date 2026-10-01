# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0018 metabolic instrument: streams Apple-silicon CPU/GPU power (every 100 ms) from powermetrics, via the one
passwordless sudo rule installed for exactly this command (see agr/README.md). Samples are stamped with the host
monotonic clock (time.perf_counter) so they align with per-token timestamps from recorder.py.'''
import plistlib, subprocess, threading, time
CMD = ['sudo', '-n', '/usr/bin/powermetrics', '--samplers', 'cpu_power,gpu_power', '-i', '100', '-f', 'plist']

def _find(d, keys):
    '''Depth-first search for the first numeric value under any of keys (plist layout varies by macOS version).'''
    if isinstance(d, dict):
        for k in keys:
            if isinstance(d.get(k), (int, float)): return float(d[k])
        for v in d.values():
            r = _find(v, keys)
            if r is not None: return r
    return None

class PowerSampler:
    def __init__(self):
        self.samples, self._buf, self.error = [], b'', None   # samples: (t_perf, gpu_mW, cpu_mW)
        self.p = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.t = threading.Thread(target=self._read, daemon=True); self.t.start()
    def _read(self):
        try:
            for chunk in iter(lambda: self.p.stdout.read1(65536), b''):
                self._buf += chunk
                while b'\x00' in self._buf:
                    doc, self._buf = self._buf.split(b'\x00', 1)
                    doc = doc.strip()
                    if not doc: continue
                    d = plistlib.loads(doc)
                    self.samples.append((time.perf_counter(), _find(d, ['gpu_power', 'gpu_energy']), _find(d, ['cpu_power', 'cpu_energy'])))
        except Exception as e: self.error = repr(e)
    def window(self, t0, t1):
        '''Samples whose 100 ms interval overlaps [t0, t1].'''
        return [s for s in self.samples if t0 - 0.1 <= s[0] <= t1 + 0.1]
    def close(self):
        self.p.terminate()
        try: self.p.wait(timeout=3)
        except subprocess.TimeoutExpired: self.p.kill()
