#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
probe_b1_squarewave.py -- generate and stage the S2 square-wave fixture.

Physical model:
    A 1 kHz square wave from an ideal function generator, sampled at
    50 kHz for 100 ms (5000 samples).  The waveform is generated as
    sign(sin(2 * pi * f * t)) -- the exact mathematical definition of a
    square wave, identical to what a benchtop Rigol DG1022 or similar
    would output to within ADC quantisation.

    Source / attribution:
        Analytically derived; no third-party data.  Canonical reference
        for a 1 kHz, 1 V_pk square wave at 50 kHz sample rate.

    Licence: Apache-2.0 (this file and the generated fixture CSV).

Outputs written to ./data/:
    b1_s2_squarewave.csv    full 5000-row time-series (time_s, voltage_V)
    b1_s2_head.txt          first 30 rows + first 10 one-sided spectrum bins
                            (for chapter embed)
Run:
    python probe_b1_squarewave.py
"""
from __future__ import annotations

import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

F_SIGNAL  = 1_000.0   # Hz
F_SAMPLE  = 50_000.0  # Hz
DURATION  = 0.100     # s
AMP       = 1.0       # V peak


def generate() -> tuple[np.ndarray, np.ndarray]:
    n_samples = int(F_SAMPLE * DURATION)
    t = np.arange(n_samples) / F_SAMPLE
    v = AMP * np.sign(np.sin(2.0 * np.pi * F_SIGNAL * t))
    # sign(0) = 0 at exact zero crossings -- nudge by half sample to avoid
    v = np.where(v == 0.0, AMP, v)
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
    peak_hz  = freq_h[peak_bin]
    peak_amp = mag_h[peak_bin] * 2.0   # one-sided -> two-sided
    with open(path, "w") as fh:
        fh.write(f"# S2 square-wave fixture: {F_SIGNAL:.0f} Hz, {F_SAMPLE/1e3:.0f} kHz sample rate, {DURATION*1000:.0f} ms\n")
        fh.write(f"# {n} samples total\n")
        fh.write(f"# Columns: time_s, voltage_V\n")
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
        fh.write(f"# Peak: {peak_hz:.1f} Hz,  amplitude (two-sided) = {peak_amp:.4f} V\n")


def main() -> int:
    t, v = generate()
    csv_path  = DATA / "b1_s2_squarewave.csv"
    head_path = DATA / "b1_s2_head.txt"
    write_csv(t, v, csv_path)
    write_head(t, v, head_path)

    n = len(t)
    spec = np.fft.fft(v) / n
    freq = np.fft.fftfreq(n, d=1.0 / F_SAMPLE)
    half = n // 2
    mag  = np.abs(spec[:half])
    peak = int(np.argmax(mag))

    print("=" * 60)
    print(" S2 square-wave fixture probe")
    print(f" Signal: {F_SIGNAL:.0f} Hz square wave, {AMP:.1f} V pk")
    print(f" Sample rate: {F_SAMPLE/1e3:.0f} kHz    Duration: {DURATION*1000:.0f} ms")
    print(f" Samples: {n}")
    print("=" * 60)
    print(f"[wrote]  {csv_path.relative_to(HERE)}")
    print(f"[wrote]  {head_path.relative_to(HERE)}")
    print()
    print("--- spectrum summary ---")
    print(f"  bin width : {F_SAMPLE/n:.2f} Hz")
    print(f"  peak bin  : {peak}  ({freq[:half][peak]:.1f} Hz)  |X| = {mag[peak]:.4f}")
    print(f"  harmonics (top 5):")
    top = sorted(range(half), key=lambda k: mag[k], reverse=True)[:5]
    for k in sorted(top):
        print(f"    k={k:4d}  f={freq[:half][k]:8.1f} Hz  |X|={mag[k]:.4f}")
    print("=" * 60)
    print(" Probe complete. Paste this output back to chat.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
