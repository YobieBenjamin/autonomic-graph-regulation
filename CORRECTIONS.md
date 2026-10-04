# Corrections log

**Outcome of the deep debug (2026-09-30; revised after the second audit).** All critical findings were independently verified. The real-time result was re-run under a corrected protocol (YB-0035, code committed before its test data existed). On the only fresh test set (seed 7), before the answer exists, the regulator raised in-time warnings on 23 of 40 wrong answers vs 11 for the LLM judge and 9 for the length control (+0.30 [+0.049, +0.487] vs the judge). Exploratory checks after the second audit: with false alarms equalized among monitorable episodes, 19 vs 11 (+0.20 [+0.02, +0.43]); with a threshold frozen from training data, 22 of 40. Seeds 5 and 6 (reused test sets) agree; their pooled estimate is descriptive only. Boundaries: on finished answers, an earlier pre-fix regulator (0.890, YB-0031) was significantly less accurate than self-consistency (0.982) and not distinguishable from the LLM judge (0.947; difference -0.057 [-0.131, +0.012]); with never-answered episodes counted as failures, the regulator is no better than length. Pre-YB-0033 accuracy claims did not beat question-type or length baselines (F16). Terminology from here on follows docs/GLOSSARY.md (e.g. regulator = organism).

Every error found in this repository, who found it, how it was verified, and how it was resolved. Nothing is silently
edited: a correction changes the affected document **and** is recorded here. Sources: the independent audit
(`archive/audit/independent_audit_2026-09-30.md`, a separate read-only Claude Code session at commit fc575cf), our
own verification (Phase A of the deep debug), and our own findings (marked *self*).
Resolution codes: **FIXED-YB-0035** (corrected in the re-run experiment), **RETRACT** (claim withdrawn), **REWORD**
(claim qualified), **ARTIFACT** (missing script or data added), **DOC** (documentation fix), **PROCESS**, **OPEN (backlog)**.

## Critical
| ID | Finding | Verified | Resolution |
|---|---|---|---|
| F1 | YB-0012 'alarms 4.5 s before the answer, 100% of detections': the online alarm fires on 89.3% of correct answers at the first check (93.9% at any check); the lead is reasoning length | Phase A rerun (exact) | RETRACT the earliness claim; superseded by matched-false-alarm races (YB-0033/34/35) |
| F2 | YB-0019 'warned 4.65 s before answering, every time': same mechanism, 56.1% false alarms | auditor rerun | RETRACT, as F1 |
| F3 | YB-0015 'reasoning phase detects errors; the reasoning trace is not contaminated': features were whole generation + answer segment; no reasoning-only feature existed | Phase A (code) | RETRACT the claim; OPEN: re-test on the reasoning segment only (backlog) |

## Major
| ID | Finding | Verified | Resolution |
|---|---|---|---|
| F4 | Layer tap stored each token's reading one step late (prompt pass first); stale, not future | Phase A: fresh forward pass (lag-1 error 0.01, aligned error 0.4-3.6) | FIXED-YB-0035: tap fixed + permanent test (agr/test_layertap_alignment.py); seeds 2-6 resynchronized (shift verified, 0.013 vs 0.5-0.9 SD); result confirmed on corrected data |
| F5 | YB-0033/34 excluded never-answered episodes (62/600, 63/600) without disclosure | auditor | FIXED-YB-0035: pre-declared sensitivity analysis; DOC disclosure in YB-0033/34 |
| F6 | YB-0034 undocumented; pre-registered pooled estimate R3 never computed | auditor, self | FIXED-YB-0035 (pooled 5+6+7); DOC: YB-0034 README and LEDGER row |
| F7 | 'EUREKA (confirmed robust)', 'first leak-free' overstated | auditor | REWORD: 'primary criterion met (YB-0033), replicated (YB-0034), confirmed under the corrected protocol (YB-0035); first such result in this program' |
| F8 | Organism false-alarm rate 10.12% > 10% cap | auditor | FIXED-YB-0035 (tightest threshold with <= 10%) |
| F9 | False alarms among monitorable episodes unreported (16.6%) | auditor | FIXED-YB-0035 (reported) |
| F10 | Bootstrap CIs ignored threshold uncertainty | auditor | FIXED-YB-0035 (all episodes resampled, thresholds re-set) |
| F11 | Analysis code committed with results, not before | auditor | PROCESS: YB-0035 code + dry run committed before seed 7 (b6c795b); DOC disclosure for earlier experiments |
| F12 | YB-0019 '≈302 features' (actual 314); unregistered metric and extrapolation change | auditor, self | DOC: count corrected; deviations listed |
| F13 | YB-0030 called pre-registered (4 minutes before results, on thrice-used data); V6 changed | auditor | REWORD: retrospective; DOC the V6 change |
| F15 | YB-0031 H5 'failure to settle confirmed' driven by one question type | auditor rerun | REWORD: weekday-specific; within-type tests reported |
| F16 | Length and question-type baselines match or beat pre-YB-0033 organisms | auditor rerun | DOC + ARTIFACT (archive/audit/artifacts/): on seed 1, length (0.796) exceeds YB-0012 (0.72), YB-0019 (0.765) and YB-0030 (0.725); question type (0.764) exceeds YB-0012 and YB-0030 and roughly matches YB-0019 (corrected per fifth audit A3); YB-0031 0.89 exceeds type 0.80 and length 0.73 |
| F17 | YB-0009 topology features include n_windows (a length proxy) | auditor rerun | OPEN (backlog) rerun without it; DOC |
| F18 | YB-0018 'substrate' entropy includes answer tokens; Proposition 2 false | auditor | RETRACT Proposition 2; OPEN (backlog) re-window |
| F19 | YB-0017 'variance 9-10x lower' is a CV ratio (≈3.7x above rest); drive correlates with length | auditor rerun | REWORD; DOC |
| F20 | '290 ns/token' attributed to competing organisms (they cost 2-4 ms) | auditor | REWORD + ARTIFACT (timing script) |
| F21 | YB-0032 length control not reproducible (0.578 does not reproduce) | auditor, self | ARTIFACT: archive/audit/artifacts/baselines_and_breakdowns.py reproduces 0.773, 15/46 and 0.578, 11/46 (our definition: derivation-correct percentile by type) |
| F22 | YB-0002 detection claims at unmatched false-positive rates | auditor rerun | REWORD; OPEN (backlog) matched comparison |
| F23 | RESEARCH_PROGRAM: 'behavior is not predictive', 'unjailbreakable by construction' | auditor | REWORD: update through YB-0035; 'text-blind' kept, 'unjailbreakable' dropped (untested) |
| F24 | Novelty claims without related work (hidden-state error prediction literature) | auditor | DOC: related-work section |

## Minor
| ID | Finding | Resolution |
|---|---|---|
| F14 | YB-0031 H4 used a test-set threshold; 'silent slip' defined by question type only | DOC deviation; per-category false alarms reported |
| F25 | 'Below chance' confidence claim cited with a CI that includes 0.5 | REWORD: cite YB-0031 0.366 [0.304, 0.433] |
| F26 | 'Perfectly ordered' levels rest on groups of 17, 8, 2 | REWORD |
| F27 | 'Better than the judge at every checkpoint' (no CIs; reverses at t=384 in YB-0034) | REWORD; CIs OPEN (backlog) |
| F28 | Lead time at best, not first, crossing | FIXED-YB-0035 |
| F29 | Live compute timing made in-time status non-deterministic | FIXED-YB-0035 (fixed 5 ms cost) |
| F30 | Judge prefixes re-tokenized from text | FIXED-YB-0035 (exact token ids, seed 7) |
| F31 | Compute ratios exclude tap cost; wall-clock not compute | REWORD |
| F32-F34 | YB-0001/0002/0017 theorem wording and test coverage | REWORD; tests OPEN (backlog) |
| F35 | YB-0019 Proposition 3 test does not check the exact statement; features numerically fragile | DOC; OPEN (backlog) exact-case test and sensitivity |
| F36 | Missing LEDGER rows (YB-0003, 0022, 0034); YB-0022 test only greps a file; wrong checkpoints in HYPOTHESES | DOC + PROCESS |
| F37 | '9x more data' (10x); V8 points dropped from explanations; methodology 0-21 vs 0-24 | DOC; code fix OPEN (backlog) |
| F38 | '6x larger judge' (5.6x total, 1.4x active parameters) | REWORD |

## Found by us (self)
| ID | Finding | Resolution |
|---|---|---|
| S1 (F39) | Greedy generation is deterministic within a session but diverged across sessions for ~40% of episodes (likely GPU sharing during the seed-2 recording) | REWORD 'token-reproducible' claims; PROCESS: record alone; log environment |
| S2 | '720/720 token-identical' was asserted before being checked (true when later checked: 480/480 + 240/240) | PROCESS: no verification claim before the check |
| S3 | Per-type 'struggle 10/12 vs slips 0/9' (YB-0012) computed ad hoc, never saved | ARTIFACT: same script reproduces 10/12 struggle and 0/9 slips |
| S4 | Pre-registration folders copied with full Makefiles broke CI (YB-0034); local checks did not mirror CI | PROCESS: YB-0035 experiment exits cleanly when data is absent (done); local check to mirror CI (Phase D) |
| S5 | Blog draft repeats F1, F3, F23, F38 and 'every experiment is public' | Phase E: rewrite from the corrected record |
| S6 | The telemetry synchronization test used an arbitrary cap (0.15) that the 4-bit, 128-expert second model exceeds while clearly synchronized | PROCESS: criterion replaced for both models by the property itself (every reading closer to its own token than to the neighbour; median error below 0.10); both pass |

## Second audit (2026-09-30): YB-0035 and the blog drafts

Independent, read-only audit of YB-0035 and both blog drafts (archive/audit/yb0035_blog_audit_2026-09-30.md): 25 findings (2 critical, 10 major, 13 minor). It found no leakage in YB-0035 and recomputed its key counts; the problems were in interpretation. Findings B1, B6, B7, B9 and B20 were verified independently before any change.

| ID | Severity | Finding | Verified | Resolution |
|---|---|---|---|---|
| B1 | critical | Blogs: watching words cannot tell you when to worry; more reliable than the judge | YB-0031 results: judge 0.947, self-consistency 0.982 vs regulator 0.890 on finished answers (checked) | REWORD: claim limited to before the answer exists, under a deadline; on finished answers self-consistency is more accurate and the judge was not distinguishable from an earlier regulator (corrected per third audit M4) |
| B2 | critical | Blogs: confident wrong answers | YB-0035 never measures confidence (checked) | REWORD: wrong answers |
| B3 | major | Blogs: warnings come earlier | Median seconds to spare favour the judge on seeds 5 and 6 | REWORD: earlier dropped |
| B4 | major | Plain blog: each test set brand new and used once | Seeds 5 and 6 reused from YB-0033/34 | REWORD: only seed 7 is fresh |
| B5 | major | Pooled estimate presented as the headline | Two of three sets already known positive; mixed judge inputs | DOC: seed 7 leads; pooled descriptive (this file, YB-0035 README, RESEARCH_PROGRAM, LEDGER) |
| B6 | major | 10% cap set on test answers; monitorable false alarms unequal (16.3/11.0/10.3%) | Recomputed from results.json (checked) | ARTIFACT: YB-0035 tests/exploratory_audit2.py: equal monitorable false alarms 19 vs 11, +0.20 [+0.02, +0.43]; frozen derivation threshold 22/40 |
| B7 | major | Technical blog: first audit 3 critical, 23 major, 12 minor | Audit file severity column: 3 / 20 / 15 (checked); repo documents not affected | FIX in blog |
| B8 | major | Technical blog: regulator beats question-type baseline | No such baseline in YB-0035 | ARTIFACT: type baseline C3 catches 6/40; regulator minus type +0.43 [+0.19, +0.63] |
| B9 | major | Resynchronization verified on 6 episodes by an uncommitted script | Confirmed: script missing; committed log showed 8/20 mismatches | ARTIFACT: agr/verify_shift.py: 11/20 identical-text episodes, median error 0.012 vs 0.81 SD (shift vs none), better in 11/11, worst single reading 2.8 SD |
| B10 | major | Per-checkpoint AUROC only for seed 7, no CIs; could reflect predicting eventual length | Seed 6 t=384: regulator 0.530 vs judge 0.607 | OPEN: all seeds with CIs; limitation stated |
| B11 | major | Plain blog: graded warnings | The winner is a binary-thresholded logistic model; AI-EWS v4 did not beat length | REWORD |
| B12 | major | Technical blog: robustly supported | One model, one checkpoint set, one machine | REWORD: supported on the pre-registered test set |
| B13 | minor | Faster serving would help every monitor | Only behavior monitors would benefit | REWORD |
| B14 | minor | Structural blind spot generalized from one model, no base rate |  | REWORD |
| B15 | minor | More than 90% confidence misquotes YB-0015 | Source: at least 0.9 on every answer token | REWORD |
| B16 | minor | No power difference; same work per word | Power result is not detectable (AUROC 0.40); mechanism retracted (F18) | REWORD |
| B17 | minor | Judge about 1.5 to 2 s, no artifact |  | ARTIFACT: archive/audit/artifacts/judge_timing.py: seed 7 median 1.55 s, 90th percentile 7.2 s |
| B18 | minor | First result beating behavior attributed to YB-0035 | YB-0033 met it first | REWORD per F7 |
| B19 | minor | Before the questions exist; confirmed on GitHub | Questions are seed-determined; it was the recordings that did not exist | REWORD |
| B20 | minor | Recorded alone; launch wrapper uncommitted | Guard added later; no contention logged | ARTIFACT: agr/start_seed7_after_push.sh (byte-identical); REWORD: no concurrent jobs logged, guard added afterwards |
| B21 | minor | Alignment pass criterion changed after seed 7 | Logged as S6 | DOC: disclosed next to the second-model claim |
| B22 | minor | YB-0035 README: result got firmer | Seed-7 lower bound vs judge +0.049 is below YB-0034 +0.070 | REWORD: held |
| B23 | minor | Related work incomplete | Burns 2023; Kuhn, Gal and Farquhar 2023; Bailey 2024 missing | DOC: add (blogs; RESEARCH_PROGRAM OPEN) |
| B24 | minor | Task list omits one type; uneven error distribution |  | DOC: all six types; per-type breakdown OPEN |
| B25 | minor | I verified every critical finding myself | Verification was done by the AI research assistant under the author's direction | REWORD |

## Third audit (2026-09-30): the v2 blog drafts

Independent, read-only audit of the two v2 drafts (archive/audit/blog_v2_audit_2026-09-30.md): no invented numbers found;
1 critical, 9 major, 20 minor findings on verifiability, attribution, provenance and wording. All resolved (rows below); blog wording applied in v3, re-audited in the fourth audit.

| ID | Severity | Finding | Verified | Resolution |
|---|---|---|---|---|
| C1 | critical | Posts claim the protocol was committed before the test recordings existed, but the repository is private and git times are author-set | GitHub server records: push of b6c795b at 2026-09-30T15:26:40Z, CI run at 15:26:42Z; first seed-7 episode 15:26:49.96Z (Mac clock, offset -1.2 ms vs Apple time server when checked). Ordering holds; the margin is about 10 s, not the 4 min implied by the local commit time | ARTIFACT: archive/audit/artifacts/c1_github_server_timestamps.json. REWORD (blogs): cite GitHub server time and the ~10 s margin; state that the code, data, reports and corrections are public (YobieBenjamin/autonomic-graph-regulation) and the commit history that timestamps the pre-registration is private and available to reviewers on request. PROCESS: protocol rule 13 (public cryptographic timestamp of every pre-registration hash at commit time) |
| M1 | major | Plain draft: cannot be sweet-talked (reintroduces the retracted unjailbreakable claim) | CORRECTIONS F23; activations depend on input text | REWORD in v3: cannot be argued with directly; whether crafted inputs can fool it is untested |
| M2 | major | Plain draft presents exploratory checks (type baseline, equal false alarms, frozen threshold) as part of the planned design | exploratory_audit2.json marks them EXPLORATORY | REWORD in v3: labeled as added afterwards |
| M3 | major | Technical conclusion blends pre-registered and exploratory results; frozen-threshold check has no judge arm or interval | exploratory_audit2.py docstring; regulator 15.0% monitorable false alarms | REWORD in v3 |
| M4 | major | 0.890 is an earlier, pre-fix regulator and its gap to the judge was not significant; repository inconsistent | YB-0031: deep minus judge -0.057 [-0.131, +0.012], not distinguishable; minus self-consistency -0.092, inferior (checked) | FIX: CORRECTIONS header and B1, RESEARCH_PROGRAM, LEDGER, YB-0035 README corrected; REWORD in v3 |
| M5 | major | Regulator also receives question type and elapsed tokens (normalization per type and checkpoint) | src/absrace.py key = (cat, t) (checked) | DOC: YB-0035 README, RESEARCH_PROGRAM, GLOSSARY text-blind entry; ARTIFACT: type-by-length baseline 9/40 (docs/exploratory_audit3.json); REWORD in v3 |
| M6 | major | Posts omit the pre-registered race the regulator lost (YB-0031: 4 vs 12 of 47) and the rejected YB-0032 design | YB-0031 results (checked) | DOC: RESEARCH_PROGRAM design history; REWORD in v3 |
| M7 | major | Posts do not disclose that code, experiments and drafts were largely AI-written, or that all audits were AI sessions | README model-written code note | DOC: README.md Authorship and AI assistance; REWORD in v3 |
| M8 | major | Closest prior work (early detection of reasoning non-convergence from hidden states, arXiv 2607.21433) not cited; novelty overstated | RESEARCH_PROGRAM related work lists it | REWORD in v3 |
| M9 | major | Re-ran the key experiment from scratch overstates: only seed 7 was newly recorded | YB-0035 PREREGISTRATION | REWORD in v3 |

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
| m1 | minor | judge size stated as total parameters only | checked | REWORD: 5.6x total, 1.4x active (model card, artifact model_sizes.json) |
| m2 | minor | self-consistency 0/40 near-guaranteed by design; timing uncommitted | checked | ARTIFACT exploratory_audit3.json (median 5.8 s); REWORD |
| m3 | minor | exactly the same false-alarm rate | checked | REWORD: about the same |
| m4 | minor | frozen threshold false-alarm rate omitted | checked | REWORD |
| m5 | minor | 600 questions without the answered count | checked | REWORD: 535 answered |
| m6 | minor | length works just as well (it did better, 74 vs 68) | checked | REWORD |
| m7 | minor | lag bug implied critical (it was major) | checked | REWORD |
| m8 | minor | confidence wording (inverted, not useless; one model) | checked | REWORD |
| m9 | minor | firm conclusion from the small power null | checked | REWORD: points toward |
| m10 | minor | synchronization test scope | checked | REWORD |
| m11 | minor | shift verification scope (seed 2; likely cause) | checked | REWORD |
| m12 | minor | 5 ms fixed vs 4.1 ms measured excluding recorder overhead | checked | REWORD |
| m13 | minor | per-checkpoint sample sizes missing | checked | ARTIFACT seed7_counts.json; REWORD |
| m14 | minor | YB-0033/34 ran under the since-corrected protocol | checked | REWORD |
| m15 | minor | launch script committed after the fact | checked | DOC |
| m16 | minor | 25 findings mostly, not only, interpretation | checked | REWORD |
| m17 | minor | offline replay, not live race | checked | REWORD |
| m18 | minor | strongest vs most stringent | checked | REWORD |
| m19 | minor | effectors not built | checked | REWORD |
| m20 | minor | all errors from four of six types | checked | ARTIFACT seed7_counts.json; REWORD |

## Fourth audit (2026-10-01): the v3 blog drafts

Independent, read-only audit of the v3 drafts with access to the public snapshot (archive/audit/blog_v3_audit_2026-10-01.md). All numbers verified against committed files; no leakage or post-registration changes. 1 critical, 5 major, 17 minor findings. IDs prefixed D4- to avoid collision with the third audit.

| ID | Severity | Finding | Verified | Resolution |
|---|---|---|---|---|
| D4-K1 | critical | Posts said the full record is public; the commit history (incl. b6c795b) is private | Public snapshot has 1 commit (checked) | REWORD (author decision): the code, data, reports and corrections are public; the commit history that timestamps the pre-registration is private and available to reviewers on request |
| D4-M1 | major | Recording start time is self-reported (local clock); clock offset checked about 10 h later | c1 artifact retrieved 01:33Z; recorder uses time.time() | REWORD: disclose; rule 13 addresses future experiments |
| D4-M2 | major | Third-audit minors not logged; C1 row outdated | checked | FIX: logged above; C1 updated |
| D4-M3 | major | LEDGER rows still stated retracted claims | 9 rows (checked) | FIX: correction notes appended, original text preserved |
| D4-M4 | major | Confidence wording (inverted signal carries information; from YB-0031) | YB-0031 0.366 [0.304, 0.433] | REWORD |
| D4-M5 | major | No standard hidden-state probe baseline | YB-0035 monitor list (checked) | DOC: limitation stated; experiment YB-0042 added to the backlog |
| D4-m1..m17 | minor | Audit count, rule count, verification attribution, which regulators the baselines beat, frozen-threshold false alarms, fixed vs measured cost, judge-vs-regulator wording, simulation wording, Qwen design class, book status, novelty caveat, judge settings, sync-test detail, resynchronized counts, model-size source, license scope for replication, full reference for arXiv 2607.21433 | checked | REWORD in v4; ARTIFACT model_sizes.json |

## Fifth audit (2026-10-01): the v4 blog drafts

Independent, read-only audit (archive/audit/blog_v4_audit_2026-10-01.md). Verdict: both drafts publishable with listed fixes. Seed-7 timeline consistent (push 15:26:40Z; alignment log 15:26:48Z; recorder start 15:26:49.955Z); no leakage; public snapshot verified; citation verified. 1 major, 10 minor findings, IDs prefixed D5-.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| D5-A1 | major | Posts said audits were told nothing about earlier findings; audits 2-4 could and did read them | REWORD v5: fresh, read-only sessions, separate from the work; later audits could read earlier findings |
| D5-A2..A11 | minor | Audit count; YB-0019 matched (not failed) the type baseline; reused seeds labelled; low reasoning effort of the monitored model; expert-count source; false-alarm footnote; single judge configuration (weak early); Part II without Part I; AI audits not unforgiving; full reference missing from the record | REWORD v5; FIX F16 wording; ARTIFACT model_sizes.json (experts); DOC RESEARCH_PROGRAM full reference |

## Self-found (2026-10-01)

| ID | Finding | How found | Resolution |
|---|---|---|---|
| S7 | The YB-0042 chain publish committed 4,810 raw per-episode recordings (about 466 MB) under data/agr: new filenames were not covered by .gitignore | Found by the three-copy verification before any public upload completed (public stayed at b7d526d) | FIX: untracked (files kept locally and in private history; packed copies under algorithms/YB-0042-probe-baseline/data are the record); .gitignore extended; snapshot pipeline now aborts on raw recordings |

## Sixth audit (2026-10-01): the v6 blog drafts, including the first audit of YB-0042 and the NVIDIA section

archive/audit/blog_v6_audit_2026-10-01.md: 1 critical, 8 major, 11 minor. Numbers verified; YB-0042 code unchanged between pre-registration and results.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| D6-C1 | critical | Public repo lacked YB-0042 when audited | Resolved: snapshot b2c7a50 (from a025fca) includes YB-0042; re-cut after YB-0045 adds the timestamp proofs |
| D6-M1 | major | Internal-state monitoring as a class overclaimed; early AUROC comparison descriptive and unpaired | FIX: RESEARCH_PROGRAM claim status; REWORD v7 |
| D6-M2 | major | Seed-8 length comparison degenerate (0/40 under the monitorable cap); probe comparisons have no interval | REWORD v7 |
| D6-M3 | major | Technical draft omits the race the regulator lost (YB-0031) and the rejected YB-0032 design | REWORD v7 |
| D6-M4 | major | YB-0042, the probe conclusion and the NVIDIA section had not been audited before | This audit covers them; v7 states six audits |
| D6-M5 | major | "blind" contradicts D5-A1 | REWORD v7 |
| D6-M6 | major | README audit description stale (three audits, no knowledge of earlier findings) | FIX: README |
| D6-M7 | major | NVIDIA facts lacked a committed source | DOC: docs/sources/nvidia_open_agent_safety_platform.md; attribution in v7 |
| D6-M8 | major | YB-0042 OpenTimestamps proof pending when audited | Resolved: proof complete (Bitcoin-anchored), committed in 4a3da80; RFC 3161 tokens added |
| D6-m1..m11 | minor | Four-layer wording; which audit verified F2; contention windows; YB-0042 training-size description; seed-8 counts; "clearly"; base rate for correct answers; quantized build; theorem-test coverage; CITATION.cff pointed to the private repo; GitHub timestamps retrieved by the author | FIX: YB-0042 README, CITATION.cff, ARTIFACT derivation_sizes.json; REWORD v7 |

## Seventh audit (2026-10-01): the v8 blog drafts, the first audit of YB-0045

archive/audit/blog_v8_audit_2026-10-01.md: 1 critical, 7 major, 7 minor. Every figure verified; YB-0045 analysis code unchanged since pre-registration 682f373.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| D7-C1 | critical | Public snapshot lacks YB-0045, docs/sources, rule 13 and timestamp proofs (repeat of D6-C1) | Re-cut after these fixes and verified on GitHub before posting |
| D7-M1 | major | Public YB-0042 OpenTimestamps proof was the unfinished one | Fixed by the re-cut (complete proof committed in 4a3da80) |
| D7-M2 | major | YB-0045 OpenTimestamps proof pending; timeline of the RFC 3161 tokens not stated | FIX: proof upgraded (complete, 4 Bitcoin attestations); REWORD: OTS 14:53Z, RFC 3161 15:45Z (after derivation recording began at 15:14Z, before the first test recording at 18:59Z) |
| D7-M3 | major | No audit had reviewed YB-0045 | This audit covers it; REWORD |
| D7-M4 | major | "At every checkpoint" overstated; equal-false-alarm and frozen-threshold results lack intervals | FIX RESEARCH_PROGRAM; REWORD v9 |
| D7-M5 | major | Probe compute cost assumed (5 ms), never measured | DOC + REWORD |
| D7-M6 | major | "Solid ground" overstated | REWORD |
| D7-M7 | major | Seed 7 called the main result while YB-0045 carries the conclusion | REWORD |
| D7-m1..m7 | minor | Per-seed sums (only the judge differs); older regulator in the offline comparison; YB-0045 monitorable false-alarm rates; power figures without an artifact; 24x is versus one layer; 100+ partners from secondary outlets; comma splice | ARTIFACT tests/power.py + docs/power.json; REWORD v9 |

## Eighth audit (2026-10-02): the v10 blog drafts, first audit of YB-0044; two independent auditors

**Claude** (fresh read-only session with repository access; archive/audit/blog_v10_audit_claude_2026-10-02.md): 3 critical, 8 major, 12 minor; every number verified by recomputation.
**GLM-5.3-flash** (Z.ai; first non-Claude auditor; given the drafts plus an evidence bundle of committed results, no repository access; archive/audit/glm_audit.py, glm_audit_prompt_v10.txt, blog_v10_audit_glm_2026-10-02.json, blog_v10_audit_glm_response.json): 86 claims checked, 71 verified, 15 findings (1 major, 14 minor); no wrong number found.
**How GLM was run:** LM Studio could not load the local GGUF (unknown architecture glm5next in llama.cpp 2.14.0, latest stable and beta); run 1 via the Z.ai API returned an empty answer because 17,908 reasoning tokens (that count is from run 2; the run-1 cause is inferred) exceeded its 16,000-token budget (confirmed from run 2 usage); run 2 (reasoning effort high, 40,000-token budget) completed.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| D8-C1 | critical | YB-0044 results untracked and not public | FIX: committed; snapshot re-cut; cited paths verified on public GitHub |
| D8-C2 | critical | Frozen-sandbox story not in the committed record | DOC: incident in docs/OPENSHELL_SETUP.md with caveat (logs not retained); claim cut from posts |
| D8-C3 | critical | Arm C 93 of 93 fixed by design; H1 nearly guaranteed | REWORD: posts lead with arm B (74 of 93 lost) and arm C costs; README and claim status note it |
| D8-M1 | major | Live enforcement latency wider than isolated; possible leftover blocks | ARTIFACT docs/supplementary.json: re-counting 4 short-gap wins as losses gives 83.9% [76.3%, 91.4%]; disclosed |
| D8-M2 | major | Live start time not verifiable | ARTIFACT docs/mock_service_log.jsonl and supplementary.json: first start 14.1 s after the RFC 3161 stamp |
| D8-M3 | major | Arm C stalls unreported; timeout cause inferred | DOC: 7 stalls over 60 s (largest 754 s) disclosed; cause not established |
| D8-M4 | major | No audit had covered YB-0044; blind; README count | REWORD; README now points to CORRECTIONS for counts |
| D8-M5 | major | Plain draft restated the retracted unjailbreakable claim | REWORD |
| D8-M6 | major | Public timestamps not before every test | REWORD: from the second test on |
| D8-M7 | major | Cited file still stated retracted claims | FIX: retraction banners in RESEARCH_PROGRAM, PROJECT_HISTORY, HYPOTHESES; Bailey et al. 2024 added |
| D8-M8 | major | Overstated as plugged into NVIDIA platform; regulator not live | REWORD: replay through open-source OpenShell; no model in the loop; no Sentry or BlueField |
| D8-m1..m12 | minor | Every-action wording; regulator-minus-probe label; AUROC source; frozen threshold scope; sixth task type; 1.4x active; post hoc label; 93 is the regulator; CORRECTIONS row for the population mismatch (see YB-0042 README deviation 1); 5 ms vs 4.1 ms; vendor claims; proofs | REWORD; proofs committed |
| D8-G2 | minor | Interval-separation claim did not name the pair (false for regulator vs probe) | REWORD (missed by Claude) |
| D8-G10 | minor | About 20 ms per token unsupported; measured median 14.4 ms over 442,306 tokens | FIX + ARTIFACT archive/audit/artifacts/token_timing_and_width.json (missed by Claude) |
| D8-G4, G7, G9 | minor | Stricter-rule claim unexplained; 2,880 width uncited | REWORD; width confirmed (2,880; ratio 24.0) in the same artifact |
| D8-G1, G3, G5, G6, G8, G11..G15 | minor | Items outside the evidence bundle, or already fixed in v11 | No change needed (verified in the repository by the Claude audit) or already fixed |

## Ninth audit (2026-10-03): the final drafts (LinkedIn plain-English version and technical v11); three auditors, three companies

**Claude** (repository access; archive/audit/final_audit_claude_2026-10-03.md): every number verified; P1 critical; P2-P5, T1-T3 major; 16 minor.
**GLM-5.3-flash** (Z.ai; evidence bundle; archive/audit/final_audit_glm_2026-10-03.json): publishable with fixes; 74 checked, 64 verified; 1 major (same sentence as Claude P4), 9 minor bundle gaps; no wrong number.
**gpt-oss-120b** (OpenAI open-weight, local; same prompt and bundle; archive/audit/final_audit_gptoss_raw.txt): returned malformed JSON (recovered leniently); verdict not publishable; 57 checked, 22 verified; most findings incorrect (for example, called the probe count of 100 unsupported and an AUROC below 0.5 not below chance). **Not independent:** it is the judge in the experiments and wrote some code. Only findings confirmed against the files were adopted (93 vs 94; median for the 7.4 s delay), both also raised by Claude.
Prompt and bundle: archive/audit/multi_audit.py, multi_audit_prompt_final.txt.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| D9-P1 | critical | Plain draft stated as fact that the model said 2 + 2 = 5 (fabricated) | FIX: replaced with a real error type (a big multiplication) |
| D9-P2 | major | Can-not-talk-its-way-past restated the retracted unjailbreakable claim (D8-M5 lost in rewrite) | REWORD with the untested caveat |
| D9-P3 | major | 1.4x active-parameter caveat missing (D8-m6 lost) | FIX |
| D9-P4 | major | Three-times claim per test set overstated (2.5x, 2.9x, 2.6x; post hoc) | REWORD |
| D9-P5 | major | Are-you-sure claim untested; self-consistency works on finished answers | REWORD: does not work as a brake |
| D9-T1 | major | Gates list contradicted the model-cannot-be-a-gate claim | REWORD: second opinion yes, control of its own actions no |
| D9-T2 | major | H2 direction largely foreseeable from pre-registered files | DISCLOSED: 68 of 93 gaps (73.1%) under 5.47 s in the plan (verified) |
| D9-T3 | major | Unaware-error ERN attributed to Gehring 1993 | FIX: Nieuwenhuis et al. 2001; source Dehaene et al. 1994 |
| D9-minor | minor | Hyperdirect hedge (Nambu 2002); literally race; brake speed; Damasio year; 93 vs 94; connected wording; lands on nobody; exactly the same confidence; 90% caveats; gpt-oss code role; review-gate untested; YB-0035 judge timing label; NVIDIA architecture wording; list numbering; full path; audit count | FIX or REWORD |

## Citation verification (2026-10-03)

Every literature citation in the published posts (32, including three added during the check) was verified against a primary source: DOI, publisher, PubMed or PMC, arXiv, proceedings, or the issuing body. Registry with URLs and access level: docs/sources/CITATIONS.md. 31 verified at abstract or full-text level; 1 (Dehaene, Posner and Tucker 1994) at record level via citing literature.

| ID | Finding | Resolution |
|---|---|---|
| CV-1 | Kadavath et al. 2022 shows self-evaluation partly works; thesis called self-policing an architectural category error | REWORD: acknowledge Kadavath; narrower claim (model cannot be the control on its own actions) |
| CV-2 | Wang et al. 2022 proposed self-consistency for accuracy, not detection | REWORD: adapted as a disagreement signal |
| CV-3 | Byrnes cited without year; a blog series | FIX: Byrnes, 2022, blog series |
| CV-4 | flexHEG cited without authors | FIX: Petrie and Aarne, 2025 |
| CV-5 | Sparrow 2007 presented without its critics | ADD: Champagne and Tonkens 2015; Robillard 2018 (both removed from the series 2026-10-04, full text unavailable; see CITATIONS.md) |
| CV-6 | ERN 100 ms timing not in the Gehring 1993 abstract | ADD: Yeung, Botvinick and Cohen 2004 |
| CV-7 | Orgad et al. 2024: hidden-state detectors generalise poorly | ADD to limitations |
| CV-8 | Sentry is a reference design, not a shipping product | REWORD |
| CV-9 | Ninth-audit fixes confirmed by primary sources: Nieuwenhuis 2001 (unaware errors), Aron and Poldrack 2006 full text (hyperdirect stop not established) | Confirmed (Nieuwenhuis later removed from the series 2026-10-04, full text unavailable; Aron direct-read evidence added to fulltext_verification.json) |

## Tenth audit (2026-10-04): Audit 1 of the final two-part series, Claude Opus 5.5 against the repository

Report: archive/audit/final_series_audit1_opus_2026-10-04.md. Verdict: publishable with fixes; no critical findings; every experimental number matched a committed file (YB-0044 recomputed from per-episode files); all 22 public paths exist.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| A10-T1 | major | Yeung 2004 registry URL returns 404 to readers; claims beyond timing unrecorded | FIX: DOI as primary URL; registry records the five claims read in the full text on 2026-10-04 |
| A10-T2 | major | Registry listed Logan, Farquhar, Chiba below full text although read in full | FIX: registry rebuilt with true access levels; 11 non-full-text papers moved to a not-cited list |
| A10-R1 | major | Full-text verification evidence uncommitted; registry and evidence disagreed on Aron and Yeung | FIX: fulltext_verify.py, fulltext_verification.json, sort_inbox.py and the inbox README committed (PDFs git-ignored); Aron and Yeung recorded as read directly |
| A10-P1..P4 | minor | Per-seed range applied to regulator only; gpt-oss-120b non-independence missing in Part 1; four pre-registered experiments not three; leftover "AI cannot be one of them" | FIX |
| A10-T3..T15 | minor | Unsourced critics clause; Byrnes revision date; unattributed Swiss cheese name; compute-cost wording; first fresh test wording; arm A computed; ninth audit covered previous drafts; Fixed vs Disclosed; timestamps from YB-0042 on; 1,031 reached a checkpoint; four deviations; power figures; YB-0015 link | FIX or REWORD |
| A10-R2..R8 | minor | Audit counts, YB-0042 deviation count and count discrepancy, stale research-program lines, NVIDIA attribution, run-1 token count, stale audit-script text | FIX (R3 documented, cause not established) |
| A10-R9 | minor | Posted drafts untracked | FIX: archive/audit/series_final_2026-10-04/ committed |

## Eleventh audit (2026-10-04): Audit 2 of the final series, three auditors from three companies at once

Prompt: archive/audit/series_audit2_prompt.txt. Reports: series_audit2_fable_2026-10-04.md (Claude Fable 5.1, repository access), series_audit2_gpt55_2026-10-04.md (GPT-5.5 via OpenAI Codex CLI on the ChatGPT subscription, repository access, session record confirms model gpt-5.5), series_audit2_glmmed_2026-10-04.json (GLM-5.3-flash, Z.ai, evidence bundle, low reasoning effort; the high-effort run had not returned after 45 minutes).

Verdicts: all three publishable with fixes. Fable: 0 critical, 0 major; recomputed YB-0044 and YB-0045 from raw files; all 28 public paths exist; all Audit 1 fixes landed except one partial. GPT-5.5: 0 Part 1 findings; 2 major on the evidence chain. GLM: 78 checked, 66 verified, 13 minor.

| ID | Source | Finding | Resolution |
|---|---|---|---|
| A11-1 | GPT-5.5 T1/R1 | Aron and Yeung recorded as FETCH_FAILED in the committed evidence while the registry says read in full | FIX: direct-read passages with pages added to fulltext_verification.json |
| A11-2 | GPT-5.5 T2 | Retracted cannot-be-jailbroken wording still in docs/RESEARCH_PROGRAM.md, which Part 2 cites | FIX: text-blind by construction; telemetry attacks untested (F23) |
| A11-3 | Fable P1/T1 | Audit count stale (nine) | FIX: eleven, with tenth and eleventh summarised in Part 2 |
| A11-4 | Fable T2 | Thirteen process rules each traced to a finding (only seven are) | FIX |
| A11-5 | Fable R1-R4 | CV-5 and CV-9 reversals unnoted; stale script header; two attributions for the millisecond claim; audit files untracked | FIX (Fable R2 claim that gpt-oss-120b never ran in LM Studio is incorrect; it did) |
| A11-6 | GLM G1 | just released (OpenShell) loosely dated | FIX: recently released |
| A11-7 | GLM G2-G12 | Eleven figures not in its bundle | NO CHANGE: each present in the repository and recomputed by Fable and Opus |
| A11-8 | GLM G13 | arXiv:2607.21433 possibly fabricated | NO CHANGE: real (read in full; confirmed live by Fable) |

## Voice edit (2026-10-04): final series, author voice pass, no factual change

At the author request, both parts were rewritten to remove AI-style phrasing (stock setups, colon reveals, tidy triplets, it-is-not-X-it-is-Y closers) and restore his irreverent voice. Facts, numbers, intervals, citations and file paths were held fixed. Verification: an automated comparison of every number in the before and after text found none removed and none added except the series markers (Part 1 of 2; a reference to Part 1). The posted drafts in archive/audit/series_final_2026-10-04/ are the voice-edited versions; the audited pre-edit versions remain in git history (commit 6020c80).

## Process findings (2026-10-04, YB-0046 to YB-0048)

| ID | Finding | Resolution |
|---|---|---|
| PF-1 | The publish pipeline re-runs experiments; for analyses whose test data already existed it would have run the confirmatory analysis before the timestamp | Gated behind make confirmatory; verified in the sandbox and during the live publish (PROTOCOL rule 14) |
| PF-2 | YB-0047 dry run crashed after 30 minutes on infinite scores for never-monitored episodes | Lowest-score rule written into the plan before the timestamp; smoke mode added (rule 15) |
| PF-3 | Code review found the leave-one-task-out test would feed the held-out type unscaled features, biasing it against internal state | Label-free normalisation from the held-out type's derivation episodes, written into the plan before the timestamp (rule 17) |
| PF-4 | A waiting script would have re-timestamped YB-0046 after its analysis started | Stopped before it could; single timestamp taken before analysis (rule 16) |
| PF-5 | Hard-linked data copies were tracked in git, doubling uploads; the public snapshot push failed | Copies untracked (hash-identical to YB-0045 data, which remains the public record); failed snapshot commit discarded (rule 17) |
| PF-6 | The audited final series drafts overstate what internal state adds (YB-0047) | Marked superseded (archive/audit/series_final_2026-10-04/SUPERSEDED.md); claim status updated in docs/RESEARCH_PROGRAM.md |
| PF-7 | YB-0047 pooled transfer AUROC mixes cross-task miscalibration with ranking | Pre-registered measure reported as is; within-task held-out AUROC reported alongside |
