// SPDX-License-Identifier: Apache-2.0
//
// test_dft_physics.cpp - Physics testbeds for the C++ DFT kernel
//
// Mirrors backends/fortran/tests/test_dft_physics.f90 - same 4 testbeds,
// same inputs, same gates, same 14 assertions.
//
// Testbeds (per shared/physics-testbeds/dft.md):
//   PT-DFT-01 - Fraunhofer single-slit diffraction
//               N=64, slit a=16, centred at n=24..39
//   PT-DFT-02 - Heat-equation impulse response
//               N=64, impulse at n=32
//   PT-DFT-03A - SHO integer frequency, N=64, f0=5
//               x[n] = cos(2*pi*5*n/64); two-bin concentration
//   PT-DFT-03B - SHO leakage, N=64, f0=5.5
//               x[n] = cos(2*pi*5.5*n/64); vs golden vector
//               (oracle Re/Im embedded; agreement numpy vs scipy: 1.986e-15)
//
// Source kept ASCII-only (KB-039).

#include "lege_artis_fourier/dft_kernel.hpp"
#include "test_harness.hpp"

#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <limits>
#include <vector>

using namespace lege_artis::fourier;
using lege_artis::fourier::testing::assert_real_close;
using lege_artis::fourier::testing::assert_real_in_range;
using lege_artis::fourier::testing::assert_zero_failures;
using lege_artis::fourier::testing::print_summary;
using lege_artis::fourier::testing::print_title;

static const double PI = 4.0 * std::atan(1.0);

// --------------------------------------------------------------------------
// PT-DFT-01 - Fraunhofer single-slit diffraction
// Setup: N=64, slit width a=16 centred at n=24..39, x[n]=1 there, 0 else.
// Expected:
//   |X[0]|^2 = 256                    (central max; gate 256*1e-12)
//   |X[4]|^2 = 0                      (first null; gate 1e-12)
//   first sidelobe power (k=5..7) in [10, 14]
//   max sidelobe/peak ratio (k=5..N/2) in [0.04, 0.05]
// --------------------------------------------------------------------------
static void test_pt01_fraunhofer(int& total, int& failed) {
    const std::size_t N = 64;

    cvector x(N, cdouble{0.0, 0.0});
    for (std::size_t n = 24; n <= 39; ++n) x[n] = cdouble{1.0, 0.0};

    const cvector X_out = dft(x);

    // 1: |X[0]|^2 = 256 (central max), gate 256e-12
    const double pwr0 = std::norm(X_out[0]);
    assert_real_close(total, failed,
                      "PT-DFT-01 central max |X[0]|^2=256",
                      pwr0, 256.0, 256.0 * 1.0e-12);

    // 2: |X[4]|^2 = 0 (first null), gate 1e-12
    const double pwr4 = std::norm(X_out[4]);
    assert_real_close(total, failed,
                      "PT-DFT-01 first null |X[4]|^2=0",
                      pwr4, 0.0, 1.0e-12);

    // 3: first sidelobe max power across k=5..7 in [10, 14]
    double sidelobe_max = 0.0;
    for (std::size_t k = 5; k <= 7; ++k) {
        const double pwr_k = std::norm(X_out[k]);
        if (pwr_k > sidelobe_max) sidelobe_max = pwr_k;
    }
    assert_real_in_range(total, failed,
                         "PT-DFT-01 first sidelobe max power (k=5..7)",
                         sidelobe_max, 10.0, 14.0);

    // 4: max sidelobe/peak ratio over k=5..N/2 in [0.04, 0.05]
    double ratio_max = 0.0;
    for (std::size_t k = 5; k <= N / 2; ++k) {
        const double pwr_k = std::norm(X_out[k]);
        const double r = pwr_k / pwr0;
        if (r > ratio_max) ratio_max = r;
    }
    assert_real_in_range(total, failed,
                         "PT-DFT-01 sidelobe/peak ratio (k=5..N/2)",
                         ratio_max, 0.04, 0.05);
}

// --------------------------------------------------------------------------
// PT-DFT-02 - Heat-equation Green's function (impulse response)
// Setup: N=64, impulse at n=32, x[n]=1 there, 0 else.
// Expected: X[k] = exp(-pi*i*k) = (-1)^k
//   |X[k]| = 1, Im(X[k]) = 0, sign pattern (-1)^k
// Gate: 1e-13
// --------------------------------------------------------------------------
static void test_pt02_heat_impulse(int& total, int& failed) {
    const std::size_t N = 64;
    const double tol = 1.0e-13;

    cvector x(N, cdouble{0.0, 0.0});
    x[32] = cdouble{1.0, 0.0};

    const cvector X_out = dft(x);

    // 1: |X[k]| = 1 for all k
    int mag_fail = 0;
    for (const auto& v : X_out) {
        if (std::abs(std::abs(v) - 1.0) > tol) ++mag_fail;
    }
    assert_zero_failures(total, failed, "PT-DFT-02 |X[k]|=1",
                         mag_fail, static_cast<int>(N), tol);

    // 2: Im(X[k]) = 0 for all k
    int im_fail = 0;
    for (const auto& v : X_out) {
        if (std::abs(v.imag()) > tol) ++im_fail;
    }
    assert_zero_failures(total, failed, "PT-DFT-02 Im(X[k])=0",
                         im_fail, static_cast<int>(N), tol);

    // 3: sign pattern (-1)^k
    int sign_fail = 0;
    for (std::size_t k = 0; k < N; ++k) {
        if ((k % 2) == 0) {
            if (X_out[k].real() <= 0.0) ++sign_fail;
        } else {
            if (X_out[k].real() >= 0.0) ++sign_fail;
        }
    }
    ++total;
    if (sign_fail > 0) {
        ++failed;
        std::printf(" [FAIL] PT-DFT-02 sign(-1)^k: %d bins with wrong sign\n",
                    sign_fail);
    } else {
        std::printf(" [PASS] PT-DFT-02 sign pattern (-1)^k correct for all 64 bins\n");
    }
}

// --------------------------------------------------------------------------
// PT-DFT-03A - SHO integer frequency (no spectral leakage)
// Setup: N=64, x[n] = cos(2*pi*5*n/64), n=0..63
// Expected:
//   X[5]  = 32 + 0i
//   X[59] = 32 + 0i (Hermitian mirror)
//   |X[k]| < 1e-12 for all other k
//   Plancherel: sum|x|^2 == (1/N)*sum|X|^2
// --------------------------------------------------------------------------
static void test_pt03a_sho_integer(int& total, int& failed) {
    const std::size_t N = 64;
    const double tol_bin = 1.0e-12;

    cvector x(N);
    for (std::size_t n = 0; n < N; ++n) {
        x[n] = cdouble{
            std::cos(2.0 * PI * 5.0 * static_cast<double>(n) / static_cast<double>(N)),
            0.0
        };
    }
    const cvector X_out = dft(x);

    // X[5] = 32 + 0i
    assert_real_close(total, failed, "PT-DFT-03A X[5] real=32",
                      X_out[5].real(), 32.0, tol_bin);
    assert_real_close(total, failed, "PT-DFT-03A X[5] imag=0",
                      X_out[5].imag(), 0.0, tol_bin);

    // X[59] = 32 + 0i
    assert_real_close(total, failed, "PT-DFT-03A X[59] real=32",
                      X_out[59].real(), 32.0, tol_bin);
    assert_real_close(total, failed, "PT-DFT-03A X[59] imag=0",
                      X_out[59].imag(), 0.0, tol_bin);

    // All other 62 bins |X[k]| < 1e-12
    int other_fail = 0;
    for (std::size_t k = 0; k < N; ++k) {
        if (k == 5 || k == 59) continue;
        if (std::abs(X_out[k]) >= tol_bin) ++other_fail;
    }
    assert_zero_failures(total, failed,
                         "PT-DFT-03A all other 62 bins <1e-12 (energy concentrated in k=5,59)",
                         other_fail, 62, tol_bin);

    // Plancherel: sum|x|^2 == (1/N)*sum|X|^2
    double e_time = 0.0, e_freq = 0.0;
    for (std::size_t n = 0; n < N; ++n) e_time += std::norm(x[n]);
    for (std::size_t k = 0; k < N; ++k) e_freq += std::norm(X_out[k]);
    e_freq /= static_cast<double>(N);
    const double tol_plancherel =
        2.0 * static_cast<double>(N) * std::numeric_limits<double>::epsilon()
        * std::max(e_time, e_freq);
    assert_real_close(total, failed, "PT-DFT-03A Plancherel",
                      e_time, e_freq, tol_plancherel);
}

// --------------------------------------------------------------------------
// PT-DFT-03B - Cosine leakage (non-integer frequency)
// Setup: N=64, x[n] = cos(2*pi*5.5*n/64), n=0..63
// Oracle: shared/golden-vectors/dft_n=64_cosine_leakage.json (NumPy+SciPy
//         cross-checked, max_abs_diff = 1.986e-15)
// Embedded as g_re[64] / g_im[64] arrays below.
// Gate: 1e-10 absolute on power spectrum |X[k]|^2 per bin (~100x margin
//       above the per-bin O(N^2*eps) ~ 9e-13 bound).
// --------------------------------------------------------------------------
static void test_pt03b_cosine_leakage(int& total, int& failed) {
    const std::size_t N = 64;
    const double gate = 1.0e-10;

    // Oracle Re(X[k]), k=0..63 (from dft_n=64_cosine_leakage.json output array)
    static const std::array<double, 64> g_re = {{
        1.0000000000000087, 1.0000000000000098, 1.0000000000000102,
        1.0000000000000124, 1.0000000000000184, 1.0000000000000522,
        0.9999999999999515, 0.9999999999999858, 0.9999999999999913,
        0.9999999999999947, 0.9999999999999957, 0.9999999999999973,
        0.9999999999999976, 0.9999999999999983, 0.9999999999999978,
        0.9999999999999989, 0.9999999999999989, 0.9999999999999983,
        0.9999999999999993, 0.9999999999999989, 0.9999999999999993,
        0.9999999999999996, 0.9999999999999999, 0.9999999999999993,
        0.9999999999999989, 0.9999999999999987, 0.9999999999999997,
        1.0,                0.9999999999999989, 0.9999999999999992,
        1.0,                0.9999999999999986, 0.9999999999999989,
        0.9999999999999996, 0.9999999999999996, 0.9999999999999991,
        0.9999999999999989, 0.9999999999999984, 0.9999999999999986,
        0.9999999999999987, 0.9999999999999989, 0.9999999999999987,
        0.9999999999999992, 0.9999999999999973, 0.9999999999999993,
        0.9999999999999986, 0.9999999999999991, 0.9999999999999987,
        0.9999999999999989, 0.9999999999999986, 0.999999999999998,
        0.9999999999999984, 0.9999999999999976, 0.999999999999996,
        0.9999999999999963, 0.999999999999994,  0.9999999999999913,
        0.9999999999999858, 0.9999999999999517, 1.0000000000000515,
        1.0000000000000184, 1.0000000000000129, 1.0000000000000102,
        1.0000000000000098
    }};

    // Oracle Im(X[k]), k=0..63
    static const std::array<double, 64> g_im = {{
        0.0,                  0.7130795100483178,   1.5853697436903686,
        2.925910975873875,    5.785005225004534,    19.485118500994588,
       -21.157328220021725,  -7.488280072923256,   -4.694583691856731,
       -3.4612099562261216,  -2.7517675353271347,  -2.2828074140041767,
       -1.9448245682872571,  -1.6864050886960076,  -1.4801216563971011,
       -1.309950904260467,   -1.165869936412268,   -1.041265133879751,
       -0.9315802086924778,  -0.8335620731538382,  -0.7448166423388842,
       -0.6635350581901365,  -0.5883183280090254,  -0.5180611961972974,
       -0.4518729478953416,  -0.3890219461937474,  -0.3288958191432467,
       -0.27097219031070807, -0.21479663413842331, -0.1599656388770634,
       -0.10611305306663266, -0.052898934013602295, 0.0,
        0.05289893401360213,  0.10611305306663277,  0.15996563887706272,
        0.21479663413842331,  0.27097219031070985,  0.3288958191432467,
        0.3890219461937465,   0.4518729478953416,   0.5180611961972981,
        0.5883183280090254,   0.6635350581901367,   0.7448166423388842,
        0.8335620731538383,   0.9315802086924784,   1.0412651338797512,
        1.165869936412268,    1.3099509042604667,   1.4801216563971007,
        1.6864050886960076,   1.9448245682872571,   2.2828074140041767,
        2.7517675353271347,   3.461209956226122,    4.694583691856731,
        7.488280072923256,    21.157328220021725, -19.485118500994588,
       -5.785005225004534,   -2.9259109758738746, -1.5853697436903689,
       -0.713079510048318
    }};

    // Build input: x[n] = cos(2*pi*5.5*n/64), n=0..63
    cvector x(N);
    for (std::size_t n = 0; n < N; ++n) {
        x[n] = cdouble{
            std::cos(2.0 * PI * 5.5 * static_cast<double>(n) / static_cast<double>(N)),
            0.0
        };
    }
    const cvector X_out = dft(x);

    // Compare power spectrum |X[k]|^2 vs oracle power, gate=1e-10 per bin
    double max_pwr_err = 0.0;
    int pwr_fail = 0;
    for (std::size_t k = 0; k < N; ++k) {
        const double oracle_pwr = g_re[k] * g_re[k] + g_im[k] * g_im[k];
        const double actual_pwr = std::norm(X_out[k]);
        const double err = std::abs(actual_pwr - oracle_pwr);
        if (err > gate) ++pwr_fail;
        if (err > max_pwr_err) max_pwr_err = err;
    }

    ++total;
    if (pwr_fail > 0) {
        ++failed;
        std::printf(" [FAIL] PT-DFT-03B leakage: %d bins failed, max_pwr_err = %.3E > gate %.3E\n",
                    pwr_fail, max_pwr_err, gate);
    } else {
        std::printf(" [PASS] PT-DFT-03B leakage profile 64 bins: max_pwr_err = %.3E  (gate %.3E)\n",
                    max_pwr_err, gate);
    }
}

int main() {
    print_title("lege-artis/fourier - DFT physics testbeds (v0.2.0 C++ ref)");

    int total = 0, failed = 0;
    test_pt01_fraunhofer(total, failed);
    test_pt02_heat_impulse(total, failed);
    test_pt03a_sho_integer(total, failed);
    test_pt03b_cosine_leakage(total, failed);

    return print_summary(total, failed);
}
