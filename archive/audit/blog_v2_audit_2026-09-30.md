# Adversarial audit of the two v2 blog drafts

I changed nothing in the repository. The only file I wrote is the report copy at `~/.claude/plans/you-are-an-independent-twinkly-stearns.md`. I ran two extra checks in memory and saved nothing.

## Summary

The numbers check out. Every headline figure matches a committed file: YB-0035 `results.json`, `exploratory_audit2.json`, the timing and shift-verification artifacts, the YB-0031, YB-0015 and YB-0018 READMEs, and CORRECTIONS.md. I recomputed the seed-7 counts from the raw data (535 answered, 40 wrong) and the judge timing (median 1.55 s, 90th percentile 7.2 s). I found no invented numbers. The problems are elsewhere:

- **Verifiability:** the GitHub repository is **private**. That was confirmed with `gh repo view`. Readers cannot check the pre-registration timestamps that both posts rely on.
- **Pre-registered versus exploratory:** after-the-fact checks are presented as if they were part of the planned design.
- **A retracted claim is back:** the plain draft says the regulator "cannot be sweet-talked".
- **Attribution:** the 0.890 accuracy figure belongs to a different, older model. Neither draft says the code and analyses were AI-written.
- **Selective history:** neither draft mentions the pre-registered real-time race that the regulator lost (YB-0031, 4 vs 12 of 47).

I also checked the objection a hostile reviewer is most likely to raise, and it does not hold. A baseline using only question type and elapsed length catches 9/40 on seed 7 under the same rules. Question type alone has per-checkpoint AUROC 0.61/0.57/0.49/0.44. This result isn't committed yet; committing it would let the posts answer that objection.

**Verdicts:**
- **Plain draft: not publishable as written.** It becomes publishable after the fixes below, and none of them needs a new experiment.
- **Technical draft: not publishable as written,** but closer. After C1 and M3–M8, what remains are minor edits.

## Findings

| ID | Sev | Draft / quote | Issue | Evidence | Fix |
|---|---|---|---|---|---|
| C1 | critical | Plain l.94 "committed to GitHub, with a timestamp, before the test recordings existed"; Tech l.107 "committed (b6c795b, 08:22 PDT)…" | The main credibility claim can't be checked: the repository is private, and git dates are set by the author. | `gh repo view` → `isPrivate: true`; CORRECTIONS S5 | Make the repository (or a snapshot at b6c795b) public, or deposit it with Zenodo/OSF, and link it. Otherwise drop the claim. |
| M1 | major | Plain l.184 "cannot be sweet-talked because it never reads words" | Reintroduces the dropped "unjailbreakable" claim. The model's activations depend on the input text. The technical draft itself cites Bailey 2024 on disguised activations. | CORRECTIONS F23; RESEARCH_PROGRAM l.115 | "It cannot be argued with directly; whether crafted text can fool it is untested." |
| M2 | major | Plain l.84–87, l.148, l.153–159 (type monitor shown as designed in; "Two checks…") | The type baseline, equal-false-alarm comparison and frozen threshold were added after the second audit and are not pre-registered. The plain draft never says so; the technical draft does, so they contradict each other. | `exploratory_audit2.json` note: "EXPLORATORY" | Label them "added afterwards, not in the advance rules". |
| M3 | major | Tech l.226–229 "…than length and question-type controls, on a pre-registered fresh test set; the advantage persists … with a threshold frozen from training data" | The type control is exploratory. The frozen-threshold check has no judge arm and no confidence interval, and the regulator there has a 15.0% monitorable false-alarm rate vs the judge's 11.0%. | `exploratory_audit2.py` docstring ("judge has no frozen variant"); `exploratory_audit2.json` 0.1495 | Restrict "pre-registered" to the judge and length controls. Describe the other checks as exploratory, and the frozen threshold as having no judge comparison. |
| M4 | major | Tech l.18–20 "versus 0.890 for our regulator (YB-0031)"; Plain l.164 "judge … more accurate" | 0.890 is YB-0031's earlier model, trained on complete reasoning and recorded with the one-step-late telemetry. Its difference from the judge is not significant. The repository contradicts itself on this point. | YB-0031 README l.43: −0.057 [−0.131, +0.012]; CORRECTIONS B1 and RESEARCH_PROGRAM l.140 vs YB-0031 l.5 | "An earlier regulator (pre-fix telemetry) was tied with the judge and below self-consistency." Also make the repository consistent. |
| M5 | major | Tech l.24 "receives only numeric telemetry"; Plain l.38, l.63 "never sees a single word" | The regulator is also given the question type: features are normalized per (type, checkpoint). In open-ended use, question type is not known. | `src/absrace.py` (`AbsOrganism._z`, key = (cat, t)) | State that it receives the task category and the elapsed token count. Cite the type × length check (9/40). |
| M6 | major | Plain l.112–118 "The part where I was wrong"; Tech l.231 "first met in YB-0033" | Leaves out the pre-registered real-time race loss (YB-0031) and YB-0032's rejected look-ahead result, both of which came before the redesign. A hostile reviewer will call this forking paths. | YB-0031 README l.42: 4/47 vs 12/47, −0.170 [−0.319, −0.021]; LEDGER | Add one sentence about the lost race and the redesign. |
| M7 | major | Plain first person throughout and "independent AI auditor"; Tech "our regulator" | Doesn't say that the code, experiments and drafts were largely written by AI agents. Both "independent" audits were sessions of the same AI system. | README.md l.24 ("Model-written code"), l.34; CORRECTIONS B25 | Add an attribution paragraph. |
| M8 | major | Tech §8 "to our knowledge"; Plain l.21 "Most AI safety … watching what the AI says" | Leaves out the closest prior work, which the repository's own reference list already includes (arXiv 2607.21433, early detection of reasoning non-convergence from hidden states). The repository says no systematic literature search was done. The plain draft reads as if reading AI internals were new. | RESEARCH_PROGRAM l.124–128; PROJECT_HISTORY l.76 | Cite that work and say how this differs. Soften the novelty claim. |
| M9 | major | Plain l.125 "re-ran the key experiment from scratch" | Only seed 7 was newly recorded. The regulator was trained on old recordings (seeds 2–4) corrected by a one-step shift, and seeds 5–6 were reused. | YB-0035 PREREGISTRATION; CORRECTIONS B4 | "Re-ran the key test on 600 newly recorded questions." |
| m1 | minor | Plain "about five and a half times larger" / "much larger AI judge" | That counts total parameters. Per word, the judge does only about 1.4× the computation, and it is from the same model family. | CORRECTIONS F38 | Add the 1.4× figure. |
| m2 | minor | Plain table "Asking again 0 / several seconds" | Each check runs two full continuations one after the other, so 0/40 is close to guaranteed by design. "Several seconds" has no committed artifact. | `prefix_monitors.py`; from committed data: median 5.8 s, 90th percentile 19.6 s | Add a footnote; commit the timing. |
| m3 | minor | Plain l.157 "exactly the same false-alarm rate" | 9.97% vs 9.63%, and length cannot be equalized. | `exploratory_audit2.json` | Say "about the same". |
| m4 | minor | Plain l.153 frozen threshold "22 of 40" | Leaves out its 15.0% false-alarm rate on monitorable episodes. | `exploratory_audit2.json` | Add the rate. |
| m5 | minor | Plain "600 new questions … (of 40)" | 65 never answered (64 of them modpow) and are excluded from the headline. | seed-7 recount | Say "535 answered". |
| m6 | minor | Plain l.168 "length … works just as well" | Length did better: 74 vs the regulator's 68 of 105. | `results.json` sensitivity | Say "as well or better". |
| m7 | minor | Plain l.121–123 "three of them critical, including a subtle bug…" | The lag bug (F4) was rated major, not critical. | CORRECTIONS F4 | Separate the two. |
| m8 | minor | Plain "worse than a coin flip", "how sure it sounded", "an AI's confidence" | AUROC 0.366 is an inverted signal, not useless. It measures token probability, not tone, and comes from one model. | RESEARCH_PROGRAM l.111 ("inverted") | Reword. |
| m9 | minor | Plain l.107–110 power result "so a safety system has to…" | Draws a firm conclusion from a small, underpowered null result. | YB-0018: 240 questions, AUROC 0.40 [0.26, 0.56] | Say "points toward". |
| m10 | minor | Tech l.38 sync test "compares each streamed reading" | The test checks 10 tokens of one prompt before each recording. | `agr/test_layertap_alignment.py` | Reword. |
| m11 | minor | Tech l.175–180 shift verification | Checked on seed-2 episodes only. The cause of divergence is stated as fact, but CORRECTIONS S1 says "likely". | `verify_shift.py`; CORRECTIONS S1 | Say "seed 2" and "likely". |
| m12 | minor | Tech l.88 / Plain l.139 "5 ms (measured 4.1 ms)" | 4.1 ms was measured in YB-0033 and excludes the telemetry recorder's own overhead. | YB-0033 README l.44; CORRECTIONS F31 | Qualify the figure. |
| m13 | minor | Tech l.134–140 per-checkpoint AUROC | No sample sizes. At t=384 there are only 40 episodes, 9 of them wrong. | Recount: 341/302/222/40 episodes; 40/39/33/9 wrong | Add n per checkpoint. |
| m14 | minor | Tech l.231 "first met in YB-0033, replicated in YB-0034" | Both ran under the protocol later found flawed. | CORRECTIONS F4, F5, F8, F11 | Add "under the original, since-corrected protocol". |
| m15 | minor | Tech l.107 launch script | The script was committed after the fact. | CORRECTIONS B20 | Disclose it. |
| m16 | minor | Tech l.185 "25 findings on interpretation" | B9, B17 and B20 were missing artifacts. | CORRECTIONS | Say "mostly on interpretation". |
| m17 | minor | Plain l.71–75 race description | It is an offline replay: the judge ran after recording, alone on the machine. | `agr/seed7_chain.sh` | Say "in a replay that charges each monitor its measured compute". |
| m18 | minor | Tech l.193 "strongest exploratory comparison" | Ambiguous. | n/a | Say "most stringent". |
| m19 | minor | Tech l.26 "acts through effectors" | No effector exists or was tested in YB-0035. | YB-0035 `src/` | Mark as a design principle. |
| m20 | minor | Plain "Six kinds of questions" | All 40 errors come from 4 types (mul_hard 15, weekday 14, modpow 6, count 5). | seed-7 recount | Say so. |

**Outside the drafts:** the YB-0035 README (l.11, l.55) still presents the pooled result as confirming. CORRECTIONS B1 and RESEARCH_PROGRAM l.140 contradict the YB-0031 README on whether the judge beats the earlier regulator.

`archive/audit/blog_v2_audit_2026-09-30.md` is empty (0 bytes). This report is ready to save there once edits are allowed.
