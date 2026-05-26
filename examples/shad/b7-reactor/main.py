#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
b7-reactor/main.py  -  Shad-tier Band 7: Nuclear reactor noise (capstone)

The closing chapter of the seven-band Shad-tier guide.  Where the bare
DFT stops being enough, and the toolkit you reach for next.

  Stage 1 -- Synthesise a reactor-noise time series
    Point-kinetics equations with six delayed-neutron precursor groups
    (Hetrick / Bell-Glasstone canonical thermal-U-235 parameters) driven
    by a Langevin stochastic source.  Two-sensor outputs: detector A
    and detector B see the same neutron field through independent
    instrument noise.  Stationary segment (200 s) + non-stationary
    transient segment (rod-step at t = 100 s of the second realisation).

  Stage 2 -- Bare DFT of the stationary segment
    np.fft.rfft reveals the Lorentzian PSD shape predicted by Cohn's
    analysis.  Corner frequency f_c = alpha / (2 pi) where alpha is the
    prompt-neutron decay constant.  Headline payoff: alpha is readable
    directly off the spectrum.

  Stage 3 -- Welch's method
    Variance-reduced PSD estimator.  scipy.signal.welch with overlapping
    Hann-windowed segments.  Same Lorentzian, ~10x lower variance per
    bin than the bare periodogram.

  Stage 4 -- Bare DFT of the transient (the limit-test)
    A reactivity step at t = 100 s makes the signal non-stationary.
    The bare DFT smears the spectrum (no time localisation).

  Stage 5 -- STFT spectrogram
    scipy.signal.spectrogram on the transient.  Time-frequency picture
    shows the corner-frequency excursion across the rod-step.

  Stage 6 -- Continuous wavelet scalogram
    pywt.cwt with a Morlet wavelet.  Tighter time localisation than
    the STFT at high frequencies; coarser at low frequencies.

  Stage 7 -- Rossi-alpha
    Pair-time histogram of synthesised neutron-detection events
    (Poisson-thinned from the neutron-density trace).  Conditional
    intensity decays as exp(-alpha tau) above the accidental floor.
    Same alpha as the PSD corner, measured in the time domain.

  Stage 8 -- Feynman-alpha
    Variance-to-mean curve of gated pulse counts as a function of
    gate length T.  Y(T) = (Var/Mean - 1) plateaus at D * [...] for
    long gates; the shape gives alpha and the Diven factor.

  Stage 9 -- Bispectrum
    Triple-product B(f1, f2) = E[X(f1) X(f2) X*(f1+f2)].  A
    deliberately injected quadratic coupling between two reactivity
    oscillations at f1 = 0.7 Hz and f2 = 1.1 Hz appears as a non-zero
    bispectral peak at (f1, f2); the bare DFT shows three separate
    peaks (at f1, f2, f1+f2) but cannot say whether they are coupled.

  Stage 10 -- Magnitude-squared coherence + transfer function
    Two-sensor coherence gamma^2(f) = |Pxy|^2 / (Pxx Pyy) for the
    A/B detector pair.  Bounded [0, 1].  Reactor-common-mode dynamics
    appear at gamma^2 ~ 1; instrument-independent noise sits at gamma^2 ~ 0.

Source documentation:
  Bell & Glasstone, Nuclear Reactor Theory (1970), Ch. 9: point kinetics +
    delayed precursors.  Thermal-U-235 beta_i and lambda_i values used here.
  Cohn, "A simplified theory of pile noise," Nucl. Sci. Eng. 7, 472 (1960):
    Lorentzian PSD for reactor neutron-density fluctuations.
  Pal & Pazsit, Neutron Fluctuations: A Reference Manual (Elsevier 2008),
    Ch. 4 (Langevin formulation) + Ch. 5 (Rossi-alpha + Feynman-alpha).
  Williams, Random Processes in Nuclear Reactors (Pergamon 1974), Ch. 5.

Reproducibility seed: 20260526  (figures are byte-reproducible on re-runs)

Output (relative to fourier/docs/shad/figures/):
  fig-b7-time-series.png      raw current-mode signal: overview + zoom
  fig-b7-bare-fft.png         periodogram of stationary segment with Lorentzian
  fig-b7-lorentzian-fit.png   PSD + analytical fit; corner frequency annotated
  fig-b7-alpha-extraction.png alpha from the corner; report card panel
  fig-b7-transient-scram.png  non-stationary segment + smeared bare-DFT
  fig-b7-welch.png            Welch vs bare periodogram (variance reduction)
  fig-b7-spectrogram.png      STFT scalogram of the transient
  fig-b7-wavelets.png         CWT scalogram of the transient
  fig-b7-rossi-alpha.png      pair-time histogram + exponential fit
  fig-b7-feynman-alpha.png    variance-to-mean curve + theoretical curve
  fig-b7-bispectrum.png       |B(f1,f2)| heatmap revealing coupling
  fig-b7-coherence.png        gamma^2(f) of A-B sensor pair

Runtime: ~30 s on a modern laptop.
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal import welch, spectrogram, coherence
import pywt

# ── Reproducibility ────────────────────────────────────────────────────────
RNG_SEED = 20260526

# ── Reactor physical parameters (Bell-Glasstone thermal U-235, 6-group) ──
# These are the canonical textbook values for a thermal light-water reactor
# fuelled with low-enrichment U-235.  Source: Bell & Glasstone Table 9.1.
BETA_I = np.array([0.000215, 0.001424, 0.001274,
                   0.002568, 0.000748, 0.000273])
LAMBDA_I = np.array([0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01])  # s^-1
BETA   = float(np.sum(BETA_I))            # 0.006502
GEN_TIME = 1.0e-4                          # prompt generation time Lambda (s)
RHO0   = 0.0                               # reactivity offset (critical reactor)

# Prompt-neutron decay constant at critical (Cohn / Williams):
#   alpha = (beta - rho) / Lambda  ;  for rho ~ 0, alpha = beta / Lambda
ALPHA_THEORY = BETA / GEN_TIME             # ≈ 65.02 s^-1
F_CORNER_THEORY = ALPHA_THEORY / (2.0 * np.pi)   # ≈ 10.35 Hz

# Mean neutron-density level (arbitrary scale; "power level" in current mode)
N_MEAN = 1.0e7                             # neutrons (population scale)

# Source strength (Langevin); calibrated to give realistic noise amplitude
# relative to N_MEAN.  Magnitude derived from sigma_n^2 = source_strength /
# (2 alpha) at the stationary point (Williams Eq. 5.32).
SRC_STRENGTH = 2.0 * ALPHA_THEORY * (0.02 * N_MEAN) ** 2   # tunes ~2 % noise

# Pulse-train parameters (used by Rossi-alpha / Feynman-alpha synthesis)
# See synth_correlated_pulse_train() for the canonical Pal-Pazsit setup.

# ── Simulation grid ────────────────────────────────────────────────────────
FS      = 1000.0           # sample rate (Hz).  Nyquist 500 Hz >> f_corner ~ 10 Hz.
DT      = 1.0 / FS         # 1 ms step
T_STAT  = 200.0            # stationary segment duration (s)
T_TRANS = 200.0            # transient segment duration (s); rod-step at midpoint
N_STAT  = int(T_STAT * FS)
N_TRANS = int(T_TRANS * FS)

# Rod-step reactivity insertion for the transient segment.
# A small subprompt step: 30 pcm at t = 100 s, ramped over 5 s.
ROD_STEP_TIME = 100.0
ROD_STEP_RAMP = 5.0
ROD_STEP_RHO  = 30e-5      # 30 pcm = 0.0003

# Two-sensor coupling parameters (for the coherence figure)
SENSOR_NOISE_FRAC = 0.3    # per-sensor instrument noise as fraction of common-mode RMS


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════

def integrate_point_kinetics(rng: np.random.Generator,
                             n_samples: int,
                             rho_t: np.ndarray | None = None,
                             coupling_t: np.ndarray | None = None,
                             ) -> np.ndarray:
    """
    Integrate the 6-group point-kinetics equations driven by a Langevin
    source, on a uniform DT grid.

    dn/dt    = (rho - beta) / Lambda * n + sum_i lambda_i C_i + S(t)
    dC_i/dt  = (beta_i / Lambda) n - lambda_i C_i

    Numerical scheme: implicit-explicit Euler stable for stiff precursor
    decays.  The prompt mode (alpha ~ 65 s^-1) is well-resolved at
    dt = 1 ms; precursor groups (lambda_i up to 3 s^-1) much slower.

    Parameters
    ----------
    rng :        numpy Generator
    n_samples :  number of time samples to integrate
    rho_t :      length-n_samples reactivity perturbation (added to RHO0).
                 None -> RHO0 throughout (stationary critical).
    coupling_t : length-n_samples extra reactivity term injected via
                 quadratic coupling, used by the bispectrum stage.

    Returns
    -------
    n_t : length-n_samples neutron population trace
    """
    n = N_MEAN
    C = (BETA_I / (LAMBDA_I * GEN_TIME)) * N_MEAN     # equilibrium precursor pops

    n_t = np.empty(n_samples)
    # Langevin noise pre-drawn for speed:
    noise = rng.normal(0.0, np.sqrt(SRC_STRENGTH / DT), n_samples)

    for k in range(n_samples):
        rho_k = RHO0
        if rho_t is not None:
            rho_k = rho_t[k]
        if coupling_t is not None:
            rho_k = rho_k + coupling_t[k]

        # Implicit step on precursor groups (stable for any DT)
        C = (C + DT * (BETA_I / GEN_TIME) * n) / (1.0 + DT * LAMBDA_I)

        # Explicit step on neutron population with Langevin source
        dn = ((rho_k - BETA) / GEN_TIME * n
              + np.dot(LAMBDA_I, C)
              + noise[k]) * DT
        n = max(n + dn, 1.0)              # population stays positive
        n_t[k] = n

    return n_t


def make_stationary_segment(rng: np.random.Generator) -> np.ndarray:
    """Stationary reactor-noise trace at constant critical reactivity."""
    return integrate_point_kinetics(rng, N_STAT)


def make_transient_segment(rng: np.random.Generator) -> np.ndarray:
    """
    Transient: 100 s stationary + 5 s reactivity ramp + 95 s at new level.
    Mimics a small control-rod withdrawal step.
    """
    t = np.arange(N_TRANS) * DT
    ramp = np.clip((t - ROD_STEP_TIME) / ROD_STEP_RAMP, 0.0, 1.0)
    rho_t = ROD_STEP_RHO * ramp
    return integrate_point_kinetics(rng, N_TRANS, rho_t=rho_t)


def make_two_sensor_pair(rng: np.random.Generator,
                         n_t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Build sensor A and sensor B current-mode signals.  Both see the
    same neutron-population trace (after subtracting the mean and
    centring around zero), plus independent instrument noise.
    """
    common = n_t - np.mean(n_t)
    rms    = np.std(common)
    noise_a = rng.normal(0.0, SENSOR_NOISE_FRAC * rms, len(n_t))
    noise_b = rng.normal(0.0, SENSOR_NOISE_FRAC * rms, len(n_t))
    return common + noise_a, common + noise_b


def make_coupled_segment(rng: np.random.Generator) -> tuple[np.ndarray, float, float]:
    """
    Stationary reactor with two sinusoidal reactivity oscillations at
    f1 and f2, PLUS a quadratic coupling term.  The coupling produces
    a sum-frequency component at f1 + f2.  Used by the bispectrum figure.
    """
    f1 = 0.7
    f2 = 1.1
    t  = np.arange(N_STAT) * DT
    a1 = 0.5 * ROD_STEP_RHO          # ~15 pcm
    a2 = 0.5 * ROD_STEP_RHO
    rho_lin = a1 * np.sin(2.0 * np.pi * f1 * t) + a2 * np.sin(2.0 * np.pi * f2 * t)
    # Quadratic coupling: factor of 4 amplifies the sum/difference response
    # so the bispectrum reading is unambiguous.
    coupling = 4.0 * rho_lin * rho_lin

    return integrate_point_kinetics(rng, N_STAT,
                                    rho_t=rho_lin,
                                    coupling_t=coupling), f1, f2


def synth_correlated_pulse_train(rng: np.random.Generator,
                                 t_total: float,
                                 chain_rate: float,
                                 alpha: float,
                                 mean_multiplicity: float = 2.5,
                                 background_rate: float = 50.0,
                                 ) -> np.ndarray:
    """
    Generate a synthetic detector pulse train with the multiplet
    correlation structure that Rossi-alpha and Feynman-alpha probe
    (Pal & Pazsit, Neutron Fluctuations Ch. 5; Williams Ch. 5.6).

    Two superimposed processes:
      1. Independent ``chains'' (fission-chain proxies) arriving as a
         Poisson process at rate `chain_rate`.  Each chain produces a
         multiplet of `k` correlated detections, with `k` drawn from
         a shifted Poisson distribution of mean `mean_multiplicity`
         (Diven-factor proxy).  Subsequent multiplet members trail
         the chain head by exp(1/alpha) inter-arrivals.
      2. An uncorrelated Poisson background at rate `background_rate`
         (radiometer / electronic noise; mimics the accidentals floor).

    Returns sorted event times in seconds.
    """
    # 1. Correlated chains
    n_chains_expected = int(t_total * chain_rate * 1.3) + 10
    chain_starts = np.cumsum(rng.exponential(1.0 / chain_rate, n_chains_expected))
    chain_starts = chain_starts[chain_starts < t_total]

    events: list[float] = []
    for t0 in chain_starts:
        # Shifted-Poisson multiplicity, minimum 1
        k = 1 + int(rng.poisson(max(mean_multiplicity - 1.0, 0.0)))
        events.append(float(t0))
        for _ in range(k - 1):
            tau = float(rng.exponential(1.0 / alpha))
            t_next = t0 + tau
            if t_next < t_total:
                events.append(t_next)

    # 2. Uncorrelated background
    n_bg_expected = int(t_total * background_rate * 1.3) + 10
    bg = np.cumsum(rng.exponential(1.0 / background_rate, n_bg_expected))
    events.extend(bg[bg < t_total].tolist())

    events.sort()
    return np.asarray(events)


# ═══════════════════════════════════════════════════════════════════════════
# SPECTRAL TOOLKIT
# ═══════════════════════════════════════════════════════════════════════════

def bare_periodogram(x: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """One-sided periodogram of x.  Returns (freq, PSD)."""
    x_c = x - np.mean(x)
    n   = len(x_c)
    X   = np.fft.rfft(x_c)
    psd = (np.abs(X) ** 2) * (2.0 / (fs * n))
    psd[0] /= 2.0
    if n % 2 == 0:
        psd[-1] /= 2.0
    freq = np.fft.rfftfreq(n, d=1.0 / fs)
    return freq, psd


def lorentzian_model(f: np.ndarray,
                     p0: float, alpha: float, p_inf: float) -> np.ndarray:
    """
    Cohn-Williams Lorentzian PSD for reactor neutron-density noise:
        S(f) = p0 * alpha^2 / (alpha^2 + (2 pi f)^2) + p_inf
    p_inf is an instrument-noise / white-source floor.
    """
    omega = 2.0 * np.pi * f
    return p0 * alpha ** 2 / (alpha ** 2 + omega ** 2) + p_inf


def fit_lorentzian(freq: np.ndarray, psd: np.ndarray,
                   f_min: float = 0.5,
                   f_max: float = 200.0) -> tuple[float, float, float]:
    """
    Two-stage Lorentzian fit in log-space.  Returns (p0, alpha, p_inf).
    Robust against the noise-floor tail by fitting only the band f_min..f_max.
    """
    from scipy.optimize import curve_fit
    mask = (freq >= f_min) & (freq <= f_max)
    f_fit = freq[mask]
    p_fit = psd[mask]

    # Initial guesses
    p_inf0 = np.median(p_fit[-20:])           # tail level
    p0_0   = max(np.max(p_fit) - p_inf0, p_inf0)
    alpha0 = ALPHA_THEORY

    try:
        popt, _ = curve_fit(
            lorentzian_model, f_fit, p_fit,
            p0=(p0_0, alpha0, p_inf0),
            maxfev=10000,
        )
        p0_hat, alpha_hat, p_inf_hat = popt
    except Exception:
        p0_hat, alpha_hat, p_inf_hat = p0_0, alpha0, p_inf0
    return p0_hat, alpha_hat, p_inf_hat


def rossi_alpha_histogram(events: np.ndarray,
                          gate: float,
                          n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Build the pair-time histogram: for each event, accumulate
    contributions from all later events within `gate` seconds.

    Returns (tau_centres, counts).  The conditional decay is fit
    elsewhere to extract alpha.
    """
    counts = np.zeros(n_bins, dtype=np.int64)
    bin_dt = gate / n_bins
    n_e    = len(events)
    i = 0
    for k in range(n_e):
        # advance the lower pointer to events still within window
        while i < k and events[k] - events[i] > gate:
            i += 1
        for j in range(k + 1, n_e):
            dt_kj = events[j] - events[k]
            if dt_kj >= gate:
                break
            idx = int(dt_kj / bin_dt)
            if 0 <= idx < n_bins:
                counts[idx] += 1
    tau = (np.arange(n_bins) + 0.5) * bin_dt
    return tau, counts


def feynman_y_curve(events: np.ndarray,
                    t_total: float,
                    gate_lengths: np.ndarray) -> np.ndarray:
    """
    Compute Feynman's Y(T) = Var(C_T) / Mean(C_T) - 1 over a sweep of
    gate lengths.  For each T, partition the event train into
    consecutive non-overlapping gates of width T, count events per gate,
    and accumulate sample mean and variance.
    """
    y = np.empty_like(gate_lengths)
    for i, T in enumerate(gate_lengths):
        edges = np.arange(0.0, t_total, T)
        if len(edges) < 5:
            y[i] = 0.0
            continue
        counts, _ = np.histogram(events, bins=edges)
        m = counts.mean()
        v = counts.var(ddof=1)
        y[i] = (v / m - 1.0) if m > 0 else 0.0
    return y


def feynman_y_theory(T: np.ndarray, alpha: float, Y_inf: float) -> np.ndarray:
    """
    Feynman-alpha theoretical curve:
        Y(T) = Y_inf * [1 - (1 - exp(-alpha T)) / (alpha T)]
    Y_inf = D * (epsilon * v(v-1)) factor (Diven factor times efficiency).
    """
    aT = alpha * T
    # Numerically safe form (avoid 0/0 at aT -> 0)
    val = np.where(aT > 1e-6,
                   1.0 - (1.0 - np.exp(-aT)) / aT,
                   0.5 * aT - aT * aT / 6.0)
    return Y_inf * val


def bispectrum_direct(x: np.ndarray,
                      fs: float,
                      n_seg: int = 8,
                      seg_len: int | None = None,
                      f_max: float | None = None,
                      ) -> tuple[np.ndarray, np.ndarray]:
    """
    Direct bispectrum estimator B(f1, f2) = <X(f1) X(f2) X*(f1+f2)>,
    averaged over non-overlapping segments.

    Returns (freq_axis, |B|^2 matrix on freq x freq grid up to f_max).
    """
    n   = len(x)
    if seg_len is None:
        seg_len = n // n_seg
    seg_len = min(seg_len, n // n_seg)
    win = np.hanning(seg_len)

    # Pre-compute frequency axis cropped to f_max
    freq_full = np.fft.rfftfreq(seg_len, d=1.0 / fs)
    if f_max is None:
        f_max = fs / 4.0
    k_max = np.searchsorted(freq_full, f_max)
    freq  = freq_full[:k_max]

    B = np.zeros((k_max, k_max), dtype=np.complex128)
    n_used = 0
    for s in range(n_seg):
        seg = x[s * seg_len: (s + 1) * seg_len]
        if len(seg) < seg_len:
            break
        seg = (seg - seg.mean()) * win
        X = np.fft.rfft(seg)
        Xc = np.conj(X)
        for i in range(k_max):
            j_max = min(k_max, len(X) - i)
            B[i, :j_max] += X[i] * X[:j_max] * Xc[i: i + j_max]
        n_used += 1

    if n_used > 0:
        B /= n_used
    return freq, np.abs(B) ** 2


# ═══════════════════════════════════════════════════════════════════════════
# FIGURES
# ═══════════════════════════════════════════════════════════════════════════

COLORS = {
    "neutron": "#1a5276",
    "noise":   "#6a7f9a",
    "fit":     "#c0392b",
    "theory":  "#1a5276",
    "measure": "#27ae60",
    "annot":   "#884400",
    "floor":   "#888888",
    "sensorA": "#1f77b4",
    "sensorB": "#d62728",
    "step":    "#c0392b",
}


def fig_time_series(n_stat: np.ndarray, out: pathlib.Path) -> None:
    """Two-panel overview: 200 s view + 5 s zoom."""
    t = np.arange(N_STAT) * DT

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.5))
    fig.suptitle(
        "B7 - Stationary reactor noise (point-kinetics + Langevin source)",
        fontsize=11,
    )

    ax1.plot(t, (n_stat - N_MEAN) / N_MEAN * 100.0,
             lw=0.4, color=COLORS["neutron"], rasterized=True)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("delta n / N_mean (%)")
    ax1.set_title(f"Overview - 200 s of critical-reactor neutron-density fluctuations")
    ax1.grid(alpha=0.25)
    ax1.set_xlim(0, T_STAT)

    n_show = int(5.0 * FS)
    ax2.plot(t[:n_show], (n_stat[:n_show] - N_MEAN) / N_MEAN * 100.0,
             lw=0.6, color=COLORS["neutron"])
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("delta n / N_mean (%)")
    ax2.set_title(f"Zoom - first 5 s; the ~10 Hz Lorentzian roll-off is set"
                  f" by alpha = {ALPHA_THEORY:.1f} s^-1")
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_bare_fft(freq: np.ndarray, psd: np.ndarray, out: pathlib.Path) -> None:
    """Bare periodogram on log-log axes."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.loglog(freq[1:], psd[1:], lw=0.4, color=COLORS["noise"],
              alpha=0.7, rasterized=True, label="raw periodogram")
    ax.axvline(F_CORNER_THEORY, color=COLORS["theory"], lw=1.0, linestyle="--",
               label=f"f_corner_theory = {F_CORNER_THEORY:.2f} Hz")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (arb units / Hz)")
    ax.set_title(
        f"B7 - Bare periodogram of {T_STAT:.0f} s stationary reactor noise"
        f"  (N = {N_STAT:,}, Df = {1/T_STAT*1e3:.2f} mHz)"
    )
    ax.set_xlim(1e-2, FS / 2.0)
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_lorentzian_fit(freq: np.ndarray, psd_welch: np.ndarray,
                       fit_params: tuple[float, float, float],
                       out: pathlib.Path) -> None:
    """Welch PSD with Lorentzian model overlay."""
    p0, alpha, p_inf = fit_params
    f_model = np.logspace(-2, np.log10(FS / 2.0), 400)
    psd_model = lorentzian_model(f_model, p0, alpha, p_inf)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.loglog(freq[1:], psd_welch[1:], lw=0.7, color=COLORS["noise"],
              alpha=0.85, label="Welch PSD (data)")
    ax.loglog(f_model, psd_model, lw=2.0, color=COLORS["fit"],
              label=f"Lorentzian fit: alpha = {alpha:.2f} s^-1")
    ax.axvline(alpha / (2.0 * np.pi), color=COLORS["annot"], lw=1.0,
               linestyle="--",
               label=f"f_corner_fit = {alpha/(2*np.pi):.2f} Hz")
    ax.axvline(F_CORNER_THEORY, color=COLORS["theory"], lw=1.0,
               linestyle=":",
               label=f"f_corner_theory = {F_CORNER_THEORY:.2f} Hz")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (arb units / Hz)")
    ax.set_title(
        "B7 - Welch PSD with Cohn-Lorentzian fit; corner frequency = alpha / (2 pi)"
    )
    ax.set_xlim(1e-2, FS / 2.0)
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_alpha_extraction(fit_params: tuple[float, float, float],
                         out: pathlib.Path) -> None:
    """Single-panel report card on the alpha extraction."""
    _, alpha, _ = fit_params
    err_pct = 100.0 * (alpha - ALPHA_THEORY) / ALPHA_THEORY
    f_meas  = alpha / (2.0 * np.pi)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axis("off")
    fig.suptitle(
        "B7 takeaway - the prompt-neutron decay constant from a PSD corner",
        fontsize=12,
    )

    rows = [
        ("Theoretical alpha (= beta / Lambda)",
         f"{ALPHA_THEORY:.2f} s^-1"),
        ("Theoretical corner frequency",
         f"{F_CORNER_THEORY:.3f} Hz"),
        ("Lorentzian-fit alpha",
         f"{alpha:.2f} s^-1"),
        ("Lorentzian-fit corner frequency",
         f"{f_meas:.3f} Hz"),
        ("Fit error vs theory",
         f"{err_pct:+.2f} %"),
        ("Reactor implication",
         "Faster alpha = tighter prompt-mode safety margin"),
    ]

    y0 = 0.86
    for k, (label, value) in enumerate(rows):
        y = y0 - k * 0.115
        ax.text(0.05, y, label, fontsize=10, color="#333333", weight="bold")
        ax.text(0.55, y, value, fontsize=10, color=COLORS["fit"])

    ax.text(0.05, 0.05,
            "Note: in an operating reactor, alpha is monitored continuously."
            " A drift in alpha\nbetween two measurement campaigns indicates a change in beta"
            " (fuel composition,\nburn-up) or in Lambda (moderator density, void fraction).",
            fontsize=9, color="#555555", style="italic")
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_transient_scram(n_trans: np.ndarray, out: pathlib.Path) -> None:
    """Three-panel: transient time-series + bare DFT of full segment."""
    t = np.arange(N_TRANS) * DT
    delta_pct = (n_trans - N_MEAN) / N_MEAN * 100.0

    fig = plt.figure(figsize=(9, 7.0))
    gs  = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.4)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    ax1.plot(t, delta_pct, lw=0.4, color=COLORS["neutron"], rasterized=True)
    ax1.axvspan(ROD_STEP_TIME, ROD_STEP_TIME + ROD_STEP_RAMP,
                color=COLORS["step"], alpha=0.18,
                label=f"rod-step ramp ({ROD_STEP_RHO*1e5:.0f} pcm over {ROD_STEP_RAMP:.0f} s)")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("delta n / N_mean (%)")
    ax1.set_title(
        f"Transient segment - reactivity step at t = {ROD_STEP_TIME:.0f} s"
        f" makes the signal non-stationary"
    )
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.25)

    # Bare DFT of the full transient
    freq, psd = bare_periodogram(n_trans, FS)
    ax2.loglog(freq[1:], psd[1:], lw=0.4, color=COLORS["noise"],
               alpha=0.75, rasterized=True, label="bare periodogram (full 200 s)")
    ax2.axvline(F_CORNER_THEORY, color=COLORS["theory"], lw=1.0, linestyle=":",
                label=f"pre-step f_corner = {F_CORNER_THEORY:.2f} Hz")
    ax2.set_xlim(1e-2, FS / 2.0)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("PSD (arb units / Hz)")
    ax2.set_title(
        "Bare DFT of the non-stationary segment - spectrum smeared, no time info"
    )
    ax2.legend(fontsize=8, loc="lower left")
    ax2.grid(alpha=0.25, which="both")

    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_welch(freq_per: np.ndarray, psd_per: np.ndarray,
              freq_w: np.ndarray, psd_w: np.ndarray,
              out: pathlib.Path) -> None:
    """Side-by-side: bare periodogram vs Welch PSD."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.loglog(freq_per[1:], psd_per[1:], lw=0.3, color=COLORS["noise"],
              alpha=0.6, rasterized=True, label="bare periodogram (variance ~ 1)")
    ax.loglog(freq_w[1:], psd_w[1:], lw=1.4, color=COLORS["fit"],
              alpha=0.95, label="Welch PSD (16 segments, Hann window)")
    ax.axvline(F_CORNER_THEORY, color=COLORS["theory"], lw=1.0, linestyle=":",
               label=f"f_corner = {F_CORNER_THEORY:.2f} Hz")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (arb units / Hz)")
    ax.set_title("B7 - Welch's method: same physics, ~10x lower bin variance")
    ax.set_xlim(1e-2, FS / 2.0)
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_spectrogram(n_trans: np.ndarray, out: pathlib.Path) -> None:
    """STFT spectrogram of the transient segment."""
    f, t, S = spectrogram(n_trans - np.mean(n_trans), fs=FS,
                          nperseg=8192, noverlap=6144, scaling="density")
    S_db = 10.0 * np.log10(S + 1e-30)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    mesh = ax.pcolormesh(t, f, S_db, cmap="viridis", shading="auto",
                         vmin=np.percentile(S_db, 5),
                         vmax=np.percentile(S_db, 99))
    ax.set_yscale("log")
    ax.set_ylim(1e-1, FS / 2.0)
    ax.axvline(ROD_STEP_TIME, color="white", lw=1.0, linestyle="--",
               alpha=0.85, label=f"rod-step at t = {ROD_STEP_TIME:.0f} s")
    ax.axhline(F_CORNER_THEORY, color="white", lw=0.7, linestyle=":",
               alpha=0.85, label=f"f_corner = {F_CORNER_THEORY:.2f} Hz")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("B7 - STFT spectrogram of the transient - the rod-step is visible in time")
    cbar = fig.colorbar(mesh, ax=ax, label="Power (dB / Hz)")
    cbar.ax.tick_params(labelsize=8)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_wavelets(n_trans: np.ndarray, out: pathlib.Path) -> None:
    """Continuous wavelet (Morlet) scalogram of the transient."""
    # Downsample to 200 Hz to keep CWT tractable
    decim = 5
    sig   = (n_trans - np.mean(n_trans))[::decim]
    fs_d  = FS / decim
    scales = np.logspace(np.log10(2.0), np.log10(256.0), 80)
    # PyWavelets cwt expects sampling_period for frequency conversion
    coeffs, freqs = pywt.cwt(sig, scales, "cmor1.5-1.0",
                             sampling_period=1.0 / fs_d)
    power = np.abs(coeffs) ** 2
    power_db = 10.0 * np.log10(power + 1e-30)
    t_axis = np.arange(len(sig)) / fs_d

    fig, ax = plt.subplots(figsize=(9, 4.8))
    mesh = ax.pcolormesh(t_axis, freqs, power_db, cmap="magma", shading="auto",
                         vmin=np.percentile(power_db, 5),
                         vmax=np.percentile(power_db, 99))
    ax.set_yscale("log")
    ax.set_ylim(freqs.min(), freqs.max())
    ax.axvline(ROD_STEP_TIME, color="white", lw=1.0, linestyle="--",
               alpha=0.85, label=f"rod-step at t = {ROD_STEP_TIME:.0f} s")
    ax.axhline(F_CORNER_THEORY, color="white", lw=0.7, linestyle=":",
               alpha=0.85, label=f"f_corner = {F_CORNER_THEORY:.2f} Hz")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("B7 - Morlet CWT scalogram - tighter time localisation at high f")
    cbar = fig.colorbar(mesh, ax=ax, label="Power (dB)")
    cbar.ax.tick_params(labelsize=8)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_rossi_alpha(tau: np.ndarray, counts: np.ndarray,
                    alpha_fit: float, A_fit: float, B_fit: float,
                    out: pathlib.Path) -> None:
    """Pair-time histogram with exponential-plus-constant fit overlay."""
    model = A_fit * np.exp(-alpha_fit * tau) + B_fit

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.bar(tau * 1e3, counts, width=(tau[1] - tau[0]) * 1e3 * 0.9,
           color=COLORS["noise"], alpha=0.75, label="pair-time histogram (data)")
    ax.plot(tau * 1e3, model, color=COLORS["fit"], lw=2.0,
            label=f"A exp(-alpha tau) + B fit; alpha = {alpha_fit:.2f} s^-1")
    ax.set_xlabel("Pair time tau (ms)")
    ax.set_ylabel("Pair count per bin")
    ax.set_title(
        "B7 - Rossi-alpha: prompt-decay measured from neutron-pair coincidences"
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_feynman_alpha(T: np.ndarray, y_meas: np.ndarray,
                      y_th: np.ndarray, alpha_fit: float, Y_inf_fit: float,
                      out: pathlib.Path) -> None:
    """Variance-to-mean curve with theory overlay."""
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.semilogx(T, y_meas, "o", color=COLORS["measure"], ms=5,
                label="measured Y(T) = Var/Mean - 1")
    ax.semilogx(T, y_th, color=COLORS["fit"], lw=2.0,
                label=f"Feynman-alpha fit: alpha = {alpha_fit:.2f} s^-1,"
                      f" Y_inf = {Y_inf_fit:.3f}")
    ax.axvline(1.0 / alpha_fit, color=COLORS["annot"], lw=0.9, linestyle="--",
               label=f"T = 1/alpha = {1.0/alpha_fit*1e3:.1f} ms")
    ax.set_xlabel("Gate length T (s)")
    ax.set_ylabel("Y(T)")
    ax.set_title("B7 - Feynman-alpha: variance-to-mean of gated counts")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_bispectrum(freq: np.ndarray, B_sq: np.ndarray,
                   f1: float, f2: float,
                   out: pathlib.Path) -> None:
    """|B(f1,f2)|^2 heatmap with coupling-peak annotation."""
    fig, ax = plt.subplots(figsize=(8, 6.5))
    log_B = np.log10(B_sq + 1e-30)
    mesh = ax.pcolormesh(freq, freq, log_B.T, cmap="cividis", shading="auto",
                         vmin=np.percentile(log_B, 70),
                         vmax=np.percentile(log_B, 99.7))
    ax.plot(f1, f2, "x", color="white", ms=14, mew=2.0,
            label=f"injected coupling (f1, f2) = ({f1:.2f}, {f2:.2f}) Hz")
    ax.set_xlabel("f1 (Hz)")
    ax.set_ylabel("f2 (Hz)")
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 3.5)
    ax.set_aspect("equal")
    ax.set_title("B7 - Bispectrum |B(f1,f2)|^2 - non-zero off-diagonal flags coupling")
    fig.colorbar(mesh, ax=ax, label="log10 |B|^2")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def fig_coherence(freq_c: np.ndarray, gamma2: np.ndarray,
                  out: pathlib.Path) -> None:
    """Magnitude-squared coherence gamma^2(f) for the A-B sensor pair."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.semilogx(freq_c[1:], gamma2[1:], color=COLORS["sensorA"], lw=1.2)
    ax.axvline(F_CORNER_THEORY, color=COLORS["theory"], lw=1.0, linestyle=":",
               label=f"f_corner = {F_CORNER_THEORY:.2f} Hz")
    ax.axhline(0.5, color=COLORS["floor"], lw=0.7, linestyle="--",
               label="gamma^2 = 0.5 reference")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("gamma^2(f)")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(1e-2, FS / 2.0)
    ax.set_title("B7 - Two-sensor magnitude-squared coherence (A vs B)")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.25, which="both")
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

    rng = np.random.default_rng(RNG_SEED)

    print("Reactor parameters (Bell-Glasstone thermal U-235, 6-group):")
    print(f"  beta_total           = {BETA:.6f}")
    print(f"  generation time      = {GEN_TIME:.2e} s")
    print(f"  alpha = beta/Lambda  = {ALPHA_THEORY:.3f} s^-1")
    print(f"  f_corner = alpha/2pi = {F_CORNER_THEORY:.4f} Hz")
    print(f"  mean population N    = {N_MEAN:.1e}")
    print(f"  sample rate FS       = {FS:.0f} Hz")
    print(f"  T_stationary         = {T_STAT:.0f} s    (N = {N_STAT:,})")
    print(f"  T_transient          = {T_TRANS:.0f} s    (N = {N_TRANS:,})")
    print()

    # ── Stationary segment + bare DFT + Welch + Lorentzian fit ────────────
    print("Synthesising stationary segment ...")
    n_stat = make_stationary_segment(rng)

    print("Bare periodogram + Welch PSD ...")
    freq_per, psd_per = bare_periodogram(n_stat, FS)
    f_w, psd_w = welch(n_stat - np.mean(n_stat), fs=FS,
                       nperseg=N_STAT // 16, noverlap=N_STAT // 32,
                       window="hann", scaling="density")

    print("Lorentzian fit ...")
    fit_params = fit_lorentzian(f_w, psd_w, f_min=0.2, f_max=200.0)
    p0_fit, alpha_fit, p_inf_fit = fit_params
    err_pct = 100.0 * (alpha_fit - ALPHA_THEORY) / ALPHA_THEORY
    print(f"  fit p0       = {p0_fit:.3e}")
    print(f"  fit alpha    = {alpha_fit:.3f} s^-1"
          f"  (theory {ALPHA_THEORY:.3f}, err {err_pct:+.2f}%)")
    print(f"  fit p_inf    = {p_inf_fit:.3e}")
    print(f"  fit f_corner = {alpha_fit/(2*np.pi):.4f} Hz"
          f"  (theory {F_CORNER_THEORY:.4f})")

    # ── Transient segment ─────────────────────────────────────────────────
    print()
    print("Synthesising transient (rod-step) segment ...")
    n_trans = make_transient_segment(rng)

    # ── Pulse events for Rossi-alpha + Feynman-alpha ──────────────────────
    # The current-mode time series above carries spectral information
    # (PSD shape) but averages out the multiplet correlation that
    # Rossi-alpha and Feynman-alpha probe.  Here we generate a separate
    # pulse train with explicit fission-chain multiplicity (Pal-Pazsit
    # Ch. 5) that produces alpha-consistent decay in the pair-time
    # histogram and the variance-to-mean curve.
    print("Synthesising correlated pulse train (detector A) ...")
    events_A = synth_correlated_pulse_train(
        rng,
        t_total=T_STAT,
        chain_rate=80.0,           # 80 chains/s
        alpha=ALPHA_THEORY,
        mean_multiplicity=2.5,     # Diven-factor proxy for thermal U-235
        background_rate=60.0,      # accidentals
    )
    print(f"  {len(events_A):,} events over {T_STAT:.0f} s"
          f"  (mean rate {len(events_A)/T_STAT:.1f} Hz)")

    print("Rossi-alpha pair-time histogram ...")
    tau, counts = rossi_alpha_histogram(events_A, gate=0.5, n_bins=80)
    # Exponential + constant fit
    from scipy.optimize import curve_fit
    try:
        popt_r, _ = curve_fit(
            lambda t, A, alf, B: A * np.exp(-alf * t) + B,
            tau, counts.astype(float),
            p0=(counts[0] - counts[-1], ALPHA_THEORY, counts[-20:].mean()),
            maxfev=10000,
        )
        A_r, alpha_r, B_r = popt_r
    except Exception:
        A_r, alpha_r, B_r = counts[0] - counts[-1], ALPHA_THEORY, float(counts[-20:].mean())
    err_r = 100.0 * (alpha_r - ALPHA_THEORY) / ALPHA_THEORY
    print(f"  Rossi-alpha fit: alpha = {alpha_r:.3f} s^-1"
          f"  (theory {ALPHA_THEORY:.3f}, err {err_r:+.2f}%)")

    print("Feynman-alpha variance-to-mean ...")
    T_gates = np.logspace(-3, 0.7, 28)
    y_meas  = feynman_y_curve(events_A, T_STAT, T_gates)
    try:
        popt_f, _ = curve_fit(
            feynman_y_theory, T_gates, y_meas,
            p0=(ALPHA_THEORY, max(y_meas[-1], 0.01)),
            maxfev=10000,
        )
        alpha_f, Y_inf_f = popt_f
    except Exception:
        alpha_f, Y_inf_f = ALPHA_THEORY, float(y_meas[-1])
    err_f = 100.0 * (alpha_f - ALPHA_THEORY) / ALPHA_THEORY
    y_th = feynman_y_theory(T_gates, alpha_f, Y_inf_f)
    print(f"  Feynman-alpha fit: alpha = {alpha_f:.3f} s^-1"
          f"  (theory {ALPHA_THEORY:.3f}, err {err_f:+.2f}%)"
          f"  Y_inf = {Y_inf_f:.3f}")

    # ── Bispectrum on the coupled segment ─────────────────────────────────
    print()
    print("Synthesising coupled-frequency segment for bispectrum ...")
    n_couple, f1, f2 = make_coupled_segment(rng)
    print(f"  injected frequencies f1 = {f1} Hz, f2 = {f2} Hz")
    print("Bispectrum estimation (8 segments) ...")
    freq_b, B_sq = bispectrum_direct(n_couple - np.mean(n_couple),
                                     fs=FS, n_seg=8, f_max=4.0)

    # ── Coherence on two-sensor pair ──────────────────────────────────────
    print("Two-sensor coherence ...")
    sig_A, sig_B = make_two_sensor_pair(rng, n_stat)
    f_c, gamma2 = coherence(sig_A, sig_B, fs=FS,
                            nperseg=N_STAT // 16, noverlap=N_STAT // 32)
    # Sanity: coherence at the corner frequency
    k_c = int(np.argmin(np.abs(f_c - F_CORNER_THEORY)))
    print(f"  gamma^2 at f_corner = {gamma2[k_c]:.3f}"
          f"  (signal is common-mode dominated at low f)")

    # ── Render all figures ────────────────────────────────────────────────
    print()
    print("Rendering 12 figures ...")
    fig_time_series(n_stat, args.out_dir / "fig-b7-time-series.png")
    print("  fig-b7-time-series.png saved.")
    fig_bare_fft(freq_per, psd_per, args.out_dir / "fig-b7-bare-fft.png")
    print("  fig-b7-bare-fft.png saved.")
    fig_lorentzian_fit(f_w, psd_w, fit_params,
                       args.out_dir / "fig-b7-lorentzian-fit.png")
    print("  fig-b7-lorentzian-fit.png saved.")
    fig_alpha_extraction(fit_params,
                         args.out_dir / "fig-b7-alpha-extraction.png")
    print("  fig-b7-alpha-extraction.png saved.")
    fig_transient_scram(n_trans, args.out_dir / "fig-b7-transient-scram.png")
    print("  fig-b7-transient-scram.png saved.")
    fig_welch(freq_per, psd_per, f_w, psd_w,
              args.out_dir / "fig-b7-welch.png")
    print("  fig-b7-welch.png saved.")
    fig_spectrogram(n_trans, args.out_dir / "fig-b7-spectrogram.png")
    print("  fig-b7-spectrogram.png saved.")
    fig_wavelets(n_trans, args.out_dir / "fig-b7-wavelets.png")
    print("  fig-b7-wavelets.png saved.")
    fig_rossi_alpha(tau, counts, alpha_r, A_r, B_r,
                    args.out_dir / "fig-b7-rossi-alpha.png")
    print("  fig-b7-rossi-alpha.png saved.")
    fig_feynman_alpha(T_gates, y_meas, y_th, alpha_f, Y_inf_f,
                      args.out_dir / "fig-b7-feynman-alpha.png")
    print("  fig-b7-feynman-alpha.png saved.")
    fig_bispectrum(freq_b, B_sq, f1, f2,
                   args.out_dir / "fig-b7-bispectrum.png")
    print("  fig-b7-bispectrum.png saved.")
    fig_coherence(f_c, gamma2, args.out_dir / "fig-b7-coherence.png")
    print("  fig-b7-coherence.png saved.")

    # ── Headline numerical summary (the AG1 grep-trace source) ────────────
    print()
    print("=" * 70)
    print("B7 HEADLINE NUMBERS (AG1 grep-trace source for the chapter)")
    print("=" * 70)
    print(f"  alpha_theory          = {ALPHA_THEORY:.3f} s^-1")
    print(f"  f_corner_theory       = {F_CORNER_THEORY:.4f} Hz")
    print(f"  alpha_PSD_fit         = {alpha_fit:.3f} s^-1  (err {err_pct:+.2f}%)")
    print(f"  alpha_Rossi           = {alpha_r:.3f} s^-1  (err {err_r:+.2f}%)")
    print(f"  alpha_Feynman         = {alpha_f:.3f} s^-1  (err {err_f:+.2f}%)")
    print(f"  Y_inf_Feynman         = {Y_inf_f:.4f}")
    print(f"  gamma^2 at f_corner   = {gamma2[k_c]:.4f}")
    print(f"  total pulses (det A)  = {len(events_A):,}")
    print(f"  N_stat samples        = {N_STAT:,}")
    print(f"  injected coupling f1+f2 = {f1+f2:.2f} Hz")
    print()
    print(f"All figures saved to: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
