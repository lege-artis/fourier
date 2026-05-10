// SPDX-License-Identifier: Apache-2.0
//
// dft_kernel.hpp - Canonical DFT reference (C++17 port of v0.1.0 Fortran)
//
// Faithful translation of shared/canonical-equations/dft.md Eq. DFT-1:
//
//     X[k] = SUM_{n=0..N-1} x[n] * exp(-2*pi*i*k*n/N),  k = 0..N-1
//
// Convention: asymmetric forward (no 1/N in forward; 1/N in inverse).
// Matches OppenheimSchafer3rd section 8.2 and numpy.fft.fft.
//
// Implementation discipline (per WORKING-SPEC-v0.3-EN.md section 4):
//   - Code is line-by-line translation of the canonical equation.
//   - No external library (no FFTW, no Eigen, no Boost).
//   - Precision: IEEE 754 binary64 (double / std::complex<double>).
//   - Compiled with -O0 -g -Wall -Wextra -Wpedantic -std=c++17 for v0.2.0
//     reference clarity. Performance build (Stage 5 / v0.5+) uses -O3 etc.
//   - Source kept ASCII-only (KB-039 rule symmetric across languages).
//
// Equation -> code mapping (per dft.md section 2):
//
//   Math (Eq. DFT-1)              | Code
//   ------------------------------|------------------------------
//   Outer sum over k              | for (int k = 0; k < nlen; ++k)
//   X[k] = 0 initial              | cdouble sum{0.0, 0.0};
//   Inner sum over n              | for (int n = 0; n < nlen; ++n)
//   Argument -2*pi*k*n/N          | omega = -TWO_PI * (k*n) / nlen
//   exp(i*omega) = cos + i*sin    | cdouble{cos(omega), sin(omega)}
//   Multiply x[n] by kernel       | x[n] * cdouble{...}
//   Accumulate                    | sum += ...
//   Store                         | X_out[k] = sum;
//
// Note: nlen holds the sequence length N from Eq. DFT-1. Native C++ 0-based
// indexing aligns naturally with the equation (no Fortran 1-based offset).

#pragma once

#include <complex>
#include <vector>

namespace lege_artis::fourier {

// Type aliases for legibility across kernel + tests.
using cdouble = std::complex<double>;
using cvector = std::vector<cdouble>;

// Forward DFT - direct evaluation of dft.md Eq. DFT-1.
// @param  x   Input sequence x[0..N-1]
// @return X   Output sequence X[0..N-1]
// @complexity O(N^2) - direct double-loop. The FFT (v0.2.0+) reduces this
//             to O(N log N) for N = 2^m. v0.1.x reference is intentionally
//             O(N^2) for clarity vs the canonical equation.
cvector dft(const cvector& x);

// Inverse DFT - dft.md Eq. DFT-2 (asymmetric convention, factor 1/N in inverse).
// @param  X   Frequency-domain sequence X[0..N-1]
// @return x   Time-domain sequence x[0..N-1]
// @complexity O(N^2)
cvector idft(const cvector& X_in);

}  // namespace lege_artis::fourier
