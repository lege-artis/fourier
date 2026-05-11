// SPDX-License-Identifier: Apache-2.0
//
// dft_kernel.cpp - Canonical DFT reference (C++17 port of v0.1.0 Fortran)
//
// See dft_kernel.hpp for full documentation, equation-to-code mapping,
// implementation discipline rationale, and convention reference.
//
// This implementation is intentionally O(N^2) and intentionally not
// optimised. v0.5+ Stage 5 introduces -O3 -march=native build target
// against the same source.

#include "lege_artis_fourier/dft_kernel.hpp"

#include <cmath>
#include <cstddef>

namespace lege_artis::fourier {

namespace {

// Mathematical constants in double precision.
// Use 4*atan(1) rather than M_PI (POSIX-only) or std::numbers::pi (C++20)
// to keep the source portable across C++17-conforming compilers.
const double PI     = 4.0 * std::atan(1.0);
const double TWO_PI = 2.0 * PI;

}  // anonymous namespace

cvector dft(const cvector& x) {
    const std::size_t nlen = x.size();
    cvector X_out(nlen);

    // Outer sum over k (one DFT output per iteration)
    for (std::size_t k = 0; k < nlen; ++k) {
        cdouble sum{0.0, 0.0};
        // Inner sum over n (the canonical Eq. DFT-1 sum)
        for (std::size_t n = 0; n < nlen; ++n) {
            // Argument of the kernel: -2*pi*k*n/N (Eq. DFT-1 exponent)
            const double omega = -TWO_PI
                * static_cast<double>(k * n)
                / static_cast<double>(nlen);
            // Accumulate: x[n] * exp(i*omega) = x[n] * (cos(omega) + i*sin(omega))
            sum += x[n] * cdouble{std::cos(omega), std::sin(omega)};
        }
        X_out[k] = sum;
    }
    return X_out;
}

cvector idft(const cvector& X_in) {
    const std::size_t nlen = X_in.size();
    cvector x_out(nlen);

    // Outer sum over n (one time-domain output per iteration)
    for (std::size_t n = 0; n < nlen; ++n) {
        cdouble sum{0.0, 0.0};
        for (std::size_t k = 0; k < nlen; ++k) {
            // Inverse kernel: +2*pi*k*n/N (sign flipped vs forward)
            const double omega = +TWO_PI
                * static_cast<double>(k * n)
                / static_cast<double>(nlen);
            sum += X_in[k] * cdouble{std::cos(omega), std::sin(omega)};
        }
        // Asymmetric inverse normalisation: factor 1/N
        x_out[n] = sum / static_cast<double>(nlen);
    }
    return x_out;
}

}  // namespace lege_artis::fourier
