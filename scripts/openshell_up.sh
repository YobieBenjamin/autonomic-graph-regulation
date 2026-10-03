#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# One command: bring up NVIDIA OpenShell on this Mac (see docs/OPENSHELL_SETUP.md). Self-validating; safe to re-run.
# Keeps Docker Desktop as the system default (the research sandbox never moves); only the OpenShell gateway uses Colima.
# Extra host ports to expose to sandboxes (e.g. a mock tool service): OPENSHELL_TUNNEL_PORTS="18080" scripts/openshell_up.sh
set -euo pipefail
export PATH=/opt/homebrew/bin:$HOME/.local/bin:/usr/local/bin:$PATH
BEFORE=$(docker context show)
[ "$BEFORE" = desktop-linux ] || echo "note: default Docker context is $BEFORE"
colima status >/dev/null 2>&1 || colima start --cpu 4 --memory 8 --disk 40 --vm-type vz
docker context use "$BEFORE" >/dev/null                       # Colima switches the default context; restore it
[ "$(docker context show)" = "$BEFORE" ] || { echo 'ABORT: could not restore the default Docker context'; exit 1; }
colima ssh -- grep -q landlock /sys/kernel/security/lsm || { echo 'ABORT: Colima kernel does not have Landlock'; exit 1; }
if ! grep -q colima "$HOME/.config/openshell/gateway.env" 2>/dev/null; then
  mkdir -p "$HOME/.config/openshell"
  printf '# OpenShell gateway only: use the Colima VM (kernel with Landlock). Docker Desktop stays the system default.\nexport DOCKER_HOST=unix://%s/.colima/default/docker.sock\n' "$HOME" > "$HOME/.config/openshell/gateway.env"
  brew services restart openshell >/dev/null; sleep 15
fi
colima ssh-config > "$HOME/.colima/ssh_config_agr"
for P in 17670 ${OPENSHELL_TUNNEL_PORTS:-}; do                   # reverse tunnels: VM loopback -> Mac loopback (nothing exposed to the network)
  # Guard: never tunnel a port with no listener on the Mac. Lima mirrors VM ports back to the Mac, so a tunnel without a host
  # listener creates a forwarding loop that destabilised the SSH connection carrying the gateway tunnel (2026-10-02).
  lsof -nP -iTCP:$P -sTCP:LISTEN 2>/dev/null | grep -v "^ssh " | grep -q LISTEN || { echo "ABORT: nothing listening on Mac port $P; start the service before its tunnel"; exit 1; }
  if ! colima ssh -- sh -c "ss -ltn | grep -q 127.0.0.1:$P"; then
    # one dedicated SSH connection per tunnel (not the shared Lima connection), so one failure cannot take down the others
    ssh -F "$HOME/.colima/ssh_config_agr" -o ControlMaster=no -o ControlPath=none -f -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -R "127.0.0.1:$P:127.0.0.1:$P" colima
  fi
  colima ssh -- sh -c "ss -ltn | grep -q 127.0.0.1:$P" || { echo "ABORT: tunnel for port $P not up"; exit 1; }
done
ST=$(openshell status 2>&1 || true)   # capture first: grep -q under pipefail would report a false failure (SIGPIPE)
printf '%s' "$ST" | grep -q 'Status: Connected' || { echo 'ABORT: OpenShell gateway not connected'; exit 1; }
openshell sandbox create --name agr-health --no-keep --no-tty --no-auto-providers --no-credential-warnings -- /bin/true >/tmp/openshell_health.log 2>&1 \
  || { echo 'ABORT: health sandbox failed (see /tmp/openshell_health.log)'; exit 1; }
echo "OK: OpenShell $(openshell --version | awk '{print $2}') ready on Colima $(colima version | head -1 | awk '{print $3}'); default Docker context: $(docker context show)"
