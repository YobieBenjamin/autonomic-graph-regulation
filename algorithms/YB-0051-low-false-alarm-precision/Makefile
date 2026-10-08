# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
.PHONY: all build test experiment dryrun confirmatory smoke clean explore explore-smoke
export PYTHONPATH := .:src
all: test experiment
build: src/libcore.so
src/libcore.so: src/vitals.c src/hpa.c src/layergraph.c
	gcc -O2 -Wall -Wextra -Werror -shared -fPIC -o $@ $^ -lm
test: build
	python3 -m py_compile src/*.py explore/*.py
experiment: build
	@echo "YB-0051: no confirmatory experiment yet (exploratory stage)"
explore: build
	python3 explore/dump_scores.py
	python3 explore/levers.py
explore-smoke: build
	SMOKE=1 python3 explore/dump_scores.py
clean:
	rm -f src/libcore.so
