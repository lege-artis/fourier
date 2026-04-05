/// validation_test.rs — KH-003 acceptance criteria
///
/// Validates Rust diagnostics against Python/NumPy canonical reference output.
/// Tolerance: ±5% on kinetic_energy and enstrophy (per KH-PHYSICS.md §7).
/// Incompressibility: divergence_rms < 1e-10.
///
/// Reference file: kh-sim/shared/physics/kh_reference_output.json
/// Run: cargo test --test validation_test
use std::path::PathBuf;

use serde::Deserialize;

// ── Mirror of reference JSON diagnostics block ────────────────────────────────

#[derive(Deserialize)]
struct RefDiagnostics {
    kinetic_energy:  f64,
    enstrophy:       f64,
    max_vorticity:   f64,
    divergence_rms:  f64,
}

#[derive(Deserialize)]
struct RefOutput {
    diagnostics: RefDiagnostics,
    grid_nx:     usize,
    grid_ny:     usize,
    steps_completed: usize,
}

// ── Load reference JSON ───────────────────────────────────────────────────────

fn load_reference() -> RefOutput {
    // Path relative to Cargo workspace root (where `cargo test` is run from)
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    // Traverse up to kh-sim/shared/physics/
    path.push("../../shared/physics/kh_reference_output.json");

    let raw = std::fs::read_to_string(&path).unwrap_or_else(|_| {
        panic!(
            "Cannot open reference file at {:?}. \
             Run `python kh_physics.py` in kh-sim/shared/physics/ first.",
            path
        )
    });
    serde_json::from_str(&raw).expect("Failed to deserialise reference JSON")
}

// ── Helpers ───────────────────────────────────────────────────────────────────

fn pct_err(got: f64, reference: f64) -> f64 {
    ((got - reference) / reference).abs() * 100.0
}

// ── Tests ─────────────────────────────────────────────────────────────────────

#[test]
fn test_diagnostics_within_tolerance() {
    let reference = load_reference();
    let ref_d = &reference.diagnostics;

    // Build a matching SimulationRequest (same grid / steps as reference)
    // We access the physics module directly via the binary crate.
    // Because this is an integration test (tests/ dir), we call the public API.
    // The binary crate name is "kh-sim-rust" — Rust normalises '-' to '_' for
    // the crate name used in use statements.
    use kh_sim_rust::physics::simulate;
    use kh_sim_rust::models::SimulationRequest;

    let req = SimulationRequest {
        grid_nx:               reference.grid_nx,
        grid_ny:               reference.grid_ny,
        domain_lx:             1.0,
        domain_ly:             0.5,
        dt:                    0.001,
        steps:                 reference.steps_completed,
        reynolds_number:       1000.0,
        velocity_shear:        1.0,
        perturbation_amplitude:0.01,
        perturbation_mode:     2,
        initial_omega:         None,
    };

    let result = simulate(&req);
    let got = &result.diagnostics;

    println!("--- Rust vs Python reference ---");
    println!("kinetic_energy : got={:.6}  ref={:.6}  err={:.2}%",
             got.kinetic_energy, ref_d.kinetic_energy,
             pct_err(got.kinetic_energy, ref_d.kinetic_energy));
    println!("enstrophy      : got={:.6}  ref={:.6}  err={:.2}%",
             got.enstrophy, ref_d.enstrophy,
             pct_err(got.enstrophy, ref_d.enstrophy));
    println!("max_vorticity  : got={:.6}  ref={:.6}  err={:.2}%",
             got.max_vorticity, ref_d.max_vorticity,
             pct_err(got.max_vorticity, ref_d.max_vorticity));
    println!("divergence_rms : got={:.2e}  ref={:.2e}",
             got.divergence_rms, ref_d.divergence_rms);

    // Acceptance criteria (KH-PHYSICS.md §7)
    assert!(
        pct_err(got.kinetic_energy, ref_d.kinetic_energy) < 5.0,
        "kinetic_energy error {:.2}% exceeds 5% tolerance",
        pct_err(got.kinetic_energy, ref_d.kinetic_energy)
    );
    assert!(
        pct_err(got.enstrophy, ref_d.enstrophy) < 5.0,
        "enstrophy error {:.2}% exceeds 5% tolerance",
        pct_err(got.enstrophy, ref_d.enstrophy)
    );
    assert!(
        got.divergence_rms < 1e-10,
        "divergence_rms {:.2e} exceeds incompressibility threshold 1e-10",
        got.divergence_rms
    );
}

#[test]
fn test_field_shapes() {
    use kh_sim_rust::physics::simulate;
    use kh_sim_rust::models::SimulationRequest;

    let req = SimulationRequest {
        grid_nx: 32, grid_ny: 16,
        domain_lx: 1.0, domain_ly: 0.5,
        dt: 0.001, steps: 10,
        reynolds_number: 1000.0, velocity_shear: 1.0,
        perturbation_amplitude: 0.01, perturbation_mode: 2,
        initial_omega: None,
    };

    let result = simulate(&req);
    let n = req.grid_nx * req.grid_ny;
    assert_eq!(result.u_velocity.len(), n, "u_velocity shape mismatch");
    assert_eq!(result.v_velocity.len(), n, "v_velocity shape mismatch");
    assert_eq!(result.vorticity.len(),  n, "vorticity shape mismatch");
    assert_eq!(result.pressure.len(),   n, "pressure shape mismatch");
    assert!((result.t_final - 0.01).abs() < 1e-9, "t_final mismatch");
}
