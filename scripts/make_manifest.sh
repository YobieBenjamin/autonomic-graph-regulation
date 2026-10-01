#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Writes MANIFEST.sha256: the SHA-256 fingerprint of every tracked file (except the manifest itself), so anyone can verify
# exactly what was published. Verify with: shasum -a 256 -c MANIFEST.sha256
cd "$(dirname "$0")/.."
git ls-files | grep -v '^MANIFEST.sha256$' | sort | while read -r f; do shasum -a 256 "$f"; done > MANIFEST.sha256
echo "MANIFEST.sha256: $(wc -l < MANIFEST.sha256 | tr -d ' ') files"
