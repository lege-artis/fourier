#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
jwst-l2-tumble-spectrum/main.py — cross-project integration example.

Consumes a JWST-L2 first-cut NDJSON trajectory file (produced by the
sibling `experiments/jwst-l2-first-cut/` package) and applies fourier's
canonical DFT analysis to extract the rotational free-precession period
from the body-frame angular-velocity time series.

This is the canonical demonstration of the structured-numerical-first ->
Fourier-transform-later methodology across two `lege-artis/*` projects:
  1. `lege-artis/jwst-l2-coupled` (eventual) / `experiments/jwst-l2-first-cut`
     (current prototype) produces the time series via rigid-body dynamics
     integration. Pure numerical output: per-snapshot state with the
     body-frame angular velocity component as one of 26 numerical fields.
  2. `lege-artis/fourier` (this project) provides the DFT analytical
     primitive. The Python oracle here uses np.fft.rfft, which IS the
     canonical Python-tier reference per doctrine §3.1 (Python = NumPy
     oracle; Fortran + C++ are the canonical hand-rolled implementations
     for cross-language bit-identity validation per doctrine §4.4 C2).

The pedagogical thread: the same algorithm that reads oscillator frequencies
from a function generator (B1), harmonic structure from audio (B2), bearing
faults from accelerometer traces (B3), and Doppler shifts from radar returns
(B5) also reads inertia-tensor ratios from rigid-body tumble. Universal
mathematics applied across instruments + scales.

Usage:
  python3 main.py [path-to-ndjson-file]

If no path is given, defaults to the bundled sample trajectory at
`./sample-trajectory.ndjson`.

Output:
  Text-only diagnostic to stdout. No figures rendered by this example —
  see `tools/plot_spectrum.py` for an optional rendering pass that consumes
  the same NDJSON file.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Iterator

import numpy as np


DEFAULT_NDJSON = pathlib.Path(__file__).parent / "sample-trajectory.ndjson"


def load_omega_a_body_x_series(ndjson_path: pathlib.Path
                                 ) -> tuple[np.ndarray, np.ndarray]:
    """Read an NDJSON file and extract (t, omega_A_body_x).

    Robust to either of the two known NDJSON record schemas:
      - first-example schema: A.omega_body[0], A.omega_body[1], A.omega_body[2]
      - sweep schema (testcases.py): same keys; identical structure for the
        fields we need."""
    t_list: list[float] = []
    omega_x_list: list[float] = []
    with ndjson_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            snap = json.loads(line)
            t_list.append(snap["t"])
            omega_x_list.append(snap["A"]["omega_body"][0])
    return np.array(t_list), np.array(omega_x_list)


def extract_principal_moments(ndjson_path: pathlib.Path
                                ) -> np.ndarray | None:
    """Read first snapshot, return body A's principal moments if present.
    Returns None if the schema does not include the field."""
    with ndjson_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            snap = json.loads(line)
            pm = snap.get("A", {}).get("principal_moments")
            if pm is not None:
                return np.array(pm)
            return None
    return None


def main(ndjson_path: pathlib.Path) -> int:
    if not ndjson_path.exists():
        print(f"ERROR: NDJSON file not found: {ndjson_path}", file=sys.stderr)
        return 2

    print(f"=== JWST-L2 tumble-spectrum cross-project example ===")
    print(f"  Input NDJSON: {ndjson_path}")

    t, omega_x = load_omega_a_body_x_series(ndjson_path)
    n = len(t)
    if n < 8:
        print(f"ERROR: only {n} snapshots; need >= 8 for meaningful FFT.")
        return 2

    dt = float(t[1] - t[0])
    duration = float(t[-1] - t[0])
    fs = 1.0 / dt
    print(f"  Snapshots:         {n}")
    print(f"  Snapshot dt:       {dt:.4f} s")
    print(f"  Total duration:    {duration:.2f} s")
    print(f"  Sample rate fs:    {fs:.4f} Hz")
    print(f"  FFT bin spacing:   {1.0/duration:.4e} Hz")

    # --- the Fourier transform (Python oracle per doctrine §3.1) ---
    signal = omega_x - omega_x.mean()    # remove DC
    # Use rfft (real-input optimised) — produces n//2 + 1 complex coefficients
    Xk = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=dt)
    magnitudes = np.abs(Xk)

    # peak detection (excluding DC bin)
    if len(magnitudes) < 2:
        print(f"ERROR: spectrum too short for peak detection.")
        return 2
    peak_idx = 1 + int(np.argmax(magnitudes[1:]))
    peak_freq = float(freqs[peak_idx])
    peak_mag = float(magnitudes[peak_idx])
    peak_period = 1.0 / peak_freq if peak_freq > 0 else 0.0

    print(f"\n--- spectrum analysis ---")
    print(f"  Peak frequency:    {peak_freq:.4f} Hz")
    print(f"  Peak period:       {peak_period:.2f} s")
    print(f"  Peak magnitude:    {peak_mag:.3e} (rad/s)")

    # --- theoretical Euler precession period ---
    # For body A with axisymmetric inertia (I_xx = I_yy != I_zz),
    # free-precession frequency in body frame:
    #   lambda = (I_axial - I_perp) / I_perp * omega_z
    # where I_axial is the symmetry-axis moment and I_perp is the diametral.
    pmA = extract_principal_moments(ndjson_path)
    omega_z_initial = float(omega_x[0])  # NOT exactly right; we should get omega_z(t=0)
    # actually, re-load first snapshot to get omega_z properly
    with ndjson_path.open() as fh:
        first_snap = json.loads(fh.readline().strip())
        omega_z_initial = float(first_snap["A"]["omega_body"][2])

    if pmA is not None and len(pmA) >= 3:
        I_axial = float(pmA[0])    # smallest moment (oblate JWST-like A)
        I_perp = float(pmA[-1])    # largest moment
        if I_perp != 0.0:
            lambda_theory = (I_axial - I_perp) / I_perp * omega_z_initial
            period_theory = 2.0 * np.pi / abs(lambda_theory) if lambda_theory != 0 else 0.0
            f_theory = abs(lambda_theory) / (2.0 * np.pi)

            print(f"\n--- theoretical Euler precession (body A axisymmetric model) ---")
            print(f"  I_axial:           {I_axial:.4f} kg.m^2")
            print(f"  I_perp:            {I_perp:.4f} kg.m^2")
            print(f"  omega_z (initial): {omega_z_initial:.6f} rad/s")
            print(f"  lambda_Euler:      {lambda_theory:.6f} rad/s")
            print(f"  Theoretical freq:  {f_theory:.4f} Hz")
            print(f"  Theoretical period:{period_theory:.2f} s")

            # bin-resolution-aware comparison
            df = 1.0 / duration
            bin_offset = abs(peak_freq - f_theory) / df
            print(f"\n--- agreement check ---")
            print(f"  Bin offset (peak vs theory): {bin_offset:.2f} FFT bins")
            if bin_offset < 1.5:
                print(f"  Result: peak matches theory within FFT bin resolution. OK.")
            else:
                print(f"  Result: peak is {bin_offset:.1f} bins away from theory.")
                print(f"          Either longer observation window needed for finer")
                print(f"          frequency resolution, or coupling-induced drift")
                print(f"          has shifted the dominant mode away from pure free")
                print(f"          precession.")
        else:
            print(f"\n  (Cannot compute theoretical Euler frequency: I_perp = 0)")
    else:
        print(f"\n  (Principal moments not recorded in NDJSON; skipping theoretical comparison)")

    print(f"\n--- cross-project methodology note ---")
    print(f"  This example consumes structured-numerical output from one project")
    print(f"  (`experiments/jwst-l2-first-cut/`) and applies the canonical Fourier")
    print(f"  transform from another (`lege-artis/fourier`) to extract a physical")
    print(f"  quantity (the inertia-tensor anisotropy ratio, encoded in the Euler")
    print(f"  frequency). The pattern generalises: any time series produced by a")
    print(f"  `lege-artis/*` integrator can be analysed with the fourier primitive")
    print(f"  without re-implementing the spectral analysis stage.")
    print(f"\n  Per doctrine §3.1 + §4.4: the Python-tier Fourier primitive is")
    print(f"  np.fft.rfft, the canonical Python oracle. The hand-rolled Fortran +")
    print(f"  C++ DFT references in fourier/backends/ produce bit-identical results")
    print(f"  per the v0.2.0 PUBLIC empirical finding (Press 2007 NR 3rd ed §12.1).")
    print(f"\n--- done ---")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ndjson_path",
        type=pathlib.Path,
        nargs="?",
        default=DEFAULT_NDJSON,
        help="Path to JWST-L2 NDJSON trajectory file "
             "(default: ./sample-trajectory.ndjson)",
    )
    args = parser.parse_args()
    sys.exit(main(args.ndjson_path))
