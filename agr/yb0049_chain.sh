#!/usr/bin/env bash
export PATH=/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH
cd ~/Desktop/SAFETY; D=algorithms/YB-0049-stage-diverse-layering; L=/tmp/chain49.log; P=$D/docs/PREREGISTRATION.md
say() { echo "[$(date -u +%H:%M:%S)] $*" >> $L; }
say START
if ls $D/docs/PREREGISTRATION.md.*.tsr >/dev/null 2>&1 && git diff --quiet HEAD -- $P agr/selfcons_yb0049.py; then say RESUME_AFTER_TIMESTAMP; else
SANDBOX_MEM=12g SANDBOX_TIMEOUT=1800 sandbox/run.sh $D test > /tmp/t49.log 2>&1 || { say STOP unit tests failed; exit 1; }; say TESTS_OK
SANDBOX_MEM=16g SANDBOX_TIMEOUT=3600 sandbox/run.sh $D smoke > /tmp/s49.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/smoke.json ] || { say STOP smoke failed; exit 1; }; say SMOKE_OK
SANDBOX_MEM=28g SANDBOX_TIMEOUT=10800 sandbox/run.sh $D dryrun > /tmp/d49.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/dryrun.json ] || { say STOP dry run failed; exit 1; }; say DRYRUN_OK
SANDBOX_MEM=28g ./publish.sh 'YB-0049 stage-diverse layering: pre-registration, stage-2 recorder (agr/selfcons_yb0049.py), analysis, tests, smoke and dry run (synthetic stage 2)' > /tmp/pub49.log 2>&1 || { say STOP publish failed; exit 1; }
git diff --quiet HEAD -- $P agr/selfcons_yb0049.py || { say STOP plan or recorder differs from commit; exit 1; }; say COMMITTED $(git log --oneline -1 | cut -c1-7)
scripts/timestamp_prereg.sh $P > /tmp/ts49.log 2>&1
[ $(grep -c 'Verification: OK' /tmp/ts49.log) -ge 2 ] || { say STOP timestamp not verified; exit 1; }; say TIMESTAMPED $(grep -o '[0-9][0-9]:[0-9][0-9]:[0-9][0-9] 2026' /tmp/ts49.log | head -1)
fi
say STAGE2_RECORDING_START
.venv/bin/python agr/selfcons_yb0049.py > /tmp/rec49.log 2>&1 || { say STOP stage-2 recorder failed; exit 1; }
for S in 9 13 14; do
  a=$(.venv/bin/python -c "import json; print(sum(1 for l in open('data/agr/episodes_LH_seed$S.jsonl') if json.loads(l)['answered']))")
  n=$(wc -l < data/agr/selfcons_yb0049_seed$S.jsonl | tr -d ' ')
  [ "$a" = "$n" ] || { say "STOP seed $S incomplete: $n of $a"; exit 1; }; say "SEED_${S}_COMPLETE $n of $a"
  cp data/agr/selfcons_yb0049_seed$S.jsonl $D/data/
done
SANDBOX_MEM=28g SANDBOX_TIMEOUT=10800 sandbox/run.sh $D confirmatory > /tmp/conf49.log 2>&1; [ $? -eq 0 ] && [ -s $D/docs/results.json ] || { say STOP confirmatory failed; exit 1; }; say CONFIRMATORY_OK
SANDBOX_MEM=28g ./publish.sh 'YB-0049 results and stage-2 recordings' > /tmp/pub49r.log 2>&1 || { say STOP results publish failed; exit 1; }; say RESULTS_COMMITTED $(git log --oneline -1 | cut -c1-7)
scripts/make_public_snapshot.sh >> /tmp/pub49r.log 2>&1 && say PUBLIC_SNAPSHOT_OK || say PUBLIC_SNAPSHOT_FAILED
say DONE
