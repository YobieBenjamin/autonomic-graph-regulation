#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Exit 0 once the Docker daemon answers; on macOS start Docker Desktop if needed (waits up to 90 s).
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
docker info >/dev/null 2>&1 && exit 0
[ "$(uname)" = Darwin ] && open -ga Docker
for _ in $(seq 45); do sleep 2; docker info >/dev/null 2>&1 && exit 0; done
echo "Docker daemon not available. Start Docker, or set MINER_SANDBOX=host / PUBLISH_SANDBOX=host (UNSAFE: runs model code on this machine)." >&2
exit 1
