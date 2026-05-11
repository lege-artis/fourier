#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b1-scope/main.py - Shad-tier Band 1: oscilloscope trace

Synthesises a scope trace (the kind of CSV you'd get out of any benchtop
oscilloscope), runs it through a DFT, and produces three plots:
  fig-b1-input.png     - time-domain trace (volts vs seconds)
  fig-b1-spectrum.png  - frequency spectrum (magnitude vs Hz)
  fig-b1-takeaway.png  - annotated spectrum with peak labelled

The trace is synthesised so the script runs anywhere without internet.
A real-data path (fetch a public scope capture) is sketched at the bottom
of the script for readers who want to repeat on actual hardware data.

Usage:
    python main.py [--out-dir <dir>]
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib.pyplot as plt
import numpy as np


def synth_scope_trace(
    sample_rate_hz: float = 10_000.0,
    duration_s: float = 0.05,
    signal_hz: float = 240.0,
    signal_amp_v: float = 1.0,
    noise_amp_v: float = 0.10,
    rng_seed: int = 42,
):
    """Return (time_s, voltage_v) for a synthesised scope trace.

    Default: 240 Hz sine wave at 1 V amplitude, sampled at 10 kHz for 50 ms,
    with 10% white-noise floor. The 240 Hz choice lands exactly on bin 12
    (N=500, bin-width 20 Hz) so B1 demonstrates the clean case before B2
    introduces spectral leakage on non-integer-bin frequencies.
    """
    rng = np.random.default_rng(rng_seed)
    n_samples = int(sample_rate_hz * duration_s)
    t = np.arange(n_samples) / sample_rate_hz
    signal = signal_amp_v * np.sin(2 * np.pi * signal_hz * t)
    noise = rng.normal(0.0, noise_amp_v, size=n_samples)
    return t, signal + noise


def compute_spectrum(samples, sample_rate_hz):
    """Return (freq_hz, magnitude) for the one-sided FFT of samples."""
    n = samples.size
    spec = np.fft.fft(samples) / n
    freq = np.fft.fftfreq(n, d=1.0 / sample_rate_hz)
    half = n // 2
    return freq[:half], np.abs(spec[:half])


def plot_input(t, v, out_path):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(t * 1000.0, v, linewidth=0.9, color="#1f4e79")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("B1 - synthesised oscilloscope trace (10 kHz sample rate)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_spectrum(freq, mag, out_path):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(freq, mag, linewidth=1.0, color="#702020")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude |X[k]| / N (V)")
    ax.set_title("B1 - DFT spectrum (one-sided, normalised)")
    ax.set_xlim(0, freq[-1])
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_takeaway(freq, mag, out_path):
    peak_idx = int(np.argmax(mag))
    peak_hz = float(freq[peak_idx])
    peak_v = float(mag[peak_idx])

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(freq, mag, linewidth=1.0, color="#1f4e79")
    ax.axvline(peak_hz, color="#a02020", linestyle="--", linewidth=0.9, alpha=0.8)
    ax.annotate(
        f"peak @ {peak_hz:.1f} Hz\nmagnitude {peak_v:.3f} V",
        xy=(peak_hz, peak_v),
        xytext=(peak_hz + 300, peak_v * 0.7),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="#a02020", linewidth=0.8),
    )
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude |X[k]| / N (V)")
    ax.set_title("B1 takeaway - the 240 Hz tone shows up as the obvious peak")
    ax.set_xlim(0, freq[-1])
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def main():
    here = pathlib.Path(__file__).resolve().parent
    default_out = here.parent.parent.parent / "docs" / "shad" / "figures"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=pathlib.Path, default=default_out)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    sample_rate = 10_000.0
    t, v = synth_scope_trace(sample_rate_hz=sample_rate)
    freq, mag = compute_spectrum(v, sample_rate)

    plot_input(t, v, args.out_dir / "fig-b1-input.png")
    plot_spectrum(freq, mag, args.out_dir / "fig-b1-spectrum.png")
    plot_takeaway(freq, mag, args.out_dir / "fig-b1-takeaway.png")

    peak_idx = int(np.argmax(mag))
    print(f"B1 done. Peak detected at {freq[peak_idx]:.2f} Hz")
    print(f"        Expected: 240.00 Hz (synthesised input)")
    print(f"        PNGs in:  {args.out_dir}")
    return 0


# ---- Real-data extension (sketch; not run by default) ----------------------
# To repeat this on a public scope capture instead of synthesised data:
#   1. Download a CC-licensed scope trace (CSV: time_s, voltage_v).
#   2. Replace synth_scope_trace() with:
#        data = np.loadtxt("trace.csv", delimiter=",", skiprows=1)
#        t = data[:, 0]; v = data[:, 1]
#        sample_rate = 1.0 / (t[1] - t[0])
#   3. Pass the arrays to compute_spectrum() and the plot_* helpers.

if __name__ == "__main__":
    raise SystemExit(main())
