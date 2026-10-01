#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Publish only after the timing/power-sensitive recording has finished (never load the machine mid-recording).
cd "$(dirname "$0")/.."; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while pgrep -f 'agr/recorder.py' >/dev/null; do sleep 20; done
./publish.sh 'AGR results written up: YB-0015 (contamination), YB-0017 (HPA organism), YB-0009 (coupling graph) with theory, math, proofs, repeatable proof, plain English; ledger + backlog (YB-0019, YB-0020); YB-0018 power instrument' > /tmp/publish11.log 2>&1
echo "EXIT=$?" >> /tmp/publish11.log; git -C ~/safety pull -q >> /tmp/publish11.log 2>&1; echo DONE >> /tmp/publish11.log
