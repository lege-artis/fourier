#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b2-audio/main.py - Shad-tier Band 2: audio sample (a chord)

Synthesises a triad (three sine waves summed) at standard concert pitches,
runs it through a DFT, and produces three plots:
  fig-b2-input.png      - time-domain waveform (amplitude vs seconds)
  fig-b2-spectrum.png   - frequency spectrum (linear scale)
  fig-b2-takeaway.png   - spectrum with three peaks labelled by note

The triad is a C-major chord at A440 tuning: C4 (261.63 Hz), E4 (329.63 Hz),
G4 (392.00 Hz). Sample rate 44.1 kHz (CD audio standard).

What this chapter adds over B1: multiple tones at once. The DFT decomposes
the chord into its constituents. Without windowing the spectrum shows
sharp peaks because each note is exactly N/(period * sample_rate)... but
real audio rarely lands on integer bins. The takeaway plot demonstrates
spectral leakage on a non-integer-frequency tone (the G4 at 392 Hz isn't
an exact integer fraction of the 44.1 kHz sample rate).

Usage:
    python main.py [--out-dir <dir>]
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib.pyplot as plt
import numpy as np


# Concert-pitch frequencies (Hz) at A4 = 440 Hz
NOTE_FREQ = {
    "C4": 261.63,
    "E4": 329.63,
    "G4": 392.00,
}


def synth_chord(
    sample_rate_hz: float = 44_100.0,
    duration_s: float = 0.5,
    amplitudes: dict | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (time_s, sample) for a synthesised C-major triad."""
    if amplitudes is None:
        amplitudes = {"C4": 0.4, "E4": 0.3, "G4": 0.3}
    n_samples = int(sample_rate_hz * duration_s)
    t = np.arange(n_samples) / sample_rate_hz
    samples = np.zeros(n_samples)
    for note, amp in amplitudes.items():
        f = NOTE_FREQ[note]
        samples += amp * np.sin(2 * np.pi * f * t)
    return t, samples


def compute_spectrum(
    samples: np.ndarray, sample_rate_hz: float, window: str = "rect"
) -> tuple[np.ndarray, np.ndarray]:
    """Return (freq_hz, magnitude) for the one-sided FFT.

    window: "rect" (no windowing) or "hann" (Hann window applied first).
    """
    n = samples.size
    if window == "hann":
        w = np.hanning(n)
        x = samples * w
        # Coherent gain compensation so the windowed peak matches amplitude
        gain = w.sum() / n
        spec = np.fft.fft(x) / (n * gain)
    else:
        spec = np.fft.fft(samples) / n
    freq = np.fft.fftfreq(n, d=1.0 / sample_rate_hz)
    half = n // 2
    return freq[:half], np.abs(spec[:half])


def plot_input(t: np.ndarray, samples: np.ndarray, out_path: pathlib.Path) -> None:
    # Plot only the first 20 ms - the whole 0.5 s would be unreadable
    end = int(0.02 * (t.size / t[-1]))
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(t[:end] * 1000.0, samples[:end], linewidth=0.7, color="#1f4e79")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    ax.set_title("B2 - C-major triad (first 20 ms of 500 ms recording)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_spectrum(freq: np.ndarray, mag: np.ndarray, out_path: pathlib.Path) -> None:
    # Zoom to 200-450 Hz where the chord lives
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(freq, mag, linewidth=1.0, color="#702020")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_title("B2 - DFT spectrum (rectangular window, zoom 200-450 Hz)")
    ax.set_xlim(200, 450)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_takeaway(
    freq: np.ndarray, mag_rect: np.ndarray, mag_hann: np.ndarray,
    out_path: pathlib.Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(freq, mag_rect, linewidth=1.0, color="#a02020", alpha=0.6,
            label="rectangular window (leakage)")
    ax.plot(freq, mag_hann, linewidth=1.0, color="#1f4e79",
            label="Hann window (cleaner peaks)")
    for note, f in NOTE_FREQ.items():
        ax.axvline(f, color="#444", linestyle=":", linewidth=0.7, alpha=0.6)
        ax.text(f, ax.get_ylim()[1] * 0.95, f" {note}\n {f:.1f} Hz",
                fontsize=9, va="top", ha="left")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_title("B2 takeaway - the three notes appear as three peaks; windowing affects sharpness")
    ax.set_xlim(200, 450)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
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

    sample_rate = 44_100.0
    t, samples = synth_chord(sample_rate_hz=sample_rate)
    freq, mag_rect = compute_spectrum(samples, sample_rate, window="rect")
    _, mag_hann = compute_spectrum(samples, sample_rate, window="hann")

    plot_input(t, samples, args.out_dir / "fig-b2-input.png")
    plot_spectrum(freq, mag_rect, args.out_dir / "fig-b2-spectrum.png")
    plot_takeaway(freq, mag_rect, mag_hann, args.out_dir / "fig-b2-takeaway.png")

    # Report bin locations
    print("B2 done. Expected peaks:")
    for note, f in NOTE_FREQ.items():
        bin_idx = int(round(f * samples.size / sample_rate))
        detected_hz = bin_idx * sample_rate / samples.size
        print(f"        {note}: {f:.2f} Hz  (nearest bin {bin_idx} = {detected_hz:.2f} Hz)")
    print(f"        PNGs in:  {args.out_dir}")
    return 0


# ---- Real-data extension (sketch) ------------------------------------------
# To repeat on a public-domain audio file:
#   1. Download a CC0/CC-BY .wav from Wikimedia Commons or Freesound.
#   2. Replace synth_chord() with:
#        from scipy.io import wavfile
#        sample_rate, samples = wavfile.read("clip.wav")
#        if samples.ndim > 1: samples = samples.mean(axis=1)  # mono
#        samples = samples.astype(float) / np.abs(samples).max()
#   3. The rest of the workflow is identical.

if __name__ == "__main__":
    raise SystemExit(main())
