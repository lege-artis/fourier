# Engineer tier — Chapter 01 — What the DFT actually computes (EN)

> **Companion canonical-tier doc.** `docs/canonical/en/01-dft-definition.md` — same content from the math-rigor angle.
> **License.** CC-BY-SA-4.0.

---

## §1. The 4-sample example, by hand

Let's compute the DFT of a length-4 input by hand. This is small enough to do every step on paper, big enough to see the structure.

**Input:**
```
x = [1, 0, -1, 0]    (a sampled cosine — one cycle in 4 samples)
```

**Formula** (from `shared/canonical-equations/dft.md` Eq. DFT-1):
$$
X[k] = \sum_{n=0}^{3} x[n] \cdot e^{-2\pi i k n / 4}
$$

For $N = 4$, the kernel values $e^{-2\pi i k n / 4}$ form a $4 \times 4$ table:

| $k \backslash n$ | $n=0$ | $n=1$ | $n=2$ | $n=3$ |
|---|---|---|---|---|
| $k=0$ | 1 | 1 | 1 | 1 |
| $k=1$ | 1 | $-i$ | $-1$ | $i$ |
| $k=2$ | 1 | $-1$ | 1 | $-1$ |
| $k=3$ | 1 | $i$ | $-1$ | $-i$ |

(Each row is a different frequency. $k=0$ is constant, $k=1$ is the slowest oscillation, $k=2$ is the fastest, $k=3$ is the negative-frequency mirror of $k=1$.)

**Computing $X[0]$** (DC component):

$$
X[0] = 1 \cdot 1 + 0 \cdot 1 + (-1) \cdot 1 + 0 \cdot 1 = 0
$$

(Sum of the input is zero — pure cosine has zero DC.)

**Computing $X[1]$** (the cosine's natural frequency):

$$
X[1] = 1 \cdot 1 + 0 \cdot (-i) + (-1) \cdot (-1) + 0 \cdot i = 1 + 1 = 2
$$

**Computing $X[2]$** (Nyquist):

$$
X[2] = 1 \cdot 1 + 0 \cdot (-1) + (-1) \cdot 1 + 0 \cdot (-1) = 1 - 1 = 0
$$

**Computing $X[3]$** (Hermitian mirror of $X[1]$):

$$
X[3] = 1 \cdot 1 + 0 \cdot i + (-1) \cdot (-1) + 0 \cdot (-i) = 1 + 1 = 2
$$

**Result:**
```
X = [0, 2, 0, 2]
```

This says:
- DC ($X[0] = 0$): no constant offset in the input. ✓
- Frequency 1 cycle/window ($X[1] = 2$): the input has a pure cosine at this frequency, amplitude $2 = N/2 = 4/2$. ✓
- Frequency 2 cycles/window ($X[2] = 0$): no signal at the Nyquist frequency. ✓
- "Negative" frequency ($X[3] = 2$): Hermitian mirror — for any real-valued input, $X[3]$ equals $\overline{X[1]} = 2$. ✓

Total energy check (Plancherel):
$$\sum_n |x[n]|^2 = 1 + 0 + 1 + 0 = 2$$
$$\frac{1}{N} \sum_k |X[k]|^2 = \frac{1}{4}(0 + 4 + 0 + 4) = 2 \checkmark$$

## §2. Why $\Theta(N^2)$?

For each output $X[k]$ — and there are $N$ of them — we summed $N$ terms. Each term is one complex multiplication and one complex addition. That's $N \times N = N^2$ complex multiplications.

For $N = 1024$, that's roughly $10^6$ complex multiplications. Modern CPUs do this in milliseconds — but for $N = 10^6$, it becomes $10^{12}$ multiplications, which is hours.

**This is where the FFT comes in.** Cooley-Tukey (1965) showed that when $N$ is a power of 2, you can compute the same DFT in $\Theta(N \log_2 N)$ multiplications instead of $\Theta(N^2)$. For $N = 10^6$, that's $20 \times 10^6$ multiplications instead of $10^{12}$ — fifty thousand times faster. See chapter 02.

## §3. The kernel "rotates"

The kernel $e^{-2\pi i k n / N}$ in the complex plane traces out the unit circle. As $n$ varies from 0 to $N-1$, the kernel:

- For $k = 0$: stays at the point $1 + 0i$ (no rotation).
- For $k = 1$: sweeps once around the unit circle (clockwise, since the exponent is negative).
- For $k = 2$: sweeps twice around.
- ...
- For $k = N/2$: sweeps $N/2$ times — at the Nyquist limit, the kernel hits +1 and -1 alternately (no information about phase between samples).
- For $k > N/2$: continues, but is now indistinguishable from "negative-frequency" components by aliasing.

This rotation is what makes the DFT a *projection* of $x$ onto each of the $N$ trigonometric basis functions. Each $X[k]$ measures "how much $x$ resembles a complex sinusoid at frequency $k$."

## §4. Picking a precision

In Fortran, you have:

| Precision | Type | Approximate $\varepsilon$ | Use when |
|---|---|---|---|
| Single | `real(real32)` | $\sim 10^{-7}$ | You don't care about precision; you care about speed. Stage 5 / performance work. |
| **Double** | `real(real64)` | $\sim 10^{-16}$ | **Default for canonical reference and golden-vector validation.** |
| Quad | `real(real128)` | $\sim 10^{-34}$ | High-precision oracle, sanity check against double, scientific applications with tight bounds. |

Conservative bound: rounding accumulates as $N \cdot \varepsilon$ in the DFT. For $N = 1024$ in double precision, that's $\sim 10^{-13}$ — three orders of magnitude better than the precision needed for typical engineering work.

## §5. What can go wrong (common bugs)

If your DFT output isn't matching expectations:

| Symptom | Likely cause |
|---|---|
| All outputs scaled by $N$ | Inverse-transform sign convention swapped (forward vs inverse normalisation) |
| Outputs at wrong frequency bins | Sign error in the kernel: $e^{+2\pi i k n / N}$ instead of $e^{-2\pi i k n / N}$ (or vice versa for inverse) |
| Real input gives non-Hermitian output | Loop indexing bug: $k$ and $n$ swapped, or off-by-one in the sum bound |
| Plancherel fails by orders of magnitude | Likely accumulator initialisation bug — output array contains garbage from previous run |
| Plancherel passes but golden vectors fail | Convention mismatch — your DFT uses asymmetric normalisation but the golden vector is symmetric (or vice versa). Check `dft.md` §6 |

The 4-sample example in §1 is small enough to compute by hand; if your implementation gets it right, the bigger cases usually work too.

## §6. The "negative frequencies" thing

For real-valued input, the DFT output exhibits **Hermitian symmetry**: $X[N-k] = \overline{X[k]}$. People sometimes call $X[k]$ for $k > N/2$ "negative frequencies" because they correspond to:

$$
e^{-2\pi i (N-k) n / N} = \overline{e^{-2\pi i k n / N}}
$$

— i.e. the complex conjugate of the $k$-th "positive frequency" basis function. In a frequency-axis picture, you'd plot:

```
[X[N/2+1], X[N/2+2], ..., X[N-1], X[0], X[1], ..., X[N/2]]
   ←--negative freqs---→        DC    ←--positive freqs--→
```

The Nyquist limit at $k = N/2$ marks the highest frequency representable; everything past it just mirrors the positive-frequency content (for real input) or carries genuinely independent content (for complex input).

In v0.1.0 we output $X[0..N-1]$ in natural index order. Tools like NumPy's `numpy.fft.fftshift` rearrange to centred frequency order if needed for visualisation.

## §7. The 4-sample example as a unit test

The §1 example ports directly to a Fortran test:

```fortran
@test
subroutine test_dft_pure_cosine_n4()
   use iso_fortran_env, only: dp => real64
   use lege_artis_fourier_dft, only: dft
   complex(dp) :: x(0:3), X_out(0:3), expected(0:3)

   x = [(1.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (-1.0_dp, 0.0_dp), (0.0_dp, 0.0_dp)]
   expected = [(0.0_dp, 0.0_dp), (2.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (2.0_dp, 0.0_dp)]

   X_out = dft(x)

   call assert_complex_array_equal(X_out, expected, tol=1.0e-12_dp)
end subroutine
```

This is the kind of test that catches sign bugs and indexing errors immediately. v0.1.0 ships with $N = 2, 4, 8, 16, 64$ golden vectors covering pure tones and combinations. See `backends/fortran/tests/test_dft_unit.f90`.

---

*Previous:* `00-quick-start.md`. *Next:* `02-fft-vs-dft-when-to-use-which.md`. *Canonical companion:* `../../canonical/en/01-dft-definition.md`.
