// SPDX-License-Identifier: Apache-2.0
//
// test_harness.hpp - Shared test infrastructure for the C++ DFT test suite
//
// Hand-rolled (no Catch2/GoogleTest) to mirror the Fortran test pattern in
// backends/fortran/tests/test_dft_unit.f90. Lightweight, zero external deps.
//
// Each test program declares its own counters (total, failed) and calls these
// helpers; helpers update counters via reference. The main() function decides
// pass/fail exit code based on counters.

#pragma once

#include "lege_artis_fourier/dft_kernel.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace lege_artis::fourier::testing {

// Print a 57-char ASCII banner line.
inline void print_banner() {
    std::printf("=========================================================\n");
}

// Print a centred title between banner lines.
inline void print_title(const std::string& title) {
    print_banner();
    std::printf(" %s\n", title.c_str());
    print_banner();
}

// Assert two complex arrays are close element-wise.
// Updates total/failed counters by reference.
inline void assert_complex_array_close(
    int& total, int& failed,
    const std::string& test_name,
    const cvector& actual,
    const cvector& expected,
    double tol)
{
    ++total;
    if (actual.size() != expected.size()) {
        ++failed;
        std::printf(" [FAIL] %s - size mismatch (actual=%zu, expected=%zu)\n",
                    test_name.c_str(), actual.size(), expected.size());
        return;
    }
    double max_err = 0.0;
    std::size_t idx = 0;
    for (std::size_t i = 0; i < actual.size(); ++i) {
        const double err = std::abs(actual[i] - expected[i]);
        if (err > max_err) {
            max_err = err;
            idx = i;
        }
    }
    if (max_err > tol) {
        ++failed;
        std::printf(" [FAIL] %s - max-err = %.3E > tol = %.3E at idx %zu\n",
                    test_name.c_str(), max_err, tol, idx);
        std::printf("        actual[idx]   = %.8f + %.8fi\n",
                    actual[idx].real(), actual[idx].imag());
        std::printf("        expected[idx] = %.8f + %.8fi\n",
                    expected[idx].real(), expected[idx].imag());
    } else {
        std::printf(" [PASS] %s - max-err = %.3E  (gate %.3E)\n",
                    test_name.c_str(), max_err, tol);
    }
}

// Assert single complex value close to expected.
inline void assert_complex_close(
    int& total, int& failed,
    const std::string& test_name,
    const cdouble& actual,
    const cdouble& expected,
    double tol)
{
    ++total;
    const double err = std::abs(actual - expected);
    if (err > tol) {
        ++failed;
        std::printf(" [FAIL] %s - err = %.3E > tol = %.3E\n",
                    test_name.c_str(), err, tol);
        std::printf("        actual   = %.8f + %.8fi\n",
                    actual.real(), actual.imag());
        std::printf("        expected = %.8f + %.8fi\n",
                    expected.real(), expected.imag());
    } else {
        std::printf(" [PASS] %s - err = %.3E  (gate %.3E)\n",
                    test_name.c_str(), err, tol);
    }
}

// Assert single real value close to expected.
inline void assert_real_close(
    int& total, int& failed,
    const std::string& test_name,
    double actual,
    double expected,
    double tol)
{
    ++total;
    const double err = std::abs(actual - expected);
    if (err > tol) {
        ++failed;
        std::printf(" [FAIL] %s - err = %.3E > tol = %.3E\n",
                    test_name.c_str(), err, tol);
        std::printf("        actual   = %.8f\n", actual);
        std::printf("        expected = %.8f\n", expected);
    } else {
        std::printf(" [PASS] %s - err = %.3E  (gate %.3E)\n",
                    test_name.c_str(), err, tol);
    }
}

// Assert a real value falls within the closed interval [lo, hi].
inline void assert_real_in_range(
    int& total, int& failed,
    const std::string& test_name,
    double val, double lo, double hi)
{
    ++total;
    if (val >= lo && val <= hi) {
        std::printf(" [PASS] %s - val = %.3E  in [%.3E, %.3E]\n",
                    test_name.c_str(), val, lo, hi);
    } else {
        ++failed;
        std::printf(" [FAIL] %s - val = %.3E  NOT in [%.3E, %.3E]\n",
                    test_name.c_str(), val, lo, hi);
    }
}

// Aggregate-failure variant: count a single test that requires all-bins-pass.
inline void assert_zero_failures(
    int& total, int& failed,
    const std::string& test_name,
    int fail_count, int bin_count, double gate)
{
    ++total;
    if (fail_count > 0) {
        ++failed;
        std::printf(" [FAIL] %s: %d/%d bins failed at gate %.3E\n",
                    test_name.c_str(), fail_count, bin_count, gate);
    } else {
        std::printf(" [PASS] %s for all %d bins  (gate %.3E)\n",
                    test_name.c_str(), bin_count, gate);
    }
}

// Print final test summary; return suggested exit code (0 pass / 1 fail).
inline int print_summary(int total, int failed) {
    print_banner();
    std::printf(" Result: %d/%d passed\n", (total - failed), total);
    if (failed > 0) {
        std::printf(" FAILED.\n");
        return 1;
    }
    std::printf(" All tests PASSED.\n");
    return 0;
}

}  // namespace lege_artis::fourier::testing
