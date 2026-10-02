# NVIDIA OpenShell on this Mac: setup, issues found, and safeguards (2026-10-01)

Purpose: run NVIDIA OpenShell (the agent sandbox and policy-enforcement runtime of the NVIDIA Open Agent Safety Platform) for
YB-0044, where an internal-state risk signal gates an agent's tool calls. One command brings it up: scripts/openshell_up.sh

## Environment
OpenShell 0.1.2 (Homebrew; local gateway as a launchd service), Colima 0.10.3 (VM type vz, 4 CPU, 8 GB), Colima kernel 6.8.0-117-generic,
Docker Desktop 28.3.2 (unchanged; remains the system default context, desktop-linux).

## What happened, in order
1. **Installer.** The PyPI package openshell is now NVIDIA's Python SDK and provides no CLI. The CLI and gateway come from
   NVIDIA's install script, which was downloaded and inspected before running (it fetches only from github.com/NVIDIA/OpenShell
   releases and Homebrew; no administrator rights on macOS).
2. **First sandbox failed: Landlock.** Docker Desktop's Linux VM kernel on macOS has no Landlock; OpenShell's supervisor checks
   for Landlock before starting a sandbox and refuses to run without it (older versions silently ran unrestricted, a reported
   security bug since fixed). Independently measured by Cisco DefenseClaw (issue 992) on Apple silicon, macOS 27, OpenShell 0.1.1.
3. **Fix: Colima.** A Linux VM whose Ubuntu kernel enables Landlock (verified: active LSMs include landlock).
4. **Safeguard: Docker context.** Colima switches the default Docker context to itself; it was switched back immediately and is
   verified on every run, so the research sandbox (all experiments and verification) never changed runtime.
5. **Safeguard: gateway only.** Only the OpenShell gateway uses Colima, via DOCKER_HOST in ~/.config/openshell/gateway.env.
6. **Second failure: callback.** The sandbox supervisor calls the gateway at 127.0.0.1 on its host network, which inside Colima
   is the VM, not the Mac (the same failure NVIDIA documented for WSL 2, issue 3880).
7. **Fix without exposure: reverse SSH tunnel.** VM 127.0.0.1:17670 is forwarded to the Mac's 127.0.0.1:17670 over Colima's SSH
   connection. The gateway stays loopback-only (mutual TLS); binding it to all interfaces was rejected because it would expose
   the gateway to the local network. Additional ports (a mock tool service) use the same mechanism (OPENSHELL_TUNNEL_PORTS).
8. **Setup-script bug found and fixed:** a status check using grep -q under pipefail reported a false failure (SIGPIPE); the
   output is now captured first and the check requires Status: Connected.
9. **Result:** sandboxes reach Ready; the setup script ends with a real health sandbox.

## Caveats
- The tunnel lives on Colima's SSH connection: after a restart of Colima or the Mac, re-run scripts/openshell_up.sh.
- Policy enforcement uses Landlock and seccomp inside Colima's VM, not Docker Desktop's; timings measured here include the
  tunnel and are specific to this setup.

## Policy schema used (NVIDIA reference: docs.nvidia.com/openshell/reference/policy-schema)
network_policies is a map of named rules: endpoints (host, port, protocol rest, enforcement enforce, rules with allow or deny
on method and path; deny takes precedence) and binaries (executable paths). Network policies are live: openshell policy set
NAME --policy FILE --wait replaces them on a running sandbox; openshell policy update merges incrementally.

## Sources
NVIDIA/OpenShell README and docs (install, policy schema, network rules, driver README); NVIDIA/OpenShell issues 664, 803,
1519, 3880 and PR 3924; cisco-ai-defense/defenseclaw issue 992. See also docs/sources/nvidia_open_agent_safety_platform.md.
