# Canonical tier — Chapter 01 — DFT: definition, linearity, Plancherel (EN)

> **Companion equations file.** `shared/canonical-equations/dft.{md,tex}`. This chapter narrates and contextualises the formal content there; the equation file is the certified math.
>
> **License.** CC-BY-SA-4.0.

---

## §1. The discrete-time Fourier perspective

A finite sequence of $N$ complex samples $x = (x[0], x[1], \ldots, x[N-1])$ can be viewed in two equivalent ways:

1. **Time-domain** (or **sample-domain**): the sequence as recorded — what each sample value is, in order.
2. **Frequency-domain**: the sequence decomposed into orthogonal trigonometric components, each weighted by a complex coefficient.

The **Discrete Fourier Transform (DFT)** is the canonical map from view (1) to view (2). The mathematics is direct: the DFT outputs $X[k]$ are obtained from the inputs $x[n]$ by the formula `dft.md` Eq. DFT-1:

$$
X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-2\pi i k n / N}
$$

Each $X[k]$ measures how much the trigonometric component $e^{2\pi i k n / N}$ — a complex sinusoid completing $k$ full cycles over the $N$-sample window — contributes to $x$.

## §2. Why this particular formula?

The kernel $e^{-2\pi i k n / N}$ is not arbitrary. Three properties make it canonical:

### §2.1 Orthogonality

The complex exponentials $\{e^{-2\pi i k n / N} : k = 0, 1, \ldots, N-1\}$ are mutually orthogonal under the inner product $\langle u, v \rangle = \sum_n u[n] \overline{v[n]}$ on $\mathbb{C}^N$. Specifically:

$$
\sum_{n=0}^{N-1} e^{-2\pi i k n / N} \cdot e^{2\pi i \ell n / N} = \begin{cases} N & k = \ell \pmod N \\ 0 & \text{otherwise} \end{cases}
$$

This is what makes the DFT a *change of basis* in $\mathbb{C}^N$ — the inputs and outputs span the same vector space, just expressed in different orthogonal bases. The orthogonality is what makes the inverse transform clean: each $x[n]$ recovers as a uniformly-weighted sum of the $X[k]$'s.

### §2.2 Group structure (roots of unity)

The kernel $\omega_N = e^{-2\pi i / N}$ is a primitive $N$-th root of unity. The set $\{\omega_N^0, \omega_N^1, \ldots, \omega_N^{N-1}\}$ forms a cyclic group under multiplication. This is what enables the FFT (chapter 02): the recursive halving of the DFT exploits the fact that $\omega_N^2 = \omega_{N/2}$.

### §2.3 Periodicity

The output sequence $X$ has the same length $N$ as the input — and $X[k]$ extends periodically: $X[k + N] = X[k]$ in the natural extension. This reflects the fact that frequencies above the Nyquist limit ($k = N/2$ for even $N$) are aliased onto lower frequencies.

These three properties — orthogonality, group structure, periodicity — are why the DFT is *the* discrete-time Fourier transform, not just *a* discretisation. Other discretisations exist (e.g. the discrete Hartley transform), but they lack one or more of these properties.

## §3. Linearity

The DFT is linear (`dft.tex` Theorem 1, `dft.md` §4):

$$
\mathrm{DFT}\{\alpha x[n] + \beta y[n]\} = \alpha \mathrm{DFT}\{x[n]\} + \beta \mathrm{DFT}\{y[n]\}
$$

This follows directly from the linearity of the finite sum. The proof is a single line — substitute, distribute the sum, factor.

**Implementation consequence.** Tested in `shared/property-tests/dft.md` Property P1: any code claiming to compute the DFT must respect linearity to within precision. Failure to do so usually indicates a bug in the kernel sign, accumulator initialisation, or output indexing — never a numerical artifact.

## §4. The Plancherel relation

Conservation of energy across the transform (`dft.tex` Theorem 2, `dft.md` §5):

$$
\sum_{n=0}^{N-1} |x[n]|^2 = \frac{1}{N} \sum_{k=0}^{N-1} |X[k]|^2
$$

Plancherel is the discrete analogue of the continuous Plancherel theorem [@Folland1992 §7.2]. The discrete proof uses the orthogonality of the kernel exponentials (§2.1 above): the squared norm in time-domain equals the squared norm in frequency-domain (up to the factor $1/N$ from the asymmetric convention).

**Implementation consequence.** Plancherel is the strongest single test of numerical accuracy. Any precision-losing implementation drifts from this identity proportionally to the accumulated rounding error. We use it as Property P2 in `shared/property-tests/dft.md` with the gate $|\sum |x|^2 - \frac{1}{N}\sum |X|^2| \leq C \cdot N \cdot \varepsilon_{\text{machine}}$.

## §5. The DC component

The output $X[0]$ has a special interpretation:

$$
X[0] = \sum_{n=0}^{N-1} x[n] \cdot e^{0} = \sum_{n=0}^{N-1} x[n]
$$

This is the **DC component** — the sum (or, after normalisation, the average) of the input. It's the only output that corresponds to a real-valued component of $x$: the constant function. All other $X[k]$ correspond to oscillating components.

**Implementation consequence.** Property P3 in `shared/property-tests/dft.md` checks $X[0] = \sum x[n]$. This is a sanity test: any nonzero rounding here indicates the kernel is being computed wrong at $k=0$ (where $\omega_N^0 = 1$ exactly, no floating-point evaluation needed).

## §6. Nyquist symmetry (for real-valued inputs)

When the input $x$ is real-valued (i.e. $x[n] \in \mathbb{R}$ for all $n$), the output $X$ has Hermitian symmetry:

$$
X[N - k] = \overline{X[k]} \quad \text{for } k = 1, 2, \ldots, N-1
$$

This is because $e^{-2\pi i (N-k) n / N} = e^{-2\pi i n} \cdot e^{2\pi i k n / N} = \overline{e^{-2\pi i k n / N}}$, and complex conjugation distributes over a real-coefficient sum.

**Implementation consequence.** Property P4 in `shared/property-tests/dft.md`. This symmetry is exploited by the **real-input FFT** (a Stage 5 / v0.5+ optimisation): one only needs to compute $X[0..N/2]$ and the rest follow by conjugation. For v0.1.0 reference, we compute all outputs explicitly — clarity over efficiency.

## §7. Choosing precision

Per `dft.md` §7, the IEEE 754 binary64 (double-precision) bound for direct DFT evaluation is conservatively $\varepsilon_{\text{double}}(N) \approx N \cdot 2^{-52}$. For $N = 1024$, that gives roughly $2.3 \times 10^{-13}$ — well within practical accuracy requirements.

For physics applications, the precision claim is documented per algorithm × precision-tier × language combination in the `precision-baseline.json` file pinned at the v0.1.0 release tag. Single precision is for performance benchmarks; double precision is the default for canonical reference and golden-vector validation; quad precision is a stretch goal for high-precision oracle scenarios.

## §8. What this chapter does not cover

- The Cooley-Tukey FFT — see chapter 02 / `fft-cooley-tukey.{md,tex}`.
- Continuous Fourier transform — outside scope; see Bracewell or Stein-Shakarchi.
- Number-theoretic transforms (DFTs over finite fields) — out of scope.
- Multidimensional DFTs (2D FFT for image processing) — stretch goal, not v0.1.0.
- Discrete cosine and sine transforms — different basis, different algorithms; out of scope.

---

*Previous:* `00-introduction.md`. *Next:* `02-fft-cooley-tukey.md`. *Equations file:* `../../shared/canonical-equations/dft.md`.
