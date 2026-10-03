# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0044 supplementary analysis (POST HOC, written in response to the eighth audit; not pre-registered). From the mock
service's own arrival log (docs/mock_service_log.jsonl, Mac clock): (1) when the live runs started relative to the RFC 3161
pre-registration timestamp (2026-10-02 18:08:17 UTC); (2) stalls between successive episode start signals per arm (gaps over
60 s); (3) H2 sensitivity: arm-B wins whose alarm-to-commit gap is shorter than the fastest isolated block (4.99 s,
docs/reload_timing.json) are re-counted as losses, since a leftover block from the previous episode may explain them.
Writes docs/supplementary.json.'''
import json, datetime as dt, numpy as np
U = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
L = [json.loads(l) for l in open('docs/mock_service_log.jsonl')]
STAMP = dt.datetime(2026, 10, 2, 18, 8, 17, tzinfo=dt.timezone.utc).timestamp()
H = sorted(r['t'] for r in L if r['path'].startswith('/health') and r['t'] >= STAMP)
B = [json.loads(l) for l in open('docs/live_B.jsonl')]; C = [json.loads(l) for l in open('docs/live_C.jsonl')]
nB = len(B); hB, hC = H[:nB], H[nB:nB + len(C)]
def stalls(h): return [dict(after_start=U(a), gap_s=round(b - a, 1)) for a, b in zip(h, h[1:]) if b - a > 60]
W = [r for r in B if not r['correct'] and r['t_alarm'] is not None]
won = [r for r in W if not r['committed']]; sus = [r for r in won if r['D'] - r['t_alarm'] < 4.99]
lost = np.array([r['committed'] or (r in sus) for r in W], float); g = np.random.default_rng(0)
bs = [lost[s].mean() for s in (g.integers(0, len(W), len(W)) for _ in range(1000))]
out = dict(note='POST HOC (eighth audit); not pre-registered', rfc3161_stamp=U(STAMP), first_live_start_signal=U(H[0]) if H else None,
           seconds_after_stamp=round(H[0] - STAMP, 1) if H else None, arm_B_start_signals=len(hB), arm_C_start_signals=len(hC),
           arm_B_window=[U(hB[0]), U(hB[-1])] if hB else None, arm_C_window=[U(hC[0]), U(hC[-1])] if hC else None,
           stalls_over_60s=dict(B=stalls(hB), C=stalls(hC)),
           H2_sensitivity=dict(suspicious_wins=[dict(idx=r['idx'], gap_s=round(r['D'] - r['t_alarm'], 2)) for r in sus],
                               share_lost_if_reclassified=[round(float(lost.mean()), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]))
json.dump(out, open('docs/supplementary.json', 'w'), indent=1); print(json.dumps(out)[:1500])
