# Contributing to kh-sim

Thank you for your interest in contributing. kh-sim is a polyglot numerical simulation
benchmark — contributions in any of the five backend languages (Rust, Scala, C++,
Fortran, Pascal), the React frontend, the Node.js log service, or the physics/validation
layer are all welcome.

---

## Ground Rules

- All contributions must pass the **validation protocol** before merging
  (see [Validation Protocol](#validation-protocol))
- Code style must match the conventions already present in each backend directory
- One feature or fix per pull request — keep diffs reviewable
- Commit messages use the imperative: `Add spectral Poisson solver`, `Fix RK4 time step`

---

## Validation Protocol

Every backend change must produce diagnostics within tolerance of the Python/NumPy
reference at t=0.1 (100 steps, 64×32 grid, Re=1000):

| Diagnostic     | Reference   | Tolerance |
|----------------|-------------|-----------|
| kinetic_energy | 0.112810    | ±5%       |
| enstrophy      | 43.705142   | ±5%       |
| divergence_rms | 1.20e-14    | < 1e-10   |

Run before submitting a PR:
```bash
# Generate reference
cd shared/physics && python kh_physics.py

# Validate all live backends
cd tests && python validate_all_backends.py

# Or validate one backend
curl -X POST http://localhost:{port}/simulate \
  -H "Content-Type: application/json" \
  -d '{"grid_nx":64,"grid_ny":32,"dt":0.001,"steps":100}'
```

---

## Development Setup

### Reference kernel (Python)
```bash
pip install numpy
cd shared/physics
python kh_physics.py   # produces kh_reference_output.json
```

### Rust backend
```bash
cd backends/rust
cargo build --release
cargo test
```

### Scala backend
```bash
cd backends/scala
sbt compile
sbt test
```

### C++ backend
```bash
cd backends/cpp
mkdir build && cd build
cmake .. && make -j4
```

### Fortran backend
```bash
cd backends/fortran
gfortran -O2 -o kh_server src/*.f90 src/*.c
```

### Pascal backend
```bash
cd backends/pascal
fpc -O2 kh_server.pas
```

### Log service
```bash
cd log-service
npm install && npm start
```

---

## Adding a New Backend

If you want to add a new language backend:

1. Create `backends/{language}/` following the existing directory structure
2. Implement all three endpoints: `POST /simulate`, `GET /health`, `GET /info`
3. Match the `SimulationRequest` / `SimulationResult` JSON schemas exactly
   (see `shared/api/openapi.yaml`)
4. Use the tanh shear + sinusoidal perturbation initial conditions from
   `shared/physics/KH-PHYSICS.md §3`
5. Pass the validation protocol with diagnostics within ±5% of reference
6. Add an entry to `kh-sim.config.yaml` `backends:` block
7. Update `README.md` backend summary table
8. Add a vhost entry in `vhost/`

---

## Bug Reports

Open an issue with:
- Backend name and language version
- Simulation parameters that reproduce the issue
- Observed vs expected diagnostics (or error output)
- Platform: OS, compiler/runtime version

---

## Pull Request Checklist

- [ ] Validation protocol passes (diagnostics within tolerance)
- [ ] `GET /health` and `GET /info` return correct schema
- [ ] No hardcoded ports — port read from config or environment variable
- [ ] Code compiles/builds without warnings on at least one target platform
- [ ] PR description includes a one-sentence summary of the change

---

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
All contributors are expected to uphold its standards.
