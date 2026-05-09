# Physics testbeds — DFT applied to known physics scenarios

> **Source.** Worked examples from `Thorne2017` *Modern Classical Physics*. Each testbed pairs a known physical setup with an analytical expected answer that our DFT implementation must reproduce within precision tolerance.
>
> **Companion.** `shared/property-tests/dft.md` covers algebraic properties; this document covers physics applications. Both must pass for v0.1.0.
>
> **License.** CC-BY-SA-4.0.

---

## §1. Purpose

Property tests (orthogonal document) verify the DFT respects mathematical invariants. Physics testbeds verify it produces *physically correct* answers in known-answer scenarios. The two together form a stronger validation than either alone:

- A buggy DFT could pass property tests if the bug is symmetric in a way that preserves linearity / Plancherel — but it would produce wrong physical answers.
- A correct DFT might still be misused (wrong convention, wrong normalisation) — physics testbeds catch this because they specify the input physics and expected output physics.

## §2. Testbed PT-DFT-01 — Fraunhofer diffraction (single slit)

### §2.1 Physics setup

A monochromatic plane wave of wavelength $\lambda$ illuminates a single slit of width $a$. Far from the slit (Fraunhofer regime), the diffraction pattern's amplitude $E(\theta)$ as a function of angle $\theta$ is the Fourier transform of the aperture function [@Thorne2017 §8.5].

Discretise the aperture as a length-$N$ array: $x[n] = 1$ for $n$ inside the slit, $0$ outside. The DFT $X[k]$ then gives the discrete diffraction amplitude.

### §2.2 Setup parameters

- $N = 64$ (aperture sampling)
- Slit width $a = 16$ samples (so 25 % of the array is open)
- Slit centred on the array: $x[n] = 1$ for $n \in \{24, 25, \ldots, 39\}$, $0$ elsewhere

### §2.3 Expected diffraction pattern

The continuous Fraunhofer pattern is $|E(\theta)|^2 \propto \mathrm{sinc}^2(a \sin\theta / \lambda)$ where $\mathrm{sinc}(x) = \sin(\pi x) / (\pi x)$.

The discrete equivalent — DFT of the rectangular aperture — produces $|X[k]|^2$ as a function of $k$ that has:

- **Central maximum** at $k = 0$: $|X[0]|^2 = a^2 = 16^2 = 256$
- **First zero** at $k$ where $a \cdot k / N = 1$, i.e. $k = N/a = 64/16 = 4$
- **First sidelobe** between $k = 4$ and $k = 8$, with peak height $\approx (a / \pi)^2 \cdot \mathrm{sinc}^2(1.43) \approx (16/\pi)^2 \cdot 0.047 \approx 12.2$
- **Sidelobe height ratio** to central peak: $\approx 0.047$ (the canonical first-sidelobe / central ratio for a rectangle aperture)

### §2.4 Test procedure

1. Build aperture array $x$ of length 64 per §2.2.
2. Compute $X = \mathrm{DFT}(x)$.
3. Compute power $|X[k]|^2$ for $k = 0, 1, \ldots, 32$.
4. Assert:
   - $||X[0]|^2 - 256| < 256 \cdot 10^{-12}$ (central max value, double precision)
   - $|X[4]|^2 < 10^{-12}$ (first zero — exactly, since $a \cdot k / N = 1$ is integer)
   - First sidelobe peak between $k = 4$ and $k = 8$, with magnitude in range $[10, 14]$.
   - Sidelobe-to-central-peak ratio: $\max_{k \geq 5} |X[k]|^2 / |X[0]|^2 \in [0.04, 0.05]$.

### §2.5 Citation

`Thorne2017` §8.5 — Fraunhofer diffraction by a single slit.

## §3. Testbed PT-DFT-02 — Heat-equation Green's function

### §3.1 Physics setup

The 1D heat equation $\partial_t u = \alpha \partial_x^2 u$ on a periodic domain $[0, L]$ has Green's function (impulse response) [@Thorne2017 §3.3]:

$$
G(x, t) = \frac{1}{\sqrt{4\pi\alpha t}} e^{-x^2 / (4\alpha t)}
$$

If we initialise with a delta-impulse $u(x, 0) = \delta(x - L/2)$ and evolve for time $t$, the spatial profile $u(x, t)$ is a Gaussian centred at $L/2$ with standard deviation $\sigma = \sqrt{2\alpha t}$.

In the frequency domain, the heat equation diagonalises: each Fourier mode decays exponentially as $\hat{u}_k(t) = \hat{u}_k(0) \cdot e^{-\alpha k^2 t}$.

### §3.2 Setup parameters

- $N = 64$ (spatial discretisation)
- $\alpha = 1$ (diffusion coefficient, normalised)
- $L = 2\pi$ (periodic domain)
- Initial condition: discrete impulse at $n = 32$ (centre): $x[32] = 1$, all others $0$.

### §3.3 Expected DFT

For the discrete impulse, the DFT is **constant in magnitude**:

$$
X[k] = e^{-2\pi i k \cdot 32 / 64} = e^{-i \pi k} = (-1)^k
$$

So $|X[k]| = 1$ for all $k$, with phase alternating between $0$ (for even $k$) and $\pi$ (for odd $k$).

### §3.4 Test procedure

1. Build impulse $x[n] = \delta_{n, 32}$.
2. Compute $X = \mathrm{DFT}(x)$.
3. Assert:
   - $|X[k]| = 1$ to within $10^{-13}$ for all $k$.
   - $X[k]$ is real for all $k$ (zero imaginary part within $10^{-13}$).
   - $X[k] > 0$ for even $k$, $X[k] < 0$ for odd $k$.

### §3.5 Why this matters as a physics test

A flat-magnitude Fourier transform of an impulse is the simplest non-trivial DFT result. Any sign error in the kernel, indexing bug, or phase convention drift shows up immediately. It also exercises the linearity property: for an impulse offset to position $n_0$, the DFT phase must be $-2\pi k n_0 / N$ (Property P7 — time-shift theorem).

### §3.6 Citation

`Thorne2017` §3.3 — Diffusion equation Green's function.

## §4. Testbed PT-DFT-03 — Simple harmonic oscillator (sampled cosine)

### §4.1 Physics setup

A simple harmonic oscillator at frequency $f_0$ produces a real-valued signal $s(t) = A \cos(2\pi f_0 t + \phi)$. Sampling at rate $f_s = N$ Hz over a 1-second window gives $N$ samples; if $f_0$ is integer-valued, the DFT exactly resolves the oscillator's frequency [@Thorne2017 §6.2].

For non-integer $f_0$, **spectral leakage** occurs: energy spreads into neighbouring bins because the cosine is no longer periodic on the sampling window.

### §4.2 Setup A — integer frequency (no leakage)

- $N = 64$, $f_0 = 5$ (integer), $A = 1$, $\phi = 0$
- $x[n] = \cos(2\pi \cdot 5 \cdot n / 64)$, $n = 0, 1, \ldots, 63$

### §4.3 Expected DFT for setup A

Per chapter 01 §1 of canonical-tier doc:

- $X[5] = N/2 = 32$ (positive frequency)
- $X[59] = N/2 = 32$ (negative-frequency mirror of $X[5]$ via Hermitian symmetry)
- $X[k] = 0$ for all other $k$ (within rounding)

Power concentration: 100 % of energy in two bins (5 and 59).

### §4.4 Setup B — non-integer frequency (leakage)

- $N = 64$, $f_0 = 5.5$ (half-integer), $A = 1$, $\phi = 0$
- $x[n] = \cos(2\pi \cdot 5.5 \cdot n / 64)$

### §4.5 Expected DFT for setup B

Energy spreads across many bins, with peaks near $k = 5$ and $k = 6$ (and their Hermitian mirrors at $k = 58$ and $k = 59$). Total energy still satisfies Plancherel ($\sum |X|^2 / N = \sum |x|^2 = N/2$).

### §4.6 Test procedure (setup A — primary)

1. Build $x[n] = \cos(2\pi \cdot 5 \cdot n / 64)$.
2. Compute $X = \mathrm{DFT}(x)$.
3. Assert:
   - $|X[5] - 32| < 10^{-12}$
   - $|X[59] - 32| < 10^{-12}$
   - $|X[k]| < 10^{-12}$ for all $k \notin \{5, 59\}$
   - Total energy: $\sum_k |X[k]|^2 = N \cdot \sum_n |x[n]|^2$ (Plancherel; same as Property P2)

### §4.7 Test procedure (setup B — leakage characterisation)

1. Build $x[n] = \cos(2\pi \cdot 5.5 \cdot n / 64)$.
2. Compute $X = \mathrm{DFT}(x)$.
3. Assert:
   - Plancherel still holds (energy conserved).
   - Peak magnitude bin in $\{4, 5, 6, 7\}$ (positive-frequency cluster).
   - **No assertion on exact peak location** — leakage is the point of this testbed; reproducing the *correct* leakage pattern is the validation.
4. Compare $|X[k]|^2$ profile against pre-computed reference (from `shared/golden-vectors/dft_n=64_cosine_leakage.json`).

### §4.8 Citation

`Thorne2017` §6.2 — Damped harmonic oscillator and frequency-domain analysis. Spectral-leakage discussion: `OppenheimSchafer3rd` §10.

## §5. Testbed coverage matrix for v0.1.0

| Testbed | $N$ | Source physics | Coverage |
|---|---|---|---|
| PT-DFT-01 — Fraunhofer single slit | 64 | Thorne §8.5 | Aperture function → diffraction pattern; sinc² shape verification |
| PT-DFT-02 — Heat-equation impulse | 64 | Thorne §3.3 | Impulse response → flat magnitude; sign-pattern verification |
| PT-DFT-03A — SHO integer freq | 64 | Thorne §6.2 | Pure tone → two-bin concentration; Hermitian symmetry; Plancherel |
| PT-DFT-03B — SHO leakage | 64 | Thorne §6.2 + Oppenheim §10 | Pure tone non-integer → leakage characterisation |

**Total physics-testbed assertions: 14.**

## §6. Round Zero coverage gate (additional to property tests)

Round Zero coverage audit (per ADR-05) extends to physics testbeds:

| Phys-Req | Testbed | Cross-check |
|---|---|---|
| Aperture diffraction predicts sinc² envelope | PT-DFT-01 | Property P2 (Plancherel within band) |
| Impulse response is flat-magnitude in frequency | PT-DFT-02 | Property P3 (DC = sum) + Property P7 (time-shift) |
| Pure tone resolves to integer bin | PT-DFT-03A | Property P4 (Hermitian) + Property P2 (Plancherel) |
| Spectral leakage profile is correct | PT-DFT-03B | Golden vector cross-check |

Each physics testbed cross-references at least one property test. No orphans. Round Zero green.

---

*End of `dft.md` physics-testbeds spec.*
