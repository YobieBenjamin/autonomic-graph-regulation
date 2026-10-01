# Audit of the v3 blog drafts

I made no changes to the repository. The only file I wrote is this report, at `~/.claude/plans/you-are-an-independent-starry-toucan.md`.

## Summary

**The numbers check out.** Every figure in both drafts matches a committed file, with the right scope, sample and rounding. The files are:
- YB-0035 `results.json`, `exploratory_audit2.json`, `exploratory_audit3.json` and `seed7_counts.json`
- the judge-timing, shift-verification and GitHub-timestamp artifacts
- the YB-0015, YB-0018, YB-0031 and YB-0033 `results.json` files

I re-derived several figures myself:
- **Sample:** 194 = 495 − 301.
- **Features:** 240 + 74 + 1 features.
- **Settings:** C = 0.1; 24-token windows, stride 8, lag up to 3.
- **Bootstrap:** 1,000 resamples, with thresholds re-set in each.

**No leaks or post-hoc changes.** The checkpoint features never use total reasoning length (`min(upto, final_start)`). After pre-registration commit b6c795b, the YB-0035 code and tests only gained license headers and the new exploratory scripts. The snapshot's `MANIFEST.sha256` verifies cleanly.

**The real problems** are where readers are sent for verification, and whether the record they find matches the posts:
- The public repo is a one-commit snapshot. The commit history that timestamps the pre-registration is private.
- The ±6 ms clock check was run about 10 hours after the recording.
- CORRECTIONS.md and LEDGER.md are out of date.

**Verdicts:**
- **Plain draft: not publishable as written.** It becomes publishable after K1 and M1–M4 plus the minor fixes. All are wording changes; no new experiment is needed.
- **Technical draft: not publishable as written,** but close. It needs K1, M1, M2 and M5 (wording or disclosure); everything else is minor.

## Findings

| ID | Sev | Draft / quote | Issue | Evidence | Fix |
|---|---|---|---|---|---|
| K1 | critical | Plain: "The full record, including every mistake and correction, is public at github.com/…"; Plain: "sent to GitHub, whose own servers logged their arrival about ten seconds before…"; Tech: "Protocol and analysis code: commit b6c795b" | The public repo is a one-commit snapshot. b6c795b and all other history are private, so readers can't find the cited commit or check that the pre-registered code is what ran. "Full record is public" is false. | agr-public `git log` = 1 commit; PROVENANCE.md: the private repo "holds the complete, unaltered history… evidence of record… Qualified reviewers may request read access" | Publish the history through b6c795b (minus docs/book), or say plainly that the history is private and available to reviewers on request. Delete "full record is public". |
| M1 | major | Tech: "15:26:49.96 UTC (Mac clock, within ±6 ms of network time)"; Plain "about ten seconds" | (a) The ±6 ms offset was measured about 10 hours after the recording. (b) Only the push time comes from GitHub's servers. The recording start comes from the author's own clock, written by the author's recorder. Because generation is greedy and the questions are fixed by the seed, a skeptic can argue seed 7 was recorded earlier and then recorded again. | `c1_github_server_timestamps.json`: `retrieved_utc` 2026-10-01T01:33Z; `t_unix` in seed7_L comes from the local `time.time()` (recorder.py l.71); PROTOCOL rule 13 (public timestamps) was not in place for b6c795b | "Offset −1 ms when checked about 10 hours later." Say the start time is self-reported. Don't imply both sides of the ordering are third-party verified. |
| M2 | major | Tech: "All findings and resolutions are logged in CORRECTIONS.md"; Plain: "logged every error in a public corrections record" | The third audit's 20 minor findings (m1–m20) are not logged. That section still says "Resolution in progress". Its C1 row still says to describe the repo as "private pending patent review". | CORRECTIONS.md third-audit table lists only C1 and M1–M9 | Log m1–m20, update C1, then re-cut the snapshot. |
| M3 | major | Both drafts send readers to the repo as the corrected record | LEDGER.md still states retracted claims as holding: YB-0012 "earliness: HOLDS (4.5 s)", YB-0019 "earliness holds", YB-0015 "contamination not supported", YB-0033 "EUREKA (confirmed robust)", YB-0017 "9-10x", YB-0018 "no metabolism". | LEDGER rows vs CORRECTIONS F1, F2, F3, F7, F19, B16 | Add correction banners to those rows (PROTOCOL rule 11), then re-snapshot. |
| M4 | major | Plain: "confidence is a poor guide… pointed the wrong way"; "its own confidence tells you little about whether it is right" | AUROC 0.366 is an inverted signal: flipped, it scores 0.634, so it carries information. It isn't controlled for question type, and it comes from YB-0031, not YB-0035. The third audit raised this (m8) and it is still unresolved. | YB-0031 results.json answer_confidence [0.366, 0.304, 0.433] | "Its confidence was misleading: wrong answers carried more of it (earlier experiment)." Drop "tells you little". |
| M5 | major | Tech §8: "What this work adds… the combination"; Plain: "What this does… mean" | No hidden-state probe baseline was run. A linear probe on activations is the obvious text-blind competitor from the cited prior work, and the first thing a hostile expert will ask for. | YB-0035 monitors: organism, aiews_v4, length C1/C2, judge, selfcons only | Add the limitation: "not compared against a standard hidden-state probe". |
| m1 | minor | Tech subtitle "two audits"; §6 heading "Two adversarial audits" | The body describes three audits, and the plain draft says three. | Three audit reports in archive/audit/ | "Three audits". |
| m2 | minor | Tech: "twelve process rules" | PROTOCOL.md has 13 rules. | docs/PROTOCOL.md | "thirteen". |
| m3 | minor | Tech: "Each critical finding was verified independently" | It was verified by the same AI assistant that did the work. The plain draft words this correctly. | CORRECTIONS B25 | "verified by the research assistant (Claude) under my direction". |
| m4 | minor | Tech: "early regulators did not beat question-type (0.764) or length (0.796)"; Plain likewise | True for YB-0012, YB-0019 and YB-0030. The YB-0031 regulator (0.890), which both posts cite, did beat type (0.80) and length (0.73). | CORRECTIONS F16 | Name the experiments. |
| m5 | minor | Plain: frozen threshold "with somewhat more false alarms" | It has fewer false alarms than the primary regulator (9.1% vs 9.9% overall; 15.0% vs 16.3% among answers it could see). | exploratory_audit2.json; results.json | "about 15% of the correct answers it could see (target 10%)". |
| m6 | minor | Plain: "charges each monitor its own measured computing time"; "about 5 milliseconds" | The regulator is charged a fixed 5 ms, not a measured time. The 4.1 ms it is based on excludes the cost of recording the vital signs. | corrected.py FIXED_COST; YB-0033 0.00405 s; F31 | State both points. |
| m7 | minor | Plain: "a larger AI judge did about as well as an earlier version of it" | The judge scored higher (0.947 vs 0.890), though not significantly. The wording leans toward the regulator. | YB-0031 −0.057 [−0.131, +0.012] | "scored higher, though not significantly". |
| m8 | minor | Plain: "Today it is a software simulation on one MacBook" | No chip simulation exists. The virtual-SoC spec is future work. | Tech §10.6; backlog items YB-0039 to YB-0041 | "software running on one MacBook". |
| m9 | minor | Plain: "a different company's model with a different internal design" | Qwen3-VL-30B-A3B is also a mixture-of-experts model. It differs in size, not design class. | HYPOTHESES YB-0037 | "of a different size". |
| m10 | minor | Plain: "In my book…"; subtitles "Part II" | The repo calls the book an unpublished draft, so readers can't consult it. | PROVENANCE.md; commit 01d4713 | "forthcoming"; link Part I if it exists. |
| m11 | minor | Plain: "what is different here is… a fair race" | Missing the technical draft's "to our knowledge" caveat. "Fair" also clashes with the plain draft's own admission that the race is lopsided against self-consistency. | Tech §8 | Add the caveat; say "a race that counts compute time". |
| m12 | minor | Judge timing (both drafts) | The judge's speed partly reflects its settings (reasoning effort "medium", up to 4,000 tokens), which aren't disclosed. The per-checkpoint scores show it also lost on accuracy, not just speed. | prefix_monitors.py l.45; AUROC 0.54–0.61 vs 0.70–0.80 | Disclose the settings; mention the accuracy gap. |
| m13 | minor | Tech: synchronization test description | The test compares 4 of the 5 readings (it skips the cosine) on one prompt. "Stricter" is loose because the old and new pass criteria aren't nested. | test_layertap_alignment.py cols [0,1,2,4]; evidence log: max error 0.099, lag error ≥ 0.601 | Reword and give the actual values. |
| m14 | minor | Tech: "regulator 30/44 and 25/43" | These differ from LEDGER's 28/44 and 24/43 with no explanation; they are the resynchronized re-analysis. | YB-0035 results.json vs LEDGER | "(after resynchronization; originally 28, 24)". |
| m15 | minor | "5.6x / 1.4x" (both drafts) | No committed source, against PROTOCOL rule 3. | Only CORRECTIONS F38 | Cite the model cards or commit the arithmetic. |
| m16 | minor | Plain: "replicate… from the public code and data" | The repo is source-available for noncommercial use only, with patent rights reserved. The raw `data/agr` recordings aren't in the snapshot (only compressed per-algorithm copies). | LICENSING.md; .gitignore | Add "source-available for noncommercial research". |
| m17 | minor | Tech: "arXiv 2607.21433, 2026" | The closest prior work is cited without authors or title. | RESEARCH_PROGRAM | Give the full reference. |

The planning tools for formal sign-off aren't available in this session, so the report above is final as written.
