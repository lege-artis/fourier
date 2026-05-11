#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b3-vibration/main.py - Shad-tier Band 3: vibration / accelerometer

Synthesises an industrial vibration signal that mimics what an
accelerometer mounted on a rotating-machinery bearing would record:
  - 1x rotation frequency (the shaft) at 30 Hz
  - 2x harmonic (mass imbalance) at 60 Hz, smaller
  - 3x harmonic (alignment) at 90 Hz, smaller still
  - A bearing-fault signature around 142 Hz (typical ball-pass frequency
    on an outer race for a 30 Hz shaft and a 9.4 BPFO ratio)
  - Broadband white noise floor

Sample rate 5 kHz (typical for vibration monitoring; bearings rarely have
content above 2 kHz). Duration 2 s.

This chapter adds: HARMONICS. Real machines don't produce pure tones; they
produce a fundamental plus integer multiples (harmonics) plus fault-specific
non-harmonic signatures. The trained eye reads vibration spectra like a
doctor reads an ECG.

Output:
  fig-b3-input.png      - time-domain trace
  fig-b3-spectrum.png   - frequency spectrum (linear) up to 500 Hz
  fig-b3-takeaway.png   - annotated spectrum with shaft harmonics + bearing
                          fault peak labelled
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib.pyplot as plt
import numpy as np


SHAFT_HZ = 30.0      # 1800 RPM rotational speed
BPFO_HZ = 142.4      # ball-pass frequency, outer race - bearing fault
HARMONICS = {
    "1x (shaft)":    (SHAFT_HZ,     1.00),
    "2x (imbalance)":(2 * SHAFT_HZ, 0.40),
    "3x (alignment)":(3 * SHAFT_HZ, 0.25),
    "BPFO (fault)":  (BPFO_HZ,      0.30),
}


def synth_vibration(
    sample_rate_hz: float = 5_000.0,
    duration_s: float = 2.0,
    noise_amp: float = 0.05,
    rng_seed: int = 17,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (time_s, accel_g) for a synthesised vibration trace."""
    rng = np.random.default_rng(rng_seed)
    n_samples = int(sample_rate_hz * duration_s)
    t = np.arange(n_samples) / sample_rate_hz
    accel = np.zeros(n_samples)
    for f, amp in HARMONICS.values():
        accel += amp * np.sin(2 * np.pi * f * t)
    accel += rng.normal(0.0, noise_amp, size=n_samples)
    return t, accel


def compute_spectrum(
    samples: np.ndarray, sample_rate_hz: float
) -> tuple[np.ndarray, np.ndarray]:
    n = samples.size
    # Hann window for cleaner peaks on real-style data
    w = np.hanning(n)
    gain = w.sum() / n
    spec = np.fft.fft(samples * w) / (n * gain)
    freq = np.fft.fftfreq(n, d=1.0 / sample_rate_hz)
    half = n // 2
    return freq[:half], np.abs(spec[:half])


def plot_input(t: np.ndarray, accel: np.ndarray, out_path: pathlib.Path) -> None:
    end = int(0.2 * t.size / t[-1])  # first 200 ms
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(t[:end] * 1000.0, accel[:end], linewidth=0.7, color="#1f4e79")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Acceleration (g)")
    ax.set_title("B3 - synthesised bearing vibration (first 200 ms of 2 s)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_spectrum(freq: np.ndarray, mag: np.ndarray, out_path: pathlib.Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(freq, mag, linewidth=0.9, color="#702020")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (g)")
    ax.set_title("B3 - DFT spectrum, Hann-windowed (zoom 0-300 Hz)")
    ax.set_xlim(0, 300)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_takeaway(freq: np.ndarray, mag: np.ndarray, out_path: pathlib.Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(freq, mag, linewidth=0.9, color="#1f4e79")
    # Annotate each known feature
    colour = {"1x (shaft)": "#208020", "2x (imbalance)": "#806020",
              "3x (alignment)": "#a06020", "BPFO (fault)": "#a02020"}
    for label, (f, _) in HARMONICS.items():
        c = colour[label]
        ax.axvline(f, color=c, linestyle="--", linewidth=0.8, alpha=0.7)
        # Find local peak near f for the annotation point
        bin_idx = int(round(f * (freq.size * 2) / (freq[-1] * 2)))
        bin_idx = min(bin_idx, mag.size - 1)
        y = float(mag[bin_idx])
        ax.annotate(label, xy=(f, y), xytext=(f + 5, y * 1.05),
                    fontsize=8.5, color=c,
                    arrowprops=dict(arrowstyle="->", color=c, linewidth=0.7))
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (g)")
    ax.set_title("B3 takeaway - shaft harmonics + bearing-fault signature stand out clearly")
    ax.set_xlim(0, 300)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    default_out = here.parent.parent.parent / "docs" / "shad" / "figures"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=pathlib.Path, default=default_out)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    sample_rate = 5_000.0
    t, accel = synth_vibration(sample_rate_hz=sample_rate)
    freq, mag = compute_spectrum(accel, sample_rate)

    plot_input(t, accel, args.out_dir / "fig-b3-input.png")
    plot_spectrum(freq, mag, args.out_dir / "fig-b3-spectrum.png")
    plot_takeaway(freq, mag, args.out_dir / "fig-b3-takeaway.png")

    print("B3 done. Expected features:")
    for label, (f, _) in HARMONICS.items():
        print(f"        {label}: {f:.1f} Hz")
    print(f"        PNGs in:  {args.out_dir}")
    return 0


# ---- Real-data extension (sketch) ------------------------------------------
# NASA Bearing Dataset (CC-BY) is the canonical real-data source. Download
# from https://www.kaggle.com/datasets/vinayak123tyagi/bearing-dataset or
# the NASA prognostics-data repository, then:
#   data = np.loadtxt("bearing_run.csv")  # one column, samples
#   sample_rate = 20_000.0  # NASA Bearing Dataset standard
# The workflow above runs unchanged on real bearing data.

if __name__ == "__main__":
    raise SystemExit(main())
