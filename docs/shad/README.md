# Just Shad's Guide to Fourier's Galaxy

Engineer-narrated, hands-on documentation tier for `lege-artis/fourier`.
For readers who want to put their own data through a DFT and read the
result, without first learning calculus.

## Chapters

| # | Title | Status | Adds |
|---|-------|--------|------|
| 00 | [Prologue](00-prologue.md) | shipped v0.3.0 | Who this is for, how to read |
| 01 | [B1 — Oscilloscope](01-oscilloscope.md) | shipped v0.3.0 | DFT as time → frequency machine — 4 real fixtures (muon MCA, square wave, triangle wave, RLC damped) |
| 02 | [B2 — Audio](02-audio.md) | shipped v0.3.0 | Multiple peaks + leakage + windowing |
| 03 | [B3 — Vibration](03-vibration.md) | shipped v0.3.0 | Harmonics + fault signatures + diagnostic reading |
| 04 | [B4 — Electronic systems](04-electronic.md) | shipped v0.3.0 | AC mains harmonics + active filter + heterodyne mixer |
| 05 | [B5 — Radar](05-radar.md) | shipped v0.3.0 | Doppler + range-Doppler + pulse compression |
| 05.5 | [B5.5 — JWST-L2](05-jwst-l2.md) | shipped v0.3.0 | Rigid-body Euler precession → FFT cross-check; structured numerical dynamics as Fourier diagnostic |
| 06 | [B6 — Radioastronomy](06-radioastronomy.md) | shipped v0.3.0 | Faint signals + sqrt(T) integration law + pulsar timing + aperture synthesis (EHT) |
| 07 | [B7 — Nuclear-reactor capstone](07-nuclear-reactor.md) | shipped v0.3.0 | Beyond-DFT toolkit: Welch PSD + Lorentzian fit + STFT + CWT + Rossi-alpha + Feynman-alpha + bispectrum + coherence |

## Example scripts

The figures in each chapter are rendered by the corresponding script in
[`../../examples/shad/`](../../examples/shad/):

- [`b1-scope/render_b1_s{1..4}.py`](../../examples/shad/b1-scope/) → `figures/fig-b1-s{1..4}-{input,spectrum,takeaway}.png` (probe scripts fetch raw data first)
- [`b2-audio/main.py`](../../examples/shad/b2-audio/main.py) → `figures/fig-b2-*.png`
- [`b3-vibration/main.py`](../../examples/shad/b3-vibration/main.py) → `figures/fig-b3-*.png`
- [`b4-electronic/main.py`](../../examples/shad/b4-electronic/main.py) → `figures/fig-b4-*.png`
- [`b5-radar/main.py`](../../examples/shad/b5-radar/main.py) → `figures/fig-b5-*.png`
- [`b6-radioastronomy/main.py`](../../examples/shad/b6-radioastronomy/main.py) → `figures/fig-b6-*.png`
- [`b7-nuclear-reactor/main.py`](../../examples/shad/b7-nuclear-reactor/main.py) → `figures/fig-b7-*.png`
- [`jwst-l2-tumble-spectrum/main.py`](../../examples/jwst-l2-tumble-spectrum/main.py) → FFT cross-check output (B5.5 text-only chapter)

Each script runs on its own (no internet required) with `python main.py`.
Requires Python 3.10+, NumPy, Matplotlib. A real-data extension sketch
sits at the bottom of each script for readers who want to repeat the
workflow on actual scope captures, .wav files, or NASA bearing data.

## Iconography

The Shad-tier voice is signalled by the Shaddack-Fourier-Galaxy dragon
avatar (Row 30 canonical asset, vermilion hanko-stamp register). The
cover asset lives at `figures/dragon-cover.png`; the chapter icon at
`figures/dragon-icon.png`.

## License

This tier is **CC-BY-SA-4.0** (consistent with the rest of `docs/`).
The example scripts in `examples/shad/` are **Apache-2.0** (consistent
with the rest of `examples/` and `backends/`).

## Cross-references

- Canonical-tier (math-first, rigorous): [`../canonical/en/`](../canonical/en/)
- Engineer-tier (worked-examples, neutral tone): [`../engineer/en/`](../engineer/en/)
- Scope-doc that locks the planned five-band progression: [`../../_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`](../../_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md)
