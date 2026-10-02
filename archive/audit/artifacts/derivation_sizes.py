# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Sixth audit m4/m5: derivation-set sizes of YB-0035 vs YB-0042, and seed-8 counts, from committed packed data.
Run from the repo root. Writes archive/audit/artifacts/derivation_sizes.json.'''
import json, gzip
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]
def summ(R):
    a = [r for r in R if r['answered']]
    return dict(recorded=len(R), answered=len(a), wrong=sum(1 for r in a if not r['correct']), answered_with_checkpoint=sum(1 for r in a if r['final_start'] > 48))
out = {'YB-0035 derivation': {S: summ(ld('algorithms/YB-0035-corrected-realtime-race/data/seed%s_L.jsonl.gz' % S)) for S in ('2', '3', '4')},
       'YB-0042 derivation': {S: summ(ld('algorithms/YB-0042-probe-baseline/data/seed%s_LH.jsonl.gz' % S)) for S in ('2', '3', '4')},
       'YB-0042 test seed 8': summ(ld('algorithms/YB-0042-probe-baseline/data/seed8_LH.jsonl.gz'))}
for k in ('YB-0035 derivation', 'YB-0042 derivation'):
    out[k]['total'] = {f: sum(v[f] for v in out[k].values()) for f in ('recorded', 'answered', 'wrong', 'answered_with_checkpoint')}
json.dump(out, open('archive/audit/artifacts/derivation_sizes.json', 'w'), indent=1); print(json.dumps(out))
