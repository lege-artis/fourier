# Sonnet Handoff — `lege-artis/fourier` Stage-4 Follow-on (Property + Physics + Golden Tests)

**Status:** Ready to delegate
**Author:** Petr Yamyang (Opus session 2026-05-09)
**Target executor:** Sonnet session(s), one per Job, runnable independently
**Locks-in version:** Monorepo `0079b1b` / lege-artis/fourier `24531a0` / tag `v0.0.2-fortran-ref-green`
**Goal of follow-on:** drive Fortran reference from v0.0.2 (5/5 unit) to v0.1.0-rc (5 unit + 6 property + 4 physics + 6 golden = 21+ tests, all green at 1e-13 gate)
**License:** Apache 2.0 / CC-BY-SA-4.0 (same as project)

---

## 0. Read these first (in order)

1. `_specs/WORKING-SPEC-v0.3-EN.md` — the master spec, especially §4 (implementation philosophy: line-by-line equation translation, no porting), §6 (three doc tiers), §11 (license stack)
2. `shared/canonical-equations/dft.md` — Eq. DFT-1 / DFT-2; the **only** authoritative source for what the algorithm computes
3. `shared/property-tests/dft.md` — P1-P8 properties; this drives Job-1
4. `shared/physics-testbeds/dft.md` — PT-DFT-01/02/03A/03B; this drives Job-2
5. `shared/golden-vectors/dft_n=*.json` — six oracle JSONs; this drives Job-3
6. `backends/fortran/src/dft_kernel.f90` — the validated kernel; **import only, do not modify**
7. `backends/fortran/tests/test_dft_unit.f90` — your **template** for test-program structure (program + contains + test subroutines + assertion helpers)
8. `backends/fortran/Makefile` — your template for adding new test-binary targets
9. `_config/KB-LESSONS-LEARNED.yaml` entries KB-037 (Fortran case-insensitivity), KB-038 (Make on Windows / cmd.exe), KB-039 (gfortran ASCII-only) — three traps already eaten in this codebase; do not re-eat them

---

## 1. Implementation discipline (NON-NEGOTIABLE)

These rules apply to every Fortran file you author or touch. Violation = re-do, no exceptions.

### 1.1 ASCII-only source
- No box-drawing characters (`═`, `─`), no em-dashes (`—`), no Greek letters (`π`), no arrows (`→`), no math symbols (`§`, `≡`, `·`) anywhere in `.f90` files (source, tests, comments)
- gfortran `-std=f2018 -pedantic` byte-counts UTF-8 against the 132-column limit; this WILL bite
- ASCII alternatives: `=`, `-`, `pi`, `->`, `section`, `==`, `*`
- Banner blocks use `=` × 57 (matches existing test file)

### 1.2 No casing collisions
- Fortran is case-insensitive; `integer :: N, k, n` declares `n` twice (silent collision, then "Symbol already has basic type" cascade)
- Convention in this codebase: `nlen` = sequence length (NOT `N`), keep `k`, `n` for math-equation indices
- Same rule applies to any new variable: if its lowercase form clashes with another in scope, rename one

### 1.3 Equation-to-code mapping in module/file header
- Every implementation file opens with a doc-comment block mapping math expressions (from `shared/canonical-equations/*.md` or `shared/property-tests/dft.md`) to specific code lines
- Reader must be able to re-derive the algorithm from the comments alone

### 1.4 Build-flag conformance (don't relax)
- All Fortran tests compile with `-O0 -g -fcheck=all -Wall -Wextra -pedantic -std=f2018 -fimplicit-none -ffp-contract=off`
- If a test triggers a warning, fix the test, don't suppress the flag
- Performance flags (`-O3 -march=native`) are reserved for Stage 5 / v0.5+; never use for v0.1.x reference

### 1.5 Tolerance gate
- Default = `1.0e-13_dp` (matches existing unit tests)
- Tests SHOULD pass at 1e-14 or better on real inputs; the 1e-13 gate is the published contract
- If a property genuinely needs a wider gate (e.g. Plancherel scales with `sum|x|^2`), document the chosen tolerance + rationale in the test's doc-comment

### 1.6 Kernel is read-only
- `backends/fortran/src/dft_kernel.f90` is validated; do NOT modify under any circumstance for this Stage-4 follow-on
- If the kernel needs a change, raise the question in a separate doc and stop the Sonnet session for Pete review
- Kernel exports: `dft`, `idft`, `dp` (precision kind). Use only these.

### 1.7 Makefile changes use the established pattern
- Each new test program gets a `$(BUILD_DIR)/test_<name>` target
- The `test:` target depends on all test binaries and runs each
- ALL Makefile recipes must work on Windows cmd.exe + POSIX sh (use the existing OS-aware MKDIR_BUILD / RM_BUILD pattern)
- No bash-only constructs (`[[`, `<<<`, `$(())`)
- No PowerShell-only constructs

### 1.8 Subroutine shape (match the template)
- Each test = a `subroutine` defined under `contains` in the same `program` unit
- Parent program declares `total` / `failed` integers; `assert_*_close` helpers update these via shared scope
- Final summary: `Result: N/M passed`, `stop 1` on any fail, `0` on all-pass
- Banner format: `=` × 57, then ` <project> - <test-suite-name> (v<version>)`, then `=` × 57

---

## 2. Job-1 — Property test backend

**Output:** `backends/fortran/tests/test_dft_property.f90`
**Spec:** `shared/property-tests/dft.md` properties P1, P2, P3, P4, P7, P8 (P5 is FFT-equivalence, deferred to v0.2.0; P6 inverse-roundtrip is already in unit suite)
**Gate:** 6/6 PASS at 1e-13 max-abs-error (some properties may use scaled gate per §1.5)
**Estimated size:** ~250-300 lines

### 2.1 Concrete inputs (LOCKED — do not improvise)

| Property | Test name (subroutine) | Inputs | Expected check |
|---|---|---|---|
| P1 Linearity | `test_p1_linearity` | x[i] = i + 2i·j (i=1..8), y[i] = (3i-1) + (-i)·j (i=1..8), alpha = (2.5, -0.3), beta = (-1.0, 1.2) | dft(alpha*x + beta*y) == alpha*dft(x) + beta*dft(y) |
| P2 Plancherel | `test_p2_plancherel` | x[i] = (0.7·i) + (0.5·i - 2)·j (i=1..16) | sum(\|x\|^2) == sum(\|X\|^2) / N (gate scaled by sum(\|x\|^2) per §1.5) |
| P3 DC bin | `test_p3_dc_bin` | x[i] = i + (0.3·i)·j (i=1..8) | X[0] == sum(x) |
| P4 Hermitian | `test_p4_hermitian` | x[i] = 0.5·i - 1.5 (real, i=1..8) | X[k] == conj(X[N-k]) for k=1..N/2; X[0] real |
| P7 Time-shift | `test_p7_time_shift` | x[i] = 0.4·i + (0.7·i - 1)·j (i=1..8), m=3 circular shift | dft(x_shifted)[k] == X[k] · exp(-2*pi*i*k*m/N) |
| P8 Convolution | `test_p8_convolution` | x = [1..8] real, y = [0.5, 1, 1.5, 2, 1.5, 1, 0.5, 0] real, z = circ-conv(x,y) | dft(z)[k] == X[k] * Y[k] |

### 2.2 Helpers needed beyond the unit-test pattern

- `assert_complex_close` — single-element complex comparison (for P3 X[0] check)
- `assert_real_close` — single real-value comparison with tolerance (for P2 Plancherel scalar)
- Reuse existing `assert_complex_array_close` for P1, P4 (after constructing expected mirror), P7, P8
- Module loop: ALL helpers go in `contains` block, share parent's `total` / `failed`

### 2.3 Makefile addition

```make
TESTS_PROP   = $(TEST_DIR)/test_dft_property.f90
TEST_PROP_BIN = $(BUILD_DIR)/test_dft_property

$(TEST_PROP_BIN): $(OBJECTS) $(TESTS_PROP) | $(BUILD_DIR)
	$(FC) $(FFLAGS) -I$(BUILD_DIR) -o $@ $(OBJECTS) $(TESTS_PROP)
```

Add `$(TEST_PROP_BIN)` to the `test:` target's run sequence (after the unit-test invocation).

### 2.4 Acceptance gate for Job-1

```powershell
cd backends/fortran
make clean
make test
# Expected:
#   Running DFT unit tests (v0.1.0 reference)...
#   ... 5/5 unit PASS ...
#   Running DFT property tests (v0.1.0 reference)...
#   ... 6/6 property PASS at 1e-13 ...
```

If any test fails: dump `actual[idx]` and `expected[idx]` (per existing helper format), revisit either the reference vector calculation or a possible kernel-precision boundary. Do NOT lower the gate without Pete review.

### 2.5 Commit + tag (Sonnet completes)

```powershell
cd C:\Users\vitez\Documents\VibeCodeProjects
git add fourier/backends/fortran/tests/test_dft_property.f90 fourier/backends/fortran/Makefile
git commit -m "fourier: Property test backend - P1+P2+P3+P4+P7+P8 6/6 PASS"
git push origin <current-branch>
git tag -a v0.0.3-fortran-property-green -m "Fortran reference - 11/11 (5 unit + 6 property) PASS at 1e-13"
git push origin v0.0.3-fortran-property-green
git subtree push --prefix=fourier lege-artis-fourier main
# Then mirror the tag to lege-artis-fourier:
git ls-remote lege-artis-fourier refs/heads/main  # get new SHA
git push lege-artis-fourier <NEW_SHA>:refs/tags/v0.0.3-fortran-property-green
```

---

## 3. Job-2 — Physics testbed backend

**Output:** `backends/fortran/tests/test_dft_physics.f90`
**Spec:** `shared/physics-testbeds/dft.md` PT-DFT-01 (Fraunhofer single-slit), PT-DFT-02 (heat-equation impulse decay), PT-DFT-03A (SHO frequency identification), PT-DFT-03B (cosine leakage profile)
**Gate:** 4/4 PASS at testbed-specific tolerances (per spec)
**Estimated size:** ~350-400 lines (more setup than property tests; physics expected values come from analytic formulae)
**Note:** PT-DFT-03B leakage testbed has its own golden-vector JSON at `shared/golden-vectors/dft_n=64_cosine_leakage.json` — load and compare against that

### 3.1 Concrete inputs

Per spec for each testbed. Where the spec says "appropriate N", use:
- PT-DFT-01 Fraunhofer: N=64, slit-width 8 (centred), expected sinc-pattern with sidelobes at known positions
- PT-DFT-02 heat-equation: N=64, impulse at n=32 (centred), check decay rate matches Green's function on each spectral mode
- PT-DFT-03A SHO: N=128, cos(2*pi*8*n/N), assert X[8] = X[120] = N/2 = 64, all others < 1e-13
- PT-DFT-03B leakage: N=64, cos(2*pi*5.5*n/N), compare element-wise against `dft_n=64_cosine_leakage.json` (load via Job-3 mechanism — depends on Job-3 if Sonnet delegates simultaneously, otherwise hard-code the expected magnitudes from a spec-provided table)

### 3.2 Same Makefile + acceptance pattern as Job-1

Tag at completion: `v0.0.4-fortran-physics-green` (15+/15+ PASS).

---

## 4. Job-3 — Golden-vector loader + verification

**Output:** `backends/fortran/tests/test_dft_golden.f90` + `tools/json_to_fortran_data.py`
**Spec:** Implicit — load `shared/golden-vectors/dft_n={2,4,8,16,64}.json`, run `dft()` on each input, compare to oracle output, gate 1e-13
**Gate:** All 6 JSON files × all input cases per file PASS

### 4.1 JSON-to-Fortran build step (per locked decision §0)

- Author `tools/json_to_fortran_data.py` — reads each `dft_n=*.json`, emits a fixed-format `.dat` file per JSON with header (N, num_cases) + per-case (input length, input flat real+imag, expected length, expected flat real+imag)
- Add Makefile target `golden-data: tools/json_to_fortran_data.py shared/golden-vectors/*.json` that regenerates the .dat files
- `test_dft_golden.f90` reads the .dat files via Fortran `open(form='formatted')` + `read(*,*)`

### 4.2 Acceptance + tagging

Tag at completion: `v0.0.5-fortran-golden-green`. After Job-1 + Job-2 + Job-3 all green, declare **v0.1.0-rc** state and prep for the public flip per WORKING-SPEC-v0.3 §10.

---

## 5. What Sonnet should NOT touch (out of scope)

- The kernel `src/dft_kernel.f90` (see §1.6)
- Specs under `_specs/`, `shared/canonical-equations/`, `shared/property-tests/`, `shared/physics-testbeds/`, `shared/reference-bibliography/` (these are Opus-authored; if a discrepancy is found, raise it, don't fix it)
- The license stack (LICENSE, LICENSE-DOCS, NOTICE, TRADEMARK.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, .github/FUNDING.yml)
- WORKING-SPEC versioning (v0.4+ requires Opus authoring)
- Stage 5 (perf build) — gated on v0.1.0 close
- Shaddack-tier docs — gated on v0.1.0 close per scope-doc
- Multi-language ports (C++, Rust, Pascal) — separate v0.2.0 work track
- The `lege-artis/fourier` org-level settings (still private until v0.1.0 release)

---

## 6. Cross-job context (read once, applies to all jobs)

- Repo state: monorepo private @ github:petr-yamyang/VibeCodeProjects, branch `thinkpad`. lege-artis/fourier private mirror @ github:lege-artis/fourier, branch `main`, sync via `git subtree push --prefix=fourier lege-artis-fourier main`
- All three jobs are independent — Sonnet can run them in parallel sessions
- Each job ends with: tests green + commit + monorepo tag + lege-artis subtree-push + lege-artis tag mirror (per pattern in §2.5)
- After all three green: monorepo state is **v0.1.0-rc**, lege-artis/fourier is ready for public flip (Opus does the public-flip + final v0.1.0 tag, NOT Sonnet)

---

## 7. Failure-mode escalation

If a Sonnet session encounters any of the following, **STOP and write a STATUS doc** instead of guessing:

- Kernel produces a value that disagrees with a property-test analytic prediction (could be kernel bug, could be test bug — Opus to triage)
- A golden-vector JSON case fails by >1e-13 (oracle disagreement, not kernel)
- A spec section is ambiguous (e.g. exact tolerance not specified for a particular testbed)
- A Makefile target works on POSIX but breaks on cmd.exe (or vice versa) and the OS-detection pattern in §1.7 doesn't cover it
- gfortran emits a warning that `-Wno-X` would suppress but feels like it's pointing at a real bug

Status-doc template: `_specs/SONNET-STATUS-<job-id>-<short-description>.md`. Pete picks it up on next Opus session.

---

## 8. End state — what v0.1.0-rc looks like

- 21+ tests across 3 test programs all PASS at 1e-13 gate
- 3 monorepo tags: `v0.0.3-fortran-property-green` / `v0.0.4-fortran-physics-green` / `v0.0.5-fortran-golden-green`
- 3 lege-artis tags mirroring the same
- WORKING-SPEC-v0.3 §10 release-checklist all green
- Ready for Opus to author the public-flip commit (LICENSE/NOTICE final review, README publish-ready, GitHub Settings → Public, tag `v0.1.0`)

---

*This handoff is the contract. Sonnet sessions execute against this; Opus reviews + integrates + tags the v0.1.0 release. Stage 5 (perf), Stage 6+ (multi-language ports), and Shaddack tier all happen after v0.1.0 ships.*
