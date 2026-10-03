# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
.PHONY: test experiment all
test:
	python3 -m py_compile tools/*.py && echo "YB-0044: tools compile (live runs need OpenShell on the host; see docs/OPENSHELL_SETUP.md)"
experiment:
	python3 tools/analyze.py
all: test experiment
