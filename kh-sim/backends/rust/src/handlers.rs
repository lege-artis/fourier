/// handlers.rs — axum route handlers
///
/// Endpoints (per openapi.yaml):
///   POST /simulate   -> run KH simulation, return SimulationResult JSON
///   GET  /health     -> liveness probe
///   GET  /info       -> backend metadata
use axum::{extract::Json, http::StatusCode, response::IntoResponse};
use tracing::info;

use crate::models::{HealthResponse, InfoResponse, SimulationRequest};
use crate::physics;

// ── POST /simulate ────────────────────────────────────────────────────────────

pub async fn simulate(
    Json(req): Json<SimulationRequest>,
) -> impl IntoResponse {
    info!(
        nx = req.grid_nx,
        ny = req.grid_ny,
        steps = req.steps,
        re = req.reynolds_number,
        "simulate request received"
    );

    // Run physics on a blocking thread so the async executor is not starved
    let result = tokio::task::spawn_blocking(move || physics::simulate(&req))
        .await
        .expect("physics task panicked");

    info!(
        t_final         = result.t_final,
        ke              = result.diagnostics.kinetic_energy,
        enstrophy       = result.diagnostics.enstrophy,
        max_vorticity   = result.diagnostics.max_vorticity,
        divergence_rms  = result.diagnostics.divergence_rms,
        compute_ms      = result.compute_time_ms,
        "simulate complete"
    );

    (StatusCode::OK, Json(result))
}

// ── GET /health ───────────────────────────────────────────────────────────────

pub async fn health() -> impl IntoResponse {
    Json(HealthResponse {
        status:  "ok",
        backend: "rust-axum",
        port:    8001,
    })
}

// ── GET /info ─────────────────────────────────────────────────────────────────

pub async fn info() -> impl IntoResponse {
    Json(InfoResponse {
        backend:      "rust-axum",
        language:     "Rust",
        framework:    "axum 0.7",
        fft_library:  "rustfft 6",
        port:         8001,
        openapi_spec: "kh-sim/shared/api/openapi.yaml",
    })
}
