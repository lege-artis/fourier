// main.cpp — KH-SIM C++ backend (KH-005)
// HTTP server: cpp-httplib 0.18 on port 8003
// Spec: kh-sim/shared/api/openapi.yaml

#include "physics.hpp"

#include <httplib.h>
#include <nlohmann/json.hpp>

#include <iostream>
#include <stdexcept>

using json = nlohmann::json;

static void set_cors(httplib::Response& res) {
    res.set_header("Access-Control-Allow-Origin",  "*");
    res.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.set_header("Access-Control-Allow-Headers", "Content-Type");
}

int main() {
    httplib::Server svr;

    // ── CORS preflight ────────────────────────────────────────────────────────
    svr.Options(".*", [](const httplib::Request&, httplib::Response& res) {
        set_cors(res);
        res.status = 204;
    });

    // ── POST /simulate ────────────────────────────────────────────────────────
    svr.Post("/simulate", [](const httplib::Request& req, httplib::Response& res) {
        set_cors(res);
        try {
            auto j = json::parse(req.body);
            khsim::SimulationRequest sr;
            khsim::from_json(j, sr);

            std::cout << "[simulate] nx=" << sr.grid_nx
                      << " ny=" << sr.grid_ny
                      << " steps=" << sr.steps
                      << " Re=" << sr.reynolds_number << "\n";

            auto result = khsim::simulate(sr);
            json out = result;

            std::cout << "[simulate] done t=" << result.t_final
                      << " ke=" << result.diagnostics.kinetic_energy
                      << " ms=" << result.compute_time_ms << "\n";

            res.set_content(out.dump(), "application/json");
        } catch (const std::exception& e) {
            json err{{"error", e.what()}};
            res.status = 400;
            res.set_content(err.dump(), "application/json");
        }
    });

    // ── GET /health ───────────────────────────────────────────────────────────
    svr.Get("/health", [](const httplib::Request&, httplib::Response& res) {
        set_cors(res);
        json h{{"status", "ok"}, {"backend", "cpp-httplib"}, {"port", 8003}};
        res.set_content(h.dump(), "application/json");
    });

    // ── GET /info ─────────────────────────────────────────────────────────────
    svr.Get("/info", [](const httplib::Request&, httplib::Response& res) {
        set_cors(res);
        json info{
            {"backend",      "cpp-httplib"},
            {"language",     "C++"},
            {"framework",    "cpp-httplib 0.18"},
            {"fft_library",  "Cooley-Tukey (built-in)"},
            {"port",         8003},
            {"openapi_spec", "kh-sim/shared/api/openapi.yaml"},
        };
        res.set_content(info.dump(), "application/json");
    });

    constexpr int PORT = 8003;
    std::cout << "kh-sim C++ backend listening on http://0.0.0.0:" << PORT << "\n";
    svr.listen("0.0.0.0", PORT);
}
