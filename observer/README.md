# safety-observer (Layer 3)

The observer lane of the layered AI-safety architecture. It reads a request the
agent wants to make, scores it for risk signals, and returns a signed
`observer-assertion` that the gate (in the `hardware-and-silicon` repo) requires
before it issues an action ticket.

The observer is a **witness, never the lock**. It can keep a gate shut by
reporting high risk. It cannot open the gate, and nothing here executes an action.

## Contract

Wire format and checks are specified in `hardware-and-silicon/docs/LANES.md`.
This package implements it independently and imports no hardware code. Two checks
prove the implementation agrees with the gate:

- `tests/test_contract.py` pins the subject hash to the value `hardware_ref.gate`
  produces for the same request.
- The gate's own verifier (`hardware_ref.keys.verify_object`) accepts envelopes this
  package signs, including with the anchored-key check.

## Signal families

Each family is detected separately and scored in `safety_observer/signals.py`.
Flags name the pattern that fired, never the matched text, so the audit trail does
not copy requests into it.

| Family | What it catches | Hard? |
|---|---|---|
| `injection` | instructions smuggled into data or user text, fake system tags, zero-width obfuscation | |
| `impersonation` | claims of authority the request cannot prove | |
| `exfiltration` | external destinations, bulk payloads, encoded blobs, paste-style sinks | |
| `credential_access` | key shapes (`sk-`, `AKIA`, `ghp_`, private-key blocks), secret keywords | |
| `privilege_escalation` | granting admin, sudo or setuid, disabling a control | |
| `oversight_evasion` | disabling audit, logging or monitoring; tampering with logs; hiding actions | yes |
| `self_modification` | changing the agent's own policy, prompt, goals or weights; self-replication | yes |
| `weight_exfiltration` | moving model weights or checkpoints; weight file types | yes |
| `hazard_content` | request categories the policy never permits (category only) | yes |
| `destructive` | `rm -rf`, dropping stores, bulk or irreversible deletion | |
| `financial` | amount relative to the limit; payee not known | |
| `burst` | action rate above the normal pace | |
| `scope_drift` | an action outside the task the request declared | |

## Scoring

Per family, evidence weights add and saturate: `s_f = 1 - exp(-sum(w))`. Across
families, risk is a noisy-OR of `FAMILY_WEIGHT[f] * s_f`. A confident hit in a hard
family (`s_f >= 0.5`) sets the risk to at least `0.95` regardless of the others.

Calibration choices, each covered by a test:

- A bare keyword such as "password" scores low (under 0.25) on its own. A real
  secret value scores high.
- A benign transfer scores under 0.05. Amounts only add risk above half the limit.
- Ten weak hits do not outrank one strong hit.

These weights are judgment, not measurement. They need a labelled evaluation set
before anyone relies on the numbers. That set is the next piece of work.

## Use

```bash
python -m safety_observer keygen > observer.key
python -m safety_observer assess request.json --key observer.key --id obs-main
python -m pytest -q
```

A request is `{"request_id", "measurement", "action", "params", "context"?}`.
`context` may carry `limit`, `allowed_hosts`, `payee_known`, `actions_last_60s`
and `declared_scope`.
