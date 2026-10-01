.PHONY: all build test experiment clean
all: test experiment
build: src/libcore.so
src/libcore.so: src/core.c
	gcc -O2 -Wall -Wextra -Werror -shared -fPIC -o $@ $< -lm
export PYTHONPATH := .:src
test: build
	python3 -m py_compile src/*.py tests/*.py
	python3 tests/test_core.py
experiment: build
	mkdir -p docs
	python3 tests/experiment.py
clean:
	rm -f src/libcore.so
