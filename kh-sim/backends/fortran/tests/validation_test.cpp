// validation_test.cpp — KH-006 Fortran backend acceptance test
// Usage: kh-sim-fortran-validate <path/to/kh_reference_output.json>

#include "kh_shim.hpp"
#include <nlohmann/json.hpp>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>

using json = nlohmann::json;

static double pct_err(double got, double ref) {
    return std::abs((got - ref) / ref) * 100.0;
}

int main(int argc, char* argv[]) {
    std::string path = "../../shared/physics/kh_reference_output.json";
    if (argc >= 2) path = argv[1];

    std::ifstream f(path);
    if (!f) {
        std::cerr << "Cannot open: " << path << "\n";
        return 1;
    }
    auto ref = json::parse(f);

    khsim::SimRequest req;
    req.nx    = ref.value("grid_nx", 64);
    req.ny    = ref.value("grid_ny", 32);
    req.steps = ref.value("steps_completed", 100);
    req.lx = 1.0; req.ly = 0.5; req.dt = 0.001;
    req.re = 1000.0; req.u0 = 1.0; req.amp = 0.01; req.mode = 2;

    auto r = khsim::simulate(req);
    const auto& d = r.diag;

    double ref_ke  = ref["diagnostics"]["kinetic_energy"];
    double ref_ens = ref["diagnostics"]["enstrophy"];
    double ref_mv  = ref["diagnostics"]["max_vorticity"];
    double ref_div = ref["diagnostics"]["divergence_rms"];

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "--- Fortran vs Python reference ---\n";
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
    std::cout << "compute_ms     : " << r.compute_ms << "\n";

    bool pass = true;
    auto check = [&](const char* name, double err, double tol) {
        if (err >= tol) { std::cerr << "FAIL " << name << ": " << err << "%\n"; pass = false; }
    };
    check("kinetic_energy", pct_err(d.kinetic_energy, ref_ke), 5.0);
    check("enstrophy",      pct_err(d.enstrophy,      ref_ens), 5.0);
    if (d.divergence_rms >= 1e-10) {
        std::cerr << "FAIL divergence_rms: " << d.divergence_rms << "\n"; pass = false;
    }
    if ((int)r.u.size() != req.nx * req.ny) {
        std::cerr << "FAIL field shape\n"; pass = false;
    }

    std::cout << (pass ? "\nAll tests PASSED\n" : "\nSome tests FAILED\n");
    return pass ? 0 : 1;
}
