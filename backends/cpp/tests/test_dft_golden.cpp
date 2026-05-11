// SPDX-License-Identifier: Apache-2.0
//
// test_dft_golden.cpp - Golden-vector verification for the C++ DFT kernel
//
// Reads .dat files produced by tools/json_to_fortran_data.py and verifies
// that dft() matches the NumPy/SciPy oracle for all N in {2,4,8,16,64}.
//
// Gate: Option G (per KB-040, Higham section 4.2)
//
//   metric = abs(got - expected) / max(abs(expected), 1.0)
//   gate   = 1.0e-13 * sqrt(N)
//
// Effective gates: N=2 -> 1.41e-13, N=4 -> 2.00e-13, N=8 -> 2.83e-13,
//                  N=16 -> 4.00e-13, N=64 -> 8.00e-13.
//
// .dat format (matching backends/fortran/tests/test_dft_golden.f90):
//   Line 1:  N  num_cases                  (whitespace-tokenized integers)
//   Per case:
//     Line:    case_name                   (64-char fixed field, space-padded)
//     N lines: re_in  im_in               (whitespace-tokenized doubles)
//     N lines: re_out im_out              (whitespace-tokenized doubles)
//
// Build: make golden-data && make test   (from fourier/backends/cpp/)

#include "lege_artis_fourier/dft_kernel.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

using namespace lege_artis::fourier;

// --------------------------------------------------------------------------
// Option G assertion: relative metric vs sqrt(N) gate.
// --------------------------------------------------------------------------
static bool assert_golden(
    const std::string& label,
    const cdouble& got, const cdouble& expected,
    double gate)
{
    const double denom = std::max(std::abs(expected), 1.0);
    const double metric = std::abs(got - expected) / denom;
    if (metric <= gate) return true;
    std::printf("  FAIL  %s  metric=%.3E  gate=%.3E\n",
                label.c_str(), metric, gate);
    return false;
}

// --------------------------------------------------------------------------
// Read N complex pairs (one per line: "re im") into out[].
// --------------------------------------------------------------------------
static bool read_n_complex(std::ifstream& fh, std::size_t n, cvector& out) {
    out.resize(n);
    std::string line;
    for (std::size_t k = 0; k < n; ++k) {
        if (!std::getline(fh, line)) return false;
        std::istringstream iss(line);
        double re, im;
        if (!(iss >> re >> im)) return false;
        out[k] = cdouble{re, im};
    }
    return true;
}

// --------------------------------------------------------------------------
// Process one .dat file; update pass/fail totals.
// Returns false on FATAL file-format error (caller should abort suite).
// --------------------------------------------------------------------------
static bool run_golden_file(int nlen, int& pass_total, int& fail_total) {
    char path_buf[128];
    std::snprintf(path_buf, sizeof path_buf,
                  "build/golden/dft_n_%d.dat", nlen);
    const std::string dat_path = path_buf;

    std::ifstream fh(dat_path);
    if (!fh.is_open()) {
        std::printf("FATAL: cannot open [%s]\n", dat_path.c_str());
        std::printf("       Run: make golden-data\n");
        return false;
    }

    // Header: N num_cases
    int dummy_n = 0, num_cases = 0;
    {
        std::string line;
        if (!std::getline(fh, line)) return false;
        std::istringstream iss(line);
        if (!(iss >> dummy_n >> num_cases)) return false;
    }

    // Option G gate
    const double gate = 1.0e-13 * std::sqrt(static_cast<double>(nlen));

    cvector x_in, x_oracle;

    for (int ic = 0; ic < num_cases; ++ic) {
        // Case name: 64-char fixed-field line
        std::string case_name;
        if (!std::getline(fh, case_name)) return false;
        // Trim trailing whitespace from the fixed-field padding
        const auto pos = case_name.find_last_not_of(" \t\r\n");
        if (pos != std::string::npos) case_name.erase(pos + 1);

        // Input
        if (!read_n_complex(fh, static_cast<std::size_t>(nlen), x_in))   return false;
        // Oracle output
        if (!read_n_complex(fh, static_cast<std::size_t>(nlen), x_oracle)) return false;

        // Run our DFT and compare
        const cvector X_tmp = dft(x_in);

        int pass_case = 0, fail_case = 0;
        for (int k = 0; k < nlen; ++k) {
            std::ostringstream lbl;
            lbl << "N=" << nlen << " " << case_name << " k=" << k;
            if (assert_golden(lbl.str(),
                              X_tmp[static_cast<std::size_t>(k)],
                              x_oracle[static_cast<std::size_t>(k)],
                              gate)) {
                ++pass_case;
            } else {
                ++fail_case;
            }
        }

        pass_total += pass_case;
        fail_total += fail_case;

        if (fail_case == 0) {
            std::printf("  N=%d  %s  %d PASS  gate= %.2E\n",
                        nlen, case_name.c_str(), pass_case, gate);
        }
    }

    return true;
}

int main() {
    std::printf("Running DFT golden-vector verification (v0.2.0 C++ ref)...\n");

    const int sizes[] = {2, 4, 8, 16, 64};

    int pass_total = 0;
    int fail_total = 0;
    for (int n : sizes) {
        if (!run_golden_file(n, pass_total, fail_total)) {
            std::printf("ABORT: file-format error processing N=%d\n", n);
            return 2;
        }
    }

    std::printf("Golden vector suite: %d PASS  %d FAIL\n",
                pass_total, fail_total);
    return (fail_total > 0) ? 1 : 0;
}
