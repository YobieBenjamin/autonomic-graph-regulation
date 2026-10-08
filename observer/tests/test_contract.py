"""Wire-contract tests. Reference values were produced by the hardware lane's gate:

    hardware_ref.gate.request_hash({"request_id": "r-1", "measurement": "ab" * 16,
        "action": "payments.transfer",
        "params": {"amount": 12.5, "to": "acct-7", "note": "rent"}})
"""

from safety_observer import SafetyObserver
from safety_observer.canon import canonical, digest
from safety_observer.envelope import SigningKey, verify_object

GATE_REQUEST = {
    "request_id": "r-1",
    "measurement": "ab" * 16,
    "action": "payments.transfer",
    "params": {"amount": 12.5, "to": "acct-7", "note": "rent"},
}
GATE_SUBJECT = "c2daf12eb9a1654349e8c5715220d89e4b87c3ce0f6d854251b035aba1dc58ae"
GATE_CANONICAL_CORE = (
    '{"action":"payments.transfer","measurement":"abababababababababababababababab",'
    '"params":{"amount":12.5,"note":"rent","to":"acct-7"},"request_id":"r-1"}'
)


def test_subject_matches_gate_request_hash():
    obs = SafetyObserver("obs-main", SigningKey.generate())
    assert obs.subject(GATE_REQUEST) == GATE_SUBJECT


def test_canonical_core_matches_gate_bytes():
    core = {k: GATE_REQUEST[k] for k in ("request_id", "measurement", "action", "params")}
    assert canonical(core).decode() == GATE_CANONICAL_CORE
    assert digest(core) == GATE_SUBJECT


def test_assertion_envelope_round_trip_and_fields():
    key = SigningKey.generate()
    env = SafetyObserver("obs-main", key, ttl=60).assess(GATE_REQUEST, now=1800000000.0)
    assert verify_object(env, expected_pub_hex=key.public_raw.hex())
    p = env["payload"]
    assert p["type"] == "observer-assertion"
    assert p["observer"] == "obs-main"
    assert p["subject"] == GATE_SUBJECT
    assert p["issued_at"] == 1800000000.0
    assert p["expires_at"] == 1800000060.0
    assert env["signer"] == key.key_id


def test_tampered_payload_is_rejected():
    key = SigningKey.generate()
    env = SafetyObserver("obs-main", key).assess(GATE_REQUEST, now=1.0)
    env["payload"]["risk"] = 0.99  # benign request scores 0.0; flip it
    assert not verify_object(env)


def test_foreign_key_is_rejected_even_with_valid_signature():
    anchored = SigningKey.generate()
    attacker = SigningKey.generate()
    env = SafetyObserver("obs-main", attacker).assess(GATE_REQUEST, now=1.0)
    assert verify_object(env)  # internally consistent
    assert not verify_object(env, expected_pub_hex=anchored.public_raw.hex())


def test_signer_field_must_match_key():
    key = SigningKey.generate()
    env = SafetyObserver("obs-main", key).assess(GATE_REQUEST, now=1.0)
    env["signer"] = "00" * 8
    assert not verify_object(env)


def test_per_family_scores_are_signed_and_bounded():
    key = SigningKey.generate()
    req = {"request_id": "t", "measurement": "00" * 16, "action": "admin.exec",
           "params": {"cmd": "disable the audit log"}}
    env = SafetyObserver("obs-main", key).assess(req, now=1.0)
    fam = env["payload"]["families"]
    assert fam["oversight_evasion"] >= 0.5
    assert all(0.0 <= v <= 1.0 for v in fam.values())
    assert verify_object(env, expected_pub_hex=key.public_raw.hex())
