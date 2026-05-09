# Fourier Foundations — working spec — v0.2 (EN)

> **Predecessor.** `FOURIER-FOUNDATIONS-PROJECT-SEED-v0.1-EN.md` (2026-05-08).
> v0.1 = scope + architecture sketch + literature shortlist + smallest-viable cut.
> **This v0.2.** Promotes seed to working spec: locks the methodological frame
> (top-down, contrast to Bouračka), wires the MI-M-T pattern-import map, and
> phases the §6 decision questions into research / model / review / implement
> stages of the 3-fold-path.
>
> **Author.** Pete Y. with Cowork/Opus assist, 2026-05-09.
> **Repo target.** `github.com/petr-yamyang/fourier-foundations` (planned).
> **Audience.** Pete (project owner), future MI-M-T contributors, OSS community
> evaluating MI-M-T as a methodology pilot.

---

## §1. Methodological frame — top-down by design

Fourier-Foundations and Bouračka are **siblings under MI-M-T** but they
**face the methodology from opposite ends**, and that is intentional:

| Axis | Bouračka case (calibration) | Fourier case (validation) |
|---|---|---|
| Direction of inquiry | bottom-up | top-down |
| Starting evidence | live SUT, screenshots, browser DOM, network captures | mathematical definition (Cooley-Tukey 1965, Stein-Shakarchi rigorous text) |
| Discovery technique | reverse engineering — observe → infer model → derive tests | derivation — define math → specify algorithm → derive tests |
| Testing posture | empirical first, model second | model first, empirical second (against canonical reference values) |
| Drift surface | runtime environment (reCAPTCHA scores, server-side feature flags) | numerical precision (rounding, IEEE-754 edge cases, language-runtime float semantics) |
| Reference truth | recon-derived screen flow + ČKP analytical doc | high-precision Wolfram/Mathematica/SciPy golden vectors + theorems with proofs |
| Failure mode | regression of UI / API behaviour | regression of numerical accuracy or convergence rate |
| What "green" means | TC executes without unexpected SKIP/FAIL on Cíl-1/2/3/4 | output matches golden vector within ε for chosen precision; properties (Plancherel, linearity, unitarity) hold |

This contrast is the **point** of having Fourier as the second pilot. MI-M-T
patterns that survive both directions are robust; patterns that only work in
one direction are revealed as method-specific accidents. v0.2 of this spec
makes that contrast a **first-class concept**, not a side note.

---

## §2. The 3-fold-path — research / model / review-refine / implement

Pete's guideline (paraphrased, 2026-05-09): *"imports new elements for
referencing, research of resources and modelling first, review and refine and
than implement as a part of 3-fold-path"*.

Reading this as a four-stage gated workflow, with the **3-fold-path =
Fortran / C++ / Rust parallel implementation** sitting in the final stage:

```
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 1 — REFERENCE                                                   │
│  Collect canonical sources (literature §4 of v0.1), pin specific       │
│  editions / equation numbers. Produce shared/reference-bibliography.bib│
│  and shared/canonical-equations/ (LaTeX-quality + code-block dual).    │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 2 — MODEL                                                       │
│  Author docs/canonical/ tier first — definitions, theorems, proofs,    │
│  complexity statements, precision claims. Engineer-tier ("for          │
│  dummies") follows derivation but stays consistent. NO CODE YET.       │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 3 — REVIEW & REFINE                                             │
│  Cross-check model against literature; produce golden vectors via      │
│  SciPy/Wolfram (independent reference, NOT the project's own code).    │
│  Write property-test specifications (Plancherel, linearity, etc.).     │
│  Open OQ / BUG entries for any model gaps. Iterate until canonical     │
│  doc + golden vectors + property specs are mutually consistent.        │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────────────┐
│  Stage 4 — IMPLEMENT (3-fold-path, parallel tracks)                    │
│   Track F  — Fortran (reference, slow + correct)                       │
│   Track C  — C++ (performance, vectorizable)                           │
│   Track R  — Rust (experimental, ownership-safety)                     │
│  Each track passes the SAME golden-vector + property tests before      │
│  merge. Cross-language equivalence test runs all three and compares.   │
└────────────────────────────────────────────────────────────────────────┘
```

The contrast with Bouračka: there, Stage 4 came first (we ran the SUT and
recorded what happened), and Stages 1-3 were partially reconstructed from
recon. For Fourier, Stages 1-3 are completed before Stage 4 starts. That is
what "top-down with some external testing inputs" means in operational terms.

---

## §3. MI-M-T pattern-import map

What patterns from Bouračka are imported into Fourier, what is adapted, and
what is new (Fourier-specific):

### §3.1 Imported as-is

| Pattern | Bouračka usage | Fourier usage |
|---|---|---|
| YAML issue log (BUG-/INFO-/OQ-) | embedded in SESSION-CLOSE doc | embedded in CHANGELOG.md or `_status/CURRENT.md` |
| R-CONFIRM-1 (independent observers same conclusion) | Selenium 5P/5S confirms drift guard | Wolfram + SciPy + manual hand-derive same golden vector before locking |
| R-PACKAGE-1 (TestCasePackage / TestCase split) | TC-CP-* organised under `cypress/e2e/aN-...` | `tests/algorithm/` + `tests/property/` + `tests/cross-language/` |
| R-DECOUPLED-1 (4-track versioning: schema/content/toolchain/release) | Excel TestPlan v0.4.2 + .gitignore versioning | algorithm-spec / golden-vectors / language-impl / release |
| R-DESIGN-1 reframed (phased coverage gating) | Cíl 1 / 2 / 3 / 4 progression | v0.1.0 → v0.2.0 → v0.5.0 → v1.0.0 milestones |
| Pre-ship audit pattern | `tools/preship_audit.py` IOC + ext blocklist | binary signing + sha256 manifest + GPG signature on releases |
| Cross-framework parity | Playwright ↔ Cypress ↔ Selenium | Fortran ↔ C++ ↔ Rust |
| Drift guard | `/error/timeout` URL polling for reCAPTCHA-v3 | precision-regression check against pinned golden vectors |
| Fixture sharing | YAML in `fixtures/test-data/` + per-framework loader | JSON in `shared/golden-vectors/` + per-language loader |

### §3.2 Adapted for Fourier specifics

| Pattern | Adaptation |
|---|---|
| TestTarget catalogue | TT-ALGO-{DFT,FFT,PSF} × TT-PRECISION-{single,double,quad} × TT-LANG-{F,C,R} × TT-PROP-{Plancherel,Linearity,Unitarity,Convergence} |
| Coverage rule | algorithm × input-class × precision × language must reach every cell of the matrix at v1.0.0 — earlier releases gated by "must reach DFT × {sine,cosine,square} × double × Fortran" |
| Email-deliverability rules | OSS public repo loosens the constraints, but pre-ship audit lives on as hash + signature manifest in each release tag |
| Excel TestPlan workbook | replaced with simpler JSON catalogue at `_status/test-plan.json` (TestPlan-as-data; no Excel) |
| Drift recon notes | `_status/drift-NN-CS-or-EN.md` — but content is "precision drift across compiler / runtime versions" |

### §3.3 Fourier-specific (new patterns)

| Pattern | What it is |
|---|---|
| Cross-language equivalence test | runs all 3 language tracks, compares output element-wise within ε; ε is precision-tier dependent |
| Convergence-rate tests | for partial-sum algorithm, asserts rate matches theoretical expectation for known smooth / discontinuous functions (PSF on triangle wave converges as O(1/n²); on square wave, O(1/n)) |
| Numerical-precision regression | each release tag pins a `precision-baseline.json`; new release must not regress per algorithm × input |
| Two-tier documentation consistency | canonical-tier and engineer-tier are independently authored, then cross-checked by a "consistency lint" — no contradictions, both tiers cite same equation IDs from `shared/canonical-equations/` |

These three patterns are candidates to **export back into Bouračka /
MI-M-T core** if they prove their worth.

---

## §4. Decisions — locking §6 of v0.1

| Q | v0.1 question | v0.2 decision | Rationale |
|---|---|---|---|
| Q-FFP-1 | License | **Apache 2.0** | patent grant; OSS-friendly; matches MI-M-T anticipated mimt-* repos |
| Q-FFP-2 | C++ or C# for performance tier | **C++17 first; C# deferred to v0.3+** | C++ is industry baseline for numerical libs; C# can be added later as a parallel track if community demand materialises |
| Q-FFP-3 | Fortran standard | **Fortran 2018** | broad compiler support (gfortran ≥ 8, ifort, ifx); covers `iso_fortran_env` quad-precision via `selected_real_kind` |
| Q-FFP-4 | Rust crate deps | **`num-complex` allowed** | reinventing complex arithmetic in Rust adds risk without scientific value; pin minor version; document in `Cargo.toml` |
| Q-FFP-5 | Canonical references locked | confirm v0.1 §4 list; ADD: Trefethen, "Spectral Methods in MATLAB" (SIAM 2000); ADD: Wikipedia citation policy = "starting reference, never single-source" | Trefethen for spectral derivation; Wikipedia caveat per academic norm |
| Q-FFP-6 | Microservice protocol | **REST first, gRPC deferred** | REST = lower bar for MI-M-T case-study; matches Bouračka's HTTP-only SUT shape so testing patterns transfer cleanly |
| Q-FFP-7 | GPU phase | **strictly v0.5+** | distract risk for weekend kickoff; pin as stretch in CHANGELOG |
| Q-FFP-8 | Doc format | **Markdown for both tiers; LaTeX inline for math via `$...$` and `$$...$$`** | renders correctly on GitHub; no Sphinx dependency |
| Q-FFP-9 | CI | **GitHub Actions; per-language matrix; cross-language equivalence as final job** | matches what Pete's other MI-M-T repos use |
| Q-FFP-10 | First ship cut | **v0.1.0 = DFT in Fortran + 5 golden vectors + canonical doc + engineer quick-start + LICENSE + README** | as v0.1 §8 specified — un-changed |

All ten questions resolved as of v0.2. Re-opening any of them requires a v0.3
of this spec with rationale.

---

## §5. v0.1.0 weekend deliverable — checkpoint definition

Reframed from v0.1 §8 with explicit checkpoints (each checkpoint is
mergeable to repo `main`, each carries a `precision-baseline.json` snapshot,
each carries a manifest sha256):

| Checkpoint | Deliverable | Stage | Done means |
|---|---|---|---|
| C-1 | Repo bootstrap | — | `fourier-foundations/` exists on GitHub with README, LICENSE, .gitignore, CHANGELOG.md, `_status/` dir; first commit tagged `v0.0.0-bootstrap` |
| C-2 | Reference bibliography | Stage 1 | `shared/reference-bibliography.bib` with all v0.1 §4 sources; `shared/canonical-equations/dft.tex` with the textbook equation in LaTeX + a code-block translation |
| C-3 | DFT canonical doc | Stage 2 | `docs/canonical/01-dft-definition.md` — definition, complexity statement, precision claim, citation keys to bibliography |
| C-4 | DFT engineer doc | Stage 2 | `docs/engineer/01-what-dft-actually-computes.md` — plain-English, worked length-4 example, "why does this take O(N²)?" intuition |
| C-5 | Golden vectors (length 2, 4, 8, 16, 64) | Stage 3 | `shared/golden-vectors/dft_n=*.json` produced via SciPy `numpy.fft.fft` at default double precision; each JSON includes input + output + ε used + python script that produced it (audit trail) |
| C-6 | Property-test spec | Stage 3 | `shared/property-tests/dft.md` — list of properties (Plancherel, linearity, DC component, Nyquist symmetry) with mathematical statement + tolerance per precision tier |
| C-7 | Fortran DFT impl | Stage 4 / Track F | `fortran/src/dft_kernel.f90` ~50 LoC; passes the 5 golden vectors; passes the 4 property tests; Makefile uses `gfortran -O0 -fcheck=all -Wall` |
| C-8 | Fortran tests + CI | Stage 4 / Track F | `fortran/tests/test_*.f90`; GitHub Actions workflow `ci/fortran.yml` runs them on push |
| C-9 | Tag v0.1.0 | release | annotated tag `v0.1.0`; release notes link to docs/canonical, docs/engineer, golden-vectors, test report; `precision-baseline.json` pinned |

Effort estimate revised: **6-8 hours** (originally 4-6h; v0.2 adds the
explicit canonical/engineer doc tier as gated checkpoints, +2h).

C++ and Rust tracks land in v0.2.0 onward; cross-language equivalence test
becomes meaningful at v0.2.0.

---

## §6. Failure-mode catalogue (preventive, before code is written)

Top-down methodology lets us pre-enumerate likely failure modes rather than
discover them post-hoc. v0.2 spec records these so they can be made into
tests in Stage 3:

| Code | Failure mode | Detection |
|---|---|---|
| FM-PREC-1 | Single-precision DFT loses energy on long input N>4096 | Plancherel test with relaxed ε for single-precision tier; explicit-fail at double-precision tier |
| FM-PREC-2 | Roundoff in twiddle factors makes FFT diverge from DFT for large N | cross-algorithm equivalence test: FFT(x) - DFT(x) max-abs < ε(N) where ε scales as O(log N · eps_machine) |
| FM-CONV-1 | Partial-sum at function discontinuity exhibits Gibbs phenomenon (~9% overshoot) | document as expected behaviour in canonical doc; test that overshoot is bounded, not absent |
| FM-LANG-1 | Language-runtime float-semantic difference (e.g., FMA contraction) causes cross-language drift > ε | per-language CI sets `-ffp-contract=off` (gcc), `/fp:strict` (msvc), `-Cstrict-fp` (rust) for reference builds |
| FM-INPUT-1 | Non-power-of-2 length N silently routed to slow DFT instead of FFT | API contract: `fft(x)` with len(x) ∉ powers-of-2 raises explicit error in v0.1, falls back to mixed-radix in v0.5 |
| FM-INPUT-2 | Empty input or length-1 input crashes | edge-case unit tests for N ∈ {0, 1, 2} |
| FM-SERVICE-1 | REST service returns NaN as JSON `null` silently | service-tier serialization audit; explicit error code for non-finite outputs |

This list expands during Stage 3.

---

## §7. Open questions (Pete to confirm before Stage 1 starts)

| OQ-FFP- | Question | Default if no decision |
|---|---|---|
| OQ-FFP-1 | Single-repo (one repo, three language subtrees) or repo-of-repos (one git submodule per language)? | single-repo, simpler ergonomics |
| OQ-FFP-2 | Czech-language engineer tier as separate `docs/engineer-cs/`? | yes, parallel to `docs/engineer/` (English) |
| OQ-FFP-3 | First Czech engineer-tier doc as part of v0.1.0 or deferred? | deferred to v0.1.1 |
| OQ-FFP-4 | "Service form" microservice land in v0.3 or v0.5? | v0.3 — keeps it close enough to MI-M-T case-study utility |
| OQ-FFP-5 | License acceptance for Apache 2.0 vs MIT — confirm? | Apache 2.0 |
| OQ-FFP-6 | Repo creation step: Pete creates manually on GitHub, or Cowork-assisted? | Pete creates manually (auth is his) |

---

## §8. Cross-references

- `FOURIER-FOUNDATIONS-PROJECT-SEED-v0.1-EN.md` — predecessor seed
- `bouracka-tests/_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md` — fixture-sharing pattern that becomes golden-vector-loader convention
- `bouracka-tests/_specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md` — parity pattern that becomes cross-language equivalence test
- `bouracka-tests/tools/preship_audit.py` — IOC scanner pattern; equivalent for Fourier = `tools/release_audit.py` (sha256 + GPG signature manifest)
- `bouracka-tests/SESSION-CLOSE-CP-SUPIN-05-2026-05-09-STATUS.md` — YAML issue-log embed pattern
- `mimt-governance/` (sibling repo, not yet public) — universal MI-M-T toolkit

---

## §11. Addendum 2026-05-09 — license & name-protection locked

**Supersedes Q-FFP-1 in §4.** v0.2 §4 listed Apache 2.0 with a thin rationale ("matches anticipated mimt-* repos"). After explicit license-vs-trademark separation analysis (Pete + Cowork-Opus, 2026-05-09), the decision stack below is now the locked reference. Any subsequent revisit requires a v0.3 of this spec with rationale.

### §11.1 Decision stack

| Layer | Decision | Rationale |
|---|---|---|
| Code license | **Apache 2.0** | (a) permissive — matches academic + hacker community reach; (b) explicit patent grant — matters for MI-M-T-adjacent methodology patterns potentially patentable; (c) §6 anti-endorsement clause — first line of defence against name abuse; (d) §7 AS-IS / NO WARRANTY — no fork can claim Pete endorses corrupted derivatives; (e) does NOT close §3.3-of-v0.1 GPU-oracle use case (proprietary CUDA/HIP/Metal vendors can use Fourier output as correctness oracle). |
| Documentation license | **CC-BY-SA-4.0** | Standard for prose: requires attribution, requires derivatives stay under same license. Applies to `docs/canonical/`, `docs/engineer/`, eventual "Fourier's story" essay. Lives in `LICENSE-DOCS`. |
| Name protection | **`TRADEMARK.md` + `NOTICE`** at repo root | Declarative statement that "MIM2000™", "Improwave™", and the personal name "Petr Yamyang" may not be used to identify forked / modified / derivative software, services, or content without prior written permission. Reinforces Apache 2.0 §6. Full legal enforceability requires CZ + EU trademark registration (separate sub-task, ~€850-1500 per mark per class — coupled with mim2000.cz redesign for evidence-of-use purposes). |
| Voluntary funding | `.github/FUNDING.yml` + README badges | GitHub Sponsors + Patreon + PayPal.me. License-independent. Wire-up at C-1 (repo bootstrap checkpoint, §5). |
| Sibling MI-M-T repos | **Apache 2.0** (same family) | Free tier of eventual MI-M-T commercial product is Apache 2.0; paid tier lives in separate proprietary repo with EULA. Trademark "MI-M-T", "MIM2000" registered separately. |

### §11.2 Files added to v0.1.0 checkpoint cut

C-1 (repo bootstrap) gains four files beyond v0.2 §5 inventory:

| File | Content |
|---|---|
| `LICENSE` | full Apache 2.0 text (verbatim from apache.org) |
| `LICENSE-DOCS` | full CC-BY-SA-4.0 text (verbatim from creativecommons.org) |
| `NOTICE` | required Apache 2.0 NOTICE file: copyright holder name, year, project name; reference to TRADEMARK.md |
| `TRADEMARK.md` | declaration as §10.1 above; explicit non-licensing of MIM2000™ / Improwave™ / Petr Yamyang names |
| `.github/FUNDING.yml` | GitHub Sponsors + Patreon URLs (Pete to populate handles before first push) |

### §11.3 What this does NOT decide

- Which CZ + EU trademark classes to register MIM2000™ / Improwave™ under — separate sub-task, coupled with mim2000.cz redesign timeline.
- Whether the "Fourier's story" essay also lands under CC-BY-SA-4.0 or under a CC-BY-NC-SA-4.0 (non-commercial) variant — defer to when essay outline is drafted.
- Commercial-tier MI-M-T EULA structure — separate sub-track, not in this spec's scope.
- Whether to require a Contributor License Agreement (CLA) for community PRs — defer to first community PR.

### §11.4 Risk register snapshot

| Risk | Mitigation |
|---|---|
| Apache 2.0 permits commercial wrapping without share-back | Accepted — community reach and adoption prioritised over commons enforcement; can revisit if abuse pattern emerges by switching new releases to MPL-2.0 (file-level copyleft preserves linking ability) |
| Name-abuse via fork claiming MIM2000 endorsement | Apache §6 + TRADEMARK.md declaration + (eventually) registered marks; cease-and-desist standing established at registration |
| Proprietary GPU vendor uses Fourier as oracle without acknowledgement | Apache 2.0 requires NOTICE file preservation in derivatives — gives standing to demand acknowledgement even in closed-source binaries |
| Community PR introduces incompatibly-licensed code | Defer CLA decision but require all PRs to declare license of any vendored code; CI lint can be added at v0.3+ |

### §11.5 Status

License decision stack locked 2026-05-09. Ready to materialise into `LICENSE`, `LICENSE-DOCS`, `NOTICE`, `TRADEMARK.md`, `.github/FUNDING.yml` at C-1 checkpoint (repo bootstrap, weekend Saturday morning).

---

## §9. Status

| Item | Hodnota |
|---|---|
| Doc | `FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` |
| Verze | v0.2 |
| Datum | 2026-05-09 |
| Audience | Pete (project owner), MI-M-T methodology pilot reviewers, OSS contributors |
| Predecessor | v0.1 seed (2026-05-08) |
| Methodology frame | top-down (contrast to Bouračka bottom-up) — locked §1 |
| Pattern-import map | locked §3 (35 patterns: 9 imported, 5 adapted, 4 new) |
| §6-of-v0.1 decisions | all 10 locked (§4 of this v0.2) |
| Open questions remaining | 6 (§7) — Pete confirms before Stage 1 |
| Next concrete action | Stage 1 — bibliography + canonical equations (~1.5h, weekend Saturday morning) |
| Status | working spec; ready for execution after OQ-FFP-1 through OQ-FFP-6 confirmation |
