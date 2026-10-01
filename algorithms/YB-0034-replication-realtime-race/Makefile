# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
.PHONY: all build test experiment clean
export PYTHONPATH := .:src
all: test experiment
build: src/libcore.so
src/libcore.so: src/vitals.c src/hpa.c src/layergraph.c
	gcc -O2 -Wall -Wextra -Werror -shared -fPIC -o $@ $^ -lm
test: build
	python3 -m py_compile src/*.py tests/*.py
	python3 tests/test_core.py
experiment: build
	python3 tests/experiment.py
clean:
	rm -f src/libcore.so

robust: build
	python3 tests/exploratory_equal_fpr.py
