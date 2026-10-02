# Seventh audit: the v8 blog drafts

I only read files. The one thing I wrote is the report copy at `~/.claude/plans/you-are-an-independent-shimmering-eich.md`.

## Summary

**Numbers.** Every figure I checked matches a committed file in the private repository, with the right scope, sign, rounding and sample.

**The public snapshot is out of date.** It's the copy readers are sent to (`~/Desktop/agr-public`, cut from private commit a025fca at 07:46 PDT on 2026-10-01). It was made before:
- the YB-0045 pre-registration;
- the YB-0045 results;
- the sixth-audit fixes, including `docs/sources`;
- rule 13 and the timestamp proofs.

So readers can't check the main result of either post from the public repository. The sixth audit flagged exactly this (CORRECTIONS.md D6-C1, which promises a new snapshot "after YB-0045"), and it has happened again.

**No audit has reviewed YB-0045.** The posts suggest the six audits support the current result, but all six came before it.

**Some claims go further than the data:** "at every checkpoint", "solid ground", and "in milliseconds" for the probe.

**Verdicts**
- **blog_plain_v8.md: not publishable as written.** It becomes publishable once the public snapshot is re-cut (C1), M1–M7 are fixed, and the minor fixes below are applied.
- **blog_technical_v8.md: not publishable as written.** Same conditions.

## Findings

| ID | Sev | Draft and quoted text | Issue | Evidence | Fix |
|---|---|---|---|---|---|
| C1 | critical | Both: "The code, data, reports and corrections are public at github.com/YobieBenjamin/autonomic-graph-regulation". Technical: "(sources: docs/sources in the repository)" | The public snapshot has no YB-0045 material: no algorithm folder, no LEDGER row, no post-YB-0045 claim status. It also lacks `docs/sources/`, the sixth audit report, `scripts/timestamp_prereg.sh`, rule 13, and the YB-0045 timestamp and RFC 3161 files. Its CITATION.cff still points to the private `safety` repo. Readers can't check the headline result ("more than three times", +0.478). This repeats D6-C1. | `agr-public/PROVENANCE.md`: source a025fca, 07:46 PDT. Private log: 682f373 at 07:53; results at 18:24–18:34. `agr-public/algorithms` ends at YB-0042. CORRECTIONS.md:177 | Re-cut the snapshot from 516d46b or later (after these fixes). Update PROVENANCE.md and confirm on GitHub before posting. |
| M1 | major | Technical: "stamped via OpenTimestamps … (proof complete, Bitcoin-anchored)" | This is true only in the private repo. The public snapshot holds the older, unfinished proof (1,085 bytes, no Bitcoin anchor). The finished proof (5,196 bytes, 4 Bitcoin attestations) was written at 07:53, after the snapshot. | `agr-public/archive/timestamps/YB-0042…ots` is 1,085 B. The private `.ots` is 5,196 B; the private `.ots.bak` is 1,085 B. | Fixed by C1. Then check that the public proof verifies. |
| M2 | major | Technical: "Pre-registration 682f373 (OpenTimestamps; RFC 3161 tokens obtained later)". Plain: "committed and publicly timestamped before any of the new test questions were recorded" | The YB-0045 OpenTimestamps proof is still pending (no Bitcoin anchor), so on its own it proves nothing yet. "Obtained later" also undersells the RFC 3161 tokens. They are dated 15:45Z, before the first test recording (seed 9, 18:59:32Z), though after derivation recording started (seed 5, 15:14:05Z). The plain post's claim is true only because of the RFC tokens, and neither draft says so. | `YB-0045…ots`: 735 B, 0 Bitcoin and 4 pending attestations. PROTOCOL.md rule 13: tokens at 15:45 UTC. `data/agr/env/recorder_seed9_1790881172.json`: 18:59:32Z. `recorder_seed5…`: 15:14:05Z | Run `ots upgrade` and commit the result. State the timeline: OpenTimestamps at 14:53Z; RFC 3161 at 15:45Z, after derivation recording began and before the first test recording at 18:59Z. |
| M3 | major | Plain: "Five further audits reviewed that test, the second test and earlier drafts … this version corrects what they found"; "It took … three pre-registered tests and six AI audits to get here". Technical: "This version incorporates all of them." | None of the six audits reviewed YB-0045, the test that "settles" the question. The sixth audit covered YB-0042 and the v6 drafts. Protocol rule 10 requires an audit before a result is presented publicly. | `blog_v6_audit_2026-10-01.md` covers YB-0042 and v6. The YB-0045 results commits (18:24–18:34) came after every audit. | Say that audits 1–6 did not cover YB-0045. Archive this seventh audit and cite it. |
| M4 | major | Plain: "It held … at every moment I checked during the AI's thinking." Technical §9: "where it also held at equal false alarms, with frozen thresholds and at every checkpoint" | Per-checkpoint AUROC is a different measure from catching errors in time. At t = 384 the regulator and judge ranges overlap: 0.761 [0.666, 0.851] vs 0.690 [0.593, 0.780]. The technical draft's own §5 claims non-overlap only at 48, 96 and 192, and those intervals are unpaired. The equal-false-alarm and frozen-threshold results are plain counts with no range (83 vs 26; 93 vs a judge tuned on the test set). The repo's claim status makes the same overstatement. | YB-0045 `results.json`: `S_per_checkpoint_auroc["384"]`. `S_equal_fpr_monitorable` has no regulator-minus-judge range. `S_frozen_derivation_thresholds` has no judge entry. RESEARCH_PROGRAM.md:160 | Write: "point estimates favoured the regulator at all four checkpoints; the ranges separate at 48, 96 and 192 tokens (unpaired)". Label the equal-false-alarm and frozen-threshold results descriptive. Make the same change in RESEARCH_PROGRAM.md. |
| M5 | major | Plain: "in milliseconds instead of seconds". Technical: probe results reported under "a deadline that counts compute" | The probe was charged the regulator's fixed 5 ms allowance (`fixed = lambda r, t: COST`). Neither the probe's compute time nor the cost of capturing hidden states (`agr/hstap.py`) was ever measured. The 4.1 ms measurement (YB-0033) is for the regulator only and leaves out recording overhead. Neither draft says this. | YB-0045 `tests/experiment.py:81–83` (same in YB-0042) | Disclose that the probe's cost was assumed. Remove "milliseconds" for the probe, or label it an assumption. |
| M6 | major | Plain: "The core idea … now rests on solid ground" | Too strong for the evidence: one model, one task family, checkpoints up to 384 tokens, AI-only audits, no human review, and the deciding result unaudited (M3). | RESEARCH_PROGRAM.md:160 (scope); README (authorship) | "…is now supported by a pre-registered, adequately powered test, for one model and one kind of task." |
| M7 | major | Plain: "The decisive test used 600 newly recorded questions" and the "The main result" section | The post calls seed 7 (YB-0035) "decisive" and "the main result", then presents YB-0045 as the test that settles the question and builds the conclusion on it. Readers see two different headline results (23/40 vs 94/138). | Plain draft, lines 123 and 166 vs 249–281 | Call seed 7 "the first fresh test" and make YB-0045 the main result. |
| m1 | minor | Technical: "Thresholds are set within each seed, so per-seed counts do not sum to the pooled counts." | Only the judge's counts fail to add up (11 + 12 + 12 = 35, vs 28 pooled). The regulator's (28 + 35 + 31 = 94) and the probe's (30 + 38 + 32 = 100) match exactly. | `posthoc_per_seed.json`; `results.json` | "…need not sum (the judge's sum to 35, not 28)". |
| m2 | minor | Plain: "asking the AI again is more accurate than the regulator". Technical §9: "On finished answers, self-consistency is more accurate." | That comparison used an older regulator from YB-0031, trained before the telemetry timing bug was fixed. The current regulator was never tested on finished answers. | YB-0031 README:43 (technical §1 states this correctly) | Add "than an earlier version of the regulator". |
| m3 | minor | Plain (third test): "with every monitor held to the same 10% false-alarm limit" | Counting only the answers each monitor could actually see, the regulator's false-alarm rate is 16.5% vs the judge's 11.6%. The post gives this breakdown for seed 7 but not for YB-0045. | YB-0045 `fpr_monitorable` | Add both rates, or cite the equal-rate check (83 vs 26). |
| m4 | minor | Technical: "Power about 0.77 at +0.175 and about 0.99 at +0.30" | These numbers come from a written scaling argument in the pre-registration. No script or output file exists, which breaks rule 3 ("No number without an artifact"). | YB-0045 PREREGISTRATION.md, "Power" section | Commit a power script and its output, or label the figures approximate. |
| m5 | minor | Both: "about 24 times less data per word" / "120 values vs 2,880 per layer" | The 24× holds only against a single layer's hidden state. The probe uses two vectors per layer (last token and prefix mean), and the four-layer probe uses four layers. "Per layer" also makes the 120 sound like a per-layer figure. | Model hidden size 2,880; YB-0042 probe definition | "120 values per token across all 24 layers vs 2,880 for one layer's hidden state". |
| m6 | minor | Plain: "with more than 100 partners" | This comes from secondary outlets (shattered.io, kingy.ai), not NVIDIA, and the repo's source record says it was not independently verified. | `docs/sources/nvidia_open_agent_safety_platform.md` | Attribute it to those outlets, or cite NVIDIA's own release. |
| m7 | minor | Plain: "…ordinary prose, I did not measure how confident…" | Comma splice. | Plain draft, lines 320–322 | Split into two sentences. |

**Checked and correct (not listed above):**
- **Seed 7 (YB-0035):**
  - The in-time counts and false-alarm rates.
  - The per-checkpoint AUROCs and episode counts.
  - 194 of 495 correct answers finish too early to monitor.
  - Judge and self-consistency timings.
  - The exploratory 19 vs 11 (+0.20 [+0.02, +0.43]) and 22/40 at 9.1% / 15.0%.
  - Type-by-length 9/40.
  - The 105/68/74/65 never-answered sensitivity counts.
- **Other tests:** seeds 5 and 6; all YB-0042 figures (including 195 and 1,609); all pooled YB-0045 figures, ranges and percentages, plus 582 and layer 18.
- **Earlier studies:** YB-0031 (0.982, 0.947, 0.890, −0.057, 0.366 [0.304, 0.433], 4 vs 12 of 47) and YB-0015 (27/36).
- **Timestamps and sizes:** the GitHub server timestamps for seed 7; the YB-0042 OpenTimestamps stamp 19 s before the first recording; model-size ratios 5.59× and 1.42×.
- **Audits and process:**
  - The shift verification: 0.012 vs 0.81, 11/11, worst reading 2.8.
  - The audit finding counts: 38/25/30/23/11/20.
  - The 13 rules.
- **Code and citation:**
  - In both seed 7 and YB-0045, the wrong answers come from four of the six question types.
  - The YB-0045 analysis code is unchanged since the pre-registration (682f373).
  - arXiv:2607.21433 exists, with the cited authors and topic.
