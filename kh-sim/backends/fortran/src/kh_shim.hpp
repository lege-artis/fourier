#pragma once
// kh_shim.hpp — C++ interface to the Fortran physics kernel
// Declares the C-linkage symbol exported by kh_physics.f90 bind(c)
// and a high-level simulate() function that wraps it.

#include <vector>
#include <optional>
#include <string>

extern "C" {
    void kh_simulate_c(
        int nx, int ny,
        double lx, double ly,
        double dt, int steps,
        double re, double u0, double amp, int mode,
        const double* init_omega,   // may be nullptr -> analytic IC
        double* out_u,
        double* out_v,
        double* out_omega,
        double* out_psi,
        double* out_ke,
        double* out_enstrophy,
        double* out_max_vort,
        double* out_div_rms
    );
}

namespace khsim {

struct SimRequest {
    int    nx = 128, ny = 64;
    double lx = 1.0, ly = 0.5;
    double dt = 0.001;
    int    steps = 100;
    double re = 1000.0, u0 = 1.0, amp = 0.01;
    int    mode = 2;
    std::optional<std::vector<double>> init_omega;
};

struct Diagnostics {
    double kinetic_energy, enstrophy, max_vorticity, divergence_rms;
};

struct SimResult {
    std::string backend = "fortran-fphttpapp";
    std::string language = "Fortran";
    int    steps_completed;
    double t_final;
    int    nx, ny;
    std::vector<double> u, v, omega, psi;
    Diagnostics diag;
    double compute_ms;
};

SimResult simulate(const SimRequest& req);

} // namespace khsim
