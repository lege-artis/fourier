#pragma once
// models.hpp — REST API data structures (mirrors openapi.yaml)
#include <optional>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>

namespace khsim {

// ── Request ───────────────────────────────────────────────────────────────────

struct SimulationRequest {
    int    grid_nx                = 128;
    int    grid_ny                = 64;
    double domain_lx              = 1.0;
    double domain_ly              = 0.5;
    double dt                     = 0.001;
    int    steps                  = 100;
    double reynolds_number        = 1000.0;
    double velocity_shear         = 1.0;
    double perturbation_amplitude = 0.01;
    int    perturbation_mode      = 2;
    std::optional<std::vector<double>> initial_omega;
};

inline void from_json(const nlohmann::json& j, SimulationRequest& r) {
    if (j.contains("grid_nx"))                r.grid_nx                = j["grid_nx"];
    if (j.contains("grid_ny"))                r.grid_ny                = j["grid_ny"];
    if (j.contains("domain_lx"))              r.domain_lx              = j["domain_lx"];
    if (j.contains("domain_ly"))              r.domain_ly              = j["domain_ly"];
    if (j.contains("dt"))                     r.dt                     = j["dt"];
    if (j.contains("steps"))                  r.steps                  = j["steps"];
    if (j.contains("reynolds_number"))        r.reynolds_number        = j["reynolds_number"];
    if (j.contains("velocity_shear"))         r.velocity_shear         = j["velocity_shear"];
    if (j.contains("perturbation_amplitude")) r.perturbation_amplitude = j["perturbation_amplitude"];
    if (j.contains("perturbation_mode"))      r.perturbation_mode      = j["perturbation_mode"];
    if (j.contains("initial_omega") && !j["initial_omega"].is_null())
        r.initial_omega = j["initial_omega"].get<std::vector<double>>();
}

// ── Response ──────────────────────────────────────────────────────────────────

struct Diagnostics {
    double kinetic_energy  = 0.0;
    double enstrophy       = 0.0;
    double max_vorticity   = 0.0;
    double divergence_rms  = 0.0;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Diagnostics,
    kinetic_energy, enstrophy, max_vorticity, divergence_rms)

struct SimulationResult {
    std::string          backend;
    std::string          language;
    int                  steps_completed;
    double               t_final;
    int                  grid_nx;
    int                  grid_ny;
    std::vector<double>  u_velocity;
    std::vector<double>  v_velocity;
    std::vector<double>  vorticity;
    std::vector<double>  pressure;
    Diagnostics          diagnostics;
    double               compute_time_ms;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(SimulationResult,
    backend, language, steps_completed, t_final,
    grid_nx, grid_ny,
    u_velocity, v_velocity, vorticity, pressure,
    diagnostics, compute_time_ms)

} // namespace khsim
