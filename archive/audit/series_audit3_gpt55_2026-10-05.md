**Verdict: publishable with fixes**

No critical findings. I found several publication-fix issues, mostly wording/evidence-chain problems rather than wrong core results.

1. **P1, major**
   **Quote:** “a check that only looks at how hard the question is… caught 75 of the 138 mistakes.”
   **Evidence:** Part 1 lines 113-115. YB-0046 prereg defines the 75-count primary baseline as `difficulty_plus_length`, using difficulty features plus `log t` / elapsed tokens, not difficulty alone: `algorithms/YB-0046-difficulty-confound/docs/PREREGISTRATION.md:25-28`. Results show `difficulty_plus_length` caught 75, while `difficulty_only` caught 73: `algorithms/YB-0046-difficulty-confound/docs/results.json:45-56`.
   **Fix:** Say “a difficulty-and-length check… caught 75” and optionally add “difficulty alone caught 73.”

2. **P2, major**
   **Quote:** “My four newest tests haven't been through outside review yet. That's coming.”
   **Evidence:** Part 1 lines 296-299. The v4 README says this draft is “Under independent audit (twelfth audit)” and not for publication before fixes: `archive/audit/series_v4_2026-10-05/README.md:3`. The audit prompt identifies this as the twelfth/final pre-publication audit: `archive/audit/series_audit3_prompt.txt:1-3`.
   **Fix:** After this audit is incorporated, update to: “The four newest tests have now had AI audits; no human expert has reviewed them yet.”

3. **T1, major**
   **Quote:** “1,605 reviews between 23:18 UTC and 07:39 UTC, with one clean pause for battery and a resume…”
   **Evidence:** Part 2 lines 448-453. The committed chain log supports commit/timestamp/start only through `STAGE2_RECORDING_START`: `agr/yb0049_chain_progress.log:1-7`. The resume script supports the planned resume safeguards and shutdown state, but not the actual 03:43 resume, 07:39 end, or 07:47 analysis time: `agr/resume_yb0049.sh:3-10`. The stage-2 JSONL records contain review content and durations but no wall-clock timestamps: `algorithms/YB-0049-stage-diverse-layering/data/selfcons_yb0049_seed9.jsonl:1` and `:536`.
   **Fix:** Commit the actual `/tmp/chain49.log`, `/tmp/rec49.log`, `/tmp/resume_yb0049.log`, or per-record wall-clock timestamps. Otherwise weaken to “stage-2 recording started immediately after the 23:18:49 timestamp; 1,605 review records were committed; the pause/resume procedure is documented.”

4. **T2, major**
   **Quote:** “this version and YB-0046 to YB-0049 have not been audited” and “Next: an independent audit of these four results and of this post…”
   **Evidence:** Part 2 lines 613-616 and 660-661. Same audit-status evidence as P2.
   **Fix:** Update after this pass: “This version and YB-0046 to YB-0049 have now had AI audit review; no human expert review yet.”

5. **T3, minor**
   **Quote:** “internal state sees more than question difficulty and transfers better than text”
   **Evidence:** Part 2 lines 649-651. YB-0047 transfer support is probe-only: pooled transfer AUROC probe `0.6643 [0.6165, 0.7125]`, regulator `0.4445 [0.3921, 0.4991]`, text `0.3839 [0.3395, 0.4331]`; `H3_supported_probe: true`, `H3_supported_regulator: false`: `algorithms/YB-0047-text-baseline-transfer/docs/results.json:160-176`.
   **Fix:** Say “the hidden-state probe, not the telemetry regulator, transferred better than the trained text monitor.”

6. **R1, major**
   **Quote:** “stage-2 recording 23:18 UTC to 07:39 UTC… analysis 07:47 UTC”
   **Evidence:** Repository README repeats the unsupported exact timing: `algorithms/YB-0049-stage-diverse-layering/README.md:8-9`. The committed raw review files prove completeness and review durations, but not exact wall-clock timing.
   **Fix:** Add committed runtime logs or remove the exact end/resume/analysis times from README and Part 2.

**Checked And Found Correct**

- All 28 explicit GitHub paths in Part 2 exist in `~/Desktop/agr-public`.
- Headline result counts and intervals in Part 2 match `results.json` for YB-0045 through YB-0049.
- Raw YB-0049 recomputation: 1,605 answered episodes, 138 wrong, 584 never reached the first checkpoint, 2 wrong among those; stage-2 files contain exactly 1,605 reviews; review median/p90 reproduce 8.227 s / 20.696 s.
- RFC 3161 tokens for YB-0046 to YB-0049 decode and match the preregistration SHA-256 hashes. OTS files are present and contain Bitcoin-attestation markers, but I could not run full OTS verification because no OTS client is installed.
- Part 2’s formulas for the in-time race, thresholding, paired bootstrap, difficulty carries, TF-IDF monitor, stack, banded score, label-free normalization, and layered alarm match the referenced code.
- Literature citations in Part 2 are present in `docs/sources/CITATIONS.md` under “all read in full.”
- `docs/THEORY_AND_POSITION.md` agrees with the detailed results, with the same probe/regulator distinction noted above.