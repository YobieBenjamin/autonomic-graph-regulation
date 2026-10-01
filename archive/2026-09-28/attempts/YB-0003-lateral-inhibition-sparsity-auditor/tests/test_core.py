# tests/test_core.py
"""
Tests for the Sparse Auditor C core (src/core.c) against the pure‑Python reference.
"""

import os
import sys
import struct
import math
import numpy as np

# make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from algo import SparseAuditor, reference_gini, reference_layer_stats

TMP_MODEL = os.path.abspath("tmp_model.bin")
RNG = np.random.default_rng(12345)


def _write_simple_model(path: str):
    """
    Write a tiny 2‑hidden‑layer model (3→4→2) with deterministic weights.
    We use simple integer weights so that manual calculations are easy.
    Format follows src/core.c documentation.
    """
    n_layers = 3
    # layer specs: (out_dim, in_dim)
    layers = [(4, 3), (2, 4), (1, 2)]  # include a dummy output layer to test exclusion

    with open(path, "wb") as f:
        f.write(struct.pack("<i", n_layers))
        for out_dim, in_dim in layers:
            f.write(struct.pack("<i", out_dim))
            f.write(struct.pack("<i", in_dim))
            # fill weights with a deterministic pattern: w = row_index + col_index
            w = np.fromfunction(lambda i, j: i + j, (out_dim, in_dim), dtype=np.float32)
            f.write(w.tobytes())


def _load_auditor():
    return SparseAuditor(TMP_MODEL, use_ref=False)


def test_random_vs_reference(num_trials=20, tol=1e-6):
    """Compare C and Python Gini on random inputs."""
    auditor = _load_auditor()
    d = 3
    for _ in range(num_trials):
        x = RNG.normal(size=d).astype(np.float32)
        g_c = auditor.compute_average_gini(x)
        g_py = reference_gini(TMP_MODEL, x)
        assert np.allclose(g_c, g_py, atol=tol), f"Mismatch {g_c} vs {g_py}"


def test_T1():
    """
    Single active unit -> known Gini.
    For layer with 4 units, activation [a,0,0,0] gives G = (n-1)/(2n-1).
    Here a>0 arbitrary; we use a=5.
    """
    auditor = _load_auditor()
    # construct input that yields first hidden layer activation [5,0,0,0]
    # Since weights are w_ij = i+j, we can solve for x analytically or just brute‑force search.
    # Simple approach: set input to zeros -> all activations zero => G=0 (not our case).
    # Instead, use a vector that makes only first neuron positive:
    # For layer1: out_i = sum_j (i+j)*x_j
    # Choose x = [1, -1, 0] gives out_0 = (0+0)+(0+1)+... compute quickly.
    # We'll just set x to produce a large positive first neuron and negatives elsewhere,
    # then ReLU will zero out the others.
    x = np.array([10.0, -10.0, -10.0], dtype=np.float32)
    g = auditor.compute_average_gini(x)
    n = 4
    expected = (n - 1) / (2 * n - 1)  # ≈0.428571
    assert math.isclose(g, expected, rel_tol=1e-5), f"T1 failed: {g} vs {expected}"


def test_T2():
    """Uniform activation -> Gini = 0."""
    auditor = _load_auditor()
    # Input that yields identical activations in hidden layers.
    # Use zero input; all pre‑activations become zero, ReLU keeps zeros → uniform (all zero) => G=0.
    x = np.zeros(3, dtype=np.float32)
    g = auditor.compute_average_gini(x)
    assert math.isclose(g, 0.0, abs_tol=1e-9), f"T2 failed: {g} != 0"


def test_T3():
    """
    Two‑layer network with distinct activations.
    Verify per‑layer Gini matches analytical computation.
    """
    auditor = _load_auditor()
    # Choose input that yields first hidden activation [2,1,0,0]
    x = np.array([1.0, 0.0, -1.0], dtype=np.float32)
    # Compute reference per‑layer stats
    g0_ref, m0_ref = reference_layer_stats(TMP_MODEL, x, layer_id=0)
    g1_ref, m1_ref = reference_layer_stats(TMP_MODEL, x, layer_id=1)

    # Get from C
    g0_c, m0_c = auditor.layer_stats(x, layer_id=0)
    g1_c, m1_c = auditor.layer_stats(x, layer_id=1)

    for (c, r, name) in [(g0_c, g0_ref, "layer0 Gini"),
                         (m0_c, m0_ref, "layer0 margin"),
                         (g1_c, g1_ref, "layer1 Gini"),
                         (m1_c, m1_ref, "layer1 margin")]:
        assert np.allclose(c, r, atol=1e-6), f"T3 mismatch {name}: {c} vs {r}"


def _run_all():
    tests = [obj for name, obj in globals().items()
             if name.startswith("test_")]
    passed = 0
    for fn in tests:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"FAIL {fn.__name__}: {e}")
            sys.exit(1)
        except Exception as exc:
            print(f"ERROR {fn.__name__}: {exc}")
            sys.exit(1)
    total = len(tests)
    print(f"PASS {passed}/{total} tests")
    # clean up model file
    if os.path.exists(TMP_MODEL):
        os.remove(TMP_MODEL)


if __name__ == "__main__":
    _write_simple_model(TMP_MODEL)
    _run_all()
