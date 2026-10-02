# AI Safety Algorithm Mine

Net-new AI safety algorithms derived from graph theory, brain science and biological behavior, grounded in *Garbage In, Gospel Out*. Every entry is **coded, compiled, tested against baselines, and documented four ways**: plain English, technical, mathematical, and code. Negative results are kept in the ledger, because a failed hypothesis is information that stops the next run from re-mining it.

```bash
make all                     # compile + test + evaluate every algorithm
./publish.sh                 # verify, commit, push to github.com/YobieBenjamin/safety
python3 miner/mine.py        # agents mine the backlog, then propose new hypotheses, within a token budget
python3 miner/test_miner.py  # offline end-to-end miner test against a mock API (no tokens)
```

| Path | Purpose |
|---|---|
| `algorithms/YB-XXXX-*/` | One self-contained algorithm: `src/` (C core + Python), `tests/`, `docs/results.json`, `README.md` |
| `LEDGER.md` | Every attempt and its result, including failures |
| `HYPOTHESES.md` | Backlog the miner draws from; add ideas here |
| `miner/mine.py` | Orchestrator: claim → generate → compile/test in sandbox → repair loop → promote or record failure |
| `.github/workflows/ci.yml` | Re-verifies every algorithm on each push |

**Miner settings:** `ANTHROPIC_API_KEY` (required), `MINER_DAILY_TOKENS` (default 2,000,000), `MINER_WORKERS` (3), `MINER_MODEL`, `MINER_REPAIRS` (2), `MINER_PUBLISH=1` to auto-push each success. Requires Docker (auto-started on macOS).

## Security model

Model-written code is untrusted. It is compiled and executed **only** inside `sandbox/run.sh`: a Docker container with no network, no Linux capabilities, no privilege escalation, a non-root user, a read-only root filesystem, 3 GB memory / 4 CPU / 256-process caps, and a wall-clock timeout. It sees only the one directory under test. The orchestrator (which holds `ANTHROPIC_API_KEY` and GitHub credentials) runs on the host and never executes generated code; secrets never enter the container. `publish.sh` also verifies inside the sandbox, from a read-only copy, before anything is pushed, and aborts if Docker is unavailable or any test fails. Both fail closed: running on the host requires an explicit `MINER_SANDBOX=host` / `PUBLISH_SANDBOX=host`.

Validated by an adversarial probe (network egress, DNS, writes outside scope, host file access, Docker socket, root escalation, secret leakage, runaway process): all blocked. Results reproduce bit-for-bit between macOS and the Linux sandbox.

## Recursive mining on GitHub

`.github/workflows/mine.yml` runs the miner daily (and on demand from the Actions tab) using the repo secret `ANTHROPIC_API_KEY`. When the backlog is empty it proposes new hypotheses from the ledger, capped per run (`MINER_MAX_NEW`). Token efficiency: 1-hour prompt caching of the spec + reference implementation, a cheap-model triage gate before any expensive build, patch-only repairs, trimmed error logs, and price-weighted budget accounting with a hard daily stop.

## Hybrid orchestrator (local-first)

`./mine` brings up the Docker sandbox and the local LLM (LM Studio, gpt-oss-120b) and runs `orchestrator/orchestrate.py`, which routes each stage to the cheapest capable resource: design and review to cloud Claude; the math-heavy C core and algorithm module to cloud Claude when available; tests, experiment harness, repairs and first-draft docs to the local model; all builds and experiments to local sandboxes (8 in parallel). A free static quality gate (duplicate definitions, stub/placeholder markers, `main()` in the C core) runs before every test. Works local-only with no API key, but then nothing is cloud-reviewed. Key from `ANTHROPIC_API_KEY` or macOS Keychain (`anthropic-api-key`). Knobs: `LOCAL_ONLY`, `CLOUD_MODEL`, `CLOUD_DAILY_TOKENS`, `HYP_CONCURRENCY`, `SANDBOX_CONCURRENCY`, `MAX_LOCAL_REPAIRS`, `PUBLISH`, `RESUME`. Logs: `orchestrator/runs/`.

Measured on the M4 Max (128 GB): gpt-oss-120b 66 tok/s single stream, 93 tok/s at 4 concurrent. First local-only attempt at YB-0003 generated design and all code for 0 cloud tokens but failed verification: the local model hallucinated an API, stubbed a function, and mis-derived a closed form (Gini of one active unit among n is (n-1)/n). Hence the quality gate and the cloud routing for core math.

## Migrating to a new machine

`gh repo clone YobieBenjamin/safety && cd safety && ./bootstrap.sh` (add `--models` to download the local LLM). It
installs the pinned environment, checks Docker, LM Studio and credentials, and validates by building and testing every
algorithm in the sandbox. Reference values: `docs/MACHINE_SETUP.md`. Full decision history: `docs/PROJECT_HISTORY.md`.
Session artifacts (run logs, raw model outputs, failed attempts): `archive/` (refresh with `scripts/archive_session.sh`).

## License

Source-available, not open source. Copyright (c) 2026 Yobie Benjamin. Software is licensed under the PolyForm Noncommercial License 1.0.0 ([LICENSE.md](LICENSE.md)); documentation, data and figures under CC BY-NC 4.0 ([LICENSE-DOCS.txt](LICENSE-DOCS.txt)). Attribution is required for any use in whole or in part ([NOTICE](NOTICE)); commercial use requires a separate license. See [LICENSING.md](LICENSING.md) for scope and contact, and [CITATION.cff](CITATION.cff) to cite this work.

## Authorship and AI assistance

Yobie Benjamin conceived and directed this research: the biological thesis, the research program, the hypotheses and the standards for what counts as a result. The code, experiments, analyses and drafts are by Yobie Benjamin and AI: Anthropic's Claude (via a Claude subscription, including Claude Code sessions) as research assistant and orchestrator, and a locally run open model (gpt-oss-120b) for some code generation. The six audits recorded in archive/audit/ were fresh, read-only Claude sessions, separate from the authoring session; the later audits could read the earlier findings. They are independent of the authoring session but not of the AI system, and no human expert review has yet been performed. Every correction is logged in CORRECTIONS.md.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
