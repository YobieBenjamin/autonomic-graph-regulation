#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Reproducibility audit: re-run every completed experiment from its committed data in the sandbox (results are rewritten
# in place), then report any difference from the committed results with git. Clean diff = reproducible.
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
OUT=archive/audit/repro_$(date +%F).txt
while ! grep -q R2_PUBLISHED /tmp/yb0034_chain.log 2>/dev/null; do sleep 60; done
git stash list >/dev/null; echo "Reproducibility audit started $(date -u +%FT%TZ) at commit $(git rev-parse --short HEAD)" > $OUT
for d in algorithms/YB-00*/; do
  n=$(basename $d); [ -f $d/docs/results.json ] || { echo "$n: no results.json (skipped)" >> $OUT; continue; }
  case $n in YB-0034*) echo "$n: skipped (in progress)" >> $OUT; continue;; esac
  t0=$(date +%s); SANDBOX_MEM=6g SANDBOX_TIMEOUT=7200 sandbox/run.sh $d all > /tmp/repro_$n.log 2>&1; rc=$?
  ch=$(git status --porcelain -- $d/docs | wc -l | tr -d ' ')
  echo "$n: exit $rc, $(( $(date +%s) - t0 )) s, changed result files: $ch" >> $OUT
  [ "$ch" != 0 ] && git diff --stat -- $d/docs >> $OUT && git diff -- $d/docs/results.json | head -40 >> $OUT
done
echo REPRO_DONE >> $OUT
