# AI Early Warning Score (AI-EWS): methodology

**Author's principle.** There is no analog for judgment other than the human brain and biology; an algorithm inside a
transformer cannot create judgment calls. Safety therefore follows the template of hospital early-warning systems
(e.g., the UK's NEWS2): combine vital signs into a **graded deterioration score** that never declares 'sick' or
'healthy' but shows a **trajectory** (stable, watch, concern, urgent), so people act before the arrest, not after.

## Structure (mirrors NEWS2)
1. **Vital signs** (text-blind, read by the external biobrain): V1 reasoning uncertainty (entropy); V2 decisiveness
   (top-1 minus top-2 margin); V3 layer HRV (successive-difference variability across layers); V4 layer synchrony
   (algebraic connectivity of the layer coupling graph); V5 expert-routing decisiveness (router entropy); V6
   critical-slowing trend (rising variance and lag-1 autocorrelation); V7 accumulated load (HPA cortisol).
2. **Banded scoring 0-3 per vital**, in the risky direction only, relative to the model's own reference distribution
   on healthy (correct/acceptable) episodes of the derivation cohort: 0 within the 10th-90th percentile band; 1 beyond
   the 90th; 2 beyond the 95th; 3 beyond the 99th (for vitals where low is risky, mirrored at 10th/5th/1st).
3. **Aggregate score** S = sum of points (0-21) and a **red flag** if any single vital scores 3.
4. **Clinical risk levels** (initial, to be recalibrated on derivation data only): stable 0-4; watch 5-6 or any red flag;
   concern 7-9; urgent >= 10.
5. **Graded response** (effectors): stable = continue; watch = observe every token and log; concern = slow generation,
   raise sampling caution, request review; urgent = pause and ask a human, or halt.
6. **Serial observation**: S is computed continuously during reasoning; the trajectory and its slope are first-class output.
7. **Context modifier (B)**: a parallel appraisal of the situation's risk adjusts the escalation thresholds, the way
   clinical context changes how a given NEWS2 score is acted on.

## Validation ladder (as clinical EWS are validated)
- **Derivation cohort**: fix bands and levels (never touched again).
- **Internal validation**: held-out episodes of the same model: AUROC of S for the outcome, calibration of levels,
  efficiency curve (share of time at watch or above vs share of events caught), lead time distribution.
- **External validation**: a different model (different 'patient population'), bands re-derived only if pre-registered.
- **Prospective validation**: live, time-resolved episodes with graded outcomes (YB-0022).

## Properties to prove per version
Monotonicity (more deviation never lowers S), boundedness (0-21), per-point explainability (each point traceable to one
vital and band), and threshold stability (bands fixed from derivation data only).

<!-- © 2026 Yobie Benjamin (YB). Autonomic Graph Regulation (AGR). SPDX-License-Identifier: CC-BY-NC-4.0 (see LICENSE-DOCS.txt, NOTICE). Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 -->
