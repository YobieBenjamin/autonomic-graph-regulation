"""Layer 3 observer: signal families, risk scoring, signed observer assertions.

This package does not import the hardware lane. It implements the wire contract
in ``hardware-and-silicon/docs/LANES.md`` independently and is tested against reference
values produced by the gate (see ``observer/tests/test_contract.py``).
"""

from .observer import SafetyObserver
from .scoring import FAMILY_WEIGHT, HARD_FAMILIES, score
from .signals import detect

__all__ = ["SafetyObserver", "detect", "score", "FAMILY_WEIGHT", "HARD_FAMILIES"]
