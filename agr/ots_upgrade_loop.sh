#!/usr/bin/env bash
# Retry OpenTimestamps upgrades; a proof counts as complete only if it contains a Bitcoin block-header attestation.
cd ~/Desktop/SAFETY; L=/tmp/ots_upgrade.log
for i in $(seq 1 24); do
  left=0
  for D in YB-0046-difficulty-confound YB-0047-text-baseline-transfer YB-0048-multilevel-fusion; do
    f=algorithms/$D/docs/PREREGISTRATION.md.ots
    .venv/bin/ots upgrade $f > /dev/null 2>&1
    if .venv/bin/ots info $f 2>&1 | grep -qi BitcoinBlockHeaderAttestation; then echo "$(date -u +%H:%M) ANCHORED $D" >> $L; else left=1; echo "$(date -u +%H:%M) pending $D" >> $L; fi
  done
  [ $left -eq 0 ] && { echo "$(date -u +%H:%M) ALL_ANCHORED" >> $L; exit 0; }
  sleep 1800
done
