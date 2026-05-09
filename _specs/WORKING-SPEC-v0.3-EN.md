# Fourier Foundations — working spec — v0.3 (EN)

> **Predecessor.** `WORKING-SPEC-v0.2-EN.md` (2026-05-09 morning, locked Apache 2.0 + CC-BY-SA-4.0 + TRADEMARK + Pascal v0.2.0 sequencing).
> **This v0.3** (2026-05-09 evening). Refines — does not rewrite. Seven locks per chat thread: implementation philosophy made explicit, Wikipedia removed from principal references, Thorne / Folland / Pinsky / Boyd / Strang / DiskretniFourierovaCS added, Stage 5 (Performance) added as gated stage, three doc tiers (canonical / engineer / performance), `shared/physics-testbeds/` directory introduced, language stack EN baseline → CS/JA/DE/IT v0.1.1+ documented.
>
> **Status of bootstrap.** `lege-artis/fourier` repo created on GitHub 2026-05-09; v0.0.1-bootstrap tag pushed via subtree from `VibeCodeProjects/fourier/`. Subtree-publish pattern empirically validated. Repo private until v0.1.0 release ceremony (shibboleth aesthetic — public sees canonical state).
>
> **Author.** Pete Y. + Cowork Opus on ThinkPad. **Audience.** Pete (project owner), future MI-M-T contributors, OSS community evaluating MI-M-T as methodology pilot.

---

## §1. Methodological frame — top-down by design (unchanged from v0.2)

Fourier-Foundations and Bouračka are **siblings under MI-M-T** but face the methodology from opposite ends, intentionally:

| Axis | Bouračka case (calibration) | Fourier case (validation) |
|---|---|---|
| Direction of inquiry | bottom-up | top-down |
| Starting evidence | live SUT, screenshots, browser DOM | mathematical definition (Cooley-Tukey 1965, Stein-Shakarchi rigorous text, Folland) |
| Discovery technique | reverse engineering | derivation |
| Testing posture | empirical first, model second | model first, empirical second (against canonical reference values from independent oracles) |
| Drift surface | runtime environment | numerical precision (rounding, IEEE-754 edge cases, FMA contraction, language-runtime float semantics) |
| Reference truth | recon-derived screen flow + ČKP analytical doc | high-precision SciPy / NumPy / Wolfram / FFTW outputs + theorems with proofs |
| Failure mode | regression of UI / API behaviour | regression of numerical accuracy or convergence rate |
| What "green" means | TC executes without unexpected SKIP/FAIL | output matches independent oracle within ε for chosen precision; properties (Plancherel, linearity, unitarity) hold; physical testbeds produce known answers |

Patterns that survive both directions are robust MI-M-T methodology; patterns that only work in one direction are revealed as method-specific accidents. This is the **point** of having Fourier as the second pilot.

---

## §2. The 3-stage authoring path → Stage 4 four-language implementation → Stage 5 optimization

**Lock 2026-05-09 evening:** what was four stages in v0.2 is now **five stages**. Stage 5 (Performance) is explicit and gated, not implicit.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 1 — REFERENCE (bibliography + canonical equations)              │
│  refs.bib + shared/canonical-equations/{dft,fft,psf}.{md,tex}          │
│  Wikipedia explicitly excluded. Thorne 2017 added as physics-testbed   │
│  source. Folland 1992 + Pinsky 2009 + Stein-Shakarchi as math canon.   │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 2 — MODEL (canonical-tier docs first, NO CODE)                  │
│  docs/canonical/en/01-dft-definition.md derives algorithm from         │
│  canonical-equations. Engineer-tier docs/engineer/en/ follows model.   │
│  Shibboleth aesthetic: math comes first, code is its faithful          │
│  translation.                                                          │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 3 — REVIEW & REFINE (golden vectors via independent oracles +   │
│  property-test specs + physics testbeds + R-COVERAGE-ZERO gate)        │
│  shared/golden-vectors/ JSONs from SciPy / NumPy / Wolfram / FFTW —    │
│  these are TESTBEDS, not source material. Multiple oracles per length  │
│  where possible (cross-check the cross-checkers).                      │
│  shared/physics-testbeds/ from Thorne 2017 (Fraunhofer diffraction,    │
│  heat-equation Green's function, harmonic oscillator spectrum).        │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 4 — IMPLEMENT (4-language parallel, FROM FIRST PRINCIPLES)      │
│  v0.1.0: Fortran reference only (DFT). Code derived directly from      │
│         §3.2 canonical equations. No porting NumPy / FFTW / etc.       │
│         The math comes first; code is its faithful translation;        │
│         line-by-line equation→code mapping verifiable in commit msg.   │
│  v0.2.0: + C++ + Rust + Pascal full-scale. Cross-language              │
│          equivalence test wires up.                                    │
│  Each track passes the SAME golden vectors + property tests + physics  │
│  testbeds before merge.                                                │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 5 — PERFORMANCE (gated by Stage 4 v0.1.0 closing green; v0.5+)  │
│  Profile, identify hot loops, apply optimizations: twiddle             │
│  pre-computation, vectorization hints, SIMD, mixed-radix when N is     │
│  not power-of-2, Bluestein for arbitrary N. Each optimization MUST     │
│  show no regression against the v0.1.0 golden vectors. Published as    │
│  separate doc tier: docs/performance/.                                 │
└────────────────────────────────────────────────────────────────────────┘
```

The discipline this encodes: nobody can rationalize "let me just borrow this fast Cooley-Tukey from FFTW" — that violates the first-principles requirement and undermines the proof-of-correctness story. **Optimizations have a separate gate**; canonical reference clears its own gate first.

---

## §3. Reference catalogue — refs.bib content for Stage 1 (revised v0.3)

**Drop:** Wikipedia entries (any). Per Pete's directive 2026-05-09: Wikipedia is at most a sanity check, never an authority. Not in `refs.bib`.

**Authoritative `refs.bib` for v0.3** (alphabetical by citation key, academic standard):

| Key | Source | Role |
|---|---|---|
| `Boyd2001` | Boyd (2001), *Chebyshev and Fourier Spectral Methods*, Dover. Free PDF available from author's site. | Spectral-methods classic; bridges Fourier with adjacent function-approximation classes. **Referential** (not principal). |
| `Bracewell3rd` | Bracewell (2000), *The Fourier Transform and Its Applications*, 3rd ed., McGraw-Hill | Engineer-friendly companion to Oppenheim-Schafer. Continuous + discrete. |
| `Cooley1965` | Cooley & Tukey (1965), "An Algorithm for the Machine Calculation of Complex Fourier Series", Math. Comp. 19, 297–301 | Original FFT paper — primary citation for any FFT theorem. |
| `DiskretniFourierovaCS` | "Diskrétní Fourierova transformace a její použití" (Czech-language reference, OL3874116M) | **CS doc-tier reference** (terminology check + Czech mathematical conventions) when CS seeders ship in v0.1.1+. |
| `Folland1992` | Folland (1992), *Fourier Analysis and Its Applications*, Wadsworth | **Second canonical math reference (locked v0.3 2026-05-09).** Bridges Korner's pure-math rigor with Bracewell's applied register. Theorem-proof structure at advanced-undergraduate / first-graduate level. |
| `IEEE754_2019` | IEEE 754-2019 Standard for Floating-Point Arithmetic | Precision claims for single / double / quad-precision tiers across all four backend tracks. |
| `Korner1989` | Korner (1989), *Fourier Analysis*, Cambridge UP | Rigorous mathematical foundation; convergence theorems with proofs. |
| `NumRec3rd` | Press, Teukolsky, Vetterling, Flannery (2007), *Numerical Recipes*, 3rd ed., Ch. 12 | **Implementation + coding-standard golden reference** (per Pete's lock 2026-05-09). Engineer-grade FFT recipes + numerical pitfalls. |
| `NumRecPascal1986` | Press et al. (1986), *Numerical Recipes: The Art of Scientific Computing*, Pascal edition, Cambridge UP | **Direct historical anchor for the Pascal backend track** (v0.2.0). Ensures Pascal implementation respects canonical Pascal-numerical-computing tradition. |
| `OppenheimSchafer3rd` | Oppenheim & Schafer (2009), *Discrete-Time Signal Processing*, 3rd ed. | DSP textbook standard; DFT/FFT in §§8-9. |
| `Pinsky2009` | Pinsky (2009), *Introduction to Fourier Analysis and Wavelets*, AMS | **Modern cross-check** (locked v0.3) against Folland 1992. Explicit attention to numerical aspects; useful if we ever extend to wavelets. |
| `SteinShakarchi2003` | Stein & Shakarchi (2003), *Fourier Analysis: An Introduction*, Princeton | Modern undergraduate-grade rigor; bridge between Korner and applied texts. |
| `Strang1986` | Strang (1986), *Introduction to Applied Mathematics*, Wellesley-Cambridge | Applied-mathematics framing of FFT with worked examples. **Referential** (backup if Folland feels too dense). |
| `Thorne2017` | Thorne & Blandford (2017), *Modern Classical Physics*, Princeton | **Physics-side testcase source (locked v0.3 2026-05-09).** Heat equation, wave propagation, statistical mechanics, optics — all use Fourier methods extensively, with worked examples we can reproduce as physics testbeds. |
| `Trefethen2000` | Trefethen (2000), *Spectral Methods in MATLAB*, SIAM | Spectral derivation; cross-language portability of spectral kernels. |

**Tier classification within refs.bib:**

- **Principal** (cited directly in canonical-tier proofs): `Cooley1965`, `Folland1992`, `Korner1989`, `NumRec3rd`, `OppenheimSchafer3rd`, `Pinsky2009`, `SteinShakarchi2003`, `Thorne2017`, `IEEE754_2019`
- **Referential** (cited as alternative perspectives or secondary sources): `Boyd2001`, `Bracewell3rd`, `Strang1986`, `Trefethen2000`
- **Track-specific anchors:** `NumRecPascal1986` (Pascal track), `DiskretniFourierovaCS` (CS doc tier)

**Open: Japanese canonical reference (OQ-FFP-7-JA).** Four candidates carried forward, none chosen; defer to v0.1.1 when CS / JA / DE / IT seeders ship:

| Candidate | Why considered | Limitation |
|---|---|---|
| 岩波書店 (Iwanami Shoten) "現代数学への入門" Fourier volume | Standard Japanese-undergraduate Fourier text; well-vetted | Need to verify which exact volume / author / edition |
| Tatsumi Tsuneo (辰巳常男) Fourier-analysis textbooks for engineering programs | Engineering register; matches lege-artis tone | Specific title / availability TBD |
| Ohishi Shinichi (大石進一) numerical Fourier methods + rigorous numerics | Rigorous-numerics angle complements canonical proofs | More specialised than introductory; may not be the *canonical* slot |
| Direct Japanese translation of Bracewell / Numerical Recipes | Authoritative content | Translation rather than originally-Japanese authoring weakens "canonical Japanese" role |

**Open: German canonical (OQ-FFP-7-DE).** Forster's *Analysis* series (esp. *Analysis 3*) likely candidate; defer to v0.1.1.

**Open: Italian canonical (OQ-FFP-7-IT).** No specific candidate yet; defer to v0.1.1.

---

## §4. Implementation philosophy (NEW §, locked v0.3)

> **Three-line summary.** Math first, code second, optimization third. Independent oracles serve as testbeds, never as source material. Documentation mirrors this discipline through three doc tiers (canonical / engineer / performance).

### §4.1 First-principles requirement

Every algorithm in `lege-artis/fourier` is implemented from the canonical mathematical equation, not by porting a reference implementation. The chain must be verifiable:

```
shared/canonical-equations/dft.tex
        ↓ (faithful translation, line-by-line equation→code mapping)
backends/fortran/src/dft_kernel.f90
```

**Stage 4 commit-message convention.** Every Stage 4 implementation commit must include the equation→code mapping in the commit body:

```
feat(fortran): DFT kernel from canonical equation §3.2

Equation: X[k] = Σ_{n=0}^{N-1} x[n] · exp(-2πi·k·n/N)
Code:
  do k = 0, N-1
     X(k) = (0.0_dp, 0.0_dp)
     do n = 0, N-1
        omega = -2.0_dp * pi * real(k*n, dp) / real(N, dp)
        X(k) = X(k) + x(n) * cmplx(cos(omega), sin(omega), kind=dp)
     end do
  end do

Reference: shared/canonical-equations/dft.tex eq. (3); refs.bib OppenheimSchafer3rd §8.2.
```

The discipline: anyone reading the commit can verify the code is a faithful translation of the cited equation. No magic; no borrowed implementations.

### §4.2 Independent oracles as testbeds

Stage 3 (Review & Refine) produces `shared/golden-vectors/dft_n=*.json` populated from **independent reference implementations**:

| Oracle | Role | Output captured |
|---|---|---|
| SciPy `numpy.fft.fft` | Primary oracle (most accessible, well-tested) | Default-precision (double) outputs for sine, cosine, square, sawtooth, gaussian, ramp, impulse inputs at lengths 2, 4, 8, 16, 64, 1024 |
| NumPy `numpy.fft.fft` | Cross-check against SciPy (they SHOULD agree exactly) | Same input set; diff vs SciPy must be at machine epsilon |
| Wolfram `Fourier` (Mathematica or WolframAlpha) | High-precision oracle for short lengths | Lengths 2, 4, 8 at extended precision; serves as ground truth for the SciPy/NumPy outputs |
| FFTW (when `lege-artis/fourier` matures) | Performance-grade oracle | Used in Stage 5 to validate optimizations don't drift |

Each golden-vector JSON includes the producing oracle in metadata + the producing script (audit trail). When two oracles disagree, the disagreement itself is documented — usually it's a small ε (~ machine epsilon), occasionally it's a known precision difference (Wolfram exact vs SciPy double), never a wild divergence.

**The oracles are testbeds.** Our implementation's job is to match them within ε, not to copy them.

### §4.3 Canonical-then-optimization discipline

Stage 4 closes when Fortran reference passes all golden vectors + property tests + physics testbeds. **Only then** does Stage 5 begin. Each Stage 5 optimization carries:

- A specific perf claim (e.g. "2× speedup on N=1024 via twiddle pre-computation")
- A benchmark run (`backends/fortran/benchmarks/`) showing the claim
- A regression test confirming all v0.1.0 golden vectors still pass
- A commit message linking the optimization to its mathematical justification (no code-only optimizations; the math has to support what the code now does)

This makes "fast incorrect code" structurally impossible — the gate is canonical correctness first, every time.

### §4.4 What this discipline rules out

- Porting FFTW / Numpy / Eigen / etc. into our `backends/<lang>/src/` — never. References, yes; ports, no.
- "Optimizing" before Stage 4 closes — never. Stage 5 is gated.
- Skipping the equation→code mapping in commit messages — never. The chain has to be verifiable.
- Treating golden vectors as ground truth without naming the oracle — never. Multiple oracles, named, cross-checked.

### §4.5 Documentation must mirror this approach

Three doc tiers, each with a different angle on the same content:

| Tier | Audience | Content style | Where it lives |
|---|---|---|---|
| **Canonical** | Mathematician, academic reviewer, contributor wanting to understand why | Theorems with proofs; cite primary sources; LaTeX-quality math; derives the algorithm from first principles | `docs/canonical/<lang>/` — EN baseline at v0.1.0; CS / JA / DE / IT seeders v0.1.1+ |
| **Engineer** | Practitioner using the library, hobbyist, student approaching from coding side | "What does this compute? Here's the code. Here's a worked example. Here's how to use it" — minimal formal notation | `docs/engineer/<lang>/` — same language schedule as canonical |
| **Performance** | Performance engineer optimizing, advanced user picking between variants | Each optimization explained with before/after benchmark, math justification, regression-test reference | `docs/performance/<lang>/` — added in Stage 5 (v0.5+); EN-only initially |

The tiers cite each other but don't duplicate content. Engineer-tier links to canonical-tier for "why does this work?"; performance-tier links to engineer-tier for "what is this code doing?".

---

## §5. v0.1.0 weekend cut — checkpoints (revised v0.3)

Reframed from v0.2 §5 to reflect the implementation philosophy. Same C-1 through C-9 structure with explicit oracle attribution.

| Checkpoint | Deliverable | Stage | Done means |
|---|---|---|---|
| C-1 | Repo bootstrap | — | DONE — v0.0.1-bootstrap tag pushed to `lege-artis/fourier` 2026-05-09 evening (private). 11 files committed, subtree-publish pattern validated. |
| C-2 | `refs.bib` (15 sources alphabetical, no Wikipedia) + bibliography README | Stage 1 | All 13 confirmed-locked sources + 2 deferred (`*JA`, `*DE`) entries present. Pinsky / Folland / Thorne entries verified against actual books in Pete's library. |
| C-3 | Canonical equations (3 algorithms × 2 formats = 6 files) | Stage 1 | `shared/canonical-equations/{dft,fft,psf}.{md,tex}` exist. Each `.md` cites refs.bib keys; each `.tex` ready for MathJax/KaTeX/PDF rendering. Consistency-lint deferred to v0.2 of canonical-equations module. |
| C-4 | Canonical-tier doc — DFT chapter | Stage 2 | `docs/canonical/en/01-dft-definition.md` derives DFT formula from first principles, cites Cooley1965 + Folland1992 + Pinsky2009. Equation→code mapping outlined in §X.X but no code yet. |
| C-5 | Engineer-tier doc — DFT chapter | Stage 2 | `docs/engineer/en/01-what-dft-actually-computes.md` plain-English worked example, length-4 by hand, complexity intuition; references the canonical-tier doc for "why." |
| C-6 | Golden vectors from independent oracles | Stage 3 | `shared/golden-vectors/dft_n={2,4,8,16,64}.json` from SciPy + NumPy + Wolfram (where applicable). Each JSON metadata names oracle + producing script + ε used. Cross-oracle disagreement documented if any. |
| C-7 | Property-test spec for DFT | Stage 3 | `shared/property-tests/dft.md` — Plancherel, linearity, DC component, Nyquist symmetry properties stated with mathematical content + tolerance per precision tier. |
| C-7b NEW | Physics testbeds spec | Stage 3 | `shared/physics-testbeds/dft.md` — Fraunhofer diffraction pattern (DFT of single-slit aperture), heat-equation Green's function (FFT of impulse), simple harmonic oscillator spectrum. Each cites `Thorne2017` chapter + analytical expected answer. |
| C-8 | Round Zero coverage gate | Stage 3 | R-COVERAGE-ZERO audit returns green: zero un-explained orphans across Reqs (mathematical properties from C-3) × TT (algorithm × precision × language × property × physics-testbed) × TC (golden-vector + property + physics testbeds from C-6/C-7/C-7b). |
| C-9 | Fortran DFT implementation | Stage 4 | `backends/fortran/src/dft_kernel.f90` derived line-by-line from canonical equation per §4.1 commit-message convention. Passes all 5 golden vectors + 4 property tests + 3 physics testbeds. Makefile uses `gfortran -O0 -fcheck=all -Wall`. CI workflow `.github/workflows/fortran.yml` mirrors kh-sim CI shape. |
| C-10 | v0.1.0 release tag | Release | Annotated tag `v0.1.0` with release notes linking docs/canonical/en, docs/engineer/en, golden vectors, test report, `precision-baseline.json` pinned. Repo flips from PRIVATE to PUBLIC at this moment per shibboleth aesthetic ceremony. |

**Effort estimate revised v0.3:** ~7-9 hours total (v0.2 was 6.5h; +0.5-2.5h for the physics-testbeds track addition + the explicit oracle-attribution discipline, which adds rigor at a small time cost).

---

## §6. Stage 5 — Performance (NEW §, locked v0.3)

Activated **only after** v0.1.0 ships green. v0.5.x release branch.

### §6.1 Stage 5 work types

| Type | What it changes | Validation |
|---|---|---|
| Twiddle pre-computation | Compute exp(-2πi·k·n/N) once, lookup at runtime | Same golden vectors pass; benchmark shows speedup |
| Vectorization (SIMD) | Use compiler intrinsics or auto-vectorization hints | Same golden vectors pass; benchmark shows speedup vs unvectorized baseline |
| Mixed-radix FFT | Handle N as product of small primes (radix-2, 3, 5) | Property tests for non-power-of-2 lengths pass; new golden vectors at N=12, 60, 360 |
| Bluestein's algorithm | Handle arbitrary N via convolution | Property tests for prime N pass (N=7, 11, 13, 257) |
| GPU bridge (v0.5+ stretch) | CUDA/HIP/Metal kernel that mirrors canonical Fortran | Cross-platform golden vectors pass; benchmark vs cuFFT for sanity |

### §6.2 Stage 5 documentation

`docs/performance/en/<optimization-id>.md` per optimization. Schema:

```
## <opt-id> — <short title>
- **Mathematical justification:** which property of the canonical algorithm makes this optimization sound (cite canonical-tier)
- **Before:** baseline benchmark (operations / second @ N=1024 per language)
- **After:** optimized benchmark
- **Speedup:** ratio
- **Regression-test reference:** all v0.1.0 golden vectors pass; specific test name
- **Trade-offs:** memory cost, code complexity, edge cases
- **Recommended use:** when this optimization is worth adopting
```

### §6.3 Performance-tier ships English-only initially

CS / JA / DE / IT translations of canonical and engineer tiers come at v0.1.1+. Performance tier does not ship language seeders until v0.6+ — practitioner audience reads English natively, the audience overlap with multilingual readers is small, the work-cost is high.

---

## §7. Repository layout (revised v0.3)

```
fourier/
├── README.md
├── LICENSE              ← Apache 2.0
├── LICENSE-DOCS         ← CC-BY-SA-4.0
├── NOTICE
├── TRADEMARK.md
├── .gitignore
├── .github/FUNDING.yml
├── _specs/
│   ├── WORKING-SPEC-v0.3-EN.md  ← THIS FILE; v0.2 retained as historical
│   └── WORKING-SPEC-v0.2-EN.md  ← historical
├── shared/
│   ├── reference-bibliography/
│   │   └── refs.bib             ← Stage 1 deliverable (15 sources)
│   ├── canonical-equations/
│   │   ├── dft.md               ← Stage 1 deliverable; .md inline-LaTeX
│   │   ├── dft.tex              ← Stage 1 deliverable; .tex companion
│   │   ├── fft-cooley-tukey.{md,tex}
│   │   └── partial-sum.{md,tex}
│   ├── golden-vectors/          ← Stage 3 deliverable
│   │   └── dft_n={2,4,8,16,64}.json   (from SciPy / NumPy / Wolfram)
│   ├── property-tests/          ← Stage 3 deliverable
│   │   └── dft.md
│   ├── physics-testbeds/        ← Stage 3 deliverable (NEW v0.3)
│   │   └── dft.md               (Fraunhofer + heat-eq + harmonic osc per Thorne2017)
│   └── input-fixtures/          ← test signals (sine, cosine, …)
├── docs/
│   ├── canonical/
│   │   ├── en/                  ← Stage 2 deliverable for v0.1.0; baseline
│   │   ├── cs/                  ← v0.1.1+ (DiskretniFourierovaCS terminology)
│   │   ├── ja/                  ← v0.1.1+ (OQ-FFP-7-JA pending choice)
│   │   ├── de/                  ← v0.1.1+ (OQ-FFP-7-DE pending choice)
│   │   └── it/                  ← v0.1.1+ (OQ-FFP-7-IT pending choice)
│   ├── engineer/
│   │   └── (same per-language structure)
│   └── performance/             ← Stage 5 deliverable (v0.5+)
│       └── en/                  ← English-only at first
├── backends/
│   ├── fortran/                 ← reference (v0.1.0)
│   │   ├── src/                 ← Stage 4 deliverable
│   │   ├── tests/
│   │   └── benchmarks/          ← Stage 5 (v0.5+)
│   ├── cpp/                     ← scaffolded (v0.2.0)
│   ├── rust/                    ← scaffolded (v0.2.0)
│   └── pascal/                  ← scaffolded (v0.2.0); NumRecPascal1986 anchor
├── ci/
│   └── (per-backend CI workflows)
└── services/                    ← v0.5+ (REST microservice form)
```

---

## §8. Failure-mode catalogue (extended v0.3)

| Code | Failure mode | Detection |
|---|---|---|
| FM-PREC-1 | Single-precision DFT loses energy on long input N>4096 | Plancherel test with relaxed ε for single-precision tier |
| FM-PREC-2 | Roundoff in twiddle factors makes FFT diverge from DFT for large N | Cross-algorithm equivalence test: FFT(x) - DFT(x) max-abs < ε(N) where ε scales as O(log N · eps_machine) |
| FM-CONV-1 | Partial-sum at function discontinuity exhibits Gibbs phenomenon (~9% overshoot) | Documented as expected behaviour; test that overshoot is bounded, not absent |
| FM-LANG-1 | Language-runtime float-semantic difference (FMA contraction) → cross-language drift > ε | Per-language CI sets `-ffp-contract=off` (gcc), `/fp:strict` (msvc), `-Cstrict-fp` (rust) for reference builds |
| FM-INPUT-1 | Non-power-of-2 length N silently routed to slow DFT instead of FFT | API contract: `fft(x)` with len(x) ∉ powers-of-2 raises explicit error in v0.1; falls back to mixed-radix in Stage 5 (v0.5+) |
| FM-INPUT-2 | Empty input or length-1 input crashes | Edge-case unit tests for N ∈ {0, 1, 2} |
| FM-SERVICE-1 | REST service returns NaN as JSON `null` silently | Service-tier serialization audit; explicit error code for non-finite outputs |
| **FM-DISCIPLINE-1** (NEW v0.3) | **Stage 4 implementation borrowed from external library instead of derived from canonical equation** | Code review of Stage 4 commit messages: each must contain the equation→code mapping per §4.1. CI lint script (Stage 4 v0.1.1+) parses commit message for the required structure. |
| **FM-DISCIPLINE-2** (NEW v0.3) | **Stage 5 optimization shipped before Stage 4 v0.1.0 closing green** | Branch protection rule on `v0.1.0` tag: no Stage 5 merges to main until v0.1.0 tagged. Operational discipline + CI gate. |
| **FM-ORACLE-1** (NEW v0.3) | **Single-oracle golden vectors used without cross-check** | Stage 3 deliverable C-6 requires multiple-oracle agreement when >1 oracle available. Single-oracle vectors flagged as `single_oracle: true` in JSON metadata for transparency. |

---

## §9. Open questions (revised v0.3)

| OQ-FFP- | Question | Default if no answer | Status |
|---|---|---|---|
| OQ-FFP-1 | Single-repo or repo-of-repos? | Single-repo | **DECIDED** v0.3 — single-repo (current `lege-artis/fourier` layout); repo-of-repos rejected as fragmenting. |
| OQ-FFP-2 | Czech engineer tier as separate `docs/engineer-cs/`? | Yes, parallel to `docs/engineer/en/` | **DECIDED** v0.3 — under `docs/{canonical,engineer}/cs/` per repo layout §7. |
| OQ-FFP-3 | First Czech engineer-tier doc as part of v0.1.0 or deferred? | Deferred to v0.1.1 | **DECIDED** v0.3 — v0.1.0 ships EN baseline only; CS/JA/DE/IT seeders v0.1.1+. |
| OQ-FFP-4 | Service form (REST microservice) v0.3 or v0.5? | v0.5+ | **DECIDED** v0.3 — Stage 5 / v0.5+ explicit; not pre-v0.5. |
| OQ-FFP-5 | License Apache 2.0 confirmed? | Yes | **DECIDED** v0.2 §11 — confirmed 2026-05-09. |
| OQ-FFP-6 | Repo creation by Pete or Cowork? | Pete | **DECIDED** v0.2 — Pete created `lege-artis/fourier` 2026-05-09 evening. |
| **OQ-FFP-7-JA** (NEW) | Japanese canonical reference | Defer to v0.1.1; 4-candidate shortlist in §3 | **OPEN** — Pete to pick from Iwanami / Tatsumi / Ohishi / translation by v0.1.1. |
| **OQ-FFP-7-DE** (NEW) | German canonical reference | Defer to v0.1.1; Forster *Analysis 3* candidate | **OPEN** — confirm Forster or alternative by v0.1.1. |
| **OQ-FFP-7-IT** (NEW) | Italian canonical reference | Defer to v0.1.1; no candidate yet | **OPEN** — research needed by v0.1.1. |
| **OQ-FFP-8** (NEW v0.3) | Equation→code mapping enforcement — manual review or CI lint? | Manual through v0.1.0; CI lint added v0.1.1+ when commit-message corpus is large enough to template | **OPEN** — operational decision deferred. |
| **OQ-FFP-9** (NEW v0.3) | Stage 5 release-branch model — separate `v0.5-perf` branch or main with feature gates? | TBD when first Stage 5 work begins | **OPEN** — defer to Stage 5 entry. |

---

## §10. Risk register (extended v0.3)

| Risk | Mitigation |
|---|---|
| Apache 2.0 permits commercial wrapping without share-back | Accepted (v0.2 §11.4) |
| Name-abuse via fork claiming MIM2000 endorsement | Apache §6 + TRADEMARK.md + future CZ/EU registration |
| Proprietary GPU vendor uses Fourier as oracle without acknowledgement | Apache 2.0 NOTICE preservation gives standing |
| Community PR introduces incompatibly-licensed code | CLA decision deferred; PR template requires license-of-vendored-code declaration |
| **Stage 4 implementation copied from external library** (NEW v0.3) | §4.1 commit-message convention + future CI lint per OQ-FFP-8 |
| **Stage 5 optimization regresses canonical correctness** (NEW v0.3) | Each optimization runs the v0.1.0 golden-vector regression test as gate; CI fails the merge if any vector drifts |
| **Wrong oracle used as testbed** (NEW v0.3) | Multiple-oracle cross-check at Stage 3 C-6; FM-ORACLE-1 detection at golden-vector authoring time |
| **Language-track lag — Pascal track stalls behind Fortran/C++/Rust** (NEW v0.3) | Pascal track is v0.2.0 scope, not v0.1.0; if it lags v0.2.0, ship v0.2.0 with Fortran+C+++Rust and slot Pascal at v0.2.1 |

---

## §11. Status and amendment log (revised v0.3)

| Item | Value |
|---|---|
| Doc | `_specs/WORKING-SPEC-v0.3-EN.md` |
| Version | v0.3 (refines v0.2; v0.2 retained as historical) |
| Date | 2026-05-09 evening |
| Author | Pete Y. + Cowork-Opus on ThinkPad |
| Predecessor | v0.2 (license + Pascal seq) |
| Empirical bootstrap | v0.0.1-bootstrap tag on `lege-artis/fourier` (private), pushed via `git subtree push --prefix=fourier lege-artis-fourier main` from VibeCodeProjects monorepo |
| Stage 1 readiness | UNBLOCKED — refs.bib + canonical-equations authoring is next concrete work |
| Open questions | 5 active (OQ-FFP-7-JA, 7-DE, 7-IT, 8, 9); 6 decided (OQ-FFP-1..6) |
| Status | **READY for Stage 1 execution.** Bibliography + canonical equations authoring can begin. |

### §11.1 v0.2 → v0.3 changelog

| Lock | Section affected | Change |
|---|---|---|
| Wikipedia removed from refs | §3 | Dropped from `refs.bib`; sanity-check role only, never authority |
| Thorne 2017 added | §3 | Physics-side testbed source; new §C-7b deliverable |
| Folland 1992 added | §3 | Second canonical math reference (locked) |
| Pinsky 2009 added | §3 | Modern cross-check against Folland |
| Boyd 2001 + Strang 1986 added | §3 | Referential / referential-backup tier |
| DiskretniFourierovaCS added | §3 | CS doc-tier reference (v0.1.1+) |
| JA / DE / IT canonical refs deferred | §3, §9 | OQ-FFP-7-JA / -DE / -IT carried as open |
| Implementation philosophy explicit | §4 (NEW) | First principles + golden-as-testbed + canonical-then-optimization |
| Stage 5 (Performance) explicit | §6 (NEW) | Gated by Stage 4 v0.1.0 closing green |
| Three doc tiers (canonical / engineer / performance) | §4.5, §7 | Performance tier added; English-only initially |
| `shared/physics-testbeds/` directory | §7 | New under `shared/` |
| Documentation language stack EN baseline → CS/JA/DE/IT | §7, §9 | EN ships v0.1.0; others v0.1.1+ |
| Failure modes FM-DISCIPLINE-1, FM-DISCIPLINE-2, FM-ORACLE-1 | §8 | New entries enforcing the philosophy |
| Risk register entries for stage-discipline + oracle-discipline | §10 | New entries |

### §11.2 What this v0.3 does NOT do

- Does not author refs.bib content itself (that's Stage 1 deliverable C-2)
- Does not author canonical-equations files (Stage 1 deliverables C-3 onwards)
- Does not pick Japanese / German / Italian canonical references (OQ-FFP-7-* remain open)
- Does not create the `shared/physics-testbeds/` content (Stage 3 deliverable C-7b)
- Does not finalise Stage 5 release-branch model (OQ-FFP-9 remains open)
- Does not choose between manual review and CI lint for equation→code mapping (OQ-FFP-8 remains open)

These are explicit follow-ups; this v0.3 is the bridge between v0.2 and the actual Stage 1 work.

---

## §12. Next concrete action

**FOURIER-S1.1** — Author `shared/reference-bibliography/refs.bib` with the 13 confirmed-locked sources from §3 in alphabetical-by-citation-key BibTeX format. Estimated ~30 min once Pete confirms physical access to all citation details (volume, edition, ISBN, year, publisher) for each source. Pete's library has Thorne 2017; Folland 1992 + Pinsky 2009 may need acquisition or library checkout.

**FOURIER-S1.2** — Author `shared/canonical-equations/dft.{md,tex}` deriving the DFT formula from first principles, citing refs.bib keys, in dual format. Estimated ~45 min.

**FOURIER-S1.3** — Author `shared/canonical-equations/fft-cooley-tukey.{md,tex}` and `shared/canonical-equations/partial-sum.{md,tex}` analogously. Estimated ~75 min combined.

**Stage 1 closure (target):** Saturday morning, ~2.5 hours total.

After Stage 1 closes: Stage 2 (Model — canonical-tier and engineer-tier docs for DFT) Saturday afternoon ~1.5h. Stage 3 (Review & Refine — golden vectors + property tests + physics testbeds) Sunday morning ~2h. Stage 4 (Implement Fortran reference) Sunday afternoon ~2h. Tag v0.1.0 Sunday evening, repo flips PRIVATE → PUBLIC.

**Total weekend cut estimate:** ~7-9 hours, distributed across Saturday + Sunday.

---

*End of WORKING-SPEC-v0.3-EN.md.*
