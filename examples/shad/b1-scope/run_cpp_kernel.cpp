// SPDX-License-Identifier: Apache-2.0
//
// run_cpp_kernel.cpp - Push the B0 Slot S1 golden vector through the
// lege-artis/fourier C++ reference kernel and print the output.
//
// This is the "how to push data into our component" example used in
// Chapter B0 of Just Shad's Guide to Fourier's Galaxy.
//
// Build (from repo root):
//   cd backends/cpp && make
//   g++ -O0 -g -std=c++17 -Iinclude \
//       examples/shad/b1-scope/run_cpp_kernel.cpp build/dft_kernel.o \
//       -o examples/shad/b1-scope/run_cpp_kernel
//
// Run:
//   ./run_cpp_kernel ../../shared/golden-vectors/dft_n=64.json cos1_plus_cos2
//
// Output:
//   Plain-text listing of input head, output head, and oracle agreement.
//   Suitable for direct paste into the chapter listing block.

#include <cmath>
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "lege_artis_fourier/dft_kernel.hpp"

using cdouble = std::complex<double>;
using cvector = std::vector<cdouble>;

// Hand-rolled minimal parser for the small subset of JSON the golden
// vectors use: just enough to lift "input" and "output" arrays from
// test_cases[case_name]. Avoids pulling a JSON library into the example.
static cvector parse_complex_array(const std::string& blob,
                                   const std::string& case_name,
                                   const std::string& key) {
    cvector out;
    // find  "case_name":
    auto case_pos = blob.find('"' + case_name + '"');
    if (case_pos == std::string::npos) {
        throw std::runtime_error("case not found: " + case_name);
    }
    // find  "key":
    auto key_pos = blob.find('"' + key + '"', case_pos);
    if (key_pos == std::string::npos) {
        throw std::runtime_error("key not found: " + key);
    }
    // Find the outer "[" that opens the array of [re,im] pairs.
    auto arr_start = blob.find('[', key_pos);
    if (arr_start == std::string::npos) {
        throw std::runtime_error("opening [ not found for key: " + key);
    }
    // Find the matching outer "]" by tracking nesting depth.
    int depth = 0;
    size_t arr_end = std::string::npos;
    for (size_t i = arr_start; i < blob.size(); ++i) {
        if (blob[i] == '[') ++depth;
        else if (blob[i] == ']') {
            --depth;
            if (depth == 0) { arr_end = i; break; }
        }
    }
    if (arr_end == std::string::npos) {
        throw std::runtime_error("matching ] not found for key: " + key);
    }
    // Walk through inner "[re, im]" pairs strictly inside the outer brackets.
    size_t pos = arr_start;            // points at outer "[" itself
    while (true) {
        pos = blob.find('[', pos + 1); // next "[" is either an inner pair or beyond arr_end
        if (pos == std::string::npos || pos >= arr_end) break;
        auto pair_end = blob.find(']', pos);
        std::string pair_str = blob.substr(pos + 1, pair_end - pos - 1);
        double re = 0.0, im = 0.0;
        std::sscanf(pair_str.c_str(), " %lf , %lf", &re, &im);
        out.emplace_back(re, im);
        pos = pair_end;
    }
    return out;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::fprintf(stderr,
            "usage: %s <golden_json_path> [case_name=cos1_plus_cos2] [--csv]\n",
            argv[0]);
        return 2;
    }
    const std::string json_path = argv[1];
    std::string case_name = "cos1_plus_cos2";
    bool csv_mode = false;
    for (int i = 2; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--csv") csv_mode = true;
        else                case_name = arg;
    }

    std::ifstream f(json_path);
    if (!f.is_open()) {
        std::fprintf(stderr, "cannot open %s\n", json_path.c_str());
        return 2;
    }
    std::stringstream blob;
    blob << f.rdbuf();
    const std::string text = blob.str();

    const cvector x         = parse_complex_array(text, case_name, "input");
    const cvector X_oracle  = parse_complex_array(text, case_name, "output");

    // *** Push data into the lege-artis/fourier C++ reference kernel ***
    const cvector X_cpp = lege_artis::fourier::dft(x);

    // Verify against oracle
    double max_err = 0.0;
    for (size_t k = 0; k < X_cpp.size(); ++k) {
        const double err = std::abs(X_cpp[k] - X_oracle[k]);
        if (err > max_err) max_err = err;
    }

    if (csv_mode) {
        // Emit CSV: bin,re,im,mag    one row per output bin.
        std::printf("bin,re,im,mag\n");
        for (size_t k = 0; k < X_cpp.size(); ++k) {
            std::printf("%zu,%.17g,%.17g,%.17g\n",
                        k, X_cpp[k].real(), X_cpp[k].imag(),
                        std::abs(X_cpp[k]));
        }
        return 0;
    }

    // Pragmatic gate: direct O(N^2) DFT at double precision accumulates
    // floating-point error roughly as N * eps with constants ~1..10x.
    // For N=64, that puts an engineering gate at ~10 * N * eps ~= 1.4e-13.
    // We use 1e-12 as the relaxed-but-honest gate. The strict 1e-13 gate
    // in the unit suite is for small-N (N<=16) cases.
    const double gate = 1.0e-12;
    std::printf("--- lege-artis/fourier C++ reference kernel ---\n");
    std::printf("N           = %zu\n", x.size());
    std::printf("case        = %s\n", case_name.c_str());
    std::printf("max abs err = %.3e   (engineering gate 1e-12 for N=%zu)\n",
                max_err, x.size());
    std::printf("agreement   = %s\n", (max_err < gate) ? "PASS" : "FAIL");

    std::printf("\nfirst 8 inputs (real part only - input is real-valued):\n");
    for (size_t n = 0; n < 8 && n < x.size(); ++n) {
        std::printf("  x[%2zu] = %+.10f\n", n, x[n].real());
    }
    std::printf("\nfirst 8 outputs:\n");
    for (size_t k = 0; k < 8 && k < X_cpp.size(); ++k) {
        std::printf("  X[%2zu] = %+.4f %+.4fj   |X[%2zu]| = %.4f\n",
                    k, X_cpp[k].real(), X_cpp[k].imag(),
                    k, std::abs(X_cpp[k]));
    }
    return 0;
}
