# Project history and decisions

A one-person AI-safety research program run like mining: many hypotheses tried, each one coded in C + Python,
compiled, tested against baselines, and documented four ways (plain English, technical, mathematical, code).
Foundations: the book *Garbage In, Gospel Out*, graph theory, brain science and biological behavior.
Every attempt is kept, including failures (see LEDGER.md and archive/).

## 2026-09-28

1. **Charter and first block (YB-0001).** Built in a cloud container: per-input effective-connectivity graph +
   normalized-Laplacian heat trace as an OOD/adversarial monitor, plus a homeostatic baseline with a drift budget.
   Spectral detector: negative result (AUROC 0.64-0.78, below MSP/energy/Mahalanobis). Drift budget: positive
   (5/5 slow poisoning caught, 0/5 false alarms).
2. **Repository.** Private permanent repo YobieBenjamin/safety. First upload through the browser with SHA-256
   verification of every file; GitHub rejects dotfiles and `.github/` via the uploader, so those used the editor.
3. **YB-0002 Bounded Homeostatic Wrapper.** Proved confinement theorems T1-T3; worst-case attacker drags an
   unbounded monitor 768-5954 Mahalanobis units with zero flags, BHW caps it at B + eta*tau. Energy + BHW:
   detection 1.1% -> 43% with 0/10 false alarms. Closed-form budget calibration (C1/C2) fails in 64-D -> YB-0007.
4. **Moved to the Mac.** gh CLI logged in as YobieBenjamin alongside an existing account; clone at ~/safety with
   .venv; macOS 27 SDK linker quirk found and auto-handled; results reproduce bit-for-bit across the cloud
   container, macOS, and the Linux sandbox.
5. **Security sandbox.** All model-written code runs only in a locked-down Docker container (no network, no
   capabilities, non-root, read-only root, CPU/memory/process caps, timeout). Adversarial probe: every escape
   blocked, planted fake secrets never reached it. Miner and publish.sh fail closed. Found and fixed: an
   `a && b` under `set -e` that could have skipped verification; Mac-built .so files leaking into Linux builds.
6. **Parallel session.** Another Claude session in the same working tree added Miner v2 (prompt caching,
   cheap-model triage), a GitHub-hosted scheduled miner (`.github/workflows/mine.yml`, inert until an
   ANTHROPIC_API_KEY repo secret exists), and CI fixes for Linux runners (caller uid, CPU clamp). History stayed
   linear; nothing was overwritten.
7. **Local-first hybrid orchestrator (`./mine`).** Docker raised to 32 GB / 12 CPUs; LM Studio gpt-oss-120b as the
   local model. First fully local attempt at YB-0003 (0 cloud tokens) failed verification: the local model
   wrote a good design and all files but hallucinated an API, left a placeholder stub overriding a real function,
   and mis-derived its own closed form (Gini of one active unit among n is (n-1)/n, not (n-1)/(2n-1)).
   Fixes: one file per call, fixed Makefile template, README written after real results, real mlp.py source in
   every prompt, broader repair scope, resume mode, a free static quality gate, and cloud routing for the
   math-heavy C core and algorithm module. Also fixed an orchestrator bug that truncated HYPOTHESES.md.
8. **Complete archive for migration.** archive/2026-09-28 (run logs, raw model outputs, failed attempts,
   benchmarks), requirements.txt, bootstrap.sh, docs/MACHINE_SETUP.md, this file. Full clone at ~/Desktop/SAFETY.

9. **Book and thesis.** The book (89.5k words) converted to Markdown with a dependency-free converter and summarized by
   the local model; it establishes transformers as statistical machines and contains no biological regulation theory,
   so the AGR program is new work built on it. Research program written (docs/RESEARCH_PROGRAM.md): internal vital
   signs, autonomic regulation, instinct and judgment, represented as graphs.
10. **Budget reality.** Only the Max subscription: paid API disabled; Claude Code (subscription, long-lived OAuth
   token, 97% prompt-overhead cut to ~425 tokens per review) used only as a capped 1-6 am review gate. Found and fixed
   a token-capture bug that appended the next Terminal word to valid tokens.
11. **Independence Principle.** The safety organism must be external, non-transformer and text-blind (cannot be
   jailbroken); signals ranked by contamination (physical < consequence < substrate < words). Patient model
   gpt-oss-20b (MLX) instrumented by a trusted recorder; YB-0015 contamination test and YB-0017 HPA-axis organism
   built with pre-registered predictions (including the author's: organism and raw signals trend together, rho > 0.7).

12. **Metabolic vitals (YB-0018): negative.** GPU power and timing carry no failure signal; transformers do fixed compute per token and have no metabolism. Hardware implication: the biobrain needs an activation/logit telemetry port. Organism cost 290 ns per token (28,000x real-time headroom).
13. **Flagship (YB-0012), pre-registered.** On held-out questions, self-consistency (0.98) and an LLM judge (0.89) beat the organism (0.72); verdict inferior on accuracy. Confirmed: output confidence is inverted (0.39, the gospel premise) and the organism warns 4.5 s before the answer. The organism catches struggle errors (10 of 12) but no silent slips (0 of 9).
14. **Deep 24-layer organism (YB-0019), pre-registered.** 0.765 vs 0.720 (not significant); first silent slips caught; no longer distinguishable from the judge; still behind self-consistency.
15. **Real-time race (YB-0023), pre-registered.** The pre-registered rule declared an organism win but did not control false alarms (organism alarmed on 66% of correct answers): recorded as a flaw. Exploratory, matched 10% false alarms: deep organism caught 11 of 21 in time vs 6 for the judge (CI includes 0) at about 700x less compute.
16. **Author's architecture and model of judgment.** Custom brain-optimized chip external to the AI accelerator; dynamic hybrid of a coupled physiological link (A) and a parallel appraisal (B); non-deterministic; decisions as hundreds to thousands of dynamically weighted signals forming a graded hunch (YB-0027 hunch field, YB-0028 critical slowing down, YB-0029 hybrid).
17. **AI Early Warning Score (AI-EWS).** Author's principle: judgment has no analog but the brain and biology; safety follows hospital early-warning systems (NEWS2). Methodology in docs/AI_EWS_METHODOLOGY.md. YB-0030 (pre-registered): transparent 7-vital score predicts failures (0.725), levels perfectly ordered (5.8% / 11.8% / 75% / 100% failure rate), on par with the black box.
18. **Operations.** CI failures traced to a legacy miner self-test coupled to the live backlog; fixture isolated. Full logs archived from /tmp (wiped on reboot).

19. **Confirmatory deep program (YB-0031), pre-registered, fresh test set.** No eureka: in-time alarms inferior to the LLM judge (the YB-0023 lead did not replicate). But with 9x more data the organism reached 0.89 (tied with a 6x larger judge), caught 60% of silent slips, and failure to settle was confirmed (p = 0.0007).

20. **Serial-observation organism (YB-0032).** Pre-registered eureka flag came back true (29/46 in time vs judge 9/46), but a post-hoc control showed the fractional checkpoints leak total reasoning length (length alone: 15/46). Not accepted. Serial training genuinely moves accuracy earlier (0.41 to 0.79 AUROC at 25%). Next: YB-0033 with absolute-time checkpoints and a length control.

21. **EUREKA: YB-0033, clean real-time race.** Pre-registered (300f037), fresh test set, no future information, compute time counted, false alarms matched and then exactly equalized: the text-blind organism caught 28/44 wrong answers before they were emitted vs 13 for a 6x larger LLM judge and 17 for a length-only control. First leak-free, pre-registered result where reading the transformer's physiology beats watching its behavior. Limits: one model, one task family, 44 errors. Next: replication and external validation on a different model.

22. **Replication (YB-0034).** Frozen replication on fresh seed 6: 24/43 in time vs judge 13 and length 11 (R1, R2 hold; R3 missing, completed in YB-0035).
23. **Independent audit and deep debug.** A separate read-only Claude Code session audited the repository blind: 38 findings (3 critical). All critical findings were verified independently (telemetry one token late, F4; earliness claims were false-alarm artifacts, F1/F2; the YB-0015 reasoning-trace claim was never tested, F3). Our own finding S1: greedy generation is deterministic within a session but can diverge across sessions under GPU sharing. Everything is logged in CORRECTIONS.md; affected reports carry correction banners.
24. **Corrected confirmation (YB-0035).** Fixed instruments and statistics, code frozen before new data: the regulator beats the LLM judge and the length control on fresh seed 7 (23/40 vs 11 and 9) and pooled over seeds 5-7 (+32 points vs each). Boundary: not better than length when never-answered episodes count as failures. Vocabulary standardized (docs/GLOSSARY.md; regulator = organism, monitored model = patient, telemetry synchronization = tap alignment).

25. **Second audit (YB-0035 and blog drafts).** No leakage found; 25 findings on interpretation (2 critical: the win holds only before the answer exists, offline the judge is better; YB-0035 never measured confidence). Artifact gaps closed with committed scripts; exploratory fairness checks: equal monitorable false alarms 19 vs 11 (+0.20 [+0.02, +0.43]), frozen threshold 22/40, question-type baseline 6/40.

## Open items
- Anthropic API key in Keychain, then a supervised pilot (`./mine --max 1`) to measure real cloud-token cost per algorithm.
- Decide the single miner of record: local orchestrator (`./mine`) vs GitHub `mine.yml`; running both would compete for hypotheses.
- Ingest the book so hypotheses derive from its chapters (not yet provided).
- Open hypotheses: YB-0003 to YB-0007. Novelty claims still need a systematic literature search.

## Lessons
- Keep negative results; they redirect the search (YB-0001 -> YB-0002 -> YB-0007).
- Local models: strong at design prose and mechanical fixes, unreliable at novel math code; never let a model verify its own theorems.
- Deterministic scaffolding (templates, static gates, sandbox) beats more model calls.
- Fail closed everywhere; test the failure path, not just the success path.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
