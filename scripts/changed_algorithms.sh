#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Lists algorithm folders whose code, tests, data or Makefile changed relative to BASE (default: origin/main),
# including uncommitted and untracked files. Used identically by publish.sh (local) and CI, so both verify the same set.
cd "$(dirname "$0")/.."; BASE="${1:-origin/main}"
if ! git rev-parse -q --verify "$BASE^{commit}" >/dev/null 2>&1; then ls -d algorithms/*/ | sed 's#/$##'; exit 0; fi   # unknown base: all
{ git diff --name-only "$BASE" -- algorithms; git ls-files --others --exclude-standard algorithms; } \
  | grep -E '^algorithms/[^/]+/(src/|tests/|data/|Makefile$)' | cut -d/ -f1-2 | sort -u
