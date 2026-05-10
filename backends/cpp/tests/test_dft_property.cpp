// SPDX-License-Identifier: Apache-2.0
//
// test_dft_property.cpp - Property tests for the C++ DFT kernel
//
// Properties tested (per shared/property-tests/dft.md):
//   P1 Linearity:    dft(alpha*x + beta*y) == alpha*dft(x) + beta*dft(y)
//   P2 Plancherel:   sum(|x|^2) == sum(|X|^2) / N
//   P3 DC bin:       X[0] == sum(x)
//   P4 Hermitian:    if x real, X[k] == conj(X[N-k])
//   P7 Time-shift:   dft(x_shifted)[k] == X[k] * exp(-2*pi*i*k*m/N)
//   P8 Convolution:  dft(circ-conv(x, y))[k] == X[k] * Y[k]
//
// (P5 FFT-equivalence deferred to v0.2.0 FFT; P6 inverse-roundtrip already
// in test_dft_unit.)
//
// Concrete inputs LOCKED per Stage-4 SONNET-HANDOFF section 2.1 - same as
// Fortran property suite. Source kept ASCII-only.

#include "lege_artis_fourier/dft_kernel.hpp"
#include "test_harness.hpp"

#include <cmath>
#include <complex>
#include <vector>

using namespace lege_artis::fourier;
using lege_artis::fourier::testing::assert_complex_array_close;
using lege_artis::fourier::testing::assert_complex_close;
using lege_artis::fourier::testing::assert_real_close;
using lege_artis::fourier::testing::print_summary;
using lege_artis::fourier::testing::print_title;

static const double PI = 4.0 * std::atan(1.0);

// -- P1 Linearity -------------------------------------------------------------
static void test_p1_linearity(int& total, int& failed) {
    const std::size_t N = 8;
    const cdouble alpha{2.5, -0.3};
    const cdouble beta{-1.0, 1.2};

    cvector x(N), y(N), z(N);
    for (std::size_t i = 0; i < N; ++i) {
        const double r = static_cast<double>(i + 1);
        x[i] = cdouble{r, 2.0 * r};
        y[i] = cdouble{3.0 * r - 1.0, -r};
        z[i] = alpha * x[i] + beta * y[i];
    }

    const cvector X_out = dft(x);
    const cvector Y_out = dft(y);
    const cvector Z_out = dft(z);

    cvector expected(N);
    for (std::size_t i = 0; i < N; ++i) {
        expected[i] = alpha * X_out[i] + beta * Y_out[i];
    }
    assert_complex_array_close(total, failed, "test_p1_linearity (N=8)",
                               Z_out, expected, 1.0e-13);
}

// -- P2 Plancherel ------------------------------------------------------------
static void test_p2_plancherel(int& total, int& failed) {
    const std::size_t N = 16;
    cvector x(N);
    for (std::size_t i = 0; i < N; ++i) {
        const double r = static_cast<double>(i + 1);
        x[i] = cdouble{0.7 * r, 0.5 * r - 2.0};
    }

    const cvector X_out = dft(x);

    double lhs = 0.0;
    for (const auto& v : x) lhs += std::norm(v);  // sum |x|^2
    double rhs = 0.0;
    for (const auto& v : X_out) rhs += std::norm(v);
    rhs /= static_cast<double>(N);  // sum |X|^2 / N

    // Gate scaled by lhs (KB-040 floor-1 doesn't apply here since lhs >> 1).
    const double tol = 1.0e-13 * lhs;
    assert_real_close(total, failed, "test_p2_plancherel (N=16)",
                      rhs, lhs, tol);
}

// -- P3 DC bin ----------------------------------------------------------------
static void test_p3_dc_bin(int& total, int& failed) {
    const std::size_t N = 8;
    cvector x(N);
    cdouble expected_dc{0.0, 0.0};
    for (std::size_t i = 0; i < N; ++i) {
        const double r = static_cast<double>(i + 1);
        x[i] = cdouble{r, 0.3 * r};
        expected_dc += x[i];
    }

    const cvector X_out = dft(x);
    assert_complex_close(total, failed, "test_p3_dc_bin (N=8)",
                         X_out[0], expected_dc, 1.0e-13);
}

// -- P4 Hermitian (real input -> conjugate-symmetric spectrum) ----------------
static void test_p4_hermitian(int& total, int& failed) {
    const std::size_t N = 8;
    cvector x(N);
    for (std::size_t i = 0; i < N; ++i) {
        const double r = static_cast<double>(i + 1);
        x[i] = cdouble{0.5 * r - 1.5, 0.0};  // real-valued
    }

    const cvector X_out = dft(x);

    // Build expected mirror: expected[k] = conj(X_out[N-k]) for k=1..N-1
    // (X_out[0] should equal its own conjugate, i.e. be real.)
    cvector mirror(N);
    mirror[0] = std::conj(X_out[0]);
    for (std::size_t k = 1; k < N; ++k) {
        mirror[k] = std::conj(X_out[N - k]);
    }

    assert_complex_array_close(total, failed,
                               "test_p4_hermitian (N=8, k=0..7)",
                               X_out, mirror, 1.0e-13);
}

// -- P7 Time-shift ------------------------------------------------------------
static void test_p7_time_shift(int& total, int& failed) {
    const std::size_t N = 8;
    const int m = 3;  // circular shift amount

    cvector x(N), x_shifted(N);
    for (std::size_t i = 0; i < N; ++i) {
        const double r = static_cast<double>(i + 1);
        x[i] = cdouble{0.4 * r, 0.7 * r - 1.0};
    }
    // x_shifted[n] = x[(n - m) mod N]
    for (std::size_t n = 0; n < N; ++n) {
        const int src = (static_cast<int>(n) - m) % static_cast<int>(N);
        const int wrapped = (src < 0) ? (src + static_cast<int>(N)) : src;
        x_shifted[n] = x[static_cast<std::size_t>(wrapped)];
    }

    const cvector X_out = dft(x);
    const cvector X_shifted_out = dft(x_shifted);

    // Expected: X_shifted[k] = X[k] * exp(-2*pi*i*k*m/N)
    cvector expected(N);
    for (std::size_t k = 0; k < N; ++k) {
        const double omega = -2.0 * PI * static_cast<double>(k) * static_cast<double>(m) / static_cast<double>(N);
        expected[k] = X_out[k] * cdouble{std::cos(omega), std::sin(omega)};
    }

    assert_complex_array_close(total, failed,
                               "test_p7_time_shift (N=8, m=3)",
                               X_shifted_out, expected, 1.0e-13);
}

// -- P8 Convolution theorem ---------------------------------------------------
static void test_p8_convolution(int& total, int& failed) {
    const std::size_t N = 8;
    cvector x(N), y(N), z(N, cdouble{0.0, 0.0});

    // x = [1..8] real
    for (std::size_t i = 0; i < N; ++i) {
        x[i] = cdouble{static_cast<double>(i + 1), 0.0};
    }
    // y = [0.5, 1, 1.5, 2, 1.5, 1, 0.5, 0]
    const double y_vals[] = {0.5, 1.0, 1.5, 2.0, 1.5, 1.0, 0.5, 0.0};
    for (std::size_t i = 0; i < N; ++i) {
        y[i] = cdouble{y_vals[i], 0.0};
    }

    // Circular convolution: z[n] = sum_{m} x[m] * y[(n-m) mod N]
    for (std::size_t n = 0; n < N; ++n) {
        for (std::size_t m = 0; m < N; ++m) {
            const int idx = (static_cast<int>(n) - static_cast<int>(m)) % static_cast<int>(N);
            const int wrapped = (idx < 0) ? (idx + static_cast<int>(N)) : idx;
            z[n] += x[m] * y[static_cast<std::size_t>(wrapped)];
        }
    }

    const cvector X_out = dft(x);
    const cvector Y_out = dft(y);
    const cvector Z_out = dft(z);

    // Expected: Z[k] = X[k] * Y[k] (element-wise)
    cvector expected(N);
    for (std::size_t k = 0; k < N; ++k) {
        expected[k] = X_out[k] * Y_out[k];
    }

    // P8 has a wider gate per Stage-4 lessons: convolution accumulates more
    // round-off; gate calibrated to ~9.1e-13 in Fortran reference.
    assert_complex_array_close(total, failed, "test_p8_convolution (N=8)",
                               Z_out, expected, 9.095e-13);
}

int main() {
    print_title("lege-artis/fourier - DFT property tests (v0.2.0 C++ ref)");

    int total = 0, failed = 0;
    test_p1_linearity(total, failed);
    test_p2_plancherel(total, failed);
    test_p3_dc_bin(total, failed);
    test_p4_hermitian(total, failed);
    test_p7_time_shift(total, failed);
    test_p8_convolution(total, failed);

    return print_summary(total, failed);
}
