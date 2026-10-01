# Machine setup (reference machine, 2026-09-28)

Everything here is reproduced by `./bootstrap.sh` on a new Mac; this file records the exact values that were validated.

## Hardware and OS
- Apple M4 Max: 16 cores (12 performance + 4 efficiency), 128 GB unified memory, 1 TB free disk
- macOS 27.0 (build 26A428), Xcode + Command Line Tools installed

## Python
- Project-only virtual environment `.venv` (never committed), pinned by `requirements.txt`:
  numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1

## Docker Desktop (sandbox for all model-written code)
- Docker 28.3.2 / Desktop 4.44.2, linux/aarch64
- Resources raised from the 8 GB default to **32 GB RAM, 12 CPUs** so 8 sandboxes run in parallel.
  Set in `~/Library/Group Containers/group.com.docker/settings-store.json` (`MemoryMiB: 32768`, `Cpus: 12`);
  the original was backed up next to it as `settings-store.json.bak-<timestamp>`. Changing it needs a full
  Docker quit + relaunch (a soft restart hung the VM once).
- Sandbox image `safety-sandbox:<sha of sandbox/Dockerfile>` is built automatically on first use.

## Local LLM (LM Studio)
- LM Studio with CLI `~/.lmstudio/bin/lms`; OpenAI-compatible server on `http://localhost:1234/v1`
- Resident model: `openai/gpt-oss-120b` (63 GB), loaded as identifier `local-strong`, context 65536, full GPU offload.
  `./mine` starts the server and loads it automatically.
- Also downloaded: gpt-oss-20b (unloaded: same speed as 120b, weaker), qwen3-vl-30b, nomic-embed-text-v1.5
- Measured: 66 tok/s single stream, 93 tok/s aggregate at 4 concurrent requests (so LOCAL_CONCURRENCY=3)

## Known quirk: macOS 27 SDK
The default Command Line Tools SDK (MacOSX27.0.sdk) cannot be read by the linker (`libSystem.B.tbd: unknown
architecture`). Host builds therefore probe and pick the Xcode SDK automatically (publish.sh, miner). Sandbox builds
run on Linux and are unaffected.

## Accounts
- GitHub: repo owner account **YobieBenjamin** (gh CLI can hold several accounts; this one must be active)
- API keys live only in macOS Keychain (`anthropic-api-key`) or environment variables, never in the repo.
- Other personal account identifiers are intentionally not recorded in this repository.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
