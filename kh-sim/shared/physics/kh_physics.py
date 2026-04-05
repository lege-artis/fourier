"""
kh_physics.py — Kelvin-Helmholtz instability reference implementation
======================================================================
2D incompressible Navier-Stokes, vorticity-streamfunction formulation.
Doubly periodic domain, pseudo-spectral Poisson solver, RK4 time stepping.

This is the CANONICAL reference. All backend implementations (Rust, Scala,
C++, Fortran, Pascal) must validate their output against this module.

See: shared/physics/KH-PHYSICS.md for full physics documentation.
See: shared/api/openapi.yaml for REST API contract.

Usage:
    python kh_physics.py                        # run reference smoke test
    python kh_physics.py --nx 128 --ny 64 --steps 200 --re 1000
"""

import numpy as np
import json
import time
import argparse
from dataclasses import dataclass, field, asdict
from typing import Optional, List


# ── Data structures (mirrors REST API schema) ──────────────────────────────────

@dataclass
class SimulationRequest:
    grid_nx:               int   = 128
    grid_ny:               int   = 64
    domain_lx:             float = 1.0
    domain_ly:             float = 0.5
    dt:                    float = 0.001
    steps:                 int   = 100
    reynolds_number:       float = 1000.0
    velocity_shear:        float = 1.0
    perturbation_amplitude:float = 0.01
    perturbation_mode:     int   = 2
    initial_omega:         Optional[List[float]] = None  # flattened Nx*Ny


@dataclass
class Diagnostics:
    kinetic_energy:  float = 0.0
    enstrophy:       float = 0.0
    max_vorticity:   float = 0.0
    divergence_rms:  float = 0.0


@dataclass
class SimulationResult:
    backend:          str   = "python-numpy"
    language:         str   = "Python"
    steps_completed:  int   = 0
    t_final:          float = 0.0
    grid_nx:          int   = 0
    grid_ny:          int   = 0
    u_velocity:       List[float] = field(default_factory=list)
    v_velocity:       List[float] = field(default_factory=list)
    vorticity:        List[float] = field(default_factory=list)
    pressure:         List[float] = field(default_factory=list)  # streamfunction ψ
    diagnostics:      Diagnostics = field(default_factory=Diagnostics)
    compute_time_ms:  float = 0.0


# ── Physics kernels ────────────────────────────────────────────────────────────

def _wavenumbers(nx: int, ny: int, dx: float, dy: float):
    """
    Return 2D wavenumber arrays for rfft2 output shape (nx, ny//2+1).
    rfft2 applies full FFT along axis-0 (kx) and real FFT along axis-1 (ky).
    """
    kx = 2.0 * np.pi * np.fft.fftfreq(nx, d=dx)    # full FFT axis-0: shape (nx,)
    ky = 2.0 * np.pi * np.fft.rfftfreq(ny, d=dy)   # real FFT axis-1: shape (ny//2+1,)
    KX, KY = np.meshgrid(kx, ky, indexing='ij')    # shape (nx, ny//2+1) ✓
    return KX, KY


def initial_conditions(nx: int, ny: int, lx: float, ly: float,
                       U0: float, delta: float, amp: float, mode: int
                       ) -> np.ndarray:
    """
    Compute initial vorticity field analytically.

    IC velocity:
        u(x,y) = U0 * tanh((y - Ly/2) / delta)
        v(x,y) = amp * sin(2*pi*mode*x / Lx)

    Vorticity ω = dv/dx - du/dy:
        = amp*(2*pi*mode/Lx)*cos(2*pi*mode*x/Lx)  [from v]
        + U0/delta * sech²((y-Ly/2)/delta)         [from -du/dy, note sign]
    """
    dx = lx / nx
    dy = ly / ny
    x = np.arange(nx) * dx
    y = np.arange(ny) * dy
    X, Y = np.meshgrid(x, y, indexing='ij')

    # Vorticity from shear layer (positive: upper layer faster)
    omega_shear = U0 / delta / np.cosh((Y - ly / 2.0) / delta) ** 2

    # Vorticity perturbation from sinusoidal v-perturbation
    omega_pert = amp * (2.0 * np.pi * mode / lx) * np.cos(2.0 * np.pi * mode * X / lx)

    return omega_shear + omega_pert


def solve_poisson(omega_hat: np.ndarray, KX: np.ndarray, KY: np.ndarray,
                  nx: int, ny: int) -> np.ndarray:
    """
    Spectral Poisson solve: ∇²ψ = -ω  →  ψ̂ = ω̂ / (kx²+ky²)

    Returns psi_hat (rfft2 coefficients).
    Mean mode (kx=ky=0) set to zero: fixes ψ_mean = 0.
    """
    K2 = KX ** 2 + KY ** 2
    K2[0, 0] = 1.0          # avoid divide-by-zero; corrected below
    psi_hat = omega_hat / K2
    psi_hat[0, 0] = 0.0     # zero mean streamfunction
    return psi_hat


def velocity_from_psi_hat(psi_hat: np.ndarray, KX: np.ndarray, KY: np.ndarray,
                           nx: int, ny: int) -> tuple:
    """
    Recover velocity from streamfunction via spectral differentiation.
        u =  dψ/dy  →  û = i·ky·ψ̂
        v = -dψ/dx  →  v̂ = -i·kx·ψ̂
    """
    u = np.fft.irfft2(1j * KY * psi_hat, s=(nx, ny))
    v = np.fft.irfft2(-1j * KX * psi_hat, s=(nx, ny))
    return u, v


def vorticity_rhs(omega: np.ndarray, u: np.ndarray, v: np.ndarray,
                  nu: float, KX: np.ndarray, KY: np.ndarray,
                  nx: int, ny: int) -> np.ndarray:
    """
    RHS of vorticity transport equation (spectral):
        f(ω) = -u·dω/dx - v·dω/dy + ν·∇²ω
    """
    omega_hat = np.fft.rfft2(omega)
    K2 = KX ** 2 + KY ** 2

    domega_dx = np.fft.irfft2(1j * KX * omega_hat, s=(nx, ny))
    domega_dy = np.fft.irfft2(1j * KY * omega_hat, s=(nx, ny))
    laplacian_omega = np.fft.irfft2(-K2 * omega_hat, s=(nx, ny))

    return -u * domega_dx - v * domega_dy + nu * laplacian_omega


def rk4_step(omega: np.ndarray, nu: float,
             KX: np.ndarray, KY: np.ndarray,
             nx: int, ny: int, dt: float) -> np.ndarray:
    """Single RK4 time step for vorticity field."""

    def step_with_omega(w):
        w_hat = np.fft.rfft2(w)
        psi_hat = solve_poisson(w_hat, KX, KY, nx, ny)
        u, v = velocity_from_psi_hat(psi_hat, KX, KY, nx, ny)
        return vorticity_rhs(w, u, v, nu, KX, KY, nx, ny)

    k1 = step_with_omega(omega)
    k2 = step_with_omega(omega + 0.5 * dt * k1)
    k3 = step_with_omega(omega + 0.5 * dt * k2)
    k4 = step_with_omega(omega + dt * k3)

    return omega + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


# ── Main simulation entry point ────────────────────────────────────────────────

def simulate(req: SimulationRequest) -> SimulationResult:
    """
    Run KH instability simulation. Returns SimulationResult matching REST schema.
    """
    t_start = time.perf_counter()

    nx, ny   = req.grid_nx, req.grid_ny
    lx, ly   = req.domain_lx, req.domain_ly
    dt       = req.dt
    steps    = req.steps
    nu       = req.velocity_shear / req.reynolds_number
    delta    = 0.05 * ly

    dx, dy   = lx / nx, ly / ny
    KX, KY   = _wavenumbers(nx, ny, dx, dy)

    # Initialise vorticity
    if req.initial_omega is not None:
        omega = np.array(req.initial_omega, dtype=float).reshape(nx, ny)
    else:
        omega = initial_conditions(nx, ny, lx, ly,
                                   U0=req.velocity_shear,
                                   delta=delta,
                                   amp=req.perturbation_amplitude,
                                   mode=req.perturbation_mode)

    # Time loop
    t = 0.0
    for _ in range(steps):
        omega = rk4_step(omega, nu, KX, KY, nx, ny, dt)
        t += dt

    # Final field recovery
    omega_hat = np.fft.rfft2(omega)
    psi_hat   = solve_poisson(omega_hat, KX, KY, nx, ny)
    psi       = np.fft.irfft2(psi_hat, s=(nx, ny))
    u, v      = velocity_from_psi_hat(psi_hat, KX, KY, nx, ny)

    # Diagnostics
    ke         = 0.5 * float(np.mean(u ** 2 + v ** 2))
    enstrophy  = 0.5 * float(np.mean(omega ** 2))
    max_vort   = float(np.max(np.abs(omega)))
    # Divergence should be machine-zero for spectral method
    div        = float(np.sqrt(np.mean(
        (np.fft.irfft2(1j * KX * np.fft.rfft2(u), s=(nx, ny)) +
         np.fft.irfft2(1j * KY * np.fft.rfft2(v), s=(nx, ny))) ** 2
    )))

    elapsed_ms = (time.perf_counter() - t_start) * 1000.0

    return SimulationResult(
        backend          = "python-numpy",
        language         = "Python",
        steps_completed  = steps,
        t_final          = round(t, 10),
        grid_nx          = nx,
        grid_ny          = ny,
        u_velocity       = u.flatten().tolist(),
        v_velocity       = v.flatten().tolist(),
        vorticity        = omega.flatten().tolist(),
        pressure         = psi.flatten().tolist(),
        diagnostics      = Diagnostics(
            kinetic_energy = ke,
            enstrophy      = enstrophy,
            max_vorticity  = max_vort,
            divergence_rms = div,
        ),
        compute_time_ms  = round(elapsed_ms, 2),
    )


# ── CLI / smoke test ───────────────────────────────────────────────────────────

def _parse_args():
    p = argparse.ArgumentParser(description="KH instability reference solver")
    p.add_argument("--nx",    type=int,   default=64,    help="Grid points x")
    p.add_argument("--ny",    type=int,   default=32,    help="Grid points y")
    p.add_argument("--lx",    type=float, default=1.0,   help="Domain length x")
    p.add_argument("--ly",    type=float, default=0.5,   help="Domain length y")
    p.add_argument("--dt",    type=float, default=0.001, help="Time step")
    p.add_argument("--steps", type=int,   default=100,   help="Steps to run")
    p.add_argument("--re",    type=float, default=1000.0,help="Reynolds number")
    p.add_argument("--amp",   type=float, default=0.01,  help="Perturbation amplitude")
    p.add_argument("--mode",  type=int,   default=2,     help="Perturbation mode")
    p.add_argument("--out",   type=str,   default="kh_reference_output.json",
                   help="Output JSON path")
    p.add_argument("--full",  action="store_true",
                   help="Include full field arrays in output (large)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    req = SimulationRequest(
        grid_nx=args.nx, grid_ny=args.ny,
        domain_lx=args.lx, domain_ly=args.ly,
        dt=args.dt, steps=args.steps,
        reynolds_number=args.re,
        perturbation_amplitude=args.amp,
        perturbation_mode=args.mode,
    )

    print(f"KH instability reference simulation")
    print(f"  Grid: {req.grid_nx}x{req.grid_ny} | dt={req.dt} | steps={req.steps} | Re={req.reynolds_number}")
    print(f"  Domain: [{req.domain_lx} x {req.domain_ly}] | amp={req.perturbation_amplitude} | mode={req.perturbation_mode}")
    print()

    result = simulate(req)

    print(f"  t_final          = {result.t_final:.4f}")
    print(f"  kinetic_energy   = {result.diagnostics.kinetic_energy:.6f}")
    print(f"  enstrophy        = {result.diagnostics.enstrophy:.6f}")
    print(f"  max_vorticity    = {result.diagnostics.max_vorticity:.6f}")
    print(f"  divergence_rms   = {result.diagnostics.divergence_rms:.2e}  (should be < 1e-10)")
    print(f"  compute_time     = {result.compute_time_ms:.1f} ms")

    # Save reference output (strip large arrays unless --full)
    out_dict = asdict(result)
    if not args.full:
        for fld in ("u_velocity", "v_velocity", "vorticity", "pressure"):
            vals = out_dict[fld]
            out_dict[fld] = {
                "length":   len(vals),
                "first_10": vals[:10],
                "last_10":  vals[-10:],
                "min":      float(min(vals)),
                "max":      float(max(vals)),
                "mean":     float(sum(vals) / len(vals)),
            }

    with open(args.out, "w") as f:
        json.dump(out_dict, f, indent=2)

    print(f"\n  Reference output -> {args.out}")
    print("\n  [PASS] Reference simulation complete.")
