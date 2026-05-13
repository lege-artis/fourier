#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Render Chapter B0 Slot S3 figures from MIT-BIH ECG record 100.

Data fetched via scipy.datasets.electrocardiogram() on first run; cached
to ~/.cache/scipy-data thereafter. This script must run with network
access on the first invocation. Subsequent runs are offline.

Outputs written to docs/shad/figures/:
  fig-s3-input.png      first 10 s of the ECG trace (voltage vs time)
  fig-s3-spectrum.png   one-sided magnitude spectrum, 0..5 Hz zoom
  fig-s3-takeaway.png   spectrum 0..30 Hz with the heart-rate fundamental
                        and first three harmonics annotated

Source attribution:
  Moody, Mark. The impact of the MIT-BIH Arrhythmia Database.
  IEEE Eng Med Biol Mag 20(3):45-50, 2001.
  Goldberger et al. PhysioBank/PhysioToolkit/PhysioNet. Circulation
  101(23): e215-e220, 2000.
  Distributed under the Open Database Licence (ODbL) 1.0.

Run:
    python render_s3.py
"""
from __future__ import annotations

import pathlib

import matplotlib.pyplot as plt
import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
OUTDIR = REPO / "docs" / "shad" / "figures"


def main() -> int:
    try:
        from scipy.datasets import electrocardiogram
    except ImportError as e:
        raise SystemExit(
            "scipy not installed. Install with:\n"
            "    pip install scipy pooch matplotlib"
        ) from e

    OUTDIR.mkdir(parents=True, exist_ok=True)

    ecg = electrocardiogram()        # network on first call, cached after
    fs = 360.0                       # MIT-BIH record 100 native sample rate
    N = ecg.size
    t = np.arange(N) / fs

    # --- spectrum: one-sided, normalised ----------------------------------
    spec = np.fft.fft(ecg) / N
    freq = np.fft.fftfreq(N, d=1.0 / fs)
    half = N // 2
    f_pos = freq[:half]
    mag = np.abs(spec[:half])

    # --- input figure: first 10 seconds -----------------------------------
    show_s = 10.0
    show_n = int(show_s * fs)
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.plot(t[:show_n], ecg[:show_n], linewidth=0.7, color="#1f4e79")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("voltage (mV)")
    ax.set_title("S3 input: MIT-BIH record 100, first 10 s @ 360 Hz")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-s3-input.png", dpi=120)
    plt.close(fig)

    # --- spectrum 0..5 Hz: heart rate band --------------------------------
    fig, ax = plt.subplots(figsize=(8, 3.3))
    mask = f_pos <= 5.0
    ax.plot(f_pos[mask], mag[mask], linewidth=0.9, color="#702020")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("|X[k]| / N (mV)")
    ax.set_title("S3 spectrum: 0 to 5 Hz (heart-rate band)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-s3-spectrum.png", dpi=120)
    plt.close(fig)

    # --- takeaway: find the heart-rate fundamental + harmonics ------------
    # heart rate is typically 0.8..2.5 Hz; find the strongest peak in that band
    hr_mask = (f_pos >= 0.8) & (f_pos <= 2.5)
    f0_idx = np.argmax(mag * hr_mask)
    f0 = f_pos[f0_idx]
    bpm = f0 * 60.0

    fig, ax = plt.subplots(figsize=(8, 3.3))
    mask = f_pos <= 30.0
    ax.plot(f_pos[mask], mag[mask], linewidth=0.9, color="#1f4e79")
    for h, label in [(1, "$f_0$"), (2, "$2f_0$"), (3, "$3f_0$")]:
        ax.axvline(h * f0, color="#a02020", linestyle="--", linewidth=0.7, alpha=0.7)
        ax.text(h * f0 + 0.15, mag[mask].max() * 0.85, f"{label}\n{h*f0:.2f} Hz",
                fontsize=9, color="#a02020")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("|X[k]| / N (mV)")
    ax.set_title(f"S3 takeaway: heart rate $f_0$ = {f0:.3f} Hz ({bpm:.1f} bpm), harmonics shown")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-s3-takeaway.png", dpi=120)
    plt.close(fig)

    print(f"S3 figures rendered.")
    print(f"  N         = {N} samples")
    print(f"  fs        = {fs} Hz")
    print(f"  duration  = {N/fs:.1f} s")
    print(f"  f0        = {f0:.3f} Hz  ({bpm:.1f} bpm)")
    print(f"  out dir   = {OUTDIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
