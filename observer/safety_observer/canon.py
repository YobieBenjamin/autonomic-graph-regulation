"""Canonical JSON and digests, as specified in LANES.md."""

import hashlib
import json
from typing import Any


def canonical(obj: Any) -> bytes:
    """Sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj: Any) -> str:
    """Hex SHA-256 of the canonical encoding."""
    return hashlib.sha256(canonical(obj)).hexdigest()


def request_core(req: dict) -> dict:
    """The fields the observer's verdict is bound to (LANES.md: subject hash)."""
    return {
        "request_id": req["request_id"],
        "measurement": req["measurement"],
        "action": req["action"],
        "params": req["params"],
    }
