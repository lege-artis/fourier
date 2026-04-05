// validation_test.cpp — KH-005 acceptance test
//
// Validates C++ diagnostics against kh_reference_output.json.
// Tolerance: +-5% on kinetic_energy and enstrophy (KH-PHYSICS.md S7).
// Incompressibility: divergence_rms < 1e-10.
//
// Usage: kh-sim-cpp-validate <path/to/kh_reference_output.json>
// CTest: cmake --build build && ctest --test-dir build -V

#include "physics.hpp"

#include <nlohmann/json.hpp>

#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

using json = nlohmann::json;

static double pct_err(double got, double ref) {
    return std::abs((got - ref) / ref) * 100.0;
}

int main(int argc, char* argv[]) {
    // Path to reference JSON passed as first argument (or default relative path)
    std::string ref_path = "../../shared/physics/kh_reference_output.json";
    if (argc >= 2) ref_path = argv[1];

    // Load reference
    std::ifstream f(ref_path);
    if (!f) {
        std::cerr << "Cannot open reference file: " << ref_path << "\n"
                  << "Run: python kh-sim/shared/physics/kh_physics.py\n";
        return 1;
    }
    json ref_json = json::parse(f);

    int ref_nx    = ref_json.value("grid_nx", 64);
    int ref_ny    = ref_json.value("grid_ny", 32);
    int ref_steps = ref_json.value("steps_completed", 100);

    double ref_ke   = ref_json["diagnostics"]["kinetic_energy"];
    double ref_ens  = ref_json["diagnostics"]["enstrophy"];
    double ref_mv   = ref_json["diagnostics"]["max_vorticity"];
    double ref_div  = ref_json["diagnostics"]["divergence_rms"];

    // Build matching request
    khsim::SimulationRequest req;
    req.grid_nx                = ref_nx;
    req.grid_ny                = ref_ny;
    req.domain_lx              = 1.0;
    req.domain_ly              = 0.5;
    req.dt                     = 0.001;
    req.steps                  = ref_steps;
    req.reynolds_number        = 1000.0;
    req.velocity_shear         = 1.0;
    req.perturbation_amplitude = 0.01;
    req.perturbation_mode      = 2;

    auto result = khsim::simulate(req);
    const auto& d = result.diagnostics;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "--- C++ vs Python reference ---\n";
    std::cout << "kinetic_energy : got=" << d.kinetic_energy
              << "  ref=" << ref_ke
              << "  err=" << std::setprecision(2) << pct_err(d.kinetic_energy, ref_ke) << "%\n";
    std::cout << "enstrophy      : got=" << std::setprecision(6) << d.enstrophy
              << "  ref=" << ref_ens
              << "  err=" << std::setprecision(2) << pct_err(d.enstrophy, ref_ens) << "%\n";
    std::cout << "max_vorticity  : got=" << std::setprecision(6) << d.max_vorticity
              << "  ref=" << ref_mv
              << "  err=" << std::setprecision(2) << pct_err(d.max_vorticity, ref_mv) << "%\n";
    std::cout << "divergence_rms : got=" << std::scientific << d.divergence_rms
              << "  ref=" << ref_div << "\n";

    // ── Acceptance criteria ────────────────────────────────────────────────────
    bool pass = true;
    auto check = [&](const char* name, double err_pct, double tol) {
        if (err_pct >= tol) {
            std::cerr << "FAIL " << name << ": " << err_pct << "% >= " << tol << "%\n";
            pass = false;
        }
    };
    check("kinetic_energy", pct_err(d.kinetic_energy, ref_ke), 5.0);
    check("enstrophy",      pct_err(d.enstrophy,      ref_ens), 5.0);
    if (d.divergence_rms >= 1e-10) {
        std::cerr << "FAIL divergence_rms: " << d.divergence_rms << " >= 1e-10\n";
        pass = false;
    }

    // ── Field shape check (nx*ny) ──────────────────────────────────────────────
    int expected_n = ref_nx * ref_ny;
    if ((int)result.u_velocity.size() != expected_n ||
        (int)result.vorticity.size()  != expected_n) {
        std::cerr << "FAIL field shape mismatch\n";
        pass = false;
    }

    if (pass) {
        std::cout << "\nAll tests PASSED\n";
        return 0;
    } else {
        std::cout << "\nSome tests FAILED\n";
        return 1;
    }
}
