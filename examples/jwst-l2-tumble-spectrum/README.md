# JWST-L2 tumble-spectrum — fourier × `experiments/jwst-l2-first-cut` integration

> **Audience.** Engineers / scientists who understand both the fourier-shad-tier
> arc (B1..B5) and the JWST-L2 rotational-dynamics first-cut, and want to see
> how the analytical primitive of one `lege-artis/*` project consumes the
> structured-numerical output of another.
>
> **Reading time.** ~5 minutes for the README, ~30 seconds to run the example.
>
> **License.** Apache-2.0 (code) + CC-BY-SA-4.0 (this README).

---

## What this example demonstrates

The canonical **structured-numerical-first → Fourier-transform-later** pattern,
realised across two projects:

1. `experiments/jwst-l2-first-cut/` (eventual `lege-artis/jwst-l2-coupled`)
   produces a per-snapshot NDJSON time series of two-body rigid-body
   coupled-rotational dynamics. **Pure numerical output**: 26 fields per
   body per snapshot + 9 system-level diagnostics; no plots, no
   visualisation.
2. `lege-artis/fourier` (this project) provides the canonical DFT
   analytical primitive. Python-tier oracle: `np.fft.rfft` per doctrine §3.1.
   Fortran + C++ canonical implementations sit in `fourier/backends/`,
   bit-identical to the Python oracle per the v0.2.0 PUBLIC empirical finding.

The example consumes one NDJSON file, extracts the body-frame ω_x time series
for body A, runs the DFT, and reports the dominant peak frequency along with
the theoretical free-precession Euler frequency. Agreement is checked at
FFT-bin resolution.

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point. Reads NDJSON, runs DFT, prints diagnostics. Text-only output. |
| `sample-trajectory.ndjson` | 100-snapshot excerpt from `experiments/jwst-l2-first-cut/outputs/case-C2-medium-x.ndjson`. ~166 KB. |
| `README.md` | This file. |

## Run it

```bash
cd fourier/examples/jwst-l2-tumble-spectrum
python3 main.py
```

Or against a custom trajectory:

```bash
python3 main.py /path/to/some-trajectory.ndjson
```

## Expected output

```
=== JWST-L2 tumble-spectrum cross-project example ===
  Input NDJSON: .../sample-trajectory.ndjson
  Snapshots:         100
  Snapshot dt:       2.0000 s
  Total duration:    198.00 s
  Sample rate fs:    0.5000 Hz
  FFT bin spacing:   5.0505e-03 Hz

--- spectrum analysis ---
  Peak frequency:    0.0050 Hz
  Peak period:       200.00 s
  Peak magnitude:    9.291e-01 (rad/s)

--- theoretical Euler precession (body A axisymmetric model) ---
  I_axial:           15384.3750 kg.m^2
  I_perp:            23322.6297 kg.m^2
  omega_z (initial): 0.080000 rad/s
  lambda_Euler:      -0.027229 rad/s
  Theoretical freq:  0.0043 Hz
  Theoretical period:230.75 s

--- agreement check ---
  Bin offset (peak vs theory): 0.13 FFT bins
  Result: peak matches theory within FFT bin resolution. OK.
```

The peak detected at 0.005 Hz / 200 s lies 0.13 FFT bins from the theoretical
Euler frequency of 0.0043 Hz / 230.75 s. In this 198 s observation window the
FFT bin spacing is 5.05 mHz, so periods between 200 s and 250 s collapse onto
the same bin. Longer observation windows (1000 s or more) tighten the
agreement — see the parametric sweep at `experiments/jwst-l2-first-cut/`.

## Why this example matters

It shows that the **same Fourier transform** Shad meets in B1 (oscilloscope
trace), B2 (audio), B3 (vibration), B4 (electronic), B5 (radar), and (queued)
B6 (radio astronomy) + B7 (nuclear reactor noise) also extracts the inertia
anisotropy ratio of a tumbling rigid body. Universal mathematics across
instruments and scales. The cross-project pattern means a new lege-artis
project that produces time-series data automatically inherits the fourier
analytical surface without re-implementing it.

Per doctrine §3.1 + §4.4, the Python-tier reference uses `np.fft.rfft` (the
canonical Python oracle). The hand-rolled Fortran and C++ DFT implementations
in `fourier/backends/` produce IEEE-754 bit-identical results across the
hand-rolled matrix, validated empirically at v0.2.0 PUBLIC release. The
example here exercises the Python oracle directly; consumers wanting to
validate against the canonical hand-rolled reference can pipe the same input
through the Fortran or C++ binaries in `backends/fortran/` or `backends/cpp/`
and compare.

## Companion plot prompts

This example is text-first by design. Plot prompts for an optional rendering
pass (deferred per the calculate-first-visualise-later discipline):

**Fig A — time series of omega_A_body[x].**
```python
import matplotlib.pyplot as plt
# t, omega_x are loaded as numpy arrays via load_omega_a_body_x_series()
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t, omega_x, lw=1.2)
ax.set_xlabel("Simulation time (s)")
ax.set_ylabel("omega_A_body[x] (rad/s)")
ax.set_title("Body A free-precession signal (raw NDJSON input to fourier)")
ax.grid(True, alpha=0.3)
```

**Fig B — DFT power spectrum with theoretical-frequency overlay.**
```python
fig, ax = plt.subplots(figsize=(10, 4))
ax.semilogy(freqs[1:], magnitudes[1:], lw=1.0, color="#d9923f")
ax.axvline(peak_freq, color="red", lw=0.7, linestyle="--",
           label=f"observed {peak_freq:.4f} Hz")
ax.axvline(f_theory, color="green", lw=0.7, linestyle=":",
           label=f"theoretical {f_theory:.4f} Hz")
ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("|DFT(omega_x)|")
ax.legend(); ax.grid(True, alpha=0.3, which="both")
```

Saved figures would live in `outputs/figures/` alongside the project pattern
established in `experiments/jwst-l2-first-cut/outputs/figures/`. Rendering is
optional; the text diagnostic is the contract.

## Cross-links

- `experiments/jwst-l2-first-cut/` — source of the input NDJSON; pragmatic
  first-cut of the eventual `lege-artis/jwst-l2-coupled` project.
- `experiments/jwst-l2-first-cut/SHAD-NARRATIVE.md` — shad-tier-voice narrative
  on the rigid-body tumble + inertia-tensor extraction. The story behind this
  example's algorithm.
- `_config/JWST-L2-COUPLED-DYNAMICS-PROJECT-v0.1.md` — strategic capture for
  the full lege-artis project that will eventually subsume this example.
- `_config/LEGE-ARTIS-LANGUAGE-DOCTRINE-v0.1.md` §3.1 (Python = NumPy oracle)
  + §4.4 (C1-C4 acceptance criteria including C2 cross-backend bit-identity).
- `fourier/docs/shad/01-oscilloscope.md` through `05-radar.md` — the existing
  shad-tier arc this example extends as a coupled-dynamics application.

## Status

Reproducibility: NumPy ≥ 1.20, Python ≥ 3.10. No other dependencies. The
sample NDJSON is committed; the example runs deterministically against it.

When the full `lege-artis/jwst-l2-coupled` project bootstraps, the example
moves under that project's `examples/` tree; the fourier-side wrapper here
gets retired or replaced by a one-liner that imports from the canonical
project. Pre-bootstrap, this `fourier/examples/` location is the natural
home because the example demonstrates fourier's analytical primitive being
consumed, not the rigid-body solver.
