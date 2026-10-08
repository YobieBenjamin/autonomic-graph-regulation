"""Layer 3 observer: signal families, risk scoring, signed observer assertions.

This package does not import the hardware lane. It implements the wire contract
in ``hardware/docs/LANES.md`` independently and is tested against reference
values produced by the gate (see ``tests/vectors.json``).
"""

from .observer import SafetyObserver
from .scoring import FAMILY_WEIGHT, HARD_FAMILIES, score
from .signals import detect

__all__ = ["SafetyObserver", "detect", "score", "FAMILY_WEIGHT", "HARD_FAMILIES"]
