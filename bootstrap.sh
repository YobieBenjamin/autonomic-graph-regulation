#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# One command to make a fresh clone fully operational on an Apple-silicon Mac, then prove it works.
#   ./bootstrap.sh            set up + self-validate (no large downloads)
#   ./bootstrap.sh --models   also download the local LLM (gpt-oss-120b, ~63 GB) via LM Studio
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.lmstudio/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
ok() { printf '  [ok]   %s\n' "$1"; }; todo() { printf '  [todo] %s\n' "$1"; TODO=1; }; TODO=0
echo '== Tools'
for t in git python3 make gcc; do command -v $t >/dev/null && ok $t || { echo "missing $t: install Xcode Command Line Tools"; exit 1; }; done
command -v gh >/dev/null && ok gh || { command -v brew >/dev/null && brew install gh >/dev/null && ok 'gh (installed)'; } || todo 'brew install gh'
echo '== Python environment (.venv, pinned in requirements.txt)'
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q -r requirements.txt && .venv/bin/python -c 'import numpy, scipy, sklearn' && ok 'numpy / scipy / scikit-learn' || todo 'pip install -r requirements.txt failed'
echo '== Docker sandbox'
if sandbox/ensure_docker.sh; then ok "docker: $(docker info --format '{{.NCPU}} CPUs, {{.MemTotal}} bytes RAM')"; else todo 'install and start Docker Desktop; recommended 32 GB RAM, 12 CPUs'; fi
echo '== Local LLM (LM Studio)'
if command -v lms >/dev/null; then
  if lms ls 2>/dev/null | grep -q gpt-oss-120b; then ok 'gpt-oss-120b present'
  elif [ "${1:-}" = --models ]; then lms get openai/gpt-oss-120b -y >/dev/null && ok 'gpt-oss-120b downloaded'
  else todo 'model missing: ./bootstrap.sh --models  (63 GB)'; fi
else todo 'install LM Studio (lmstudio.ai), open it once, rerun'; fi
echo '== Credentials (never stored in this repo)'
gh auth status >/dev/null 2>&1 && ok 'gh logged in' || todo 'gh auth login  (as the repo owner account)'
security find-generic-password -s anthropic-api-key >/dev/null 2>&1 && ok 'Anthropic API key in Keychain' || todo 'optional cloud tier: security add-generic-password -a "$USER" -s anthropic-api-key -w'
echo '== Self-validation: build + test every algorithm inside the sandbox'
if docker info >/dev/null 2>&1 && sandbox/run.sh . test --ro > /tmp/bootstrap_test.log 2>&1; then ok "$(grep -c 'tests passed' /tmp/bootstrap_test.log) algorithm test suites pass"
else todo 'sandbox tests did not pass: see /tmp/bootstrap_test.log'; fi
[ $TODO = 0 ] && echo 'READY: ./mine to start mining' || echo 'Finish the [todo] items above, then rerun ./bootstrap.sh'
