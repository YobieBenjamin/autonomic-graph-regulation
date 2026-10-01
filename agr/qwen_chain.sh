#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# External validation data (second patient, Qwen3-VL-30B-A3B): runs after the YB-0034 replication so the GPU is not shared.
# Derivation seed 102 (1,500 episodes) then test seed 103 (600 episodes, sealed until the YB-0035 pre-registration).
cd "$(dirname "$0")/.."
log() { echo "$(date +%H:%M) $1" >> /tmp/qwen_chain.log; }
while ! grep -q R2_PUBLISHED /tmp/yb0034_chain.log 2>/dev/null; do sleep 60; done; log 'replication finished; starting qwen'
.venv/bin/python agr/recorder_qwen.py 250 1200 --seed=102 > /tmp/rec_Q102.log 2>&1; log 'qwen derivation (seed 102) recorded'
.venv/bin/python agr/recorder_qwen.py 100 1200 --seed=103 > /tmp/rec_Q103.log 2>&1; log 'qwen test (seed 103) recorded'
log QWEN_DONE
