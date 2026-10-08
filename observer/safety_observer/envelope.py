"""Ed25519 signed envelopes: {payload, signer, pub, sig} per LANES.md."""

import base64
import hashlib
import os
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .canon import canonical


def _pub_bytes(pk: Ed25519PublicKey) -> bytes:
    return pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


class SigningKey:
    def __init__(self, seed: bytes):
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be 32 bytes")
        self._sk = Ed25519PrivateKey.from_private_bytes(seed)
        self.public_raw = _pub_bytes(self._sk.public_key())

    @classmethod
    def generate(cls) -> "SigningKey":
        return cls(os.urandom(32))

    @property
    def key_id(self) -> str:
        return hashlib.sha256(self.public_raw).digest()[:8].hex()

    def sign_object(self, payload: Mapping[str, Any]) -> dict:
        payload = dict(payload)
        return {
            "payload": payload,
            "signer": self.key_id,
            "pub": self.public_raw.hex(),
            "sig": base64.b64encode(self._sk.sign(canonical(payload))).decode("ascii"),
        }


def verify_object(envelope: Any, expected_pub_hex: str | None = None) -> bool:
    """Check an envelope. If ``expected_pub_hex`` is given, the embedded key must equal it.

    An envelope carrying a different key is rejected even when its signature is
    internally valid: that is the forged-key attack a trust anchor exists to stop.
    """
    if not isinstance(envelope, Mapping):
        return False
    try:
        pub_hex = envelope["pub"]
        pub_raw = bytes.fromhex(pub_hex)
        sig = base64.b64decode(envelope["sig"], validate=True)
        payload = envelope["payload"]
    except (KeyError, ValueError, TypeError):
        return False
    if expected_pub_hex is not None and pub_hex != expected_pub_hex:
        return False
    if envelope.get("signer") != hashlib.sha256(pub_raw).digest()[:8].hex():
        return False
    try:
        Ed25519PublicKey.from_public_bytes(pub_raw).verify(sig, canonical(payload))
    except (InvalidSignature, ValueError):
        return False
    return True
