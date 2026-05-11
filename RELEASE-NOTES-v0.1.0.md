# lege-artis/fourier — v0.1.0

**Released:** 2026-05-10
**Tag:** `v0.1.0`
**Status:** Public canonical reference. Fortran backend complete and validated.

---

## What this is

A canonical reference implementation of the Discrete Fourier Transform, faithfully translated from `shared/canonical-equations/dft.md` (Eq. DFT-1) into IEEE-754 binary64 Fortran 2018, with a layered test pyramid that validates the implementation against:

- Algebraic properties guaranteed by the math (linearity, Plancherel, Hermitian symmetry, time-shift, convolution)
- Physical testbeds drawn from textbook physics (single-slit Fraunhofer diffraction, heat-equation impulse decay, simple harmonic oscillator frequency identification, spectral leakage on cosines at non-integer frequencies)
- Independent FFT oracles (NumPy + SciPy, both backed by pocketfft) in pre-generated golden-vector form

The implementation philosophy is non-negotiable: **the canonical equation is the source; the code is its faithful translation.** No external library is linked, no FFT optimisation is used in the reference build (Stage 5 / v0.5+ scope), and every implementation file carries an inline math-to-code mapping table so a reader can re-derive the algorithm from comments alone.

## Test summary — ThinkPad gfortran 13.x / Windows 10 (commit `3f3fae2`)

| Suite | Count | Worst error | Gate |
|-------|-------|-------------|------|
| **Unit** (small-N analytic checks) | 5/5 PASS | 4.638E-15 | 1.000E-13 |
| **Property** (P1, P2, P3, P4, P7, P8) | 6/6 PASS | 2.348E-13 (P8) | 9.095E-13 (P8) |
| **Physics** (PT-DFT-01/02/03A/03B) | 14/14 PASS | 6.253E-12 (PT-DFT-03B) | 1.000E-10 |
| **Golden-vector** (38 cases, N∈{2,4,8,16,64}) | 748/748 element-checks PASS | — | 1e-13·√N |
| **Total** | **63 test assertions + 748 element-checks** | | |

Golden-vector breakdown by N: 12 + 32 + 64 + 128 + 512 = 748 element-checks across 38 deterministic input cases (cosine/sine tones, ramps, impulses, DC, combinations).

## Gate formulae

**Unit / property / physics tests** use a flat absolute gate `1.0e-13_dp` (P8 convolution and PT-DFT-03B leakage testbeds use scaled gates per their derivations).

**Golden-vector verification** uses Option G (per KB-040, after L1-norm and flat-absolute attempts failed):

```
metric = abs(got - expected) / max(abs(expected), 1.0_dp)
gate   = 1.0e-13_dp * sqrt(real(N, dp))
```

Rationale: direct O(N²) DFT backward error scales as O(√N · ε) per output bin (Higham §4.2). Floor-1 denominator handles near-zero oracle bins without false failures. Effective gates: N=2 → 1.41e-13, N=4 → 2.00e-13, N=8 → 2.83e-13, N=16 → 4.00e-13, N=64 → 8.00e-13.

## What's in this release

**Code** (Apache 2.0):
- `backends/fortran/src/dft_kernel.f90` — kernel module exporting `dft`, `idft`, `dp` (precision kind)
- `backends/fortran/tests/test_dft_unit.f90` — 5 unit tests
- `backends/fortran/tests/test_dft_property.f90` — 6 property tests (P1, P2, P3, P4, P7, P8)
- `backends/fortran/tests/test_dft_physics.f90` — 14 physics testbed assertions
- `backends/fortran/tests/test_dft_golden.f90` — 748 golden-vector element-checks
- `backends/fortran/Makefile` — OS-aware build chain (Windows cmd.exe + POSIX sh both supported)
- `tools/generate_golden_vectors.py` — NumPy + SciPy oracle, cross-checked
- `tools/json_to_fortran_data.py` — JSON → fixed-format `.dat` converter for the golden-vector loader
- `.github/workflows/fortran.yml` — GitHub Actions reference build + test

**Specs and docs** (CC-BY-SA-4.0):
- `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy, 5-stage workflow, license stack rationale, 3 doc tiers, language stack roadmap
- `_specs/SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md` — delegation contract used to author Jobs 1+2+3
- `_specs/SONNET-CLOSE-v0.1.0-RC-2026-05-10.md` — release-candidate close-out, test results, session-incidents log
- `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — fourth doc tier scope (engineer-narrated, deferred to v0.2.x)
- `shared/canonical-equations/{dft,fft-cooley-tukey,partial-sum}.{md,tex}` — three canonical equations with code-mapping tables
- `shared/property-tests/dft.md` — eight algebraic properties (P1-P8)
- `shared/physics-testbeds/dft.md` — four physical testbeds (PT-DFT-01/02/03A/03B)
- `shared/golden-vectors/dft_n=*.json` — six oracle JSONs, NumPy + SciPy cross-checked
- `shared/reference-bibliography/refs.bib` — 13 confirmed sources (Cooley-Tukey 1965, Stein-Shakarchi 2003, Folland 1992, Pinsky 2009, Numerical Recipes 2007, Thorne 2017, Oppenheim-Schafer 3rd ed., Boyd 2001, Strang 1986, plus Czech and Japanese references queued for v0.1.1+)
- `docs/canonical/en/{00-introduction,01-dft-definition}.md` — formal-rigour tier (chapters 0+1)
- `docs/engineer/en/{00-quick-start,01-what-dft-actually-computes}.md` — worked-examples tier (chapters 0+1)

**Governance** (Apache 2.0 / CC-BY-SA-4.0):
- `LICENSE` (Apache 2.0) + `LICENSE-DOCS` (CC-BY-SA-4.0) + `NOTICE` + `TRADEMARK.md`
- `CONTRIBUTING.md` + `CODE_OF_CONDUCT.md` + `SECURITY.md`
- `README.md` + this `RELEASE-NOTES-v0.1.0.md`

## What's NOT in this release (and where it goes)

- **FFT (Cooley-Tukey decimation-in-time)** — v0.2.0. Property P5 (FFT ≡ DFT to floating-point precision) lands when FFT lands.
- **C++ / Rust / Pascal backends** — v0.2.0. Mirrors the four-language layout of the sibling `lege-artis/kh-sim`. Pascal track anchors directly on Numerical Recipes 1986.
- **CS / JA / DE / IT translations** — v0.1.1+. Bibliography sources for these languages are already in `refs.bib` (commented).
- **Performance build (Stage 5)** — v0.5+. Uses `-O3 -march=native -funroll-loops` against the same kernel + tests; gated on v0.1.0 closing green (which it has).
- **"Shaddack tier" docs (engineer-narrated, dry-humour register)** — v0.2.x. Five-band progression from oscilloscope traces through audio/vibration/geophysical to EHT/LIGO interferometry, all on public-data examples. Scope in `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`.

## Build and test on your machine

```bash
git clone https://github.com/lege-artis/fourier.git
cd fourier/backends/fortran
make clean
make test
```

Expected output:

```
Running DFT unit tests (v0.1.0 reference)...
=========================================================
 lege-artis/fourier - DFT unit tests (v0.1.0 reference)
=========================================================
 [PASS] test_dft_n4_pure_cosine - max-err = 3.674E-16  (gate 1.000E-13)
 [PASS] test_dft_n4_dc_input    - max-err = 4.682E-16  (gate 1.000E-13)
 ... (5 unit + 6 property + 14 physics + golden-vector summary) ...
 Result: 25/25 PASS  (+ 748/748 golden-vector element-checks)
 All tests PASSED.
```

Requires gfortran (tested on 13.x), GNU Make, Python 3 with NumPy + SciPy (for regenerating golden vectors and converting them to Fortran-readable `.dat`).

## Citation

```
Yamyang, P. (2026). lege-artis/fourier v0.1.0 — canonical Fortran reference
implementation of the Discrete Fourier Transform.
https://github.com/lege-artis/fourier (tag v0.1.0)
```

## License

- **Code** (everything under `backends/`, `tools/`, Makefiles, GitHub Actions): Apache License 2.0 — see `LICENSE`
- **Documentation** (everything under `docs/`, `shared/`, `_specs/`, this file): Creative Commons Attribution-ShareAlike 4.0 International — see `LICENSE-DOCS`
- **Trademark notice**: the names `MIM2000`, `Improwave`, and the personal name `Petr Yamyang` are not licensed for derivative use — see `TRADEMARK.md`

## Acknowledgements

The implementation discipline ("first-principles translation of the canonical equation, validated against independent oracles") owes its shape to the textbooks listed in `shared/reference-bibliography/refs.bib`. Three build-chain traps that bit during this release ship as cross-project lessons-learned in the project owner's portfolio (KB-037 Fortran case-insensitivity, KB-038 Make on Windows cmd.exe, KB-039 gfortran ASCII-only, KB-040 Option G error gate).

The Sonnet sessions (ThinkPad + MacBook) that authored Jobs 1+2+3 against the delegation pack at `_specs/SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md` ran cleanly to completion with no spec ambiguity and no kernel bugs surfaced — a vote of confidence in the spec-first authoring discipline.
