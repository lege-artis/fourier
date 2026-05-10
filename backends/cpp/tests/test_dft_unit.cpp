// SPDX-License-Identifier: Apache-2.0
//
// test_dft_unit.cpp - Unit tests for the C++ DFT kernel
//
// Mirrors backends/fortran/tests/test_dft_unit.f90 - same 5 tests, same
// inputs, same gates. Source kept ASCII-only.
//
// Tests included:
//   - test_dft_n4_pure_cosine - section-1 worked example from docs
//   - test_dft_n4_dc_input    - DC input -> DC output
//   - test_dft_n4_impulse_at_centre - impulse -> X[k] = (-1)^k
//   - test_dft_n8_pure_cosine - same shape, larger N
//   - test_dft_idft_roundtrip_n8 - inverse recovers input

#include "lege_artis_fourier/dft_kernel.hpp"
#include "test_harness.hpp"

#include <cmath>
#include <vector>

using namespace lege_artis::fourier;
using lege_artis::fourier::testing::assert_complex_array_close;
using lege_artis::fourier::testing::print_summary;
using lege_artis::fourier::testing::print_title;

static void test_dft_n4_pure_cosine(int& total, int& failed) {
    // x = [1, 0, -1, 0]  (pure cosine at k=1, N=4)
    // Expected: X = [0, 2, 0, 2]
    const cvector x        = {{1.0, 0.0}, {0.0, 0.0}, {-1.0, 0.0}, {0.0, 0.0}};
    const cvector expected = {{0.0, 0.0}, {2.0, 0.0}, {0.0, 0.0}, {2.0, 0.0}};
    const double tol = 1.0e-13;

    const cvector X_out = dft(x);
    assert_complex_array_close(total, failed, "test_dft_n4_pure_cosine",
                               X_out, expected, tol);
}

static void test_dft_n4_dc_input(int& total, int& failed) {
    // x = [1, 1, 1, 1]  (DC, all unit)
    // Expected: X = [4, 0, 0, 0]
    const cvector x        = {{1.0, 0.0}, {1.0, 0.0}, {1.0, 0.0}, {1.0, 0.0}};
    const cvector expected = {{4.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}};
    const double tol = 1.0e-13;

    const cvector X_out = dft(x);
    assert_complex_array_close(total, failed, "test_dft_n4_dc_input",
                               X_out, expected, tol);
}

static void test_dft_n4_impulse_at_centre(int& total, int& failed) {
    // x = [0, 0, 1, 0] (impulse at n=2, N=4)
    // X[k] = exp(-2*pi*i*k*2/4) = exp(-pi*i*k) = (-1)^k
    const cvector x        = {{0.0, 0.0}, {0.0, 0.0}, {1.0, 0.0}, {0.0, 0.0}};
    const cvector expected = {{1.0, 0.0}, {-1.0, 0.0}, {1.0, 0.0}, {-1.0, 0.0}};
    const double tol = 1.0e-13;

    const cvector X_out = dft(x);
    assert_complex_array_close(total, failed, "test_dft_n4_impulse_at_centre",
                               X_out, expected, tol);
}

static void test_dft_n8_pure_cosine(int& total, int& failed) {
    // N=8 cosine at k=1: x[n] = cos(2*pi*1*n/8)
    // Expected: X[1] = X[7] = 4 = N/2; all others = 0.
    const std::size_t N = 8;
    const double pi = 4.0 * std::atan(1.0);
    cvector x(N);
    for (std::size_t n = 0; n < N; ++n) {
        x[n] = cdouble{std::cos(2.0 * pi * static_cast<double>(n) / static_cast<double>(N)), 0.0};
    }
    cvector expected(N, cdouble{0.0, 0.0});
    expected[1] = cdouble{4.0, 0.0};  // k=1
    expected[7] = cdouble{4.0, 0.0};  // k=7 (Hermitian mirror)
    const double tol = 1.0e-13;

    const cvector X_out = dft(x);
    assert_complex_array_close(total, failed, "test_dft_n8_pure_cosine",
                               X_out, expected, tol);
}

static void test_dft_idft_roundtrip_n8(int& total, int& failed) {
    // idft(dft(x)) == x within precision (Property P6).
    const std::size_t N = 8;
    cvector x(N);
    for (std::size_t i = 0; i < N; ++i) {
        const double r = static_cast<double>(i + 1);
        x[i] = cdouble{r * 0.3, r * 0.5 - 1.0};
    }
    const double tol = 1.0e-13;

    const cvector X_freq = dft(x);
    const cvector x_back = idft(X_freq);
    assert_complex_array_close(total, failed, "test_dft_idft_roundtrip_n8",
                               x_back, x, tol);
}

int main() {
    print_title("lege-artis/fourier - DFT unit tests (v0.2.0 C++ ref)");

    int total = 0, failed = 0;
    test_dft_n4_pure_cosine(total, failed);
    test_dft_n4_dc_input(total, failed);
    test_dft_n4_impulse_at_centre(total, failed);
    test_dft_n8_pure_cosine(total, failed);
    test_dft_idft_roundtrip_n8(total, failed);

    return print_summary(total, failed);
}
