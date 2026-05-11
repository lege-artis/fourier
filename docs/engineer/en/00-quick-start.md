# lege-artis/fourier — engineer tier — Quick start (EN)

> **Audience.** Software engineer, data scientist, hobbyist. You want to use the Fourier algorithms, understand what they compute, and validate that the results are right. You probably don't need theorem-proof rigor — you need a working mental model and runnable code.
>
> **Reading time.** ~10 minutes for this Quick Start. ~30 minutes for the full engineer tier.
>
> **License.** CC-BY-SA-4.0.
>
> **Companion.** Canonical-tier `docs/canonical/en/00-introduction.md` covers the same scope from the math-rigor angle.

---

## §1. What this library does

In one sentence: **transforms a sequence of numbers into another sequence that says "how much of each pure tone is in your signal."**

Three algorithms:

| Algorithm | What you give it | What you get back |
|---|---|---|
| **DFT** (Discrete Fourier Transform) | A list of $N$ numbers (samples of your signal) | A list of $N$ complex numbers, one per frequency bin |
| **FFT** (Fast Fourier Transform) | Same as DFT, but $N$ must be a power of 2 | Same output as DFT, computed *much* faster |
| **PSF** (Partial Sum of Fourier Series) | Fourier coefficients of a periodic function + a point $x$ | The reconstructed function value at $x$ |

The DFT and FFT compute the same thing — the FFT is just an algorithmic shortcut when $N$ is a power of 2. If accuracy or arbitrary $N$ is your priority, use DFT. If speed and your $N$ is a power of 2, use FFT.

## §2. The "what does Fourier actually compute" intuition

Imagine you record a sound for one second at 1000 samples per second. You now have $N = 1000$ numbers. The DFT (or FFT) gives you back $N = 1000$ complex numbers $X[0], X[1], \ldots, X[999]$.

| Output | What it means |
|---|---|
| $X[0]$ | The "DC" — total / average of all input samples |
| $X[1]$ | How much "1 cycle per second" tone is in your input |
| $X[2]$ | How much "2 cycles per second" tone |
| ... | ... |
| $X[500]$ | How much "500 cycles per second" tone (this is the **Nyquist limit** — the highest frequency you can detect with 1000 samples/sec sampling) |
| $X[501..999]$ | "Negative frequencies" — for a real-valued input these mirror $X[1..499]$ (Hermitian symmetry) |

The magnitude $|X[k]|$ tells you "amplitude at this frequency"; the phase $\arg(X[k])$ tells you "where in its cycle is this frequency at $t = 0$". Most engineering uses care about magnitude and call $|X[k]|^2$ the **power spectrum**.

## §3. Hello-World example (Fortran reference)

```fortran
program hello_dft
  use iso_fortran_env, only: dp => real64
  use lege_artis_fourier_dft, only: dft
  implicit none

  integer, parameter      :: N = 8
  complex(dp), allocatable :: x(:), X_out(:)
  real(dp)                :: pi
  integer                 :: n_idx

  pi = 4.0_dp * atan(1.0_dp)
  allocate(x(0:N-1))
  allocate(X_out(0:N-1))

  ! Input: pure cosine wave at frequency k = 1, sampled over 1 period
  do n_idx = 0, N - 1
     x(n_idx) = cmplx(cos(2.0_dp * pi * real(n_idx, dp) / real(N, dp)), 0.0_dp, kind=dp)
  end do

  ! Compute DFT
  X_out = dft(x)

  ! Print: should show |X(1)| ≈ N/2 = 4, |X(N-1)| ≈ 4 (real input → Hermitian)
  ! All other |X(k)| ≈ 0 (within ε)
  do n_idx = 0, N - 1
     write(*, '(A, I0, A, F12.6, A, F12.6, A)') &
        'X(', n_idx, ') = ', real(X_out(n_idx)), ' + ', aimag(X_out(n_idx)), 'i'
  end do
end program hello_dft
```

**Expected output** (within rounding):

```
X(0) = 0.000000 + 0.000000i      ← DC (no constant offset in pure cosine)
X(1) = 4.000000 + 0.000000i      ← N/2 — half the signal energy at k=1
X(2) = 0.000000 + 0.000000i
X(3) = 0.000000 + 0.000000i
X(4) = 0.000000 + 0.000000i
X(5) = 0.000000 + 0.000000i
X(6) = 0.000000 + 0.000000i
X(7) = 4.000000 + 0.000000i      ← Hermitian mirror of X(1)
```

A pure cosine wave at integer-frequency $k = 1$ over $N$ samples produces magnitude $N/2$ at $X[1]$ and (by Hermitian symmetry for real input) $N/2$ at $X[N-1]$. Everything else should be zero.

If you ran this and got something different, either (a) you have a sign bug in your DFT, or (b) your input wasn't actually a pure cosine. Use this as your sanity check.

## §4. Quick reference — when to use what

| Situation | Recommended | Why |
|---|---|---|
| You're learning what Fourier methods do | DFT | Direct from the formula; easy to inspect |
| Your $N$ is a power of 2 and you want speed | FFT | Same answer as DFT, $N \log N$ vs $N^2$ |
| Your $N$ is *not* a power of 2 (e.g. 1000, 1024 is, 1500 is not) | **v0.1.0:** DFT (FFT requires $N = 2^m$). **v0.5+:** mixed-radix FFT or Bluestein (Stage 5) | DFT works for any $N$ |
| You need to reconstruct a function from its samples | PSF (partial sum of Fourier series) | Reverses the DFT for periodic functions |
| You need extreme numerical precision | DFT in quad precision (binary128) | DFT rounding is well-understood; quad precision pushes ε down to $\sim 2^{-112}$ |
| You need extreme speed and don't care about clarity | wait for Stage 5 / v0.5+ | The current v0.1.0 reference is `-O0 -fcheck=all` — clarity over speed |

## §5. The "what does Fourier *not* do" caveats

Five common confusions:

| Misconception | What's actually true |
|---|---|
| "DFT gives me frequencies in Hz" | DFT outputs are indexed $k = 0, 1, \ldots, N-1$; you get frequencies in Hz only after multiplying by $f_s / N$ where $f_s$ is your sampling rate |
| "I can detect any frequency in my signal" | Only frequencies up to the **Nyquist limit** $f_s / 2$ — anything higher gets *aliased* onto a lower frequency. If you sampled at 1000 Hz, you can't detect 600 Hz; it shows up as 400 Hz |
| "DFT of a real signal is real" | False — DFT of a real signal is *Hermitian*: $X[N-k] = \overline{X[k]}$. The output is generally complex; only $X[0]$ and (for even $N$) $X[N/2]$ are guaranteed real |
| "FFT and DFT might give different answers" | In exact arithmetic, identical. In floating-point, they differ by a small amount: the FFT is actually *more accurate* for large $N$ (less accumulated rounding) |
| "Gibbs phenomenon means my code has a bug" | False — Gibbs is a real mathematical property of Fourier-series partial sums at jump discontinuities. Any correct implementation of PSF will show it. See the Square Wave testbed in `shared/physics-testbeds/dft.md` |

## §6. Validation: how to know it works

The library ships with three validation layers:

1. **Property tests** (`shared/property-tests/dft.md`): linearity, Plancherel, DC component, Nyquist symmetry, FFT≡DFT equivalence. Each is a one-line invariant your output must satisfy.
2. **Golden vectors** (`shared/golden-vectors/dft_n=*.json`): inputs paired with outputs from independent oracles (SciPy, NumPy, Wolfram). Your code's output must match within precision-tier ε.
3. **Physics testbeds** (`shared/physics-testbeds/dft.md`): the algorithms applied to known physics scenarios (Fraunhofer diffraction pattern, heat-equation Green's function, etc.). The output must match analytical predictions from `Thorne2017`.

Running them: see `backends/fortran/tests/README.md` for v0.1.0; equivalent test entry points in C++ / Rust / Pascal at v0.2.0+.

## §7. License + funding

Code under Apache 2.0 (`LICENSE`); documentation under CC-BY-SA-4.0 (`LICENSE-DOCS`); names protected (`TRADEMARK.md`). Voluntary support via `.github/FUNDING.yml` (GitHub Sponsors / Patreon / PayPal — populated at first PUBLIC push, currently private repo during pre-v0.1.0 development).

## §8. Multilingual roadmap

This `docs/engineer/en/` content is the EN baseline. Translations to CS / JA / DE / IT follow at v0.1.1+ — see `docs/canonical/en/00-introduction.md` §7 for the full multilingual plan.

---

*Next:* `01-what-dft-actually-computes.md` — a longer worked example explaining the DFT mechanics step by step.
