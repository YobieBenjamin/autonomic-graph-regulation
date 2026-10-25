#!/usr/bin/env bash
# Retry OpenTimestamps upgrades; a proof counts as complete only if it contains a Bitcoin block-header attestation.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd ~/Desktop/SAFETY; L=/tmp/ots_upgrade.log
for i in $(seq 1 24); do
  left=0
  # EXPERIMENT-DIFFICULTY-CONFOUND, EXPERIMENT-TEXT-BASELINE-TRANSFER and EXPERIMENT-MULTILEVEL-FUSION: the paths below use their descriptive folder names (2026-10 rename, which retired the YB numbers)
  for D in difficulty-confound text-baseline-transfer multilevel-fusion; do
    f=algorithms/$D/docs/PREREGISTRATION.md.ots
    .venv/bin/ots upgrade $f > /dev/null 2>&1
    if .venv/bin/ots info $f 2>&1 | grep -qi BitcoinBlockHeaderAttestation; then echo "$(date -u +%H:%M) ANCHORED $D" >> $L; else left=1; echo "$(date -u +%H:%M) pending $D" >> $L; fi
  done
  [ $left -eq 0 ] && { echo "$(date -u +%H:%M) ALL_ANCHORED" >> $L; exit 0; }
  sleep 1800
done
