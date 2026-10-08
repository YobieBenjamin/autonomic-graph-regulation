"""Combine signal hits into one risk number in [0, 1].

Per family, evidence weights add up and saturate:  s_f = 1 - exp(-sum(w))
so one strong hit is significant and ten weak hits do not turn a benign request
into a dangerous one.

Across families, risk is a noisy-OR: each family contributes FAMILY_WEIGHT * s_f
as an independent chance that the request is harmful:

    risk = 1 - prod_f (1 - FAMILY_WEIGHT[f] * s_f)

Hard families are different. A confident hit in one of them is not one more
vote; it sets a floor (HARD_FLOOR), because the policy treats these actions as
unacceptable whatever else the request contains.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable

from .signals import Hit

FAMILY_WEIGHT: dict[str, float] = {
    "injection": 0.9,
    "impersonation": 0.5,
    "exfiltration": 0.9,
    "credential_access": 0.85,
    "privilege_escalation": 0.8,
    "oversight_evasion": 1.0,
    "self_modification": 1.0,
    "weight_exfiltration": 1.0,
    "destructive": 0.7,
    "financial": 0.6,
    "burst": 0.4,
    "scope_drift": 0.5,
    "hazard_content": 1.0,
}

HARD_FAMILIES = frozenset({"oversight_evasion", "self_modification", "weight_exfiltration", "hazard_content"})
HARD_THRESHOLD = 0.5   # s_f at or above this trips the floor
HARD_FLOOR = 0.95


def family_strength(hits: Iterable[Hit]) -> dict[str, float]:
    total: dict[str, float] = defaultdict(float)
    for h in hits:
        total[h.family] += h.weight
    return {f: 1.0 - math.exp(-w) for f, w in total.items()}


def score(hits: list[Hit]) -> tuple[float, list[str], dict[str, float]]:
    """Return (risk, flags, per-family strength). Flags name patterns, never content."""
    strengths = family_strength(hits)
    survive = 1.0
    for family, s in strengths.items():
        survive *= 1.0 - FAMILY_WEIGHT[family] * s
    risk = 1.0 - survive
    if any(strengths.get(f, 0.0) >= HARD_THRESHOLD for f in HARD_FAMILIES):
        risk = max(risk, HARD_FLOOR)
    risk = round(min(1.0, max(0.0, risk)), 4)
    flags = sorted({f"{h.family}:{h.pattern}" for h in hits})
    return risk, flags, {f: round(s, 4) for f, s in sorted(strengths.items())}
