# YB-0050: a powered decider, and whether the regulator can scale

Pre-registered test (docs/PREREGISTRATION.md) on NEW test seeds 15 to 26, recorded after the plan is timestamped. It settles two close
calls from YB-0047 and YB-0049 with about four times the data, tests whether a stack with no language-model signal comes within 10 points
of the model's own self-consistency, and measures the two numbers that decide whether the regulator scales: cost per check as a share of
inference, and the false-alarm burden at realistic error base rates.

Position held by the author (design principle, not a tested claim): no AI is the judge, jury or arbiter of AI safety. The model's
disagreement with itself is used only as a signal measured by outside code; the decision to alarm, hold or block is made by non-LLM code
and, for irreversible acts, a human.

## Run
One command on the Mac: `agr/yb0050_start.sh` (waits for AC power; `--now` to skip). Progress: /tmp/chain50.log, copied to
agr/yb0050_chain_progress.log. Analysis targets: `make smoke`, `make dryrun`, `make confirmatory` (only after the public timestamp).

## Code
src/decider.py (alarm rules, one paired bootstrap for every comparison, burden arithmetic, operation counts; new), tests/experiment.py
(new), tests/test_decider.py (new). Every other file in src/ is a byte-identical copy of YB-0048 (layered.py of YB-0049); see
docs/src_hashes.txt. Recorders: agr/recorder.py (unchanged), agr/selfcons_yb0050.py (agr/selfcons_yb0049.py with only seeds and file
names changed).

## Data
Derivation: YB-0045 recordings, seeds 2 to 14, through hash-verified local hard links (not tracked; the record is
algorithms/YB-0045-powered-replication/data). Test: seeds 15 to 26 and their self-consistency reviews, packed into data/ by the chain
(tracked).

## Results (confirmatory; plan committed 64150a4, RFC 3161 timestamps 04:06:46 and 04:06:47 UTC 2026-10-06 (FreeTSA, DigiCert);
recording 04:30 to 12:02 UTC, self-consistency 12:02 UTC 2026-10-06 to 07:53 UTC 2026-10-07, analysis 07:54 to 08:08 UTC; docs/results.json)
Test: seeds 15 to 26, 7,200 episodes, 6,457 answered, 530 wrong (743 never answered; 2,315 answered before the first checkpoint).
- H1 NOT SUPPORTED: layered minus self-consistency alone -0.055 [-0.078, -0.032] (469 vs 498 of 530 at 10% false alarms). On this
  data the model's own self-disagreement carries the layered system; giving half the budget to the probe costs catches.
- H2 SUPPORTED: probe minus trained text +0.053 [+0.018, +0.089] (363 vs 335). Sensitivity with never-answered episodes counted as
  failures: -0.013 [-0.032, +0.012] (not supported), so the in-distribution advantage holds only for answered episodes.
- H3 NOT SUPPORTED: non-LLM stack minus self-consistency -0.260 [-0.301, -0.213] (360 vs 498), far outside the 0.10 margin. Excluding
  the model's self-disagreement costs about 26 points of recall at a 10% false-alarm budget on this data.
- H4 (cost, pooled wall-clock share of inference): difficulty 0.003%, probe 0.004%, text 0.02%, regulator 0.31%, non-LLM stack 0.34%
  (all pass the 1% bar); self-consistency 392%, layered 392%, gated layered 214% (fail). Analytic: probe 2.7e-7 of inference operations.
  The gate sent 61% of episodes to self-consistency and lost 12 points of recall versus the ungated layered rule.
- H5 (burden at a 1% error base rate): at a 10% false-alarm budget, precision is probe 6.5% (14 false alarms per true one), stack 6.4%,
  self-consistency 9.9%, layered 11.3%. At a 1% false-alarm budget: probe catches 30% at 23% precision (3.3 false per true), stack
  28% at 22%, layered 20% at 29%; self-consistency with 4 samples cannot operate at 1% (its smallest step alarms more than 1% of
  correct answers). At a 0.1% base rate every monitor is below 4% precision.
- Descriptive: AUROC self-consistency 0.966, stack 0.898, probe 0.892, text 0.885, regulator 0.876, difficulty 0.852. Self-consistency
  dominates on multiplication (137 vs probe 65 of 155) and letter counting (45 vs 9 of 52).

## Deviations
1. Battery stop: on 2026-10-06 the Mac was unplugged; the battery guard stopped the chain at 20:57 UTC (12%), but the self-consistency
   recorder ignored SIGINT inside MLX and kept running unsupervised. It was stopped cleanly by SIGTERM at about 21:46 UTC and the chain
   resumed at 21:46 UTC from the timestamped plan (RESUME_AFTER_TIMESTAMP; plan and recorders unchanged; the recorder resumes from
   complete records). The guard (agr/battery_guard_yb0050.sh) was patched to escalate SIGINT, then SIGTERM, then SIGKILL. Concurrent
   conditions during part of the run are recorded in the environment snapshots.
2. The automated results publish failed on a network timeout (HTTP 408) after the results commit 310c89a; the push was retried with a
   larger HTTP buffer. No analysis was re-run.
