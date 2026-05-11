# lege-artis/fourier — v0.2.0

**Released:** 2026-05-10
**Tag:** `v0.2.0`
**Status:** C++ reference port complete and validated against the v0.1.0 Fortran baseline. Rust + Pascal ports queued for v0.2.x point releases.

---

## What's new in v0.2.0

A second canonical reference language: **C++17**. The C++ port translates `shared/canonical-equations/dft.md` Eq. DFT-1 directly into idiomatic C++, mirrors the Fortran reference's test pyramid (5 unit + 6 property + 14 physics + 748 golden-vector element-checks), and produces **bit-identical worst-error numbers to the Fortran reference** when run on identical inputs.

This is not a Fortran-to-C++ translation — it's an independent equation-to-code rendering in a second language. The fact that both backends produce numerically identical results validates two things:

1. The kernels are faithful to the canonical equation in both languages
2. IEEE-754 double-precision arithmetic gives identical accumulation order across compilers when no optimisation reorders operations (`-O0 -ffp-contract=off`)

## Test summary — ThinkPad gfortran 13.x + g++ 11.4 (sandbox)

| Suite | Fortran v0.1.0 | C++ v0.2.0 | Match |
|-------|---------------|------------|-------|
| Unit (5 tests) | 4.638E-15 worst | 4.638E-15 worst | ✓ identical |
| Property (6 tests) | P8: 2.348E-13 worst | P8: 2.348E-13 worst | ✓ identical |
| Physics (14 assertions) | PT-DFT-03B: 6.253E-12 worst | PT-DFT-03B: 6.253E-12 worst | ✓ identical |
| Golden-vector (748 element-checks) | 748/748 PASS @ Option G | 748/748 PASS @ Option G | ✓ same gate, same data |
| **Total per backend** | **63 assertions + 748 element-checks** | **63 assertions + 748 element-checks** | |

Cross-language baseline match: **bit-identical**. Both backends compute the same DFT values to the last ULP on identical inputs because both use the same direct O(N²) algorithm with the same accumulation order in the same IEEE-754 binary64 precision.

## What's in this release

**Code (Apache 2.0):**

New for v0.2.0:
- `backends/cpp/include/lege_artis_fourier/dft_kernel.hpp` — public API
- `backends/cpp/src/dft_kernel.cpp` — kernel implementation (C++17)
- `backends/cpp/tests/test_harness.hpp` — hand-rolled assertion helpers (no external test framework)
- `backends/cpp/tests/test_dft_unit.cpp` — 5 unit tests
- `backends/cpp/tests/test_dft_property.cpp` — 6 property tests (P1+P2+P3+P4+P7+P8)
- `backends/cpp/tests/test_dft_physics.cpp` — 14 physics testbed assertions (PT-DFT-01/02/03A/03B)
- `backends/cpp/tests/test_dft_golden.cpp` — 748 golden-vector element-checks (Option G gate)
- `backends/cpp/Makefile` — OS-aware build chain (Windows cmd.exe + POSIX sh both supported)
- `tools/json_to_fortran_data.py` — extended to write to both backends' `build/golden/` dirs

Carried from v0.1.0:
- `backends/fortran/` — Fortran reference (unchanged; still passes all v0.1.0 tests)
- `shared/canonical-equations/`, `shared/property-tests/`, `shared/physics-testbeds/`, `shared/golden-vectors/`, `shared/reference-bibliography/` — unchanged
- `docs/canonical/en/`, `docs/engineer/en/` — unchanged (chapters 0+1)
- License stack (LICENSE, LICENSE-DOCS, NOTICE, TRADEMARK.md) — unchanged

**Specs and process docs (CC-BY-SA-4.0):**
- `_specs/SONNET-HANDOFF-v0.2.0-CPP-PORT.md` — the delegation contract that drove the C++ port (Sonnet-targeted, Opus-authored)
- `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — updated with Shad rename + B1+B2+B3 first-deliverable scope (locked 2026-05-10)
- All other v0.1.0 specs unchanged

## Implementation discipline (unchanged from v0.1.0, applied uniformly)

- **First-principles translation**: each backend translates the canonical equation directly, not the other backend's source. The Fortran kernel is not the source-of-truth for C++; `shared/canonical-equations/dft.md` is.
- **No external math libraries**: no FFTW, no Eigen, no Boost, no MKL, no LAPACK. Both backends ship pure-language reference code.
- **No optimisation in v0.x reference builds**: `-O0` + `-ffp-contract=off` in both backends. Stage 5 (perf, v0.5+) introduces optimised target on the same source.
- **ASCII-only source** (KB-039): both Fortran and C++ source files contain no Unicode. Banner blocks use `=` × 57.
- **Equation-to-code mapping in module headers**: every implementation file opens with a doc-comment block showing how each math operation maps to specific code lines.
- **OS-aware Makefiles** (KB-038): both backends build cleanly on Windows cmd.exe + POSIX sh + macOS without modification.

## Build and test on your machine

**Fortran reference (unchanged from v0.1.0):**
```bash
git clone https://github.com/lege-artis/fourier.git
cd fourier/backends/fortran
make clean && make test    # 5 unit + 6 property + 14 physics + 748 golden
```

**C++ reference (new in v0.2.0):**
```bash
cd ../cpp
make clean && make test    # 5 unit + 6 property + 14 physics + 748 golden
```

Requires gfortran 13+ for Fortran, g++ 11+ (or clang++ 14+) for C++. Both with GNU Make + Python 3 with NumPy + SciPy (for golden-vector regeneration).

## What's NOT yet in this release (next-track roadmap)

- **Rust port** — queued for v0.2.x. `backends/rust/` directory will mirror the C++ structure. Sonnet-delegable per the same handoff pattern.
- **Pascal port** — queued for v0.2.x. Anchors directly on Numerical Recipes 1986 1st edition.
- **CMake support for the C++ backend** — queued for v0.2.x convenience cleanup. `make` works cross-platform; CMake is for IDE integration.
- **CS / JA / DE / IT translations of canonical + engineer doc tiers** — queued for v0.2.1+.
- **Shad-tier engineer-narrated docs** (B1 oscilloscope + B2 audio + B3 vibration first deliverable batch) — queued for v0.2.x. Scope locked at `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`.
- **FFT (Cooley-Tukey decimation-in-time)** — queued for v0.3.0. Property P5 (FFT ≡ DFT to floating-point precision) lands when FFT lands.
- **Performance build (Stage 5)** — queued for v0.5+. Same kernels, swapped flags (`-O3 -march=native`), gated on FFT shipping at v0.3.0.

## Citation

```
Yamyang, P. (2026). lege-artis/fourier v0.2.0 — Fortran + C++ canonical
reference implementations of the Discrete Fourier Transform.
https://github.com/lege-artis/fourier (tag v0.2.0)
```

## License

- **Code** (everything under `backends/`, `tools/`, Makefiles, GitHub Actions): Apache License 2.0 — see `LICENSE`
- **Documentation** (everything under `docs/`, `shared/`, `_specs/`, this file): Creative Commons Attribution-ShareAlike 4.0 International — see `LICENSE-DOCS`
- **Trademark notice**: the names `MIM2000`, `Improwave`, and the personal name `Petr Yamyang` are not licensed for derivative use — see `TRADEMARK.md`

## Acknowledgements

The implementation discipline carried from v0.1.0 — first-principles equation translation, validation against independent oracles, layered test pyramid — is what makes the second-language port land cleanly. Authoring the C++ kernel from `shared/canonical-equations/dft.md` (rather than from `backends/fortran/src/dft_kernel.f90`) is what makes the cross-language match meaningful: two independent renderings of the same math, both validated against the same oracle, both producing identical numerical results. That's not a coincidence; that's the canonical-reference pattern working as designed.

KB-037 through KB-041 carry across to C++ unchanged: case-insensitivity (Fortran-only), OS-aware Makefile (both languages), ASCII-only source (both), Option G gate (both), sandbox-vs-PowerShell git index lock (process-level, not language-level).
