# JOB-3 — Performance + noisy / poorly-structured / multidim data — scoping spike

**Status:** Exploratory. Deliverable is a **decision document** + a small POC, NOT a production code rollout.
**Estimated effort:** 2-4 hours.
**Acceptance gate:** the ADR at §6 is committed, with all sections filled in defensibly. POC numbers are reproducible.

---

## §0. Why this job is different from JOB-1 + JOB-2

JOB-1 and JOB-2 are **execution jobs** — known scope, known acceptance criteria, well-bounded effort.

JOB-3 is a **scoping spike**. The question Pete is asking — *"what does a performance-tuned next round look like for multidim / noisy / poorly-structured data?"* — has at least four legitimate answers, and the wrong one is expensive to walk back from. The deliverable is a written architecture-decision document, the kind that informs the v0.5+ Stage 5 work properly, instead of jumping to code that locks in an answer prematurely.

---

## §1. The question Pete is asking, decomposed

"Performance-tuned second round of C++ (or other choice which would provide high performance for multidimensional highly-noised or poorly-structured data)" decomposes into three orthogonal questions:

| Question | What it's really asking | Where the answer lives |
|----------|-------------------------|------------------------|
| **Q1 — language/runtime choice for perf** | Will C++ -O3 with proper vectorization beat the alternatives, or is there a runtime (Julia, Rust, modern Fortran) that wins on the actual workload? | Stage 5 perf-build sequencing |
| **Q2 — multidim DFT support** | 2D / 3D DFT for images, volumetric data, MRI/seismic. Implementation pattern: row-then-column 1D vs. native 2D, FFTW vs. in-house, memory layout | new working-spec section + new backends/* sub-track |
| **Q3 — robustness for noisy / poorly-structured data** | Preprocessing pipeline: windowing strategy, detrending, outlier rejection, segmentation/Welch averaging, robust spectral estimation | Shad-tier B7 capstone scope + a `tools/robust-spectral/` library |

**These three are NOT the same thing.** Conflating them is exactly the trap this job exists to avoid. Q1 is a build/toolchain question. Q2 is a math/API expansion. Q3 is a methodology question that has very little to do with the FFT itself and everything to do with what you feed it.

---

## §2. Deliverable shape — the ADR

Produce a single decision document at:

```
fourier/_specs/ADR-001-PERF-NOISY-MULTIDIM-v0.1.md
```

Format follows the Architecture Decision Record convention (Michael Nygard / Joel Parker Henderson style):

```
# ADR-001 — Performance + noisy/multidim data direction for v0.3+

## Status
Proposed (2026-05-1X)

## Context
[~200 words: what the current state is (Fortran ref + C++ ref + Pascal ref at v0.2.1),
 what use-cases are pushing this question, what Stage 5 already gates]

## Decision drivers
[5-8 bullet points, e.g. "must preserve bit-identity cross-language baseline for ref builds",
 "must not break the published v0.2.x API contract",
 "Shad-tier B7 capstone needs methodology answers",
 "MI-M-T case-study testbeds will be the first real consumers of multidim"]

## Considered options
- **Q1 options:** (a) C++ + FFTW3, (b) C++ + handwritten SIMD intrinsics, (c) Julia + FFTW.jl, (d) Modern Fortran 2018 + OpenMP, (e) Rust + rustfft
- **Q2 options:** (i) 1D primitives composed externally (row-then-column), (ii) native N-dim API in each backend, (iii) thin wrapper over FFTW's nd interface
- **Q3 options:** (A) Build robust preprocessing as part of fourier/, (B) Build as separate sibling lege-artis/spectral-toolkit, (C) Document the recipes in Shad-tier B7 + leave implementation to consumers

For each option: 3-5 bullets on pros / cons / cost / risk.

## Decision
[Pete's recommended path forward. The doc records the recommendation; Pete confirms or
 overrides on next ThinkPad session.]

## Consequences
[What we commit to. What we explicitly don't. What follow-up work this unblocks.]

## Compliance with project principles
[How the choice respects: Apache-2.0 license stack, no-third-party-deps reference rule,
 Stage 5 gating, cross-language baseline match property]
```

---

## §3. Small POC to validate the recommendation

After the ADR is drafted, build the **minimum POC needed to make its numbers defensible**. The POC is not production code — it's evidence. Suggested shape:

**POC-1 (perf upper bound):** time the current Fortran reference + the current C++ reference on N = {128, 1024, 16384, 65536} complex inputs. Report `microseconds per DFT` for each. **No** changes to the kernels — measure what we have, baseline first.

**POC-2 (perf candidate):** compile the C++ kernel ONCE with `-O3 -march=native -ffast-math` (note: `-ffast-math` would break bit-reproducibility, so this is **a separate non-reference build** for perf comparison ONLY — clearly labelled). Time on the same N values. Report speedup factor.

**POC-3 (multidim row-then-column):** implement a 32×32 complex 2D DFT in Python (NumPy) using two calls to the Pascal/C++/Fortran kernel via subprocess — verify it produces the same result as `np.fft.fft2`. This proves the row-then-column composition works without needing native 2D in the backends.

**POC-4 (noisy-data preprocessing):** generate a synthetic vibration signal (mimic B3) + add 30% outlier-noise + 200%-of-fundamental DC drift. Apply (a) raw FFT, (b) Hann-windowed FFT after detrending, (c) Welch PSD with 8 segments. Plot all three spectra side-by-side. Show that the "robust" pipeline recovers the diagnostic peaks the raw FFT loses.

**Store POC artifacts at:**
```
fourier/_specs/adr-001-poc/
├── poc-1-perf-baseline.{md,py}
├── poc-2-perf-cpp-fast.{md,py}     (note: NOT in backends/cpp/ — this is a perf-only experiment)
├── poc-3-row-then-column.{md,py}
└── poc-4-robust-preprocessing.{md,py,png × 3}
```

Each POC sub-doc is ~50-100 words + a measurement table or a figure. Total POC size: ~1 hour of work after the ADR is drafted.

---

## §4. Out of scope (parking lot)

To keep this spike from sprawling:

- **No** actual implementation of FFTW integration or native 2D DFT in the v0.2.x backends. Those are v0.3+ work, gated by the ADR's decision.
- **No** Julia / Rust comparative builds. Q1 candidates are *named* in the ADR but not benchmarked beyond C++ vs. Fortran in POC-1/2 (the existing reference builds). Pete decides whether to commission additional comparative builds after reading the ADR.
- **No** Stage 5 perf gates revision. WORKING-SPEC §"Stage 5 gated v0.5+" stays as-is until Pete explicitly rewrites it.
- **No** API additions to v0.2.x backends. v0.2.1 ships with the current API; v0.3 is when API expansion happens (gated by ADR-001 confirming the API surface).

---

## §5. Done criteria

- [ ] `fourier/_specs/ADR-001-PERF-NOISY-MULTIDIM-v0.1.md` exists, all template sections filled in, Pete's recommendation explicit
- [ ] `fourier/_specs/adr-001-poc/` has 4 POC sub-folders with reproducible scripts + measured numbers
- [ ] POC-1 + POC-2 timing tables present + comparable (same machine, same N values)
- [ ] POC-3 demonstrates row-then-column 2D DFT agrees with `np.fft.fft2` to < 1e-13
- [ ] POC-4 produces 3 spectrum plots showing the diagnostic-recovery progression
- [ ] ADR §"Decision" section reads as an executive-ready recommendation: someone who reads only that section + §"Consequences" can act on it
- [ ] Pre-flight sanitization grep clean per MASTER-BRIEF §5
- [ ] Commit message: `docs(adr): ADR-001 perf + noisy + multidim direction (recommendation + POCs)`

---

## §6. The decision template — copy this verbatim

```markdown
## Decision

After weighing the options in §2, the recommended direction for the v0.3+ line is:

**Q1 (language/runtime for perf):** [your choice]
  Rationale: [2-4 sentences]

**Q2 (multidim DFT support):** [your choice]
  Rationale: [2-4 sentences]

**Q3 (noisy / poorly-structured data robustness):** [your choice]
  Rationale: [2-4 sentences]

**Sequencing:**
  - v0.2.1 (this weekend): ships JOB-1 + JOB-2 as planned; no perf/multidim/robustness work
  - v0.2.2: Rust port (already queued; pre-empts perf work to complete the 4-language reference)
  - v0.3.0: [first concrete consequence of the Q1/Q2/Q3 decisions]
  - v0.5+ (Stage 5): [perf-tuned reference build with measured speedups; locked behind the gate]

**Hand-back to Pete:** this ADR is committed in Proposed state. On next ThinkPad session, Pete reviews + either Accepts (status flips to Accepted, work begins) or Counters (writes Counter-proposal section + bounces back to MacBook).
```

---

## §7. Notes for the MacBook session running this

- **Don't fall in love with one option.** The point of the ADR is to write down the option you didn't pick and why. If §2 ends up listing only one option, you've not done the work.
- **Numbers matter.** Q1 in particular reduces to "what's the speedup factor on representative N?". Don't write "C++ -O3 is faster" — measure it. POC-2 gives you the number.
- **Methodology > language for Q3.** Robust spectral estimation is mostly an algorithmic question (Welch, multitaper, robust periodogram), not a language question. The right Q3 answer might be "use C++ kernel + a Python preprocessing library in `tools/robust-spectral/`".
- **Keep the ADR < 4 pages.** Decisions that need 10 pages aren't decisions, they're explorations. If you find yourself > 4 pages, the ADR is trying to do work that belongs in a separate scoping doc — split it.
- **No `mim2000`, `improwave`, `bouracka`, etc.** ADRs publish with the rest of fourier/ — sanitization rules apply.

End of JOB-3-PERF-NOISY-MULTIDIM-SCOPING.md
