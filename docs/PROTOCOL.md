# Research protocol (Phase D, 2026-09-30)

Rules every experiment follows. Each rule exists because of a specific failure recorded in CORRECTIONS.md.

1. **Pre-register code, not just prose.** Hypotheses, decision rules, the complete analysis code and a dry run are
   committed and pushed before the test data exists; the recording chain waits until GitHub confirms that commit.
   *(F11)*
2. **Fresh test sets are touched once.** Re-running an analysis is allowed only after a crash that produced no visible
   result, and is logged as a deviation. Test sets used by earlier analyses become derivation data. *(YB-0031 crash)*
3. **No number without an artifact.** Every number in a report, the ledger, the history or a blog post comes from a
   committed script and output file. Ad hoc calculations are not cited. *(F21, S3)*
4. **Verify before claiming.** Words like 'verified', 'proved' or 'confirmed' appear only after the check has run and
   its output is committed. *(S2, F7)*
5. **Early-warning claims face mandatory controls.** Monitors are compared at matched (at most 10%) false-alarm rates
   with thresholds re-set in every bootstrap resample, and must beat question-type and length-only baselines, with
   never-answered episodes as a pre-declared sensitivity analysis. *(F1, F2, F5, F8-F10, F16)*
6. **No information from the future.** Features, normalization and checkpoints use only what a real-time monitor
   could know at that moment. *(YB-0032 look-ahead)*
7. **Run alone, and record the environment.** Recordings and timed monitors run with no other heavy job
   (agr/runguard.py refuses to start otherwise; overrides are recorded); every run writes an environment snapshot
   under data/agr/env/. *(S1)*
8. **Telemetry synchronization is tested before every recording.** agr/test_layertap_alignment.py (and the
   per-model variants) must pass; recording chains abort otherwise. *(F4)*
9. **Local verification mirrors CI.** Both run 'make verify': every test, plus the full experiment of each algorithm
   whose code, tests, data or Makefile changed (scripts/changed_algorithms.sh). Placeholder tests must say what they
   are. *(S4, F36)*
10. **Independent audit before major claims.** A separate, read-only session audits the repository blind before a
    result is presented externally; its report is archived unedited in archive/audit/.
11. **Corrections are logged, never silent.** Errors go in CORRECTIONS.md; historical reports keep their text and
    carry a correction banner. Changes to a test's pass criterion are logged too.
12. **One vocabulary.** docs/GLOSSARY.md defines every term; new documents use its accepted names.
13. **Independently verifiable timing, without disclosure.** Applied with scripts/timestamp_prereg.sh, which records the commit hash and timestamps it two independent ways: OpenTimestamps (anchored in the Bitcoin blockchain via public calendars) and RFC 3161 tokens from two certificate-based timestamp authorities (FreeTSA, DigiCert), each verified. Only fingerprints leave the machine. (Added 2026-10-01; the RFC 3161 tokens for YB-0042 and YB-0045 were obtained after the fact, on 2026-10-01 15:45 UTC.) At the moment a pre-registration is committed, its commit
    hash is publicly timestamped (e.g. OpenTimestamps, anchored in a public ledger) and the hash is recorded, so anyone
    can later verify that the exact protocol existed at that time, without the content being disclosed before the
    author chooses. Reports cite server-side or third-party timestamps, never local git times alone. For YB-0035 the
    evidence is GitHub's own push and CI records, preserved in archive/audit/artifacts/c1_github_server_timestamps.json.
    *(third audit C1)*
14. **Secondary analyses of existing data are gated.** When test data already exists, the confirmatory analysis runs only through an explicit make confirmatory target after the public timestamp; make experiment (called by publish and CI) must exit without analysing. Origin: 2026-10-04, YB-0046 (the publish pipeline would otherwise have run the analysis before the timestamp).
15. **Smoke test before dry run.** Every analysis has a SMOKE mode that runs every code path on a small slice of non-test data in minutes; it must pass before the full dry run. Origin: 2026-10-04, YB-0047 (a crash surfaced only after a 30-minute dry run).
16. **One timestamp per plan, taken before analysis.** Automated chains must not re-timestamp after the analysis starts; the chain stops at the first failure and logs each step with UTC times. Origin: 2026-10-04, YB-0046.
17. **Reused data is referenced, not duplicated, and reused code is checked for silent fallbacks.** Analyses that reuse recordings read a hash-verified local link and do not track a second copy; reused normalisation code is reviewed for unseen-category fallbacks. Origin: 2026-10-04 (duplicated data broke the public push; YB-0045 code silently leaves unseen task types unnormalised, found in YB-0047 review).

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
