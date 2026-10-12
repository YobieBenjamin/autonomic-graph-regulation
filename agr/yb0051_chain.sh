#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# YB-0051 chain (one command, resumable; start it with agr/yb0051_start.sh). Copy of agr/yb0050_chain.sh; changes: algorithm folder,
# test seeds 27-38, 8-sample review recorder run seed by seed, a 2-episode real-model review smoke on derivation seed 2 before the
# timestamp, and an AC-power check before every seed (lesson of the YB-0050 battery stop). Never re-timestamps (rule 16).
export PATH=$HOME/.lmstudio/bin:/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH
cd "$(dirname "$0")/.."; D=algorithms/YB-0051-low-false-alarm-precision; L=/tmp/chain51.log; P=$D/docs/PREREGISTRATION.md
SEEDS="27 28 29 30 31 32 33 34 35 36 37 38"; FROZEN="$P agr/selfcons_yb0051.py agr/recorder.py $D/tests/candidates.py $D/tests/score_test.py $D/tests/experiment.py"
say() { echo "[$(date -u +%F' '%H:%M:%S)] $*" >> $L; cp $L agr/yb0051_chain_progress.log 2>/dev/null; }
ac() { if ! pmset -g batt | grep -q 'AC Power'; then say "WAITING_FOR_AC_POWER $1"; until pmset -g batt | grep -q 'AC Power'; do sleep 60; done; say ON_AC_POWER; fi; }
say START
if ls $P.*.tsr >/dev/null 2>&1 && git diff --quiet HEAD -- $FROZEN; then say RESUME_AFTER_TIMESTAMP; else
  SANDBOX_MEM=12g SANDBOX_TIMEOUT=1800 sandbox/run.sh $D test > /tmp/t51.log 2>&1 || { say STOP unit tests failed; exit 1; }; say TESTS_OK
  rm -f data/agr/selfcons_yb0051_smoke_seed2.jsonl
  SMOKE_SEED=2 .venv/bin/python agr/selfcons_yb0051.py --limit 2 > /tmp/scs51.log 2>&1 || { say STOP review smoke failed; exit 1; }
  .venv/bin/python -c "import json; R=[json.loads(l) for l in open('data/agr/selfcons_yb0051_smoke_seed2.jsonl')]; assert len(R)==2 and all(len(r['answers'])==8 and r['review_seconds_k8']>=r['review_seconds_k4']>0 for r in R)" || { say STOP review smoke output wrong; exit 1; }; say REVIEW_SMOKE_OK
  SANDBOX_MEM=16g SANDBOX_TIMEOUT=3600 sandbox/run.sh $D smoke > /tmp/s51.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/smoke.json ] || { say STOP smoke failed; exit 1; }; say SMOKE_OK
  SANDBOX_MEM=28g SANDBOX_TIMEOUT=14400 sandbox/run.sh $D dryrun > /tmp/d51.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/dryrun.json ] || { say STOP dry run failed; exit 1; }; say DRYRUN_OK
  SANDBOX_MEM=28g ./publish.sh 'YB-0051 precision at low false-alarm rates: pre-registration, candidates, scoring, analysis, tests, 8-sample review recorder, chain, smoke and dry run (synthetic self-consistency)' > /tmp/pub51.log 2>&1 || { say STOP publish failed; exit 1; }
  git diff --quiet HEAD -- $FROZEN || { say STOP plan or frozen code differs from commit; exit 1; }; say COMMITTED $(git log --oneline -1 | cut -c1-7)
  scripts/timestamp_prereg.sh $P > /tmp/ts51.log 2>&1
  [ $(grep -c 'Verification: OK' /tmp/ts51.log) -ge 2 ] || { say STOP timestamp not verified; exit 1; }; say TIMESTAMPED
fi
ac "before recording"
.venv/bin/python agr/test_layertap_alignment.py > /tmp/align51a.log 2>&1 || { say STOP telemetry alignment test failed; exit 1; }
.venv/bin/python agr/test_hstap_alignment.py > /tmp/align51b.log 2>&1 || { say STOP hidden-state alignment test failed; exit 1; }; say ALIGNMENT_OK
for S in $SEEDS; do
  f=data/agr/episodes_LH_seed$S.jsonl
  if [ -f $f ] && [ "$(wc -l < $f | tr -d ' ')" = 600 ]; then continue; fi
  ac "before seed $S"
  .venv/bin/python agr/recorder.py 100 800 --layers --hs --seed=$S > /tmp/rec51_$S.log 2>&1 || { say "STOP recording seed $S failed"; exit 1; }
  say "SEED_${S}_RECORDED $(wc -l < $f | tr -d ' ') episodes"
done
say SELFCONS_START
for S in $SEEDS; do
  a=$(.venv/bin/python -c "import json; print(sum(1 for l in open('data/agr/episodes_LH_seed$S.jsonl') if json.loads(l)['answered']))")
  o=data/agr/selfcons_yb0051_seed$S.jsonl; n=$( [ -f $o ] && wc -l < $o | tr -d ' ' || echo 0)
  if [ "$a" != "$n" ]; then
    ac "before review of seed $S"
    .venv/bin/python agr/selfcons_yb0051.py --seed $S > /tmp/sc51_$S.log 2>&1 || { say "STOP self-consistency recorder failed on seed $S"; exit 1; }
    n=$(wc -l < $o | tr -d ' ')
  fi
  [ "$a" = "$n" ] || { say "STOP seed $S self-consistency incomplete: $n of $a"; exit 1; }; say "SEED_${S}_SELFCONS_COMPLETE $n of $a"
  cp $o $D/data/
done
.venv/bin/python - <<'PY' >> $L 2>&1 || { say STOP packing failed; exit 1; }
import json, gzip, os, numpy as np
D = 'algorithms/YB-0051-low-false-alarm-precision/data'
for S in [str(s) for s in range(27, 39)]:   # same packing as agr/yb0050_chain.sh (no shift)
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
SANDBOX_MEM=28g SANDBOX_TIMEOUT=14400 sandbox/run.sh $D confirmatory > /tmp/conf51.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/results.json ] || { say STOP confirmatory failed; exit 1; }; say CONFIRMATORY_OK
SANDBOX_MEM=28g ./publish.sh 'YB-0051 results, test-seed recordings 27-38 and 8-sample self-consistency' > /tmp/pub51r.log 2>&1 || { say STOP results publish failed; exit 1; }; say RESULTS_COMMITTED $(git log --oneline -1 | cut -c1-7)
scripts/make_public_snapshot.sh >> /tmp/pub51r.log 2>&1 && say PUBLIC_SNAPSHOT_OK || say PUBLIC_SNAPSHOT_FAILED
say DONE
