# kh-sim — Kelvin-Helmholtz Instability Simulation Suite

A polyglot simulation benchmark: five independent backend implementations of the
2D Kelvin-Helmholtz (KH) instability solver, a React frontend, a Node.js log service,
and a Physics-Informed Neural Network (PINN) companion — all sharing a single OpenAPI
contract and validated against a common Python/NumPy reference kernel.

**Version:** 0.1.0-scaffold | **Status:** in-progress

---

## Physics

The Kelvin-Helmholtz instability occurs at the interface between two fluid layers moving
at different velocities. Small perturbations amplify into characteristic rolling vortex
structures (KH billows).

The solver uses the **vorticity-streamfunction formulation** of 2D incompressible
Navier-Stokes:

```
∂ω/∂t + u·∂ω/∂x + v·∂ω/∂y = ν∇²ω

∇²ψ = -ω    (Poisson)

u = ∂ψ/∂y,  v = -∂ψ/∂x
```

Spatial discretisation is **pseudo-spectral** (2D FFT). Time integration uses **RK4**.
Full physics specification: [`shared/physics/KH-PHYSICS.md`](shared/physics/KH-PHYSICS.md).

---

## Architecture

```
kh-sim/
├── backends/
│   ├── rust/       Rust   + axum         :8001
│   ├── scala/      Scala  + http4s       :8002
│   ├── cpp/        C++    + cpp-httplib  :8003
│   ├── fortran/    Fortran + C-interop   :8004
│   └── pascal/     Pascal + fphttpapp   :8005
├── frontend/       React (dev :3000)
├── log-service/    Node.js + Express     :8006   (MongoDB event log)
├── pinn/           FastAPI PINN service  :8600
├── shared/
│   ├── api/        openapi.yaml          (single API contract, all backends)
│   └── physics/    kh_physics.py         (NumPy reference kernel)
├── auth/           Authentication layer
├── docker/         Compose stack
├── tests/          Cross-backend integration tests
└── vhost/          Nginx vhost configs
```

All five backends expose **identical endpoints** on their respective ports:

| Method | Path       | Description                          |
|--------|------------|--------------------------------------|
| POST   | /simulate  | Run KH instability for N time steps  |
| GET    | /health    | Backend health status                |
| GET    | /info      | Language, version, build metadata    |

Full API spec: [`shared/api/openapi.yaml`](shared/api/openapi.yaml)

---

## Quick Start

### Prerequisites
- Docker 24.x + Compose v2 (for the full stack)
- OR individual language toolchains (see backend READMEs)
- Python 3.11+ (for reference kernel and validation scripts)

### Run reference simulation
```bash
cd shared/physics
python kh_physics.py
# → writes kh_reference_output.json
```

### Run individual backend (example: Rust)
```bash
cd backends/rust
cargo run --release
# Backend listening on :8001

curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"grid_nx":64,"grid_ny":32,"dt":0.001,"steps":100}'
```

### Run full stack (Docker)
```bash
cd docker
docker compose up --build
```

---

## Backend Summary

| Backend  | Language | Framework      | Port | FFT Library        | Status     |
|----------|----------|----------------|------|--------------------|------------|
| rust     | Rust     | axum           | 8001 | rustfft            | scaffold   |
| scala    | Scala    | http4s         | 8002 | Breeze/JTransforms | scaffold   |
| cpp      | C++      | cpp-httplib    | 8003 | FFTW3              | scaffold   |
| fortran  | Fortran  | C-interop HTTP | 8004 | hand-rolled / fftpack5 | scaffold |
| pascal   | Pascal   | fphttpapp      | 8005 | custom DFT / FFTW3 | scaffold   |

---

## Validation Protocol

All backends are validated against the Python/NumPy reference kernel. Pass criteria at
t=0.1 (100 steps, 64×32 grid, Re=1000):

| Diagnostic     | Reference value | Tolerance |
|----------------|----------------|-----------|
| kinetic_energy | 0.112810       | ±5%       |
| enstrophy      | 43.705142      | ±5%       |
| max_vorticity  | 31.907572      | ±5%       |
| divergence_rms | 1.20e-14       | < 1e-10   |

```bash
# Run cross-backend validation
cd tests
python validate_all_backends.py
```

---

## Default Simulation Parameters

| Parameter             | Value  |
|-----------------------|--------|
| Grid                  | 128×64 |
| Domain (Lx × Ly)      | 1.0 × 0.5 |
| Reynolds number Re    | 1000   |
| Time step dt          | 0.001  |
| Default steps         | 100    |
| Perturbation amplitude| 0.01   |
| Perturbation mode k   | 2      |

---

## Log Service

All simulation runs are logged to MongoDB via the Node.js log service on `:8006`.

| Route           | Method | Description                    |
|-----------------|--------|--------------------------------|
| /event          | POST   | Record simulation event        |
| /viewer         | GET    | HTML event viewer              |
| /summary        | GET    | Aggregate run statistics       |
| /health         | GET    | Service health                 |

---

## Project Context

kh-sim is the **numerical reference layer** for the
[MI-M-T](../3-fold-path/backlog/MI-M-T-POC-PROPOSAL.md) test evidence system.
It also serves as a polyglot integration benchmark evaluating FFT implementation
fidelity and HTTP API consistency across five systems languages.

Related: [`PHYSICS-NUMERICAL-METHODS-v0.1.md`](../PHYSICS-NUMERICAL-METHODS-v0.1.md)
(Track NUM — Fortran reference modules + multi-language verification matrix)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions must pass the validation
protocol above before merging.

## License

[MIT](LICENSE)
