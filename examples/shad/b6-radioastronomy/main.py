#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b6-radioastronomy/main.py  -  Shad-tier Band 6: Radio astronomy (PSR B1937+21)

A demonstration of integration time as the signal-processing resource.

  Stage 1 -- Synthesise a time series
    A periodic pulse train at f_spin = 641.9 Hz (PSR B1937+21's rotation
    frequency) is buried in Gaussian noise at a single-sample SNR of -20 dB.
    The signal is invisible by eye in any short segment of the raw data.

  Stage 2 -- Apply the DFT to the full 120-second time series
    np.fft.rfft on 491,520 samples reveals a sharp spike at 641.9 Hz
    and its 2nd and 3rd harmonics.  The noise floor drops as 1/sqrt(N);
    the signal concentrates into one bin per harmonic.

  Stage 3 -- Measure SNR vs integration time
    Run Stage 2 on sub-durations T = 1, 2, 4, ... 120 s and plot the
    measured SNR at f_spin.  The points follow the theoretical sqrt(T)
    growth law.

Physical source: PSR B1937+21 (Backer et al. 1982, Nature 300, 615).
Parameters from ATNF Pulsar Catalogue (Manchester et al. 2005,
  doi: 10.1086/428488), accessed 2026-05-25.

Reproducibility seed: 20260525  (figures are byte-reproducible on re-runs)

Output (relative to fourier/docs/shad/figures/):
  fig-b6-input.png      raw time series (noise-dominated) + phase-folded profile
  fig-b6-spectrum.png   FFT spectrum showing spike at f_spin and harmonics
  fig-b6-takeaway.png   annotated spectrum + SNR vs integration time
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ── Reproducibility ────────────────────────────────────────────────────────
RNG_SEED = 20260525

# ── PSR B1937+21 physical parameters (ATNF PSRCAT v2.5.1) ─────────────────
P_S       = 1.5578064688e-3   # spin period (s)
F_SPIN    = 1.0 / P_S         # spin frequency (Hz) = 641.928...
DM_PC_CM3 = 71.025            # dispersion measure (pc cm^-3)
DIST_KPC  = 3.6               # distance (kpc, NE2001 electron density model)

# ── Simulation parameters ──────────────────────────────────────────────────
FS              = 4096          # sample rate (Hz); Nyquist = 2048 Hz > 3*F_SPIN
T_OBS           = 120.0         # integration time (s)
PULSE_AMP       = 0.1           # pulse amplitude (noise units); single-sample power SNR = -20 dB
NOISE_SIGMA     = 1.0           # noise standard deviation
N_FOLD_BINS     = 64            # phase bins for folded profile figure

# Derived constants
SAMP_PER_PERIOD = FS / F_SPIN   # 6.381 samples per rotation period
N_SAMPLES       = int(T_OBS * FS)  # 491 520 samples


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════

def synthesise_time_series(rng: np.random.Generator) -> np.ndarray:
    """
    Build the full N_SAMPLES time series: periodic delta-pulse train + white noise.

    The pulsar emits one pulse per rotation period P_S.  Each pulse is modelled
    as a single-sample spike (the period is only ~6.38 samples at this sample
    rate, so a narrow Gaussian would be sub-sample; the spike is the limit).
    The spike amplitude PULSE_AMP = 0.1 gives a single-sample power SNR of
    (0.1/1.0)^2 = 0.01 = -20 dB.

    The pulse locations are determined by the fractional sample index of each
    rotation: pulse_n = round(k * SAMP_PER_PERIOD) for k = 0, 1, 2, ...
    This correctly handles the non-integer SAMP_PER_PERIOD = 6.381.
    """
    ts = rng.normal(0.0, NOISE_SIGMA, N_SAMPLES)

    # Vectorised pulse injection: place one spike per period
    k_max = int(N_SAMPLES / SAMP_PER_PERIOD) + 1
    pulse_indices = np.round(np.arange(k_max) * SAMP_PER_PERIOD).astype(int)
    pulse_indices = pulse_indices[pulse_indices < N_SAMPLES]
    ts[pulse_indices] += PULSE_AMP

    return ts


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def fold_profile(ts: np.ndarray, n_bins: int) -> np.ndarray:
    """
    Phase-fold ts into n_bins phase bins, averaging all contributing samples.

    Each sample at index n is assigned to bin floor((n / SAMP_PER_PERIOD % 1) * n_bins).
    The profile shows the mean signal as a function of rotational phase.
    """
    n = np.arange(len(ts))
    phase_frac = (n / SAMP_PER_PERIOD) % 1.0    # fractional phase [0, 1)
    bin_idx    = (phase_frac * n_bins).astype(int) % n_bins

    profile = np.zeros(n_bins)
    counts  = np.zeros(n_bins, dtype=int)
    np.add.at(profile, bin_idx, ts)
    np.add.at(counts,  bin_idx, 1)
    counts = np.maximum(counts, 1)
    return profile / counts


def snr_at_spin_frequency(ts: np.ndarray) -> float:
    """
    Return the amplitude SNR of the FFT spike at F_SPIN.

    Amplitude SNR = |X[k_spin]| / rms_noise_floor
    where k_spin is the bin nearest F_SPIN and rms_noise_floor is the
    median absolute magnitude across all bins (robust estimator).
    """
    n    = len(ts)
    spec = np.fft.rfft(ts)
    mag  = np.abs(spec) / n

    freq     = np.fft.rfftfreq(n, d=1.0 / FS)
    k_spin   = int(np.round(F_SPIN * (n / FS)))   # = round(F_SPIN * T)
    k_spin   = min(k_spin, len(mag) - 1)

    # Robust noise floor: median of bins away from the spin harmonics
    harmonic_mask = np.zeros(len(mag), dtype=bool)
    for h in range(1, 5):
        k_h = int(np.round(h * F_SPIN * (n / FS)))
        if k_h < len(mag):
            harmonic_mask[max(0, k_h - 3): k_h + 4] = True

    noise_floor = np.median(mag[~harmonic_mask])
    if noise_floor < 1e-30:
        return 0.0
    return mag[k_spin] / noise_floor


def snr_vs_time(ts: np.ndarray, t_values: np.ndarray) -> np.ndarray:
    """Compute amplitude SNR at F_SPIN for each integration length in t_values."""
    snrs = []
    for t in t_values:
        n = int(t * FS)
        snrs.append(snr_at_spin_frequency(ts[:n]))
    return np.array(snrs)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURES
# ═══════════════════════════════════════════════════════════════════════════

COLORS = {
    "noise":   "#6a7f9a",
    "signal":  "#c0392b",
    "theory":  "#1a5276",
    "measure": "#27ae60",
    "annot":   "#884400",
    "floor":   "#888888",
}


def fig_input(ts: np.ndarray, out: pathlib.Path) -> None:
    """
    Two-panel time-domain figure.

    Panel 1: First 100 ms of raw data (noise-dominated; pulses invisible).
    Panel 2: Phase-folded profile averaged over the full T_OBS seconds
             (pulse clearly visible after full coherent averaging).
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.5))
    fig.suptitle(
        f"B6 – PSR B1937+21: raw time series and phase-folded profile",
        fontsize=11,
    )

    # Panel 1: first 100 ms
    n_show    = int(0.1 * FS)   # 410 samples
    t_ms      = np.arange(n_show) / FS * 1e3

    ax1.plot(t_ms, ts[:n_show], lw=0.5, color=COLORS["noise"], alpha=0.85,
             label="dedispersed time series")

    # Mark pulse locations (barely visible ticks at the top)
    k_max   = int(n_show / SAMP_PER_PERIOD) + 1
    p_idx   = np.round(np.arange(k_max) * SAMP_PER_PERIOD).astype(int)
    p_idx   = p_idx[p_idx < n_show]
    p_t_ms  = p_idx / FS * 1e3
    ax1.vlines(p_t_ms, ymin=2.8, ymax=3.4, color=COLORS["signal"], lw=0.7,
               label=f"pulse epochs (P = {P_S*1e3:.4f} ms; {len(p_idx)} pulses shown)")

    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Amplitude (noise units)")
    ax1.set_title(
        f"Raw data, first 100 ms — single-sample SNR = {20*np.log10(PULSE_AMP/NOISE_SIGMA):.0f} dB"
        f"  [{len(p_idx)} pulse epochs; all invisible against noise]"
    )
    ax1.set_ylim(-3.8, 3.8)
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(alpha=0.25)

    # Panel 2: phase-folded profile over full T_OBS
    profile   = fold_profile(ts, N_FOLD_BINS)
    phase_deg = np.linspace(0, 360, N_FOLD_BINS, endpoint=False)

    ax2.plot(phase_deg, profile, lw=1.2, color=COLORS["signal"], label="folded profile")
    ax2.axhline(0, color="#aaaaaa", lw=0.6, linestyle="--")
    n_periods = int(T_OBS * F_SPIN)
    ax2.set_xlabel("Rotational phase (degrees)")
    ax2.set_ylabel("Mean amplitude (noise units)")
    ax2.set_title(
        f"Phase-folded profile: {n_periods:,} periods averaged over {T_OBS:.0f} s"
        f"  — pulse shape clearly visible after coherent integration"
    )
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_spectrum(ts: np.ndarray, out: pathlib.Path) -> None:
    """
    FFT magnitude spectrum of the full T_OBS time series.

    Shows the spike at F_SPIN and its 2nd and 3rd harmonics above the
    noise floor.  Y-axis: log-magnitude (dB).
    """
    n    = len(ts)
    spec = np.fft.rfft(ts)
    mag  = np.abs(spec) / n
    freq = np.fft.rfftfreq(n, d=1.0 / FS)

    mag_db = 20.0 * np.log10(mag + 1e-30)

    # Noise floor estimate (median, excluding harmonic regions)
    harmonic_mask = np.zeros(len(mag), dtype=bool)
    for h in range(1, 5):
        k_h = int(np.round(h * F_SPIN * T_OBS))
        if k_h < len(mag):
            harmonic_mask[max(0, k_h - 5): k_h + 6] = True
    noise_db = 20.0 * np.log10(np.median(mag[~harmonic_mask]) + 1e-30)

    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax.plot(freq, mag_db, lw=0.35, color=COLORS["noise"], alpha=0.7, rasterized=True)
    ax.axhline(noise_db, color=COLORS["floor"], lw=0.9, linestyle="--",
               label=f"noise floor ≈ {noise_db:.1f} dB")

    # Annotate harmonics
    harmonic_labels = [
        (1, "f_spin\n641.9 Hz"),
        (2, "2f_spin\n1283.8 Hz"),
        (3, "3f_spin\n1925.7 Hz"),
    ]
    for h, lbl in harmonic_labels:
        f_h  = h * F_SPIN
        k_h  = int(np.round(f_h * T_OBS))
        if k_h < len(mag):
            peak_db = mag_db[k_h]
            ax.annotate(
                lbl,
                xy=(freq[k_h], peak_db),
                xytext=(freq[k_h] + 30, peak_db - 5),
                fontsize=8, color=COLORS["annot"],
                arrowprops=dict(arrowstyle="->", color=COLORS["annot"], lw=0.8),
            )

    ax.set_xlim(0, 2050)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("FFT magnitude (dB, normalised)")
    ax.set_title(
        f"B6 – FFT of {T_OBS:.0f} s of PSR B1937+21 data"
        f"  (N = {n:,} samples, Δf = {1/T_OBS*1e3:.2f} mHz)"
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_takeaway(ts: np.ndarray, out: pathlib.Path) -> None:
    """
    Two-panel takeaway figure.

    Panel 1: Annotated FFT zoom around F_SPIN (shows noise floor, SNR, spike label).
    Panel 2: SNR vs integration time (measured simulation + theoretical sqrt(T) curve).
    """
    fig = plt.figure(figsize=(9, 6.5))
    gs  = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.45)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # ── Panel 1: zoomed spectrum ───────────────────────────────────────────
    n    = len(ts)
    spec = np.fft.rfft(ts)
    mag  = np.abs(spec) / n
    freq = np.fft.rfftfreq(n, d=1.0 / FS)
    mag_db = 20.0 * np.log10(mag + 1e-30)

    # Zoom to 580-720 Hz
    mask  = (freq >= 580) & (freq <= 720)
    f_z   = freq[mask]
    m_z   = mag_db[mask]

    ax1.plot(f_z, m_z, lw=0.5, color=COLORS["noise"], alpha=0.85, rasterized=True)

    harmonic_mask = np.zeros(len(mag), dtype=bool)
    for h in range(1, 5):
        k_h = int(np.round(h * F_SPIN * T_OBS))
        if k_h < len(mag):
            harmonic_mask[max(0, k_h - 5): k_h + 6] = True
    noise_db = 20.0 * np.log10(np.median(mag[~harmonic_mask]) + 1e-30)

    ax1.axhline(noise_db, color=COLORS["floor"], lw=0.9, linestyle="--",
                label=f"noise floor ({noise_db:.1f} dB)")

    k_spin   = int(np.round(F_SPIN * T_OBS))
    peak_db  = mag_db[k_spin]
    snr_db   = peak_db - noise_db

    ax1.annotate(
        f"f_spin = {F_SPIN:.1f} Hz\npeak SNR = {snr_db:.1f} dB",
        xy=(freq[k_spin], peak_db),
        xytext=(F_SPIN + 15, peak_db - 4),
        fontsize=9, color=COLORS["annot"],
        arrowprops=dict(arrowstyle="->", color=COLORS["annot"], lw=0.9),
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                  edgecolor=COLORS["annot"], alpha=0.85),
    )

    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("FFT magnitude (dB)")
    ax1.set_title(
        f"B6 takeaway (panel 1) – Zoomed FFT around f_spin after {T_OBS:.0f} s integration"
    )
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.25)

    # ── Panel 2: SNR vs integration time ──────────────────────────────────
    t_vals = np.array([1, 2, 4, 8, 16, 32, 64, 120], dtype=float)
    snr_meas = snr_vs_time(ts, t_vals)
    snr_meas_db = 20.0 * np.log10(snr_meas + 1e-12)

    # Theoretical sqrt(T) curve calibrated to the T_OBS measured point
    snr_theory_db = snr_meas_db[-1] + 10.0 * np.log10(t_vals / T_OBS)

    ax2.plot(t_vals, snr_theory_db, lw=1.6, color=COLORS["theory"],
             label=r"theoretical $\sqrt{T}$ law")
    ax2.plot(t_vals, snr_meas_db, "o", ms=6, color=COLORS["measure"],
             label="measured FFT peak SNR")
    ax2.axhline(0, color="#aaaaaa", lw=0.8, linestyle=":", label="SNR = 0 dB (detection threshold)")

    ax2.set_xscale("log")
    ax2.set_xlabel("Integration time T (s)")
    ax2.set_ylabel("SNR at f_spin (dB)")
    ax2.set_title(
        r"B6 takeaway (panel 2) – SNR $\propto \sqrt{T}$: integration time buys dynamic range"
    )
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.25, which="both")
    ax2.set_xticks(t_vals)
    ax2.set_xticklabels([f"{int(t)} s" for t in t_vals], fontsize=8)

    fig.savefig(out, dpi=110)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main() -> int:
    here        = pathlib.Path(__file__).resolve().parent
    default_out = here.parent.parent.parent / "docs" / "shad" / "figures"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=pathlib.Path, default=default_out)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(RNG_SEED)

    print(f"PSR B1937+21 simulation parameters:")
    print(f"  Spin period P          = {P_S*1e3:.7f} ms")
    print(f"  Spin frequency f_spin  = {F_SPIN:.4f} Hz")
    print(f"  Sample rate FS         = {FS} Hz  (Nyquist = {FS//2} Hz; 3 harmonics fit)")
    print(f"  Samples per period     = {SAMP_PER_PERIOD:.3f}")
    print(f"  Integration time T_OBS = {T_OBS:.0f} s")
    print(f"  Total samples N        = {N_SAMPLES:,}")
    print(f"  Pulses in T_OBS        = {int(T_OBS * F_SPIN):,}")
    print(f"  Single-sample SNR      = {20*np.log10(PULSE_AMP/NOISE_SIGMA):.1f} dB")
    print()

    print("Synthesising time series…")
    ts = synthesise_time_series(rng)

    # Report SNR at the spin frequency for the full integration
    snr_full = snr_at_spin_frequency(ts)
    print(f"Full {T_OBS:.0f} s FFT peak SNR at f_spin = {F_SPIN:.1f} Hz:  "
          f"{20*np.log10(snr_full):.1f} dB")

    # Theoretical amplitude SNR for comparison
    # SNR_amp = PULSE_AMP * sqrt(N_SAMPLES) / (SAMP_PER_PERIOD * NOISE_SIGMA)
    snr_theory = PULSE_AMP * np.sqrt(N_SAMPLES) / (SAMP_PER_PERIOD * NOISE_SIGMA)
    print(f"Theoretical amplitude SNR (sqrt(N) formula): {20*np.log10(snr_theory):.1f} dB")
    print()

    print("SNR vs integration time:")
    t_vals = np.array([1, 4, 16, 64, 120], dtype=float)
    for t in t_vals:
        n = int(t * FS)
        snr = snr_at_spin_frequency(ts[:n])
        snr_th = PULSE_AMP * np.sqrt(n) / (SAMP_PER_PERIOD * NOISE_SIGMA)
        print(f"  T = {t:5.0f} s  N = {n:7,}  "
              f"SNR_meas = {20*np.log10(snr):.1f} dB  "
              f"SNR_theory = {20*np.log10(snr_th):.1f} dB")
    print()

    print("Rendering figures…")
    fig_input(ts, args.out_dir / "fig-b6-input.png")
    print(f"  fig-b6-input.png saved.")

    fig_spectrum(ts, args.out_dir / "fig-b6-spectrum.png")
    print(f"  fig-b6-spectrum.png saved.")

    fig_takeaway(ts, args.out_dir / "fig-b6-takeaway.png")
    print(f"  fig-b6-takeaway.png saved.")

    print(f"\nAll figures saved to: {args.out_dir}")
    return 0


# ── Real-data extension notes ──────────────────────────────────────────────
# The NANOGrav 15-year data set is publicly available at:
#   https://zenodo.org/records/8433091
#   G. Agazie et al. (NANOGrav), ApJS 265, 49 (2023), doi: 10.3847/1538-4365/acdc91
# Format: ASCII .tim (pulse arrival times) and .par (timing model) files,
#   compatible with TEMPO2 / PINT (pip install pint-pulsar enterprise).
# The FFT of timing residuals (observed TOAs minus best-fit model) reveals
#   orbital periods in binary systems: PSR B1855+09 (P_orb = 12.33 days),
#   PSR J1713+0747 (P_orb = 67.8 days) both show clear spectral features.
# The ATNF Pulsar Catalogue (PSRCAT) is available at:
#   https://www.atnf.csiro.au/research/pulsar/psrcat/
#   R. N. Manchester et al., AJ 129, 1993 (2005), doi: 10.1086/428488

if __name__ == "__main__":
    raise SystemExit(main())
