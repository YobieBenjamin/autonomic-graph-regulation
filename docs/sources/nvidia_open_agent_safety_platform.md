# Source record: NVIDIA Open Agent Safety Platform (retrieved 2026-10-01)

Facts relied on in this project's documents, each attributed to NVIDIA or to the named outlet. Not independently verified.

| Fact (as described by the source) | Source |
|---|---|
| The platform combines the open-source OpenShell runtime (on NVIDIA Vera CPUs) with NVIDIA Sentry on BlueField-4 DPUs. | NVIDIA Developer Blog, https://developer.nvidia.com/blog/nvidia-open-agent-safety-platform-a-reference-for-continuous-in-silicon-agent-monitoring/ |
| In a Vera Rubin POD, BlueField-4 sits on the node's only path to the model and provides out-of-band observability and policy enforcement. | Same |
| Sentry provides out-of-band, in-silicon telemetry of agent activity and policy enforcement, and can quarantine agents in milliseconds (vendor claim). | NVIDIA, https://www.nvidia.com/en-us/solutions/ai/agent-safety/ |
| OpenShell enforces policy outside the agent process, sandboxes agents, filters system calls, and provides an audit trail of allow and deny decisions; Apache 2.0 open source. | NVIDIA, https://www.nvidia.com/en-us/ai/openshell/ ; https://flowtivity.ai/blog/nvidia-open-agent-safety-platform/ (license) |
| Announced by Jensen Huang with more than 100 industry partners (announced 2026-09-28). | https://shattered.io/nvidia-ai-agent-safety-platform-100-partners-2026/ ; https://kingy.ai/blog/nvidia-open-agent-safety-platform-openshell-sentry/ |
| OpenShell version 0.1.0; policies in YAML compiled to OPA Rego. | ServeTheHome, https://www.servethehome.com/nvidia-open-agent-safety-platform-launched/ |

This project's characterization (that the platform governs agent actions against policy and, as described, does not observe
model-internal state) is our reading of these descriptions, not a statement by NVIDIA.
