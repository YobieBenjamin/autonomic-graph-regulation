# Audit of the v4 blog drafts (fifth audit)

I changed nothing in the repository; the only file I wrote is this report, at `~/.claude/plans/you-are-an-independent-merry-rossum.md`.

## Summary

**Numbers.** All but one number in both drafts trace to a committed file, with the right scope, sign, rounding and sample. The exception is "32 routed experts" (A6), which is correct but has no committed source.

**Seed-7 timeline.** It is consistent. GitHub logged the push at 15:26:40Z. After that, the alignment log was written at 15:26:48Z, the first layer file at 15:26:50Z, and the recorder's start time is 15:26:49.955Z.

**Leakage.** I found none. No seed-7 question appears in seeds 2–6, and all 65 never-answered episodes stopped at the 800-token cap.

**Public snapshot.** It is public and up to date (HEAD b7d526d, built from private commit b0b7588), and the manifest verifies with no failures. It contains everything the drafts point readers to.

**Citation.** arXiv:2607.21433 exists, and the three author names match (Oladri, Jawahar, Mohamed; submitted 23 July 2026).

**Extra check.** The regulator is also told the question type, so I tested whether its per-checkpoint score could just be that. My own computation, not committed:

| Seed-7 checkpoint (tokens) | 48 | 96 | 192 | 384 |
|---|---|---|---|---|
| Question type alone | 0.61 | 0.57 | 0.49 | 0.44 |
| Final reasoning length (known only in hindsight) | 0.63 | 0.59 | 0.55 | 0.57 |
| Regulator | 0.70 | 0.73 | 0.80 | 0.83 |

The regulator beats both, which supports the drafts' claim.

**Verdicts:**
- **Plain draft: publishable with the listed fixes.** A1 (major, a wording change) must be fixed; the rest are minor.
- **Technical draft: publishable with the listed fixes.** A1 and A2 must be fixed (one sentence each); the rest are minor.

## Findings

| ID | Sev | Draft and quoted sentence | Issue | Evidence | Suggested fix |
|---|---|---|---|---|---|
| A1 | major | Plain: "Each audit was a separate session of an AI model, told nothing about earlier findings". Tech: "given no knowledge of earlier findings" | False for audits 2–4: they could read, and did read, the earlier findings in the repository. The posts rely on audit independence for credibility. | `blog_v3_audit_2026-10-01.md` row M4: "The third audit raised this (m8)". `CORRECTIONS.md`, which lists every earlier finding, is open to every audit. | "Each audit was a fresh, read-only session of an AI model (Claude), separate from the session that did the work; the later audits could read the earlier findings." |
| A2 | minor | Tech §6: "All three audits were separate sessions…" | The subtitle and the §6 heading both say four audits. This is the same kind of slip as the earlier finding D4-m1, in the section about rigour. | Tech subtitle and §6 heading | "All four audits…" (fix together with A1). |
| A3 | minor | Tech §6: "the regulators of YB-0012, YB-0019 and YB-0030 did not beat question-type (AUROC 0.764) or length (0.796) baselines" | YB-0019 scored 0.765, just above the question-type baseline, so read literally the sentence is false for YB-0019. | `baselines_and_breakdowns.json`: YB-0019 0.765 vs question type 0.7641. `CORRECTIONS.md` row F16 has the same slip. | "…did not beat the length baseline (0.796) and at best matched question type (0.764)." Fix F16 too. |
| A4 | minor | Plain: "Two earlier test sets, re-analysed with the corrected instruments, showed the same pattern." | The plain draft never says these sets were reused. They are where the redesign was first shown to work, so they are not independent confirmation. The technical draft says this correctly. | `CORRECTIONS.md` B4 and B5; YB-0035 README | Add "already used to develop the redesign (supporting, not independent, evidence)". |
| A5 | minor | Both drafts: the monitored model's settings ("greedy decoding") | The monitored model ran at low reasoning effort while the judge ran at medium. Neither draft says so. Effort affects reasoning length, error rate and when each checkpoint is reached. | `agr/recorder.py` line 55; `agr/prefix_monitors.py` line 45 | Tech §2: "greedy decoding, low reasoning effort". |
| A6 | minor | Tech §2: "32 routed experts per block" | Correct, but nothing committed records it, which breaks protocol rule 3 (no number without an artifact). | No match in `agr/`, `docs/` or the artifacts | Add the expert count to `model_sizes.json` from the same model card. |
| A7 | minor | Plain results table (no false-alarm column) | The regulator used more of its false-alarm allowance than its rivals: 9.9% of correct answers, against 6.7% for the judge and 6.3% for length. Among answers each could see, 16.3% against 11.0% and 10.3%. The plain draft mentions this only later, in words, without these numbers. | `results.json`, `fpr` and `fpr_monitorable` | Footnote under the table: "false alarms: regulator 10%, judge 7%, length 6% of correct answers". |
| A8 | minor | Plain: "than a much larger AI judge could"; "much larger" used twice | (a) "Could" implies a ceiling on what a judge can do, but this was one configuration (one prompt, medium effort). (b) The judge is 5.6x larger in total size but does only 1.4x the computation per token. (c) At the 48- and 96-token checkpoints the judge scored 0.54 and 0.56, below a question-type lookup (0.61 and 0.57, my computation). Critics will call it a weak competitor. | `results.json` per-checkpoint scores; `model_sizes.json` active ratio 1.42 | Plain: "…than the AI judge I tested". Tech §7: add "one judge configuration, weak at early checkpoints". |
| A9 | minor | Both subtitles: "Garbage In, Gospel Out, Part II" | There is no link to a Part I. The fourth audit (D4-m10) asked for one, and `CORRECTIONS.md` records that finding as reworded in v4, but the link is still missing. | Fourth audit row m10 | Link Part I, or drop "Part II". |
| A10 | minor | Plain: "four unforgiving audits" | Oversells audits that were all AI sessions, by the same vendor's model as the assistant that did the work. | README section "Authorship and AI assistance" | "four AI audits". |
| A11 | minor | Tech §8: "(Oladri, Jawahar and Mohamed, 2026, arXiv:2607.21433…)" | The names are correct, but the repository's own related-work list still gives only the arXiv number, so the post is ahead of the record it points to. | `docs/RESEARCH_PROGRAM.md` line 125 | Add the full reference to `RESEARCH_PROGRAM.md` before posting. |

Two of my checks used outside resources: the arXiv citation and the snapshot's public visibility on GitHub. Two MCP servers were also unavailable: Slack and Supabase need authorization, and the GitHub server failed to connect. Neither affected this audit.
