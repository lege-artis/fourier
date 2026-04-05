// physics.cpp — KH instability physics kernel (C++ port of kh_physics.py)
//
// Physics: 2D incompressible Navier-Stokes, vorticity-streamfunction form.
// Numerics: pseudo-spectral (Cooley-Tukey in-place radix-2 FFT), RK4.
//
// Reference: kh-sim/shared/physics/KH-PHYSICS.md
// Canonical:  kh-sim/shared/physics/kh_physics.py

#include "physics.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <complex>
#include <numbers>    // std::numbers::pi (C++20)
#include <numeric>
#include <stdexcept>
#include <vector>

namespace khsim {

using cd = std::complex<double>;
using vc = std::vector<cd>;
using vd = std::vector<double>;

static constexpr double PI = std::numbers::pi;

// ── Cooley-Tukey in-place radix-2 FFT (requires n = power of 2) ──────────────

static void fft1d(vc& a, bool inverse) {
    const int n = static_cast<int>(a.size());
    // bit-reversal permutation
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) std::swap(a[i], a[j]);
    }
    // butterfly stages
    for (int len = 2; len <= n; len <<= 1) {
        double ang = 2.0 * PI / len * (inverse ? -1.0 : 1.0);
        cd wlen(std::cos(ang), std::sin(ang));
        for (int i = 0; i < n; i += len) {
            cd w(1.0, 0.0);
            for (int j = 0; j < len / 2; ++j) {
                cd u = a[i + j];
                cd v = a[i + j + len / 2] * w;
                a[i + j]           = u + v;
                a[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
    if (inverse)
        for (auto& x : a) x /= static_cast<double>(n);
}

// ── 2D FFT: row-then-column (row-major layout, nx rows of ny elements) ────────

static vc fft2(const vd& real, int nx, int ny) {
    vc buf(nx * ny);
    for (int k = 0; k < nx * ny; ++k)
        buf[k] = {real[k], 0.0};

    // FFT along axis-1 (rows)
    vc row(ny);
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) row[j] = buf[i * ny + j];
        fft1d(row, false);
        for (int j = 0; j < ny; ++j) buf[i * ny + j] = row[j];
    }

    // FFT along axis-0 (columns)
    vc col(nx);
    for (int j = 0; j < ny; ++j) {
        for (int i = 0; i < nx; ++i) col[i] = buf[i * ny + j];
        fft1d(col, false);
        for (int i = 0; i < nx; ++i) buf[i * ny + j] = col[i];
    }
    return buf;
}

static vd ifft2_real(vc buf, int nx, int ny) {
    // IFFT along axis-0 (columns)
    vc col(nx);
    for (int j = 0; j < ny; ++j) {
        for (int i = 0; i < nx; ++i) col[i] = buf[i * ny + j];
        fft1d(col, true);
        for (int i = 0; i < nx; ++i) buf[i * ny + j] = col[i];
    }
    // IFFT along axis-1 (rows)
    vc row(ny);
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) row[j] = buf[i * ny + j];
        fft1d(row, true);
        for (int j = 0; j < ny; ++j) buf[i * ny + j] = row[j];
    }
    vd out(nx * ny);
    for (int k = 0; k < nx * ny; ++k) out[k] = buf[k].real();
    return out;
}

// ── Wavenumbers ───────────────────────────────────────────────────────────────

static vd angular_fftfreq(int n, double d) {
    vd out(n);
    int half = n / 2;
    for (int i = 0; i <= half; ++i)
        out[i] = 2.0 * PI * i / (n * d);
    for (int i = half + 1; i < n; ++i)
        out[i] = 2.0 * PI * (i - n) / (n * d);
    return out;
}

// ── Initial conditions ────────────────────────────────────────────────────────

static vd initial_conditions(int nx, int ny,
                              double lx, double ly,
                              double u0, double delta,
                              double amp, int mode) {
    double dx = lx / nx, dy = ly / ny;
    vd omega(nx * ny);
    for (int i = 0; i < nx; ++i) {
        double x = i * dx;
        double pert_x = amp * (2.0 * PI * mode / lx)
                            * std::cos(2.0 * PI * mode * x / lx);
        for (int j = 0; j < ny; ++j) {
            double y = j * dy;
            double z = (y - ly / 2.0) / delta;
            double ch = std::cosh(z);
            omega[i * ny + j] = u0 / delta / (ch * ch) + pert_x;
        }
    }
    return omega;
}

// ── Poisson solve ─────────────────────────────────────────────────────────────

static vc solve_poisson(const vc& omega_hat,
                        const vd& kx, const vd& ky,
                        int nx, int ny) {
    vc psi_hat(omega_hat);
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            int idx = i * ny + j;
            if (i == 0 && j == 0) {
                psi_hat[0] = {0.0, 0.0};
            } else {
                double k2 = kx[idx] * kx[idx] + ky[idx] * ky[idx];
                psi_hat[idx] = omega_hat[idx] / k2;
            }
        }
    }
    return psi_hat;
}

// ── Velocity from psi ─────────────────────────────────────────────────────────

static std::pair<vd, vd> velocity_from_psi(const vc& psi_hat,
                                            const vd& kx, const vd& ky,
                                            int nx, int ny) {
    int n = nx * ny;
    vc u_hat(n), v_hat(n);
    cd I{0.0, 1.0};
    for (int k = 0; k < n; ++k) {
        u_hat[k] =  I * ky[k] * psi_hat[k];
        v_hat[k] = -I * kx[k] * psi_hat[k];
    }
    return {ifft2_real(std::move(u_hat), nx, ny),
            ifft2_real(std::move(v_hat), nx, ny)};
}

// ── Vorticity RHS ─────────────────────────────────────────────────────────────

static vd vorticity_rhs(const vd& omega, const vd& u, const vd& v,
                         double nu,
                         const vd& kx, const vd& ky,
                         int nx, int ny) {
    int n = nx * ny;
    vc omega_hat = fft2(omega, nx, ny);
    cd I{0.0, 1.0};

    vc dx_spec(n), dy_spec(n), lap_spec(n);
    for (int k = 0; k < n; ++k) {
        dx_spec[k]  = I * kx[k] * omega_hat[k];
        dy_spec[k]  = I * ky[k] * omega_hat[k];
        double k2   = kx[k]*kx[k] + ky[k]*ky[k];
        lap_spec[k] = -k2 * omega_hat[k];
    }
    vd dox = ifft2_real(std::move(dx_spec), nx, ny);
    vd doy = ifft2_real(std::move(dy_spec), nx, ny);
    vd lap = ifft2_real(std::move(lap_spec), nx, ny);

    vd rhs(n);
    for (int k = 0; k < n; ++k)
        rhs[k] = -u[k] * dox[k] - v[k] * doy[k] + nu * lap[k];
    return rhs;
}

// ── RK4 step ──────────────────────────────────────────────────────────────────

static vd add_scaled(const vd& a, const vd& b, double s) {
    vd out(a.size());
    for (size_t k = 0; k < a.size(); ++k) out[k] = a[k] + s * b[k];
    return out;
}

static vd rk4_step(const vd& omega, double nu,
                   const vd& kx, const vd& ky,
                   int nx, int ny, double dt) {
    auto f = [&](const vd& w) -> vd {
        vc wh = fft2(w, nx, ny);
        vc ph = solve_poisson(wh, kx, ky, nx, ny);
        auto [u, v] = velocity_from_psi(ph, kx, ky, nx, ny);
        return vorticity_rhs(w, u, v, nu, kx, ky, nx, ny);
    };
    vd k1 = f(omega);
    vd k2 = f(add_scaled(omega, k1, 0.5 * dt));
    vd k3 = f(add_scaled(omega, k2, 0.5 * dt));
    vd k4 = f(add_scaled(omega, k3, dt));

    vd out(omega.size());
    for (size_t k = 0; k < omega.size(); ++k)
        out[k] = omega[k] + (dt / 6.0) * (k1[k] + 2*k2[k] + 2*k3[k] + k4[k]);
    return out;
}

// ── Diagnostics ───────────────────────────────────────────────────────────────

static double mean(const vd& v) {
    return std::accumulate(v.begin(), v.end(), 0.0) / v.size();
}

static Diagnostics compute_diagnostics(const vd& omega,
                                       const vd& u, const vd& v,
                                       const vd& kx, const vd& ky,
                                       int nx, int ny) {
    int n = nx * ny;
    vd ke_arr(n), ens_arr(n);
    double max_w = 0.0;
    for (int k = 0; k < n; ++k) {
        ke_arr[k]  = 0.5 * (u[k]*u[k] + v[k]*v[k]);
        ens_arr[k] = 0.5 * omega[k] * omega[k];
        max_w = std::max(max_w, std::abs(omega[k]));
    }

    cd I{0.0, 1.0};
    vc uh = fft2(u, nx, ny);
    vc vh = fft2(v, nx, ny);
    vc div_spec(n);
    for (int k = 0; k < n; ++k)
        div_spec[k] = I * kx[k] * uh[k] + I * ky[k] * vh[k];
    vd div = ifft2_real(std::move(div_spec), nx, ny);
    vd div2(n);
    for (int k = 0; k < n; ++k) div2[k] = div[k] * div[k];

    return {mean(ke_arr), mean(ens_arr), max_w, std::sqrt(mean(div2))};
}

// ── Main entry point ──────────────────────────────────────────────────────────

SimulationResult simulate(const SimulationRequest& req) {
    using clock = std::chrono::high_resolution_clock;
    auto t0 = clock::now();

    int nx = req.grid_nx, ny = req.grid_ny;
    double lx = req.domain_lx, ly = req.domain_ly;
    double dt = req.dt;
    int nsteps = req.steps;
    double nu  = req.velocity_shear / req.reynolds_number;
    double delta = 0.05 * ly;
    double dx = lx / nx, dy = ly / ny;

    vd kx_1d = angular_fftfreq(nx, dx);
    vd ky_1d = angular_fftfreq(ny, dy);
    vd kx(nx * ny), ky(nx * ny);
    for (int i = 0; i < nx; ++i)
        for (int j = 0; j < ny; ++j) {
            kx[i*ny+j] = kx_1d[i];
            ky[i*ny+j] = ky_1d[j];
        }

    vd omega;
    if (req.initial_omega) {
        omega = *req.initial_omega;
        if ((int)omega.size() != nx * ny)
            throw std::invalid_argument("initial_omega size mismatch");
    } else {
        omega = initial_conditions(nx, ny, lx, ly,
                                   req.velocity_shear, delta,
                                   req.perturbation_amplitude,
                                   req.perturbation_mode);
    }

    double t = 0.0;
    for (int s = 0; s < nsteps; ++s) {
        omega = rk4_step(omega, nu, kx, ky, nx, ny, dt);
        t += dt;
    }

    vc oh  = fft2(omega, nx, ny);
    vc ph  = solve_poisson(oh, kx, ky, nx, ny);
    vd psi = ifft2_real(ph, nx, ny);
    auto [u, v] = velocity_from_psi(ph, kx, ky, nx, ny);
    Diagnostics diag = compute_diagnostics(omega, u, v, kx, ky, nx, ny);

    double elapsed_ms = std::chrono::duration<double, std::milli>(
        clock::now() - t0).count();

    // round t to avoid floating-point drift in JSON
    t = std::round(t * 1e10) / 1e10;

    return {
        "cpp-httplib", "C++",
        nsteps, t, nx, ny,
        std::move(u), std::move(v), std::move(omega), std::move(psi),
        diag,
        std::round(elapsed_ms * 100.0) / 100.0,
    };
}

} // namespace khsim
