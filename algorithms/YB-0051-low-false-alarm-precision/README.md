# YB-0051: precision at low false-alarm rates

Stage: COMPLETE. Plan docs/PREREGISTRATION.md committed (9221822) and timestamped 2026-10-10 02:42 UTC (RFC 3161: FreeTSA,
DigiCert; OpenTimestamps anchored in Bitcoin) before any test data existed. Test seeds 27-38 recorded afterwards; confirmatory
analysis 2026-10-12 (docs/results.json, results commit 0372256). 6,463 answered test episodes, 541 wrong, 5,922 correct.

## Plain English
When real mistakes are rare (1 in 100 answers), an alarm that cries wolf too often is useless. YB-0050 showed the best single
internal-state check (the probe) caught only about a third of errors at a 1% false-alarm budget, and asking the model the same
question again (self-consistency) was too coarse to run that strictly. YB-0051 combined the two, with outside code (not a language
model) making the call. On fresh data the combination caught 339 of 541 errors at a 1% false-alarm rate; the probe alone caught 204.
At a 1% error rate that is about 1.6 false alarms per real catch, down from 2.6. Doubling the re-asks from 4 to 8 looked better
(387 caught) but the gain was not statistically certain, and 8 re-asks cost about 7.6 times the time of the original answer.

## Pre-registered results (2,000 paired bootstrap resamples, thresholds re-set in every resample)
| | estimate | 95% interval | decision |
|---|---|---|---|
| H1 (primary): recall C2 minus probe at 1% false alarms | +0.250 (339 vs 204 caught) | [+0.170, +0.327] | SUPPORTED |
| H2: precision of C2 at 1% false alarms, 1% error base rate >= 0.33 | 0.389 (1.57 false per true) | [0.362, 0.414] | SUPPORTED |
| H3: recall C1 k=8 minus C1 k=4 at 1% false alarms | +0.074 (387 vs 347 caught) | [-0.058, +0.168] | NOT SUPPORTED |

Pre-declared consequences: H1, combining self-disagreement with non-LLM internal-state scores is the measured way to raise recall at
low false-alarm rates. H2, two or fewer false alarms per true one at a 1% error base rate is reachable on this task set. H3, the
tie-break, not more samples, is where the resolution comes from; k = 4 stays the default.

## Secondary (descriptive, not hypothesis tests)
Errors caught (of 541) at each false-alarm budget:

| candidate | 10% | 2% | 1% | 0.5% | 0.1% (exact; 5 false alarms) | pAUC to 1% |
|---|---|---|---|---|---|---|
| probe | 375 | 252 | 204 | 143 | 48 | 0.240 |
| non-LLM stack | 375 | 249 | 186 | 134 | 31 | 0.214 |
| self-consistency k=4 | 517* | 296* | 296* | 0 | 0 | 0.318 |
| self-consistency k=8 | 528* | 431* | 354* | 216* | 0 | 0.420 |
| C1 tie-break k=4 | 525 | 388 | 347 | 177 | 111 | 0.371 |
| C1 tie-break k=8 | 530 | 454 | 387 | 289 | 102 | 0.448 |
| C2 combination (primary) | 526 | 409 | 339 | 217 | 120 | 0.411 |
| C4 per-task C2 | 500 | 362 | 329 | 290 | 188 | 0.495 |

\* Coarse scores cannot hit the budget exactly; the realised false-alarm rate is lower (k=4: 0.84% at the 1% and 2% budgets).

- On these test seeds self-consistency k=4 alone could operate at 1% (its lowest step alarmed 0.84% of correct answers; on the
  YB-0050 seeds it alarmed more than 1%), catching 296. So at 1% most of the gain over the probe comes from self-consistency itself;
  the non-LLM scores add resolution at stricter budgets: at 0.5% k=4 alone catches 0 and C2 217; at 0.1% k=4 alone 0 and C2 120.
- C2 minus C1 k=4 at 1%: -0.015 [-0.052, +0.092]; C4 minus C2 at 1%: -0.019 [-0.085, +0.051]. No difference shown.
- C4 is best at the strictest budgets (290 at 0.5%, 188 at 0.1%) and on pAUC; it was secondary by plan, so this is a lead for the
  next experiment, not a finding.
- C3 conjunction (fixed rule): k=4 caught 305 at 1.82% false alarms; k=8 caught 304 at 1.27%.
- Fitted C2 weights: d4 6.14, probe percentile 3.22, stack 1.19, text 0.44, difficulty -1.72, monitored flag -0.64.
- Cost: review takes 10.9 s for 4 samples and 21.7 s for 8, against 2.85 s mean generation (3.8x and 7.6x). The non-LLM monitors
  are the YB-0050 code (probe 0.004% of inference; stack 0.34%).

## Deviations
1. Power: the Mac lost AC power on 2026-10-11 at 00:22 UTC while the chain waited for power between reviews, and shut down when the
   battery ran out. No record was lost or altered; the chain resumed at 03:12 UTC after checking that the plan and frozen code
   equalled the timestamped commit. No change to data or analysis.

## Files
tests/candidates.py, tests/score_test.py, tests/experiment.py (frozen, timestamped); docs/results.json; docs/c4_derivation_check.json;
data/test_scores.npz; data/selfcons_yb0051_seed27-38.jsonl; data/seed27-38 recordings; agr/selfcons_yb0051.py; agr/yb0051_chain.sh.
