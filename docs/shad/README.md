# Just Shad's Guide to Fourier's Galaxy

Engineer-narrated, hands-on documentation tier for `lege-artis/fourier`.
For readers who want to put their own data through a DFT and read the
result, without first learning calculus.

## Chapters

| # | Title | Status | Adds |
|---|-------|--------|------|
| 00 | [Prologue](00-prologue.md) | shipped v0.2.x | Who this is for, how to read |
| 01 | [B1 — Oscilloscope](01-oscilloscope.md) | shipped v0.2.x | DFT as time → frequency machine |
| 02 | [B2 — Audio](02-audio.md) | shipped v0.2.x | Multiple peaks + leakage + windowing |
| 03 | [B3 — Vibration](03-vibration.md) | shipped v0.2.x | Harmonics + fault signatures + diagnostic reading |
| 04 | B4 — Geophysical | queued v0.2.x | Long records + noise floors + periodogram averaging |
| 05 | B5 — Radio interferometry / LIGO | queued v0.2.x | FFT in modern observational physics |

## Example scripts

The figures in each chapter are rendered by the corresponding script in
[`../../examples/shad/`](../../examples/shad/):

- [`b1-scope/main.py`](../../examples/shad/b1-scope/main.py) → `figures/fig-b1-*.png`
- [`b2-audio/main.py`](../../examples/shad/b2-audio/main.py) → `figures/fig-b2-*.png`
- [`b3-vibration/main.py`](../../examples/shad/b3-vibration/main.py) → `figures/fig-b3-*.png`

Each script runs on its own (no internet required) with `python main.py`.
Requires Python 3.10+, NumPy, Matplotlib. A real-data extension sketch
sits at the bottom of each script for readers who want to repeat the
workflow on actual scope captures, .wav files, or NASA bearing data.

## Iconography

The Shad-tier voice is signalled by a placeholder dragon avatar (Miyazaki
register; smoking weed, drinking tea, looking mildly amused). The custom
asset is queued; for v0.2.x the placeholder marker stays in
[`00-prologue.md`](00-prologue.md).

## License

This tier is **CC-BY-SA-4.0** (consistent with the rest of `docs/`).
The example scripts in `examples/shad/` are **Apache-2.0** (consistent
with the rest of `examples/` and `backends/`).

## Cross-references

- Canonical-tier (math-first, rigorous): [`../canonical/en/`](../canonical/en/)
- Engineer-tier (worked-examples, neutral tone): [`../engineer/en/`](../engineer/en/)
- Scope-doc that locks the planned five-band progression: [`../../_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`](../../_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md)
