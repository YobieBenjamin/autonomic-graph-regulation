# Corrections log

**Outcome of the deep debug (2026-09-30; revised after the second audit).** All critical findings were independently verified. The real-time result was re-run under a corrected protocol (EXPERIMENT-CORRECTED-REALTIME-RACE, code committed before its test data existed). On the only fresh test set (seed 7), before the answer exists, the regulator raised in-time warnings on 23 of 40 wrong answers vs 11 for the LLM judge and 9 for the length control (+0.30 [+0.049, +0.487] vs the judge). Exploratory checks after the second audit: with false alarms equalized among monitorable episodes, 19 vs 11 (+0.20 [+0.02, +0.43]); with a threshold frozen from training data, 22 of 40. Seeds 5 and 6 (reused test sets) agree; their pooled estimate is descriptive only. Boundaries: on finished answers, an earlier pre-fix regulator (0.890, EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM) was significantly less accurate than self-consistency (0.982) and not distinguishable from the LLM judge (0.947; difference -0.057 [-0.131, +0.012]); with never-answered episodes counted as failures, the regulator is no better than length. Pre-EXPERIMENT-CLEAN-REALTIME-RACE accuracy claims did not beat question-type or length baselines (REVIEW-BASELINES-BEAT-EARLY-ORGANISMS). Terminology from here on follows docs/GLOSSARY.md (e.g. regulator = organism).

Every error found in this repository, who found it, how it was verified, and how it was resolved. Nothing is silently
edited: a correction changes the affected document **and** is recorded here. Sources: the independent audit
(`archive/audit/independent_audit_2026-09-30.md`, a separate read-only Claude Code session at commit fc575cf), our
own verification (Phase A of the deep debug), and our own findings (marked *self*).
Resolution codes: **FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE** (corrected in the re-run experiment), **RETRACT** (claim withdrawn), **REWORD**
(claim qualified), **ARTIFACT** (missing script or data added), **DOC** (documentation fix), **PROCESS**, **OPEN (backlog)**.

## Critical
| ID | Finding | Verified | Resolution |
|---|---|---|---|
| REVIEW-FLAGSHIP-EARLINESS-CLAIM-RETRACTED | EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP 'alarms 4.5 s before the answer, 100% of detections': the online alarm fires on 89.3% of correct answers at the first check (93.9% at any check); the lead is reasoning length | Phase A rerun (exact) | RETRACT the earliness claim; superseded by matched-false-alarm races (EXPERIMENT-CLEAN-REALTIME-RACE/34/35) |
| REVIEW-DEEP-EARLINESS-CLAIM-RETRACTED | EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM 'warned 4.65 s before answering, every time': same mechanism, 56.1% false alarms | auditor rerun | RETRACT, as REVIEW-FLAGSHIP-EARLINESS-CLAIM-RETRACTED |
| REVIEW-REASONING-TRACE-CLAIM-RETRACTED | EXPERIMENT-CONTAMINATION-TEST 'reasoning phase detects errors; the reasoning trace is not contaminated': features were whole generation + answer segment; no reasoning-only feature existed | Phase A (code) | RETRACT the claim; OPEN: re-test on the reasoning segment only (backlog) |

## Major
| ID | Finding | Verified | Resolution |
|---|---|---|---|
| REVIEW-LAYER-TAP-ONE-STEP-LATE | Layer tap stored each token's reading one step late (prompt pass first); stale, not future | Phase A: fresh forward pass (lag-1 error 0.01, aligned error 0.4-3.6) | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE: tap fixed + permanent test (agr/test_layertap_alignment.py); seeds 2-6 resynchronized (shift verified, 0.013 vs 0.5-0.9 SD); result confirmed on corrected data |
| REVIEW-UNANSWERED-EPISODES-EXCLUDED | EXPERIMENT-CLEAN-REALTIME-RACE/34 excluded never-answered episodes (62/600, 63/600) without disclosure | auditor | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE: pre-declared sensitivity analysis; DOC disclosure in EXPERIMENT-CLEAN-REALTIME-RACE/34 |
| REVIEW-POOLED-ESTIMATE-NEVER-COMPUTED | EXPERIMENT-REPLICATION-REALTIME-RACE undocumented; pre-registered pooled estimate EXPERIMENT-REPLICATION-POOLED-SEEDS-ESTIMATE never computed | auditor, self | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE (pooled 5+6+7); DOC: EXPERIMENT-REPLICATION-REALTIME-RACE README and LEDGER row |
| REVIEW-EUREKA-WORDING-OVERSTATED | 'EUREKA (confirmed robust)', 'first leak-free' overstated | auditor | REWORD: 'primary criterion met (EXPERIMENT-CLEAN-REALTIME-RACE), replicated (EXPERIMENT-REPLICATION-REALTIME-RACE), confirmed under the corrected protocol (EXPERIMENT-CORRECTED-REALTIME-RACE); first such result in this program' |
| REVIEW-FALSE-ALARM-CAP-EXCEEDED | Organism false-alarm rate 10.12% > 10% cap | auditor | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE (tightest threshold with <= 10%) |
| REVIEW-MONITORABLE-FALSE-ALARMS-UNREPORTED | False alarms among monitorable episodes unreported (16.6%) | auditor | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE (reported) |
| REVIEW-BOOTSTRAP-IGNORED-THRESHOLD-UNCERTAINTY | Bootstrap CIs ignored threshold uncertainty | auditor | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE (all episodes resampled, thresholds re-set) |
| REVIEW-ANALYSIS-CODE-COMMITTED-LATE | Analysis code committed with results, not before | auditor | PROCESS: EXPERIMENT-CORRECTED-REALTIME-RACE code + dry run committed before seed 7 (b6c795b); DOC disclosure for earlier experiments |
| REVIEW-DEEP-FEATURE-COUNT-WRONG | EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM '≈302 features' (actual 314); unregistered metric and extrapolation change | auditor, self | DOC: count corrected; deviations listed |
| REVIEW-WARNING-SCORE-NOT-PREREGISTERED | EXPERIMENT-AI-EARLY-WARNING-SCORE called pre-registered (4 minutes before results, on thrice-used data); EXPERIMENT-VITAL-CRITICAL-SLOWING-TREND changed | auditor | REWORD: retrospective; DOC the EXPERIMENT-VITAL-CRITICAL-SLOWING-TREND change |
| REVIEW-SETTLING-DRIVEN-BY-WEEKDAY | EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM EXPERIMENT-CONFIRMATORY-FAILURE-TO-SETTLE 'failure to settle confirmed' driven by one question type | auditor rerun | REWORD: weekday-specific; within-type tests reported |
| REVIEW-BASELINES-BEAT-EARLY-ORGANISMS | Length and question-type baselines match or beat pre-EXPERIMENT-CLEAN-REALTIME-RACE organisms | auditor rerun | DOC + ARTIFACT (archive/audit/artifacts/): on seed 1, length (0.796) exceeds EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP (0.72), EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM (0.765) and EXPERIMENT-AI-EARLY-WARNING-SCORE (0.725); question type (0.764) exceeds EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP and EXPERIMENT-AI-EARLY-WARNING-SCORE and roughly matches EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM (corrected per fifth audit REVIEW-DEEP-ORGANISM-MATCHED-TYPE); EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM 0.89 exceeds type 0.80 and length 0.73 |
| REVIEW-TOPOLOGY-WINDOW-COUNT-PROXY | EXPERIMENT-PHYSIOLOGICAL-COUPLING-GRAPH topology features include n_windows (a length proxy) | auditor rerun | OPEN (backlog) rerun without it; DOC |
| REVIEW-SUBSTRATE-ENTROPY-PROPOSITION-RETRACTED | EXPERIMENT-METABOLIC-VITALS 'substrate' entropy includes answer tokens; Proposition 2 false | auditor | RETRACT Proposition 2; OPEN (backlog) re-window |
| REVIEW-HPA-VARIANCE-RATIO-MISSTATED | EXPERIMENT-HPA-AXIS-ORGANISM 'variance 9-10x lower' is a CV ratio (≈3.7x above rest); drive correlates with length | auditor rerun | REWORD; DOC |
| REVIEW-TOKEN-COST-MISATTRIBUTED | '290 ns/token' attributed to competing organisms (they cost 2-4 ms) | auditor | REWORD + ARTIFACT (timing script) |
| REVIEW-LENGTH-CONTROL-NOT-REPRODUCIBLE | EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM length control not reproducible (0.578 does not reproduce) | auditor, self | ARTIFACT: archive/audit/artifacts/baselines_and_breakdowns.py reproduces 0.773, 15/46 and 0.578, 11/46 (our definition: derivation-correct percentile by type) |
| REVIEW-WRAPPER-UNMATCHED-FALSE-POSITIVES | EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER detection claims at unmatched false-positive rates | auditor rerun | REWORD; OPEN (backlog) matched comparison |
| REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED | RESEARCH_PROGRAM: 'behavior is not predictive', 'unjailbreakable by construction' | auditor | REWORD: update through EXPERIMENT-CORRECTED-REALTIME-RACE; 'text-blind' kept, 'unjailbreakable' dropped (untested) |
| REVIEW-NOVELTY-CLAIMED-WITHOUT-LITERATURE | Novelty claims without related work (hidden-state error prediction literature) | auditor | DOC: related-work section |

## Minor
| ID | Finding | Resolution |
|---|---|---|
| REVIEW-SILENT-SLIP-TEST-SET-THRESHOLD | EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM EXPERIMENT-CONFIRMATORY-SILENT-SLIPS used a test-set threshold; 'silent slip' defined by question type only | DOC deviation; per-category false alarms reported |
| REVIEW-BELOW-CHANCE-CITATION-WRONG | 'Below chance' confidence claim cited with a CI that includes 0.5 | REWORD: cite EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM 0.366 [0.304, 0.433] |
| REVIEW-LEVEL-ORDERING-SMALL-GROUPS | 'Perfectly ordered' levels rest on groups of 17, 8, 2 | REWORD |
| REVIEW-EVERY-CHECKPOINT-CLAIM-UNSUPPORTED | 'Better than the judge at every checkpoint' (no CIs; reverses at t=384 in EXPERIMENT-REPLICATION-REALTIME-RACE) | REWORD; CIs OPEN (backlog) |
| REVIEW-LEAD-TIME-NOT-FIRST-CROSSING | Lead time at best, not first, crossing | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE |
| REVIEW-LIVE-TIMING-NONDETERMINISTIC | Live compute timing made in-time status non-deterministic | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE (fixed 5 ms cost) |
| REVIEW-JUDGE-PREFIXES-RETOKENIZED | Judge prefixes re-tokenized from text | FIXED-EXPERIMENT-CORRECTED-REALTIME-RACE (exact token ids, seed 7) |
| REVIEW-COMPUTE-RATIOS-EXCLUDE-TAP | Compute ratios exclude tap cost; wall-clock not compute | REWORD |
| REVIEW-HEAT-TRACE-THEOREM-WORDING, REVIEW-WRAPPER-THEOREM-WORDING and REVIEW-HPA-THEOREM-WORDING | Theorem wording and test coverage in EXPERIMENT-HOMEOSTATIC-HEAT-TRACE-MONITOR, EXPERIMENT-BOUNDED-HOMEOSTASIS-WRAPPER and EXPERIMENT-HPA-AXIS-ORGANISM | REWORD; tests OPEN (backlog) |
| REVIEW-DEEP-PROPOSITION-TEST-INEXACT | EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM Proposition 3 test does not check the exact statement; features numerically fragile | DOC; OPEN (backlog) exact-case test and sensitivity |
| REVIEW-MISSING-LEDGER-ROWS | Missing LEDGER rows (EXPERIMENT-LATERAL-INHIBITION-SPARSITY-AUDITOR, 0022, 0034); EXPERIMENT-GRADED-AGENTIC-EARLY-WARNING test only greps a file; wrong checkpoints in HYPOTHESES | DOC + PROCESS |
| REVIEW-DATA-RATIO-MISSTATED | '9x more data' (10x); EXPERIMENT-VITAL-FAILURE-TO-SETTLE points dropped from explanations; methodology 0-21 vs 0-24 | DOC; code fix OPEN (backlog) |
| REVIEW-JUDGE-SIZE-RATIO-MISSTATED | '6x larger judge' (5.6x total, 1.4x active parameters) | REWORD |

## Found by us (self)
| ID | Finding | Resolution |
|---|---|---|
| REVIEW-GREEDY-RUNS-DIVERGED-ACROSS-SESSIONS (REVIEW-GREEDY-RUNS-DIVERGED-ACROSS-SESSIONS) | Greedy generation is deterministic within a session but diverged across sessions for ~40% of episodes (likely GPU sharing during the seed-2 recording) | REWORD 'token-reproducible' claims; PROCESS: record alone; log environment |
| REVIEW-VERIFICATION-CLAIMED-BEFORE-CHECK | '720/720 token-identical' was asserted before being checked (true when later checked: 480/480 + 240/240) | PROCESS: no verification claim before the check |
| REVIEW-AD-HOC-COUNTS-UNSAVED | Per-type 'struggle 10/12 vs slips 0/9' (EXPERIMENT-VITALS-VS-BEHAVIOR-FLAGSHIP) computed ad hoc, never saved | ARTIFACT: same script reproduces 10/12 struggle and 0/9 slips |
| REVIEW-COPIED-MAKEFILES-BROKE-CI | Pre-registration folders copied with full Makefiles broke CI (EXPERIMENT-REPLICATION-REALTIME-RACE); local checks did not mirror CI | PROCESS: EXPERIMENT-CORRECTED-REALTIME-RACE experiment exits cleanly when data is absent (done); local check to mirror CI (Phase D) |
| REVIEW-BLOG-REPEATED-RETRACTED-CLAIMS | Blog draft repeats REVIEW-FLAGSHIP-EARLINESS-CLAIM-RETRACTED, REVIEW-REASONING-TRACE-CLAIM-RETRACTED, REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED, REVIEW-JUDGE-SIZE-RATIO-MISSTATED and 'every experiment is public' | Phase E: rewrite from the corrected record |
| REVIEW-SYNC-TEST-ARBITRARY-CAP | The telemetry synchronization test used an arbitrary cap (0.15) that the 4-bit, 128-expert second model exceeds while clearly synchronized | PROCESS: criterion replaced for both models by the property itself (every reading closer to its own token than to the neighbour; median error below 0.10); both pass |

## Second audit (2026-09-30): EXPERIMENT-CORRECTED-REALTIME-RACE and the blog drafts

Independent, read-only audit of EXPERIMENT-CORRECTED-REALTIME-RACE and both blog drafts (archive/audit/yb0035_blog_audit_2026-09-30.md): 25 findings (2 critical, 10 major, 13 minor). It found no leakage in EXPERIMENT-CORRECTED-REALTIME-RACE and recomputed its key counts; the problems were in interpretation. Findings REVIEW-BETTER-THAN-JUDGE-OVERSTATED, REVIEW-UNEQUAL-MONITORABLE-FALSE-ALARMS, REVIEW-FIRST-AUDIT-COUNTS-WRONG, REVIEW-RESYNC-CHECK-UNCOMMITTED and REVIEW-LAUNCH-WRAPPER-UNCOMMITTED were verified independently before any change.

| ID | Severity | Finding | Verified | Resolution |
|---|---|---|---|---|
| REVIEW-BETTER-THAN-JUDGE-OVERSTATED | critical | Blogs: watching words cannot tell you when to worry; more reliable than the judge | EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM results: judge 0.947, self-consistency 0.982 vs regulator 0.890 on finished answers (checked) | REWORD: claim limited to before the answer exists, under a deadline; on finished answers self-consistency is more accurate and the judge was not distinguishable from an earlier regulator (corrected per third audit REVIEW-OLD-REGULATOR-GAP-NOT-SIGNIFICANT) |
| REVIEW-CONFIDENCE-NEVER-MEASURED | critical | Blogs: confident wrong answers | EXPERIMENT-CORRECTED-REALTIME-RACE never measures confidence (checked) | REWORD: wrong answers |
| REVIEW-EARLIER-WARNING-CLAIM-DROPPED | major | Blogs: warnings come earlier | Median seconds to spare favour the judge on seeds 5 and 6 | REWORD: earlier dropped |
| REVIEW-REUSED-TEST-SETS-CALLED-NEW | major | Plain blog: each test set brand new and used once | Seeds 5 and 6 reused from EXPERIMENT-CLEAN-REALTIME-RACE/34 | REWORD: only seed 7 is fresh |
| REVIEW-POOLED-ESTIMATE-AS-HEADLINE | major | Pooled estimate presented as the headline | Two of three sets already known positive; mixed judge inputs | DOC: seed 7 leads; pooled descriptive (this file, EXPERIMENT-CORRECTED-REALTIME-RACE README, RESEARCH_PROGRAM, LEDGER) |
| REVIEW-UNEQUAL-MONITORABLE-FALSE-ALARMS | major | 10% cap set on test answers; monitorable false alarms unequal (16.3/11.0/10.3%) | Recomputed from results.json (checked) | ARTIFACT: EXPERIMENT-CORRECTED-REALTIME-RACE tests/exploratory_audit2.py: equal monitorable false alarms 19 vs 11, +0.20 [+0.02, +0.43]; frozen derivation threshold 22/40 |
| REVIEW-FIRST-AUDIT-COUNTS-WRONG | major | Technical blog: first audit 3 critical, 23 major, 12 minor | Audit file severity column: 3 / 20 / 15 (checked); repo documents not affected | FIX in blog |
| REVIEW-TYPE-BASELINE-MISSING | major | Technical blog: regulator beats question-type baseline | No such baseline in EXPERIMENT-CORRECTED-REALTIME-RACE | ARTIFACT: type baseline EXPERIMENT-QUESTION-TYPE-BASELINE catches 6/40; regulator minus type +0.43 [+0.19, +0.63] |
| REVIEW-RESYNC-CHECK-UNCOMMITTED | major | Resynchronization verified on 6 episodes by an uncommitted script | Confirmed: script missing; committed log showed 8/20 mismatches | ARTIFACT: agr/verify_shift.py: 11/20 identical-text episodes, median error 0.012 vs 0.81 SD (shift vs none), better in 11/11, worst single reading 2.8 SD |
| REVIEW-CHECKPOINT-AUROC-ONE-SEED | major | Per-checkpoint AUROC only for seed 7, no CIs; could reflect predicting eventual length | Seed 6 t=384: regulator 0.530 vs judge 0.607 | OPEN: all seeds with CIs; limitation stated |
| REVIEW-GRADED-WARNINGS-OVERSTATED | major | Plain blog: graded warnings | The winner is a binary-thresholded logistic model; AI-EWS v4 did not beat length | REWORD |
| REVIEW-ROBUSTLY-SUPPORTED-OVERSTATED | major | Technical blog: robustly supported | One model, one checkpoint set, one machine | REWORD: supported on the pre-registered test set |
| REVIEW-FASTER-SERVING-OVERGENERALIZED | minor | Faster serving would help every monitor | Only behavior monitors would benefit | REWORD |
| REVIEW-BLIND-SPOT-OVERGENERALIZED | minor | Structural blind spot generalized from one model, no base rate |  | REWORD |
| REVIEW-CONFIDENCE-THRESHOLD-MISQUOTED | minor | More than 90% confidence misquotes EXPERIMENT-CONTAMINATION-TEST | Source: at least 0.9 on every answer token | REWORD |
| REVIEW-POWER-NULL-OVERSTATED | minor | No power difference; same work per word | Power result is not detectable (AUROC 0.40); mechanism retracted (REVIEW-SUBSTRATE-ENTROPY-PROPOSITION-RETRACTED) | REWORD |
| REVIEW-JUDGE-TIMING-UNSUPPORTED | minor | Judge about 1.5 to 2 s, no artifact |  | ARTIFACT: archive/audit/artifacts/judge_timing.py: seed 7 median 1.55 s, 90th percentile 7.2 s |
| REVIEW-FIRST-RESULT-MISATTRIBUTED | minor | First result beating behavior attributed to EXPERIMENT-CORRECTED-REALTIME-RACE | EXPERIMENT-CLEAN-REALTIME-RACE met it first | REWORD per REVIEW-EUREKA-WORDING-OVERSTATED |
| REVIEW-RECORDINGS-NOT-QUESTIONS-ABSENT | minor | Before the questions exist; confirmed on GitHub | Questions are seed-determined; it was the recordings that did not exist | REWORD |
| REVIEW-LAUNCH-WRAPPER-UNCOMMITTED | minor | Recorded alone; launch wrapper uncommitted | Guard added later; no contention logged | ARTIFACT: agr/start_seed7_after_push.sh (byte-identical); REWORD: no concurrent jobs logged, guard added afterwards |
| REVIEW-ALIGNMENT-CRITERION-CHANGED | minor | Alignment pass criterion changed after seed 7 | Logged as REVIEW-SYNC-TEST-ARBITRARY-CAP | DOC: disclosed next to the second-model claim |
| REVIEW-FIRMER-RESULT-OVERSTATED | minor | EXPERIMENT-CORRECTED-REALTIME-RACE README: result got firmer | Seed-7 lower bound vs judge +0.049 is below EXPERIMENT-REPLICATION-REALTIME-RACE +0.070 | REWORD: held |
| REVIEW-UNCERTAINTY-PAPERS-UNCITED | minor | Related work incomplete | Burns 2023; Kuhn, Gal and Farquhar 2023; Bailey 2024 missing | DOC: add (blogs; RESEARCH_PROGRAM OPEN) |
| REVIEW-TASK-LIST-INCOMPLETE | minor | Task list omits one type; uneven error distribution |  | DOC: all six types; per-type breakdown OPEN |
| REVIEW-VERIFICATION-ATTRIBUTED-TO-AUTHOR | minor | I verified every critical finding myself | Verification was done by the AI research assistant under the author's direction | REWORD |

## Third audit (2026-09-30): the v2 blog drafts

Independent, read-only audit of the two v2 drafts (archive/audit/blog_v2_audit_2026-09-30.md): no invented numbers found;
1 critical, 9 major, 20 minor findings on verifiability, attribution, provenance and wording. All resolved (rows below); blog wording applied in v3, re-audited in the fourth audit.

| ID | Severity | Finding | Verified | Resolution |
|---|---|---|---|---|
| REVIEW-COMMIT-BEFORE-DATA-UNPROVEN | critical | Posts claim the protocol was committed before the test recordings existed, but the repository is private and git times are author-set | GitHub server records: push of b6c795b at 2026-09-30T15:26:40Z, CI run at 15:26:42Z; first seed-7 episode 15:26:49.96Z (Mac clock, offset -1.2 ms vs Apple time server when checked). Ordering holds; the margin is about 10 s, not the 4 min implied by the local commit time | ARTIFACT: archive/audit/artifacts/c1_github_server_timestamps.json. REWORD (blogs): cite GitHub server time and the ~10 s margin; state that the code, data, reports and corrections are public (YobieBenjamin/autonomic-graph-regulation) and the commit history that timestamps the pre-registration is private and available to reviewers on request. PROCESS: protocol rule 13 (public cryptographic timestamp of every pre-registration hash at commit time) |
| REVIEW-SWEET-TALK-CLAIM-REINTRODUCED | major | Plain draft: cannot be sweet-talked (reintroduces the retracted unjailbreakable claim) | CORRECTIONS REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED; activations depend on input text | REWORD in v3: cannot be argued with directly; whether crafted inputs can fool it is untested |
| REVIEW-EXPLORATORY-PRESENTED-AS-PLANNED | major | Plain draft presents exploratory checks (type baseline, equal false alarms, frozen threshold) as part of the planned design | exploratory_audit2.json marks them EXPLORATORY | REWORD in v3: labeled as added afterwards |
| REVIEW-CONCLUSION-BLENDS-EXPLORATORY | major | Technical conclusion blends pre-registered and exploratory results; frozen-threshold check has no judge arm or interval | exploratory_audit2.py docstring; regulator 15.0% monitorable false alarms | REWORD in v3 |
| REVIEW-OLD-REGULATOR-GAP-NOT-SIGNIFICANT | major | 0.890 is an earlier, pre-fix regulator and its gap to the judge was not significant; repository inconsistent | EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM: deep minus judge -0.057 [-0.131, +0.012], not distinguishable; minus self-consistency -0.092, inferior (checked) | FIX: CORRECTIONS header and REVIEW-BETTER-THAN-JUDGE-OVERSTATED, RESEARCH_PROGRAM, LEDGER, EXPERIMENT-CORRECTED-REALTIME-RACE README corrected; REWORD in v3 |
| REVIEW-REGULATOR-SEES-TYPE-AND-LENGTH | major | Regulator also receives question type and elapsed tokens (normalization per type and checkpoint) | src/absrace.py key = (cat, t) (checked) | DOC: EXPERIMENT-CORRECTED-REALTIME-RACE README, RESEARCH_PROGRAM, GLOSSARY text-blind entry; ARTIFACT: type-by-length baseline 9/40 (docs/exploratory_audit3.json); REWORD in v3 |
| REVIEW-LOST-RACE-OMITTED | major | Posts omit the pre-registered race the regulator lost (EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM: 4 vs 12 of 47) and the rejected EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM design | EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM results (checked) | DOC: RESEARCH_PROGRAM design history; REWORD in v3 |
| REVIEW-AI-AUTHORSHIP-UNDISCLOSED | major | Posts do not disclose that code, experiments and drafts were largely AI-written, or that all audits were AI sessions | README model-written code note | DOC: README.md Authorship and AI assistance; REWORD in v3 |
| REVIEW-CLOSEST-PRIOR-WORK-UNCITED | major | Closest prior work (early detection of reasoning non-convergence from hidden states, arXiv 2607.21433) not cited; novelty overstated | RESEARCH_PROGRAM related work lists it | REWORD in v3 |
| REVIEW-RERUN-FROM-SCRATCH-OVERSTATED | major | Re-ran the key experiment from scratch overstates: only seed 7 was newly recorded | EXPERIMENT-CORRECTED-REALTIME-RACE PREREGISTRATION | REWORD in v3 |

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
| m14 | minor | EXPERIMENT-CLEAN-REALTIME-RACE/34 ran under the since-corrected protocol | checked | REWORD |
| m15 | minor | launch script committed after the fact | checked | DOC |
| m16 | minor | 25 findings mostly, not only, interpretation | checked | REWORD |
| m17 | minor | offline replay, not live race | checked | REWORD |
| m18 | minor | strongest vs most stringent | checked | REWORD |
| m19 | minor | effectors not built | checked | REWORD |
| m20 | minor | all errors from four of six types | checked | ARTIFACT seed7_counts.json; REWORD |

## Fourth audit (2026-10-01): the v3 blog drafts

Independent, read-only audit of the v3 drafts with access to the public snapshot (archive/audit/blog_v3_audit_2026-10-01.md). All numbers verified against committed files; no leakage or post-registration changes. 1 critical, 5 major, 17 minor findings. IDs prefixed REVIEW-FOURTH-AUDIT-OF-BLOG-DRAFTS- to avoid collision with the third audit.

| ID | Severity | Finding | Verified | Resolution |
|---|---|---|---|---|
| REVIEW-FULL-RECORD-NOT-PUBLIC | critical | Posts said the full record is public; the commit history (incl. b6c795b) is private | Public snapshot has 1 commit (checked) | REWORD (author decision): the code, data, reports and corrections are public; the commit history that timestamps the pre-registration is private and available to reviewers on request |
| REVIEW-RECORDING-START-SELF-REPORTED | major | Recording start time is self-reported (local clock); clock offset checked about 10 h later | c1 artifact retrieved 01:33Z; recorder uses time.time() | REWORD: disclose; rule 13 addresses future experiments |
| REVIEW-THIRD-AUDIT-MINORS-UNLOGGED | major | Third-audit minors not logged; REVIEW-COMMIT-BEFORE-DATA-UNPROVEN row outdated | checked | FIX: logged above; REVIEW-COMMIT-BEFORE-DATA-UNPROVEN updated |
| REVIEW-LEDGER-RETRACTED-CLAIMS | major | LEDGER rows still stated retracted claims | 9 rows (checked) | FIX: correction notes appended, original text preserved |
| REVIEW-INVERTED-CONFIDENCE-WORDING | major | Confidence wording (inverted signal carries information; from EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM) | EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM 0.366 [0.304, 0.433] | REWORD |
| REVIEW-NO-PROBE-BASELINE | major | No standard hidden-state probe baseline | EXPERIMENT-CORRECTED-REALTIME-RACE monitor list (checked) | DOC: limitation stated; experiment EXPERIMENT-PROBE-BASELINE added to the backlog |
| REVIEW-FOURTH-AUDIT-OF-BLOG-DRAFTS minor items 1 to 17 | minor | Audit count, rule count, verification attribution, which regulators the baselines beat, frozen-threshold false alarms, fixed vs measured cost, judge-vs-regulator wording, simulation wording, Qwen design class, book status, novelty caveat, judge settings, sync-test detail, resynchronized counts, model-size source, license scope for replication, full reference for arXiv 2607.21433 | checked | REWORD in v4; ARTIFACT model_sizes.json |

## Fifth audit (2026-10-01): the v4 blog drafts

Independent, read-only audit (archive/audit/blog_v4_audit_2026-10-01.md). Verdict: both drafts publishable with listed fixes. Seed-7 timeline consistent (push 15:26:40Z; alignment log 15:26:48Z; recorder start 15:26:49.955Z); no leakage; public snapshot verified; citation verified. 1 major, 10 minor findings, IDs prefixed REVIEW-FIFTH-AUDIT-OF-BLOG-DRAFTS-.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| REVIEW-AUDITS-SAW-EARLIER-FINDINGS | major | Posts said audits were told nothing about earlier findings; audits 2-4 could and did read them | REWORD v5: fresh, read-only sessions, separate from the work; later audits could read earlier findings |
| Ten minor findings of the fifth audit, one per item in the next column | minor | Audit count; EXPERIMENT-DEEP-LAYER-GRAPH-ORGANISM matched (not failed) the type baseline; reused seeds labelled; low reasoning effort of the monitored model; expert-count source; false-alarm footnote; single judge configuration (weak early); Part II without Part I; AI audits not unforgiving; full reference missing from the record | REWORD v5; FIX REVIEW-BASELINES-BEAT-EARLY-ORGANISMS wording; ARTIFACT model_sizes.json (experts); DOC RESEARCH_PROGRAM full reference |

## Self-found (2026-10-01)

| ID | Finding | How found | Resolution |
|---|---|---|---|
| REVIEW-RAW-RECORDINGS-COMMITTED | The EXPERIMENT-PROBE-BASELINE chain publish committed 4,810 raw per-episode recordings (about 466 MB) under data/agr: new filenames were not covered by .gitignore | Found by the three-copy verification before any public upload completed (public stayed at b7d526d) | FIX: untracked (files kept locally and in private history; packed copies under algorithms/probe-baseline/data are the record); .gitignore extended; snapshot pipeline now aborts on raw recordings |

## Sixth audit (2026-10-01): the v6 blog drafts, including the first audit of EXPERIMENT-PROBE-BASELINE and the NVIDIA section

archive/audit/blog_v6_audit_2026-10-01.md: 1 critical, 8 major, 11 minor. Numbers verified; EXPERIMENT-PROBE-BASELINE code unchanged between pre-registration and results.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| REVIEW-PUBLIC-SNAPSHOT-OUT-OF-DATE | critical | Public repo lacked EXPERIMENT-PROBE-BASELINE when audited | Resolved: snapshot b2c7a50 (from a025fca) includes EXPERIMENT-PROBE-BASELINE; re-cut after EXPERIMENT-POWERED-REPLICATION adds the timestamp proofs |
| REVIEW-INTERNAL-STATE-CLASS-OVERCLAIMED | major | Internal-state monitoring as a class overclaimed; early AUROC comparison descriptive and unpaired | FIX: RESEARCH_PROGRAM claim status; REWORD v7 |
| REVIEW-SEED-EIGHT-LENGTH-DEGENERATE | major | Seed-8 length comparison degenerate (0/40 under the monitorable cap); probe comparisons have no interval | REWORD v7 |
| REVIEW-TECHNICAL-DRAFT-OMITS-LOST-RACE | major | Technical draft omits the race the regulator lost (EXPERIMENT-CONFIRMATORY-DEEP-PROGRAM) and the rejected EXPERIMENT-SERIAL-EARLY-WARNING-ORGANISM design | REWORD v7 |
| REVIEW-PROBE-AND-NVIDIA-UNAUDITED | major | EXPERIMENT-PROBE-BASELINE, the probe conclusion and the NVIDIA section had not been audited before | This audit covers them; v7 states six audits |
| REVIEW-BLIND-AUDIT-WORDING | major | "blind" contradicts REVIEW-AUDITS-SAW-EARLIER-FINDINGS | REWORD v7 |
| REVIEW-README-AUDIT-DESCRIPTION-STALE | major | README audit description stale (three audits, no knowledge of earlier findings) | FIX: README |
| REVIEW-NVIDIA-FACTS-UNSOURCED | major | NVIDIA facts lacked a committed source | DOC: docs/sources/nvidia_open_agent_safety_platform.md; attribution in v7 |
| REVIEW-PROBE-PROOF-PENDING | major | EXPERIMENT-PROBE-BASELINE OpenTimestamps proof pending when audited | Resolved: proof complete (Bitcoin-anchored), committed in 4a3da80; RFC 3161 tokens added |
| REVIEW-SIXTH-AUDIT-OF-BLOG-DRAFTS minor items 1 to 11 | minor | Four-layer wording; which audit verified REVIEW-DEEP-EARLINESS-CLAIM-RETRACTED; contention windows; EXPERIMENT-PROBE-BASELINE training-size description; seed-8 counts; "clearly"; base rate for correct answers; quantized build; theorem-test coverage; CITATION.cff pointed to the private repo; GitHub timestamps retrieved by the author | FIX: EXPERIMENT-PROBE-BASELINE README, CITATION.cff, ARTIFACT derivation_sizes.json; REWORD v7 |

## Seventh audit (2026-10-01): the v8 blog drafts, the first audit of EXPERIMENT-POWERED-REPLICATION

archive/audit/blog_v8_audit_2026-10-01.md: 1 critical, 7 major, 7 minor. Every figure verified; EXPERIMENT-POWERED-REPLICATION analysis code unchanged since pre-registration 682f373.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| REVIEW-PUBLIC-SNAPSHOT-OUT-OF-DATE | critical | Public snapshot lacks EXPERIMENT-POWERED-REPLICATION, docs/sources, rule 13 and timestamp proofs (repeat of REVIEW-PUBLIC-SNAPSHOT-OUT-OF-DATE) | Re-cut after these fixes and verified on GitHub before posting |
| REVIEW-PUBLIC-PROOF-UNFINISHED | major | Public EXPERIMENT-PROBE-BASELINE OpenTimestamps proof was the unfinished one | Fixed by the re-cut (complete proof committed in 4a3da80) |
| REVIEW-REPLICATION-PROOF-PENDING | major | EXPERIMENT-POWERED-REPLICATION OpenTimestamps proof pending; timeline of the RFC 3161 tokens not stated | FIX: proof upgraded (complete, 4 Bitcoin attestations); REWORD: OTS 14:53Z, RFC 3161 15:45Z (after derivation recording began at 15:14Z, before the first test recording at 18:59Z) |
| REVIEW-REPLICATION-UNAUDITED | major | No audit had reviewed EXPERIMENT-POWERED-REPLICATION | This audit covers it; REWORD |
| REVIEW-CHECKPOINT-WORDING-INTERVALS-MISSING | major | "At every checkpoint" overstated; equal-false-alarm and frozen-threshold results lack intervals | FIX RESEARCH_PROGRAM; REWORD v9 |
| REVIEW-PROBE-COST-NEVER-MEASURED | major | Probe compute cost assumed (5 ms), never measured | DOC + REWORD |
| REVIEW-SOLID-GROUND-OVERSTATED | major | "Solid ground" overstated | REWORD |
| REVIEW-SEED-SEVEN-CALLED-MAIN | major | Seed 7 called the main result while EXPERIMENT-POWERED-REPLICATION carries the conclusion | REWORD |
| REVIEW-SEVENTH-AUDIT-OF-BLOG-DRAFTS minor items 1 to 7 | minor | Per-seed sums (only the judge differs); older regulator in the offline comparison; EXPERIMENT-POWERED-REPLICATION monitorable false-alarm rates; power figures without an artifact; 24x is versus one layer; 100+ partners from secondary outlets; comma splice | ARTIFACT tests/power.py + docs/power.json; REWORD v9 |

## Eighth audit (2026-10-02): the v10 blog drafts, first audit of EXPERIMENT-OPENSHELL-GATING; two independent auditors

**Claude** (fresh read-only session with repository access; archive/audit/blog_v10_audit_claude_2026-10-02.md): 3 critical, 8 major, 12 minor; every number verified by recomputation.
**GLM-5.3-flash** (Z.ai; first non-Claude auditor; given the drafts plus an evidence bundle of committed results, no repository access; archive/audit/glm_audit.py, glm_audit_prompt_v10.txt, blog_v10_audit_glm_2026-10-02.json, blog_v10_audit_glm_response.json): 86 claims checked, 71 verified, 15 findings (1 major, 14 minor); no wrong number found.
**How GLM was run:** LM Studio could not load the local GGUF (unknown architecture glm5next in llama.cpp 2.14.0, latest stable and beta); run 1 via the Z.ai API returned an empty answer because 17,908 reasoning tokens (that count is from run 2; the run-1 cause is inferred) exceeded its 16,000-token budget (confirmed from run 2 usage); run 2 (reasoning effort high, 40,000-token budget) completed.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| REVIEW-GATING-RESULTS-NOT-PUBLIC | critical | EXPERIMENT-OPENSHELL-GATING results untracked and not public | FIX: committed; snapshot re-cut; cited paths verified on public GitHub |
| REVIEW-FROZEN-SANDBOX-STORY-UNRECORDED | critical | Frozen-sandbox story not in the committed record | DOC: incident in docs/OPENSHELL_SETUP.md with caveat (logs not retained); claim cut from posts |
| REVIEW-HOLD-ARM-WINS-BY-DESIGN | critical | Arm C 93 of 93 fixed by design; EXPERIMENT-HOLD-PREVENTS-MORE-COMMITS nearly guaranteed | REWORD: posts lead with arm B (74 of 93 lost) and arm C costs; README and claim status note it |
| REVIEW-LIVE-ENFORCEMENT-LATENCY-WIDER | major | Live enforcement latency wider than isolated; possible leftover blocks | ARTIFACT docs/supplementary.json: re-counting 4 short-gap wins as losses gives 83.9% [76.3%, 91.4%]; disclosed |
| REVIEW-LIVE-START-UNVERIFIABLE | major | Live start time not verifiable | ARTIFACT docs/mock_service_log.jsonl and supplementary.json: first start 14.1 s after the RFC 3161 stamp |
| REVIEW-HOLD-ARM-STALLS-UNREPORTED | major | Arm C stalls unreported; timeout cause inferred | DOC: 7 stalls over 60 s (largest 754 s) disclosed; cause not established |
| REVIEW-GATING-EXPERIMENT-UNAUDITED | major | No audit had covered EXPERIMENT-OPENSHELL-GATING; blind; README count | REWORD; README now points to CORRECTIONS for counts |
| REVIEW-UNJAILBREAKABLE-CLAIM-RESTATED | major | Plain draft restated the retracted unjailbreakable claim | REWORD |
| REVIEW-TIMESTAMPS-NOT-EVERY-TEST | major | Public timestamps not before every test | REWORD: from the second test on |
| REVIEW-CITED-FILE-RETRACTED-CLAIMS | major | Cited file still stated retracted claims | FIX: retraction banners in RESEARCH_PROGRAM, PROJECT_HISTORY, HYPOTHESES; Bailey et al. 2024 added |
| REVIEW-PLATFORM-INTEGRATION-OVERSTATED | major | Overstated as plugged into NVIDIA platform; regulator not live | REWORD: replay through open-source OpenShell; no model in the loop; no Sentry or BlueField |
| REVIEW-EIGHTH-AUDIT-OF-BLOG-DRAFTS minor items 1 to 12 | minor | Every-action wording; regulator-minus-probe label; AUROC source; frozen threshold scope; sixth task type; 1.4x active; post hoc label; 93 is the regulator; CORRECTIONS row for the population mismatch (see EXPERIMENT-PROBE-BASELINE README deviation 1); 5 ms vs 4.1 ms; vendor claims; proofs | REWORD; proofs committed |
| REVIEW-INTERVAL-PAIR-UNNAMED | minor | Interval-separation claim did not name the pair (false for regulator vs probe) | REWORD (missed by Claude) |
| REVIEW-TOKEN-TIME-UNSUPPORTED | minor | About 20 ms per token unsupported; measured median 14.4 ms over 442,306 tokens | FIX + ARTIFACT archive/audit/artifacts/token_timing_and_width.json (missed by Claude) |
| REVIEW-STRICTER-RULE-UNEXPLAINED, REVIEW-TELEMETRY-WIDTH-RATIO-UNVERIFIED, REVIEW-HIDDEN-WIDTH-UNCITED | minor | Stricter-rule claim unexplained; 2,880 width uncited | REWORD; width confirmed (2,880; ratio 24.0) in the same artifact |
| REVIEW-TYPE-BASELINE-COUNT-UNSUPPORTED, REVIEW-RELEASE-DELAY-MISDESCRIBED, REVIEW-RETRACTED-LEAD-FIGURE-UNVERIFIABLE, REVIEW-PARTNER-COUNT-UNVERIFIED, REVIEW-TASK-TYPE-COUNT-INCONSISTENT, REVIEW-REGULATOR-SETTING-UNCITED, REVIEW-PROBE-SELECTION-PROCEDURE-UNEVIDENCED, REVIEW-RESAMPLE-COUNT-UNEVIDENCED, REVIEW-FEATURE-COUNTS-UNEVIDENCED, REVIEW-PROCESS-RULE-COUNT-UNCITED | minor | Items outside the evidence bundle, or already fixed in v11 | No change needed (verified in the repository by the Claude audit) or already fixed |

## Ninth audit (2026-10-03): the final drafts (LinkedIn plain-English version and technical v11); three auditors, three companies

**Claude** (repository access; archive/audit/final_audit_claude_2026-10-03.md): every number verified; REVIEW-FABRICATED-ARITHMETIC-EXAMPLE critical; REVIEW-TALK-PAST-CLAIM-RESTATED, REVIEW-ACTIVE-PARAMETER-CAVEAT-MISSING, REVIEW-THREE-TIMES-CLAIM-OVERSTATED, REVIEW-ARE-YOU-SURE-UNTESTED, REVIEW-GATES-LIST-CONTRADICTION, REVIEW-RACE-DIRECTION-FORESEEABLE and REVIEW-UNAWARE-ERROR-MISATTRIBUTED major; 16 minor.
**GLM-5.3-flash** (Z.ai; evidence bundle; archive/audit/final_audit_glm_2026-10-03.json): publishable with fixes; 74 checked, 64 verified; 1 major (same sentence as Claude REVIEW-THREE-TIMES-CLAIM-OVERSTATED), 9 minor bundle gaps; no wrong number.
**gpt-oss-120b** (OpenAI open-weight, local; same prompt and bundle; archive/audit/final_audit_gptoss_raw.txt): returned malformed JSON (recovered leniently); verdict not publishable; 57 checked, 22 verified; most findings incorrect (for example, called the probe count of 100 unsupported and an AUROC below 0.5 not below chance). **Not independent:** it is the judge in the experiments and wrote some code. Only findings confirmed against the files were adopted (93 vs 94; median for the 7.4 s delay), both also raised by Claude.
Prompt and bundle: archive/audit/multi_audit.py, multi_audit_prompt_final.txt.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| REVIEW-FABRICATED-ARITHMETIC-EXAMPLE | critical | Plain draft stated as fact that the model said 2 + 2 = 5 (fabricated) | FIX: replaced with a real error type (a big multiplication) |
| REVIEW-TALK-PAST-CLAIM-RESTATED | major | Can-not-talk-its-way-past restated the retracted unjailbreakable claim (REVIEW-UNJAILBREAKABLE-CLAIM-RESTATED lost in rewrite) | REWORD with the untested caveat |
| REVIEW-ACTIVE-PARAMETER-CAVEAT-MISSING | major | 1.4x active-parameter caveat missing (REVIEW-EIGHTH-AUDIT-OF-BLOG-DRAFTS minor item 6 lost) | FIX |
| REVIEW-THREE-TIMES-CLAIM-OVERSTATED | major | Three-times claim per test set overstated (2.5x, 2.9x, 2.6x; post hoc) | REWORD |
| REVIEW-ARE-YOU-SURE-UNTESTED | major | Are-you-sure claim untested; self-consistency works on finished answers | REWORD: does not work as a brake |
| REVIEW-GATES-LIST-CONTRADICTION | major | Gates list contradicted the model-cannot-be-a-gate claim | REWORD: second opinion yes, control of its own actions no |
| REVIEW-RACE-DIRECTION-FORESEEABLE | major | EXPERIMENT-REACTIVE-BLOCK-LOSES-RACES direction largely foreseeable from pre-registered files | DISCLOSED: 68 of 93 gaps (73.1%) under 5.47 s in the plan (verified) |
| REVIEW-UNAWARE-ERROR-MISATTRIBUTED | major | Unaware-error ERN attributed to Gehring 1993 | FIX: Nieuwenhuis et al. 2001; source Dehaene et al. 1994 |
| REVIEW-NINTH-AUDIT-OF-FINAL-DRAFTS minor findings | minor | Hyperdirect hedge (Nambu 2002); literally race; brake speed; Damasio year; 93 vs 94; connected wording; lands on nobody; exactly the same confidence; 90% caveats; gpt-oss code role; review-gate untested; EXPERIMENT-CORRECTED-REALTIME-RACE judge timing label; NVIDIA architecture wording; list numbering; full path; audit count | FIX or REWORD |

## Citation verification (2026-10-03)

Every literature citation in the published posts (32, including three added during the check) was verified against a primary source: DOI, publisher, PubMed or PMC, arXiv, proceedings, or the issuing body. Registry with URLs and access level: docs/sources/CITATIONS.md. 31 verified at abstract or full-text level; 1 (Dehaene, Posner and Tucker 1994) at record level via citing literature.

| ID | Finding | Resolution |
|---|---|---|
| REVIEW-SELF-EVALUATION-EVIDENCE-UNACKNOWLEDGED | Kadavath et al. 2022 shows self-evaluation partly works; thesis called self-policing an architectural category error | REWORD: acknowledge Kadavath; narrower claim (model cannot be the control on its own actions) |
| REVIEW-SELF-CONSISTENCY-PURPOSE-MISSTATED | Wang et al. 2022 proposed self-consistency for accuracy, not detection | REWORD: adapted as a disagreement signal |
| REVIEW-BYRNES-CITATION-UNDATED | Byrnes cited without year; a blog series | FIX: Byrnes, 2022, blog series |
| REVIEW-FLEXHEG-AUTHORS-MISSING | flexHEG cited without authors | FIX: Petrie and Aarne, 2025 |
| REVIEW-SPARROW-CRITICS-OMITTED | Sparrow 2007 presented without its critics | ADD: Champagne and Tonkens 2015; Robillard 2018 (both removed from the series 2026-10-04, full text unavailable; see CITATIONS.md) |
| REVIEW-ERROR-NEGATIVITY-TIMING-UNSOURCED | ERN 100 ms timing not in the Gehring 1993 abstract | ADD: Yeung, Botvinick and Cohen 2004 |
| REVIEW-PROBE-GENERALIZATION-LIMIT-OMITTED | Orgad et al. 2024: hidden-state detectors generalise poorly | ADD to limitations |
| REVIEW-SENTRY-CALLED-PRODUCT | Sentry is a reference design, not a shipping product | REWORD |
| REVIEW-AUDIT-FIXES-SOURCE-CONFIRMED | Ninth-audit fixes confirmed by primary sources: Nieuwenhuis 2001 (unaware errors), Aron and Poldrack 2006 full text (hyperdirect stop not established) | Confirmed (Nieuwenhuis later removed from the series 2026-10-04, full text unavailable; Aron direct-read evidence added to fulltext_verification.json) |

## Tenth audit (2026-10-04): Audit 1 of the final two-part series, Claude Opus 5.5 against the repository

Report: archive/audit/final_series_audit1_opus_2026-10-04.md. Verdict: publishable with fixes; no critical findings; every experimental number matched a committed file (EXPERIMENT-OPENSHELL-GATING recomputed from per-episode files); all 22 public paths exist.

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| REVIEW-YEUNG-SOURCE-UNVERIFIABLE | major | Yeung 2004 registry URL returns 404 to readers; claims beyond timing unrecorded | FIX: DOI as primary URL; registry records the five claims read in the full text on 2026-10-04 |
| REVIEW-REGISTRY-ACCESS-LEVELS-WRONG | major | Registry listed Logan, Farquhar, Chiba below full text although read in full | FIX: registry rebuilt with true access levels; 11 non-full-text papers moved to a not-cited list |
| REVIEW-VERIFICATION-EVIDENCE-UNCOMMITTED | major | Full-text verification evidence uncommitted; registry and evidence disagreed on Aron and Yeung | FIX: fulltext_verify.py, fulltext_verification.json, sort_inbox.py and the inbox README committed (PDFs git-ignored); Aron and Yeung recorded as read directly |
| REVIEW-PER-SEED-RANGE-REGULATOR-ONLY, REVIEW-JUDGE-MODEL-INDEPENDENCE-OMITTED, REVIEW-PREREGISTERED-EXPERIMENT-COUNT-WRONG, REVIEW-AI-CANNOT-BE-SAFEGUARD-LEFTOVER | minor | Per-seed range applied to regulator only; gpt-oss-120b non-independence missing in Part 1; four pre-registered experiments not three; leftover "AI cannot be one of them" | FIX |
| Thirteen minor findings of the tenth audit, one per item in the next column | minor | Unsourced critics clause; Byrnes revision date; unattributed Swiss cheese name; compute-cost wording; first fresh test wording; arm A computed; ninth audit covered previous drafts; Fixed vs Disclosed; timestamps from EXPERIMENT-PROBE-BASELINE on; 1,031 reached a checkpoint; four deviations; power figures; EXPERIMENT-CONTAMINATION-TEST link | FIX or REWORD |
| Seven minor findings of the tenth audit, one per item in the next column | minor | Audit counts, EXPERIMENT-PROBE-BASELINE deviation count and count discrepancy, stale research-program lines, NVIDIA attribution, run-1 token count, stale audit-script text | FIX (REVIEW-PROBE-COUNTS-DISAGREE documented, cause not established) |
| REVIEW-POSTED-DRAFTS-UNTRACKED | minor | Posted drafts untracked | FIX: archive/audit/series_final_2026-10-04/ committed |

## Eleventh audit (2026-10-04): Audit 2 of the final series, three auditors from three companies at once

Prompt: archive/audit/series_audit2_prompt.txt. Reports: series_audit2_fable_2026-10-04.md (Claude Fable 5.1, repository access), series_audit2_gpt55_2026-10-04.md (GPT-5.5 via OpenAI Codex CLI on the ChatGPT subscription, repository access, session record confirms model gpt-5.5), series_audit2_glmmed_2026-10-04.json (GLM-5.3-flash, Z.ai, evidence bundle, low reasoning effort; the high-effort run had not returned after 45 minutes).

Verdicts: all three publishable with fixes. Fable: 0 critical, 0 major; recomputed EXPERIMENT-OPENSHELL-GATING and EXPERIMENT-POWERED-REPLICATION from raw files; all 28 public paths exist; all Audit 1 fixes landed except one partial. GPT-5.5: 0 Part 1 findings; 2 major on the evidence chain. GLM: 78 checked, 66 verified, 13 minor.

| ID | Source | Finding | Resolution |
|---|---|---|---|
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 1 | GPT-5.5 REVIEW-DIRECT-READ-PASSAGES-MISSING | Aron and Yeung recorded as FETCH_FAILED in the committed evidence while the registry says read in full | FIX: direct-read passages with pages added to fulltext_verification.json |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 2 | GPT-5.5 REVIEW-JAILBREAK-WORDING-IN-PROGRAM | Retracted cannot-be-jailbroken wording still in docs/RESEARCH_PROGRAM.md, which Part 2 cites | FIX: text-blind by construction; telemetry attacks untested (REVIEW-UNJAILBREAKABLE-CLAIM-DROPPED) |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 3 | Fable REVIEW-NINE-AUDIT-COUNT-STALE | Audit count stale (nine) | FIX: eleven, with tenth and eleventh summarised in Part 2 |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 4 | Fable REVIEW-RULE-TRACING-OVERSTATED | Thirteen process rules each traced to a finding (only seven are) | FIX |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 5 | Fable REVIEW-CITATION-REVERSALS-UNNOTED, REVIEW-SCRIPT-DOCSTRING-STILL-STALE, REVIEW-MILLISECOND-CLAIM-TWO-ATTRIBUTIONS, REVIEW-AUDIT-SCRIPTS-UNTRACKED | REVIEW-SPARROW-CRITICS-OMITTED and REVIEW-AUDIT-FIXES-SOURCE-CONFIRMED reversals unnoted; stale script header; two attributions for the millisecond claim; audit files untracked | FIX (Fable REVIEW-SCRIPT-DOCSTRING-STILL-STALE claim that gpt-oss-120b never ran in LM Studio is incorrect; it did) |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 6 | GLM REVIEW-OPENSHELL-RELEASE-LOOSELY-DATED | just released (OpenShell) loosely dated | FIX: recently released |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 7 | GLM: eleven findings of figures missing from its evidence bundle | Eleven figures not in its bundle | NO CHANGE: each present in the repository and recomputed by Fable and Opus |
| REVIEW-ELEVENTH-AUDIT-OF-SERIES item 8 | GLM REVIEW-ARXIV-CITATION-DOUBTED | arXiv:2607.21433 possibly fabricated | NO CHANGE: real (read in full; confirmed live by Fable) |

## Voice edit (2026-10-04): final series, author voice pass, no factual change

At the author request, both parts were rewritten to remove AI-style phrasing (stock setups, colon reveals, tidy triplets, it-is-not-X-it-is-Y closers) and restore his irreverent voice. Facts, numbers, intervals, citations and file paths were held fixed. Verification: an automated comparison of every number in the before and after text found none removed and none added except the series markers (Part 1 of 2; a reference to Part 1). The posted drafts in archive/audit/series_final_2026-10-04/ are the voice-edited versions; the audited pre-edit versions remain in git history (commit 6020c80).

## Process findings (2026-10-04, EXPERIMENT-DIFFICULTY-CONFOUND, EXPERIMENT-TEXT-BASELINE-TRANSFER and EXPERIMENT-MULTILEVEL-FUSION)

| ID | Finding | Resolution |
|---|---|---|
| REVIEW-PUBLISH-RERUNS-BEFORE-TIMESTAMP | The publish pipeline re-runs experiments; for analyses whose test data already existed it would have run the confirmatory analysis before the timestamp | Gated behind make confirmatory; verified in the sandbox and during the live publish (PROTOCOL rule 14) |
| REVIEW-DRY-RUN-INFINITE-SCORES | EXPERIMENT-TEXT-BASELINE-TRANSFER dry run crashed after 30 minutes on infinite scores for never-monitored episodes | Lowest-score rule written into the plan before the timestamp; smoke mode added (rule 15) |
| REVIEW-HELDOUT-FEATURES-UNSCALED | Code review found the leave-one-task-out test would feed the held-out type unscaled features, biasing it against internal state | Label-free normalisation from the held-out type's derivation episodes, written into the plan before the timestamp (rule 17) |
| REVIEW-WAITING-SCRIPT-RETIMESTAMP-RISK | A waiting script would have re-timestamped EXPERIMENT-DIFFICULTY-CONFOUND after its analysis started | Stopped before it could; single timestamp taken before analysis (rule 16) |
| REVIEW-DATA-COPIES-TRACKED | Hard-linked data copies were tracked in git, doubling uploads; the public snapshot push failed | Copies untracked (hash-identical to EXPERIMENT-POWERED-REPLICATION data, which remains the public record); failed snapshot commit discarded (rule 17) |
| REVIEW-FINAL-DRAFTS-OVERSTATE-INTERNAL-STATE | The audited final series drafts overstate what internal state adds (EXPERIMENT-TEXT-BASELINE-TRANSFER) | Marked superseded (archive/audit/series_final_2026-10-04/SUPERSEDED.md); claim status updated in docs/RESEARCH_PROGRAM.md |
| REVIEW-POOLED-TRANSFER-MIXES-MISCALIBRATION | EXPERIMENT-TEXT-BASELINE-TRANSFER pooled transfer AUROC mixes cross-task miscalibration with ranking | Pre-registered measure reported as is; within-task held-out AUROC reported alongside |

## Twelfth audit (2026-10-05): series v4 and EXPERIMENT-DIFFICULTY-CONFOUND, EXPERIMENT-TEXT-BASELINE-TRANSFER, EXPERIMENT-MULTILEVEL-FUSION and EXPERIMENT-STAGE-DIVERSE-LAYERING, three auditors from three companies
Prompt: archive/audit/series_audit3_prompt.txt. Reports: series_audit3_fable_2026-10-05.md (Claude Fable 5.1, repository access), series_audit3_gpt55_2026-10-05.md (GPT-5.5 via Codex, repository access), series_audit3_glm_* (GLM, evidence bundle, low effort). All three: publishable with fixes; no critical findings; every number traced or recomputed (Fable and GPT-5.5 recomputed EXPERIMENT-STAGE-DIVERSE-LAYERING from the 1,605 raw reviews).

| ID | Source | Finding | Resolution |
|---|---|---|---|
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 1 | Fable REVIEW-ASSUMED-COST-UNLABELLED | 5 ms monitor cost stated without "assumed" (regression from earlier drafts) | FIX in both parts |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 2 | GPT-5.5 REVIEW-DIFFICULTY-COUNT-INCLUDES-LENGTH, GLM REVIEW-DIFFICULTY-COUNT-INCLUDES-LENGTH | Part 1 attributed 75 to difficulty alone; 75 is difficulty plus length, difficulty alone 73 | FIX |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 3 | all three | EXPERIMENT-STAGE-DIVERSE-LAYERING resume, end and analysis times rested on uncommitted /tmp logs; pause was manual, guard never fired | FIX: run logs committed under docs/run_logs for EXPERIMENT-DIFFICULTY-CONFOUND, EXPERIMENT-TEXT-BASELINE-TRANSFER, EXPERIMENT-MULTILEVEL-FUSION and EXPERIMENT-STAGE-DIVERSE-LAYERING; README states manual stop |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 4 | Fable REVIEW-LAYERED-RECALL-COMPARISON-LOOSE | 124 described as "as many as" 123; "same recall" | FIX: one more; nearly the same |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 5 | Fable REVIEW-TEXT-READER-COLLAPSE-OVERSTATED, REVIEW-EVERY-CHECK-BEAT-JUDGE-UNTESTED, REVIEW-TRANSFER-COMPARISON-NOT-PREREGISTERED, REVIEW-EVERY-CHECK-BEAT-JUDGE-UNTESTED, REVIEW-HOLDS-LIST-OVERSTATED; GPT-5.5 REVIEW-TRANSFER-SUPPORT-PROBE-ONLY | Overstated transfer and "every check beat the judge" wording; probe vs text transfer not pre-registered; triage descriptive | FIX: probe only; tested comparisons named; descriptive labels |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 6 | Fable REVIEW-MULTIPLY-COUNT-ROUNDED-DIFFERENTLY, REVIEW-BANDED-TABLE-SUBSET-UNSTATED, REVIEW-ANALYSIS-START-UNLOGGED, REVIEW-STOP-TIME-FIGURES-INCONSISTENT; REVIEW-README-TIMESTAMP-ONE-SECOND-OFF, REVIEW-THEORY-NEXT-STEPS-STALE, REVIEW-TIMESTAMP-RULE-WORDING-INEXACT, REVIEW-CHAIN-LOGS-UNCOMMITTED | 6,000 vs 5,800; banded table covers 1,021 monitored episodes; EXPERIMENT-DIFFICULTY-CONFOUND start-time evidence; 120 vs 190 ms; EXPERIMENT-MULTILEVEL-FUSION README time; stale theory next steps; protocol rule 13 wording; uncommitted logs | FIX |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 7 | GPT-5.5 REVIEW-NOT-YET-AUDITED-STALE | "Not yet audited" stale after this audit | FIX: twelve audits; human review still pending |
| REVIEW-TWELFTH-AUDIT-OF-SERIES item 8 | GLM REVIEW-ELEVEN-AUDIT-COUNT-UNSUPPORTED, REVIEW-NEWEST-RESULTS-OUTSIDE-BUNDLE, REVIEW-OPENSHELL-VENDOR-UNCONFIRMED | Eleven-audit count unsupported; EXPERIMENT-DIFFICULTY-CONFOUND, EXPERIMENT-TEXT-BASELINE-TRANSFER, EXPERIMENT-MULTILEVEL-FUSION and EXPERIMENT-STAGE-DIVERSE-LAYERING numbers absent; OpenShell provenance | NO CHANGE: bundle gaps (all eleven audits in this file; numbers recomputed by the other two auditors; OpenShell confirmed from NVIDIA's release) |
