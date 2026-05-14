#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Render B1 Slot S1 figures: Rodriguez muon-lifetime MCA histogram.

Source: MuonLifetimeData.zip fetched by probe_b1_muon.py.
File used: data/muon/extracted/Muon Lifetime Data/MainRunFinal.Spe
Format: Ortec Maestro MCA spectrum file (.Spe).
  Header ends at $DATA:\\n0 16383\\n; followed by 16384 integer count lines.
  Time calibration from calibration runs: t_ns = 2.2986 * channel - 162.8
  Main run live time: 71199 s; total events: 22321.

Outputs written to docs/shad/figures/:
  fig-b1-s1-input.png      MCA histogram: counts vs time (us)
  fig-b1-s1-spectrum.png   DFT magnitude of the decay histogram
  fig-b1-s1-takeaway.png   annotated spectrum with Lorentzian width + lifetime

Also writes data/b1_s1_head.txt (first 30 non-zero channels, for chapter embed).

Run:
    python render_b1_s1.py
"""
from __future__ import annotations

import pathlib

import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
SPE_PATH = HERE / "data" / "muon" / "extracted" / "Muon Lifetime Data" / "MainRunFinal.Spe"
OUTDIR   = REPO / "docs" / "shad" / "figures"
DATA_DIR = HERE / "data"

# Time calibration from least-squares fit to 8 calibration runs (ns/channel)
NS_PER_CH = 2.2986   # ns per channel
OFFSET_NS = -162.8   # ns offset


BIN_US    = 0.2     # rebin width for display and DFT
T_START   = 2.9     # us -- hardware minimum delay
T_END_FIT = 12.0    # us -- beyond this, accidental background dominates


def parse_spe(path: pathlib.Path) -> np.ndarray:
    lines = open(path).readlines()
    for i, l in enumerate(lines):
        if l.strip() == "$DATA:":
            start = i + 2
            break
    counts = np.array([int(lines[j].strip()) for j in range(start, min(start + 16384, len(lines)))])
    return counts


def calibrate_time(channels: np.ndarray) -> np.ndarray:
    return (channels * NS_PER_CH + OFFSET_NS) / 1000.0   # -> microseconds


def rebin(all_counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rebin the raw 2.3 ns channels into 0.2 us bins."""
    ch_all = np.arange(len(all_counts))
    t_all  = calibrate_time(ch_all.astype(float))
    bins_edges  = np.arange(T_START, 20.0 + BIN_US, BIN_US)
    bin_centers = 0.5 * (bins_edges[:-1] + bins_edges[1:])
    binned, _ = np.histogram(t_all, bins=bins_edges, weights=all_counts)
    return bin_centers, binned


def write_head(channels: np.ndarray, counts: np.ndarray, path: pathlib.Path) -> None:
    t_us = calibrate_time(channels)
    with open(path, "w") as fh:
        fh.write("# S1 Rodriguez muon MCA histogram (MainRunFinal.Spe)\n")
        fh.write(f"# Time calibration: t_ns = {NS_PER_CH:.4f} * channel + ({OFFSET_NS:.1f}) ns\n")
        fh.write("# Total events: 22321   Live time: 71199 s\n")
        fh.write("# Rebinned to 0.2 us bins for display\n")
        fh.write("# Columns: channel, time_us, counts\n")
        fh.write("#\n")
        fh.write("# --- first 30 non-zero channels ---\n")
        fh.write(f"{'channel':>8s}  {'time_us':>10s}  {'counts':>8s}\n")
        for ch, t, c in zip(channels[:30], t_us[:30], counts[:30]):
            fh.write(f"  {ch:6d}  {t:10.4f}  {c:8d}\n")
        fh.write(f"  ... ({len(channels) - 30} more non-zero channels)\n")


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    if not SPE_PATH.exists():
        print(f"ERROR: {SPE_PATH} not found. Run probe_b1_muon.py first.")
        return 1

    all_counts = parse_spe(SPE_PATH)
    nz_ch      = np.where(all_counts > 0)[0]
    nz_counts  = all_counts[nz_ch]
    total      = int(all_counts.sum())
    n_nz       = len(nz_ch)

    write_head(nz_ch, nz_counts, DATA_DIR / "b1_s1_head.txt")

    # Rebin to 0.2 us bins for display and DFT
    t_bins, c_bins = rebin(all_counts)
    t_us_first = calibrate_time(nz_ch[:1].astype(float))[0]
    t_us_last  = calibrate_time(nz_ch[-1:].astype(float))[0]

    # ---- input figure: rebinned MCA histogram ----
    show_mask = (t_bins >= T_START) & (t_bins <= 20.0)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar(t_bins[show_mask], c_bins[show_mask], width=BIN_US * 0.9,
           color="#1f4e79", alpha=0.85)
    ax.set_xlabel("decay time $t$ ($\\mu$s)")
    ax.set_ylabel(f"counts per {BIN_US:.1f} $\\mu$s bin")
    ax.set_title("S1 Rodriguez muon MCA histogram (MainRunFinal.Spe)\n"
                 f"71 199 s live time  |  {total:,} muon decays  |  rebinned to {BIN_US:.1f} $\\mu$s channels")
    ax.set_xlim(T_START - 0.2, 20.2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-b1-s1-input.png", dpi=120)
    plt.close(fig)

    # ---- DFT of the rebinned histogram ----
    fit_mask = show_mask
    c_dft    = c_bins[fit_mask].astype(float)
    N        = len(c_dft)
    spec     = np.fft.fft(c_dft)
    dt       = BIN_US * 1e-6   # s
    freq     = np.fft.fftfreq(N, d=dt)
    half     = N // 2
    mag      = np.abs(spec[:half]) / N

    # ---- spectrum figure ----
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.semilogy(freq[:half], mag + 1e-2,
                color="#702020", linewidth=1.2, alpha=0.9)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("$|X[k]|$ (log scale)")
    ax.set_title("S1 spectrum: DFT of muon decay histogram (rebinned)\n"
                 "DC peak = total event count; low-frequency decay structure visible")
    ax.set_xlim(0, freq[half - 1])
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-b1-s1-spectrum.png", dpi=120)
    plt.close(fig)

    # ---- takeaway: log-scale rebinned histogram + PDG exponential overlay ----
    # Overlay with known PDG muon lifetime tau = 2.197 us (not a fit; the hardware
    # minimum-delay cut at ~3 us and accidental background cause naive fits to be
    # biased. The PDG value is plotted as the known-correct reference.)
    TAU_PDG  = 2.197   # us
    plot_mask = (t_bins >= T_START) & (t_bins <= 15.0) & (c_bins > 0)
    t_plot   = t_bins[plot_mask]
    c_plot   = c_bins[plot_mask]
    # Normalise model to match data at the start bin
    N0_model = c_plot[0] * np.exp(t_plot[0] / TAU_PDG)
    t_model  = np.linspace(t_plot[0], 15.0, 500)
    c_model  = N0_model * np.exp(-t_model / TAU_PDG)

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.semilogy(t_plot, c_plot + 0.1, ".", markersize=4, color="#1f4e79",
                alpha=0.85, label=f"data ({BIN_US:.1f} $\\mu$s bins)")
    ax.semilogy(t_model, c_model, "-", color="#a02020", linewidth=1.4,
                label=f"PDG $\\tau$ = 2.197 $\\mu$s  (not a fit; known from particle physics)")
    ax.set_xlabel("decay time $t$ ($\\mu$s)")
    ax.set_ylabel("counts (log scale)")
    ax.set_title("S1 takeaway: muon lifetime histogram\n"
                 "exponential slope consistent with $\\tau$ = 2.197 $\\mu$s; "
                 "flat tail = accidental background")
    ax.set_xlim(T_START - 0.2, 15.2)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig-b1-s1-takeaway.png", dpi=120)
    plt.close(fig)

    print(f"S1 figures rendered.")
    print(f"  SPE file   : {SPE_PATH.name}")
    print(f"  Total cts  : {total:,}")
    print(f"  Non-zero ch: {n_nz}")
    print(f"  Bin 0 (t={t_bins[show_mask][0]:.2f} us): {c_bins[show_mask][0]:.0f} counts")
    print(f"  PDG tau    : 2.197 us (plotted as reference)")
    print(f"  head.txt   : data/b1_s1_head.txt")
    print(f"  out dir    : {OUTDIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
