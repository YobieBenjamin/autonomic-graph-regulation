# YB-0023 · The real-time race: who warns before the answer, counting their own compute time?

> **Corrections (2026-09-30; see [CORRECTIONS.md](../../CORRECTIONS.md)):** The exploratory matched-false-alarm lead did not replicate on fresh data (YB-0031); the question was settled by YB-0033 to YB-0035. F4 applies to its telemetry.

**Status:** tested · **Verdict:** pre-registered rule ⚠️ flawed (it declared an organism win without controlling false alarms: the organism alarmed on 66% of correct answers). Exploratory at matched 10% false alarms: the deep organism caught 11 of 21 wrong answers in time vs 6 for the LLM judge (+0.24, CI −0.05 to +0.52, not significant) at about 700x less compute.
**Reproduce:** `make` here (sandbox), then `PYTHONPATH=.:src python3 tests/exploratory_matched_fpr.py` for the exploratory analysis.

## 1. Plain English
A biobrain chip must act before the model's answer goes out. So we held a race: at 25%, 50% and 75% of the model's reasoning, each monitor could look at what existed so far, and its warning only counted if it finished computing before the answer was emitted, timed on this Mac.

Our pre-registered scoring rule turned out to be flawed: it compared how many wrong answers each monitor caught but let the organism keep a threshold that fired on two-thirds of correct answers too. By that rule the organism 'won', which we do not accept. Holding every monitor to the same 10% false-alarm rate (an analysis added afterwards, so exploratory), the deep 24-layer organism caught 11 of 21 wrong answers in time; the 120-billion-parameter judge caught 6; self-consistency caught 3. The organism needed 2.4 milliseconds per check; the judge needed 1.7 seconds. It is the first comparison where the organism leads, in exactly the setting a real-time chip lives in, but with 21 errors the lead is not statistically proven. It must be confirmed on fresh data (YB-0031).

## 2. Theory
A regulator coupled to an accelerator is useful only if its signal arrives before the output is emitted. Behavior monitors need text and compute; the organism needs a few microseconds of numeric work per token.

## 3. Mathematics and proofs
Checkpoints k_f = ⌊f · final_start⌋ for f ∈ {0.25, 0.5, 0.75}. Time at checkpoint t_f = Σ_{i<k_f} ℓ_i and deadline D = Σ_{i<final_start} ℓ_i, using the original recording's per-token latencies ℓ_i. A monitor's alarm at f is valid iff score > threshold and t_f + c_f ≤ D, where c_f is its measured compute time (judge and self-consistency run alone on a quiet machine; organism timed at analysis).
**Proposition 1 (earliest valid alarm).** The first checkpoint in time order that satisfies validity gives the earliest in-time alarm. *By construction; tested.*
**Proposition 2 (no look-ahead).** Organism prefix features read only tokens before k_f. *Tested:* altering all later tokens leaves the prefix features unchanged.
**Exploratory matched-FPR rule.** For each monitor, in-time score m_i = max over valid checkpoints; threshold = 90th percentile of m_i over correct episodes; recall = share of wrong episodes with m_i above it. Paired bootstrap (1000, seed 0) over wrong episodes for the recall difference.

## 4. Code map
| File | Role |
|---|---|
| src/race.py | Checkpoints, clock, deadline validity, earliest valid alarm |
| src/*.c, src/deep.py, src/flagship.py, src/hpa.py, src/agr.py | Frozen organisms (YB-0012, YB-0019) and shared cores |
| tests/test_core.py | 5 tests: checkpoints, clock, deadline rule, earliest alarm, no look-ahead |
| tests/experiment.py | Pre-registered analysis (docs/results.json) |
| tests/exploratory_matched_fpr.py | Exploratory matched-FPR analysis (docs/exploratory_matched_fpr.json) |
| ../../agr/prefix_monitors.py | Prefix judge and prefix self-consistency with measured compute time |
| docs/PREREGISTRATION.md, docs/SPEC_NOTES.md | Rules committed before any run |

## 5. Repeatable proof
`make` and the exploratory script regenerate both JSON files identically from data/ (frozen organisms; recorded monitor outputs and timings; fixed seeds). Compute times are physical measurements on this machine.
Data fingerprints (SHA-256 prefix): layers_seed0.npz 5a619127e59a8c82; layers_seed1.npz 58c8cb914652dfe9; prefix_judge.jsonl.gz 8c2289661ce7c97a; prefix_selfcons.jsonl.gz f0a68aedaf645117; seed0_L.jsonl.gz 376eff10b53eb1b0; seed1_L.jsonl.gz 7c7d76f43cfd7b84; seed1_original.jsonl.gz 3f88c87f32afb00b; 

## 6. Results (217 held-out answered episodes, 21 wrong)
Pre-registered (per-monitor thresholds as specified): recall before deadline / false alarms on correct answers:
deep organism 76.2% / 65.8%; token organism 95.2% / 93.9%; judge 28.6% / 12.2%; self-consistency 14.3% / 1.5%.
Exploratory, matched at 10% false alarms: deep organism 11/21 (52.4%), median 3.57 s to spare, 2.4 ms per check; judge 6/21 (28.6%), 5.34 s to spare, 1.66 s per check; self-consistency 3/21 (14.3%, binary score, 1.5% false alarms), 1.22 s to spare, 2.41 s per check; token organism 0/21. Deep minus judge: +0.238 [−0.048, +0.524].
Information-matched AUROC (compute ignored) at 25/50/75%: deep organism 0.652/0.726/0.744; judge 0.704/0.775/0.773; self-consistency 0.694/0.699/0.588; token organism 0.372/0.560/0.623.

## 7. Verdict
- Pre-registered H1-RT: formally 'organism wins' but **rejected as uninformative** because the rule did not match false-alarm rates (the pre-registration's flaw, recorded below).
- Exploratory (matched false alarms): the deep organism leads the judge in time-constrained detection, not significantly.
- With equal information, the deep organism nearly matches the judge and beats self-consistency; the shallow organism collapses on partial reasoning.

## 8. Limitations
21 errors; compute times from one Mac (faster serving would help every monitor); prefixes re-tokenized from recorded text; the exploratory analysis was designed after seeing results. Confirmation is pre-registered as YB-0031 on a fresh held-out set.

## Deviations from the pre-registration
The pre-registered decision rule compared recall without controlling each monitor's false-alarm rate; organism thresholds frozen on complete reasoning were far too permissive on partial reasoning. Result retained but rejected as uninformative; the matched-FPR analysis is exploratory.

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
