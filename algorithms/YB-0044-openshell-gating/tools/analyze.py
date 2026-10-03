# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0044 pre-registered analysis. Inputs: docs/replay_plan.json, docs/live_B.jsonl, docs/live_C.jsonl. Episodes whose agent
did not start (harness failure) are excluded from both arms and counted. Arm A (permission only) is computed: every commit is
permitted. H1: among wrong answers, prevented share C minus B, paired bootstrap (1,000 resamples, numpy seed 0); supported iff
the 95% lower bound > 0. H2: among wrong answers with an in-time alarm, share still committed under B; supported iff the 95%
lower bound > 0.5. Costs: correct commits held (C) or blocked (B); delay of released commits in C. Writes docs/results.json.'''
import json, os, numpy as np
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rd = lambda p: {r['idx']: r for r in (json.loads(l) for l in open(p))} if os.path.exists(p) else {}
P = {e['idx']: e for e in json.load(open('docs/replay_plan.json'))['episodes']}; B, C = rd('docs/live_B.jsonl'), rd('docs/live_C.jsonl')
if not B or not C: print('live runs not complete: nothing to analyse'); raise SystemExit(0)
ok = [i for i in P if i in B and i in C and B[i]['started'] and C[i]['started']]; failed = len(P) - len(ok)
W = [i for i in ok if not P[i]['correct']]; K = [i for i in ok if P[i]['correct']]
pb = np.array([not B[i]['committed'] for i in W], float); pc = np.array([not C[i]['committed'] for i in W], float)
g = np.random.default_rng(0); d = [(pc[s] - pb[s]).mean() for s in (g.integers(0, len(W), len(W)) for _ in range(1000))]
h1 = [round(float((pc - pb).mean()), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]
WA = [i for i in W if P[i]['t_alarm'] is not None]; lost = np.array([B[i]['committed'] for i in WA], float)
d2 = [lost[s].mean() for s in (g.integers(0, len(WA), len(WA)) for _ in range(1000))] if WA else [0]
h2 = [round(float(lost.mean()), 4) if WA else None, round(float(np.percentile(d2, 2.5)), 4), round(float(np.percentile(d2, 97.5)), 4)]
rel = [C[i]['commit_delay_s'] for i in ok if C[i]['committed'] and C[i]['commit_delay_s'] is not None]
res = dict(episodes_planned=len(P), harness_failures_excluded=failed, analysed=len(ok), wrong=len(W), correct=len(K),
           arm_A_permission_only=dict(wrong_committed=len(W), prevented=0),
           arm_B_reactive=dict(wrong_prevented=int(pb.sum()), correct_blocked=sum(1 for i in K if not B[i]['committed'])),
           arm_C_hold=dict(wrong_prevented=int(pc.sum()), correct_held=sum(1 for i in K if not C[i]['committed'])),
           H1_prevented_C_minus_B=h1, H1_supported=bool(h1[1] > 0),
           H2_inTime_alarms_on_wrong=len(WA), H2_share_still_committed_under_B=h2, H2_supported=bool(WA and h2[1] > 0.5),
           C_release_delay_s=dict(n=len(rel), median=round(float(np.median(rel)), 3) if rel else None, p90=round(float(np.percentile(rel, 90)), 3) if rel else None))
json.dump(res, open('docs/results.json', 'w'), indent=1); print(json.dumps(res))
