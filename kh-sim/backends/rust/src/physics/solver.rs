/// solver.rs — KH instability physics kernel (Rust port of kh_physics.py)
///
/// Physics: 2D incompressible Navier-Stokes, vorticity-streamfunction form.
/// Numerics: pseudo-spectral (full-complex 2D FFT), RK4 time integration.
///
/// Reference: kh-sim/shared/physics/KH-PHYSICS.md
/// Canonical: kh-sim/shared/physics/kh_physics.py
use std::f64::consts::PI;

use num_complex::Complex64;

use super::fft2d::{Fft2DPlans, make_wavenumbers};
use crate::models::{Diagnostics, SimulationRequest, SimulationResult};

// ── Initial conditions ────────────────────────────────────────────────────────

/// Analytic initial vorticity: omega = dv/dx - du/dy
///   u(x,y) = U0 * tanh((y - Ly/2) / delta)
///   v(x,y) = amp * sin(2*PI*mode*x / Lx)
/// => omega_shear = U0/delta * sech^2((y-Ly/2)/delta)
///    omega_pert  = amp * (2*PI*mode/Lx) * cos(2*PI*mode*x/Lx)
fn initial_conditions(
    nx: usize,
    ny: usize,
    lx: f64,
    ly: f64,
    u0: f64,
    delta: f64,
    amp: f64,
    mode: usize,
) -> Vec<f64> {
    let dx = lx / nx as f64;
    let dy = ly / ny as f64;
    let mut omega = vec![0.0f64; nx * ny];

    for i in 0..nx {
        let x = i as f64 * dx;
        let pert_x = amp * (2.0 * PI * mode as f64 / lx) * (2.0 * PI * mode as f64 * x / lx).cos();

        for j in 0..ny {
            let y = j as f64 * dy;
            let z = (y - ly / 2.0) / delta;
            let shear = u0 / delta / z.cosh().powi(2); // sech^2 = 1/cosh^2
            omega[i * ny + j] = shear + pert_x;
        }
    }
    omega
}

// ── Spectral Poisson solve ────────────────────────────────────────────────────

/// Solve nabla^2 psi = -omega in Fourier space:
///   psi_hat = omega_hat / (kx^2 + ky^2)
///   psi_hat[0,0] = 0  (zero mean streamfunction)
fn solve_poisson(
    omega_hat: &[Complex64],
    kx: &[f64],
    ky: &[f64],
    nx: usize,
    ny: usize,
) -> Vec<Complex64> {
    let mut psi_hat = omega_hat.to_vec();

    for i in 0..nx {
        for j in 0..ny {
            let idx = i * ny + j;
            let k2 = kx[idx].powi(2) + ky[idx].powi(2);
            if i == 0 && j == 0 {
                psi_hat[idx] = Complex64::new(0.0, 0.0); // zero mean
            } else {
                psi_hat[idx] = omega_hat[idx] / k2;
            }
        }
    }
    psi_hat
}

// ── Velocity from streamfunction ──────────────────────────────────────────────

/// u = d(psi)/dy  =>  u_hat = i * ky * psi_hat
/// v = -d(psi)/dx =>  v_hat = -i * kx * psi_hat
fn velocity_from_psi_hat(
    psi_hat: &[Complex64],
    kx: &[f64],
    ky: &[f64],
    plans: &Fft2DPlans,
    nx: usize,
    ny: usize,
) -> (Vec<f64>, Vec<f64>) {
    let i_unit = Complex64::new(0.0, 1.0);

    let u_hat: Vec<Complex64> = (0..nx * ny)
        .map(|idx| i_unit * ky[idx] * psi_hat[idx])
        .collect();

    let v_hat: Vec<Complex64> = (0..nx * ny)
        .map(|idx| -i_unit * kx[idx] * psi_hat[idx])
        .collect();

    let u = plans.ifft2_real(&u_hat);
    let v = plans.ifft2_real(&v_hat);
    (u, v)
}

// ── Vorticity RHS ─────────────────────────────────────────────────────────────

/// f(omega) = -u * d(omega)/dx - v * d(omega)/dy + nu * laplacian(omega)
fn vorticity_rhs(
    omega: &[f64],
    u: &[f64],
    v: &[f64],
    nu: f64,
    kx: &[f64],
    ky: &[f64],
    plans: &Fft2DPlans,
    nx: usize,
    ny: usize,
) -> Vec<f64> {
    let i_unit = Complex64::new(0.0, 1.0);
    let omega_hat = plans.fft2(omega);

    let domega_dx: Vec<f64> = {
        let spec: Vec<Complex64> = (0..nx * ny)
            .map(|idx| i_unit * kx[idx] * omega_hat[idx])
            .collect();
        plans.ifft2_real(&spec)
    };

    let domega_dy: Vec<f64> = {
        let spec: Vec<Complex64> = (0..nx * ny)
            .map(|idx| i_unit * ky[idx] * omega_hat[idx])
            .collect();
        plans.ifft2_real(&spec)
    };

    let lap_omega: Vec<f64> = {
        let spec: Vec<Complex64> = (0..nx * ny)
            .map(|idx| {
                let k2 = kx[idx].powi(2) + ky[idx].powi(2);
                -k2 * omega_hat[idx]
            })
            .collect();
        plans.ifft2_real(&spec)
    };

    (0..nx * ny)
        .map(|idx| -u[idx] * domega_dx[idx] - v[idx] * domega_dy[idx] + nu * lap_omega[idx])
        .collect()
}

// ── Single RK4 step ───────────────────────────────────────────────────────────

fn add_scaled(a: &[f64], b: &[f64], scale: f64) -> Vec<f64> {
    a.iter().zip(b.iter()).map(|(&x, &y)| x + scale * y).collect()
}

fn rk4_step(
    omega: &[f64],
    nu: f64,
    kx: &[f64],
    ky: &[f64],
    plans: &Fft2DPlans,
    nx: usize,
    ny: usize,
    dt: f64,
) -> Vec<f64> {
    let step = |w: &[f64]| -> Vec<f64> {
        let w_hat = plans.fft2(w);
        let psi_hat = solve_poisson(&w_hat, kx, ky, nx, ny);
        let (u, v) = velocity_from_psi_hat(&psi_hat, kx, ky, plans, nx, ny);
        vorticity_rhs(w, &u, &v, nu, kx, ky, plans, nx, ny)
    };

    let k1 = step(omega);
    let k2 = step(&add_scaled(omega, &k1, 0.5 * dt));
    let k3 = step(&add_scaled(omega, &k2, 0.5 * dt));
    let k4 = step(&add_scaled(omega, &k3, dt));

    (0..nx * ny)
        .map(|idx| {
            omega[idx] + (dt / 6.0) * (k1[idx] + 2.0 * k2[idx] + 2.0 * k3[idx] + k4[idx])
        })
        .collect()
}

// ── Diagnostics ───────────────────────────────────────────────────────────────

fn mean(v: &[f64]) -> f64 {
    v.iter().sum::<f64>() / v.len() as f64
}

fn compute_diagnostics(
    omega: &[f64],
    u: &[f64],
    v: &[f64],
    kx: &[f64],
    ky: &[f64],
    plans: &Fft2DPlans,
    nx: usize,
    ny: usize,
) -> Diagnostics {
    let i_unit = Complex64::new(0.0, 1.0);

    let ke = 0.5 * mean(&u.iter().zip(v.iter()).map(|(&ui, &vi)| ui * ui + vi * vi).collect::<Vec<_>>());
    let enstrophy = 0.5 * mean(&omega.iter().map(|&w| w * w).collect::<Vec<_>>());
    let max_vorticity = omega.iter().map(|&w| w.abs()).fold(0.0_f64, f64::max);

    // Divergence: d(u)/dx + d(v)/dy should be machine-zero for spectral method
    let u_hat = plans.fft2(u);
    let v_hat = plans.fft2(v);
    let div_spec: Vec<Complex64> = (0..nx * ny)
        .map(|idx| i_unit * kx[idx] * u_hat[idx] + i_unit * ky[idx] * v_hat[idx])
        .collect();
    let div = plans.ifft2_real(&div_spec);
    let divergence_rms = mean(&div.iter().map(|&d| d * d).collect::<Vec<_>>()).sqrt();

    Diagnostics { kinetic_energy: ke, enstrophy, max_vorticity, divergence_rms }
}

// ── Main entry point ──────────────────────────────────────────────────────────

pub fn simulate(req: &SimulationRequest) -> SimulationResult {
    let start = std::time::Instant::now();

    let nx    = req.grid_nx;
    let ny    = req.grid_ny;
    let lx    = req.domain_lx;
    let ly    = req.domain_ly;
    let dt    = req.dt;
    let steps = req.steps;
    let nu    = req.velocity_shear / req.reynolds_number;
    let delta = 0.05 * ly;

    let dx = lx / nx as f64;
    let dy = ly / ny as f64;

    let plans = Fft2DPlans::new(nx, ny);
    let (kx, ky) = make_wavenumbers(nx, ny, dx, dy);

    // Initialise vorticity
    let mut omega: Vec<f64> = match &req.initial_omega {
        Some(v) => {
            assert_eq!(v.len(), nx * ny, "initial_omega length must equal nx*ny");
            v.clone()
        }
        None => initial_conditions(nx, ny, lx, ly, req.velocity_shear, delta,
                                   req.perturbation_amplitude, req.perturbation_mode),
    };

    // Time integration
    let mut t = 0.0_f64;
    for _ in 0..steps {
        omega = rk4_step(&omega, nu, &kx, &ky, &plans, nx, ny, dt);
        t += dt;
    }

    // Final field recovery
    let omega_hat = plans.fft2(&omega);
    let psi_hat   = solve_poisson(&omega_hat, &kx, &ky, nx, ny);
    let psi       = plans.ifft2_real(&psi_hat);
    let (u, v)    = velocity_from_psi_hat(&psi_hat, &kx, &ky, &plans, nx, ny);

    let diagnostics = compute_diagnostics(&omega, &u, &v, &kx, &ky, &plans, nx, ny);

    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;

    SimulationResult {
        backend:         "rust-axum",
        language:        "Rust",
        steps_completed: steps,
        t_final:         (t * 1e10).round() / 1e10,
        grid_nx:         nx,
        grid_ny:         ny,
        u_velocity:      u,
        v_velocity:      v,
        vorticity:       omega,
        pressure:        psi,
        diagnostics,
        compute_time_ms: (elapsed_ms * 100.0).round() / 100.0,
    }
}
