"""The Layer 3 observer: request in, signed observer assertion out."""

from __future__ import annotations

import time
from typing import Any, Mapping

from .canon import digest, request_core
from .envelope import SigningKey
from .scoring import score
from .signals import detect

DEFAULT_TTL = 60.0


class SafetyObserver:
    def __init__(self, observer_id: str, key: SigningKey, ttl: float = DEFAULT_TTL):
        self.observer_id = observer_id
        self.key = key
        self.ttl = ttl

    def subject(self, request: Mapping[str, Any]) -> str:
        """The request hash the gate computes too. A verdict is bound to this value."""
        return digest(request_core(dict(request)))

    def assess(self, request: Mapping[str, Any], now: float | None = None) -> dict:
        """Score one request and return a signed observer-assertion envelope.

        ``request`` carries request_id, measurement, action, params and an optional
        context (limit, allowed_hosts, payee_known, actions_last_60s, declared_scope).
        Context is used for scoring only and is not part of the bound subject.
        """
        hits = detect(request["action"], request["params"], request.get("context"))
        risk, flags, families = score(hits)
        issued = time.time() if now is None else now
        payload = {
            "type": "observer-assertion",
            "observer": self.observer_id,
            "subject": self.subject(request),
            "risk": risk,
            "flags": flags,
            "families": families,  # per-family strength; gate ignores unknown fields
            "issued_at": issued,
            "expires_at": issued + self.ttl,
        }
        return self.key.sign_object(payload)
