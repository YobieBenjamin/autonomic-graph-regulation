## Verdict: publishable with fixes

No Part 1 findings. Experimental numbers, tables, intervals, timestamps, public GitHub paths, and Part 1/Part 2 factual alignment checked out. I found publication-blocking-for-clean-evidence issues in the citation/repository evidence chain, not in the reported experiment results.

## Findings

### T1 — major

**Exact quote:** Part 2 says: “The error-related negativity… begins around the time of an erroneous response and peaks roughly 100 ms later… (Yeung, Botvinick and Cohen, 2004…)” and later: “every literature citation was checked against the full text of the paper.”

**Evidence:** `archive/audit/fulltext_verification.json` records `Aron & Poldrack 2006` as `FETCH_FAILED` with HTTP 403 at lines 44-50, and `Yeung, Botvinick & Cohen 2004` as `FETCH_FAILED` with HTTP 404 at lines 52-59. `docs/sources/CITATIONS.md` then asserts both were read in full at lines 10-11.

**Fix:** Add committed direct-read evidence for Aron and Yeung to `fulltext_verification.json` with passages supporting each claim, or trim the biological claims to what the committed evidence actually supports.

### T2 — minor

**Exact quote:** Part 2 cites `docs/RESEARCH_PROGRAM.md` to verify: “the regulator is not a transformer, contains none, never reads the monitored model’s text or self-report…”

**Evidence:** The cited file still says “No LLM in the safety loop” and “cannot be jailbroken or prompt-injected” at `docs/RESEARCH_PROGRAM.md` lines 16-18, while `CORRECTIONS.md` line 40 says “unjailbreakable by construction” was reworded/dropped, and `docs/RESEARCH_PROGRAM.md` line 116 says robustness to adversarial inputs is untested.

**Fix:** Replace the stale top-level wording in `docs/RESEARCH_PROGRAM.md` with the current claim: text-blind by construction, but adversarial manipulation of telemetry is untested.

### R1 — major

**Exact quote:** `CORRECTIONS.md` says Audit 1’s R1 was fixed: “Aron and Yeung recorded as read directly.”

**Evidence:** `archive/audit/fulltext_verification.json` still records Aron as `FETCH_FAILED` at lines 44-50 and Yeung as `FETCH_FAILED` at lines 52-59, with empty passages.

**Fix:** Either update the verification artifact to record the direct reads and supporting passages, or change `CORRECTIONS.md` to say the registry was manually updated but the verification artifact remains incomplete.

## Checked And Found Correct

- Audit 1 fixes mostly landed in the drafts: Part 1 now discloses gpt-oss-120b non-independence, uses “lock on its own actions,” and describes three monitoring tests plus OpenShell.
- All explicit Part 2 GitHub `blob/main` paths I extracted exist in `/Users/yobie_benjamin/Desktop/agr-public`.
- YB-0045 table matches `docs/results.json`: 100 / 94 / 39 / 31 / 28 of 138, FPRs, H1 +0.478, probe comparisons, per-seed post hoc results, power, AUROCs, and never-answered sensitivity.
- YB-0035 and YB-0042 counts and intervals match their result files.
- YB-0044 recomputation from JSONL matches: arm B stopped 19, lost 74 of 93 alarmed wrong cases; arm C stopped 93, held 16 correct; 14 false-alarm holds plus 2 unexplained holds; median release delay 7.419 s.
- Public snapshot includes the final draft files and the full-text verification files.
- No retracted experimental claim resurfaced in the drafts themselves.