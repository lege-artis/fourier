# lege-artis / fourier

Canonical reference implementation of FFT, DFT, and Numerical Partial Sum of Fourier Series.

## Status

Pre-v0.1.0 — bootstrap phase. Repository is currently **private** during development. First public release at `v0.1.0` will be the Fortran reference implementation with golden vectors and dual-tier (canonical math + engineer-friendly) documentation.

## Plan

* **v0.1.0** — Fortran reference + golden vectors + dual-tier docs for DFT
* **v0.2.0** — C++ performance + Rust experimental + Pascal full-scale (mirrors `lege-artis/kh-sim` four-language layout)
* **v0.5.0+** — Stretch goals: GPU bridge, REST microservice form

## License

* Code: Apache License 2.0 — see `LICENSE`
* Documentation: CC-BY-SA-4.0 — see `LICENSE-DOCS`
* Names: `MIM2000` / `Improwave` / `Petr Yamyang` not licensed for derivative use — see `TRADEMARK.md`

## Central reference

Numerical Recipes (Press, Teukolsky, Vetterling, Flannery) — 2007 3rd ed. for general FFT recipes; 1986 Pascal edition is direct historical anchor for the Pascal track.

## See also

* Master spec: `_specs/WORKING-SPEC-v0.2-EN.md`
* Sibling repo: [lege-artis/kh-sim](https://github.com/lege-artis/kh-sim) — Kelvin-Helmholtz instability solver; same multi-backend pattern this repo follows.
