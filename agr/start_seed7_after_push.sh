#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# COMMITTED AFTER THE FACT (audit B20): this is the exact wrapper that launched agr/seed7_chain.sh on 2026-09-30.
# It waited until GitHub reported commit b6c795b (the YB-0035 protocol) as main, logged that, then ran the chain.
# The run-alone guard (agr/runguard.py) did not exist yet; no contention was logged in data/agr/contention_windows.txt.
cd ~/Desktop/SAFETY; export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
while [ "$(git ls-remote origin -h refs/heads/main | cut -c1-7)" != "b6c795b" ]; do sleep 30; done
echo "$(date +%H:%M) protocol b6c795b confirmed on GitHub; starting seed 7" >> /tmp/seed7_chain.log
exec agr/seed7_chain.sh
