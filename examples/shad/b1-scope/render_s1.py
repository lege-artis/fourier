#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Render Chapter B0 Slot S1 figures from the project's own golden vector.

Source data: shared/golden-vectors/dft_n=64.json, case 'cos1_plus_cos2'.
That JSON is the verified-to-1e-13 oracle for the Fortran and C++ kernels
and is the ground-truth real-data input for the S1 pipeline slot.

Outputs written to docs/shad/figures/:
  fig-s1-input.png      time-domain plot of the 64-sample input
  fig-s1-spectrum.png   one-sided magnitude spectrum
  fig-s1-takeaway.png   annotated spectrum with peaks at k=1, k=2 labelled

Run:
    python render_s1.py
"""
from __future__ import annotations

import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
GOLDEN = REPO / "shared" / "golden-vectors" / "dft_n=64.json"
OUTDIR = REPO / "docs" / "shad" / "figures"


def load_case(path: pathlib.Path, case_name: str):
    data = json.loads(path.read_text())
    case = data["test_cases"][case_name]
    x = np.array([complex(re, im) for re, im in case["input"]])
    X_expected = np.array([complex(re, im) for re, im in case["output"]])
    return data["N"], x, X_expected


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    N, x, X_expected = load_case(GOLDEN, "cos1_plus_cos2")
    spec = np.fft.fft(x)
    err = float(np.max(np.abs(spec - X_expected)))
    assert err < 1e-13, f"S1 oracle disagreement: {err:.3e}"

    half = N // 2
    bins = np.arange(half)
    mag = np.abs(spec[:half])

    # ---- input figure ----
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.plot(np.arange(N), x.real, marker="o", linewidth=1.0, color="#1f4e79", markersize=3.5)
    ax.set_xlabel("sample index $n$")
    ax.set_ylabel("$x[n]$ (real part)")
    ax.set_title("S1 input: $x[n] = \\cos(2\\pi n / 64) + \\cos(4\\pi n / 64)$")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-s1-input.png", dpi=120)
    plt.close(fig)

    # ---- spectrum figure ----
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.stem(bins, mag, basefmt=" ", linefmt="#702020", markerfmt="o")
    ax.set_xlabel("frequency bin $k$")
    ax.set_ylabel("$|X[k]|$")
    ax.set_title("S1 spectrum (one-sided, unnormalised)")
    ax.set_xlim(-0.5, half - 0.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-s1-spectrum.png", dpi=120)
    plt.close(fig)

    # ---- takeaway figure ----
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.stem(bins, mag, basefmt=" ", linefmt="#1f4e79", markerfmt="o")
    ax.axhline(N / 2, color="#a02020", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.annotate(f"peaks at $k=1, k=2$\n|X|=N/2={N//2}",
                xy=(2, N / 2), xytext=(8, N / 2 * 0.95),
                fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#a02020", linewidth=0.8))
    ax.annotate(f"oracle agreement\nmax err = {err:.2e}",
                xy=(half - 1, 1), xytext=(half * 0.5, 6),
                fontsize=9, color="#2e6e3a")
    ax.set_xlabel("frequency bin $k$")
    ax.set_ylabel("$|X[k]|$")
    ax.set_title("S1 takeaway: two clean peaks, machine-epsilon agreement with oracle")
    ax.set_xlim(-0.5, half - 0.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-s1-takeaway.png", dpi=120)
    plt.close(fig)

    print(f"S1 figures rendered.")
    print(f"  N        = {N}")
    print(f"  max err  = {err:.3e}   (gate: 1e-13)")
    print(f"  peaks    = bins {np.argsort(mag)[-2:][::-1].tolist()}")
    print(f"  out dir  = {OUTDIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
