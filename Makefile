# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
.PHONY: test all verify
# Builds and tests every algorithm; fails if any fails.
test:
	@set -e; for d in algorithms/*/; do echo "== $$d"; $(MAKE) -C $$d test; done
all:
	@set -e; for d in algorithms/*/; do echo "== $$d"; $(MAKE) -C $$d all; done

# Same check locally and in CI: every test, plus the full experiment of each algorithm listed in .verify_changed
# (written by scripts/changed_algorithms.sh: algorithms whose code, tests, data or Makefile changed).
verify:
	@set -e; for d in algorithms/*/; do echo "== test $$d"; $(MAKE) -C $$d test; done; \
	if [ -s .verify_changed ]; then for d in $$(cat .verify_changed); do echo "== experiment $$d"; $(MAKE) -C $$d experiment; done; \
	else echo "== no algorithm code or data changed: experiments skipped"; fi
