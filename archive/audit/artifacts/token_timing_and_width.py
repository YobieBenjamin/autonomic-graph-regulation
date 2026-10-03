# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Eighth audit (GLM G7, G9, G10): commit the evidence for two figures used in the posts. (1) Per-token generation time of
gpt-oss-20b in the YB-0045 test recordings (per-token latencies stored in each episode). (2) Hidden-state width per layer,
read from the recorded hidden-state snapshots. Writes archive/audit/artifacts/token_timing_and_width.json.'''
import json, gzip, numpy as np
D = 'algorithms/YB-0045-powered-replication/data/'
lat = []
for S in ('9', '13', '14'):
    for l in gzip.open(D + 'seed%s_LH.jsonl.gz' % S, 'rt'):
        r = json.loads(l); lat += [x for x in r['latency'][1:]]
lat = np.array(lat, float) * 1000
z = np.load(D + 'hs_seed9.npz'); k = z.files[0]; w = int(z[k].shape[-1])
out = dict(per_token_ms=dict(n_tokens=int(lat.size), median=round(float(np.median(lat)), 2), p10=round(float(np.percentile(lat, 10)), 2), p90=round(float(np.percentile(lat, 90)), 2)),
           hidden_state_width_per_layer=w, telemetry_values_per_token=120, ratio_one_layer_to_telemetry=round(w / 120, 1), source='YB-0045 test seeds 9, 13, 14')
json.dump(out, open('archive/audit/artifacts/token_timing_and_width.json', 'w'), indent=1); print(json.dumps(out))
