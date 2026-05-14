#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
probe_b1_rlc.py -- generate and stage the S4 RLC damped-transient fixture.

Physical model:
    Step response of an underdamped series RLC circuit:

        R = 2 Ohm,  L = 100 mH,  C = 100 uF

    Parameters:
        omega_0  = 1/sqrt(L*C) = 316.2 rad/s   ->  f_0 = 50.3 Hz
        alpha    = R/(2*L)     =  10.0 rad/s   ->  tau = 100 ms
        omega_d  = sqrt(omega_0^2 - alpha^2)   = 316.0 rad/s  -> f_d = 50.3 Hz

    Voltage across capacitor after step at t=0:
        v(t) = exp(-alpha * t) * cos(omega_d * t)   (normalised to 1 V initial)

    Sample rate: 2 kHz,  duration: 500 ms  ->  1000 samples.
    The oscillation at ~50 Hz decays with time constant 100 ms, giving
    ~5 clearly visible cycles before amplitude halves.

    Source / attribution:
        Analytically derived from exact solution of d^2v/dt^2 + (R/L) dv/dt
        + v/(LC) = 0.  No third-party data.

    Licence: Apache-2.0 (this file and the generated fixture CSV).

Outputs written to ./data/:
    b1_s4_rlc.csv       full 1000-row time-series (time_s, voltage_V)
    b1_s4_head.txt      first 30 rows + first 10 one-sided spectrum bins
Run:
    python probe_b1_rlc.py
"""
from __future__ import annotations

import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

R        = 2.0        # Ohm
L        = 0.100      # H
C        = 100e-6     # F
F_SAMPLE = 2_000.0    # Hz
DURATION = 0.500      # s

OMEGA_0  = 1.0 / np.sqrt(L * C)
ALPHA    = R / (2.0 * L)
OMEGA_D  = np.sqrt(max(OMEGA_0**2 - ALPHA**2, 0.0))
F_D      = OMEGA_D / (2.0 * np.pi)
TAU      = 1.0 / ALPHA if ALPHA > 0 else np.inf


def generate() -> tuple[np.ndarray, np.ndarray]:
    n_samples = int(F_SAMPLE * DURATION)
    t = np.arange(n_samples) / F_SAMPLE
    v = np.exp(-ALPHA * t) * np.cos(OMEGA_D * t)
    return t, v


def write_csv(t: np.ndarray, v: np.ndarray, path: pathlib.Path) -> None:
    with open(path, "w") as fh:
        fh.write("time_s,voltage_V\n")
        for ti, vi in zip(t, v):
            fh.write(f"{ti:.6f},{vi:.8f}\n")


def write_head(t: np.ndarray, v: np.ndarray, path: pathlib.Path) -> None:
    n = len(t)
    spec = np.fft.fft(v) / n
    freq = np.fft.fftfreq(n, d=1.0 / F_SAMPLE)
    half = n // 2
    freq_h, mag_h = freq[:half], np.abs(spec[:half])
    peak_bin = int(np.argmax(mag_h))
    with open(path, "w") as fh:
        fh.write(f"# S4 RLC damped transient fixture\n")
        fh.write(f"# R={R:.0f} Ohm  L={L*1000:.0f} mH  C={C*1e6:.0f} uF\n")
        fh.write(f"# omega_0 = {OMEGA_0:.1f} rad/s  f_0 = {OMEGA_0/(2*np.pi):.2f} Hz\n")
        fh.write(f"# alpha   = {ALPHA:.1f} rad/s   tau = {TAU*1000:.1f} ms\n")
        fh.write(f"# omega_d = {OMEGA_D:.1f} rad/s  f_d = {F_D:.2f} Hz\n")
        fh.write(f"# {n} samples  fs = {F_SAMPLE:.0f} Hz  duration = {DURATION*1000:.0f} ms\n")
        fh.write("# Columns: time_s, voltage_V\n")
        fh.write("#\n")
        fh.write("# --- first 30 rows ---\n")
        fh.write(f"{'time_s':>12s}  {'voltage_V':>14s}\n")
        for i in range(30):
            fh.write(f"  {t[i]:10.6f}  {v[i]:14.8f}\n")
        fh.write(f"  ... ({n - 30} more rows)\n")
        fh.write("#\n")
        fh.write("# --- first 10 one-sided spectrum bins (by magnitude) ---\n")
        fh.write(f"{'freq_Hz':>10s}  {'|X|':>12s}  {'|X|/Xpk':>10s}\n")
        top10 = sorted(range(half), key=lambda k: mag_h[k], reverse=True)[:10]
        for k in sorted(top10):
            fh.write(f"  {freq_h[k]:8.2f}  {mag_h[k]:12.6f}  {mag_h[k]/mag_h[peak_bin]:10.6f}\n")
        fh.write(f"#\n")
        fh.write(f"# Peak: {freq_h[peak_bin]:.2f} Hz  (expected f_d = {F_D:.2f} Hz)\n")


def main() -> int:
    t, v = generate()
    csv_path  = DATA / "b1_s4_rlc.csv"
    head_path = DATA / "b1_s4_head.txt"
    write_csv(t, v, csv_path)
    write_head(t, v, head_path)

    n = len(t)
    spec = np.fft.fft(v) / n
    freq = np.fft.fftfreq(n, d=1.0 / F_SAMPLE)
    half = n // 2
    mag  = np.abs(spec[:half])
    peak = int(np.argmax(mag))

    print("=" * 60)
    print(" S4 RLC damped-transient fixture probe")
    print(f" R={R:.0f} Ohm  L={L*1000:.0f} mH  C={C*1e6:.0f} uF")
    print(f" omega_0 = {OMEGA_0:.1f} rad/s  f_0 = {OMEGA_0/(2*np.pi):.2f} Hz")
    print(f" alpha   = {ALPHA:.1f} rad/s   tau = {TAU*1000:.1f} ms")
    print(f" f_d     = {F_D:.2f} Hz   (damped resonance)")
    print(f" Samples: {n}  fs={F_SAMPLE:.0f} Hz  duration={DURATION*1000:.0f} ms")
    print("=" * 60)
    print(f"[wrote]  {csv_path.relative_to(HERE)}")
    print(f"[wrote]  {head_path.relative_to(HERE)}")
    print()
    print("--- spectrum summary ---")
    print(f"  bin width : {F_SAMPLE/n:.4f} Hz")
    print(f"  peak bin  : {peak}  ({freq[:half][peak]:.2f} Hz)  |X| = {mag[peak]:.6f}")
    print(f"  expected  : f_d = {F_D:.2f} Hz")
    print(f"  top 5 bins:")
    top = sorted(range(half), key=lambda k: mag[k], reverse=True)[:5]
    for k in sorted(top):
        print(f"    k={k:4d}  f={freq[:half][k]:7.2f} Hz  |X|={mag[k]:.6f}")
    print("=" * 60)
    print(" Probe complete. Paste this output back to chat.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
