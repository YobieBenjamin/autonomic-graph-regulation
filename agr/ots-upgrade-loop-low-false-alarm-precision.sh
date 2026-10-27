#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Retry the OpenTimestamps upgrade for the EXPERIMENT-LOW-FALSE-ALARM-PRECISION plan until it carries a Bitcoin block-header attestation (up to 12 hours after it appears).
# EXPERIMENT-LOW-FALSE-ALARM-PRECISION: the paths below use its descriptive folder name (2026-10 rename, which retired the YB numbers)
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd "$(dirname "$0")/.."; L=/tmp/ots_upgrade51.log; f=algorithms/low-false-alarm-precision/docs/PREREGISTRATION.md.ots
until [ -s $f ]; do pgrep -f agr/low-false-alarm-precision-chain.sh > /dev/null || exit 0; sleep 300; done
for i in $(seq 1 48); do
  .venv/bin/ots upgrade $f > /dev/null 2>&1
  if .venv/bin/ots info $f 2>&1 | grep -qi BitcoinBlockHeaderAttestation; then echo "$(date -u +%H:%M) ANCHORED" >> $L; exit 0; fi
  echo "$(date -u +%H:%M) pending" >> $L; sleep 900
done
