#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Run a make target on algorithm code inside the locked-down sandbox container.
#   sandbox/run.sh <dir> <target>        dir mounted read-write at /work (miner: keeps docs/results.json)
#   sandbox/run.sh <dir> <target> --ro  dir mounted read-only, copied to tmpfs, built there (publish check)
# Lockdown: no network, no capabilities, no privilege escalation, non-root, read-only root fs,
# memory/CPU/process caps, wall-clock timeout. Only <dir> is visible; no host secrets enter.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dir="$(cd "$1" && pwd)"; target="${2:-test}"; mode="${3:-}"
tag="safety-sandbox:$(shasum -a 256 "$here/Dockerfile" | cut -c1-12)"
docker image inspect "$tag" >/dev/null 2>&1 || docker build -q -t "$tag" "$here" >/dev/null
cpus="${SANDBOX_CPUS:-4}"; avail="$(docker info --format '{{.NCPU}}' 2>/dev/null || echo 1)"
[ "$avail" -lt "$cpus" ] && cpus="$avail"            # never request more CPUs than the host has (CI runners: 2)
uid="$(id -u)"; gid="$(id -g)"                 # match caller so mounted dirs are writable on Linux too
[ "$uid" = 0 ] && { uid=10001; gid=10001; }   # never run as root inside the sandbox
lock=(--rm --network none --cap-drop ALL --security-opt no-new-privileges --user "$uid:$gid"
      --read-only --tmpfs /tmp:rw,exec,size=${SANDBOX_TMPFS:-2g} --memory "${SANDBOX_MEM:-3g}" --cpus "$cpus"
      --pids-limit 256)
tmo="${SANDBOX_TIMEOUT:-1500}"
if [ "$mode" = --ro ]; then
  exec docker run "${lock[@]}" -v "$dir":/src:ro "$tag" \
    sh -c "mkdir /tmp/w && tar -C /src --exclude=./.venv --exclude=./.git --exclude=./data/agr --exclude='*.so' --exclude=__pycache__ -cf - . | tar -C /tmp/w -xf - && cd /tmp/w && timeout $tmo make $target"
else
  exec docker run "${lock[@]}" -v "$dir":/work "$tag" timeout "$tmo" make "$target"
fi
