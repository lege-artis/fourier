# Fourier v0.2.x — Testbed expansion to enforce reference-implementation acceptance criteria (C1–C4)

**Status:** Ready to delegate
**Author:** Opus (orchestrator) — 2026-05-21
**Target executor:** Sonnet (MacBook or ThinkPad; toolchain-agnostic — gfortran + g++ + Python 3.13)
**Locks-in version baseline:** lege-artis/fourier v0.2.0 PUBLIC (Fortran + C++ both green at bit-identical worst-error numbers)
**Goal:** drive lege-artis/fourier from v0.2.0 → v0.2.x by adding the testbed expansion that promotes Fortran and Pascal from "hand-rolled-and-visible" to "state-of-the-art best-referential, best-documented, best-tested" per the doctrine codified in `_config/LEGE-ARTIS-LANGUAGE-DOCTRINE-v0.1.md` §4.4 (criteria C1–C4)
**License:** Apache-2.0 (code) + CC-BY-SA-4.0 (docs)
**Tag at green:** `v0.0.X-testbed-expansion-c1234-green` per-stage; rolling up into `v0.2.1` once the full matrix is green across Fortran + C++ (Pascal joins at its v0.2.x landing)

---

## §0. Read these first (in order)

These contain the contract and the existing patterns. **Do not re-derive what they already specify.**

1. `../../../_config/LEGE-ARTIS-LANGUAGE-DOCTRINE-v0.1.md` §4.4 — **C1–C4 acceptance criteria**. This is the contract. Implement to it literally.
2. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy + three doc tiers + canonical equation immutability.
3. `_specs/SONNET-HANDOFF-v0.2.0-CPP-PORT.md` — proven discipline template; §1 (implementation discipline — ASCII-only, equation-to-code mapping), §3 (tolerance gates) apply unchanged.
4. `shared/canonical-equations/dft.md` — Eq. DFT-1, the **only** authoritative source for the algorithm.
5. `shared/property-tests/dft.md` — existing property-test catalogue (P1–P8). Some C1 textbook tests overlap; preserve the existing assertions and **add** the textbook-verbatim layer, do not replace.
6. `shared/physics-testbeds/dft.md` — existing physics testbeds (PT-DFT-01..03B; Thorne-anchored). Same overlap principle.
7. `backends/fortran/tests/*.f90` — existing test patterns. Inherit the file/test-runner convention.
8. `backends/cpp/tests/*` — same, C++ side.

Optional but useful:
- `_config/KB-LESSONS-LEARNED.yaml` KB-037..041 — five traps already eaten (Fortran case-insensitivity, GNU-Make-on-Windows, ASCII-only Fortran source under `-pedantic`, etc.).
- `RELEASE-NOTES-v0.2.0.md` — sets framing for `v0.2.1` notes you'll author at end.

---

## §1. Scope — five deliverables, all binding for canonical-reference status

| # | Deliverable | C-criterion | Where it lands | Estimated effort |
|---|---|---|---|---|
| **D1** | NR-textbook-verbatim FFT test set — ≥3 inputs/outputs from Press 1986 NR Pascal ch.12 + ≥3 from Press 2007 NR 3rd ed ch.12–13 | **C1** | `shared/textbook-verbatim/dft.md` + `backends/<lang>/tests/test_textbook_verbatim.*` + 6+ golden vectors under `shared/golden-vectors/textbook-*/` | ~4–6 h |
| **D2** | Cooley-Tukey 1965 paper 8-point worked example reproduction | **C1** (tertiary anchor) | Same files as D1; one extra golden vector `shared/golden-vectors/cooley-tukey-1965-n8.json` + one extra test per backend | ~1–2 h |
| **D3** | IEEE-754 corner-case test set — denormals, ±0, NaN propagation, ±∞ | (best practice; complements C1) | `shared/ieee754-corners/dft.md` + `backends/<lang>/tests/test_ieee754_corners.*` | ~2–3 h |
| **D4** | Empirical O(N log N) complexity audit (nightly, not per-commit) | **C4** | `backends/<lang>/tests/complexity_audit.*` + `.github/workflows/nightly-complexity.yml` + `_audit/complexity-audit-log.md` | ~3–4 h |
| **D5** | Cross-backend bit-identity CI assertion across hand-rolled matrix | **C2** | `tests/cross_backend/test_bit_identity.py` + `.github/workflows/cross-backend.yml` | ~2–3 h |

All five are independent and may run in parallel sub-sessions. **Suggested order if sequential:** D1 → D2 → D5 → D3 → D4. D1 + D2 deliver the highest reader-impact; D5 formalises the v0.2.0 implicit finding; D3 + D4 are infrastructure-leaning.

**C3 (per-routine textbook citation)** is a separate, smaller workstream — handled as a side-quest within D1 since you'll be touching the routine headers to add the textbook anchors anyway. See §3.6 below.

---

## §2. Implementation discipline (NON-NEGOTIABLE — inherited from prior handoffs)

- **ASCII-only source files** (KB-039). No Unicode in `.f90`, `.cpp`, `.hpp`, `.pas`, `.py`, or `.toml`. Markdown narrative may use Unicode.
- **Equation-to-code mapping** in module header comments. Every new test program opens with a doc-comment block citing the textbook reference, the equation, and the input/output expectation.
- **Translate the textbook example directly.** For D1 + D2: do NOT translate from one backend's test to another — read the textbook example, take the inputs as published, and validate against the outputs as published. Each backend independently reproduces the textbook.
- **No third-party FFT libraries** in test code. Use the existing backend kernels (`dft_kernel.cpp`, `kh_fft.f90`-equivalent). The textbook tests verify the reference, not a library.
- **Clarity flags, NOT performance flags** for D1/D2/D3/D5 tests. D4 complexity audit explicitly **does** use release-no-LTO flags because complexity is a runtime measurement — document the build profile in the audit doc.
- **Tolerance gates** for D1/D2: `≤ 1e-13` for absolute error against textbook-printed values (the textbook gives 4–6 significant digits typically; we're verifying our impl produces those same digits at full IEEE-754 precision). For D3: corner-case behaviour is binary (correct/incorrect propagation), not tolerance-based. For D4: slope ±0.1. For D5: ≤ 1 ULP × sqrt(N) accumulated.

---

## §3. Per-deliverable specs

### §3.1 D1 — NR-textbook-verbatim FFT test set

**Authoring source:** `shared/textbook-verbatim/dft.md` (new file). Structure mirrors `shared/physics-testbeds/dft.md`:

- §1 Purpose — why textbook-verbatim is the highest form of reference-implementation validation
- §2 Test TV-NR1986-A: Press 1986 NR Pascal ed ch.12 example 1 (specify input array verbatim from the book; record output array verbatim; cite page + equation)
- §3 Test TV-NR1986-B: Press 1986 NR Pascal ed ch.12 example 2
- §4 Test TV-NR1986-C: Press 1986 NR Pascal ed ch.12 example 3
- §5 Test TV-NR2007-A: Press 2007 NR 3rd ed ch.12 example 1
- §6 Test TV-NR2007-B: Press 2007 NR 3rd ed ch.12 example 2
- §7 Test TV-NR2007-C: Press 2007 NR 3rd ed ch.12–13 example 3
- §8 Coverage matrix (which examples land which routine: forward DFT? inverse? real-input? complex-input? real-and-imag mixed? FFT vs DFT?)
- §9 Citations (full page/equation specifications)

**Practical sourcing.** The textbooks are NOT in the repo (copyright). Pete owns physical copies (Press 1986 Pascal ed, Press 2007 3rd ed). The Sonnet executor cannot extract the example numerics directly; instead:

**Sourcing procedure:**
1. List the candidate example types per textbook section (e.g., "Press 1986 §12.2 gives a 16-point example with specific input array — extract input + output values from book").
2. Output a checklist `shared/textbook-verbatim/EXAMPLES-TO-LOOKUP.md` with: example identifier, textbook page, what the executor needs Pete to transcribe.
3. STOP here for the textbook-input phase. Pete fills the JSON inputs manually (15–30 min of transcription) and commits them as `shared/golden-vectors/textbook-nr1986-a.json`, etc.
4. Resume on the test-program side: implement `test_textbook_verbatim.f90` (and `.cpp`, `.pas` when present) that reads the JSON, runs the kernel, asserts against the textbook output values (also transcribed by Pete into the JSON's `expected_output` field).

**Acceptance gate D1:** ≥3 NR-1986 examples + ≥3 NR-2007 examples implemented; per-backend test runs green; tolerance ≤1e-13 vs textbook-printed values; `shared/textbook-verbatim/dft.md` complete with citations.

### §3.2 D2 — Cooley-Tukey 1965 paper 8-point reproduction

**Source.** Cooley, J. W., & Tukey, J. W. (1965). "An algorithm for the machine calculation of complex Fourier series." *Math. Comp.*, 19(90), 297–301.

The paper contains an 8-point worked example tracing the decimation-in-time butterfly stages. Extract:
- Input array: 8 complex values from the paper
- Intermediate values: after stage 1, stage 2, stage 3 (the paper shows these explicitly)
- Output array: 8 complex DFT values

**Implementation.** A single test program per backend (`test_cooley_tukey_1965.f90`, `test_cooley_tukey_1965.cpp`, etc.) that:
1. Sets up the 8-point input from the paper
2. Calls the backend's FFT kernel
3. Compares output against the paper's printed output (tolerance ≤1e-13)
4. **Bonus assertion** (optional, valuable): if the backend's FFT exposes intermediate stages (instrumentation hook), compare those too — this is the test that validates the butterfly ordering matches the paper, not just the final result.

**Sourcing procedure:** Same as D1 — list paper examples to transcribe, Pete commits the JSON, Sonnet implements the test programs.

**Acceptance gate D2:** Per-backend test green at ≤1e-13 vs paper-printed values; `shared/golden-vectors/cooley-tukey-1965-n8.json` committed with full citation in the JSON metadata block.

### §3.3 D3 — IEEE-754 corner cases

**Catalog (no textbook needed; IEEE-754 spec is the reference):**

| Test ID | Input pattern | Expected output behavior |
|---|---|---|
| IEEE-01 | All-zero input (1.0 = the impulse moved out) | DFT output: all zeros (no NaN, no -0.0 propagation in the wrong direction) |
| IEEE-02 | Single denormal (smallest subnormal at index 0) | DFT output: all values are denormal magnitude or zero; no NaN/Inf |
| IEEE-03 | `+0.0` vs `-0.0` distinction | DFT preserves IEEE-754 zero-sign in the imaginary part of the DC component (verifies kernel doesn't convert -0 → +0 via add-then-subtract) |
| IEEE-04 | NaN injected at one index | NaN propagates to ALL output indices (FFT is a linear combination of all inputs) — verify no silent NaN-to-zero conversion |
| IEEE-05 | +Inf at one index | Output has Inf or NaN at every index, never silently saturated to a finite max |
| IEEE-06 | Mix of +Inf and -Inf | Output: NaN at indices where Inf + (-Inf) cancellation would occur per the butterfly; finite-or-Inf elsewhere |
| IEEE-07 | Underflow accumulation | Repeated FFT of underflowing-magnitude input does not produce spurious values (verifies sub-normal handling in the multiply step) |

**Implementation.** Single test program per backend, ~7 sub-tests. Use the backend's native NaN/Inf construction (Fortran: `ieee_value`; C++: `std::numeric_limits<double>::quiet_NaN()`, etc.). Assertion-driver pattern matches existing test programs.

**Acceptance gate D3:** 7/7 sub-tests green per backend; `shared/ieee754-corners/dft.md` authored documenting each test's purpose + IEEE-754 §X reference.

### §3.4 D4 — Empirical O(N log N) complexity audit

**Test program per backend** (`complexity_audit.f90`, `complexity_audit.cpp`, etc.) that:
1. Runs FFT at N = 2^6, 2^7, ..., 2^16 (11 sizes)
2. For each N, runs FFT 5 times, takes the median wall-clock time
3. Outputs a CSV: `N, log10(N), log10(N log N), median_time_s, log10(time)`
4. Performs a linear regression of `log10(time)` vs `log10(N log N)`
5. Asserts slope ∈ [0.9, 1.1] (target 1.0 for O(N log N))
6. Writes the regression coefficients + fit residual to `_audit/complexity-audit-<backend>-<date>.md`

**CI workflow.** `.github/workflows/nightly-complexity.yml` triggered by `schedule: - cron: '0 3 * * *'` (3 AM UTC nightly). Runs the audit per backend; uploads the audit doc as an artifact; fails the workflow run if slope drifts out of band. Posts a PR comment on next push summarising drift.

**Acceptance gate D4:** Workflow runs successfully on a manual `workflow_dispatch`; slope for Fortran ∈ [0.9, 1.1]; same for C++; audit doc generated and human-readable.

**Note for Pascal landing (later):** When Pascal lands in v0.2.x, the same workflow extends to include Pascal — one new job, copy-paste of the Fortran job with `gfortran` → `fpc`. The workflow is structured to make this trivial.

### §3.5 D5 — Cross-backend bit-identity CI assertion

**Test program** `tests/cross_backend/test_bit_identity.py` (Python harness, since this is a cross-language comparison best done outside any one backend) that:
1. Invokes each hand-rolled backend's CLI with the same canonical input set (use the existing 6 golden vectors as the input set — they already exist)
2. Captures each backend's output to bit-precision (read the JSON output as IEEE-754 hex representation, not just decimal)
3. Asserts pairwise hex-identity across the hand-rolled matrix:
   - Fortran vs C++: hex-identical for every element of every golden output
   - Pascal vs Fortran (when Pascal lands): hex-identical
   - (NOT vs Python oracle — Python uses NumPy which has its own butterfly order; this is the algorithmic-factor exemption.)
4. Where hex-identity fails, output ULP-distance per element and assert ≤ 1 ULP × sqrt(N).

**CI workflow.** `.github/workflows/cross-backend.yml`, path-filtered to fire when any backend's kernel changes. Runs on every push that touches `backends/**/src/*` or `backends/**/include/*` or `tests/cross_backend/*`.

**Acceptance gate D5:** 6 golden vectors × Fortran-vs-C++ pair = 6 comparisons, all hex-identical (this is the v0.2.0 finding promoted to CI). Workflow runs green on baseline commit; deliberately introduces a 1-line change in one backend (e.g., reorder two adds) and verifies workflow goes red.

### §3.6 C3 side-quest — per-routine textbook citations + grep audit

During D1, you will be touching kernel routine headers anyway. Promote every public routine in `backends/fortran/src/*.f90` and `backends/cpp/src/*.cpp` to carry the citation pattern specified in `_config/LEGE-ARTIS-LANGUAGE-DOCTRINE-v0.1.md` §4.4 C3:

```
! Iterative DIT Cooley-Tukey FFT.
! Reference: Press et al. (2007) Numerical Recipes 3rd ed §12.2,
!            eq. 12.2.2 (decimation-in-time recurrence).
! Sign convention: forward = exp(-2*pi*i*k*n/N), per §12.1 standard.
! Complexity: O(N log N), verified empirically per C4 audit.
subroutine fft1d_inplace(a, nlen)
```

Authored allowlist: `_audit/textbook-citations-allowlist.yaml` listing routine name → expected citation pattern. Grep-audit script: `scripts/audit-citations.sh` that scans `backends/*/src/*.{f90,cpp,pas}` for public routines and verifies each carries a citation matching the allowlist.

CI wires the grep audit as a pre-build step in each backend's workflow (`.github/workflows/fortran.yml`, etc.).

**Acceptance gate C3 side-quest:** Every public routine in Fortran + C++ backends has a citation header; grep audit script returns clean; CI fails when a citation is removed.

---

## §4. Acceptance gates (rollup)

| Gate | Pass condition | Tag at green |
|---|---|---|
| D1 + C3 side-quest | 6 textbook examples green per backend; all kernel routines cited; grep audit clean | `v0.0.X-d1-textbook-verbatim-green` |
| D2 | Cooley-Tukey 1965 example green per backend | `v0.0.X-d2-cooley-tukey-1965-green` |
| D3 | 7/7 IEEE-754 corners green per backend | `v0.0.X-d3-ieee754-corners-green` |
| D4 | Nightly workflow runs green; slope in band; audit doc human-readable | `v0.0.X-d4-complexity-audit-green` |
| D5 | Pairwise hex-identity across hand-rolled matrix; red on deliberate drift | `v0.0.X-d5-bit-identity-ci-green` |
| **Rollup** | All 5 gates green for Fortran + C++; Pascal scaffold ready (tests + workflows extend to Pascal trivially when port lands) | **`v0.2.1`** with RELEASE-NOTES-v0.2.1.md authored mirroring v0.2.0 |

---

## §5. Out of scope

- **Pascal backend implementation** — handled separately in `_handoffs/macbook-v0.2.x-weekend/JOB-2-FOURIER-V0.2-PASCAL.md`. The testbed expansion here is **forward-compatible** with Pascal (the test programs are per-backend so Pascal port adds its own copy when it lands).
- **Rust backend implementation** — queued for v0.2.2; same forward-compatibility.
- **Translations** of any text into CS / JA / DE / IT — v0.1.1+ workstream.
- **Stage 5 performance flags** — D4 measures complexity at clarity-flag build to verify the algorithm IS O(N log N); Stage 5 will re-measure at perf-flag build to characterise constant-factor performance. Stage 5 is gated v0.5+ and not in scope here.
- **Shad-tier chapters** — separate workstream.
- **GW-solver-project** — parallel project; do not touch.

---

## §6. References (citations the brief itself uses)

- Press, W. H., Flannery, B. P., Teukolsky, S. A., & Vetterling, W. T. (1986). *Numerical Recipes in Pascal: The Art of Scientific Computing*. Cambridge University Press. — Pascal pedagogical anchor.
- Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007). *Numerical Recipes: The Art of Scientific Computing*, 3rd ed. Cambridge University Press. — modern Fortran + C++ anchor.
- Cooley, J. W., & Tukey, J. W. (1965). An algorithm for the machine calculation of complex Fourier series. *Math. Comp.*, 19(90), 297–301. — algorithmic origin anchor.
- IEEE Std 754-2019, *IEEE Standard for Floating-Point Arithmetic*. — corner-case behavior reference.
- Higham, N. J. (2002). *Accuracy and Stability of Numerical Algorithms*, 2nd ed. SIAM. §4.2 — sqrt(N) accumulated-rounding scaling.
- `_config/LEGE-ARTIS-LANGUAGE-DOCTRINE-v0.1.md` §4.4 — the C1–C4 contract.

---

## §7. STATUS report template

At end of work, author `_handoffs/v0.2.x-testbed-expansion-c1-c4/STATUS-REPORT-FILLED.md` with:

1. Per-deliverable D1..D5 status (PASS / PARTIAL / BLOCKED) + commit hashes for each green checkpoint
2. C3 side-quest status: routines audited, allowlist entries authored, grep audit wired
3. Tag-at-green log: which tags lit when, on which commits
4. Cross-backend bit-identity report: the actual hex-identity table for the 6 golden vectors × (Fortran, C++)
5. Complexity audit baseline: the regression coefficients + residuals for Fortran + C++ at the v0.2.1 baseline
6. Blockers / open questions for v0.2.2 (when Pascal lands, when Rust lands)
7. RELEASE-NOTES-v0.2.1.md authored, ready for Pete's review

---

*End of SONNET-BRIEF.md — fourier v0.2.x testbed-expansion-c1-c4.*
*Apply to `lege-artis/fourier` Fortran + C++ backends at v0.2.0 baseline.*
*Pascal/Rust ports inherit the patterns when they land in v0.2.2+.*
