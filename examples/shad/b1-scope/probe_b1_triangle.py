#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
probe_b1_triangle.py -- generate and stage the S3 triangle-wave fixture.

Physical model:
    A 1 kHz triangle wave from an ideal function generator, sampled at
    50 kHz for 100 ms (5000 samples).  Generated as
    (2 / pi) * arcsin(sin(2 * pi * f * t)), which gives a triangle wave
    identical to what a function generator outputs.

    Contrasts with S2 (square wave): same fundamental frequency and sample
    rate, but the harmonic content falls off as 1/n^2 instead of 1/n.
    The DFT shows the same odd-harmonic series but with different amplitude
    envelope -- teaching that the DFT measures *shape*, not just frequency.

    Licence: Apache-2.0 (this file and the generated fixture CSV).

Outputs written to ./data/:
    b1_s3_triangle.csv      full 5000-row time-series (time_s, voltage_V)
    b1_s3_head.txt          first 30 rows + first 10 one-sided spectrum bins
Run:
    python probe_b1_triangle.py
"""
from __future__ import annotations

import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

F_SIGNAL  = 1_000.0
F_SAMPLE  = 50_000.0
DURATION  = 0.100
AMP       = 1.0


def generate() -> tuple[np.ndarray, np.ndarray]:
    n_samples = int(F_SAMPLE * DURATION)
    t = np.arange(n_samples) / F_SAMPLE
    v = AMP * (2.0 / np.pi) * np.arcsin(np.sin(2.0 * np.pi * F_SIGNAL * t))
    return t, v


def write_csv(t: np.ndarray, v: np.ndarray, path: pathlib.Path) -> None:
    with open(path, "w") as fh:
        fh.write("time_s,voltage_V\n")
        for ti, vi in zip(t, v):
            fh.write(f"{ti:.8f},{vi:.6f}\n")


def write_head(t: np.ndarray, v: np.ndarray, path: pathlib.Path) -> None:
    n = len(t)
    spec = np.fft.fft(v) / n
    freq = np.fft.fftfreq(n, d=1.0 / F_SAMPLE)
    half = n // 2
    freq_h, mag_h = freq[:half], np.abs(spec[:half])
    peak_bin = int(np.argmax(mag_h))
    with open(path, "w") as fh:
        fh.write(f"# S3 triangle-wave fixture: {F_SIGNAL:.0f} Hz, {F_SAMPLE/1e3:.0f} kHz sample rate, {DURATION*1000:.0f} ms\n")
        fh.write(f"# {n} samples total\n")
        fh.write("# Columns: time_s, voltage_V\n")
        fh.write("#\n")
        fh.write("# --- first 30 rows ---\n")
        fh.write(f"{'time_s':>14s}  {'voltage_V':>12s}\n")
        for i in range(30):
            fh.write(f"  {t[i]:12.8f}  {v[i]:12.6f}\n")
        fh.write(f"  ... ({n - 30} more rows)\n")
        fh.write("#\n")
        fh.write("# --- first 10 non-zero one-sided spectrum bins ---\n")
        fh.write(f"{'freq_Hz':>10s}  {'|X|/Xpk':>12s}\n")
        nz = [(freq_h[k], mag_h[k]) for k in range(half) if mag_h[k] > 0.01 * mag_h[peak_bin]][:10]
        for f_hz, m in nz:
            fh.write(f"  {f_hz:8.1f}  {m / mag_h[peak_bin]:12.6f}\n")
        fh.write(f"#\n")
        fh.write(f"# Peak: {freq_h[peak_bin]:.1f} Hz,  |X| = {mag_h[peak_bin]:.4f}\n")


def main() -> int:
    t, v = generate()
    csv_path  = DATA / "b1_s3_triangle.csv"
    head_path = DATA / "b1_s3_head.txt"
    write_csv(t, v, csv_path)
    write_head(t, v, head_path)

    n = len(t)
    spec = np.fft.fft(v) / n
    freq = np.fft.fftfreq(n, d=1.0 / F_SAMPLE)
    half = n // 2
    mag  = np.abs(spec[:half])
    peak = int(np.argmax(mag))

    print("=" * 60)
    print(" S3 triangle-wave fixture probe")
    print(f" Signal: {F_SIGNAL:.0f} Hz triangle wave, {AMP:.1f} V pk")
    print(f" Sample rate: {F_SAMPLE/1e3:.0f} kHz    Duration: {DURATION*1000:.0f} ms")
    print(f" Samples: {n}")
    print("=" * 60)
    print(f"[wrote]  {csv_path.relative_to(HERE)}")
    print(f"[wrote]  {head_path.relative_to(HERE)}")
    print()
    print("--- spectrum summary ---")
    print(f"  bin width : {F_SAMPLE/n:.2f} Hz")
    print(f"  peak bin  : {peak}  ({freq[:half][peak]:.1f} Hz)  |X| = {mag[peak]:.4f}")
    print(f"  harmonics (top 7, odd only for triangle):")
    top = sorted(range(half), key=lambda k: mag[k], reverse=True)[:7]
    for k in sorted(top):
        print(f"    k={k:4d}  f={freq[:half][k]:8.1f} Hz  |X|={mag[k]:.6f}")
    print("=" * 60)
    print(" Probe complete. Paste this output back to chat.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
