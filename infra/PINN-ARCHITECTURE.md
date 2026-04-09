# PINN Architecture — Dual-Backend Physics-Informed Neural Networks
**Project:** VibeCodeProjects — PINN Integration (ml-infra)
**Version:** 1.0.0 | **Date:** 2026-03-28
**Status:** Architecture design — implementation pending
**Author:** ThinkPad / CoWork session 2026-03-28
**Supersedes:** —
**Related docs:** `infra/ML-ARCHITECTURE.md`, `infra/LOG-ARCHITECTURE.md`

---

## 1. Motivation and Scope

Physics-Informed Neural Networks (PINNs) encode governing PDEs directly into the neural network loss function, enabling mesh-free solutions to complex differential equation systems. For the **kh-sim** project (Kelvin-Helmholtz instability simulation), PINNs offer an alternative to classical numerical solvers — allowing learned, generalised solutions parameterised over initial/boundary conditions.

This document covers:
- Dual-backend strategy (DeepXDE + JAX/Equinox)
- Common abstraction interface (Strategy pattern, FastAPI REST)
- Integration topology with the existing platform ecosystem
- Data and result schemas
- UML component, sequence, and class diagrams
- Architecture Decision Record (ADR-PINN-001)
- Implementation task map (PINN-001..009)

**Scope is limited to the kh-sim domain at this stage.** The PINN solver interface is designed for extension to additional PDE families (heat equation, wave equation, Schrödinger) without backend coupling.

---

## 2. Architecture Decision Record — ADR-PINN-001

**Title:** PINN Framework Selection — Parallel Evaluation Strategy

**Status:** Accepted (2026-03-28)

**Context:**
The ml-infra project initially specified TensorFlow (TF Serving) as the ML backend. TF Serving is an inference server for pre-trained SavedModels; it does not natively support PINN-specific training workflows (adaptive collocation, PDE residual loss, automatic differentiation over spatial-temporal domains). Two candidates were evaluated:

| Criterion | DeepXDE | JAX + Equinox/Flax |
|-----------|---------|-------------------|
| PINN-specific API | Yes (purpose-built) | No (manual implementation) |
| PDE families supported | Navier-Stokes, KH, heat, wave, ... | Any (custom AD) |
| Backend options | TF / PyTorch / JAX / PaddlePaddle | JAX native |
| TF Serving compatibility | Yes (via TF backend → SavedModel) | No (Torchserve not needed; FastAPI serve) |
| Forward-mode AD (∂u/∂x exact) | Partial | Native (jax.jvp) |
| vmapping over collocation pts | Via backend | Native (jax.vmap) |
| JIT compilation | Via backend | Native (jax.jit) |
| GPU requirement | Optional | Optional |
| Research community | PINN-centric, active | High-performance physics ML |
| Learning curve | Low-medium | High |

**Decision:**
Install and implement both backends in parallel within a common interface. The backend is selected at runtime via configuration (environment variable or API parameter). Evidence from the kh-sim domain (accuracy, training speed, memory footprint) will drive the production decision. Interfaces to the platform ecosystem are defined once and are backend-agnostic.

TF Serving (from ML-ARCHITECTURE.md) is retained for general ML inference (non-PINN models). The PINN solver uses its own FastAPI serving layer.

**Consequences:**
- Additional development effort (two implementations) — offset by deferred framework lock-in
- Common REST interface must be agreed before either backend is implemented
- DeepXDE(TF backend) → SavedModel → TF Serving pathway remains available as a third option for pure inference after training
- JAX backend path requires a lightweight FastAPI serve layer (no TF Serving)

---

## 3. Component Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CONSUMERS                                                              │
│                                                                         │
│  kh-sim React F/E ──────────────────────────────────────────────────┐  │
│  kh-sim Rust/Scala/C++/Fortran/Pascal backends (optional co-solve) ─┤  │
│  External REST clients                                               │  │
└──────────────────────────────────────────────────────────────────┬──┘  │
                                                                   │ HTTP │
┌──────────────────────────────────────────────────────────────────▼──────┐
│  PINN FASTAPI SERVICE  (port 8600)                                       │
│                                                                          │
│  POST /v1/pinn/solve          GET /v1/pinn/results/{id}                  │
│  POST /v1/pinn/train          GET /v1/pinn/backends                      │
│  GET  /v1/pinn/health                                                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  PINN BACKEND DISPATCHER  (Strategy Pattern)                     │   │
│  │                                                                  │   │
│  │  backend = config["PINN_BACKEND"] or request.backend             │   │
│  │  solver  = BackendRegistry.get(backend)  # implements PINNSolver │   │
│  └──────────────┬───────────────────────────────────┬──────────────┘   │
│                 │                                   │                   │
│    ┌────────────▼────────────┐      ┌───────────────▼──────────────┐   │
│    │  DeepXDE Backend        │      │  JAX + Equinox Backend        │   │
│    │                         │      │                               │   │
│    │  deepxde (TF/JAX/PT)    │      │  jax, equinox, optax, flax   │   │
│    │  domain decomposition   │      │  jax.jit, jax.vmap, jax.jvp  │   │
│    │  adaptive sampling      │      │  custom PDE residual loss     │   │
│    │  → SavedModel (opt.)    │      │  → JAX JIT-compiled fn        │   │
│    └────────────┬────────────┘      └───────────────┬──────────────┘   │
└─────────────────┼──────────────────────────────────┼───────────────────┘
                  │ results                           │ results
┌─────────────────▼──────────────────────────────────▼───────────────────┐
│  PERSISTENCE LAYER                                                       │
│                                                                          │
│  PostgreSQL (vibedev)                                                    │
│  └── pinn_runs       — run metadata, params, status, backend            │
│  └── pinn_solutions  — solution snapshots (jsonb field array)           │
│                                                                          │
│  MongoDB (vibedev)                                                       │
│  └── pinn_metrics    — per-epoch training loss, residuals, timing       │
│  └── logs            — standard log events (log-connector-python)        │
└──────────────────────────────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────────────┐
│  OPTIONAL: TF SERVING (port 8501)                                        │
│                                                                          │
│  DeepXDE(TF backend) → export SavedModel → TF Serving for pure inference│
│  (post-training serving path, bypasses FastAPI training overhead)        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. UML — Logical Component Diagram

```
┌──────────────────────────────────────────────────────────┐
│ <<component>>                                            │
│ PINNService (FastAPI :8600)                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ <<interface>>                                     │  │
│  │ PINNSolver                                        │  │
│  │  + solve(PDEProblem) : SolutionField              │  │
│  │  + train(TrainingConfig) : TrainedModel           │  │
│  │  + evaluate(TrainedModel, np.ndarray) : np.ndarray│  │
│  │  + backend_name() : str                           │  │
│  └────────────────────┬──────────────────────────────┘  │
│             ┌──────────┴───────────┐                    │
│  ┌──────────▼──────┐   ┌──────────▼────────┐           │
│  │DeepXDEBackend   │   │JAXEquinoxBackend   │           │
│  │ -dde_model      │   │ -eqx_model         │           │
│  │ -geometry       │   │ -params            │           │
│  │ -pde_fn         │   │ -pde_residual_fn   │           │
│  │ +solve()        │   │ +solve()           │           │
│  │ +train()        │   │ +train()           │           │
│  │ +evaluate()     │   │ +evaluate()        │           │
│  └─────────────────┘   └───────────────────┘           │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │BackendRegistry                                  │   │
│  │ -_registry: dict[str, PINNSolver]               │   │
│  │ +register(name, solver)                         │   │
│  │ +get(name) : PINNSolver                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │PDEProblem (dataclass)                           │   │
│  │ problem_type: str        # "kelvin-helmholtz"   │   │
│  │ domain: Domain           # geometry bounds      │   │
│  │ boundary_conditions: list[BC]                   │   │
│  │ initial_conditions: list[IC]                    │   │
│  │ pde_params: dict         # Re, rho1, rho2, ...  │   │
│  │ collocation_points: int                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │SolutionField (dataclass)                        │   │
│  │ run_id: UUID                                    │   │
│  │ backend: str                                    │   │
│  │ u_velocity: np.ndarray  # shape (N, Nt)         │   │
│  │ v_velocity: np.ndarray                          │   │
│  │ pressure: np.ndarray                            │   │
│  │ vorticity: np.ndarray                           │   │
│  │ t_snapshots: list[float]                        │   │
│  │ residuals: dict[str, float]  # PDE + BC losses  │   │
│  │ training_time_s: float                          │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

---

## 5. UML — Sequence Diagram: PINN Solve Request

```
 React F/E          PINNService         BackendRegistry    DeepXDE/JAX      PostgreSQL       MongoDB
    │                    │                     │               │                │                │
    │ POST /v1/pinn/solve│                     │               │                │                │
    │ {problem, backend} │                     │               │                │                │
    │───────────────────►│                     │               │                │                │
    │                    │ validate(PDEProblem) │               │                │                │
    │                    │──────────────────── ►│               │                │                │
    │                    │ solver = get(backend)│               │                │                │
    │                    │◄─────────────────────│               │                │                │
    │                    │                     │               │                │                │
    │                    │ INSERT pinn_runs     │               │                │                │
    │                    │────────────────────────────────────────────────────►│                │
    │                    │ run_id              │               │                │                │
    │                    │◄────────────────────────────────────────────────────│                │
    │                    │                     │               │                │                │
    │ 202 {run_id}       │                     │               │                │                │
    │◄───────────────────│                     │               │                │                │
    │                    │                     │               │                │                │
    │                    │ solver.train(config)│               │                │                │
    │                    │───────────────────────────────────►│                │                │
    │                    │    [epoch loop]     │               │                │                │
    │                    │    emit metrics     │───────────────────────────────────────────────►│
    │                    │    (pinn_metrics)   │               │                │               │
    │                    │                     │               │                │                │
    │                    │◄─── TrainedModel ───────────────────│                │                │
    │                    │ solver.evaluate(model, domain_pts)  │                │                │
    │                    │────────────────────────────────────►│                │                │
    │                    │◄─── SolutionField ──────────────────│                │                │
    │                    │                     │               │                │                │
    │                    │ UPDATE pinn_runs + INSERT pinn_solutions              │                │
    │                    │────────────────────────────────────────────────────►│                │
    │                    │                     │               │                │                │
    │ GET /v1/pinn/results/{run_id}            │               │                │                │
    │───────────────────►│                     │               │                │                │
    │◄─── SolutionField ─│                     │               │                │                │
```

---

## 6. REST API Interface Contract

**Base URL:** `http://localhost:8600`

### 6.1 Submit solve request
```
POST /v1/pinn/solve
Content-Type: application/json

{
  "problem_type": "kelvin-helmholtz",
  "backend": "deepxde" | "jax" | "auto",
  "domain": {
    "x": [0.0, 1.0],
    "y": [0.0, 0.5],
    "t": [0.0, 2.0]
  },
  "pde_params": {
    "reynolds_number": 1000,
    "density_ratio": 1.0,
    "velocity_shear": 1.0,
    "perturbation_amplitude": 0.01
  },
  "training_config": {
    "epochs": 5000,
    "learning_rate": 1e-3,
    "collocation_points": 10000,
    "boundary_points": 200,
    "initial_points": 500,
    "optimizer": "adam",
    "scheduler": "exponential_decay"
  }
}
```

**Response: 202 Accepted**
```json
{
  "run_id": "uuid",
  "status": "training",
  "backend": "deepxde",
  "estimated_duration_s": 120,
  "poll_url": "/v1/pinn/results/uuid"
}
```

### 6.2 Poll results
```
GET /v1/pinn/results/{run_id}

Response: 200 OK
{
  "run_id": "uuid",
  "status": "complete" | "training" | "failed",
  "backend": "deepxde",
  "training_time_s": 87.4,
  "residuals": {
    "pde_loss": 1.2e-4,
    "bc_loss": 3.1e-5,
    "ic_loss": 8.7e-5,
    "total_loss": 2.0e-4
  },
  "solution": {
    "t_snapshots": [0.0, 0.5, 1.0, 1.5, 2.0],
    "grid_shape": [128, 64],
    "u_velocity": [...],
    "v_velocity": [...],
    "vorticity": [...]
  }
}
```

### 6.3 Enumerate available backends
```
GET /v1/pinn/backends
Response: { "backends": ["deepxde", "jax"], "default": "deepxde" }
```

### 6.4 Health
```
GET /v1/pinn/health
Response: { "status": "ok", "backends": { "deepxde": "ready", "jax": "ready" } }
```

---

## 7. Database Schema

### 7.1 PostgreSQL — `vibedev` database

```sql
-- Run metadata and status tracking
CREATE TABLE pinn_runs (
    run_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_type    VARCHAR(64) NOT NULL,
    backend         VARCHAR(32) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'pending',  -- pending|training|complete|failed
    pde_params      JSONB,
    training_config JSONB,
    pde_loss        DOUBLE PRECISION,
    bc_loss         DOUBLE PRECISION,
    ic_loss         DOUBLE PRECISION,
    total_loss      DOUBLE PRECISION,
    training_time_s DOUBLE PRECISION,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Solution field snapshots (chunked per time snapshot)
CREATE TABLE pinn_solutions (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID REFERENCES pinn_runs(run_id) ON DELETE CASCADE,
    t_snapshot      DOUBLE PRECISION NOT NULL,
    grid_shape      INTEGER[],
    u_velocity      DOUBLE PRECISION[],  -- flattened, row-major
    v_velocity      DOUBLE PRECISION[],
    pressure        DOUBLE PRECISION[],
    vorticity       DOUBLE PRECISION[],
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_pinn_solutions_run_id ON pinn_solutions(run_id);
CREATE INDEX idx_pinn_runs_status ON pinn_runs(status, created_at DESC);
CREATE INDEX idx_pinn_runs_backend ON pinn_runs(backend, created_at DESC);
```

### 7.2 MongoDB — `vibedev.pinn_metrics`

Per-epoch training telemetry (high write rate, schema-flexible):

```json
{
  "_id": "ObjectId",
  "run_id": "uuid",
  "epoch": 1250,
  "backend": "deepxde",
  "losses": {
    "pde": 4.2e-3,
    "bc": 1.1e-3,
    "ic": 2.8e-3,
    "total": 8.1e-3
  },
  "learning_rate": 8.7e-4,
  "elapsed_s": 24.3,
  "timestamp": "ISODate"
}
```

**Indexes:**
```js
db.pinn_metrics.createIndex({ run_id: 1, epoch: 1 })
db.pinn_metrics.createIndex({ timestamp: 1 }, { expireAfterSeconds: 2592000 })  // 30-day TTL
```

---

## 8. Data Flow — Information Structure

```
PDEProblem (input)
    │
    ├── problem_type        → selects PDE kernel (KH / Navier-Stokes / ...)
    ├── domain              → geometry: x/y/t bounds
    ├── boundary_conditions → Dirichlet / Neumann / periodic
    ├── initial_conditions  → velocity/pressure field at t=0
    └── pde_params          → Re, ρ1/ρ2, shear velocity, perturbation
         │
         ▼
    Backend (DeepXDE or JAX)
         │
         ├── Collocation points (sampled from domain)
         ├── PDE residual loss  L_pde = ||N[u]||² over interior points
         ├── BC loss            L_bc  = ||u - g||² on boundary
         ├── IC loss            L_ic  = ||u(x,0) - u₀||²
         └── Total loss         L = λ₁L_pde + λ₂L_bc + λ₃L_ic
              │
              ▼
    TrainedModel
         │
         ├── DeepXDE path  → SavedModel → (optional) TF Serving
         └── JAX path      → JIT-compiled eval_fn (closure over params)
              │
              ▼
    SolutionField (output)
         ├── u, v, p, ω on evaluation grid
         ├── residuals per loss term
         └── training telemetry → MongoDB pinn_metrics
              │
              ▼
    PostgreSQL pinn_runs / pinn_solutions
         │
         ▼
    REST response → React F/E (visualisation canvas)
```

---

## 9. Integration with Platform Ecosystem

| Ecosystem Component | Integration | Notes |
|--------------------|-------------|-------|
| **kh-sim React F/E** | REST `POST /v1/pinn/solve`, `GET /v1/pinn/results/{id}` | Visualisation canvas renders vorticity field + loss curves |
| **kh-sim backends** (Rust/Scala/C++) | Optional: co-solve — classical solver result vs PINN result comparison endpoint | Future phase |
| **TF Serving** (ML-ARCHITECTURE.md) | DeepXDE(TF backend) → SavedModel export → TF Serving inference (port 8501) | Pure inference after training; training always via PINNService |
| **PostgreSQL (vibedev)** | `pinn_runs`, `pinn_solutions` tables | Managed by DB-001 infra |
| **MongoDB (vibedev)** | `pinn_metrics` collection (high-frequency training telemetry) | Log-infra log-connector-python also writes to `logs` collection |
| **log-infra** | log-connector-python → MongoDB `logs` + Elasticsearch CI/test events | Training errors, service health events |
| **CI/CD (ci-heartbeat.yml)** | `pinn-smoke-test` job: spin PINNService, submit minimal solve, assert loss < threshold | Both backends tested |
| **OAuth2 (future)** | `/v1/pinn/*` endpoints behind OIDC middleware (MI-M-T multi-tenant scope) | AUTH-001 ADR will address |
| **Docker** | PINNService containerised; `infra/docker/pinn-service/docker-compose.yml` | Both backends in single image via optional dependency groups |

---

## 10. Directory Structure

```
VibeCodeProjects/
├── infra/
│   ├── PINN-ARCHITECTURE.md         ← this document
│   ├── ML-ARCHITECTURE.md           ← TF Serving / general ML
│   ├── LOG-ARCHITECTURE.md          ← log stack
│   └── docker/
│       └── pinn-service/
│           ├── docker-compose.yml
│           └── Dockerfile
├── ml/
│   ├── pinn/
│   │   ├── __init__.py
│   │   ├── solver_interface.py      ← PINNSolver Protocol + PDEProblem + SolutionField
│   │   ├── registry.py              ← BackendRegistry
│   │   ├── backends/
│   │   │   ├── deepxde_backend.py   ← DeepXDEBackend : PINNSolver
│   │   │   └── jax_backend.py       ← JAXEquinoxBackend : PINNSolver
│   │   ├── problems/
│   │   │   ├── kelvin_helmholtz.py  ← KH PDE definition for both backends
│   │   │   └── navier_stokes.py     ← Generalised NS (future)
│   │   ├── service/
│   │   │   ├── main.py              ← FastAPI app (port 8600)
│   │   │   ├── routes.py            ← /v1/pinn/* endpoints
│   │   │   └── persistence.py       ← PG + MongoDB write helpers
│   │   ├── requirements-deepxde.txt ← deepxde[tensorflow] or deepxde[jax]
│   │   ├── requirements-jax.txt     ← jax, equinox, optax, flax
│   │   └── tests/
│   │       ├── test_interface.py    ← Protocol compliance for both backends
│   │       ├── test_kh_deepxde.py   ← KH solve smoke test (DeepXDE)
│   │       └── test_kh_jax.py       ← KH solve smoke test (JAX)
│   ├── models/                      ← Git LFS (TF Serving models)
│   ├── training/
│   └── validation/
```

---

## 11. CI/CD — PINN Smoke Test Job

```yaml
# Addition to .github/workflows/ci-heartbeat.yml

pinn-smoke-test:
  name: PINN Smoke Test (DeepXDE + JAX)
  runs-on: ubuntu-latest
  needs: [postgres-check, mongodb-check]
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: "3.11" }

    - name: Install DeepXDE backend
      run: pip install -r ml/pinn/requirements-deepxde.txt

    - name: Install JAX backend
      run: pip install -r ml/pinn/requirements-jax.txt

    - name: Run interface compliance tests
      run: pytest ml/pinn/tests/test_interface.py -v

    - name: DeepXDE smoke solve (100 epochs, minimal domain)
      run: pytest ml/pinn/tests/test_kh_deepxde.py -v -k "smoke"

    - name: JAX smoke solve (100 epochs, minimal domain)
      run: pytest ml/pinn/tests/test_kh_jax.py -v -k "smoke"

    - name: Upload loss curves as CI artifact
      uses: actions/upload-artifact@v4
      with:
        name: pinn-loss-curves-${{ github.run_number }}
        path: ml/pinn/tests/outputs/
```

---

## 12. Resource Requirements

| Component | RAM | Disk | GPU |
|-----------|-----|------|-----|
| DeepXDE (TF backend, CPU) | 2–4 GB | ~1 GB | Optional |
| DeepXDE (JAX backend, CPU) | 1–3 GB | ~500 MB | Optional |
| JAX + Equinox (CPU) | 1–2 GB | ~400 MB | Optional |
| PINNService FastAPI | 256 MB | — | No |
| **Total (both backends, no GPU)** | **3–6 GB peak** | **~2 GB** | — |

> ThinkPad (no discrete GPU): CPU training only. Smoke tests use minimal domain (100×50 grid, 100 epochs) to keep CI runtime < 5 min.
> GPU path: JAX detects CUDA automatically; DeepXDE inherits from backend (TF or JAX).

---

## 13. Implementation Task Map

See `TASKS-shared.yaml` project `ml-infra` — tasks PINN-001 through PINN-009.

| Task ID | Title | Depends on |
|---------|-------|-----------|
| PINN-001 | PINN architecture design + ADR (this document) | — |
| PINN-002 | PINNSolver interface + PDEProblem / SolutionField data models | PINN-001 |
| PINN-003 | BackendRegistry + FastAPI service scaffold (port 8600) | PINN-002 |
| PINN-004 | KH PDE definition — shared problem kernel | PINN-002 |
| PINN-005 | DeepXDE backend implementation (KH/NS, TF backend) | PINN-003, PINN-004 |
| PINN-006 | JAX + Equinox backend implementation (KH/NS) | PINN-003, PINN-004 |
| PINN-007 | PostgreSQL schema migration (pinn_runs, pinn_solutions) | DB-001, PINN-002 |
| PINN-008 | MongoDB pinn_metrics collection + TTL index | DB-002, PINN-002 |
| PINN-009 | CI pinn-smoke-test job (both backends, loss threshold assertions) | PINN-005, PINN-006, GEN-010 |
