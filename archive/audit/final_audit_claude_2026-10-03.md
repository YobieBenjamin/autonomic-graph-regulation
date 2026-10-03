# Ninth audit of the final blog drafts (read-only, nothing modified)

## Summary

**Numbers.** Every number in both drafts matches the committed files. I recomputed the YB-0044 figures from the per-episode files, and checked YB-0035, YB-0042 and YB-0045 against their results files and `archive/audit/artifacts/`:
- **YB-0044 arms:** 19 and 3 (arm B); 93 and 16, which is 14 + 2 (arm C).
- **YB-0044 hypotheses:** H1 +0.536; H2 79.6% (74 of 93); post hoc sensitivity 83.9%.
- **YB-0044 timings:** races won and lost 8.4 / 2.9 / 8.2 s; release delay 7.4 s median, 9.0 s 90th percentile; policy latency 5.47 s and 3.55 s; first live start 14.1 s after the stamp; seven stalls, the largest 754 s.

**Paths and audit record.** Every cited path exists and is tracked here and in `~/Desktop/agr-public`, which is the snapshot of commit 6309796. The audit counts, the GLM figures (71 of 86), the 13 protocol rules and the licences check out.

**Where the problems are:** the new biology and drone content, framing, and two eighth-audit fixes that the plain-English rewrite dropped.

**Verdicts**
- **Technical draft: not publishable as written.** No number is wrong. Once T1–T3 are fixed (wording only), it is publishable with the minor fixes.
- **Plain-English draft: not publishable as written.** It has a made-up anecdote (P1), two eighth-audit regressions (P2, P3), an overstated per-seed claim (P4) and an untested claim stated as fact (P5). After those, it is publishable with the minor fixes.

## Findings

| ID | Sev | Draft and quote | Issue | Evidence | Fix |
|---|---|---|---|---|---|
| P1 | critical | P: "the same calm confidence it used to tell me 2 + 2 = 5" | This says, as fact, that the model said 2 + 2 = 5. No such episode exists, and no task type is single-digit addition. | Task types in `agr/recorder.py`; "2 + 2" appears nowhere else in the repo | Use a real error type, e.g. "…when it got a multiplication wrong." |
| P2 | major | P: "the AI can't talk its way past it"; closing "a nervous system it can't talk its way past" | This brings back the retracted "unjailbreakable" claim without the "untested" caveat (eighth-audit fix D8-M5 lost in the rewrite). Bailey et al. 2024 shows activation monitors can be evaded. | CORRECTIONS F23, D8-M5; technical draft line 415 | "Clever wording can't argue with it directly; whether crafted text can fool its readings hasn't been tested." |
| P3 | major | P: "a much bigger AI" (three times, including the table); "about five and a half times larger" | The 1.4x active-parameter caveat (D8-m6) was never applied. Per token, the judge is only 1.42x the size of the monitored model. | `model_sizes.json`: ratio_total 5.59, ratio_active 1.42 | Add the 1.4x caveat once; drop "much". |
| P4 | major | P: "more than three times as many… That held up in each of the three separate test sets" | The regulator never reaches 3x in a single test set: 28 vs 11 (2.5x), 35 vs 12 (2.9x), 31 vs 12 (2.6x). The per-set analysis was also post hoc. | `posthoc_per_seed.json` | "More than three times overall, and clearly more in each set (checked afterwards)." |
| P5 | major | P: "ask the AI 'are you sure?' That doesn't work"; "It will happily confirm its own mistake" | The repo never tested self-verification prompting. Its own evidence points the other way: self-consistency, which re-asks the same model, was the best detector on finished answers (0.982). Kadavath et al. 2022 found self-evaluation partly works. | No such experiment in the repo; YB-0031 | "Doesn't work as a brake: re-asking catches some errors after the fact, but it's too slow and blind when the model is consistently wrong." |
| T1 | major | T gate 4 "self-consistency or an LLM judge" vs "the model under watch cannot be one of the gates" (line 355) and §13; P: "can't be on that list is the AI checking itself" | The technical draft contradicts itself: self-consistency is the monitored model checking itself. The plain draft hides the conflict by dropping self-consistency from gate 4. | Technical lines 347–356 and 457 | Say the model may give an after-the-fact second opinion but cannot be the control that gates its own action. Use the same wording in the plain draft. |
| T2 | major | T: "The empirical findings are H2 and arm C's costs" | H2 was largely predictable before the run, from files committed with the pre-registration (the replay plan's answer and alarm times, and the 5.47 s latency). From those, 68 of 93 gaps (73%) are under 5.47 s, which already clears the >0.5 bar. The run reused YB-0045 test episodes whose results were already known. | Gaps recomputed from `live_B.jsonl`, which match the plan; H2 rule in PREREGISTRATION.md | Disclose that H2's direction was foreseeable (about 73%), and that the run confirmed real enforcement behaved as predicted, with wider live latency. |
| T3 | major | T: ERN appears "including errors the person does not consciously notice (Gehring et al., 1993)" | Wrong source. Unaware-error ERN is Nieuwenhuis et al. 2001; the medial-frontal (ACC) source is Dehaene et al. 1994. Gehring 1993 named and characterised the ERN. | Own knowledge; nothing in the repo supports it | Cite Nieuwenhuis et al. 2001, or drop the clause. |
| T4 | minor | T: hyperdirect pathway "implements the stop (Aron and Poldrack, 2006)" | Overstated. Their fMRI study supports the idea and proposes the route; the anatomy is from Nambu et al. 2002. The ~200 ms SSRT figure is fine. | Own knowledge | "is thought to implement". |
| P6 | minor | P: go and stop processes "literally race" | The race is a model. Neural evidence points to an interactive race, not a literal one (Boucher et al. 2007). | Own knowledge | Delete "literally". |
| P7 | minor | P: "Your brain's brake is fast enough most of the time" | No source. Standard stop-signal tasks are set up so stopping fails about 50% of the time. | Own knowledge | Drop it, or say "about a fifth of a second". |
| T5 | minor | Both: "Damasio" with no year | Every other citation has a year. | — | Damasio 1994 or 1996. |
| P8 | minor | P: "warned in time about 93" (the table above says 94) | Two numbers, no explanation. 93 is the frozen-threshold count; 94 uses the test-set threshold. | YB-0045 results: frozen 93, caught 94 | Add "with the alarm level fixed in advance". |
| P9 | minor | P: "Next I connected the watchdog to a real safety tool" | Brings back the "connected live" wording dropped after D8-M8; the next paragraph corrects it. | `live_race.py` | "…tested its warnings against…" |
| P10 | minor | P: "too often it lands on nobody" | An empirical claim with no source; the responsibility-gap literature argues this but does not measure frequency. | Matthias 2004; Sparrow 2007 | "…it can end up landing on nobody." |
| P11 | minor | P title "Your AI Lies…"; "exactly the same confidence" | "Lies" implies intent. "Exactly the same" contradicts the post's own finding that the model was more confident when wrong (AUROC 0.366). "Your AI" generalises from one model. | YB-0031 | "the same confidence, sometimes more"; consider "Confidently Wrong" in the title. |
| P12 | minor | P: "three out of four… with 90% confidence or more" | Drops the technical draft's caveats: the measure is top-1 token probability on every answer token, and there was no base rate for correct answers. | Technical lines 35–37 | Add both caveats briefly. |
| P13 | minor | P tools list | Leaves out that gpt-oss-120b also generated some code. | README.md:51; technical line 12 | Add it to the gpt-oss-120b line. |
| T6 | minor | T: review gate "more accurate after the fact… next chance for the 45" | The accuracy figure is from YB-0031. Whether a review gate catches those 45 YB-0045 misses was not tested. | YB-0031 vs YB-0045 | Say so. |
| T7 | minor | T: judge "median 1.55 s, 90th percentile 7.2 s" | These are YB-0035 seed-7 figures; the artifact has no YB-0045 judge timing. | `judge_timing.json` | Label them "(YB-0035)". |
| T8 | minor | T §13: "NVIDIA reached the same architecture" | NVIDIA governs actions, not internals, as §7 itself says. | Technical line 238 | "…also puts enforcement outside the agent". |
| T9 | minor | T §14 list numbered 6–10 | Conversion artifact. | Technical lines 476–493 | Renumber 1–5. |
| T10 | minor | T: "docs/exploratory_audit2.json" | Does not resolve from the repo root. | Actual path: `algorithms/YB-0035-corrected-realtime-race/docs/exploratory_audit2.json` | Give the full path. |
| B1 | minor | Both: "Eight audits" / "checked eight times" | Out of date once this ninth audit is logged. gpt-oss-120b, one of this round's auditors, is the judge the regulator beat and a code contributor, so it is not independent. | README.md:51 | Update the count; note gpt-oss-120b's conflict. |

## Checked and fine

- **Eighth-audit fixes:** C1–C3, M1–M4, M6–M8, G2 and G10 are reflected in the technical draft. The incident is documented in `docs/OPENSHELL_SETUP.md`, with the caveat that the logs were not kept.
- **Citations:** Logan and Cowan 1984, Craig 2002, Matthias 2004 and Sparrow 2007 are described correctly, as are the ~200 ms SSRT and ~100 ms ERN figures.
- **Public timestamps "from the second test on":** this holds. The YB-0042 OpenTimestamps stamp is 03:15:13Z on 1 October, about one minute after its pre-registration commit and four hours before the results.

The full report is also saved at `/Users/yobie_benjamin/.claude/plans/you-are-an-independent-groovy-tarjan.md`.
