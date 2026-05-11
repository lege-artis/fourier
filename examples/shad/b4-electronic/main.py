#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b4-electronic/main.py - Shad-tier Band 4: electronic systems

Demonstrates three ways Fourier analysis describes active circuits:

  1. AC mains harmonics -- what does "50 Hz mains" actually look like
     in the spectrum?  Synthesises a realistic mains waveform distorted
     by non-linear loads (rectifiers, dimmers, switching power supplies).
     Shows Total Harmonic Distortion (THD) as a single number.

  2. Active filter -- a 2nd-order Sallen-Key low-pass filter (fc=300 Hz,
     Q=0.707 Butterworth) applied in the frequency domain.  Plots the
     spectrum before and after to show that filtering IS multiplication in
     the frequency domain.

  3. Heterodyne mixer -- multiplying an RF carrier (1000 Hz) by a local
     oscillator (900 Hz) in the time domain produces sum (1900 Hz) and
     difference (100 Hz) frequency components in the spectrum.  This is
     the exact principle used in every superheterodyne radio since 1918.

Sample rate 10 kHz, duration 0.5 s (N=5000, frequency resolution 2 Hz).
RNG seed 20260511 -- figures are byte-reproducible on re-runs.

Output (relative to fourier/docs/shad/figures/):
  fig-b4-input.png       time-domain mains waveform (first 60 ms)
  fig-b4-spectrum.png    mains spectrum, filter before+after, mixer output
  fig-b4-takeaway.png    same three panels with engineering annotations
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ---- Global parameters -------------------------------------------------------

FS = 10_000.0       # sample rate (Hz)
DURATION = 0.5      # record length (s)
N = int(FS * DURATION)  # 5000 samples; freq resolution = 2 Hz

MAINS_F0 = 50.0     # fundamental (European mains)
# Amplitudes for odd harmonics: fund 100%, 3rd 4%, 5th 2.5%, 7th 1.5%, 9th 0.8%
# THD = sqrt(0.04^2 + 0.025^2 + 0.015^2 + 0.008^2) / 1.0 = approx 5.0%
MAINS_HARMONICS = {
    "1st (fund)": (MAINS_F0,        1.000),
    "3rd":        (3 * MAINS_F0,    0.040),
    "5th":        (5 * MAINS_F0,    0.025),
    "7th":        (7 * MAINS_F0,    0.015),
    "9th":        (9 * MAINS_F0,    0.008),
}

FILTER_FC = 300.0   # low-pass cutoff (Hz)
FILTER_Q  = 0.7071  # Butterworth (maximally flat)

RF_HZ  = 1_000.0   # RF carrier frequency
LO_HZ  =   900.0   # local oscillator frequency
# Product: IF_DIFF = RF - LO = 100 Hz;  IF_SUM = RF + LO = 1900 Hz

# ---- Synthesis helpers -------------------------------------------------------

def make_time() -> np.ndarray:
    return np.arange(N) / FS


def synth_mains(t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    sig = np.zeros_like(t)
    for _label, (f, amp) in MAINS_HARMONICS.items():
        sig += amp * np.sin(2.0 * np.pi * f * t)
    # Tiny noise floor (0.5%) to make the spectrum look realistic
    sig += rng.normal(0.0, 0.005, size=t.size)
    return sig


def synth_filter_input(t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Broadband test signal: two in-band tones + two out-of-band tones + noise."""
    sig  = 0.8 * np.sin(2.0 * np.pi *   80.0 * t)   # in-band
    sig += 0.6 * np.sin(2.0 * np.pi *  200.0 * t)   # in-band
    sig += 0.5 * np.sin(2.0 * np.pi *  600.0 * t)   # above cutoff
    sig += 0.4 * np.sin(2.0 * np.pi * 1_200.0 * t)  # well above cutoff
    sig += rng.normal(0.0, 0.04, size=t.size)
    return sig


def apply_sk_lowpass(sig: np.ndarray, fc: float, q: float) -> np.ndarray:
    """Apply 2nd-order Sallen-Key low-pass in the frequency domain.

    Transfer function (Eq. SK-LP):
        H(f) = 1 / (1 + j*(f/fc)/Q - (f/fc)^2)

    Ref: Sedra & Smith, Microelectronic Circuits, ch. 12 (active filter synthesis).
    """
    freq_bins = np.fft.fftfreq(sig.size, d=1.0 / FS)
    ratio = freq_bins / fc
    # Complex denominator; avoid DC division warning by using complex ratio
    H = 1.0 / (1.0 + 1j * ratio / q - ratio ** 2)
    spec_in  = np.fft.fft(sig)
    spec_out = spec_in * H
    return np.real(np.fft.ifft(spec_out))


def synth_mixer(t: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (rf, lo, product) time-domain signals."""
    rf  = np.sin(2.0 * np.pi * RF_HZ * t)
    lo  = np.sin(2.0 * np.pi * LO_HZ * t)
    mix = rf * lo    # product in time = convolution in freq
    return rf, lo, mix


# ---- Spectrum helpers --------------------------------------------------------

def spectrum(sig: np.ndarray, window: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """One-sided magnitude spectrum.  Returns (freq_hz, magnitude)."""
    s = sig.copy()
    if window:
        w = np.hanning(s.size)
        gain = w.sum() / s.size
        s *= w
        s /= gain
    spec = np.fft.fft(s) / s.size
    freq = np.fft.fftfreq(s.size, d=1.0 / FS)
    half = s.size // 2
    return freq[:half], np.abs(spec[:half]) * 2.0   # one-sided * 2 for energy


def thd(harmonics: dict) -> float:
    """Total Harmonic Distortion from the HARMONICS table (fundamental = index 0)."""
    amps = list(h[1] for h in harmonics.values())
    fund = amps[0]
    return float(np.sqrt(sum(a ** 2 for a in amps[1:])) / fund)


# ---- Figures -----------------------------------------------------------------

COLORS = {
    "mains_line": "#1f4e79",
    "harmonics":  ["#228822", "#c07000", "#c05000", "#b02020", "#800080"],
    "before":     "#1f4e79",
    "after":      "#b04040",
    "cutoff":     "#404040",
    "rf":         "#1f4e79",
    "lo":         "#228822",
    "if_diff":    "#b02020",
    "if_sum":     "#c07000",
}


def fig_input(t: np.ndarray, mains: np.ndarray, out: pathlib.Path) -> None:
    """Time-domain snapshot of the mains waveform (first 60 ms)."""
    end = int(0.060 * FS)   # 60 ms = 3 full cycles of 50 Hz
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(t[:end] * 1000.0, mains[:end], linewidth=0.9,
            color=COLORS["mains_line"])
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude (normalised)")
    ax.set_title("B4 - synthesised 50 Hz mains waveform (first 60 ms; 3 cycles)")
    ax.axhline(0, color="#aaa", linewidth=0.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_spectrum(
    freq_m: np.ndarray, mag_m: np.ndarray,
    freq_fb: np.ndarray, mag_fb: np.ndarray,
    freq_fa: np.ndarray, mag_fa: np.ndarray,
    freq_mx: np.ndarray, mag_mx: np.ndarray,
    out: pathlib.Path,
) -> None:
    """Three-panel bare spectrum figure (no annotations)."""
    fig = plt.figure(figsize=(10, 8))
    gs  = gridspec.GridSpec(3, 1, hspace=0.55)

    # Panel 1: mains harmonics
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(freq_m, mag_m, linewidth=0.9, color=COLORS["mains_line"])
    ax1.set_xlim(0, 600)
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("Magnitude")
    ax1.set_title("1. AC mains spectrum (0-600 Hz)")
    ax1.grid(alpha=0.3)

    # Panel 2: low-pass filter before / after
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(freq_fb, mag_fb, linewidth=0.9, color=COLORS["before"],
             label="before filter", alpha=0.8)
    ax2.plot(freq_fa, mag_fa, linewidth=1.1, color=COLORS["after"],
             label="after filter", alpha=0.9)
    ax2.set_xlim(0, 1_800)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Magnitude")
    ax2.set_title("2. Sallen-Key LP filter (fc = 300 Hz)")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    # Panel 3: mixer output
    ax3 = fig.add_subplot(gs[2])
    ax3.plot(freq_mx, mag_mx, linewidth=0.9, color=COLORS["mains_line"])
    ax3.set_xlim(0, 2_200)
    ax3.set_xlabel("Frequency (Hz)")
    ax3.set_ylabel("Magnitude")
    ax3.set_title("3. Heterodyne mixer output (RF x LO)")
    ax3.grid(alpha=0.3)

    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_takeaway(
    freq_m: np.ndarray, mag_m: np.ndarray,
    freq_fb: np.ndarray, mag_fb: np.ndarray,
    freq_fa: np.ndarray, mag_fa: np.ndarray,
    freq_mx: np.ndarray, mag_mx: np.ndarray,
    out: pathlib.Path,
) -> None:
    """Three-panel annotated takeaway figure."""
    fig = plt.figure(figsize=(10, 9))
    gs  = gridspec.GridSpec(3, 1, hspace=0.65)

    # ---------- Panel 1: mains harmonics (annotated) ----------
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(freq_m, mag_m, linewidth=0.9, color=COLORS["mains_line"])
    ax1.set_xlim(0, 600)

    for i, (label, (f, _)) in enumerate(MAINS_HARMONICS.items()):
        c = COLORS["harmonics"][i]
        ax1.axvline(f, color=c, linestyle="--", linewidth=0.8, alpha=0.7)
        # Amplitude from table (spectrum shows peak; for annotation use table value)
        idx = int(round(f / FS * N))
        idx = min(idx, mag_m.size - 1)
        y   = float(mag_m[idx])
        offset_x = 8 if i % 2 == 0 else -70
        ax1.annotate(label, xy=(f, y), xytext=(f + offset_x, y + 0.04),
                     fontsize=8, color=c,
                     arrowprops=dict(arrowstyle="->", color=c, linewidth=0.6))

    thd_pct = thd(MAINS_HARMONICS) * 100.0
    ax1.text(0.97, 0.92, f"THD = {thd_pct:.1f}%", transform=ax1.transAxes,
             ha="right", va="top", fontsize=9, color="#500000",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff0f0", alpha=0.8))
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("Magnitude")
    ax1.set_title("1. AC mains: fundamental + odd harmonics from non-linear loads")
    ax1.grid(alpha=0.3)

    # ---------- Panel 2: filter before/after (annotated) ----------
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(freq_fb, mag_fb, linewidth=0.9, color=COLORS["before"],
             label="input (broadband)", alpha=0.7)
    ax2.plot(freq_fa, mag_fa, linewidth=1.1, color=COLORS["after"],
             label="filtered output", alpha=0.9)
    ax2.axvline(FILTER_FC, color=COLORS["cutoff"], linestyle=":", linewidth=1.2)
    ax2.text(FILTER_FC + 15, ax2.get_ylim()[1] * 0.5 if ax2.get_ylim()[1] > 0 else 0.4,
             f"fc = {FILTER_FC:.0f} Hz\n-40 dB/decade", fontsize=8,
             color=COLORS["cutoff"])
    # Arrow pointing to -40 dB/decade rolloff region
    ax2.annotate("content above fc\nattenuated here", xy=(800, 0.05),
                 xytext=(1100, 0.28), fontsize=8, color=COLORS["after"],
                 arrowprops=dict(arrowstyle="->", color=COLORS["after"], linewidth=0.7))
    ax2.set_xlim(0, 1_800)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Magnitude")
    ax2.set_title("2. Filter = multiplier in frequency domain: content above fc shrinks")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    # ---------- Panel 3: mixer output (annotated) ----------
    ax3 = fig.add_subplot(gs[2])
    ax3.plot(freq_mx, mag_mx, linewidth=0.9, color=COLORS["mains_line"])
    ax3.set_xlim(0, 2_200)

    # Mark RF, LO, IF-diff, IF-sum
    annotations = [
        (LO_HZ,                   "LO\n900 Hz",   COLORS["lo"],      +70),
        (RF_HZ,                   "RF\n1000 Hz",  COLORS["rf"],      +70),
        (RF_HZ - LO_HZ,           "IF-\n100 Hz",  COLORS["if_diff"], +30),
        (RF_HZ + LO_HZ,           "IF+\n1900 Hz", COLORS["if_sum"],  -100),
    ]
    for f, lbl, c, dx in annotations:
        ax3.axvline(f, color=c, linestyle="--", linewidth=0.9, alpha=0.7)
        idx = int(round(f / FS * N))
        idx = min(idx, mag_mx.size - 1)
        y   = float(mag_mx[idx])
        ax3.annotate(lbl, xy=(f, y), xytext=(f + dx, y + 0.03),
                     fontsize=8, color=c,
                     arrowprops=dict(arrowstyle="->", color=c, linewidth=0.7))
    ax3.text(0.5, 0.88,
             r"$f_{RF} \times f_{LO}\ \rightarrow\ (f_{RF}-f_{LO})\ +\ (f_{RF}+f_{LO})$",
             transform=ax3.transAxes, ha="center", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f4ff", alpha=0.8))
    ax3.set_xlabel("Frequency (Hz)")
    ax3.set_ylabel("Magnitude")
    ax3.set_title("3. Heterodyne: multiply RF x LO in time = spectrum shift in frequency")
    ax3.grid(alpha=0.3)

    fig.savefig(out, dpi=110)
    plt.close(fig)


# ---- Main --------------------------------------------------------------------

def main() -> int:
    here        = pathlib.Path(__file__).resolve().parent
    default_out = here.parent.parent.parent / "docs" / "shad" / "figures"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=pathlib.Path, default=default_out)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(20260511)
    t   = make_time()

    # -- Sub-topic 1: mains -----------------------------------------------------
    mains = synth_mains(t, rng)
    freq_m, mag_m = spectrum(mains, window=False)   # pure tones: no window needed

    # -- Sub-topic 2: active filter ---------------------------------------------
    filt_in  = synth_filter_input(t, rng)
    filt_out = apply_sk_lowpass(filt_in, fc=FILTER_FC, q=FILTER_Q)
    freq_fb, mag_fb = spectrum(filt_in,  window=True)
    freq_fa, mag_fa = spectrum(filt_out, window=True)

    # -- Sub-topic 3: heterodyne mixer ------------------------------------------
    _, _, mix = synth_mixer(t)
    freq_mx, mag_mx = spectrum(mix, window=False)

    # -- Render figures ---------------------------------------------------------
    fig_input(t, mains, args.out_dir / "fig-b4-input.png")
    fig_spectrum(freq_m, mag_m,
                 freq_fb, mag_fb, freq_fa, mag_fa,
                 freq_mx, mag_mx,
                 args.out_dir / "fig-b4-spectrum.png")
    fig_takeaway(freq_m, mag_m,
                 freq_fb, mag_fb, freq_fa, mag_fa,
                 freq_mx, mag_mx,
                 args.out_dir / "fig-b4-takeaway.png")

    print("B4 done.")
    print(f"  AC mains THD : {thd(MAINS_HARMONICS)*100:.1f}%")
    print(f"  Mixer IF-     : {RF_HZ - LO_HZ:.0f} Hz  (RF - LO)")
    print(f"  Mixer IF+     : {RF_HZ + LO_HZ:.0f} Hz  (RF + LO)")
    print(f"  Figures in    : {args.out_dir}")
    return 0


# ---- Real-data extension notes -----------------------------------------------
# AC mains: OPSD (Open Power System Data) publishes 50-Hz grid time-series.
# https://data.open-power-system-data.org/ (CC-BY-4.0)
# Load a 1-second window from any 50 Hz grid recording and run
# spectrum(data, window=False) -- the workflow above is identical.
#
# RF captures: rtl-sdr.com publishes sample IQ captures (public domain).
# Decode with scipy.io.wavfile and feed the real part to synth_mixer().
# The IF arithmetic is unchanged.

if __name__ == "__main__":
    raise SystemExit(main())
