## Audit 2 (Claude Fable 5.1), final two-part series, 2026-10-04

### Verdict: publishable with fixes

No critical or major findings. Every experimental number in both drafts traces to a committed file, and I recomputed the YB-0044 figures from the per-episode rows and the replay plan. All 28 repository paths named in Part 2 exist in the public snapshot, which is at private commit eea6cb2 and byte-identical to the private copies of both drafts, CORRECTIONS.md, CITATIONS.md and fulltext_verification.json. All 21 literature citations in Part 2 are in the registry as read in full, and the descriptions match the sources. All Audit 1 fixes landed except one partial repository fix (R2 below). The remaining problems are an out-of-date audit count in both posts, one overstated phrase, and three small inconsistencies in the repository.

### Part 1

**P1 (minor). Audit count is already stale.**
- Quote (lines 257-259): "The work has been checked nine times by AI reviewers, most recently by three AI systems from three different companies".
- Evidence: CORRECTIONS.md line 264 logs a "Tenth audit (2026-10-04)" by Claude Opus 5.5, and this three-company pass is the eleventh. The ninth audit's finding B1 flagged the identical staleness in the previous drafts.
- Fix: "checked ten times by AI reviewers, then once more by three AI systems from three different companies before publication" (adjust the parenthetical about gpt-oss-120b to the pass it belongs to, the ninth).

### Part 2

**T1 (minor). Same stale count, twice.**
- Quotes: subtitle line 6 "nine audits"; line 415 "Nine audits. The first seven were fresh..."
- Evidence: CORRECTIONS.md lines 264-276 (tenth audit, 2026-10-04, no critical findings, 3 major, registry rebuilt).
- Fix: "Ten audits" in both places, plus one sentence after line 436: "The tenth (Claude Opus 5.5, on these drafts) found no wrong number and no critical issue; it rebuilt the citation registry so that every cited paper was read in full. A final three-company pass followed."

**T2 (minor). "Each traced to a finding" overstates the protocol.**
- Quote (line 134): "thirteen process rules, each traced to a finding".
- Evidence: docs/PROTOCOL.md. Rules 1, 3, 4, 5, 7, 8 and 9 cite finding IDs (F11; F21, S3; S2, F7; F1, F2, F5, F8-F10, F16; S1; F4; S4, F36). Rules 2, 6, 10, 11, 12 and 13 cite none.
- Fix: "thirteen process rules, seven of them traced to a logged finding", or add the finding IDs to the six rules (rule 13 to C1 and D4-M1).

### Repository

**R1 (minor). Citation-verification rows record additions that were later reversed.**
- Quote: CORRECTIONS.md line 258, CV-5 "ADD: Champagne and Tonkens 2015; Robillard 2018"; line 262, CV-9 "Nieuwenhuis 2001 (unaware errors) ... Confirmed".
- Evidence: docs/sources/CITATIONS.md lines 35-45 lists all three as removed on 2026-10-04 because the full text could not be read; neither draft names them. Only A10-T3 ("unsourced critics clause") hints at the reversal.
- Fix: append to CV-5 and CV-9 "(removed from the series 2026-10-04, full text unavailable; see CITATIONS.md)".

**R2 (minor). A10-R8 is logged as FIX but the script docstring is still stale.**
- Quote: archive/audit/multi_audit.py line 4 "gpt-oss-120b via LM Studio"; line 9 "Usage ... archive/audit/glm_audit.py"; line 10 "Outputs: archive/audit/glm_audit_prompt_v10.txt, blog_v10_audit_glm_raw.txt ...".
- Evidence: CORRECTIONS.md line 275 (A10-R8 "stale audit-script text ... FIX"); only the "eight earlier audits" string on line 32 was changed. gpt-oss-120b ran locally, not in LM Studio (line 7 says LM Studio could not load the model).
- Fix: correct the docstring, or amend A10-R8 to say only the audit-count string was fixed.

**R3 (minor). The millisecond-quarantine claim still has two attributions.**
- Quote: docs/sources/nvidia_open_agent_safety_platform.md line 9 attributes it to nvidia.com/solutions/ai/agent-safety; CITATIONS.md row 21 attributes it to the press release "stated by Jensen Huang in launch coverage".
- Evidence: CORRECTIONS.md line 275 logs A10-R6 as FIX. The drafts are safe either way ("NVIDIA claims", Part 2 lines 350-351 and 492-493), but the two records still disagree.
- Fix: name both sources in both records, or pick one.

**R4 (minor). This audit's prompt and script are untracked.**
- Evidence: `git status` shows `?? archive/audit/multi_audit_prompt_series.txt` and `?? archive/audit/multi_audit_series.py`; neither is in the public snapshot.
- Fix: commit them with the Audit 2 reports before publication, as was done for the ninth audit (CORRECTIONS.md line 234).

### Audit 1 fixes verified as landed

P1 (regulator-only 2.5-2.9x, Part 1 line 130), P2 (gpt-oss-120b non-independence, line 259), P3 (four pre-registered experiments, line 267), P4 ("lock on its own actions", line 283). T1 (Yeung row with DOI and five claims; DOI resolves via doi.apa.org), T2 (Logan, Farquhar, Chiba at full text), T3 (critics clause gone, line 402), T4 (Byrnes 2022), T5 (Swiss cheese gone), T6 (author lists: arXiv 2607.21433 is Oladri, Jawahar, Mohamed; 2506.03409 is Petrie and Aarne, 2025, both confirmed live today), T7 (compute-cost wording, lines 161-165), T8 (line 180), T9 ("computed", line 361), T10 (line 427), T11 ("Disclosed rather than fixed", line 440), T12 ("from YB-0042 on", line 129), T13 (1,031, line 198), T14 (four deviations, line 194), T15 (power figures, line 509), YB-0015 link (line 46). R1 (verification JSON, script and inbox README committed and public), R2 (16 minor, CORRECTIONS line 231), R3 (count discrepancy noted in YB-0042 README line 41), R4 (four deviations), R5 (RESEARCH_PROGRAM "in our reading", no "is running"), R7 (run-1 cause marked inferred, line 208), R9 (drafts committed).

### Checked and found correct

**YB-0044 (recomputed from live_B.jsonl, live_C.jsonl, replay_plan.json):** 276 episodes, 138 wrong, 138 correct; 93 alarmed wrong; arm B 19 stopped, 74 committed (79.57%), 3 correct blocked; arm C 93 stopped, 16 held (14 with alarms, 2 without); won-race gap median 8.38 s, lost median 2.88 s, max 8.23 s; four wins below the fastest isolated block (4.94, 4.61, 3.85, 1.31 s); 167 released commits, median 7.419 s, 90th percentile 8.98 s; every agent started; plan gaps under 5.47 s: 68 of 93 (73.1%). results.json: H1 +0.536 [+0.456, +0.616]; H2 79.6% [72.0%, 87.1%]. supplementary.json: 83.9% [76.3%, 91.4%]; 7 stalls, largest 753.9 s; first start 14.1 s after the stamp. reload_timing.json: deny 5.465 (4.99-5.943), allow 3.551 (3.081-4.013), 20 cycles, 0 failures, 50 ms client, OpenShell 0.1.2. Pre-registration: numpy seed 44, smoke episodes 900015 and 900021, 12 s retry window. RFC 3161 tokens (DigiCert and FreeTSA) both 2026-10-02 18:08:17 GMT; OpenTimestamps Bitcoin-anchored (block 969631).

**YB-0045:** derivation 5,365; test 1,605 and 138; the full table (caught 100/94/39/31/28; FPR 9.95/6.27/5.25/7.02%; monitorable 16.5/10.4/8.7/11.6%; shares 72/68/28/22/20%); H1 +0.478 [+0.307, +0.560]; probe minus judge +0.522 [+0.363, +0.606]; regulator minus probe −0.044 [−0.128, +0.024]; per-seed +0.405 [+0.241, +0.595], +0.469 [+0.250, +0.623], +0.404 [+0.208, +0.628] with per-seed ratios 28/11, 35/12, 31/12; 83 vs 26; frozen 93 and 100; all twelve per-checkpoint AUROCs and the interval-separation statements (regulator vs judge separate at 48, 96, 192 and overlap at 384; regulator vs probe overlap throughout); −0.081 [−0.146, −0.036]; power 0.77 at +0.175 and 1.0 at +0.30; 1,000 paired threshold-resampling bootstrap. Timestamps: OTS stamped 14:53:27Z, RFC 3161 15:45:29-30Z, first seed-9 recording 18:59:33Z (from seed9_LH.jsonl.gz t_unix).

**YB-0042:** −0.025 [−0.170, +0.109]; 18, 21, 17; +0.175 [−0.061, +0.439]; 340 test episodes (300 correct), 495 all correct; 1,609 and 1,031 vs 5,367.

**YB-0035:** 535 and 40; 23 (FPR 9.9%, monitorable 16.3%), judge 11, length 9, type 6 (exploratory), self-consistency 0; +0.300 [+0.049, +0.487]; +0.350 [+0.128, +0.544]; pre-registration b6c795b.

**YB-0031 and YB-0015:** 0.3657 [0.3044, 0.4329]; 0.9818, 0.9471, 0.8897; YB-0031 test seed 3 was fresh; 27 of 36 (75%) with retraction banner intact.

**Instruments and method:** 24 layers, 32 experts, 5 channels giving 120 values; features 24 × 5 × 2 = 240 plus 2 × 37 = 74 graph features; W, S, LAG = 24, 8, 3; C = 0.1; probe layers (6, 12, 18, 23) with grouped 5-fold CV; 5 ms fixed vs 0.00405 s measured in YB-0033; judge 1.546 s median and 7.179 s 90th percentile; 5.59x total and 1.42x active parameters; 14.44 ms over 442,306 tokens; 2,880 vs 120; six task categories (add_hard, count, modpow, mul_easy, mul_hard, weekday); FreeTSA and DigiCert in the timestamp script; 13 protocol rules.

**Audit record:** 38 (3 critical) in the first audit; 25/2, 30/1, 23/1, 11/0, 20/1, 15/1; eighth Claude 3/8/12; GLM 86 checked, 71 verified, 15 findings (1 major, 14 minor); ninth Claude 1 critical, 7 major, 16 minor; ninth summary sentence; eleven removed citations.

**Citations:** all 21 in Part 2 are in the registry at full text; descriptions of Kadavath, Logan and Cowan, Aron and Poldrack, Yeung, Chiba and Krichmar, NEWS2, Orgad, Wang, Oladri, Goldowsky-Dill, Bailey, Sparrow, Petrie and Aarne, Byrnes and NVIDIA match the recorded claims.

**Retractions and framing:** F1, F2, F3, F18 and F23 do not resurface; "unjailbreakable" absent, with the untested-attack caveat in both parts; YB-0044 framed as a replay with no model in the loop, arm C by design, arm A computed; Part 1 and Part 2 agree on 5.5x and 1.4x, 138/100/94/28, 93 and 74, 5.5 s, 7 s median, 16 held, "from the second test on", and the model-is-not-the-lock conclusion.

Note: the Slack and Supabase connectors need authorisation and the GitHub server failed to connect this session. None was needed; this audit used local files plus three live arXiv and DOI fetches.
