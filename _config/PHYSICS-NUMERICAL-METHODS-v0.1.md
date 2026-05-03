# Physics Numerical Methods — v0.1
## State-of-the-art numerical methods + Fortran reference + 4-port parallel impl + multi-protocol microservice interfaces

**Version:** v0.1.0
**Authority:** Companion to `3-fold-path/backlog/PHYSICS-CALIBRATION-MODELS-v0.1.md` (the 3 models + calibration tests).
**This doc adds:** the *numerical methods* layer (which algorithm, why, citations, test cases for numerical correctness as distinct from physics-model correctness), the *Fortran reference watermark* implementation plan (file-level), the *parallel-port spec* for Rust + Scala + Pascal + C (Pascal/C gated by validation), and the *4-channel microservice surface* per implementation (REST + gRPC + WebSocket streaming + file-dump fallback).
**Audience:** ThinkPad Sonnet sessions implementing Track PHYS + new Track NUM (numerical layer + microservices); MacBook Sonnet implementing the graphical frontend per `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md`.

---

## §0. Reading order

1. `_config/OPUS-CYCLE-v0.2-MASTER.md` (strategic frame, with v0.2.1 amendment box)
2. `_config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` (Stages, parallel topologies)
3. `3-fold-path/backlog/PHYSICS-CALIBRATION-MODELS-v0.1.md` (the 3 models, calibration test catalogue)
4. **This document** (numerical methods + Fortran reference + ports + microservice protocols)
5. `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` (frontend visualisation design system)

---

## §1. Cross-cutting decisions

### 1.1 Implementation language ordering (locked)

**Fortran first as the watermark reference; then all 4 ports (Rust, Scala, Pascal, C) in parallel.** Pascal + C are conditional — they ship only if their precision/stability validates against Fortran within tolerance for non-linear regions.

| Language | Role | Compiler / runtime | Validation gate to ship |
|----------|------|--------------------|-------------------------|
| **Fortran** | **Reference watermark** | gfortran 13+ (Topology A), Intel `ifx` optional (Topology A) | All §2/§3/§4 numerical-method test cases pass |
| **Rust** | Port (mandatory) | rustc 1.74+ | Outputs match Fortran within tolerance per §1.5 |
| **Scala** | Port (mandatory) | Scala 3.4+ on JDK 21 | Outputs match Fortran within tolerance per §1.5 |
| **Pascal** | Port (conditional) | Free Pascal 3.2.2+ | **Must demonstrate** stable handling of non-linear advection AND its data-structure overhead is < 2× Fortran wall-clock |
| **C** | Port (conditional) | gcc 13+ or clang 17+ | **Must demonstrate** same as Pascal |

Pascal and C are kept as pedagogical / portability proofs. If they fail the gate they remain "draft" without a v0.2 release — that decision is documented + bounce-back trigger TRG-NEW1 (§9 below).

### 1.2 Microservice protocol stack (locked)

Each language implementation exposes the **same** four-channel surface:

| Channel | Purpose | Default port |
|---------|---------|--------------|
| **REST** | Casual users + control plane (start run, fetch result, list runs); JSON request/response | 8081 (KH), 8082 (GR), 8083 (Ising) |
| **gRPC** | High-throughput numerical streaming (large arrays, protocol buffers, bidirectional) | 9081 / 9082 / 9083 |
| **WebSocket** | Live progress + interim solution snapshots for the graphical frontend | (same port as REST, path `/ws/run/{id}`) |
| **File-dump** | Fallback / testing / load test — write NetCDF or HDF5 to a known path; return path in REST response | filesystem path `/results/<run_id>/` |

The four channels share **one** core solver — a thin protocol layer wraps the same compiled object/library. No re-implementation per channel.

### 1.3 Watermark contract (Fortran as canonical)

For every numerical kernel:
- Fortran emits a **canonical reference output JSON** (or NetCDF for large arrays) with deterministic seeds.
- Each ported implementation runs the same recipe and is required to match within tolerance in §1.5.
- The Fortran source carries a code-level watermark comment block at module top: `! REFERENCE WATERMARK — kh-sim Fortran reference, vN.M; canonical for: <test cases>; do not modify without bumping reference version + regenerating reference outputs.`

### 1.4 Build + run topology (per language)

Each implementation lives in its own subtree of the relevant package and is independently buildable. Discovery + invocation is uniform via `Makefile` targets.

```
kh-sim/                          (existing)
├── shared/
│   ├── physics/ (existing, KH-PHYSICS.md + reference outputs)
│   ├── api/openapi.yaml         (extended for KH REST contract)
│   ├── proto/khsim.proto        (NEW — gRPC contract)
│   └── frontend/                (NEW — graphical components)
└── backends/
    ├── fortran/  (existing — REFERENCE; expand per §2.4)
    ├── rust/     (existing — port; expand per §2.5)
    ├── scala/    (existing — port; expand per §2.6)
    ├── cpp/      (existing — gated as "C" per §1.1)
    └── pascal/   (existing — gated)

3-fold-path/code/physics-gr/     (NEW per PHYSICS-CALIBRATION §3.5)
├── shared/
│   ├── api/openapi.yaml
│   ├── proto/grsim.proto
│   └── frontend/
└── backends/
    ├── fortran/  (NEW — REFERENCE)
    ├── rust/     (NEW)
    ├── scala/    (NEW)
    ├── cpp/      (gated)
    └── pascal/   (gated)

3-fold-path/code/physics-ising/  (NEW per PHYSICS-CALIBRATION §4.5)
├── shared/
│   ├── api/openapi.yaml
│   ├── proto/ising.proto
│   └── frontend/
└── backends/
    ├── fortran/  (NEW — REFERENCE)
    ├── rust/     (NEW)
    ├── scala/    (NEW)
    ├── cpp/      (gated)
    └── pascal/   (gated)
```

### 1.5 Cross-implementation tolerance ladder

Tolerances against Fortran reference output, per quantity:

| Quantity class | Tolerance (relative) | Why |
|----------------|---------------------:|-----|
| Linear-stage numerics (FFTs, matrix solves) | 1e-12 | machine-precision agreement expected |
| Time-integrated nonlinear quantities (e.g. ω at t = T) | 1e-6 | rounding accumulation |
| Statistical observables (Ising MC averages) | 1 σ of MC estimator | statistical noise |
| Integer / discrete quantities (Petrov classification, peak count) | bit-exact | no tolerance |
| Wall-clock | informational only; not a gate | language perf differs |

---

## §2. Model A — Kelvin-Helmholtz (CFD)

### 2.1 State-of-the-art numerical method (locked)

**Pseudo-spectral with FFT for spatial derivatives + 4th-order exponential time differencing Runge-Kutta (ETDRK4) for time integration**, with 2/3-rule de-aliasing.

Why this stack:
- Doubly periodic domain ⇒ spectral methods are *natural* (FFT diagonalises the Laplacian; spectral accuracy ⇒ exponential convergence in N for smooth fields).
- ETDRK4 (Cox & Matthews 2002, JCP 176:430; Kassam & Trefethen 2005, SIAM J. Sci. Comput. 26:1214) handles the stiff diffusion term *exactly* (no CFL on viscosity) while integrating the nonlinear advection term explicitly.
- 2/3-rule de-aliasing (Orszag 1971) prevents spurious aliasing from the quadratic nonlinearity (`u·∇ω`) and is the de-facto standard for spectral CFD.
- Stable for moderate Re (we target Re ~ 1000 – 10⁴ in canonical KH).

**References (citation block to embed in Fortran source):**
- Cox, S. M., & Matthews, P. C. (2002). *Exponential time differencing for stiff systems*. JCP 176:430–455.
- Kassam, A.-K., & Trefethen, L. N. (2005). *Fourth-order time-stepping for stiff PDEs*. SIAM JSC 26:1214–1233.
- Orszag, S. A. (1971). *On the elimination of aliasing in finite-difference schemes by filtering high-wavenumber components*. JAS 28:1074.
- Boyd, J. P. (2001). *Chebyshev and Fourier Spectral Methods*, 2nd ed. — chapters 1–3 + 12 (de-aliasing).
- Canuto, C., Hussaini, M. Y., Quarteroni, A., & Zang, T. A. (2006). *Spectral Methods: Fundamentals in Single Domains*. Springer — chapter 5.

### 2.2 Algorithmic recipe (Fortran-ready pseudocode)

```
INPUT
   Nx, Ny       grid (powers of 2 for FFT; default 256 × 128)
   Lx, Ly       domain (default 1.0, 0.5)
   U0, delta    shear (default 1.0, 0.025)
   A, k_pert    perturbation amplitude + mode (default 0.01, 2)
   Re           Reynolds number (default 1000)
   T_end        final time (default 1.0)
   dt0          initial time step (CFL controlled below)
   seed         RNG seed (deterministic)

INIT
   nu = U0 / Re
   x[i] = i*Lx/Nx;  y[j] = j*Ly/Ny;
   omega(x,y,0) computed analytically per KH-PHYSICS §3.

TIME LOOP (ETDRK4)
   For t = 0 .. T_end:
       1. Forward FFT: omega_hat = FFT2(omega).
       2. Streamfunction Poisson: psi_hat = -omega_hat / k2  (k2[0,0] = 1 to avoid 0/0; psi_hat[0,0] = 0).
       3. Velocity recovery (in spectral): u_hat = i*ky*psi_hat;  v_hat = -i*kx*psi_hat.
       4. Nonlinear term in physical space:
              u = IFFT2(u_hat); v = IFFT2(v_hat);
              dox = IFFT2(i*kx * omega_hat); doy = IFFT2(i*ky * omega_hat);
              N = -(u*dox + v*doy);
              N_hat = FFT2(N);
              N_hat = de_alias_2_3(N_hat).
       5. ETDRK4 step on omega_hat with linear operator L(k) = -nu*(k2):
              omega_hat_new = ETDRK4_step(omega_hat, N_hat, L, dt).
       6. Adaptive dt: dt = 0.4 * min(dx, dy) / max(|u|,|v|)  (CFL); diffusion CFL is ∞ (handled exactly by ETD).
       7. Periodically: write snapshot to result file (every k snapshots; user-configurable).
   Inverse FFT for final omega.

OUTPUT
   omega(x,y,t)        snapshots
   diagnostics[]       L2 norm of omega, kinetic energy, mode-2 amplitude, vortex centroid
   reference_hash      sha256 of canonical run output for cross-language verification
```

### 2.3 Numerical-method test cases (distinct from physics-model tests)

These validate the *numerical kernel* (FFT, Poisson, ETDRK4, de-aliasing) — separate from the physics-model calibration tests in PHYSICS-CALIBRATION-MODELS §2.6.

| TC ID | Test target | Method check | Pass criterion |
|-------|-------------|--------------|----------------|
| TC-NUM-KH-001 | FFT2 round-trip | `IFFT2(FFT2(field)) == field` | ‖diff‖_∞ ≤ 1e-12 for random field |
| TC-NUM-KH-002 | Spectral Poisson | Solve ∇²ψ = -ω where ω is a single Fourier mode (cos(2πk·x)); compare against analytical | rel err ≤ 1e-12 |
| TC-NUM-KH-003 | ETDRK4 on linear scalar test | dy/dt = λy, λ < 0; integrate to t = 10/|λ|; compare to e^(λt) | rel err ≤ 1e-10 |
| TC-NUM-KH-004 | ETDRK4 order verification | Halve dt repeatedly on a known-solution problem; observed convergence rate ≥ 3.9 (target 4) | order ≥ 3.9 over 5 dt halvings |
| TC-NUM-KH-005 | De-aliasing 2/3 rule | Fourier mode at k > 2N/3; should be zeroed | post-filter amplitude ≤ 1e-15 |
| TC-NUM-KH-006 | CFL control | Run with Re = 100, 1000, 10000; no CFL violation should crash | all 3 Re values run to T_end |
| TC-NUM-KH-007 | Energy conservation (inviscid limit) | Set Re = ∞ (nu = 0); run to T = 0.5; KE drift ≤ 1e-3 | drift ≤ 1e-3 (no perfect conservation due to de-aliasing) |
| TC-NUM-KH-008 | Reference output match | Run canonical recipe; sha256 of output matches `kh_reference_output.json` reference hash | hash match |

### 2.4 Fortran reference implementation plan (file-level, ready for Sonnet)

```
kh-sim/backends/fortran/
├── Makefile                       (build: gfortran -O3 -fopenmp; targets: build/test/bench/serve)
├── src/
│   ├── kh_constants.f90           — module: physical & numerical constants (KH-PHYSICS §3 defaults)
│   ├── kh_grid.f90                — module: grid coords, wavenumber arrays kx/ky/k2
│   ├── kh_fft.f90                 — module: forward/inverse 2D FFT wrappers (FFTW3 or fftpack5)
│   ├── kh_poisson.f90             — module: spectral Poisson solver (psi_hat = -omega_hat/k2)
│   ├── kh_velocity.f90            — module: spectral velocity recovery (u_hat, v_hat from psi_hat)
│   ├── kh_nonlinear.f90           — module: nonlinear term assembly + 2/3 de-aliasing
│   ├── kh_etdrk4.f90              — module: ETDRK4 time integrator (Cox-Matthews + Kassam-Trefethen)
│   ├── kh_diagnostics.f90         — module: L2 norm, KE, mode-2 amplitude, vortex centroid
│   ├── kh_io.f90                  — module: read params, write JSON / NetCDF snapshots
│   ├── kh_reference.f90           — module: REFERENCE WATERMARK; sha256 of canonical run; reference recipe
│   ├── kh_solver.f90              — module: top-level solver loop (orchestrates the above)
│   └── kh_main.f90                — program: CLI entry point (kh_main --recipe canonical --out reference.nc)
├── service/
│   ├── kh_rest.f90                — REST server (use json-fortran + fortran-http or call C bindings to a thin Rust/Go HTTP wrapper)
│   ├── kh_grpc.f90                — gRPC server (gRPC C bindings via ISO_C_BINDING)
│   ├── kh_ws.f90                  — WebSocket emitter
│   └── kh_filedump.f90            — write NetCDF/HDF5
├── tests/
│   ├── test_num_001_fft_roundtrip.f90    (TC-NUM-KH-001)
│   ├── test_num_002_poisson.f90          (TC-NUM-KH-002)
│   ├── test_num_003_etdrk4_linear.f90    (TC-NUM-KH-003)
│   ├── test_num_004_etdrk4_order.f90     (TC-NUM-KH-004)
│   ├── test_num_005_dealias.f90          (TC-NUM-KH-005)
│   ├── test_num_006_cfl.f90              (TC-NUM-KH-006)
│   ├── test_num_007_energy.f90           (TC-NUM-KH-007)
│   ├── test_num_008_reference_hash.f90   (TC-NUM-KH-008)
│   └── test_runner.f90                   (drives all tests; exit code = failure count)
└── ref/
    ├── kh_reference_output.nc          (canonical output, NetCDF; binary)
    ├── kh_reference_output.json        (small-case canonical; JSON; cross-language hash anchor)
    └── kh_reference_recipe.toml        (input parameters that produced the reference)
```

**Sonnet step-by-step implementation order (NUM-KH-FOR-01..09):**
1. **NUM-KH-FOR-01** — Constants + grid + FFT wrappers (`kh_constants.f90`, `kh_grid.f90`, `kh_fft.f90`); test TC-NUM-KH-001 green.
2. **NUM-KH-FOR-02** — Poisson + velocity (`kh_poisson.f90`, `kh_velocity.f90`); TC-NUM-KH-002 green.
3. **NUM-KH-FOR-03** — Nonlinear + de-alias (`kh_nonlinear.f90`); TC-NUM-KH-005 green.
4. **NUM-KH-FOR-04** — ETDRK4 (`kh_etdrk4.f90`); TC-NUM-KH-003 + TC-NUM-KH-004 green.
5. **NUM-KH-FOR-05** — Diagnostics + IO (`kh_diagnostics.f90`, `kh_io.f90`).
6. **NUM-KH-FOR-06** — Solver loop + main (`kh_solver.f90`, `kh_main.f90`); TC-NUM-KH-006 + TC-NUM-KH-007 green.
7. **NUM-KH-FOR-07** — Generate reference output (`kh_reference.f90`); TC-NUM-KH-008 green; commit `ref/*` artefacts.
8. **NUM-KH-FOR-08** — REST + file-dump services (`service/kh_rest.f90`, `service/kh_filedump.f90`); curl /run smoke test.
9. **NUM-KH-FOR-09** — gRPC + WebSocket services (`service/kh_grpc.f90`, `service/kh_ws.f90`); end-to-end client smoke.

Parallel ports (Rust / Scala / Pascal / C) start once NUM-KH-FOR-07 closes (reference is canonical). They reuse the same `ref/*` and the same numerical-test-case set; same step ordering.

### 2.5 Rust port spec (NUM-KH-RUST-01..09)

Crates: `ndarray`, `rustfft`, `serde`, `serde_json`, `axum` (REST), `tonic` (gRPC), `tokio-tungstenite` (WebSocket), `netcdf` or `hdf5-rust` (file dump).

Module structure mirrors Fortran 1:1:
```
backends/rust/src/
├── constants.rs
├── grid.rs
├── fft.rs                  (rustfft 2D wrapper)
├── poisson.rs
├── velocity.rs
├── nonlinear.rs
├── etdrk4.rs
├── diagnostics.rs
├── io.rs
├── reference.rs
├── solver.rs
└── bin/
    ├── kh_main.rs
    ├── kh_rest.rs          (axum)
    ├── kh_grpc.rs          (tonic)
    └── kh_ws.rs            (tungstenite)
```

Numerical test suite identical to Fortran (TC-NUM-KH-001..008); shared expected outputs in `kh-sim/shared/physics/test_expectations.json`.

### 2.6 Scala port spec (NUM-KH-SCALA-01..09)

Scala 3.4 on JDK 21. Libraries: `breeze` (linear algebra), `spire` (numerics), `cats-effect` (effects), `http4s` (REST), `fs2-grpc` (gRPC), `http4s` WebSocket.

Module structure:
```
backends/scala/src/main/scala/khsim/
├── constants.scala
├── grid.scala
├── fft/Fft2D.scala         (existing — extend for ETDRK4)
├── poisson.scala
├── velocity.scala
├── nonlinear.scala
├── etdrk4.scala
├── diagnostics.scala
├── io.scala
├── reference.scala
├── solver.scala
└── service/
    ├── KhMain.scala
    ├── KhRest.scala        (http4s)
    ├── KhGrpc.scala        (fs2-grpc)
    └── KhWs.scala
```

### 2.7 Pascal & C ports — gated (NUM-KH-PASCAL-* / NUM-KH-CGCC-*)

**Validation gate**: before declaring either port shippable in v0.2, the implementation must:
1. Pass TC-NUM-KH-001..008.
2. Output match Fortran reference to 1e-6 (per §1.5 row 2).
3. Demonstrate stable handling of Re = 10⁴ for the full T_end without numerical blow-up.
4. Wall-clock < 2 × Fortran on the canonical recipe.

If gate fails → mark as "draft / not released in v0.2"; surface as NUM-* OQ; defer to v0.3.

C uses GSL FFT (`gsl_fft_complex_*`) or FFTW3 directly. Pascal uses Free Pascal + a Pascal FFT port (e.g. `tpipfft` or wrap FFTW3 via cdecl).

---

## §3. Model B — General Relativity (symbolic)

### 3.1 State-of-the-art numerical method (locked)

**Symbolic-only computation; no floating-point.** Stack:
- **Fortran** for the reference is *unusual* for symbolic work. We **adapt the rule**: the canonical reference for GR is the **SymPy Python kernel** (per PHYSICS-CALIBRATION §3.3); each language port wraps that kernel via FFI **OR** re-implements the symbolic algebra natively.

| Language | Strategy |
|----------|----------|
| Python (canonical) | SymPy native; this is the watermark for GR (overrides §1.3 "Fortran first" rule for this model only) |
| Rust | Use `symbolica` crate (Rust CAS, 2023+) OR FFI to SymPy |
| Scala | Use `breeze.math` for tensor arithmetic + custom symbolic layer; OR FFI to SymPy via `jep` |
| Fortran | Numerical-only fallback: evaluate Christoffel/Riemann at sample (r, θ) points and confirm against SymPy at the same points (1e-12 agreement) |
| C, Pascal | Same numerical-only fallback as Fortran; conditional |

**References:**
- Stephani, H. et al. (2003). *Exact Solutions of Einstein's Field Equations*, 2nd ed. — Petrov classification algorithm §4.2.
- Chinea, F. J., González-Romero, L. M. (1992). *A note on the symbolic computation of curvature tensors*. CMA 50:215.
- The `symbolica` Rust crate documentation (Ben Ruijl, 2023+).
- Podolský, J., & Griffith, J. B. (2009). *Exact Space-Times in Einstein's General Relativity*, CUP — chapters 3 / 9 / 13.

### 3.2 Algorithmic recipe

For each metric (Minkowski / Schwarzschild / Kerr):
```
INPUT:  metric tensor g_{μν} as symbolic matrix in chart coordinates;
        coordinates list (t, r, θ, φ) as symbolic variables;
        physical parameters (M, a) as symbolic positive reals.

COMPUTE (symbolic):
  1. g^{μν} = g.inv()                                     (matrix inverse)
  2. Γ^a_{bc} = ½ g^{ad}(∂_b g_{dc} + ∂_c g_{db} - ∂_d g_{bc})
  3. R^a_{bcd} = ∂_c Γ^a_{bd} - ∂_d Γ^a_{bc} + Γ^a_{ce}Γ^e_{bd} - Γ^a_{de}Γ^e_{bc}
  4. R_{ab} = R^c_{acb}
  5. R = g^{ab} R_{ab}
  6. C_{abcd} = R_{abcd} - (g_{a[c} R_{d]b} - g_{b[c} R_{d]a}) + (1/3) R g_{a[c} g_{d]b}
  7. Petrov classification: solve eigenvalue equation for Weyl tensor on null tetrad; classify per §4.2 of Stephani et al.
  8. Newman-Penrose Ψ_n: compute on the chosen null tetrad (Kinnersley for Kerr, standard for Schwarzschild).

VALIDATE:
  - Vacuum check: simplify(R_{ab}) must be 0.
  - Kretschmann K = R_{abcd} R^{abcd}: simplify and compare against P&G value.
  - Petrov type: compare against table.
```

### 3.3 Numerical-method test cases

| TC ID | Test target | Method check | Pass criterion |
|-------|-------------|--------------|----------------|
| TC-NUM-GR-001 | Matrix inverse | g · g^{-1} = I | symbolic equality |
| TC-NUM-GR-002 | Symbolic differentiation | ∂_r (1 - 2M/r) = 2M/r² | symbolic equality |
| TC-NUM-GR-003 | Tensor index contraction | g^{μν} g_{νρ} = δ^μ_ρ | symbolic identity |
| TC-NUM-GR-004 | Riemann symmetries | R_{abcd} = -R_{bacd} = -R_{abdc} = R_{cdab} | symbolic equality (sample components) |
| TC-NUM-GR-005 | Bianchi identity (algebraic) | R_{a[bcd]} = 0 | symbolic 0 |
| TC-NUM-GR-006 | Bianchi identity (differential, on Schwarzschild) | ∇_e R_{abcd} + cyclic = 0 | symbolic 0 (sample) |
| TC-NUM-GR-007 | Numerical evaluation match (Fortran/C/Pascal ports) | Eval Γ^t_{tr} for Schwarzschild at (M=1, r=10) → 0.001/(1 - 0.2) = 0.00125; Fortran port output | rel err ≤ 1e-12 |

### 3.4 Implementation plans (by language)

**Python / SymPy (NUM-GR-PY-01..05, the canonical):** see PHYSICS-CALIBRATION §3.5 — already detailed. Output `pgr/calibration/ref_*.py` is the watermark.

**Rust (NUM-GR-RUST-01..05):**
- Crate: `symbolica` (modern Rust CAS).
- Module structure mirrors `pgr/`:
  - `pgr_rs/src/metrics/{minkowski.rs, schwarzschild.rs, kerr.rs}` — metric matrix builders.
  - `pgr_rs/src/tensors.rs` — christoffel/riemann/ricci/weyl using symbolica.
  - `pgr_rs/src/petrov.rs` — Petrov classification.
  - `pgr_rs/src/main.rs` — CLI.
  - `pgr_rs/src/service/` — REST/gRPC/WS endpoints (output is symbolic expression as LaTeX or human-readable string).
- Validation gate: same TCs; result must match SymPy's symbolic output (string-equality after canonicalisation OR algebraic-difference reduction to 0).

**Scala (NUM-GR-SCALA-01..05):** options:
- Option A (preferred): use `jep` (Java Embedded Python) to call SymPy from Scala; thin wrapper.
- Option B (independent): build minimal symbolic algebra in Scala using ADTs (Sym, Add, Mul, Pow, Diff, ...); much more work; only if Option A fails on portability.

**Fortran / C / Pascal (NUM-GR-FOR-01..03 / -CGCC / -PASCAL):** numerical-only fallback. Build a small evaluator that:
- Receives a metric tensor + chart point as input.
- Computes Christoffel/Riemann at that point as floating-point arrays.
- Returns the array; cross-validate against SymPy evaluated at the same point.

This means Fortran's role for GR is **not** the symbolic watermark (SymPy is) but a **point-wise numerical cross-check** that the symbolic results, when evaluated at floating-point points, agree with a fast compiled evaluator.

### 3.5 Microservice surface for GR

REST: `POST /run/metric/<name>` returns the symbolic Christoffel/Riemann/etc. as JSON-of-strings (LaTeX or pretty-printed sympy).
gRPC: same as REST but protobuf with `repeated string` for tensor components.
WebSocket: streams progress (e.g. "computing Riemann components 1/256... 256/256").
File dump: writes a structured directory with one file per tensor:
```
/results/gr/<run_id>/
├── recipe.toml               (input metric + chart)
├── christoffel/
│   ├── G_t_tr.txt            (symbolic expression, pretty-printed)
│   └── ...
├── riemann/
├── ricci/
├── weyl/
└── petrov.txt                (single line: 'D' or 'I' or ...)
```

---

## §4. Model C — 2D Ising (classical + quantum)

### 4.1 State-of-the-art numerical methods (locked)

**Classical 2D Ising:**
- **Wolff cluster algorithm** (Wolff 1989, PRL 62:361) as the reference — eliminates critical slowing down near T_c; the modern standard for accurate critical-temperature estimation.
- **Metropolis** retained as the simplest pedagogical reference (TC-NUM-IS-001..002).
- **Wang-Landau** algorithm (Wang & Landau 2001, PRL 86:2050) for density-of-states / specific-heat (optional; gated).

**Quantum 2D TFIM:**
- **Stochastic Series Expansion (SSE) QMC** (Sandvik 2010, AIP 1297:135; lecture notes) — sign-problem-free for TFIM; the modern standard for 2D large-L.
- **Exact Diagonalization (ED)** for L ≤ 4 — uses Lanczos via `scipy.sparse.linalg.eigsh` (Python) / `arpack` bindings (Fortran/C).
- **DMRG / MPS** (White 1992, PRL 69:2863) for 1D and quasi-2D ladders — using `quimb` or `ITensor.jl` in the canonical Python; native ports defer to v0.3.

**References:**
- Wolff, U. (1989). *Collective Monte Carlo updating for spin systems*. PRL 62:361.
- Wang, F., & Landau, D. P. (2001). *Efficient, multiple-range random walk algorithm to calculate the density of states*. PRL 86:2050.
- Sandvik, A. W. (2010). *Computational studies of quantum spin systems*. AIP Conf. Proc. 1297:135. (Open-access lecture notes.)
- White, S. R. (1992). *Density matrix formulation for quantum renormalization groups*. PRL 69:2863.
- Newman, M. E. J., & Barkema, G. T. (1999). *Monte Carlo Methods in Statistical Physics*. OUP — chapters 3–6.
- Onsager, L. (1944). *Crystal statistics. I. A two-dimensional model with an order-disorder transition*. PR 65:117.
- Pfeuty, P. (1970). *The one-dimensional Ising model with a transverse field*. Ann. Phys. 57:79.
- Blöte, H. W. J., & Deng, Y. (2002). *Cluster Monte Carlo simulation of the transverse Ising model*. PRE 66:066110.

### 4.2 Algorithmic recipes

**Wolff cluster (classical):**
```
INPUT: lattice L×L; J; T; seed
INIT: spins[L][L] random ±1; beta = 1/T; p_add = 1 - exp(-2*beta*J)
LOOP:
  pick seed site (i0, j0)
  cluster = {(i0, j0)};  spin0 = spins[i0][j0]
  stack = [(i0, j0)]
  while stack not empty:
    pop (i, j)
    for each NN (i', j'):
      if (i', j') not in cluster and spins[i'][j'] == spin0:
        if rand() < p_add:
          add (i', j') to cluster + stack
  flip every site in cluster
RECORD: M = sum(spins) / (L*L); E = -J * sum(NN pairs); update averages
```

**SSE QMC (quantum TFIM):**
- Operator-string sampling in imaginary-time series expansion; diagonal + off-diagonal updates; loop / cluster updates for ergodicity.
- Reference implementation: Sandvik 2010 §4 pseudocode (open-access).

### 4.3 Numerical-method test cases

| TC ID | Test target | Method check | Pass criterion |
|-------|-------------|--------------|----------------|
| TC-NUM-IS-001 | Metropolis detailed balance | Sample 10⁵ accepted moves; ratio test on a small lattice | within 5% of theoretical |
| TC-NUM-IS-002 | Metropolis ergodicity | All 2^(L²) configs visited for L = 4 in long enough run | coverage ≥ 99% |
| TC-NUM-IS-003 | Wolff cluster correctness | Critical exponents from Wolff converge to Onsager (β = 1/8, ν = 1) using FSS on L = 16, 32, 64 | exponents within 5% |
| TC-NUM-IS-004 | RNG quality | Seed reproducibility + Marsaglia diehard subset (chi-square, runs, gap) | all pass |
| TC-NUM-IS-005 | Lanczos convergence | Eigenvalue of L=4 TFIM Hamiltonian converges to within 1e-10 in ≤ 200 iter | converges |
| TC-NUM-IS-006 | SSE QMC sign-problem-free | All samples have positive weight | 100% positive |
| TC-NUM-IS-007 | Reference output match | Fortran SSE QMC at L=8, g=3.04438; energy/site reference | match within 1σ |

### 4.4 Implementation plan (Fortran reference + ports)

```
3-fold-path/code/physics-ising/backends/fortran/
├── Makefile
├── src/
│   ├── ising_constants.f90
│   ├── ising_lattice.f90               (2D Ising lattice + periodic NN)
│   ├── ising_rng.f90                   (Mersenne Twister or PCG)
│   ├── ising_metropolis.f90
│   ├── ising_wolff.f90                 (cluster algorithm)
│   ├── ising_observables.f90           (M, E, χ, C; FSS analysis)
│   ├── ising_quantum_lanczos.f90       (sparse Hamiltonian + Lanczos via ARPACK)
│   ├── ising_quantum_sse.f90           (SSE QMC; Sandvik 2010 §4 pseudocode)
│   ├── ising_io.f90
│   ├── ising_reference.f90             (REFERENCE WATERMARK)
│   ├── ising_solver.f90                (top-level orchestration: classical / quantum subcommand)
│   └── ising_main.f90                  (CLI)
├── service/
│   ├── ising_rest.f90
│   ├── ising_grpc.f90
│   ├── ising_ws.f90
│   └── ising_filedump.f90
├── tests/                              (TC-NUM-IS-001..007)
└── ref/
    ├── ising_classical_reference.json
    ├── ising_quantum_reference.json
    └── ising_recipes.toml
```

**Sonnet step-by-step (NUM-IS-FOR-01..09):**
1. Lattice + RNG (`ising_lattice.f90`, `ising_rng.f90`); TC-NUM-IS-004 green.
2. Metropolis (`ising_metropolis.f90`); TC-NUM-IS-001..002 green.
3. Wolff (`ising_wolff.f90`); TC-NUM-IS-003 green.
4. Observables + FSS analysis (`ising_observables.f90`).
5. Lanczos quantum (`ising_quantum_lanczos.f90`); TC-NUM-IS-005 green.
6. SSE QMC (`ising_quantum_sse.f90`); TC-NUM-IS-006..007 green.
7. IO + solver loop + main + reference.
8. REST + file-dump services.
9. gRPC + WebSocket services.

Ports follow same pattern as KH (§2.5–2.7).

---

## §5. Microservice surface — common contracts

### 5.1 REST surface (uniform across all 3 models)

```
GET  /health                           → {status, model, version, language}
GET  /reference                        → recipe + reference output hash
POST /run                              → {run_id, status: "pending"} ; body = recipe (JSON)
GET  /run/{run_id}                     → {run_id, status, progress, links: { result, ws } }
GET  /run/{run_id}/result              → result JSON (small) OR file-dump path (large)
GET  /run/{run_id}/diagnostics         → diagnostics (L2 norm, KE, vortex centroid, ...)
DELETE /run/{run_id}                   → cancel + cleanup
GET  /runs                             → list with filter ?status=&model=
```

OpenAPI 3.1 spec lives at `<package>/shared/api/openapi.yaml`. Same shape for KH / GR / Ising; only the recipe payload differs.

### 5.2 gRPC surface (`<package>/shared/proto/<model>.proto`)

```proto
syntax = "proto3";
package physics.<model>;

service <Model>Solver {
  rpc Health(HealthRequest) returns (HealthResponse);
  rpc Run(RunRequest) returns (RunResponse);              // unary control
  rpc StreamRun(RunRequest) returns (stream Snapshot);    // server streaming for progress
  rpc GetResult(GetResultRequest) returns (Result);
  rpc CancelRun(CancelRequest) returns (CancelResponse);
}
```

### 5.3 WebSocket streaming

URL: `ws://host:port/ws/run/{run_id}`. Server pushes JSON frames every k steps:
```json
{"t":0.05,"step":50,"l2_omega":1.234,"ke":0.567,"snapshot_url":"/run/abc/snapshot/50.png"}
```

Frontend (per Graphics manual) consumes this for the live visualisation.

### 5.4 File-dump fallback

Writes to `/results/<model>/<run_id>/` (or env-configurable):
- `recipe.toml` — exact input
- `result.nc` (NetCDF) or `result.h5` (HDF5) — full field data
- `diagnostics.json` — scalar diagnostics
- `snapshots/*.png` — pre-rendered preview images (optional)
- `manifest.json` — index of the above

Used for: large datasets that don't fit cleanly in REST/gRPC payloads; CI replay; load test where REST is bypassed.

---

## §6. Frontend graphical visualisation (cross-reference)

Each model gets a small graphical frontend per `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` §6 (Physics Frontend Components).

Key elements per page:
- **Recipe form**: input parameters with defaults; "Use canonical recipe" button.
- **Progress + WebSocket connection**: live updating.
- **Visualisation pane**:
  - KH: vorticity heatmap (canvas), updated as snapshots arrive.
  - GR: rendered LaTeX of tensor components; collapsible per Christoffel/Riemann/Ricci.
  - Ising: spin lattice mosaic (classical) or energy/magnetization plot (quantum).
- **Diagnostics**: live numbers; final-state download buttons (JSON / NetCDF / PNG).

The visual identity comes from zemla.org-derived design system (per Graphics manual §3).

---

## §7. Cross-language consistency + watermarking discipline

Per §1.3 + §1.5:
- Fortran is the watermark for KH + Ising (Python/SymPy is the watermark for GR — special case).
- Each port commits a validation matrix output in its `tests/` showing TC-NUM-* results + agreement with the reference within tolerance.
- The reference output file (`ref/*.nc`, `ref/*.json`) is **never** modified by a port — only by the reference language with explicit version bump.
- Sha256 of the reference output is recorded in the canonical recipe TOML; any port that produces a different hash on the canonical recipe is non-conforming and gets a NUM-* OQ.

---

## §8. Iteration plan — Track NUM (numerical layer + microservices)

| Iteration ID | Owner | Goal | Estimated effort |
|--------------|-------|------|-------------------|
| **NUM-KH-FOR-01..09** | ThinkPad | Fortran reference for KH (per §2.4) | 5 sessions |
| **NUM-KH-RUST-01..09** | ThinkPad | Rust port for KH (parallel after FOR-07) | 4 sessions |
| **NUM-KH-SCALA-01..09** | ThinkPad | Scala port for KH (parallel) | 4 sessions |
| **NUM-KH-PASCAL-*** | ThinkPad | Pascal port (gated; defer if validation fails) | 3 sessions |
| **NUM-KH-CGCC-*** | ThinkPad | C port (gated) | 3 sessions |
| **NUM-GR-PY-01..05** | ThinkPad | Python/SymPy reference for GR (canonical) | 3 sessions |
| **NUM-GR-RUST-01..05** | ThinkPad | Rust port (symbolica) | 3 sessions |
| **NUM-GR-SCALA-01..05** | ThinkPad | Scala port (jep wrapper) | 2 sessions |
| **NUM-GR-FOR-01..03** | ThinkPad | Fortran point-wise numerical cross-check | 1 session |
| **NUM-IS-FOR-01..09** | ThinkPad | Fortran reference for Ising (classical + quantum) | 5 sessions |
| **NUM-IS-RUST-01..09** | ThinkPad | Rust port | 4 sessions |
| **NUM-IS-SCALA-01..09** | ThinkPad | Scala port | 4 sessions |

**Total estimated effort:** ~37–43 ThinkPad iterations. Spread over multiple weeks; runs in parallel with PoC track. NOT all iterations need to ship in v0.2 — Fortran references + at least one full port per model is the v0.2 release gate; remaining ports follow in v0.2.x dot releases.

**v0.2 minimum release gate (Track NUM):**
- KH: Fortran ref + Rust port + REST surface + frontend visualisation
- GR: Python/SymPy ref + Rust port + REST surface + frontend (LaTeX render)
- Ising: Fortran ref (classical only — Wolff) + Rust port + REST + frontend (spin mosaic)

Quantum Ising (Lanczos / SSE QMC), Scala ports, gRPC + WebSocket channels, and Pascal/C ports are v0.2.x stretch targets.

---

## §9. Open questions

| OQ# | Question | Resolve by |
|-----|----------|------------|
| OQ-NUM-01 | FFT library choice for Fortran: FFTW3 (best perf, GPL) vs FFTPACK 5.1 (BSD, slower) — affects licensing of public release | NUM-KH-FOR-01 |
| OQ-NUM-02 | gRPC support across all 4 ported languages — Pascal gRPC bindings are immature; if Pascal is gated-in, can we accept REST-only for Pascal? | per-language NUM-*-09 |
| OQ-NUM-03 | NetCDF vs HDF5 for file dump — NetCDF is CFD standard, HDF5 has wider language support | NUM-KH-FOR-05 |
| OQ-NUM-04 | OpenMP for Fortran inner loops — turn on by default? Affects single-threaded reference reproducibility | NUM-KH-FOR-06 |
| OQ-NUM-05 | Reference recipe granularity — one canonical recipe per model, or a small recipe family (3–5 recipes) for richer cross-validation? | NUM-KH-FOR-07 |
| OQ-NUM-06 | Pascal/C validation gate (§1.1) — who declares pass/fail? Sonnet on its own, or Opus call? | per-language gate moment |
| OQ-NUM-07 | Symbolica (Rust CAS) maturity for non-trivial GR algebra (Kerr) — fallback to FFI-SymPy if symbolica chokes? | NUM-GR-RUST-03 |
| OQ-NUM-08 | SSE QMC initial scope — should it ship as part of Fortran reference v0.2, or defer to v0.2.x? | NUM-IS-FOR-06 |

---

## §10. Status footer

| Item | Value |
|------|-------|
| Document | `PHYSICS-NUMERICAL-METHODS-v0.1.md` |
| Output position | `_config/PHYSICS-NUMERICAL-METHODS-v0.1.md` |
| Models covered | 3 (KH, GR, Ising) |
| Languages planned | 5 (Fortran ref + Rust + Scala + Pascal/C gated) |
| Microservice channels per impl | 4 (REST + gRPC + WebSocket + file-dump) |
| Numerical-method TCs defined | 22 (8 KH + 7 GR + 7 Ising) |
| Step-by-step Fortran impl plan | 27 sub-iterations (9 per model) |
| References cited | 14 |
| Open questions | 8 (OQ-NUM-01..08) |
| Status | v0.1 — ready for ThinkPad NUM-KH-FOR-01 (first iteration) |

---

*PHYSICS-NUMERICAL-METHODS-v0.1.md — 2026-05-03 — MacBook CoWork session — Opus*
