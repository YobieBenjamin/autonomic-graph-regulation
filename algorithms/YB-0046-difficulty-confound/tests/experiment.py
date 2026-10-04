# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0046 analysis (pre-registered; docs/PREREGISTRATION.md): is the internal-state signal more than a difficulty detector?
Reuses YB-0045 code unchanged (src/ is a verified copy). Real run: fit on YB-0045 derivation seeds, evaluate on YB-0045 test seeds 9, 13, 14
(previously analysed in YB-0045: a pre-registered SECONDARY analysis, not a fresh test). DRY_RUN=1: fit on seeds 2-8, evaluate on 10-12,
never reading test seeds; writes docs/dryrun.json.'''
import json, gzip, os, sys, numpy as np
sys.path.insert(0, 'src')
from absrace import checkpoints, parallel_features, AbsOrganism
from corrected import in_time_max, cap_threshold, boot_diff, evaluate
from probe import Probe, select
from difficulty import DifficultyBaseline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
COST, T, DRY = 0.005, (48, 96, 192, 384), os.environ.get('DRY_RUN') == '1'
DERIV = ('2', '3', '4', '5', '6', '7', '8', '10', '11', '12'); TEST = ('9', '13', '14')
if DRY: DERIV, TEST = ('2', '3', '4', '5', '6', '7', '8'), ('10', '11', '12')
ld = lambda p: [json.loads(l) for l in gzip.open(p, 'rt')]

def load_seed(S, off):
    R = [dict(r, idx=off + r['idx']) for r in ld('data/seed%s_LH.jsonl.gz' % S)]
    z = np.load('data/layers_LH_seed%s_0.npz' % S); L = {off + int(k[1:]): z[k].astype(np.float32) for k in z.files}
    h = np.load('data/hs_seed%s.npz' % S); H = {}
    for k in h.files:
        i, rest = k[1:].split('_', 1); H.setdefault(off + int(i), {})[rest] = h[k]
    return R, L, H

def in_time(R, fn, cost):
    V = []
    for r in R:
        lat = np.asarray(r['latency'], float); D = float(lat[:r['final_start']].sum())
        V.append(in_time_max([(fn(r, t), float(lat[:t].sum()), cost(r, t), D) for t in checkpoints(r)]))
    return np.array(V)

def boot_auc(y, s, n=1000, seed=0):
    g = np.random.default_rng(seed); a = []
    for _ in range(n):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(y): a.append(roc_auc_score(y[i], s[i]))
    return [round(float(roc_auc_score(y, s)), 4), round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]

class Stack:
    '''H3 combined monitor: logistic regression on [difficulty-baseline logit, regulator score], fitted on CROSS-FITTED derivation scores.'''
    def fit(self, d, o, y):
        X = np.c_[np.log(np.clip(d, 1e-6, 1 - 1e-6) / (1 - np.clip(d, 1e-6, 1 - 1e-6))), o]; self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        self.lr = LogisticRegression(C=1.0, max_iter=5000).fit((X - self.mu) / self.sd, y); return self
    def score(self, d, o):
        x = np.array([np.log(np.clip(d, 1e-6, 1 - 1e-6) / (1 - np.clip(d, 1e-6, 1 - 1e-6))), o]); return float(self.lr.predict_proba(((x - self.mu) / self.sd)[None])[0, 1])

def main():
    if not DRY and os.environ.get('RUN_CONFIRMATORY') != '1':
        print('pre-registration stage: the confirmatory analysis runs only via make confirmatory, after the public timestamp'); return
    if not all(os.path.exists('data/seed%s_LH.jsonl.gz' % S) for S in DERIV + TEST):
        print('YB-0045 recordings not present (public checkout): nothing to analyse'); return
    Rd, Ld, Hd = [], {}, {}
    for S in DERIV:
        R, L, H = load_seed(S, 100000 * int(S)); Rd += R; Ld.update(L); Hd.update(H)
    R8, L8, H8, PJ = [], {}, {}, {}
    for S in TEST:
        R, L, H = load_seed(S, 100000 * int(S)); R8 += R; L8.update(L); H8.update(H)
        p = 'data/prefix_judge_abs_s%s.jsonl.gz' % S
        if os.path.exists(p): PJ.update({(100000 * int(S) + d['idx'], int(d['f'])): d for d in ld(p)})
    Rd = [r for r in Rd if r['answered'] and r['idx'] in Ld and all(('last_%d' % t) in Hd.get(r['idx'], {}) for t in checkpoints(r))]
    jobs = [(r, t) for r in Rd for t in checkpoints(r)]
    X = parallel_features(jobs, Ld, 4); O = AbsOrganism().fit_from(X, jobs)
    (bl, bc), _ = select(jobs, Hd); P = Probe(bl, bc).fit(jobs, Hd)
    DB = DifficultyBaseline(use_t=True).fit(jobs); D0 = DifficultyBaseline(use_t=False).fit(jobs)
    # cross-fitted derivation scores (same GroupKFold(5) as YB-0045) for the stacker
    yj = np.array([0 if r['correct'] else 1 for r, _ in jobs]); grp = np.array([r['idx'] for r, _ in jobs]); cfo, cfd = np.zeros(len(jobs)), np.zeros(len(jobs))
    for tr, te in GroupKFold(5).split(np.zeros(len(jobs)), yj, grp):
        Ot = AbsOrganism().fit_from(X[tr], [jobs[i] for i in tr]); Dt = DifficultyBaseline(use_t=True).fit([jobs[i] for i in tr])
        for i in te: r, t = jobs[i]; cfo[i] = Ot.score(r, Ld[r['idx']], t); cfd[i] = Dt.score(r, t)
    S = Stack().fit(cfd, cfo, yj)
    havej = len(PJ) > 0
    ok = lambda r: r['idx'] in L8 and all(('last_%d' % t) in H8.get(r['idx'], {}) for t in checkpoints(r)) and (not havej or all((r['idx'], t) in PJ for t in checkpoints(r)))
    A = [r for r in R8 if r['answered'] and ok(r)]; y = np.array([0 if r['correct'] else 1 for r in A]); mon = np.array([len(checkpoints(r)) > 0 for r in A])
    fixed, free = (lambda r, t: COST), (lambda r, t: 0.0)
    oc = {}; dc = {}
    for r in A:
        for t in checkpoints(r): oc[(r['idx'], t)] = O.score(r, L8[r['idx']], t); dc[(r['idx'], t)] = DB.score(r, t)
    V = dict(regulator=in_time(A, lambda r, t: oc[(r['idx'], t)], fixed), probe=in_time(A, lambda r, t: P.score(r, t, H8), fixed),
             difficulty_plus_length=in_time(A, lambda r, t: dc[(r['idx'], t)], free), difficulty_only=in_time(A, lambda r, t: D0.score(r, t), free),
             combined=in_time(A, lambda r, t: S.score(dc[(r['idx'], t)], oc[(r['idx'], t)]), fixed))
    if havej: V['judge'] = in_time(A, lambda r, t: PJ[(r['idx'], t)]['score'], lambda r, t: PJ[(r['idx'], t)]['compute_s'])
    per = {m: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in evaluate(v_, y, mon).items() if k != 'fired'} for m, v_ in V.items()}
    h1 = boot_diff(V['regulator'], V['difficulty_plus_length'], y); h2 = boot_diff(V['probe'], V['difficulty_plus_length'], y); h3 = boot_diff(V['combined'], V['difficulty_plus_length'], y)
    res = dict(dry_run=DRY, deriv_seeds=DERIV, eval_seeds=TEST, derivation_answered=len(Rd), derivation_observations=len(jobs), probe_selected=dict(layer=bl, C=bc),
               eval_answered=len(A), eval_wrong=int(y.sum()), monitors=per,
               difficulty_models={c: m[0] for c, m in DB.m.items()},
               H1_regulator_minus_difficulty=h1, H1_supported=bool(h1[1] > 0),
               H2_probe_minus_difficulty=h2, H2_supported=bool(h2[1] > 0),
               H3_combined_minus_difficulty=h3, H3_supported=bool(h3[1] > 0),
               S_difficulty_only_vs_with_length=boot_diff(V['difficulty_plus_length'], V['difficulty_only'], y))
    if havej: res['S_difficulty_minus_judge'] = boot_diff(V['difficulty_plus_length'], V['judge'], y); res['S_regulator_minus_judge'] = boot_diff(V['regulator'], V['judge'], y)
    pc = {}
    for t in T:
        idx = [i for i, r in enumerate(A) if t in checkpoints(r)]
        if len(idx) < 20 or y[idx].sum() < 3: continue
        yt = y[idx]; e = dict(regulator=boot_auc(yt, np.array([oc[(A[i]['idx'], t)] for i in idx])), probe=boot_auc(yt, np.array([P.score(A[i], t, H8) for i in idx])),
                              difficulty_plus_length=boot_auc(yt, np.array([dc[(A[i]['idx'], t)] for i in idx])),
                              combined=boot_auc(yt, np.array([S.score(dc[(A[i]['idx'], t)], oc[(A[i]['idx'], t)]) for i in idx])))
        pc[str(t)] = dict(episodes=len(idx), wrong=int(yt.sum()), auroc_with_ci=e)
    res['S_per_checkpoint_auroc'] = pc
    wc = {}
    for c in sorted(set(r['cat'] for r in A)):
        ii = [i for i, r in enumerate(A) if r['cat'] == c and len(checkpoints(r)) > 0]; yc = y[ii]
        if yc.sum() < 10 or yc.sum() == len(yc): wc[c] = dict(episodes=len(ii), wrong=int(yc.sum()), note='fewer than 10 wrong: not analysed'); continue
        e = {}
        for m in ('regulator', 'probe', 'difficulty_plus_length', 'combined'): e[m] = boot_auc(yc, V[m][ii])
        wc[c] = dict(episodes=len(ii), wrong=int(yc.sum()), in_time_score_auroc_with_ci=e)
    res['S_within_category'] = wc
    out = 'docs/dryrun.json' if DRY else 'docs/results.json'
    json.dump(res, open(out, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print(json.dumps({k: res[k] for k in ('eval_answered', 'eval_wrong', 'H1_regulator_minus_difficulty', 'H1_supported', 'H2_probe_minus_difficulty', 'H2_supported', 'H3_combined_minus_difficulty', 'H3_supported')}, default=str))

if __name__ == '__main__': main()
