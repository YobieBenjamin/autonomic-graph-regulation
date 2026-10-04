# Fact-check audit: Part 1 (plain English) and Part 2 (technical), 2026-10-04

## Verdict: publishable with fixes

**No critical findings.** No experimental number is wrong, no retracted claim has come back, and the drafts have no material overstatement of the results.

- **Numbers:** every experimental figure in both drafts matches a committed file. I recomputed the YB-0044 figures from the per-episode files (`live_B.jsonl`, `live_C.jsonl`, `replay_plan.json`). That covers 19/74/93, 3 and 16 (14 + 2), 8.4/2.9/8.2 s, the four short-gap wins, eight slow losses, 7.42/8.98 s on 167 released commits, and 68/93 plan gaps. Everything matched.
- **Other experiments:** YB-0045, YB-0042, YB-0035 and YB-0031 all match their result files. So do the timestamps (checked against the RFC 3161 tokens), audit counts 1–9, model sizes, judge timing, per-token timing, feature counts (240 + 74 + log t) and hyperparameters.
- **Public paths:** all 22 GitHub paths cited in Part 2 exist in the public snapshot, which is at private commit d9deaee.
- **What needs fixing:** the citation evidence, and a few small consistency and wording points.

## Part 1

**P1 (minor). "Reading the inside of the AI … (between 2.5 and 2.9 times as many in each…)" (lines 127–131)**
- The 2.5–2.9× range is true only for the regulator (28/11, 35/12, 31/12).
- "Reading the inside" also covers the probe, whose per-seed ratios are 2.7–3.2× (30/11, 38/12, 32/12).
- Evidence: `YB-0045…/docs/posthoc_per_seed.json`.
- **Fix:** "My watchdog caught between 2.5 and 2.9 times as many…"

**P2 (minor). "checked nine times by AI reviewers, most recently by three AI systems from three different companies" (lines 257–259)**
- One of the three, gpt-oss-120b, is not independent: it is the judge in the experiments and helped write code. Most of its findings were also incorrect (CORRECTIONS.md line 233). Part 2 discloses this; Part 1 does not.
- The most recent check was actually the citation verification (CORRECTIONS.md line 248).
- **Fix:** add "(one of them, gpt-oss-120b, is not independent of this work)" and mention the citation check.

**P3 (minor). "the three tests I committed to in advance" (line 265); Part 2 subtitle "three pre-registered tests"**
- YB-0044 was also pre-registered (commit 43b2a9a, RFC 3161 stamp at 18:08:17 UTC).
- **Fix:** "three monitoring tests, plus a fourth with NVIDIA's tool, all written down in advance."

**P4 (minor). "the AI can't be one of them" (lines 280–281)**
- This contradicts lines 211–212 and 217 ("A second opinion after the fact…"; "The AI can give a second opinion on its own finished work"). That wording was the fix for ninth-audit finding T1, and this line was missed.
- **Fix:** "…and the AI can't be the lock on its own actions."

## Part 2

**T1 (major). Yeung, Botvinick and Cohen 2004 cannot be verified as cited (lines 82–87)**
- The registry URL (`CITATIONS.md` #5, uvic.ca PDF) returns 404. I re-checked it today, so readers cannot open it.
- The uncommitted `fulltext_verification.json` records that fetch as failed (404).
- The registry supports only "ERN timing, about 100 ms". The draft adds four more claims: generated in anterior cingulate cortex; begins around the time of the error; explicit report takes several hundred ms; the paper reviews the original reports.
- **Fix:** replace the URL with the DOI (Psychological Review 111(4):931), read the full text, and record each claim it supports. Otherwise trim the sentence to "the ERN peaks roughly 100 ms after an error".

**T2 (major). Part 2 cites sources the registry records below full-text level**
- Logan & Cowan 1984 is #1, recorded as "abstract; author full-text PDF available".
- Farquhar et al. 2024 is #20, recorded as "bibliographic".
- Chiba & Krichmar 2020 is #26, recorded as "open access".
- The uncommitted verification file shows all three were read in full, so the fix is to the registry, not the post.
- **Fix:** update the access levels in `CITATIONS.md` and commit the verification evidence (see R1).

**T3 (minor). Sparrow 2007 "has its critics" (lines 397–398)**
- CV-5 required adding Champagne & Tonkens 2015 and Robillard 2018. Neither is named.
- Both are abstract-only in the registry, which conflicts with the full-text rule.
- **Fix:** get their full texts and name them, or log CV-5 as changed to "unsourced caveat".

**T4 (minor). "Byrnes, 2022, revised 2024, blog series" (line 478)**
- "Revised 2024" is not in the registry (#27 says Jan–May 2022) and has no verification record.
- **Fix:** drop "revised 2024", or source it and add it to the registry.

**T5 (minor). "That is the Swiss cheese model" (line 353)**
- This is not attributed and is not in the registry.
- **Fix:** cite Reason (1990/2000) and register it, or drop the name.

**T6 (minor). Some author lists are not confirmed by the verification text**
- "Oladri, Jawahar and Mohamed": the extracted text confirms the arXiv number and the first two authors, but not "Mohamed".
- "Petrie and Aarne": neither name appears in the extracted text.
- **Fix:** confirm against the arXiv author lines for 2607.21433 and 2506.03409.

**T7 (minor). "charges each monitor its measured compute … a fixed 5 ms per regulator check, against 4.1 ms measured" (lines 159–163)**
- The regulator is charged a fixed cost, and the probe's cost is assumed.
- The 4.1 ms comes from YB-0033 (`docs/results.json` median 0.00405 s) and excludes recorder overhead (CORRECTIONS m12).
- **Fix:** "charges each monitor a compute cost … a fixed 5 ms (4.1 ms measured in YB-0033, excluding recorder overhead)".

**T8 (minor). "YB-0035, seed 7: the first fresh test" (line 177)**
- This conflicts with line 42, which calls YB-0031 "a fresh test set".
- **Fix:** "the first fresh test of the corrected race".

**T9 (minor). "Permission gate (OpenShell): stopped 0 of 138" (line 358)**
- This is arm A, which was computed, not run.
- **Fix:** add "(computed)".

**T10 (minor). "The ninth audit, of these final drafts" (line 422)**
- The ninth audit reviewed the 10-03 drafts (`post_technical_v11.md`, `post_plain_linkedin.md`).
- These 10-04 drafts differ by roughly 210 and 164 diff lines, including the citation rewrites. Section 10 also never mentions the citation verification (CV-1 to CV-9).
- **Fix:** "of the previous drafts; a citation verification followed (CORRECTIONS CV-1–CV-9)". Ideally, also run a short audit of the diff.

**T11 (minor). "Fixed: … a prose-versus-code population mismatch …, a training-size omission" (lines 435–437)**
- Both were disclosed as deviations. The code ran unchanged (`YB-0042 README` lines 35–36).
- **Fix:** "Disclosed:" instead of "Fixed:".

**T12 (minor). "public timestamps (OpenTimestamps … plus RFC 3161 …)" (lines 128–131)**
- Read as general, this overstates. YB-0035 had no public timestamp (only GitHub server records, with about a 10 s margin). The RFC 3161 tokens for YB-0042 and YB-0045 were obtained afterwards, at 15:45 UTC (PROTOCOL rule 13).
- Part 1 correctly says "from the second test on", so the two parts are inconsistent.
- **Fix:** "public timestamps from YB-0042 on…"

**T13 (minor). "the training set was 1,609 answered episodes" (lines 195–196)**
- YB-0042's linked `results.json` shows `derivation_answered = 1031`, because it counts only episodes with hidden-state snapshots.
- **Fix:** add "(1,031 reached a checkpoint)".

**T14 (minor). "Two deviations, both disclosed" (YB-0042, line 191)**
- The README lists four deviations (the other two are contention windows and the seed-8 counts).
- **Fix:** "Four deviations disclosed; two matter here:".

**T15 (minor). "pre-registered, powered" (line 501)**
- Power was 0.77 at YB-0042's effect size (+0.175).
- **Fix:** "powered (0.77 at +0.175, above 0.99 at +0.30)".

**Unlinked number (minor).** "27 of 36 errors (75%)" (line 46) gives no experiment ID or file, yet Part 1 promises every number links to a file.
- **Fix:** cite `algorithms/YB-0015-contamination-test/README.md` (it exists in the public snapshot).

**Aron & Poldrack is accurate.** I checked the PMC full text. It says responses "can be stopped in as little as 120 ms", gives mean SSRTs of 187.4 and 189.3 ms, and describes the hyperdirect route as a candidate, not established. The only gap is the missing committed artifact (R1).

## Repository

**R1 (major). The citation verification evidence is uncommitted and contradicts the registry**
- `archive/audit/fulltext_verification.json`, `fulltext_verify.py` and `papers_inbox/` are untracked (`??`), so they are absent from the public snapshot.
- The registry says Aron & Poldrack and Yeung were checked at full text. The JSON says both fetches failed (403 and 404).
- CV-9 says "Aron and Poldrack 2006 full text" was confirmed, with no artifact behind it.
- **Fix:** commit the artifact, record how Aron was read (via PMC), and fix the Yeung row.

**R2 (minor). CORRECTIONS.md line 231 says the ninth Claude audit had "14 minor" findings.** The report has 16 (T4–T10, P6–P13, B1), and CORRECTIONS line 246 itself names 16 items.

**R3 (minor). YB-0042 counts disagree slightly across files.**
- Derivation episodes with snapshots: README and `results.json` say 1,031; `derivation_sizes.json` says 1,027.
- Seed-8 monitorable episodes: 340 versus 339.
- **Fix:** reconcile the counts or explain the difference.

**R4 (minor). YB-0042 README status line says "Two deviations disclosed below", but four are listed.**

**R5 (minor). `docs/RESEARCH_PROGRAM.md` has two stale or overstated lines.**
- Line 155 still says "A powered replication (YB-0045) is running".
- Line 152 states as fact that NVIDIA's platform "does not observe the model's internal state". The source record calls this the project's own reading.

**R6 (minor). The millisecond-quarantine claim is attributed to two different sources.** The registry (#32) gives the press release; the source note gives the agent-safety solutions page.

**R7 (minor). CORRECTIONS.md cites a token count from the wrong run.**
- Line 208 blames run 1's failure on "17,908 reasoning tokens", but 17,908 is run 2's usage.
- **Fix:** mark the run-1 cause as inferred.

**R8 (minor). Stale text in `multi_audit.py`.** It still tells auditors there were "seven earlier audits" (there were eight), and its docstring still says "v10" and "running locally in LM Studio".

**R9 (minor). The posted drafts are not in the repository.** `series_final_2026-10-04/` is untracked, so these drafts are neither committed nor public.

## Checked and correct

**YB-0045:** the full table; H1 +0.478 [+0.307, +0.560]; the per-seed intervals; per-checkpoint AUROC and the interval-separation statements; 83 vs 26; 93 and 100 at frozen thresholds; −0.081 [−0.146, −0.036]; power figures.

**Timestamps:** 14:53, 15:45 and 18:59 UTC (YB-0045); 18:08:17 UTC and the 14.1 s start gap (YB-0044).

**YB-0035 and YB-0042:** every count and interval.

**YB-0031:** 0.366 [0.304, 0.433], 0.982, 0.947 and 0.890.

**YB-0044 setup:** policy latency 5.47 s (4.99–5.94) and 3.55 s (3.08–4.01); stalls (7, largest 754 s); sensitivity 83.9% [76.3%, 91.4%].

**Model and runtime figures:** 5.6× total and 1.4× active parameters; judge timing 1.55 s median and 7.2 s 90th percentile; 14.4 ms per token over 442,306 tokens; 120 vs 2,880 values per token; thirteen protocol rules; six task types.

**Audit counts:** 38/3, 25/2, 30/1, 23/1, 11/0, 20/1 and 15/1 for audits 1–7; the eighth- and ninth-audit summaries.

**Retractions:** F1, F2, F3 and F18 are correctly summarised, and none of the retracted claims resurface in either draft.

**Descriptions of sources:** Kadavath, Orgad, Wang, Bailey, Sparrow, NEWS2, Oladri and the NVIDIA hedging are all described accurately.

Two connectors could not be used this session. Slack and Supabase need authorising (via `/mcp` or your claude.ai connector settings), and the GitHub server failed to connect with a bad Authorization header. Neither affected this audit, which used local files only.
