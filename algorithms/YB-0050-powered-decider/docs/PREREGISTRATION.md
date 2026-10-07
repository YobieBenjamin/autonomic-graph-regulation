# YB-0050 pre-registration (DRAFT): a powered decider, and whether the regulator can scale

Status: DRAFT, 2026-10-05. Not committed, not timestamped. Becomes binding only when committed and timestamped with
scripts/timestamp_prereg.sh BEFORE any test-seed recording starts (PROTOCOL rules 1, 13, 16).

## Why
YB-0045 to YB-0049 left two close calls and two unmeasured scaling questions.
- Close call A (YB-0047): the hidden-state probe was not shown to beat a trained reader of the reasoning text (+0.072 [0.000, +0.153]).
- Close call B (YB-0049, descriptive): self-consistency alone caught 124 of 138, the layered system 123. Layering was never tested against
  self-consistency alone.
- Scaling: the regulator's cost per check relative to inference, and its false-alarm burden at realistic error base rates, have not been
  measured. At planet scale these, not throughput, decide whether it can work.

Position held by the author (design principle, not a tested claim): no AI is the judge, jury or arbiter of AI safety. The model's
disagreement with itself may be used only as a signal measured by outside, non-LLM code (theory P1, refined after YB-0049). The decision to
alarm, hold or block is always made by non-LLM code and, for irreversible acts, a human. This test measures what each signal is worth and
what it costs. It can fail.

## Data
- NEW test seeds 15 to 26 (12 seeds), recorded after this plan is timestamped: agr/recorder.py 100 800 --layers --hs, the YB-0045
  generation settings unchanged (gpt-oss-20b). Expected, from YB-0045 rates: about 6,400 answered episodes and about 550 wrong answers
  (about 4x YB-0045). The recording chain records actual counts; no seed is added or dropped after the timestamp.
- Self-consistency on every answered test episode: the YB-0049 method verbatim (agr/selfcons_yb0049.py, extended only to accept seeds 15
  to 26): 4 samples, temperature 0.8, reasoning effort low, at most 800 tokens; d = share of samples disagreeing with the original answer.
  Wall-clock per review recorded. Known limitation: MLX sampling is not bit-reproducible across runs (the recorder smoke on derivation
  seed 2 reproduced 2 of 3 YB-0049 smoke reviews exactly; the third differed in one of four samples), so the recorded reviews are the record.
- Derivation (all fitting, layer and C selection, normalisation statistics, band cut-points): YB-0045 derivation seeds plus the former
  test seeds 9, 13, 14 (PROTOCOL rule 2: once analysed, test seeds become derivation data).
- Population: all answered test episodes, defined exactly as in YB-0045 to YB-0049; never-answered episodes counted as failures as the
  pre-declared sensitivity analysis (PROTOCOL rule 5), for the comparisons without self-consistency (H2, and stack minus probe), since
  self-consistency is defined only for answered episodes.

## Monitors (code reused byte-identical where possible; hashes in docs/src_hashes.txt)
- Probe: YB-0045 hidden-state probe, in-time score over checkpoints {48, 96, 192, 384}.
- Text: YB-0047 trained text-prefix monitor (src/textmon.py).
- Difficulty: YB-0046 question-difficulty baseline (src/difficulty.py); length and question-type controls as in YB-0045.
- Non-LLM stack: the YB-0048 learned stack of difficulty, text, probe and regulator, refit on derivation data. Contains no language model.
- Banded score: the YB-0048 NEWS2-style levels (stable, watch, concern, urgent), cut-points from derivation data.
- Self-consistency (SC): d as above. A signal from the model, read by outside code.
- Layered: YB-0049 rule unchanged (probe at 5% OR d >= delta, total 10% budget).
- Gated layered (scaling variant, fixed in advance): run SC only on episodes whose in-time banded score is watch or above (at least 1
  point) or that were never monitored (no in-time checkpoint, so no banded score); alarm if probe at 5% OR (gated and d >= delta), total
  10% budget, delta chosen by the YB-0049 rule over the gated episodes.
- Controls (PROTOCOL rule 5): elapsed-length percentile and question-type error rate, as in YB-0045, scored and compared in every run.
- Not recorded for the new seeds: the LLM judge (gpt-oss-120b) baseline. It caught 28 of 138 in YB-0045, far below every trained
  monitor, and the author's position excludes LLM judges from the decision path; it is dropped to save recording time.

All recall comparisons: in-time recall at matched false-alarm rate (10% of correct episodes unless stated), thresholds re-set in every one
of 2,000 paired bootstrap resamples over answered test episodes (PROTOCOL rule 5); one bootstrap serves every comparison, so all
differences are paired. Code: src/decider.py (rules, bootstrap, burden arithmetic, operation counts), tests/experiment.py.

## Hypotheses and decision rules
- H1 (primary, close call B): layered minus SC alone > 0. Supported if the lower 95% bound > 0.
- H2 (close call A): probe minus trained text > 0. Supported if the lower 95% bound > 0.
- H3 (non-inferiority, safety without an AI signal): non-LLM stack minus SC alone, margin 0.10. Supported (non-inferior) if the lower 95%
  bound > -0.10.
- H4 (scaling: cost). Cost per check as a share of the monitored model's own inference for the same episode. Primary measure:
  measured wall-clock, pooled over test episodes (sum of monitor seconds / sum of generation seconds), with a 1,000-resample bootstrap
  interval. Monitor seconds are timed per scoring call in the analysis sandbox (CPU); generation seconds are the recorder's per-episode
  wall time (Apple GPU, including telemetry taps, which makes inference look slower; stated as a limitation). Self-consistency seconds
  are the recorded review times. Secondary: analytic operations (probe and text monitor only) against 2 x 3.6e9 active parameters x
  tokens generated. Supported for a monitor if its pooled wall-clock share is at most 1%. Reported for: probe, text, difficulty, non-LLM stack, SC (expected
  several times inference), layered, gated layered (SC cost x share of episodes gated).
- H5 (scaling: false-alarm burden, descriptive with a pre-declared reference). For each monitor, from measured recall (TPR) and false-alarm
  rate (FPR) with bootstrap intervals: precision PPV = TPR x p / (TPR x p + FPR x (1 - p)) and alarms per million actions
  1e6 x (TPR x p + FPR x (1 - p)), at error base rates p = 10%, 1%, 0.1%; plus recall at a 1% false-alarm rate (about 58 false alarms
  expected at that rate, enough to estimate). Reference, stated in advance: a monitor whose PPV at p = 1% is below 10% would send more than
  nine false alarms for every true one at that base rate.
- Secondary (descriptive): gated layered recall vs layered recall and the share of SC calls saved; per-seed results; per-task-type results;
  review delay a hold gate would impose (median, 90th percentile).

## Pre-declared consequences
- H1 supported: layering adds catches beyond the model's own disagreement (P5 supported, narrow). Not supported: on this data SC carries
  the layered system; report H3 to H5 regardless.
- H2 supported: internal state beats a trained text reader at equal training, in-distribution (P2 strengthened). Not supported: P2 stays
  "beats difficulty, not shown to beat trained text"; the case for internals rests on transfer (YB-0047 Part B) and on T3 at scale.
- H3 supported: a stack with no AI signal comes within 10 points of the model's own self-check on this data. Not supported: report the
  measured cost of excluding the model's self-disagreement; P1 as a design principle then has a stated accuracy price.
- H4 and H5 determine whether "scales better in theory" can be stated as a measured result, and at which base rates it holds.

## Process (PROTOCOL rules 1 to 17)
One command: agr/yb0050_start.sh (waits for AC power, then runs agr/yb0050_chain.sh under caffeinate with a battery guard; every
recorder resumes where it stopped). Smoke test (rule 15) and dry run on derivation seeds only, with synthetic SC scores for the test path; analysis code complete and
committed with this plan; plan timestamped (rule 13) before recording; recording run alone with runguard and environment snapshots
(rule 7); layer-tap alignment test before recording (rule 8); confirmatory analysis only via make confirmatory (rule 14); independent
audit before any external claim (rule 10).

## Estimated cost (to be measured, not assumed)
Base recording: about 8 hours (0.64 h of generation per seed, measured on YB-0045 seeds 9, 13, 14, times 12 seeds). Self-consistency on
about 6,400 answered episodes: about 19 hours at YB-0049's measured rate (4.71 h for 1,605). Analysis: under an hour (the dry run took
8 minutes on a quarter of the data). Total about 28 hours on the Mac, on AC power. Alternatively the DGX Spark, recorded as an
environment change.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
