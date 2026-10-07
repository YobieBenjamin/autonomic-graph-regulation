#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0050 chain (one command, resumable; start it with agr/yb0050_start.sh). Each stage runs alone and stops at the first failure.
# Before the timestamp: unit tests -> smoke -> dry run (sandbox) -> publish (commit + push) -> plan unchanged -> timestamp (rule 13).
# After the timestamp: alignment tests (rule 8) -> record test seeds 15-26 -> self-consistency on every answered episode -> pack ->
# completeness check -> confirmatory analysis (rule 14) -> publish results -> public snapshot. Never re-timestamps (rule 16).
export PATH=$HOME/.lmstudio/bin:/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH
cd "$(dirname "$0")/.."; D=algorithms/YB-0050-powered-decider; L=/tmp/chain50.log; P=$D/docs/PREREGISTRATION.md; SEEDS="15 16 17 18 19 20 21 22 23 24 25 26"
say() { echo "[$(date -u +%F' '%H:%M:%S)] $*" >> $L; cp $L agr/yb0050_chain_progress.log 2>/dev/null; }
say START
if ls $P.*.tsr >/dev/null 2>&1 && git diff --quiet HEAD -- $P agr/selfcons_yb0050.py agr/recorder.py; then say RESUME_AFTER_TIMESTAMP; else
  SANDBOX_MEM=12g SANDBOX_TIMEOUT=1800 sandbox/run.sh $D test > /tmp/t50.log 2>&1 || { say STOP unit tests failed; exit 1; }; say TESTS_OK
  SANDBOX_MEM=16g SANDBOX_TIMEOUT=3600 sandbox/run.sh $D smoke > /tmp/s50.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/smoke.json ] || { say STOP smoke failed; exit 1; }; say SMOKE_OK
  SANDBOX_MEM=28g SANDBOX_TIMEOUT=14400 sandbox/run.sh $D dryrun > /tmp/d50.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/dryrun.json ] || { say STOP dry run failed; exit 1; }; say DRYRUN_OK
  SANDBOX_MEM=28g ./publish.sh 'YB-0050 powered decider and scaling measurements: pre-registration, analysis, tests, recorders, chain, smoke and dry run (synthetic self-consistency)' > /tmp/pub50.log 2>&1 || { say STOP publish failed; exit 1; }
  git diff --quiet HEAD -- $P agr/selfcons_yb0050.py agr/recorder.py || { say STOP plan or recorder differs from commit; exit 1; }; say COMMITTED $(git log --oneline -1 | cut -c1-7)
  scripts/timestamp_prereg.sh $P > /tmp/ts50.log 2>&1
  [ $(grep -c 'Verification: OK' /tmp/ts50.log) -ge 2 ] || { say STOP timestamp not verified; exit 1; }; say TIMESTAMPED
fi
if ! pmset -g batt | grep -q 'AC Power'; then say WAITING_FOR_AC_POWER before recording; until pmset -g batt | grep -q 'AC Power'; do sleep 60; done; say ON_AC_POWER; fi
.venv/bin/python agr/test_layertap_alignment.py > /tmp/align50a.log 2>&1 || { say STOP telemetry alignment test failed; exit 1; }
.venv/bin/python agr/test_hstap_alignment.py > /tmp/align50b.log 2>&1 || { say STOP hidden-state alignment test failed; exit 1; }; say ALIGNMENT_OK
for S in $SEEDS; do
  f=data/agr/episodes_LH_seed$S.jsonl
  if [ -f $f ] && [ "$(wc -l < $f | tr -d ' ')" = 600 ]; then continue; fi
  .venv/bin/python agr/recorder.py 100 800 --layers --hs --seed=$S > /tmp/rec50_$S.log 2>&1 || { say "STOP recording seed $S failed"; exit 1; }
  say "SEED_${S}_RECORDED $(wc -l < $f | tr -d ' ') episodes"
done
say SELFCONS_START
.venv/bin/python agr/selfcons_yb0050.py > /tmp/sc50.log 2>&1 || { say STOP self-consistency recorder failed; exit 1; }
for S in $SEEDS; do
  a=$(.venv/bin/python -c "import json; print(sum(1 for l in open('data/agr/episodes_LH_seed$S.jsonl') if json.loads(l)['answered']))")
  n=$(wc -l < data/agr/selfcons_yb0050_seed$S.jsonl | tr -d ' ')
  [ "$a" = "$n" ] || { say "STOP seed $S self-consistency incomplete: $n of $a"; exit 1; }; say "SEED_${S}_SELFCONS_COMPLETE $n of $a"
  cp data/agr/selfcons_yb0050_seed$S.jsonl $D/data/
done
.venv/bin/python - <<'PY' >> $L 2>&1 || { say STOP packing failed; exit 1; }
import json, gzip, os, numpy as np
D = 'algorithms/YB-0050-powered-decider/data'
for S in [str(s) for s in range(15, 27)]:   # same packing as agr/yb0045_chain.sh (no shift)
    src = 'data/agr/episodes_LH_seed%s.jsonl' % S; R = [json.loads(l) for l in open(src)]
    assert all('toks' in r for r in R), 'fixed recorder required'
    with gzip.open(os.path.join(D, 'seed%s_LH.jsonl.gz' % S), 'wt') as f: f.write(open(src).read())
    lay, hs = {}, {}
    for r in R:
        st = np.load('data/agr/layers_LH_seed%s/%d.npy' % (S, r['idx'])).astype(float)
        assert len(st) == r['n_tokens'], 'fixed tap: one reading per generated token'
        X = st[:max(r['final_start'], 2)]; X[:, :, :3] = np.log1p(np.maximum(X[:, :, :3], 0)); lay['i%d' % r['idx']] = X.astype(np.float16)
        z = np.load('data/agr/hs_seed%s/%d.npz' % (S, r['idx']))
        for k in z.files: hs['i%d_%s' % (r['idx'], k)] = z[k]
    np.savez_compressed(os.path.join(D, 'layers_LH_seed%s_0.npz' % S), **lay); np.savez_compressed(os.path.join(D, 'hs_seed%s.npz' % S), **hs)
    print('packed seed', S, len(R), 'episodes, no shift')
PY
say PACKED
SANDBOX_MEM=28g SANDBOX_TIMEOUT=14400 sandbox/run.sh $D confirmatory > /tmp/conf50.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/results.json ] || { say STOP confirmatory failed; exit 1; }; say CONFIRMATORY_OK
SANDBOX_MEM=28g ./publish.sh 'YB-0050 results, test-seed recordings 15-26 and self-consistency' > /tmp/pub50r.log 2>&1 || { say STOP results publish failed; exit 1; }; say RESULTS_COMMITTED $(git log --oneline -1 | cut -c1-7)
scripts/make_public_snapshot.sh >> /tmp/pub50r.log 2>&1 && say PUBLIC_SNAPSHOT_OK || say PUBLIC_SNAPSHOT_FAILED
say DONE
