#!/usr/bin/env python3
"""
generate_golden_vectors.py — produce shared/golden-vectors/*.json from
independent oracles (NumPy + SciPy) for v0.1.0 DFT validation.

Per WORKING-SPEC-v0.3-EN.md §4.2:
  - Independent oracles serve as TESTBEDS, never source material.
  - Each golden-vector JSON includes oracle name, producing script,
    timestamp, and ε used (audit trail).
  - Where multiple oracles available, cross-check is run and any
    disagreement documented.

Usage:
    pip install --user numpy scipy
    python tools/generate_golden_vectors.py

Output:
    shared/golden-vectors/dft_n=2.json
    shared/golden-vectors/dft_n=4.json
    shared/golden-vectors/dft_n=8.json
    shared/golden-vectors/dft_n=16.json
    shared/golden-vectors/dft_n=64.json
    shared/golden-vectors/dft_n=64_cosine_leakage.json   (PT-DFT-03B testbed)

License: Apache 2.0 (this script is code, not docs).
"""

from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import json
import os
import pathlib
import platform
import sys

import numpy as np
from scipy import fft as _scipy_fft

ORACLE_VERSION = {
    "numpy": np.__version__,
    "scipy_fft": "scipy.fft (scipy " + __import__("scipy").__version__ + ")",
    "python": sys.version.split()[0],
    "platform": platform.platform(),
}

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "shared" / "golden-vectors"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Input fixtures (deterministic, reproducible across runs) ──────────────────

def gen_inputs(N: int) -> dict[str, np.ndarray]:
    """Return a dict of named complex inputs of length N for canonical use."""
    n = np.arange(N)
    inputs = {
        # Pure tones (real-valued)
        "cosine_k1":  np.cos(2 * np.pi * 1 * n / N).astype(np.complex128),
        "cosine_k2":  np.cos(2 * np.pi * 2 * n / N).astype(np.complex128),
        "sine_k1":    np.sin(2 * np.pi * 1 * n / N).astype(np.complex128),
        # Combinations
        "cos1_plus_cos2": (np.cos(2*np.pi*n/N) + np.cos(4*np.pi*n/N)).astype(np.complex128),
        # Impulse
        "impulse_at_0":   np.zeros(N, dtype=np.complex128).at_zero_helper(0) if False else _impulse(N, 0),
        "impulse_centred":_impulse(N, N // 2),
        # Constant (DC)
        "dc_one":         np.ones(N, dtype=np.complex128),
        # Linear ramp (real)
        "ramp":           np.arange(N, dtype=np.complex128),
    }
    # Length-2 special case: drop combinations / cos2 that don't fit
    if N < 4:
        for k in ("cosine_k2", "cos1_plus_cos2"):
            inputs.pop(k, None)
    return inputs

def _impulse(N: int, pos: int) -> np.ndarray:
    a = np.zeros(N, dtype=np.complex128)
    a[pos] = 1.0
    return a

# ─── DFT computation via independent oracles ───────────────────────────────────

def dft_numpy(x: np.ndarray) -> np.ndarray:
    """Oracle 1: NumPy's pocketfft via numpy.fft.fft (asymmetric forward, no 1/N)."""
    return np.fft.fft(x).astype(np.complex128)

def dft_scipy(x: np.ndarray) -> np.ndarray:
    """Oracle 2: SciPy's pocketfft via scipy.fft.fft. Should agree exactly with NumPy
    in modern versions (both back pocketfft) — cross-check confirms no environmental drift."""
    return _scipy_fft.fft(x).astype(np.complex128)

def cross_check(x: np.ndarray, name: str) -> tuple[np.ndarray, dict]:
    """Run both oracles, return primary output (NumPy) + agreement metadata."""
    X_np = dft_numpy(x)
    X_sp = dft_scipy(x)
    diff = np.abs(X_np - X_sp).max()
    agreement = {
        "max_abs_diff_numpy_vs_scipy": float(diff),
        "agree_within_eps": bool(diff < 1e-13),
    }
    if not agreement["agree_within_eps"]:
        print(f"  [WARN] {name}: oracle disagreement — diff={diff:.3e}")
    return X_np, agreement

# ─── JSON serialisation ────────────────────────────────────────────────────────

def complex_to_json(arr: np.ndarray) -> list[list[float]]:
    """[[re_0, im_0], [re_1, im_1], ...]  for JSON-friendly representation."""
    return [[float(c.real), float(c.imag)] for c in arr]

def json_from_complex(arr: list[list[float]]) -> np.ndarray:
    return np.array([complex(re, im) for re, im in arr], dtype=np.complex128)

# ─── Main: emit golden vectors per length ──────────────────────────────────────

def emit_golden_vectors(lengths: list[int]) -> None:
    for N in lengths:
        inputs = gen_inputs(N)
        bundle = {
            "schema_version": "1.0",
            "algorithm": "DFT",
            "N": N,
            "convention": "asymmetric forward (no 1/N in forward); "
                          "matches OppenheimSchafer3rd §8.2 and numpy.fft.fft",
            "precision": "double (IEEE 754 binary64)",
            "generated_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "oracles": ORACLE_VERSION,
            "producing_script": "tools/generate_golden_vectors.py",
            "epsilon_used": 1e-13,
            "test_cases": {},
        }
        for input_name, x in inputs.items():
            X, agreement = cross_check(x, f"N={N}, {input_name}")
            bundle["test_cases"][input_name] = {
                "input":  complex_to_json(x),
                "output": complex_to_json(X),
                "agreement": agreement,
                "single_oracle": False,  # both NumPy + SciPy used
            }

        out_path = OUT_DIR / f"dft_n={N}.json"
        out_path.write_text(json.dumps(bundle, indent=2))
        sha = _hashlib.sha256(out_path.read_bytes()).hexdigest()[:16]
        print(f"[OK] {out_path.relative_to(REPO_ROOT)} — {len(bundle['test_cases'])} test cases — sha256={sha}")

def emit_pt_dft_03b_leakage() -> None:
    """PT-DFT-03B testbed: cosine at non-integer frequency 5.5 over N=64.
    Captures the spectral-leakage profile for cross-check."""
    N = 64
    n = np.arange(N)
    x = np.cos(2 * np.pi * 5.5 * n / N).astype(np.complex128)
    X, agreement = cross_check(x, "PT-DFT-03B leakage")
    bundle = {
        "schema_version": "1.0",
        "testbed": "PT-DFT-03B",
        "description": "Cosine at non-integer frequency 5.5; spectral leakage profile",
        "physics_source": "Thorne2017 §6.2 + OppenheimSchafer3rd §10",
        "N": N,
        "convention": "asymmetric forward",
        "precision": "double",
        "generated_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "oracles": ORACLE_VERSION,
        "producing_script": "tools/generate_golden_vectors.py",
        "epsilon_used": 1e-13,
        "input": complex_to_json(x),
        "output": complex_to_json(X),
        "agreement": agreement,
        "single_oracle": False,
    }
    out_path = OUT_DIR / "dft_n=64_cosine_leakage.json"
    out_path.write_text(json.dumps(bundle, indent=2))
    sha = _hashlib.sha256(out_path.read_bytes()).hexdigest()[:16]
    print(f"[OK] {out_path.relative_to(REPO_ROOT)} (PT-DFT-03B leakage) — sha256={sha}")

if __name__ == "__main__":
    print(f"== generate_golden_vectors.py ==")
    print(f"   numpy:  {np.__version__}")
    print(f"   scipy:  {__import__('scipy').__version__}")
    print(f"   out:    {OUT_DIR.relative_to(REPO_ROOT)}")
    print()

    emit_golden_vectors([2, 4, 8, 16, 64])
    emit_pt_dft_03b_leakage()
    print("\nDone.")
