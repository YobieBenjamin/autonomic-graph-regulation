#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Dedicated-machine chain: finish batch 1, extend to 480 episodes (same deterministic prefix), then analyze.
cd "$(dirname "$0")/.."
while pgrep -f 'agr/recorder.py' >/dev/null; do sleep 20; done
.venv/bin/python agr/recorder.py 80 800 >> /tmp/rec_full.log 2>&1
agr/after_recording.sh
