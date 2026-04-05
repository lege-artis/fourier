// kh_shim.cpp — C++ wrapper around Fortran kh_simulate_c()
// Allocates output buffers, calls Fortran, packages SimResult.

#include "kh_shim.hpp"
#include <chrono>
#include <cmath>
#include <stdexcept>

namespace khsim {

SimResult simulate(const SimRequest& req) {
    using clock = std::chrono::high_resolution_clock;
    auto t0 = clock::now();

    int n = req.nx * req.ny;
    std::vector<double> u(n), v(n), omega(n), psi(n);
    double ke, enstrophy, max_vort, div_rms;

    const double* init_ptr = req.init_omega
        ? req.init_omega->data()
        : nullptr;

    kh_simulate_c(
        req.nx, req.ny,
        req.lx, req.ly,
        req.dt, req.steps,
        req.re, req.u0, req.amp, req.mode,
        init_ptr,
        u.data(), v.data(), omega.data(), psi.data(),
        &ke, &enstrophy, &max_vort, &div_rms
    );

    double elapsed = std::chrono::duration<double, std::milli>(
        clock::now() - t0).count();

    double t_final = std::round(req.steps * req.dt * 1e10) / 1e10;

    return SimResult{
        "fortran-httplib", "Fortran",
        req.steps, t_final, req.nx, req.ny,
        std::move(u), std::move(v), std::move(omega), std::move(psi),
        {ke, enstrophy, max_vort, div_rms},
        std::round(elapsed * 100.0) / 100.0,
    };
}

} // namespace khsim
