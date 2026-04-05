/// models.rs — REST API data structures (mirrors openapi.yaml / kh_physics.py dataclasses)
use serde::{Deserialize, Serialize};

// ── Request ──────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
pub struct SimulationRequest {
    #[serde(default = "default_grid_nx")]
    pub grid_nx: usize,

    #[serde(default = "default_grid_ny")]
    pub grid_ny: usize,

    #[serde(default = "default_domain_lx")]
    pub domain_lx: f64,

    #[serde(default = "default_domain_ly")]
    pub domain_ly: f64,

    #[serde(default = "default_dt")]
    pub dt: f64,

    #[serde(default = "default_steps")]
    pub steps: usize,

    #[serde(default = "default_reynolds_number")]
    pub reynolds_number: f64,

    #[serde(default = "default_velocity_shear")]
    pub velocity_shear: f64,

    #[serde(default = "default_perturbation_amplitude")]
    pub perturbation_amplitude: f64,

    #[serde(default = "default_perturbation_mode")]
    pub perturbation_mode: usize,

    /// Optional: pre-initialised vorticity (row-major flattened, length nx*ny).
    /// If None, the analytic IC is used.
    pub initial_omega: Option<Vec<f64>>,
}

fn default_grid_nx()                -> usize { 128 }
fn default_grid_ny()                -> usize { 64  }
fn default_domain_lx()              -> f64   { 1.0 }
fn default_domain_ly()              -> f64   { 0.5 }
fn default_dt()                     -> f64   { 0.001 }
fn default_steps()                  -> usize { 100 }
fn default_reynolds_number()        -> f64   { 1000.0 }
fn default_velocity_shear()         -> f64   { 1.0 }
fn default_perturbation_amplitude() -> f64   { 0.01 }
fn default_perturbation_mode()      -> usize { 2 }

// ── Response ─────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize)]
pub struct Diagnostics {
    pub kinetic_energy:  f64,
    pub enstrophy:       f64,
    pub max_vorticity:   f64,
    pub divergence_rms:  f64,
}

#[derive(Debug, Serialize)]
pub struct SimulationResult {
    pub backend:         &'static str,
    pub language:        &'static str,
    pub steps_completed: usize,
    pub t_final:         f64,
    pub grid_nx:         usize,
    pub grid_ny:         usize,
    pub u_velocity:      Vec<f64>,
    pub v_velocity:      Vec<f64>,
    pub vorticity:       Vec<f64>,
    pub pressure:        Vec<f64>,   // streamfunction psi
    pub diagnostics:     Diagnostics,
    pub compute_time_ms: f64,
}

// ── Health / Info ─────────────────────────────────────────────────────────────

#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status:  &'static str,
    pub backend: &'static str,
    pub port:    u16,
}

#[derive(Debug, Serialize)]
pub struct InfoResponse {
    pub backend:      &'static str,
    pub language:     &'static str,
    pub framework:    &'static str,
    pub fft_library:  &'static str,
    pub port:         u16,
    pub openapi_spec: &'static str,
}
