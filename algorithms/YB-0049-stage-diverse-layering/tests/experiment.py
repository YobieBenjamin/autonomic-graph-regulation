# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0049 analysis (pre-registered; docs/PREREGISTRATION.md): stage-diverse layering. Stage 1 = hidden-state probe in time (YB-0045 code);
stage 2 = post-answer self-consistency (data/selfcons_yb0049_seed*.jsonl, recorded AFTER the plan was timestamped). SMOKE=1 and DRY_RUN=1 use
derivation seeds only with SYNTHETIC stage-2 scores (pipeline check, no test data). Confirmatory run only via make confirmatory.'''
import json, gzip, os, sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints
from corrected import in_time_max
from probe import Probe, select
from layered import choose, alarm, recall_layered, recall_single, boot, tight, D_GRID
from sklearn.metrics import roc_auc_score
COST, DRY = 0.005, os.environ.get('DRY_RUN') == '1'
DERIV = ('2', '3', '4', '5', '6', '7', '8', '10', '11', '12'); TEST = ('9', '13', '14')
if DRY: DERIV, TEST = ('2', '3', '4', '5', '6', '7', '8'), ('10', '11', '12')
SMOKE = os.environ.get('SMOKE') == '1'
if SMOKE: DRY, DERIV, TEST = True, ('2', '3'), ('10',)
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]
def load_seed(S, off):
    R = [dict(r, idx=off + r['idx']) for r in ld('data/seed%s_LH.jsonl.gz' % S)]
    if SMOKE: R = R[:150]
    h = np.load('data/hs_seed%s.npz' % S); H = {}
    for k in h.files:
        i, rest = k[1:].split('_', 1); H.setdefault(off + int(i), {})[rest] = h[k]
    return R, H
def in_time(R, fn, cost):
    V = []
    for r in R:
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
        V.append(in_time_max([(fn(r, t), float(lat[:t].sum()), cost(r, t), D) for t in checkpoints(r)]))
    return np.array(V)
def main():
    if not DRY and os.environ.get('RUN_CONFIRMATORY') != '1':
        print('pre-registration stage: the confirmatory analysis runs only via make confirmatory, after the public timestamp'); return
    if not all(os.path.exists('data/seed%s_LH.jsonl.gz' % S) for S in DERIV + TEST):
        print('YB-0045 recordings not present (public checkout): nothing to analyse'); return
    SC = {}
    if not DRY:
        for S in TEST:
            p = 'data/selfcons_yb0049_seed%s.jsonl' % S
            if not os.path.exists(p): print('stage-2 recordings missing for seed', S); return
            for l in open(p): d = json.loads(l); SC[100000 * int(S) + d['idx']] = d
    Rd, Hd = [], {}
    for S in DERIV:
        R, H = load_seed(S, 100000 * int(S)); Rd += R; Hd.update(H)
    R8, H8, PJ = [], {}, {}
    for S in TEST:
        R, H = load_seed(S, 100000 * int(S)); R8 += R; H8.update(H)
        p = 'data/prefix_judge_abs_s%s.jsonl.gz' % S
        if os.path.exists(p): PJ.update({(100000 * int(S) + d['idx'], int(d['f'])): d for d in ld(p)})
    Rd = [r for r in Rd if r['answered'] and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]; (bl, bc), _ = select(jobs, Hd); P = Probe(bl, bc).fit(jobs, Hd)
    havej = len(PJ) > 0
    ok = lambda r: all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r)) and (not havej or all((r['idx'], t) in PJ for t in checkpoints(r)))
    A = [r for r in R8 if r['answered'] and ok(r)]; y = np.array([0 if r['correct'] else 1 for r in A])
    if DRY:   # synthetic stage 2 for pipeline checks only
        g = np.random.default_rng(7); d = np.where(g.random(len(A)) < 0.45 * y + 0.04, g.choice([0.25, 0.5, 0.75, 1.0], len(A)), 0.0); sec = np.full(len(A), 4.0)
    else:
        miss = [r['idx'] for r in A if r['idx'] not in SC]
        if miss: print('stage-2 scores missing for', len(miss), 'episodes'); return
        d = np.array([SC[r['idx']]['b2_disagree'] for r in A]); sec = np.array([SC[r['idx']]['review_seconds'] for r in A])
    v1 = in_time(A, lambda r, t: P.score(r, t, H8), lambda r, t: COST)
    rl, fl, t1, dl = recall_layered(v1, d, y); rs, fs, ts = recall_single(v1, y)
    h1 = boot(v1, d, y)
    a_l = alarm(v1, d, t1, dl); a_p = np.where(np.isfinite(v1), v1, -1e18) > ts
    td = tight(d[y == 0], 0.10); a_s = d > td
    missed = (y == 1) & ~a_p
    jac = lambda a, b: round(float(((a & b) & (y == 1)).sum() / max(1, ((a | b) & (y == 1)).sum())), 4)
    res = dict(dry_run=DRY, smoke=SMOKE, synthetic_stage2=DRY, deriv_seeds=DERIV, eval_seeds=TEST, probe_selected=dict(layer=bl, C=bc),
               eval_answered=len(A), eval_wrong=int(y.sum()), never_monitored=int((~np.isfinite(v1)).sum()),
               layered=dict(caught=int(a_l[y == 1].sum()), recall=round(rl, 4), fpr=round(fl, 4), stage1_alpha=0.05, delta=dl),
               probe_alone=dict(caught=int(a_p[y == 1].sum()), recall=round(rs, 4), fpr=round(fs, 4)),
               selfcons_alone=dict(caught=int(a_s[y == 1].sum()), fpr=round(float(a_s[y == 0].mean()), 4), auroc=round(float(roc_auc_score(y, d)), 4) if 0 < y.sum() < len(y) else None),
               H1_layered_minus_probe=h1, H1_supported=bool(h1[1] > 0),
               H2_probe_missed_errors=int(missed.sum()), H2_caught_by_stage2=int((missed & (d >= dl)).sum()) if dl is not None else 0,
               H3_jaccard_probe_selfcons=jac(a_p, a_s), H3_reference_jaccard_probe_text_YB0048=0.7431,
               S_stage2_errors_without_checkpoint=int(((~np.isfinite(v1)) & (y == 1) & (d >= dl)).sum()) if dl is not None else 0,
               S_review_seconds=dict(median=round(float(np.median(sec)), 3), p90=round(float(np.percentile(sec, 90)), 3)),
               S_allocation_sensitivity={str(a): dict(zip(('recall', 'fpr', 'tau1', 'delta'), [round(x, 4) if isinstance(x, float) else x for x in recall_layered(v1, d, y, a)])) for a in (0.025, 0.075)})
    out = 'docs/smoke.json' if SMOKE else ('docs/dryrun.json' if DRY else 'docs/results.json')
    json.dump(res, open(out, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print(json.dumps({k: res[k] for k in ('eval_answered', 'eval_wrong', 'layered', 'probe_alone', 'H1_layered_minus_probe', 'H1_supported', 'H2_probe_missed_errors', 'H2_caught_by_stage2')}, default=str))
if __name__ == '__main__': main()
