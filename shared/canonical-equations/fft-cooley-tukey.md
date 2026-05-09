# Canonical equation — Fast Fourier Transform (Cooley-Tukey radix-2)

> **Format.** Markdown with embedded LaTeX. Companion: `fft-cooley-tukey.tex`.
> **License.** CC-BY-SA-4.0.

---

## §1. Setup

The Cooley-Tukey radix-2 FFT [@Cooley1965] computes the same DFT defined in `dft.md` Eq. DFT-1, but exploits a recursive decomposition when $N$ is a power of 2 to reduce complexity from $\Theta(N^2)$ to $\Theta(N \log N)$.

Throughout this document, $N = 2^m$ for some $m \in \mathbb{N}_0$, and $\omega_N = e^{-2\pi i / N}$ is the primitive $N$-th root of unity.

## §2. Decimation-in-time decomposition

Split the input sequence $x[0], x[1], \ldots, x[N-1]$ into even-indexed and odd-indexed subsequences:

$$
x_{\text{even}}[r] = x[2r], \quad x_{\text{odd}}[r] = x[2r+1], \quad r = 0, 1, \ldots, N/2 - 1
$$

The DFT of $x$ at frequency $k$ splits as:

$$
X[k] = \sum_{r=0}^{N/2-1} x[2r] \cdot \omega_N^{2rk} + \sum_{r=0}^{N/2-1} x[2r+1] \cdot \omega_N^{(2r+1)k}
\qquad (\text{Eq. FFT-1})
$$

Using $\omega_N^{2rk} = \omega_{N/2}^{rk}$ (since $e^{-2\pi i \cdot 2 / N} = e^{-2\pi i / (N/2)}$):

$$
X[k] = \underbrace{\sum_{r=0}^{N/2-1} x_{\text{even}}[r] \cdot \omega_{N/2}^{rk}}_{X_{\text{even}}[k]}
       + \omega_N^k \cdot \underbrace{\sum_{r=0}^{N/2-1} x_{\text{odd}}[r] \cdot \omega_{N/2}^{rk}}_{X_{\text{odd}}[k]}
\qquad (\text{Eq. FFT-2})
$$

Each underbraced sum is a DFT of length $N/2$. So:

$$
X[k] = X_{\text{even}}[k] + \omega_N^k \cdot X_{\text{odd}}[k], \quad k = 0, 1, \ldots, N/2 - 1
\qquad (\text{Eq. FFT-3})
$$

## §3. Periodicity exploit (the second half)

For $k \in \{N/2, N/2+1, \ldots, N-1\}$, write $k = N/2 + j$ where $j \in \{0, 1, \ldots, N/2-1\}$. Then:

$$
\omega_{N/2}^{r(N/2+j)} = \omega_{N/2}^{rj} \cdot \omega_{N/2}^{rN/2} = \omega_{N/2}^{rj} \cdot 1 = \omega_{N/2}^{rj}
$$

(since $\omega_{N/2}^{N/2} = e^{-2\pi i (N/2) / (N/2)} = e^{-2\pi i} = 1$.) So $X_{\text{even}}[N/2+j] = X_{\text{even}}[j]$ and similarly for $X_{\text{odd}}$.

The twiddle factor for the second half:

$$
\omega_N^{N/2+j} = \omega_N^{N/2} \cdot \omega_N^j = -\omega_N^j
$$

(since $\omega_N^{N/2} = e^{-\pi i} = -1$.) Therefore:

$$
X[N/2 + j] = X_{\text{even}}[j] - \omega_N^j \cdot X_{\text{odd}}[j], \quad j = 0, 1, \ldots, N/2 - 1
\qquad (\text{Eq. FFT-4})
$$

## §4. The butterfly

Combining Eq. FFT-3 and Eq. FFT-4 gives the **butterfly operation**:

$$
\begin{aligned}
X[k]       &= X_{\text{even}}[k] + \omega_N^k \cdot X_{\text{odd}}[k] \\
X[k + N/2] &= X_{\text{even}}[k] - \omega_N^k \cdot X_{\text{odd}}[k]
\end{aligned}
\qquad k = 0, 1, \ldots, N/2 - 1
\qquad (\text{Eq. FFT-5})
$$

Each butterfly: one complex multiplication ($\omega_N^k \cdot X_{\text{odd}}[k]$) plus one complex addition and one complex subtraction. Two outputs from two inputs, sharing one twiddle. $N/2$ butterflies per stage.

## §5. Recursion and complexity

Let $T(N)$ be the cost of the FFT of length $N$. Eq. FFT-5 says: solve two subproblems of size $N/2$, then perform $N/2$ butterflies (each constant cost). The recurrence:

$$
T(N) = 2 T(N/2) + cN, \quad T(1) = O(1)
\qquad (\text{Eq. FFT-6})
$$

By the master theorem, $T(N) = \Theta(N \log_2 N)$.

Concretely, $\log_2 N$ stages, each with $N/2$ butterflies, each costing one complex multiplication: total $\frac{N}{2} \log_2 N$ multiplications, $N \log_2 N$ additions.

## §6. Code-block translation (recursive form)

The faithful recursive translation (Fortran 2018, doubleprecision; full iterative form in `backends/fortran/src/fft_kernel.f90` v0.2.0):

```fortran
recursive subroutine fft_recursive(x, N) result(X_out)
   complex(dp), intent(in)  :: x(0:N-1)
   integer,     intent(in)  :: N
   complex(dp)              :: X_out(0:N-1)
   complex(dp), allocatable :: X_even(:), X_odd(:)
   complex(dp)              :: t
   real(dp)                 :: theta
   integer                  :: k

   if (N <= 1) then
      X_out = x
      return
   end if

   X_even = fft_recursive(x(0:N-2:2), N/2)   ! DFT of even-indexed
   X_odd  = fft_recursive(x(1:N-1:2), N/2)   ! DFT of odd-indexed

   do k = 0, N/2 - 1
      theta = -2.0_dp * pi * real(k, dp) / real(N, dp)
      t = cmplx(cos(theta), sin(theta), kind=dp) * X_odd(k)   ! twiddle * odd
      X_out(k)       = X_even(k) + t                          ! Eq. FFT-5 first
      X_out(k + N/2) = X_even(k) - t                          ! Eq. FFT-5 second
   end do
end subroutine
```

| Math (Eq. FFT-5) | Code |
|---|---|
| Recurse on even-indexed inputs | `X_even = fft_recursive(x(0:N-2:2), N/2)` |
| Recurse on odd-indexed inputs | `X_odd = fft_recursive(x(1:N-1:2), N/2)` |
| Twiddle $\omega_N^k$ | `cmplx(cos(theta), sin(theta), kind=dp)` with $\theta = -2\pi k / N$ |
| $\omega_N^k \cdot X_{\text{odd}}[k]$ | `t = ... * X_odd(k)` |
| $X[k] = X_{\text{even}}[k] + \omega_N^k X_{\text{odd}}[k]$ | `X_out(k) = X_even(k) + t` |
| $X[k+N/2] = X_{\text{even}}[k] - \omega_N^k X_{\text{odd}}[k]$ | `X_out(k + N/2) = X_even(k) - t` |

The recursive form is correct (faithful to Eq. FFT-5) but allocates intermediate arrays, which hurts cache performance. The iterative bit-reversal-based form (deferred to v0.2.0 / Stage 5) is the typical production layout. For v0.1.0 reference correctness this recursive form is acceptable.

## §7. Equivalence with DFT (the validity claim)

Eq. FFT-3 + Eq. FFT-4 are derived from Eq. DFT-1 by re-indexing the sum and exploiting periodicity / sign-flip of roots of unity. Therefore:

$$
\mathrm{FFT}(x) \equiv \mathrm{DFT}(x) \quad \text{when } N = 2^m \text{ exactly}
\qquad (\text{Eq. FFT-7})
$$

In **floating-point arithmetic**, the equivalence holds within rounding error:

$$
\| \mathrm{FFT}(x) - \mathrm{DFT}(x) \|_\infty \leq C \cdot \log_2(N) \cdot \varepsilon_{\text{machine}} \cdot \|x\|_\infty
\qquad (\text{Eq. FFT-8})
$$

with $C$ a small constant (typically $\leq 4$) [@NumRec3rd §12.2]. This is **better** than the direct DFT bound (which is $O(N \cdot \varepsilon)$) because the recursive halving reduces accumulated rounding.

This bound is the cross-algorithm equivalence-test gate in `shared/property-tests/dft.md` Property P5.

## §8. Twiddle-factor precision

Computing $\omega_N^k = \cos(2\pi k / N) - i \sin(2\pi k / N)$ via `cos`/`sin` library calls produces twiddles correct to one ULP each (single rounding). Pre-computation of all twiddles into a table at startup (Stage 5 optimisation) does not change correctness — only performance.

When $N$ is large enough that successive twiddle differences fall below `eps_machine`, the FFT rounding error grows accordingly. For $N = 2^{20} \approx 10^6$ in double precision, twiddle precision is still adequate ($\log_2(N) \cdot \varepsilon \approx 4 \times 10^{-15}$).

## §9. Citations

- `Cooley1965` — original derivation (cited throughout)
- `NumRec3rd §12.2` — empirical FFT rounding bounds (cited in §7)
- `OppenheimSchafer3rd §9` — radix-2 + radix-4 + Bluestein (cited as engineer-tier reference)
- `Folland1992 §8.1` — DFT/FFT equivalence as a structural result (cited in §7)

---

*End of `fft-cooley-tukey.md`. Companion: `fft-cooley-tukey.tex`.*
