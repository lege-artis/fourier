# Canonical equation — Numerical Partial Sum of Fourier Series (PSF)

> **Format.** Markdown with embedded LaTeX. Companion: `partial-sum.tex`.
> **License.** CC-BY-SA-4.0.

---

## §1. Setup — continuous Fourier series

For an integrable function $f: [-\pi, \pi] \to \mathbb{C}$ (or any function periodic with period $2\pi$), the **Fourier series** is the formal expansion:

$$
f(x) \sim \sum_{n=-\infty}^{\infty} c_n \cdot e^{i n x}
\qquad\qquad (\text{Eq. PSF-1})
$$

with **Fourier coefficients**:

$$
c_n = \frac{1}{2\pi} \int_{-\pi}^{\pi} f(x) \cdot e^{-i n x} \, dx
\qquad\qquad (\text{Eq. PSF-2})
$$

The "$\sim$" in Eq. PSF-1 acknowledges that the series may not converge to $f$ in pointwise sense, depending on $f$'s regularity (see §4).

## §2. The partial-sum operator

The **partial sum** of the Fourier series of $f$ truncated at frequency $\pm M$ is:

$$
S_M[f](x) = \sum_{n=-M}^{M} c_n \cdot e^{i n x}
\qquad\qquad (\text{Eq. PSF-3})
$$

This is a finite trigonometric polynomial — always well-defined, always continuous in $x$.

For real-valued $f$, we have $c_{-n} = \overline{c_n}$ and the partial sum can be written equivalently as:

$$
S_M[f](x) = \frac{a_0}{2} + \sum_{n=1}^{M} (a_n \cos(nx) + b_n \sin(nx))
\qquad\qquad (\text{Eq. PSF-4})
$$

with real coefficients:

$$
a_n = \frac{1}{\pi} \int_{-\pi}^{\pi} f(x) \cos(nx) \, dx, \quad
b_n = \frac{1}{\pi} \int_{-\pi}^{\pi} f(x) \sin(nx) \, dx
\qquad (\text{Eq. PSF-5})
$$

## §3. Numerical evaluation — discretisation of the integral

For numerical computation, the integrals in Eq. PSF-2 (or Eq. PSF-5) are approximated by the trapezoidal rule on $K$ equally-spaced sample points $x_j = -\pi + 2\pi j / K$, $j = 0, 1, \ldots, K-1$:

$$
\hat{c}_n = \frac{1}{K} \sum_{j=0}^{K-1} f(x_j) \cdot e^{-i n x_j}
\qquad\qquad (\text{Eq. PSF-6})
$$

Equivalently in terms of the DFT (`dft.md` Eq. DFT-1) applied to the sample sequence $f[j] = f(x_j)$:

$$
\hat{c}_n = \frac{1}{K} \cdot \mathrm{DFT}_K\{f[j]\}[n] \cdot e^{i n \pi}
\qquad (\text{Eq. PSF-7})
$$

(The phase $e^{in\pi}$ accounts for the $-\pi$ origin of $x_j$ vs the DFT's $0$-indexed convention.)

When $f$ is band-limited to frequencies $|n| < K/2$, the trapezoidal approximation $\hat{c}_n$ equals the exact $c_n$ — this is the **discrete-to-continuous Fourier coefficient correspondence**.

## §4. Convergence theorems

### §4.1 Smooth $f$: rapid (faster than any polynomial)

If $f \in C^\infty(\mathbb{T})$ (smooth on the circle), the Fourier coefficients decay faster than any polynomial:

$$
|c_n| = O(|n|^{-k}) \quad \text{for any } k \in \mathbb{N}
\qquad (\text{Eq. PSF-8})
$$

and the partial sum converges to $f$ uniformly:

$$
\| f - S_M[f] \|_\infty \to 0 \quad \text{as } M \to \infty
\qquad (\text{Eq. PSF-9})
$$

### §4.2 Piecewise smooth $f$: convergence rate $O(1/M)$

If $f$ is piecewise smooth (continuous with continuous derivative except at finitely many points where finite jumps occur), the partial sum converges to $f$ pointwise at points of continuity, and to $\frac{1}{2}(f(x^-) + f(x^+))$ at jump points. The convergence rate is:

$$
\| f - S_M[f] \|_2 = O(M^{-1}) \quad \text{(in } L^2 \text{ norm)}
\qquad (\text{Eq. PSF-10})
$$

[@Korner1989 Ch. 12].

### §4.3 The Gibbs phenomenon

At a jump discontinuity of magnitude $\Delta$, the partial sum **overshoots** by approximately $0.0895 \Delta$ regardless of $M$:

$$
\lim_{M \to \infty} \max_x S_M[f](x) - f(\sup) = G \cdot \Delta
\qquad (\text{Eq. PSF-11})
$$

with $G \approx 0.08949$ the **Gibbs constant** [@Folland1992 §3.5].

This is **not** a numerical artifact — it is an analytical property of the Fourier series. Any implementation must reproduce this overshoot to be correct.

## §5. Test cases (for `shared/physics-testbeds/`)

### §5.1 Sawtooth wave (piecewise linear, jump at endpoints)

$$
f(x) = x \quad \text{for } x \in (-\pi, \pi]
$$

Fourier coefficients: $c_n = i \cdot \frac{(-1)^n}{n}$ for $n \neq 0$, $c_0 = 0$.

Partial sum:

$$
S_M[f](x) = -2 \sum_{n=1}^{M} \frac{(-1)^{n+1}}{n} \sin(nx)
$$

Gibbs overshoot at $x = \pm\pi$: $\approx 0.179 \pi \approx 0.562$.

### §5.2 Square wave (jump at $x = 0$)

$$
f(x) = \mathrm{sgn}(x), \quad x \in (-\pi, \pi]
$$

Fourier coefficients: $c_n = \frac{2}{i n \pi}$ for odd $n$, $0$ for even $n$.

Partial sum:

$$
S_M[f](x) = \frac{4}{\pi} \sum_{n \text{ odd}, n \leq M} \frac{\sin(nx)}{n}
$$

Gibbs overshoot at $x = 0$: $\approx 1.179$ (compared to true value $\pm 1$).

### §5.3 Triangular wave (continuous, piecewise linear, no jumps but kink)

$$
f(x) = |x|, \quad x \in [-\pi, \pi]
$$

Fourier coefficients: $a_0 = \pi$, $a_n = -\frac{4}{\pi n^2}$ for odd $n$, $0$ for even $n$.

Partial sum:

$$
S_M[f](x) = \frac{\pi}{2} - \frac{4}{\pi} \sum_{n \text{ odd}, n \leq M} \frac{\cos(nx)}{n^2}
$$

No Gibbs phenomenon (function is continuous); convergence is $O(1/M^2)$ in $L^\infty$.

These three cases form the v0.1.0 partial-sum test track in `shared/physics-testbeds/dft.md`.

## §6. Code-block translation

The faithful translation for evaluating $S_M[f](x)$ at a single point given coefficients $\{a_n, b_n\}$ (Fortran 2018):

```fortran
function partial_sum(a, b, M, x) result(S)
   real(dp), intent(in) :: a(0:M), b(0:M)
   integer,  intent(in) :: M
   real(dp), intent(in) :: x
   real(dp)             :: S
   integer              :: n
   S = 0.5_dp * a(0)
   do n = 1, M
      S = S + a(n) * cos(real(n, dp) * x) + b(n) * sin(real(n, dp) * x)
   end do
end function
```

| Math (Eq. PSF-4) | Code |
|---|---|
| $S = a_0 / 2$ | `S = 0.5_dp * a(0)` |
| Sum over $n$ from 1 to $M$ | `do n = 1, M` |
| $a_n \cos(nx) + b_n \sin(nx)$ | `a(n) * cos(real(n, dp) * x) + b(n) * sin(real(n, dp) * x)` |
| Accumulate | `S = S + ...` |

For evaluating at many points (e.g. plotting), the inner cos/sin calls are the cost driver. Stage 5 optimisation: precompute cos/sin tables, use Horner-like recurrence for trigonometric identity.

## §7. Citations

- `Korner1989 Ch. 12` — convergence theorems with proofs (cited in §4)
- `Folland1992 §3.5` — Gibbs phenomenon derivation (cited in §4)
- `SteinShakarchi2003 Ch. 2-3` — pointwise convergence at points of continuity (cited as cross-reference)
- `Bracewell3rd Ch. 8` — engineer-friendly partial-sum discussion (cited as cross-reference)

---

*End of `partial-sum.md`. Companion: `partial-sum.tex`.*
