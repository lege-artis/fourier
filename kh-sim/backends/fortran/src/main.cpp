// main.cpp — KH-SIM Fortran backend HTTP server (KH-006)
// cpp-httplib on port 8004; physics delegated to Fortran via kh_shim

#include "kh_shim.hpp"

#include <httplib.h>
#include <nlohmann/json.hpp>

#include <iostream>
#include <stdexcept>

using json = nlohmann::json;

static void cors(httplib::Response& res) {
    res.set_header("Access-Control-Allow-Origin",  "*");
    res.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.set_header("Access-Control-Allow-Headers", "Content-Type");
}

static khsim::SimRequest parse_request(const json& j) {
    khsim::SimRequest r;
    if (j.contains("grid_nx"))                r.nx   = j["grid_nx"];
    if (j.contains("grid_ny"))                r.ny   = j["grid_ny"];
    if (j.contains("domain_lx"))              r.lx   = j["domain_lx"];
    if (j.contains("domain_ly"))              r.ly   = j["domain_ly"];
    if (j.contains("dt"))                     r.dt   = j["dt"];
    if (j.contains("steps"))                  r.steps= j["steps"];
    if (j.contains("reynolds_number"))        r.re   = j["reynolds_number"];
    if (j.contains("velocity_shear"))         r.u0   = j["velocity_shear"];
    if (j.contains("perturbation_amplitude")) r.amp  = j["perturbation_amplitude"];
    if (j.contains("perturbation_mode"))      r.mode = j["perturbation_mode"];
    if (j.contains("initial_omega") && !j["initial_omega"].is_null())
        r.init_omega = j["initial_omega"].get<std::vector<double>>();
    return r;
}

int main() {
    httplib::Server svr;

    svr.Options(".*", [](const httplib::Request&, httplib::Response& res) {
        cors(res); res.status = 204;
    });

    svr.Post("/simulate", [](const httplib::Request& req, httplib::Response& res) {
        cors(res);
        try {
            auto j  = json::parse(req.body);
            auto sr = parse_request(j);
            std::cout << "[simulate] nx=" << sr.nx << " ny=" << sr.ny
                      << " steps=" << sr.steps << " Re=" << sr.re << "\n";
            auto r = khsim::simulate(sr);
            json out;
            out["backend"]         = r.backend;
            out["language"]        = r.language;
            out["steps_completed"] = r.steps_completed;
            out["t_final"]         = r.t_final;
            out["grid_nx"]         = r.nx;
            out["grid_ny"]         = r.ny;
            out["u_velocity"]      = r.u;
            out["v_velocity"]      = r.v;
            out["vorticity"]       = r.omega;
            out["pressure"]        = r.psi;
            out["diagnostics"] = {
                {"kinetic_energy",  r.diag.kinetic_energy},
                {"enstrophy",       r.diag.enstrophy},
                {"max_vorticity",   r.diag.max_vorticity},
                {"divergence_rms",  r.diag.divergence_rms},
            };
            out["compute_time_ms"] = r.compute_ms;
            std::cout << "[simulate] done t=" << r.t_final
                      << " ke=" << r.diag.kinetic_energy
                      << " ms=" << r.compute_ms << "\n";
            res.set_content(out.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 400;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Get("/health", [](const httplib::Request&, httplib::Response& res) {
        cors(res);
        res.set_content(
            json{{"status","ok"},{"backend","fortran-httplib"},{"port",8004}}.dump(),
            "application/json");
    });

    svr.Get("/info", [](const httplib::Request&, httplib::Response& res) {
        cors(res);
        res.set_content(json{
            {"backend",      "fortran-httplib"},
            {"language",     "Fortran"},
            {"framework",    "cpp-httplib 0.18 (C-interop shim)"},
            {"fft_library",  "Cooley-Tukey (native Fortran)"},
            {"port",         8004},
            {"openapi_spec", "kh-sim/shared/api/openapi.yaml"},
        }.dump(), "application/json");
    });

    constexpr int PORT = 8004;
    std::cout << "kh-sim Fortran backend listening on http://0.0.0.0:" << PORT << "\n";
    svr.listen("0.0.0.0", PORT);
}
