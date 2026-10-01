#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Re-record training (seed 0, 480) and held-out (seed 1, 240) episodes with 24-layer telemetry. Same questions and,
# with greedy decoding, the same tokens and answers as before (verified on a smoke test).
cd "$(dirname "$0")/.."
.venv/bin/python agr/recorder.py 80 800 --layers > /tmp/rec_L0.log 2>&1
.venv/bin/python agr/recorder.py 40 800 --layers --seed=1 > /tmp/rec_L1.log 2>&1
echo DEEP_RECORDING_DONE > /tmp/deep_chain.log
