# YB-0044 · Internal-state alarm vs real OpenShell enforcement: the commit-point race

**Status:** pre-registered (docs/PREREGISTRATION.md, commit 43b2a9a, RFC 3161 2026-10-02 18:08:17 UTC); live runs started 14.1 s later (docs/supplementary.json, from docs/mock_service_log.jsonl). **H1 and H2 supported.**

| Arm | Wrong commits stopped (of 138) | Correct commits blocked or held (of 138) |
|---|---|---|
| A, permission only (computed) | 0 | 0 |
| B, reactive block | 19 | 3 |
| C, hold until cleared | 93 | 16 |

- **H1** prevented share C minus B: +0.536 [+0.456, +0.616]. **Note: arm C stops every alarmed action by design (it releases only without an alarm), so its 93 equals the plan's 93 alarms on wrong answers and H1 was nearly guaranteed once arm B lost races.**
- **H2** in-time alarms on wrong answers still committed under B: 79.6% [72.0%, 87.1%] (74 of 93). This is the empirical finding.
- **Costs of holding:** median release delay 7.4 s (90th percentile 9.0 s; much of it OpenShell's own allow latency on this setup); 16 correct commits held: 14 with regulator alarms, 2 without (release issued on time, commit never arrived within the agent's 12 s retry window).

## Limitations and post hoc checks (eighth audit)
1. **Replay, not live inference:** precomputed alarm times from YB-0045 recordings; the agent waits the recorded answer time; no model in the loop. Only open-source OpenShell 0.1.2 was used (not NVIDIA Sentry/BlueField), on a Mac via Colima and a tunnel.
2. **Policy-transition overlap (M1):** arm B sends deny without waiting; enforcement latency in the live run varied more than in isolation (4 wins with gaps under the fastest isolated block, down to 1.31 s; 8 losses with gaps above 5.94 s). A leftover block from the previous episode may explain the short-gap wins. Re-counting them as losses: 83.9% [76.3%, 91.4%] still committed (docs/supplementary.json). H2 holds either way.
3. **Stalls (M3):** arm C had 7 gaps over 60 s between episode starts (largest 754 s at 19:45 UTC); both release timeouts are near stalls; allow-command durations were not recorded, so the timeout explanation is an inference. "0 harness failures" means every agent started.
4. The two smoke episodes (900015, 900021) are the first two plan episodes and ran before pre-registration; their outcomes are in docs/smoke_live_*.jsonl.
