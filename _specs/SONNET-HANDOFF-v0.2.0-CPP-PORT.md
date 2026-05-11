# Sonnet Handoff — `lege-artis/fourier` v0.2.0 C++ Port

**Status:** Ready to delegate
**Author:** Petr Yamyang (Opus session 2026-05-10)
**Target executor:** Sonnet session(s), runnable independently or in parallel with v0.2.0 Rust + Pascal ports
**Locks-in version:** lege-artis/fourier v0.1.0 PUBLIC (`0106afb`); monorepo `b30999a`
**Goal:** drive lege-artis/fourier from v0.1.0 (Fortran reference only) to v0.2.0-rc1 (Fortran + C++ both green at the same gates)
**License:** Apache-2.0 (this delegation contract; same as the project)

---

## 0. Read these first (in order)

1. `_specs/SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md` — the Stage-4 handoff that drove Jobs 1+2+3 to green. Sections §1 (implementation discipline), §5 (out of scope), §6 (cross-job context), §7 (failure-mode escalation) **all apply identically here** — re-read them, don't re-derive.
2. `_specs/SONNET-CLOSE-v0.1.0-RC-2026-05-10.md` — the Stage-4 close-out, especially the gate formulae table and the Option G error-gate rationale (§KB-040)
3. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy, three doc tiers (canonical / engineer / performance), Stage 5 perf-build sequencing (gated v0.5+)
4. `shared/canonical-equations/dft.md` — Eq. DFT-1; **the only authoritative source for what the algorithm computes**
5. `backends/fortran/src/dft_kernel.f90` — the validated Fortran reference. Your C++ kernel must produce values that match this kernel within the same tolerance gates the Fortran kernel produces against the SciPy/NumPy oracle. Read for the math-to-code mapping pattern; do **NOT** translate Fortran-to-C++ syntactically — translate the canonical equation directly into idiomatic C++.
6. `backends/fortran/tests/test_dft_*.f90` — your test programs mirror this layout (unit + property + physics + golden = 4 test programs)
7. `_config/KB-LESSONS-LEARNED.yaml` entries KB-037, KB-038, KB-039, KB-040, KB-041 — five build-chain / numerical / process traps already eaten in this codebase; do not re-eat them

---

## 1. Implementation discipline (NON-NEGOTIABLE — same as Stage-4)

§1.1 through §1.8 of `SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md` apply unchanged. Specifically:

- **ASCII-only source** (KB-039) — no Unicode in `.cpp` / `.hpp` source files, comments, or string literals; no UTF-8 box-drawing or em-dashes. Use `=` instead of `═`, `-` instead of `—`, `pi` instead of `π`. Banner blocks use `=` × 57.
- **Equation-to-code mapping in module/file header** — every implementation file opens with a doc-comment block mapping math expressions to specific code lines.
- **Build-flag conformance**: clarity flags for v0.2.0 reference (NOT performance — Stage 5 / v0.5+ scope):
  ```
  CXXFLAGS = -O0 -g -Wall -Wextra -Wpedantic -std=c++17 \
             -ffp-contract=off -fsignaling-nans
  ```
- **Tolerance gates** — same as Fortran: 1e-13 unit/property, P8 9.1e-13, PT-DFT-03B 1e-10, golden-vector Option G 1e-13·sqrt(N).
- **Kernel module is the source of math truth, NOT the Fortran kernel.** Translate Eq. DFT-1 directly into C++; do NOT port Fortran code line-by-line. The implementation philosophy is "canonical equation -> code", not "Fortran -> C++".
- **Subroutine shape**: each test = a function in a `program` namespace; parent program declares `total` / `failed` counters; `assert_*_close` helpers update via shared scope.
- **Banner format**: `=` × 57, then ` lege-artis/fourier - <suite-name> (v0.2.0 C++ ref)`, then `=` × 57.

### 1.1 New constraints specific to C++ port

- **C++17 standard.** No C++20 features (modules, concepts) — those younger language features narrow compiler-version compatibility for an OSS reference. Use:
  - `std::complex<double>` for complex numbers
  - `std::vector<std::complex<double>>` for sequences
  - `std::array<...>` for fixed-size sequences where natural
  - `<cmath>` for `cos` / `sin` / `atan` / `sqrt`
  - `<cassert>` for runtime correctness checks (debug builds)
  - **NOT** `std::execution::par` or any parallel STL — Stage 5 scope.
- **No FFTW, no Eigen, no Boost.** External-library use is forbidden in the v0.1.x/v0.2.0 reference per WORKING-SPEC §4. Numerical Recipes 2007 3rd edition is the C++ idiom anchor; mirror its style for direct DFT (their §12.2-12.3).
- **Header + source split.** `backends/cpp/include/lege_artis_fourier/dft_kernel.hpp` declares the API; `backends/cpp/src/dft_kernel.cpp` implements. Tests include the header.
- **Namespacing.** All public symbols live under `namespace lege_artis::fourier`. Functions: `dft`, `idft`. Type alias: `using cdouble = std::complex<double>;` for legibility in tests.
- **No exceptions thrown by the kernel.** The math has no failure modes worth throwing for at this stage. Wrong-size inputs are caught by `assert(...)` in debug builds; release builds trust the caller.

---

## 2. Build system — Make (consistency with Fortran), CMake support deferred

The repo's existing OS-aware Makefile pattern (KB-038) extends naturally to C++. Add a sibling `backends/cpp/Makefile` mirroring `backends/fortran/Makefile` structure:

```make
CXX := g++

CXXFLAGS_REF  = -O0 -g -Wall -Wextra -Wpedantic -std=c++17
CXXFLAGS_REF += -ffp-contract=off -fsignaling-nans
CXXFLAGS_PERF = -O3 -march=native -funroll-loops -std=c++17  # v0.5+ Stage 5
CXXFLAGS = $(CXXFLAGS_REF)

INC_DIR   = include
SRC_DIR   = src
TEST_DIR  = tests
BUILD_DIR = build

ifeq ($(OS),Windows_NT)
    MKDIR_BUILD = if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)"
    RM_BUILD    = if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
else
    MKDIR_BUILD = mkdir -p "$(BUILD_DIR)"
    RM_BUILD    = rm -rf "$(BUILD_DIR)"
endif

# ... (test targets, golden-data prep target, test:, clean: — see Fortran Makefile pattern)
```

The `golden-data:` target is the same script as Fortran's: `python3 ../../tools/json_to_fortran_data.py` produces fixed-format `.dat` files; both backends consume them. **Do not author a parallel JSON parser in C++** — adds dependency complexity. The `.dat` format is the canonical cross-language data interchange.

CMake support is queued but out of scope for v0.2.0; will add at v0.2.x cleanup if community asks. Decision logged in this handoff so reviewers don't loop on it.

---

## 3. Job-1 — C++ kernel + unit tests

**Output:**
- `backends/cpp/include/lege_artis_fourier/dft_kernel.hpp`
- `backends/cpp/src/dft_kernel.cpp`
- `backends/cpp/tests/test_dft_unit.cpp`
- `backends/cpp/Makefile`

**Spec:** Same as Fortran unit tests — N=4 pure cosine, N=4 DC input, N=4 impulse-at-centre, N=8 pure cosine, N=8 IDFT roundtrip
**Gate:** 5/5 PASS at 1e-13
**Estimated size:** ~120 lines kernel + ~200 lines test program + ~50 lines Makefile

### 3.1 Kernel API (LOCKED)

```cpp
// backends/cpp/include/lege_artis_fourier/dft_kernel.hpp
#pragma once
#include <complex>
#include <vector>

namespace lege_artis::fourier {

using cdouble = std::complex<double>;
using cvector = std::vector<cdouble>;

// Forward DFT - direct evaluation of dft.md Eq. DFT-1.
// Asymmetric forward (no 1/N in forward; matches numpy.fft.fft).
cvector dft(const cvector& x);

// Inverse DFT - dft.md Eq. DFT-2 with 1/N normalisation.
cvector idft(const cvector& X_in);

}  // namespace lege_artis::fourier
```

### 3.2 Tag at green

`v0.0.6-cpp-unit-green` (continues numbering from `v0.0.5-fortran-golden-green`).

---

## 4. Job-2 — C++ property tests

**Output:** `backends/cpp/tests/test_dft_property.cpp`
**Spec:** P1 Linearity, P2 Plancherel, P3 DC bin, P4 Hermitian, P7 Time-shift, P8 Convolution — same concrete inputs locked in `SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md` §2.1. Numerical inputs are the contract; do not improvise.
**Gate:** 6/6 PASS at the same gates (P1-P4/P7 1e-13, P2 scaled, P8 9.1e-13)
**Tag:** `v0.0.7-cpp-property-green`

---

## 5. Job-3 — C++ physics testbeds

**Output:** `backends/cpp/tests/test_dft_physics.cpp`
**Spec:** PT-DFT-01 Fraunhofer single-slit, PT-DFT-02 heat-equation impulse, PT-DFT-03A SHO frequency identification, PT-DFT-03B leakage profile — per `shared/physics-testbeds/dft.md`. PT-DFT-03B leakage testbed compares against `shared/golden-vectors/dft_n=64_cosine_leakage.json` (after JSON→.dat conversion).
**Gate:** 14/14 assertions PASS at testbed-specific tolerances
**Tag:** `v0.0.8-cpp-physics-green`

---

## 6. Job-4 — C++ golden-vector verification

**Output:** `backends/cpp/tests/test_dft_golden.cpp`
**Spec:** Load `backends/cpp/build/golden/dft_n_{2,4,8,16,64}.dat` (produced by the same `tools/json_to_fortran_data.py`; both backends share the .dat artifacts), run `dft()` on each input, compare to oracle output using **Option G gate** (per KB-040):
```cpp
double metric = std::abs(got - expected) / std::max(std::abs(expected), 1.0);
double gate   = 1.0e-13 * std::sqrt(static_cast<double>(N));
```
**Gate:** 748/748 element-checks PASS
**Tag:** `v0.0.9-cpp-golden-green`

---

## 7. After all four C++ jobs land green — v0.2.0 release

**Opus (NOT Sonnet) authors the v0.2.0 release commit:**

1. Update `RELEASE-NOTES-v0.2.0.md` (mirror v0.1.0 structure; add C++ section to "What's in this release")
2. Update `_specs/WORKING-SPEC-v0.3-EN.md` to mark C++ as v0.2.0 shipped + Rust/Pascal as next-track for v0.2.x
3. Update `MANIFEST.yaml` `projects.lege-artis/fourier` entry: live_version → v0.2.0, test_summary expanded with cpp_* fields
4. Update `CLAUDE.md` § CURRENT STATE row + HANDOFF block
5. Cross-language sanity check: run a Python script that loads the same JSON inputs, runs both `backends/fortran/build/test_dft_golden` AND `backends/cpp/build/test_dft_golden`, asserts they produce values agreeing to within 1e-12 (cross-language consistency, tighter than Option G because both use the same algorithm — only IEEE-754 ordering differences allowed)
6. Tag `v0.2.0` on monorepo + lege-artis/fourier
7. Publish GitHub Release at v0.2.0

**Visibility flip is NOT needed** — repo already public. v0.2.0 is just a tagged release on the existing public repo.

---

## 8. What Sonnet should NOT touch (out of scope)

Same as Stage-4 §5, plus:
- Rust port (`backends/rust/`) — separate v0.2.0 track, separate handoff doc when ready
- Pascal port (`backends/pascal/`) — separate v0.2.0 track, anchors directly on Numerical Recipes 1986 1st edition
- CMake support — deferred to v0.2.x cleanup (Make is the v0.2.0 scope per §2)
- Stage 5 perf build (`backends/cpp/Makefile` `perf:` target wired but not exercised in v0.2.0 — gated v0.5+)
- Shad-tier documentation chapters — separate work track per `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`

---

## 9. Sonnet failure-mode escalation

Same as Stage-4 §7. Specifically for C++ port:

- If a test fails at gate that the Fortran equivalent passes at → suspect translation bug, NOT kernel bug. Re-derive the equation translation from `shared/canonical-equations/dft.md`, not from the Fortran source.
- If `g++ -std=c++17 -Wpedantic` emits a warning → fix the source, do not suppress the flag (KB-039 Fortran rule applies symmetrically).
- If the Make recipe works in MSYS2 sh but breaks in cmd.exe → use the OS-aware pattern from KB-038. Do not assume the user has sh in PATH.
- If JSON parsing crosses your mind as a "simpler" alternative to the .dat loader → no. Cross-language consistency requires both backends consume identical data; the .dat format is the contract.
- If you suspect the Option G gate is wrong → no, it's not. Re-read KB-040. The gate was empirically validated against 748 element-checks.

Status-doc template: `_specs/SONNET-STATUS-CPP-<job-id>-<short-description>.md`. Pete picks up on next Opus session.

---

## 10. Pre-release content audit (R-PRE-PUB-AUDIT-1)

The repo is already public, so v0.2.0 doesn't trigger a visibility flip. But each commit pushed to `lege-artis/fourier:main` propagates publicly. Before any subtree-push during the v0.2.0 work:

1. `grep -rinE "bouracka|bouračka|čkp|ckp|supin|mi-m-t" backends/cpp/ tests/` should return zero matches in non-historical files
2. `grep -rinE "bouracka|bouračka|čkp|ckp|supin|mi-m-t" *.md _specs/` should return zero matches in any new files (existing v0.1.0 files have already been audited)
3. ASCII-only check: `grep -rilP "[^\x00-\x7F]" backends/cpp/` should return zero
4. License header in every new `.cpp` / `.hpp`: SPDX-License-Identifier comment line at top (`// SPDX-License-Identifier: Apache-2.0`)

These are MANIFEST `conventions.pre_publication_audit_rule` (R-PRE-PUB-AUDIT-1) applied to ongoing development on a public repo, not just to one-time visibility flips.

---

## 11. Cross-port coordination — Rust + Pascal in parallel

If Rust and Pascal port handoffs are authored and assigned to separate Sonnet sessions in parallel:

- Each port has its own `backends/<lang>/` directory; no shared code beyond `shared/` and `tools/`
- Each port has its own SONNET-HANDOFF-v0.2.0-<LANG>-PORT.md
- Each port produces its own tag chain (`v0.0.10-rust-*`, `v0.0.13-pascal-*`)
- Race conditions during commit + subtree-push are managed by Pete on the user's PowerShell, not by Sonnet. Sonnet's job ends at "tests pass + commit prepared". Pete coordinates the cross-port pushes.
- v0.2.0 release happens **after all three ports** (C++ + Rust + Pascal) land green.

---

## 12. End state — what v0.2.0 looks like

- 4 C++ test programs all PASS at the same gates as Fortran
- Rust + Pascal ports also green (via parallel Sonnet sessions)
- Monorepo + lege-artis/fourier tagged `v0.2.0`
- GitHub Release at `v0.2.0` published
- Cross-language sanity script confirms all 4 backends produce values agreeing within 1e-12
- WORKING-SPEC-v0.3-EN.md updated to mark v0.2.0 closed + v0.2.x doc-tier + Stage 5 perf as next active tracks

---

*This handoff is the contract for the C++ track of v0.2.0. Sonnet sessions execute against this; Opus reviews, integrates, and tags the v0.2.0 release. Stage 5 (perf), Stage 6+ (Shad-tier authoring), and v0.1.1+ translations all happen after v0.2.0 ships.*
