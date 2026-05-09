# lege-artis/fourier — canonical tier — Introduction (EN)

> **Audience.** Mathematician, physicist, academic reviewer, contributor wanting to understand *why* the algorithms in this repository compute what they claim to compute.
>
> **Reading time.** ~25 minutes for this Introduction. ~2 hours for the full canonical tier (this + chapters 01-03).
>
> **License.** CC-BY-SA-4.0 (per `LICENSE-DOCS`).
>
> **Companion.** Engineer-tier `docs/engineer/en/00-quick-start.md` covers the same scope from the practitioner-using-the-library angle.

---

## §1. Scope of the canonical tier

`lege-artis/fourier` provides reference implementations of three foundational algorithms:

| Algorithm | What it computes | Complexity | Canonical equation file |
|---|---|---|---|
| **DFT** (Discrete Fourier Transform) | Frequency-domain representation of a finite sequence of complex samples | $\Theta(N^2)$ direct | `shared/canonical-equations/dft.{md,tex}` |
| **FFT** (Fast Fourier Transform, Cooley-Tukey radix-2) | Same DFT, computed via recursive halving exploiting the structure of roots of unity when $N = 2^m$ | $\Theta(N \log N)$ | `shared/canonical-equations/fft-cooley-tukey.{md,tex}` |
| **PSF** (Numerical Partial Sum of Fourier Series) | Truncated Fourier-series reconstruction of a continuous periodic function from its $K$ samples | $\Theta(K \cdot M)$ direct evaluation; $\Theta(K \log K)$ via DFT for coefficient estimation | `shared/canonical-equations/partial-sum.{md,tex}` |

The three are tightly related: the DFT is the discrete analogue of the Fourier-coefficient integral; the FFT is an algorithmic accelerator for the DFT; the PSF uses (estimated) Fourier coefficients to reconstruct a function. Implementing all three together makes the relationship visible.

## §2. Canonical-tier promise

This documentation tier holds itself to the **lege artis** standard:

- Every algorithm is **derived from first principles** in this tier. We do not say "the FFT works because that's how it works" — we show the recurrence, prove the equivalence with direct DFT, derive the complexity.
- Every claim cites a primary source (see `shared/reference-bibliography/refs.bib`). For numerical bounds, we cite IEEE 754. For convergence theorems, we cite Korner / Folland / Stein-Shakarchi. For the FFT itself, we cite Cooley-Tukey 1965.
- **Wikipedia is not a primary source.** It can be a sanity check, never an authority.
- The mathematical content lives in `shared/canonical-equations/*.tex` files, written in proper LaTeX with theorem/proof structure. These docs in `docs/canonical/en/` are guided readings of those equation files plus the surrounding context.
- Engineer-tier docs (`docs/engineer/en/`) translate this content for practitioners, but never contradict it. If you ever read something in the engineer tier that disagrees with the canonical tier, the canonical tier wins; please file an issue.

## §3. Why these three algorithms together?

The Fourier transform is the mathematical operation; the DFT is its discretisation; the FFT is one algorithm for computing the DFT efficiently; the PSF is one application of the DFT (reconstruct a function from samples).

Implementing them together has pedagogical and verification value:

- **Pedagogical**: A reader studying Fourier methods sees the chain *concept → discretisation → algorithm → application* in one repository.
- **Verification**: The DFT is the slow-but-trustworthy oracle for the FFT (Property P5 in `shared/property-tests/dft.md`). The PSF tests both the DFT (by computing coefficients) and the trigonometric-polynomial evaluator. Cross-checks fall out of the structure.

## §4. The first-principles requirement

Per `WORKING-SPEC-v0.3-EN.md` §4.1, the implementation discipline of `lege-artis/fourier` is:

> Every algorithm is implemented from the canonical mathematical equation, not by porting a reference implementation. The chain must be verifiable: equation file → code, line-by-line.

What this rules out:

- Borrowing FFTW's bit-reversal permutation table — even though it's correct, the code-as-translation chain is broken.
- "Optimising" the DFT by recognising structure that isn't in the canonical equation — Stage 5 work, gated separately.
- Treating SciPy / NumPy / Wolfram outputs as source — they are oracles (testbeds) for our implementation, not source material.

What this enables:

- A reader can verify our Fortran DFT implementation matches `shared/canonical-equations/dft.{md,tex}` by inspection. The git commit message for the implementation includes the equation→code mapping explicitly.
- When IEEE 754 implementations differ across platforms (FMA contraction, etc.), our reference is the math, not a particular library's output.

## §5. The canonical-then-optimization discipline

v0.1.0 ships only the **canonical reference**: a Fortran implementation prioritising clarity and correctness over performance. The Makefile compiles with `-O0 -fcheck=all -Wall` — no optimisation; runtime checks enabled. This is the version against which all subsequent optimisations are validated.

Stage 5 (Performance — v0.5+) introduces optimisations: twiddle pre-computation, vectorisation, mixed-radix for non-power-of-2 lengths, Bluestein's algorithm for arbitrary lengths. Each optimisation:

- Has its own documentation entry in `docs/performance/en/`
- Carries a benchmark (before/after)
- Passes the v0.1.0 golden-vector regression test
- Provides a mathematical justification (which property of the canonical algorithm makes the optimisation sound)

**Performance is never an excuse to violate canonical correctness.** This is a structural commitment, not a slogan.

## §6. Reading order

This canonical tier has four chapters:

| Chapter | File | Subject |
|---|---|---|
| 00 | `00-introduction.md` (this file) | Scope, promise, discipline |
| 01 | `01-dft-definition.md` | Definition of the DFT, with proofs of linearity and Plancherel |
| 02 | `02-fft-cooley-tukey.md` | Derivation of Cooley-Tukey radix-2 FFT, with proof of equivalence to direct DFT |
| 03 | `03-partial-sums-convergence.md` | Convergence theorems for Fourier series partial sums, including Gibbs phenomenon |

Each chapter cites the corresponding `shared/canonical-equations/*.{md,tex}` files for the formal derivations. The chapters provide the surrounding narrative; the equation files provide the certified math.

## §7. Multilingual roadmap

This `docs/canonical/en/` content is the **EN baseline** for v0.1.0. Translations to CS / JA / DE / IT will follow at v0.1.1+ and onwards:

| Language | Translation reference | Status |
|---|---|---|
| EN (English) | self | **v0.1.0 baseline** |
| CS (Czech) | `DiskretniFourierovaCS` for terminology + Czech mathematical conventions | v0.1.1+ |
| JA (Japanese) | OQ-FFP-7-JA — pending choice (Iwanami / Tatsumi / Ohishi / translation) | v0.1.1+ |
| DE (German) | OQ-FFP-7-DE — likely Forster *Analysis 3* | v0.1.1+ |
| IT (Italian) | OQ-FFP-7-IT — TBD | v0.1.1+ |

Translations are not mechanical; they may refine concepts where the source language has more or fewer terms for a phenomenon. Every language version is reviewed by a native speaker with mathematical / engineering literacy in the topic.

## §8. License attribution

This documentation, including the chapters that follow, is licensed under **CC-BY-SA-4.0**. You may reuse it (with attribution) and create derivative works (which must also be CC-BY-SA-4.0). The code in this repository is separately licensed under Apache 2.0 — see `LICENSE`. Names "MIM2000", "Improwave", and the personal name "Petr Yamyang" are not licensed for derivative use — see `TRADEMARK.md`.

---

*Next:* `01-dft-definition.md`.
