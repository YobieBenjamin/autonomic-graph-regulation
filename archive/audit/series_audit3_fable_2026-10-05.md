# Twelfth audit, Fable 5.1: series v4 (YB-0045 to YB-0049)

Audited against private commit 7d825e0 and public snapshot 656d1d7, which names 7d825e0.

## Verdict: publishable with fixes

Every number, interval, count, hash, path and formula in both drafts traced to a committed file or recomputed correctly. Two findings are major. Both are disclosure regressions rather than wrong results.

## Findings

### Part 1

**P1 (major)** Quote: "The inside reader warns while the AI is still thinking, in a few thousandths of a second." (lines 203 to 204). The 5 ms monitor cost is an assumed charge, never measured. Evidence: CORRECTIONS.md line 199 (D7-M5, "Probe compute cost assumed (5 ms), never measured"), YB-0047 PREREGISTRATION.md ("5 ms (assumed, as for the probe; disclosed)"), docs/RESEARCH_PROGRAM.md line 162. The previous audited Part 2 carried the qualifier (archive/audit/series_final_2026-10-04/Part2 line 159). Fix: "in what I assume is a few thousandths of a second; I charged every inside check 5 ms and have not measured it."

**P2 (minor)** Quote: "The ask-it-again check, all by itself, caught 124. That's as many as both layers together." (191 to 192). Layered caught 123 (YB-0049 results.json, layered.caught). Fix: "one more than both layers together, 124 to 123."

**P3 (minor)** Quotes: "The trained word reader fell apart." (138) and "they didn't handle new kinds of problems at all" (143 to 144). Within-type held-out AUROC for text is 0.710, 0.565, 0.518, 0.453 and for the regulator 0.570, 0.552, 0.291, 0.547 (YB-0047 results.json, S_transfer_by_task). Pooled values below 0.5 partly reflect miscalibration (PF-7). Part 1 also omits that no monitor transferred on day-of-week (Part 2 lines 396 to 397). Fix: "mostly failed on the new kind" and add that none of the three handled unseen calendar dates.

**P4 (minor)** Quote: "Every check I built that runs as outside code beat the AI judge, even the dumb difficulty check." (280 to 282, under "Sure"). Tested with intervals only for regulator, probe, difficulty, stack and banded score. Length (39) and task type (31) versus judge (28) were never tested and run at lower false-alarm rates (YB-0045 results.json). Fix: "caught more mistakes than the AI judge, and where I tested the gap it held."

**P5 (minor)** Quote: "about 6,000 multiplications for each word" (268 to 269) versus Part 2 "about 5,800 multiply-adds" (571). Same quantity, 5,761. Fix: one rounding in both parts.

**P6 (minor)** Quote: "it handles new kinds of problems better than reading the words" (283 to 284, under "Sure"). The probe-versus-text transfer comparison was not pre-registered; H3 tests each monitor against 0.5. Fix: "kept working on new kinds of problems where reading the words did not."

### Part 2

**T1 (major)** Quote: "c the monitor's compute cost (5 ms for internal-state and text monitors, measured per call for the judge, 0 for metadata baselines)" (130 to 133). The word "assumed" appears nowhere in v4 Part 2. Evidence as P1. Fix: "a fixed 5 ms charge, assumed and never measured, for internal-state and text monitors."

**T2 (minor)** Quote: "the layered system reached the same recall with fewer false alarms (6.95% vs 8.86%)" (516 to 517). 123 versus 124. Fix: "nearly the same recall (123 vs 124)."

**T3 (minor)** The banded-level table (433 to 444) sums to 1,021 episodes and 136 wrong. It covers only episodes that reached a checkpoint (YB-0048 tests/experiment.py, `m = mon & ...`), excluding 584 never-monitored episodes with 2 wrong. Fix: add "of the 1,021 episodes that reached a checkpoint."

**T4 (minor)** P1 row: "Every outside-code monitor beat the LLM judge (YB-0046)" (57 to 59). See P4. Fix: "caught more errors than the judge; tested for difficulty, regulator, probe, stack and banded score."

**T5 (minor)** Section 15 "Holds: ... transfers better than text; ... a hospital-style score is a good triage tool" (649 to 653). Neither is a pre-registered result. The triage gradient is a descriptive secondary. Fix: "transfers where text does not"; label the triage sentence descriptive.

**T6 (minor)** Quote: "analysis started 18:29:59 UTC" (290) for YB-0046. No committed or surviving log records this. The /tmp chain logs exist for YB-0047 and YB-0048 but not YB-0046. Only the YB-0046 README and docs/SCALE_UP_PROPOSAL.md assert it. results.json mtime is 18:41:01 UTC. Fix: commit evidence or write "started within a minute of the timestamp, finished 18:41 UTC."

**T7 (minor)** Line 563 to 564 "stopping in as little as about 120 ms (Aron and Poldrack, 2006)" while docs/THEORY_AND_POSITION.md L4 row says "about 190 ms". Both are in CITATIONS.md (fastest versus mean SSRT). Fix: "stop-signal reaction times near 190 ms, as fast as about 120 ms."

### Repository

**R1 (major)** The committed YB-0049 chain log, agr/yb0049_chain_progress.log, has 7 lines ending at STAGE2_RECORDING_START 23:18:49. The resume at 03:43:12, the three SEED_COMPLETE lines at 07:39:34, CONFIRMATORY_OK at 07:47:04 and RESULTS_COMMITTED exist only in /tmp/chain49.log. The pause time 00:05 UTC exists only as a comment in agr/resume_yb0049.sh. No /tmp/battery_guard.log exists, so the guard did not fire and the stop was manual. The stage-2 records carry review_seconds but no wall-clock time per record. The YB-0049 README (lines 8 to 9) and Part 2 (450 to 453) rest on this uncommitted evidence. The sequence itself checks out: the sum of review_seconds is 4.71 h, matching the two windows of 23:18:49 to 00:05 and 03:43 to 07:39 (4.72 h); the resume script verifies plan and recorder against commit 1ec19a9, and the chain's resume branch skips timestamping. Fix: commit /tmp/chain49.log over the truncated log and commit /tmp/resume_yb0049.log; state in the README that the pause was a manual clean stop before the battery threshold and that per-review wall-clock times were not recorded.

**R2 (minor)** algorithms/YB-0048-multilevel-fusion/README.md line 9: "timestamped 20:10:56 UTC". Both RFC 3161 tokens read 20:10:55 UTC. Part 2 is correct. Fix: 20:10:55.

**R3 (minor)** docs/THEORY_AND_POSITION.md section 6 still says "Next tests: YB-0048 (now, existing data)", and the header reads "v1, 2026-10-04" though edited on 2026-10-05 in 7d825e0. Fix: update to the scale-up pointer and bump the version.

**R4 (minor)** docs/PROTOCOL.md rule 13 says the script "records the commit hash and timestamps it". For YB-0046 to YB-0049, scripts/timestamp_prereg.sh hashes PREREGISTRATION.md itself. The imprint equals the committed file's SHA-256 in all four cases, so the guarantee holds, but the wording does not match current practice. Fix: "timestamps the pre-registration file, or a record of the commit hash."

**R5 (minor)** The /tmp chain logs for YB-0047 and YB-0048, which back the "analysis started" times in Part 2, are not committed. Fix: commit them.

## Checked and found correct

- **All results numbers.** YB-0045 counts, shares, FPRs, +0.478 [+0.307, +0.560], power 0.77 and 1.0. YB-0046 all six counts, H1 to H3 and the secondary interval, per-checkpoint and within-type AUROCs. YB-0047 90 caught, both intervals, CV AUROC 0.841 at C=1, per-checkpoint AUROCs, four held-out rows and pooled H3 with intervals. YB-0048 96, 86 at 6.4%, both intervals, overlaps 81/19/9/84, 117 and 21, stack and probe AUROCs, four banded levels. YB-0049 123 at 6.95%, 124 at 8.86%, AUROC 0.965, +0.167 [+0.092, +0.250], 38 and 28, Jaccard 0.697 versus 0.7431 (81/109), 8.2 s and 20.7 s, 584 never monitored, 2 errors there, allocation 121 at 4.8% and 127 at 9.3%.
- **YB-0049 stage 2 recomputed** from the committed jsonl and YB-0045 labels: 1,605 reviews, one per answered test episode, no gaps or extras; AUROC 0.9652; d above 0.25 catches 124 at 8.86%; median 8.227 s, p90 20.696 s; 584 episodes end before token 48 with 2 wrong, both at d ≥ 0.75. The data/agr and algorithms copies are identical.
- **Other artifacts.** YB-0044 5.47 s (4.99 to 5.94), 74 of 93, 79.6% [72.0, 87.1], 93 held, 7.4 s, 16 of 138; alarm-to-commit gap median 3.29 s supports Part 1's "within a few seconds". YB-0031 AUROC 0.366 [0.304, 0.433] and 0.982. YB-0015 27 of 36. Token timing 14.44 ms over 442,306 tokens. Judge 1.546 s and 7.179 s. Model sizes 5.59x and 1.42x. Bandwidth arithmetic.
- **Pre-registration sequence.** Commits fe4ad29, 9307f20, 4a1e395, 1ec19a9 exist with the stated content and precede their RFC 3161 times by 8 to 10 s. Both TSA tokens per plan read exactly the times in Part 2. Message imprints equal the SHA-256 of the committed plans, which were never modified after their plan commit. All four OpenTimestamps proofs contain Bitcoin block-header attestations. The YB-0047 and YB-0048 chain logs show CONFIRMATORY_START at 19:24:50 and 20:10:56.
- **Public snapshot.** All 27 GitHub paths in Part 2 exist. PROVENANCE.md names 7d825e0. Key files are byte-identical between private and public. YB-0049 stage-2 data, the drafts and the resume scripts are public.
- **Code matches text.** The in_time function is identical in YB-0045 to YB-0049. in_time_max, cap_threshold and boot_diff match the formulas. Regulator 240 + 74 + 1 features, C = 0.1, 24-token windows, stride 8, lags 0 to 3, |ρ| in either direction. Probe layout, 5,761 inputs, layer 18, C = 0.001 by grouped 5-fold CV. add_carries verbatim; multiplication carries; per-type C = 1 and the fewer-than-5-errors rule. TF-IDF settings and C grid. Stack and Bands.points verbatim; GroupKFold(5) cross-fitting. Label-free normalisation in YB-0047 Part B. layered.choose verbatim, D_GRID, 5% stage-1 budget, thresholds re-set in every resample. Unit tests check the cap, the useless-stage-2 reduction and no peeking past t. The stage-2 recorder's sampling and normalisation are verbatim from agr/monitors.py.
- **Consistency.** Hypotheses, decision rules and pre-declared consequences match what both drafts report. CORRECTIONS.md PF-1 to PF-7 and protocol rules 14 to 17 are as described. LEDGER rows and RESEARCH_PROGRAM claim status agree. THEORY_AND_POSITION P1 to P7 agree with Part 2's table apart from R3 and T7. All 21 citations are in docs/sources/CITATIONS.md as read in full and are described consistently with the registry. Part 1 and Part 2 agree on every shared number except P5.

The report is also saved at `~/.claude/plans/you-are-an-independent-silly-goose.md`.
