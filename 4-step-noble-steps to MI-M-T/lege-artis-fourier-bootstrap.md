# lege-artis/fourier — bootstrap & kickoff plan

> **Trigger.** 2026-05-09 — Pete confirmed `lege-artis/fourier` as the canonical home for FFT/DFT/Partial-Sum reference implementation. Sibling to existing `kh-sim` (Kelvin-Helmholtz instability solver). Track 5 of OPUS-CYCLE v0.2 → v0.3 transition per `_config/CLAUDE-MD-DELTA-2026-05-09.md` Delta 3.
>
> **First content under `4-step-noble-steps to MI-M-T/`.** This folder was previously empty (held only an inspiration zip from 2026-04-26). The 4-step value chain — **Impulse → Test Set → Execution → Evidence** per OPUS-CYCLE §2.1 — applies to canonical-math projects too: Fourier is the second concrete worked example after kh-sim, and the first one positioned explicitly under the `lege-artis` org for academic / hacker community publication.
>
> **Master spec.** `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` (lives at SUPIN root provisionally; migrates to `lege-artis/fourier/_specs/WORKING-SPEC-v0.2-EN.md` at C-1 checkpoint per the migration plan).
>
> **Companion docs.** `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md` (operational walkthrough), `_config/CLAUDE-MD-DELTA-2026-05-09.md` (Delta 5 ADR-05 R-COVERAGE-ZERO).
>
> **Audience.** Pete (project owner + executor of bootstrap steps); future Cowork sessions on ThinkPad and MacBook implementing the weekend Stage 1; the eventual Sonnet session implementing Stage 4 tracks.

---

## §1. Why mirror the kh-sim pattern

`kh-sim` (currently at `petr-yamyang/kh-sim`, migrating to `lege-artis/kh-sim` per migration plan §3) has already validated the multi-backend canonical-math repo pattern. Its present structure is:

```
kh-sim/
├── README.md, LICENSE (MIT), CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, .gitignore
├── kh-sim.config.yaml
├── auth/
├── backends/
│   ├── fortran/      ← reference implementation (8/8 TCs PASS)
│   │   ├── src/
│   │   └── tests/
│   ├── cpp/          ← scaffolded
│   ├── rust/         ← scaffolded
│   └── pascal/       ← scaffolded
├── docker/
├── frontend/
├── log-service/
├── reference/
├── shared/
├── tests/
└── vhost/
```

**This is the proven pattern.** Reusing it means: same community-pack convention (LICENSE / CONTRIBUTING / CODE_OF_CONDUCT / SECURITY / .gitignore identical-shape), same `backends/<lang>/{src,tests}` layout, same shared/ for golden vectors and reference data, same multi-language test parity expectation. The Fourier weekend cut starts on solid empirical ground rather than inventing a layout from scratch.

**Differences for Fourier vs kh-sim:**

| Aspect | kh-sim | fourier (per WORKING-SPEC v0.2 + 2026-05-09 locks) |
|---|---|---|
| Subject matter | Single canonical PDE simulation (Kelvin-Helmholtz instability) | Three canonical algorithms (DFT, FFT, Partial-Sum of Fourier Series) |
| Backend languages | Fortran (8/8 PASS) + C++ + Rust + Pascal (4-language layout) | **v0.1.0:** Fortran reference only. **v0.2.0:** + C++ performance + Rust experimental + Pascal full-scale (mirrors kh-sim's 4-language commitment per Q3 lock 2026-05-09). |
| Test surface | Per-TC numerical correctness against reference values | Golden vectors + property tests (Plancherel, linearity, unitarity) + cross-language equivalence + convergence-rate |
| Reference precision | Machine epsilon for linear ops; 5% tolerance for nonlinear | Per-precision-tier ε (single / double / quad); convergence-rate matches theoretical O(1/n²) for smooth, O(1/n) for square-wave Gibbs |
| Two-tier docs | README + (deferred) academic write-up | **Mandatory canonical-tier + engineer-tier from day one** per shibboleth aesthetic |
| Canonical-equations format | n/a | **Dual-format per Q2 lock 2026-05-09:** `.md` with embedded LaTeX (`$..$`, `$$..$$`) for inline GitHub rendering + parallel `.tex` companion for proper math typesetting (MathJax/KaTeX/LaTeX→PDF). Both files per equation; the `.md` cites the `.tex` for downstream PDF rendering. |
| Central reference text | (project-internal) | **Numerical Recipes (Press, Teukolsky, Vetterling, Flannery)** elevated as central reference across all four language tracks. 2007 3rd ed for general FFT recipes + numerical pitfalls; 1986 Pascal edition is direct historical anchor for the Pascal track. |
| Service form | None planned | REST microservice form sketched in v0.1 §3.2 (deferred to v0.5+) |
| GPU bridge | None planned | Stretch goal for v0.5+ — proprietary GPU vendors as oracle consumers |
| License | MIT | Apache 2.0 (code) + CC-BY-SA-4.0 (docs) per WORKING-SPEC v0.2 §11 |

Both projects export the **`lege-artis` core principle**: the math comes first, the code is its faithful translation, both tiers of documentation prove the translation is honest. kh-sim demonstrated this for one PDE; Fourier demonstrates it for the three foundational discrete-time algorithms.

---

## §2. Bootstrap sequence (after GATE-PORT-1 closes)

Prerequisites:
- `lege-artis` GitHub org exists (per migration plan §2)
- `lege-artis/fourier` empty repo created on GitHub (per migration plan §4.1)
- ThinkPad has a clean working directory under `C:\Users\vitez\Documents\VibeCodeProjects\` for the new clone

### §2.1 Initial clone + community-pack mirror

```powershell
cd C:\Users\vitez\Documents\VibeCodeProjects
git clone https://github.com/lege-artis/fourier.git
cd fourier

# Mirror community-pack from kh-sim (review + adapt each file)
$kh = "C:\Users\vitez\Documents\VibeCodeProjects\kh-sim"
Copy-Item "$kh\.gitignore" .
Copy-Item "$kh\CODE_OF_CONDUCT.md" .
Copy-Item "$kh\CONTRIBUTING.md" .
Copy-Item "$kh\SECURITY.md" .
# LICENSE: kh-sim uses MIT, fourier uses Apache 2.0 — DO NOT copy LICENSE; fetch fresh:
# Browser: https://www.apache.org/licenses/LICENSE-2.0.txt → save as LICENSE
# README: kh-sim's README is project-specific — do not copy verbatim; author fresh from WORKING-SPEC v0.2 §1

# Add Fourier-specific licensing files:
# LICENSE-DOCS: full CC-BY-SA-4.0 text from creativecommons.org
# NOTICE: per Apache 2.0 convention
# TRADEMARK.md: name protection declaration

# Add scaffolding directory tree (mirrors kh-sim shape):
mkdir -Force `
    _specs, `
    backends, backends\fortran, backends\fortran\src, backends\fortran\tests, `
    backends\cpp, backends\cpp\src, backends\cpp\tests, `
    backends\rust, backends\rust\src, backends\rust\tests, `
    docs, docs\canonical, docs\engineer, `
    shared, shared\golden-vectors, shared\reference-bibliography, shared\input-fixtures, `
    ci, `
    services, `
    .github

# Migrate working spec from SUPIN/
cp ..\SUPIN\FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md _specs\WORKING-SPEC-v0.2-EN.md
# After successful migration, retire the SUPIN copy (move to SUPIN/archive/obsolete/migrated-to-lege-artis/)
```

### §2.2 First commit

```powershell
git add .
git commit -m "chore: initial bootstrap — community-pack from kh-sim pattern + working spec v0.2

* LICENSE Apache 2.0; LICENSE-DOCS CC-BY-SA-4.0; NOTICE; TRADEMARK.md per WORKING-SPEC §11
* Multi-backend layout mirrors kh-sim/backends/{fortran,cpp,rust} convention
* shared/ holds golden vectors + reference bibliography + input fixtures
* docs/{canonical,engineer} for two-tier shibboleth-aesthetic documentation
* services/ placeholder for the REST microservice form (deferred to v0.5+)
* _specs/WORKING-SPEC-v0.2-EN.md migrated from SUPIN/

References:
* SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md (master spec, retired in SUPIN after migration)
* _config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md
* _config/CLAUDE-MD-DELTA-2026-05-09.md (Track 5 entry)
* OPUS-CYCLE-v0.2-MASTER.md §2 (conceptual triple) + §7 (parallel tracks)
"

git push origin main
git tag -a v0.0.1-bootstrap -m "Bootstrap: community-pack + WORKING-SPEC v0.2"
git push origin v0.0.1-bootstrap
```

---

## §3. Stage 1 — Reference (bibliography + canonical equations)

Per WORKING-SPEC v0.2 §2 stage-1 spec. Estimated 1.5h on Saturday morning.

### §3.1 Bibliography

Author `shared/reference-bibliography/refs.bib` with the v0.2 §4 source list. **Order: alphabetical by citation key per academic standard (T3 lock 2026-05-09).** Each entry in BibTeX with `@book{...}` or `@article{...}`:

| Citation key | Source | Role |
|---|---|---|
| `Bracewell3rd` | Bracewell (2000), "The Fourier Transform and Its Applications" 3rd ed., McGraw-Hill | Continuous + discrete; engineer-friendly companion to Oppenheim-Schafer |
| `Cooley1965` | Cooley & Tukey (1965), "An Algorithm for the Machine Calculation of Complex Fourier Series", Math. Comp. 19, 297–301 | Original FFT paper — primary citation for any FFT theorem |
| `IEEE754_2019` | IEEE 754-2019 Standard for Floating-Point Arithmetic | Precision claims for single / double / quad-precision tiers across all language backends |
| `Korner1989` | Korner (1989), "Fourier Analysis", Cambridge UP | Rigorous mathematical foundation; convergence theorems |
| `NumRec3rd` | Press, Teukolsky, Vetterling, Flannery (2007), "Numerical Recipes" 3rd ed., Ch. 12 | **Central reference text** (per Q3 lock 2026-05-09); engineer-grade FFT recipes + numerical pitfalls; explicit code patterns referenced across all four backend tracks |
| `NumRecPascal1986` | Press, Flannery, Teukolsky, Vetterling (1986), "Numerical Recipes: The Art of Scientific Computing", Pascal edition, Cambridge UP | **Direct historical anchor for the Pascal backend track** (v0.2.0); ensures Pascal implementation respects the canonical-Pascal numerical-computing tradition rather than treating Pascal as a curiosity |
| `OppenheimSchafer3rd` | Oppenheim & Schafer (2009), "Discrete-Time Signal Processing" 3rd ed. | DSP standard textbook; DFT/FFT in §§8-9 |
| `SteinShakarchi2003` | Stein & Shakarchi (2003), "Fourier Analysis: An Introduction", Princeton | Modern undergraduate-grade rigor; bridge between Korner and applied texts |
| `Trefethen2000` | Trefethen (2000), "Spectral Methods in MATLAB", SIAM | Spectral derivation; cross-language portability of spectral kernels |

Used for citations in canonical-tier docs (`docs/canonical/*.md`) and equation-source attribution (`shared/canonical-equations/*.tex`). The `NumRec3rd` and `NumRecPascal1986` entries cross-reference each other as parallel editions of the same authoritative work.

### §3.2 Canonical equations

Author one **pair** of files per algorithm under `shared/canonical-equations/`. Per Q2 lock 2026-05-09 — dual-format honors WORKING-SPEC v0.2 §11.1 Q-FFP-8 Markdown decision while preserving canonical-tier rigor for power users:

| Pair | `.md` content (inline GitHub rendering) | `.tex` content (proper math typesetting) |
|---|---|---|
| `dft.{md,tex}` | DFT formula `$X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-2\pi i k n / N}$` with embedded math + array-semantics code-block + complexity statement + precision claim per IEEE 754 + citations to `OppenheimSchafer3rd` and `Bracewell3rd` | Same equation in proper LaTeX `\begin{equation}...\end{equation}` blocks; theorem-style precision-claim derivation; ready for MathJax/KaTeX/LaTeX→PDF rendering |
| `fft-cooley-tukey.{md,tex}` | Cooley-Tukey radix-2 derivation in Markdown + LaTeX inline; complexity `$O(N \log N)$`; twiddle-factor precision-propagation summary; citations to `Cooley1965` and `NumRec3rd` Ch. 12 | Full derivation as LaTeX theorem-proof structure; stated propagation theorem with proof; precision bound `$\varepsilon(N) = O(\log N \cdot \varepsilon_{\text{machine}})$` |
| `partial-sum.{md,tex}` | Partial sum of Fourier series formula in Markdown + LaTeX inline; Dirichlet, Fejér, Riemann-Lebesgue convergence statements; Gibbs phenomenon ~9% overshoot at discontinuities; citations to `Korner1989` and `SteinShakarchi2003` | Full convergence-theorem proofs (Dirichlet test, Fejér's theorem); Gibbs overshoot quantification with proof |

**Convention.** The `.md` file is the operational source — both doc tiers reference it. The `.tex` file is the academic-grade companion for downstream PDF rendering and proper math typesetting. Both files cite the same `refs.bib` keys. A consistency-lint pass (deferred to v0.2 of `lege-artis/coverage-algebra` or earlier) verifies the math content matches across both formats.

**Render targets** (deferred wiring; documented for design intent):
- `.md` files → GitHub-flavored Markdown with MathJax (renders inline at github.com/lege-artis/fourier file view)
- `.tex` files → Pandoc → PDF or LaTeX → PDF for academic citation use; rendered output not committed to repo, generated on demand
- Engineer-tier docs (`docs/engineer/*.md`) embed the `.md` equations via Markdown include
- Canonical-tier docs (`docs/canonical/*.md`) embed both: link to `.md` for live reference, link to `.tex` (or rendered PDF) for formal derivation

### §3.3 Stage 1 checkpoint (C-1 + C-2 per WORKING-SPEC v0.2 §5)

Stage 1 closes when:

- [ ] `shared/reference-bibliography/refs.bib` exists with all 8 sources properly formatted
- [ ] `shared/reference-bibliography/canonical-equations/{dft,fft-cooley-tukey,partial-sum}.tex` exist with LaTeX + code-block
- [ ] All citations in TBD canonical-tier docs resolve to refs.bib keys
- [ ] First commit landed: `chore: Stage 1 — bibliography + canonical equations`
- [ ] Tag `v0.0.2-stage1` pushed

---

## §4. Stage 2-4 sequencing

Per WORKING-SPEC v0.2 §2 + §5 checkpoint structure:

| Stage | Deliverable | Estimated effort | Owner |
|---|---|---|---|
| Stage 2 — Model | `docs/canonical/01-dft-definition.md` (canonical tier) + `docs/engineer/01-what-dft-actually-computes.md` (engineer tier). NO CODE YET. Both docs reference `shared/canonical-equations/dft.md` + `dft.tex` per Q2 dual-format. | 1.5h Saturday afternoon | Pete (authoring) + Cowork-Opus (consistency check between tiers) |
| Stage 3 — Review & Refine | Golden vectors via SciPy + Wolfram independent reference → `shared/golden-vectors/dft_n=*.json` (lengths 2, 4, 8, 16, 64). Property-test specs → `shared/property-tests/dft.md`. Round Zero coverage gate per ADR-05: zero un-explained orphans before Stage 4. | 1.5h Sunday morning | Pete (golden vector generation) + Cowork-Opus (Round Zero validation) |
| Stage 4 Track F — Implement Fortran | `backends/fortran/src/dft_kernel.f90` (~50 LoC) + tests passing all 5 golden vectors + 4 property tests; Makefile uses `gfortran -O0 -fcheck=all -Wall`. CI workflow `.github/workflows/fortran.yml` mirrors kh-sim's CI shape. References `NumRec3rd` Ch. 12 patterns. | 2h Sunday afternoon | Pete (initial implementation; or Sonnet session if Stage 3 closes cleanly per R-SONNET-1) |
| C-9 release tag | `v0.1.0` annotated tag with release notes linking docs/canonical, docs/engineer, golden vectors, test report, `precision-baseline.json` pinned | 0.5h | Pete |

**Stage 4 Tracks C, R, P (C++, Rust, Pascal)** land at **v0.2.0** per Q3 lock 2026-05-09 — each track adds its own `backends/<lang>/{src,tests}` and per-language CI workflow. Cross-language equivalence test becomes meaningful at v0.2.0 once at least two backends exist; full four-language equivalence matrix at v0.2.0 close.

**Pascal track specifics (v0.2.0):**
- `backends/pascal/src/dft_kernel.pas` and FFT + PSF equivalents
- Compiler target: Free Pascal Compiler (`fpc`) — same toolchain kh-sim uses for its `backends/pascal`
- Reference text for the track: **`NumRecPascal1986`** (Numerical Recipes Pascal edition) — direct historical anchor; ensures the implementation respects the canonical Pascal-numerical-computing tradition rather than treating Pascal as a curiosity
- Tests: pytest-compatible test runner same shape as Fortran track; per-Pascal-test invokes compiled binary and parses output

**Total v0.1.0 weekend cut effort:** ~6.5 hours per WORKING-SPEC v0.2 §5 (Fortran reference only; revised from §1 v0.1's 4-6h estimate to reflect dual doc tier explicit cost).

**Total v0.2.0 follow-on effort estimate:** ~12-16 hours across C++ + Rust + Pascal tracks (3-4h each backend Stage 4); cross-language equivalence test wiring + CI matrix per language ~2h additional. Spread across multiple sessions; Sonnet handoff strongly recommended for the per-backend grind work once Stage 3 closes (per R-SONNET-1).

---

## §5. Sonnet handoff trigger

Per R-SONNET-1 (OQ-PORT-6 lock 2026-05-09 — Sonnet for bounded grinding work where test surface, resources, and analytical questions are settled), Sonnet handoff for Fourier becomes appropriate **after Stage 3 closes**:

- Golden vectors locked
- Property-test specs locked
- Round Zero coverage audit returns green (zero un-explained orphans)
- All open analytical questions in WORKING-SPEC v0.2 §7 (OQ-FFP-1..6) are answered
- Acceptance criteria per backend track concrete and finite

At that point Stage 4 implementation across Fortran / C++ / Rust is exactly the bounded-grinding shape Sonnet handles well. Three tracks **could** even run as three Sonnet sessions if test-spec separation is clean — but pragmatically two parallel sessions (one ThinkPad, one MacBook) is the OPUS-CYCLE-defined pattern; the third track waits or runs sequentially.

Sonnet handoff prompt template: `_config/HANDOVER-V0.2-THINKPAD.md` (existing) or `_config/HANDOVER-V0.2-MACBOOK.md` (existing) — adapt with Fourier-specific master spec pointer (`lege-artis/fourier/_specs/WORKING-SPEC-v0.2-EN.md`) and acceptance criteria from this bootstrap doc §4.

---

## §6. mim2000.cz publication chain — sequencing reminder

Per Pete's 2026-05-09 sequencing decision (locked OQ-PORT-2/3): **mim2000.cz redesign + content/design uplift of all 3-fold-path FIRST**, then trademark filing, then Fourier publication chain activation. The Fourier code can ship to `lege-artis/fourier` independently — what waits is the LinkedIn / mim2000.cz / zemla.org cross-linking.

Sequence:
1. Fourier weekend cut → `lege-artis/fourier` v0.1.0 tag (this doc's §3-§4 covers this)
2. mim2000.cz redesign sub-project initiates (separate seed doc TBD)
3. mim2000.cz content covers Fourier as a project entry under `mim2000.cz/projects/`
4. zemla.org Physics section expansion adds the science-rigorous post about Fourier (with link back to lege-artis/fourier and to mim2000.cz)
5. LinkedIn portfolio entry mentions `lege-artis/fourier` as a worked reference
6. The "Fourier's story" essay (per WORKING-SPEC v0.1 §1.5) drafts after the publication chain is live, using accumulated session provenance as raw material

---

## §7. Status

| Item | Value |
|---|---|
| Doc | `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` |
| Version | v0.1 |
| Date | 2026-05-09 |
| Author | Cowork-Opus on ThinkPad |
| Pattern source | kh-sim multi-backend layout (validated per its 8/8 TCs PASS reference implementation) |
| Master spec | `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` (provisional location until Stage 1 migrates to `lege-artis/fourier/_specs/WORKING-SPEC-v0.2-EN.md`) |
| Blocked on | GATE-PORT-1 (`lege-artis` GitHub org creation by Pete — ~3 minutes manual UI action per migration plan §2) |
| Estimated unblock-to-v0.1.0 effort | ~6.5 hours of weekend authoring + ~5 minutes of Pete's bootstrap clicks + Sonnet session for Stage 4 if applicable |
| Status | Draft — ready to execute as soon as `lege-artis/fourier` exists on GitHub |

---

## §7b. Decisions locked 2026-05-09 (chat thread refinement)

The following decisions from CLAUDE-MD-DELTA-2026-05-09.md §10 directly affect this bootstrap doc:

| Lock | Effect on this doc |
|---|---|
| Q2 (canonical-equations dual-format) | §3.2 rewritten: `.md` + `.tex` companion per equation under `shared/canonical-equations/` |
| Q3 (Pascal as fourth language v0.2.0) | §1 differences table: Pascal added as fourth backend track. §4 sequencing: v0.2.0 includes Pascal alongside C++ and Rust. New "Pascal track specifics" subsection notes `NumRecPascal1986` as historical anchor. |
| Q4 (Pete runs script manually, split flow) | Migration plan §4.2 carries the Q4 note — this doc references the migration plan |
| T3 (alphabetical BibTeX) | §3.1 rewritten as alphabetical-by-key table; `NumRec3rd` and `NumRecPascal1986` cross-referenced |
| Numerical Recipes elevated as central reference | §3.1 marks `NumRec3rd` as "central reference text"; §3.2 cites `NumRec3rd` Ch. 12 in fft-cooley-tukey equation pair; §4 Track F + Pascal track specifics reference Numerical Recipes |

---

## §8. What this doc does NOT do

- Does not create the GitHub org or repo (those are Pete's manual UI actions per migration plan §2 + §4.1)
- Does not author the canonical-tier or engineer-tier docs themselves (Stage 2 work)
- Does not produce the golden vectors (Stage 3 work — needs SciPy + Wolfram independent reference)
- Does not write the Fortran DFT code (Stage 4 Track F — happens after Stage 3 closes)
- Does not write the cross-language equivalence test (Stage 4 v0.2.0 work, needs two backends)
- Does not draft the "Fourier's story" essay (waits until publication chain is live per §6)
- Does not migrate kh-sim from `petr-yamyang/kh-sim` (separate operation per migration plan §3)
- Does not bootstrap `lege-artis/mimt` (deferred to OPUS-CYCLE v0.2 → v0.3 transition per migration plan §5)

The above are explicit follow-ups; this doc is the bridge between WORKING-SPEC v0.2 and the actual repo on GitHub.
