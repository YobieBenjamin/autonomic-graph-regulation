# YB-0042 · The regulator versus a hidden-state probe (and a second fresh replication against the LLM judge)

**Status:** pre-registered (docs/PREREGISTRATION.md, with the full analysis code and a dry run, docs/dryrun.json), before
any YB-0042 recording exists. **Results (seed 8): H1 not distinguishable (the probe matches the regulator); H2 not replicated (regulator vs judge interval includes zero).** Four deviations disclosed below.
**Reproduce:** `SANDBOX_MEM=12g SANDBOX_TIMEOUT=14400 sandbox/run.sh algorithms/YB-0042-probe-baseline all` (dry run: `DRY_RUN=1`).

## Plain English
Our regulator reads 120 summary vital signs per token. The obvious competitor from published work is a probe: a simple
statistical model trained on the AI's full internal state (thousands of numbers per layer). If a probe does as well as
or better than the regulator in the same race, the honest conclusion is that reading the AI's internals beats the AI
judge, but our particular vital signs add nothing. This experiment finds out, and also repeats the race against the
judge on a second, brand-new test set.

## Instruments
agr/hstap.py captures hidden states in the same pass as the telemetry (agr/layertap.py, unchanged);
agr/test_hstap_alignment.py verifies alignment and that the telemetry is unchanged (passed 2026-10-01: aligned error
0.010-0.114 vs neighbour 0.735-1.949; telemetry errors identical to the YB-0035 baseline). Chain: agr/yb0042_chain.sh.

## Results (pre-registered analysis, run unchanged; docs/results.json)
| Monitor | In time (of 40) |
|---|---|
| Probe, all four layers (secondary) | 21 |
| Probe, best single layer (primary; layer 6, C = 0.001 by derivation CV) | 18 |
| Regulator | 17 |
| LLM judge | 10 |
| Question type | 5 |
| Length | 0 |

- **H1** regulator minus probe: -0.025 [-0.170, +0.109]: **not distinguishable**. Pre-declared consequence applies: the added value of the telemetry features over a standard hidden-state probe is not supported.
- **H2** regulator minus judge: +0.175 [-0.061, +0.439]: **not replicated** on seed 8.
- Regulator minus length +0.425 [+0.048, +0.595]; minus question type +0.300 [+0.151, +0.579]. Probe minus judge +0.200 [-0.043, +0.464].
- Per-checkpoint AUROC (seed 8): t = 96: regulator 0.788 [0.706, 0.866], probe 0.758 [0.665, 0.841], judge 0.567 [0.468, 0.667]; t = 384 (47 episodes): judge 0.849 [0.733, 0.951], regulator 0.707 [0.482, 0.903].

## Deviations (disclosed)
1. **Population mismatch between pre-registration prose and code.** The committed analysis code excludes answered episodes without a hidden-state snapshot (those that finished before token 48: 195 in seed 8, all correct). The prose stated the 10% false-alarm cap over all correct test episodes. As run, the cap applied to the 300 monitorable correct episodes (stricter for every monitor equally). The code was run unchanged as pre-registered.
2. **Training-set size.** The chain recorded 600 episodes per derivation seed (100 per question type), 1,800 in total (1,609 answered; 1,031 with hidden-state snapshots, 2,779 observations). YB-0035 derivation seeds were 4,800, 600 and 600 recorded (5,367 answered), so the reduction is entirely in seed 2 (corrected per sixth audit m4; archive/audit/artifacts/derivation_sizes.json). The pre-registration did not state the size. Both monitors trained on the same data, so H1 is a fair comparison, but H2 had less power than YB-0035.
3. **Contention:** two logged windows, both during derivation recordings (a 22 s git push in seed 2; a background-priority document conversion in seed 3); see data/agr/contention_windows.txt.
4. **Seed-8 counts:** 600 recorded, 535 answered, 40 wrong; results.json reports 340 test episodes because of deviation 1 (archive/audit/artifacts/derivation_sizes.json).


**Known count discrepancy (tenth audit, R3):** derivation episodes with hidden-state snapshots are 1,031 in this README and docs/results.json but 1,027 in derivation_sizes.json; seed-8 monitorable episodes are 340 in one file and 339 in another. The cause is not established; no reported comparison depends on the difference.
