# Property tests — Discrete Fourier Transform

> **Companion equations file.** `shared/canonical-equations/dft.{md,tex}`.
> **Implementation tests** that consume this spec: `backends/<lang>/tests/test_dft_property.<ext>`.
> **License.** CC-BY-SA-4.0.

---

## §1. Purpose

This document specifies the algebraic / analytical properties that any correct DFT implementation must satisfy. Each property is a one-line invariant: an equation relating inputs and outputs that holds within a stated precision tolerance.

These tests **complement** golden-vector tests:

- **Golden vectors** (`shared/golden-vectors/`): "given input X, output must equal pre-computed Y to within ε." Catches numerical regression against an independent oracle.
- **Property tests** (this document): "for any valid input, this invariant must hold." Catches structural bugs (sign errors, indexing, normalisation conventions) that golden vectors might miss if the convention happens to match the bug.

Both types of tests must pass for v0.1.0.

## §2. Notation

Let $\mathrm{DFT}: \mathbb{C}^N \to \mathbb{C}^N$ denote our DFT implementation. Inputs are $x = (x[0], \ldots, x[N-1])$; outputs are $X = (X[0], \ldots, X[N-1])$.

Convention: asymmetric forward (no $1/N$ in forward, $1/N$ in inverse) per `dft.md` §6.

Precision tolerance per tier (per `IEEE754_2019`):

| Tier | $\varepsilon_{\text{tier}}$ | Test gate $C \cdot N \cdot \varepsilon$ ($C = 2$) |
|---|---|---|
| Single (binary32) | $\approx 1.19 \times 10^{-7}$ | $2.4 N \times 10^{-7}$ |
| Double (binary64) | $\approx 2.22 \times 10^{-16}$ | $4.4 N \times 10^{-16}$ |
| Quad (binary128) | $\approx 1.93 \times 10^{-34}$ | $3.9 N \times 10^{-34}$ |

For $N = 1024$ in double precision, tolerance ≈ $4.5 \times 10^{-13}$ — well above any meaningful precision regression.

## §3. Properties

### Property P1 — Linearity

**Statement.** For scalars $\alpha, \beta \in \mathbb{C}$ and inputs $x, y \in \mathbb{C}^N$:

$$
\mathrm{DFT}(\alpha x + \beta y) = \alpha \cdot \mathrm{DFT}(x) + \beta \cdot \mathrm{DFT}(y)
$$

**Test procedure.**
1. Generate two random complex inputs $x, y$ of length $N$.
2. Pick two random complex scalars $\alpha, \beta$.
3. Compute LHS: $\mathrm{DFT}(\alpha x + \beta y)$.
4. Compute RHS: $\alpha \cdot \mathrm{DFT}(x) + \beta \cdot \mathrm{DFT}(y)$.
5. Assert $\| \text{LHS} - \text{RHS} \|_\infty \leq C \cdot N \cdot \varepsilon$ with $C = 2$.

**Coverage.** Test at lengths $N \in \{4, 8, 16, 64, 1024\}$.

**Reference:** `dft.md` Eq. DFT-4, `dft.tex` Theorem 1.

### Property P2 — Plancherel / Parseval

**Statement.**

$$
\sum_{n=0}^{N-1} |x[n]|^2 = \frac{1}{N} \sum_{k=0}^{N-1} |X[k]|^2
$$

**Test procedure.**
1. Generate random complex input $x$ of length $N$.
2. Compute $X = \mathrm{DFT}(x)$.
3. Compute $E_{\text{time}} = \sum_n |x[n]|^2$.
4. Compute $E_{\text{freq}} = \frac{1}{N} \sum_k |X[k]|^2$.
5. Assert $|E_{\text{time}} - E_{\text{freq}}| \leq C \cdot N \cdot \varepsilon \cdot \max(E_{\text{time}}, E_{\text{freq}})$ with $C = 2$.

**Coverage.** $N \in \{4, 8, 16, 64, 1024\}$.

**Reference:** `dft.md` Eq. DFT-5, `dft.tex` Theorem 2.

### Property P3 — DC component

**Statement.**

$$
X[0] = \sum_{n=0}^{N-1} x[n]
$$

**Test procedure.**
1. Generate random complex input $x$.
2. Compute $X = \mathrm{DFT}(x)$.
3. Compute $S = \sum_n x[n]$ (direct sum).
4. Assert $|X[0] - S| \leq C \cdot N \cdot \varepsilon \cdot \max(|S|, 1)$ with $C = 1$.

**Coverage.** $N \in \{4, 8, 16, 64\}$.

**Reference:** `dft.md` Eq. DFT-1 at $k = 0$ (kernel reduces to 1 exactly).

### Property P4 — Hermitian symmetry for real inputs

**Statement.** For real-valued input $x \in \mathbb{R}^N$ and $k \in \{1, \ldots, N-1\}$:

$$
X[N - k] = \overline{X[k]}
$$

**Test procedure.**
1. Generate random real input $x$.
2. Compute $X = \mathrm{DFT}(x)$.
3. For each $k \in \{1, \ldots, N-1\}$, assert $|X[N-k] - \overline{X[k]}| \leq C \cdot N \cdot \varepsilon$ with $C = 2$.

**Coverage.** $N \in \{4, 8, 16, 64, 1024\}$.

**Reference:** `dft.md` §2 (kernel symmetry); chapter 01 §6.

### Property P5 — FFT ≡ DFT (for $N = 2^m$)

**Statement.** For $N = 2^m$ and any input $x \in \mathbb{C}^N$:

$$
\mathrm{FFT}(x) = \mathrm{DFT}(x) \pm O(\log_2(N) \cdot \varepsilon \cdot \|x\|)
$$

**Test procedure** (only meaningful at v0.2.0+ when FFT lands; v0.1.0 ships DFT only):
1. Generate random complex input $x$ of length $N = 2^m$.
2. Compute $X_{\text{DFT}} = \mathrm{DFT}(x)$ and $X_{\text{FFT}} = \mathrm{FFT}(x)$.
3. Assert $\| X_{\text{FFT}} - X_{\text{DFT}} \|_\infty \leq C \cdot \log_2(N) \cdot \varepsilon \cdot \|x\|_\infty$ with $C = 4$.

**Coverage.** $N \in \{4, 8, 16, 64, 1024, 4096\}$ (powers of 2).

**Reference:** `fft-cooley-tukey.md` Eq. FFT-7/FFT-8.

### Property P6 — Inverse DFT recovers input

**Statement.**

$$
x = \mathrm{IDFT}(\mathrm{DFT}(x))
$$

where the inverse uses the asymmetric convention (factor $1/N$ in inverse).

**Test procedure** (requires IDFT — v0.1.0 ships forward only; this test activates v0.1.1+).
1. Generate random complex input $x$.
2. Compute $X = \mathrm{DFT}(x)$.
3. Compute $x' = \mathrm{IDFT}(X)$.
4. Assert $\| x - x' \|_\infty \leq C \cdot N \cdot \varepsilon \cdot \|x\|_\infty$ with $C = 2$.

**Coverage.** $N \in \{4, 8, 16, 64, 1024\}$ (when IDFT is implemented).

**Reference:** `dft.md` Eq. DFT-2.

### Property P7 — Time-shift theorem

**Statement.** Let $y[n] = x[(n - n_0) \mod N]$ (circular shift by $n_0$). Then:

$$
Y[k] = e^{-2\pi i k n_0 / N} \cdot X[k]
$$

**Test procedure.**
1. Generate random input $x$, pick random shift $n_0 \in \{1, \ldots, N-1\}$.
2. Compute shifted $y$.
3. Compute $X = \mathrm{DFT}(x)$ and $Y = \mathrm{DFT}(y)$.
4. For each $k$, compute expected $Y_{\text{expected}}[k] = e^{-2\pi i k n_0 / N} \cdot X[k]$.
5. Assert $\| Y - Y_{\text{expected}} \|_\infty \leq C \cdot N \cdot \varepsilon$ with $C = 2$.

**Coverage.** $N \in \{8, 16, 64\}$.

**Reference:** Standard property; see `OppenheimSchafer3rd` §8.4.

### Property P8 — Convolution theorem

**Statement.** For sequences $x, h \in \mathbb{C}^N$ with circular convolution $z[n] = \sum_{m=0}^{N-1} x[m] h[(n-m) \mod N]$:

$$
\mathrm{DFT}(z) = \mathrm{DFT}(x) \cdot \mathrm{DFT}(h)
$$

(elementwise multiplication on the right).

**Test procedure.**
1. Generate random $x, h$ of length $N$.
2. Compute circular convolution $z$ directly (slow, $O(N^2)$).
3. Compute LHS = $\mathrm{DFT}(z)$.
4. Compute RHS = $\mathrm{DFT}(x) \odot \mathrm{DFT}(h)$ (elementwise).
5. Assert $\| \text{LHS} - \text{RHS} \|_\infty \leq C \cdot N \cdot \varepsilon \cdot \|x\| \cdot \|h\|$ with $C = 4$.

**Coverage.** $N \in \{8, 16, 64\}$.

**Reference:** `OppenheimSchafer3rd` §8.5; `Folland1992` §1.5.

## §4. Test naming convention

Per backend, test files follow the pattern `test_dft_property.{f90,cpp,rs,pas}` with subroutines / functions named `test_dft_p{N}_{name}`:

```
test_dft_p1_linearity
test_dft_p2_plancherel
test_dft_p3_dc_component
test_dft_p4_hermitian_real_input
test_dft_p5_fft_dft_equivalence    (v0.2.0+)
test_dft_p6_inverse_recovers       (v0.1.1+)
test_dft_p7_time_shift
test_dft_p8_convolution
```

## §5. Reporting

Each test outputs:

```
[P1 linearity   ] N=  16  PASS  max-err = 8.88e-16  (gate 1.42e-14)
[P1 linearity   ] N=  64  PASS  max-err = 1.78e-15  (gate 5.68e-14)
...
[P2 plancherel  ] N=1024  PASS  rel-err = 4.44e-15  (gate 4.55e-13)
```

A failure prints the full input that triggered it (or a hash + seed for reproducible regeneration), the actual vs expected output near the failure index, and the gate that was missed.

## §6. Coverage matrix

For v0.1.0, the canonical-tier reference:

| Property | $N=2$ | $N=4$ | $N=8$ | $N=16$ | $N=64$ | $N=1024$ |
|---|---|---|---|---|---|---|
| P1 linearity | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| P2 plancherel | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| P3 DC | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| P4 hermitian | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| P5 FFT≡DFT | — | — | — | — | — | — (activates v0.2.0+) |
| P6 inverse | — | — | — | — | — | — (activates v0.1.1+) |
| P7 time-shift | — | — | ✓ | ✓ | ✓ | — |
| P8 convolution | — | — | ✓ | ✓ | ✓ | — |

**Total v0.1.0 property-test count:** 25 test invocations across P1-P4, P7, P8.

## §7. Round Zero coverage gate

R-COVERAGE-ZERO (per CLAUDE.md ADR-05) requires that:
- Every requirement in `01_Requirements` (the canonical-equation properties) maps to at least one test in this document.
- Every test in this document maps to at least one requirement.
- No orphans on either side.

The requirements covered:

| Req-id | Property | Test |
|---|---|---|
| REQ-DFT-DEF | DFT formula correctness | P3 (DC) + P4 (Hermitian) + golden vectors |
| REQ-DFT-LIN | Linearity | P1 |
| REQ-DFT-PLA | Plancherel | P2 |
| REQ-FFT-EQUIV | FFT ≡ DFT | P5 (v0.2.0+) |
| REQ-DFT-INV | Inverse roundtrip | P6 (v0.1.1+) |
| REQ-DFT-SHIFT | Time-shift theorem | P7 |
| REQ-DFT-CONV | Convolution theorem | P8 |

Round Zero audit verifies this matrix has no orphan-rows / orphan-columns; passes for v0.1.0.

---

*End of `dft.md` property-tests spec.*
