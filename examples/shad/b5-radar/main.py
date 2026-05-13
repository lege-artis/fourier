#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b5-radar/main.py  -  Shad-tier Band 5: Radar (NEXRAD-style)

Three progressive stages of the same Fourier machinery:

  Stage 1 – Single chirp pulse + matched-filter pulse compression
    A linear-FM (chirp) pulse is transmitted.  The received echo is
    delayed (target range) and buried in noise (SNR ~ 0 dB raw).
    Cross-correlating the echo with the known transmit waveform in the
    frequency domain (matched filter) compresses the pulse energy into
    a sharp range peak, lifting SNR by the time-bandwidth product.

  Stage 2 – Pulse train + Doppler DFT
    64 pulses are transmitted at PRF = 1000 Hz.  A moving target
    imprints a phase shift between successive echoes proportional to
    its radial velocity (Doppler shift: df = 2*v_r*f_c/c).
    A DFT across the pulse-train direction converts phase history
    into velocity.

  Stage 3 – 2-D range-Doppler map (NEXRAD-style volume scan)
    Stack all 64 compressed range profiles into a matrix:
      rows  = range bins (fast-time, within a pulse)
      cols  = pulse index (slow-time, across the CPI)
    Apply DFT along slow-time axis -> range-Doppler map.
    Three targets at different ranges and velocities appear as
    isolated bright cells in a 2-D heatmap.

Parameters mirror a real NEXRAD S-band unit (WSR-88D long-pulse mode):
  f_c  = 2.8 GHz   (S-band carrier)
  tau  = 1.6 us    (pulse duration)
  BW   = 0.625 MHz (chirp bandwidth; time-bandwidth product = 1.0)
  PRF  = 1000 Hz   (unambiguous range ~ 150 km, unamb velocity ~ 27 m/s)
  N_p  = 64        (pulses per coherent processing interval)
  fs   = 2 MHz     (fast-time sample rate within a pulse)

Targets (synthesised):
  T1: range 30 km, radial velocity +20 m/s (precipitation, approaching)
  T2: range 65 km, radial velocity   0 m/s (ground clutter analogue)
  T3: range 110 km, radial velocity -35 m/s (precipitation, receding)

Reproducibility seed: 20260512  (figures are byte-reproducible on re-runs)

Output (relative to fourier/docs/shad/figures/):
  fig-b5-input.png      time-domain: transmit chirp + noisy echo (stage 1)
  fig-b5-spectrum.png   bare 2-D range-Doppler heatmap (stage 3)
  fig-b5-takeaway.png   annotated range-Doppler map (all targets labelled)
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
RNG_SEED = 20260512

# ── Radar system parameters (NEXRAD WSR-88D long-pulse analogue) ───────────
C_LIGHT   = 3.0e8           # speed of light (m/s)
F_C       = 2.8e9           # S-band carrier (Hz)
TAU_S     = 1.6e-6          # pulse duration (s)
BW_HZ     = 0.625e6         # chirp bandwidth (Hz); TBP = BW * tau = 1.0
FS_HZ     = 2.0e6           # fast-time sample rate (Hz; = 2x chirp BW)
PRF_HZ    = 1_000.0         # pulse repetition frequency (Hz)
N_PULSES  = 64              # coherent processing interval (CPI) length
# Derived
LAMBDA    = C_LIGHT / F_C   # wavelength ~ 10.7 cm
T_PRI     = 1.0 / PRF_HZ   # pulse repetition interval (s)
R_UNAMBIG = C_LIGHT * T_PRI / 2.0          # max unambiguous range ~ 150 km
V_UNAMBIG = PRF_HZ * LAMBDA / 4.0          # max unambiguous speed  ~ 26.8 m/s
N_SAMP_PU = int(FS_HZ * TAU_S)             # samples per pulse  = 3
N_RANGE   = int(FS_HZ * T_PRI)             # samples per PRI   = 2000
CHIRP_K   = BW_HZ / TAU_S                  # chirp rate (Hz/s)

# ── Targets ────────────────────────────────────────────────────────────────
# (range_m, radial_velocity_m_s, relative_RCS)
TARGETS = [
    (30_000.0,   +20.0, 1.00),   # T1: approaching precipitation cell
    (65_000.0,     0.0, 0.50),   # T2: stationary (ground clutter analogue)
    (110_000.0, -35.0, 0.70),   # T3: receding  precipitation cell
]

# ── SNR budget ──────────────────────────────────────────────────────────────
# Raw single-pulse SNR per target (before compression or integration):
SINGLE_PULSE_SNR_DB = 0.0   # 0 dB — echo buried in noise

# After matched-filter compression: gain = TBP = BW*tau = 1.0 (our BW is tiny;
#   in a real NEXRAD super-resolution mode BW ~ 0.625 MHz gives TBP >> 1).
# After N_PULSES integration: gain = 10*log10(64) ~ 18 dB.
# Total expected SNR at output: ~ 18 dB — clearly visible above noise floor.


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════

def make_chirp() -> np.ndarray:
    """
    Build the complex baseband transmit chirp.

    A linear-FM (LFM) chirp sweeps from -BW/2 to +BW/2 over tau seconds:
        s_tx(t) = exp(j * pi * K * t^2),   0 <= t < tau
    where K = BW / tau is the chirp rate.

    In the frequency domain, a chirp has near-constant magnitude across BW
    and a quadratic phase.  The matched filter reverses this phase, producing
    a sinc-like compressed pulse whose 3-dB width is 1/BW.
    """
    t = np.arange(N_SAMP_PU) / FS_HZ          # time axis within the pulse
    # Complex baseband LFM chirp (equation LFM-1 in signal-processing literature)
    chirp = np.exp(1j * np.pi * CHIRP_K * t ** 2)
    return chirp.astype(np.complex128)


def range_delay_samples(range_m: float) -> int:
    """Convert range (metres) to round-trip delay in fast-time samples."""
    tau_rt = 2.0 * range_m / C_LIGHT       # round-trip travel time
    return int(np.round(tau_rt * FS_HZ))   # convert to sample index


def doppler_phase_per_pulse(vel_m_s: float) -> float:
    """
    Phase advance (radians) between successive pulses for a target moving
    at radial velocity v_r (positive = approaching radar).

    Each PRI the target moves v_r * T_PRI metres closer.  The two-way path
    shortens by 2 * v_r * T_PRI metres, adding a phase:
        phi = 2*pi * (2 * v_r * T_PRI) / lambda
            = 2*pi * v_r / (PRF * lambda / 2)
            = 2*pi * f_d / PRF
    where f_d = 2*v_r*f_c/c is the Doppler frequency.
    """
    f_doppler = 2.0 * vel_m_s * F_C / C_LIGHT
    return 2.0 * np.pi * f_doppler / PRF_HZ


def build_pulse_matrix(chirp: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """
    Build the full N_RANGE x N_PULSES raw receive matrix.

    For each of N_PULSES transmissions, each target contributes a delayed,
    Doppler-shifted, amplitude-scaled echo of the chirp.  White complex
    Gaussian noise is added to achieve the target single-pulse SNR.

    Returns shape: (N_RANGE, N_PULSES) complex128
    """
    # Signal amplitude from SNR target:
    #   SNR = A^2 / noise_power; noise_power = sigma^2 per complex sample
    noise_sigma = 1.0                          # normalise noise to unit power
    sig_amp_per_rcs1 = noise_sigma * 10 ** (SINGLE_PULSE_SNR_DB / 20.0)

    matrix = np.zeros((N_RANGE, N_PULSES), dtype=np.complex128)

    for pulse_idx in range(N_PULSES):
        # Add echo from each target
        for (r_m, v_mps, rcs) in TARGETS:
            delay     = range_delay_samples(r_m)
            dphi      = doppler_phase_per_pulse(v_mps)
            amplitude = sig_amp_per_rcs1 * np.sqrt(rcs)
            phase     = pulse_idx * dphi          # slow-time phase history

            # Inject chirp at delay offset (zero-pad if needed)
            end = delay + N_SAMP_PU
            if end <= N_RANGE:
                matrix[delay:end, pulse_idx] += amplitude * np.exp(1j * phase) * chirp

        # Additive white complex Gaussian noise
        noise = rng.normal(0, noise_sigma / np.sqrt(2), N_RANGE)
        noise = noise + 1j * rng.normal(0, noise_sigma / np.sqrt(2), N_RANGE)
        matrix[:, pulse_idx] += noise

    return matrix


# ═══════════════════════════════════════════════════════════════════════════
# PROCESSING — THE FOURIER PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def matched_filter_compress(raw_matrix: np.ndarray, chirp: np.ndarray) -> np.ndarray:
    """
    Stage 1+2: Apply matched filter along the fast-time (range) axis.

    The matched filter for signal s(t) is its time-reversed conjugate s*(-t).
    In the frequency domain, cross-correlation = pointwise multiply by conj(S(f)):

        compressed(t) = IFFT( FFT(rx) * conj(FFT(tx)) )

    This is the same DFT we have been using throughout the Shad tier,
    now used for extraction rather than description.

    Parameters
    ----------
    raw_matrix : shape (N_RANGE, N_PULSES)
    chirp      : shape (N_SAMP_PU,) — the known transmit waveform

    Returns
    -------
    compressed : shape (N_RANGE, N_PULSES)
        Each column is one pulse's range profile after compression.
    """
    N_FFT = N_RANGE              # FFT length = full PRI length

    # Pre-compute the reference spectrum (zero-padded to N_FFT)
    chirp_padded = np.zeros(N_FFT, dtype=np.complex128)
    chirp_padded[:N_SAMP_PU] = chirp
    TX = np.fft.fft(chirp_padded)   # transmit reference spectrum
    TX_CONJ = np.conj(TX)           # conjugate = matched filter kernel

    compressed = np.zeros_like(raw_matrix)
    for p in range(N_PULSES):
        RX = np.fft.fft(raw_matrix[:, p], n=N_FFT)   # receive spectrum
        # Multiply: correlation in time = conjugate-product in frequency
        compressed[:, p] = np.fft.ifft(RX * TX_CONJ).real

    return compressed


def range_doppler_map(compressed: np.ndarray) -> np.ndarray:
    """
    Stage 3: Compute range-Doppler map via slow-time DFT.

    After pulse compression, each row of 'compressed' is a range profile.
    A DFT across the N_PULSES dimension of each range bin extracts the
    Doppler frequency of any target present at that range:

        RD[range_bin, doppler_bin] = DFT_slow_time( compressed[range_bin, :] )

    The Doppler axis spans -PRF/2 to +PRF/2 (after fftshift),
    which maps to radial velocities -V_unambig to +V_unambig.

    Parameters
    ----------
    compressed : shape (N_RANGE, N_PULSES)

    Returns
    -------
    rd_map : shape (N_RANGE, N_PULSES), magnitude of the Doppler DFT,
             with Doppler axis zero-centred (fftshift applied).
    """
    # Apply Hann window along slow-time to suppress Doppler sidelobes
    window = np.hanning(N_PULSES)                        # shape (N_PULSES,)
    windowed = compressed * window[np.newaxis, :]        # broadcast over range

    # DFT across slow-time (axis=1)
    rd_complex = np.fft.fft(windowed, axis=1)            # shape (N_RANGE, N_PULSES)

    # fftshift to centre zero-Doppler
    rd_shifted = np.fft.fftshift(rd_complex, axes=1)

    return np.abs(rd_shifted)


# ═══════════════════════════════════════════════════════════════════════════
# AXIS UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def range_axis_km() -> np.ndarray:
    """Range axis in kilometres: 0 to R_unambig."""
    return np.arange(N_RANGE) * C_LIGHT / (2.0 * FS_HZ) / 1_000.0


def velocity_axis_ms() -> np.ndarray:
    """
    Doppler velocity axis (m/s), zero-centred after fftshift.
    Bin spacing = PRF / N_PULSES.  Range = [-V_unambig, +V_unambig].
    """
    f_bins = np.fft.fftshift(np.fft.fftfreq(N_PULSES, d=1.0 / PRF_HZ))
    return f_bins * LAMBDA / 2.0     # frequency -> radial velocity


# ═══════════════════════════════════════════════════════════════════════════
# FIGURES
# ═══════════════════════════════════════════════════════════════════════════

COLORS = {
    "tx":     "#1f4e79",
    "rx":     "#b04040",
    "target": ["#22882e", "#c07000", "#b02020"],
}


def fig_input(chirp: np.ndarray, raw_matrix: np.ndarray,
              out: pathlib.Path) -> None:
    """
    Two-panel time-domain figure:
    Panel 1: transmit chirp (real part; shows FM sweep)
    Panel 2: received echo for pulse 0, first 300 samples — shows the
             noise floor and the faint echo from T1 at delay ~ 200 samples.
    """
    t_pulse_us = np.arange(N_SAMP_PU) / FS_HZ * 1e6   # microseconds

    # Single-pulse receive signal (pulse 0), converted to time axis in us
    t_rx_us = np.arange(N_RANGE) / FS_HZ * 1e6
    rx_real = raw_matrix[:, 0].real

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.5))
    fig.suptitle("B5 – Radar: transmit chirp and noisy received echo", fontsize=11)

    # Panel 1: transmit chirp
    ax1.plot(t_pulse_us, chirp.real, lw=1.0, color=COLORS["tx"], label="Re{tx chirp}")
    ax1.plot(t_pulse_us, chirp.imag, lw=0.7, color="#4090c0", alpha=0.6,
             label="Im{tx chirp}", linestyle="--")
    ax1.set_xlabel("Time within pulse (µs)")
    ax1.set_ylabel("Amplitude")
    ax1.set_title(f"Transmit: linear-FM chirp, BW={BW_HZ/1e6:.3f} MHz, "
                  f"τ={TAU_S*1e6:.1f} µs")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(alpha=0.3)

    # Panel 2: received echo (first 400 samples ≈ first 200 µs ≈ 0–30 km range)
    show_n = 400
    ax2.plot(t_rx_us[:show_n], rx_real[:show_n], lw=0.6,
             color=COLORS["rx"], label="Re{rx echo} — pulse 0")
    # Mark where T1's echo is expected
    d1 = range_delay_samples(TARGETS[0][0])
    ax2.axvspan(d1 / FS_HZ * 1e6, (d1 + N_SAMP_PU) / FS_HZ * 1e6,
                alpha=0.18, color="#22882e", label=f"T1 echo window (range {TARGETS[0][0]/1e3:.0f} km)")
    ax2.set_xlabel("Fast time (µs)   [= round-trip range / c × 10⁶]")
    ax2.set_ylabel("Amplitude")
    ax2.set_title(f"Received echo: SNR ≈ {SINGLE_PULSE_SNR_DB:.0f} dB raw — "
                  "echo buried in noise (first 200 µs shown)")
    ax2.legend(fontsize=8, loc="upper right")
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_spectrum(rd_map: np.ndarray, range_km: np.ndarray,
                 vel_ms: np.ndarray, out: pathlib.Path) -> None:
    """
    Bare range-Doppler heatmap (log magnitude, dB scale).
    Rows = range bins (km), columns = Doppler bins (m/s).
    Uses imshow with extent set to physical axes.
    """
    rd_db = 20.0 * np.log10(rd_map + 1e-12)   # avoid log(0)
    # Crop to interesting range/velocity window
    r_max_idx = int(130_000 / (C_LIGHT / (2.0 * FS_HZ)))   # 130 km
    rd_crop   = rd_db[:r_max_idx, :]
    r_axis    = range_km[:r_max_idx]

    vmin = np.percentile(rd_crop, 5)
    vmax = np.percentile(rd_crop, 99.5)

    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(rd_crop, aspect="auto", origin="lower",
                   extent=[vel_ms[0], vel_ms[-1], r_axis[0], r_axis[-1]],
                   cmap="turbo", vmin=vmin, vmax=vmax, interpolation="nearest")
    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label("Magnitude (dB)", fontsize=9)
    ax.set_xlabel("Radial velocity (m/s)  [negative = receding]")
    ax.set_ylabel("Range (km)")
    ax.set_title("B5 – Range-Doppler map (bare): 2-D DFT over 64 pulses")
    ax.grid(alpha=0.2, color="white", lw=0.4)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_takeaway(rd_map: np.ndarray, range_km: np.ndarray,
                 vel_ms: np.ndarray, out: pathlib.Path) -> None:
    """
    Annotated range-Doppler map: each target cell labelled, wind-gradient
    region highlighted, PRF-fold ambiguity zone marked.
    """
    rd_db = 20.0 * np.log10(rd_map + 1e-12)
    r_max_idx = int(130_000 / (C_LIGHT / (2.0 * FS_HZ)))
    rd_crop   = rd_db[:r_max_idx, :]
    r_axis    = range_km[:r_max_idx]

    vmin = np.percentile(rd_crop, 5)
    vmax = np.percentile(rd_crop, 99.5)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(rd_crop, aspect="auto", origin="lower",
              extent=[vel_ms[0], vel_ms[-1], r_axis[0], r_axis[-1]],
              cmap="turbo", vmin=vmin, vmax=vmax, interpolation="nearest")

    # Annotate each target
    ann_params = [
        # (true range km, true vel m/s, label, text_offset)
        (30.0,   +20.0, "T1: precip cell\n30 km, +20 m/s\n(approaching)",   (+2, +8)),
        (65.0,     0.0, "T2: ground clutter\n65 km, 0 m/s",                  (+2, +10)),
        (110.0, -35.0,  "T3: precip cell\n110 km, −35 m/s\n(receding)",      (+2, -15)),
    ]
    for r_km, v_ms, lbl, (dv, dr) in ann_params:
        ax.annotate(lbl,
                    xy=(v_ms, r_km),
                    xytext=(v_ms + dv, r_km + dr),
                    fontsize=8, color="white",
                    arrowprops=dict(arrowstyle="->", color="white", lw=0.9),
                    bbox=dict(boxstyle="round,pad=0.2",
                              facecolor="#00000080", edgecolor="none"))

    # Mark zero-Doppler line (clutter ridge)
    ax.axvline(0, color="#ffffff80", lw=0.9, linestyle="--")
    ax.text(0.5, 118, "zero-Doppler\n(stationary clutter)", color="white",
            fontsize=7.5, ha="left",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#00000070",
                      edgecolor="none"))

    # Mark Doppler unambiguous limits
    v_u = V_UNAMBIG
    for sign, label in [(+1, f"+V_unamb\n+{v_u:.1f} m/s"),
                         (-1, f"−V_unamb\n−{v_u:.1f} m/s")]:
        ax.axvline(sign * v_u, color="yellow", lw=0.7, linestyle=":",
                   alpha=0.6)
        ax.text(sign * v_u + 0.4, 5, label, color="yellow",
                fontsize=6.5, ha="center", va="bottom",
                bbox=dict(boxstyle="round,pad=0.1",
                          facecolor="#00000080", edgecolor="none"))

    ax.set_xlabel("Radial velocity (m/s)   [negative = receding from radar]",
                  fontsize=9)
    ax.set_ylabel("Range (km)", fontsize=9)
    ax.set_title("B5 takeaway – reading the range-Doppler map like a radar engineer",
                 fontsize=10)
    ax.grid(alpha=0.15, color="white", lw=0.4)
    fig.tight_layout()
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

    rng   = np.random.default_rng(RNG_SEED)
    chirp = make_chirp()

    print("Building raw pulse matrix (64 pulses × 2000 fast-time samples)…")
    raw = build_pulse_matrix(chirp, rng)

    print("Applying matched-filter pulse compression (range DFT + conjugate multiply)…")
    compressed = matched_filter_compress(raw, chirp)

    print("Computing range-Doppler map (slow-time DFT over 64 pulses)…")
    rd_map   = range_doppler_map(compressed)
    range_km = range_axis_km()
    vel_ms   = velocity_axis_ms()

    # Verify targets are visible: find peak in each target region
    print("\nTarget detection summary:")
    for label, (r_m, v_mps, rcs) in zip(["T1", "T2", "T3"], TARGETS):
        r_bin = range_delay_samples(r_m)
        f_d   = 2.0 * v_mps * F_C / C_LIGHT
        v_bin_raw = int(np.round(f_d / PRF_HZ * N_PULSES))
        v_bin = (N_PULSES // 2 + v_bin_raw) % N_PULSES   # after fftshift
        window = 5
        r_sl = slice(max(0, r_bin - window), min(N_RANGE, r_bin + window))
        v_sl = slice(max(0, v_bin - window), min(N_PULSES, v_bin + window))
        peak = rd_map[r_sl, v_sl].max()
        noise_floor = np.median(rd_map)
        snr_est = 20 * np.log10(peak / (noise_floor + 1e-12))
        print(f"  {label}: range {r_m/1e3:.0f} km, vel {v_mps:+.0f} m/s  "
              f"-> estimated peak SNR {snr_est:.1f} dB")

    print(f"\nSystem parameters:")
    print(f"  Unambiguous range:    {R_UNAMBIG/1e3:.0f} km")
    print(f"  Unambiguous velocity: ±{V_UNAMBIG:.1f} m/s")
    print(f"  Range resolution:     {C_LIGHT/(2*BW_HZ):.0f} m  (= c / 2BW)")
    print(f"  Velocity resolution:  {PRF_HZ*LAMBDA/2/N_PULSES*100:.0f} cm/s  (= PRF*lambda/2/N_pulses)")

    print("\nRendering figures…")
    fig_input(chirp, raw, args.out_dir / "fig-b5-input.png")
    fig_spectrum(rd_map, range_km, vel_ms, args.out_dir / "fig-b5-spectrum.png")
    fig_takeaway(rd_map, range_km, vel_ms, args.out_dir / "fig-b5-takeaway.png")
    print(f"Figures saved to: {args.out_dir}")
    return 0


# ── Real-data extension notes ──────────────────────────────────────────────
# NEXRAD Level-II data is public domain (NOAA / AWS Open Data):
#   https://registry.opendata.aws/noaa-nexrad/
#   Format: bzip2-compressed binary; use PyART (pip install arm_pyart) or
#   wradlib (pip install wradlib) to read Level-II volumes.
#   The Doppler velocity field is pre-computed by the WSR-88D unit; you can
#   also work from the raw I/Q if your dataset includes it (Level-2.5 mode).
# The matched-filter and range-Doppler pipeline above is structurally
# identical to what the WSR-88D's signal processor does, just at 2.8 GHz
# instead of our baseband 2 MHz simulation.

if __name__ == "__main__":
    raise SystemExit(main())
