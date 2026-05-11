# Canonical equation — Discrete Fourier Transform (DFT)

> **Format.** Markdown with embedded LaTeX (inline `$..$` and block `$$..$$`).
> Companion file: `dft.tex` (same content in proper LaTeX `\begin{equation}` form for MathJax/KaTeX/PDF rendering).
>
> **Cited from.** `docs/canonical/en/01-dft-definition.md` (canonical-tier doc), `docs/engineer/en/01-what-dft-actually-computes.md` (engineer-tier doc).
>
> **License.** CC-BY-SA-4.0 (per `LICENSE-DOCS`).

---

## §1. Definition

For a finite sequence of complex samples $x[0], x[1], \ldots, x[N-1]$ with $N \in \mathbb{N}$, the **Discrete Fourier Transform** $X[k]$ is defined for each $k \in \{0, 1, \ldots, N-1\}$ by:

$$
X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-2\pi i k n / N}
\qquad\qquad (\text{Eq. DFT-1})
$$

where $i^2 = -1$ is the imaginary unit and the kernel $e^{-2\pi i k n / N}$ is a complex root of unity of order $N$.

Equivalently, writing $\omega_N = e^{-2\pi i / N}$ (the primitive $N$-th root of unity):

$$
X[k] = \sum_{n=0}^{N-1} x[n] \cdot \omega_N^{k n}
\qquad\qquad (\text{Eq. DFT-1'})
$$

The inverse DFT (IDFT) recovers the time-domain samples from the frequency-domain coefficients:

$$
x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X[k] \cdot e^{+2\pi i k n / N}
\qquad\qquad (\text{Eq. DFT-2})
$$

The asymmetry in the normalisation factor $1/N$ is one common convention; alternative conventions distribute $1/\sqrt{N}$ symmetrically across both transforms (see §6).

## §2. Code-block translation (the equation→code mapping)

The faithful translation of Eq. DFT-1 into code (Fortran 2018 `complex(real64)` shown; same shape applies to C++ / Rust / Pascal):

```fortran
! DFT kernel — direct translation of Eq. DFT-1
do k = 0, N - 1
   X(k) = (0.0_dp, 0.0_dp)
   do n = 0, N - 1
      omega = -2.0_dp * pi * real(k * n, dp) / real(N, dp)
      X(k) = X(k) + x(n) * cmplx(cos(omega), sin(omega), kind=dp)
   end do
end do
```

The mapping is line-by-line:

| Math (Eq. DFT-1) | Code |
|---|---|
| Outer sum over $k$ | `do k = 0, N - 1` |
| $X[k] = 0$ initial | `X(k) = (0.0_dp, 0.0_dp)` |
| Inner sum over $n$ | `do n = 0, N - 1` |
| Argument $-2\pi k n / N$ | `omega = -2.0_dp * pi * real(k*n, dp) / real(N, dp)` |
| $e^{i\omega} = \cos\omega + i\sin\omega$ | `cmplx(cos(omega), sin(omega), kind=dp)` |
| Multiply $x[n]$ by kernel | `x(n) * cmplx(...)` |
| Accumulate | `X(k) = X(k) + ...` |

This is what the v0.1.0 commit message must show explicitly per `WORKING-SPEC-v0.3-EN.md` §4.1.

## §3. Complexity

The direct evaluation of Eq. DFT-1 requires $N$ complex multiplications and $N-1$ complex additions per output coefficient, and there are $N$ output coefficients:

$$
T_{\text{DFT}}(N) = \Theta(N^2) \qquad\qquad (\text{Eq. DFT-3})
$$

This is the textbook DFT complexity. The Fast Fourier Transform (see `fft-cooley-tukey.md`) reduces this to $\Theta(N \log N)$ by recursive halving when $N$ is a power of 2 [@Cooley1965].

## §4. Linearity (property to test)

The DFT is a **linear transformation**: for scalars $\alpha, \beta \in \mathbb{C}$ and sequences $x, y$:

$$
\mathrm{DFT}\{\alpha x[n] + \beta y[n]\} = \alpha \mathrm{DFT}\{x[n]\} + \beta \mathrm{DFT}\{y[n]\}
\qquad (\text{Eq. DFT-4})
$$

Tested in `shared/property-tests/dft.md` Property P1.

## §5. Plancherel / Parseval relation (property to test)

Conservation of energy across the transform:

$$
\sum_{n=0}^{N-1} |x[n]|^2 = \frac{1}{N} \sum_{k=0}^{N-1} |X[k]|^2
\qquad (\text{Eq. DFT-5})
$$

This is the discrete analogue of the Plancherel theorem [@Folland1992 §7.2] and serves as a strong numerical-accuracy test: any precision-losing implementation drifts from this identity proportionally to the accumulated rounding error.

Tested in `shared/property-tests/dft.md` Property P2.

## §6. Alternative normalisations

Three conventions are in common use:

| Convention | Forward $X[k]$ | Inverse $x[n]$ | Common in |
|---|---|---|---|
| **Asymmetric (this project's default)** | $\sum_n x[n] e^{-2\pi i k n / N}$ | $\frac{1}{N} \sum_k X[k] e^{+2\pi i k n / N}$ | Engineering (Oppenheim-Schafer, Bracewell), NumPy, MATLAB |
| **Symmetric** | $\frac{1}{\sqrt{N}} \sum_n x[n] e^{-2\pi i k n / N}$ | $\frac{1}{\sqrt{N}} \sum_k X[k] e^{+2\pi i k n / N}$ | Physics, mathematics (Stein-Shakarchi) |
| **Inverse-asymmetric** | $\frac{1}{N} \sum_n x[n] e^{-2\pi i k n / N}$ | $\sum_k X[k] e^{+2\pi i k n / N}$ | Some signal-processing texts |

`lege-artis/fourier` adopts the **asymmetric forward / inverse-1/N** convention (the engineering / NumPy default) for v0.1.0. The convention is documented at the top of every `backends/<lang>/src/dft_kernel.*` source file. Switching conventions is trivial — multiply by $\sqrt{N}$ — but the choice must be one and consistent across all backends.

## §7. Precision claims

Per `IEEE754_2019` and the precision tiers documented in `WORKING-SPEC-v0.3-EN.md` §4.2:

| Precision | Type | Expected ε per Eq. DFT-1 evaluation at $N$ | Used for |
|---|---|---|---|
| Single (float32) | IEEE 754 binary32 | $\varepsilon_{\text{single}}(N) \approx N \cdot 2^{-23}$ | Performance benchmarks; not for canonical reference |
| **Double (float64)** | IEEE 754 binary64 | $\varepsilon_{\text{double}}(N) \approx N \cdot 2^{-52}$ | **Default for canonical reference and golden vectors** |
| Quad (float128) | IEEE 754 binary128 (where supported) | $\varepsilon_{\text{quad}}(N) \approx N \cdot 2^{-112}$ | High-precision oracle / stretch goal |

The bound is conservative: actual rounding accumulates as $O(\sqrt{N} \cdot \varepsilon_{\text{machine}})$ statistically [@NumRec3rd §12.1] but can grow up to $O(N \cdot \varepsilon)$ in adversarial inputs. Property tests (Plancherel, etc.) use the linear-in-$N$ bound as the gate.

## §8. Citations (refs.bib keys)

- `Cooley1965` — for the FFT reduction to $\Theta(N \log N)$ when $N$ is a power of 2 (cited in §3)
- `Folland1992 §7.2` — Plancherel relation derivation (cited in §5)
- `OppenheimSchafer3rd §8.2` — the asymmetric / inverse-1/N convention used here (cited in §6)
- `Bracewell3rd Ch.5` — engineer-friendly convention discussion (cited in §6)
- `SteinShakarchi2003 Ch.7` — symmetric convention used in physics-mathematics literature (cited in §6)
- `IEEE754_2019` — precision claims (cited in §7)
- `NumRec3rd §12.1` — empirical rounding behaviour (cited in §7)

---

*End of `dft.md`. Companion: `dft.tex`.*
