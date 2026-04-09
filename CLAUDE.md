# VibeCodeProjects — Claude Context

## Project summary
Multi-backend KH-instability simulation platform (Rust, Scala, C++, Fortran, Pascal)
with tri-layer symbolic/reasoning/log infrastructure (Julia, Clojure, ELK→Datahike).

## Always read first
1. `_config/SESSION-HANDOFF.md` — task state, R0 gate status, next priorities
2. `TASKS-shared.yaml` — canonical task registry (semantic merge, v2.0.0 schema)

## Key files
| Path | Purpose |
|---|---|
| `.github/workflows/kh-sim-ci.yml` | KH-SIM CI — build + validate + lint (5 backends) |
| `.github/workflows/ci-heartbeat.yml` | Platform toolchain probes |
| `infra/SYMB-ARCHITECTURE.md` | SYMB-001 ADR — tri-layer architecture |
| `infra/PINN-ARCHITECTURE.md` | PINN ADR |
| `kh-sim/shared/physics/KH-PHYSICS.md` | Physics reference + validation spec |
| `kh-sim/shared/physics/kh_reference_output.json` | Canonical validation output |
| `_config/Start-LocalEnv.ps1` | LDE controller (up/down/health/build/logs) |
| `_config/merge-tasks.py` | Semantic merge driver for TASKS-shared.yaml |
| `_tests/test_task_integrity.py` | TASKS integrity CI gate |

## R0 milestone gate tasks
See `TASKS-shared.yaml` → `milestones.R0` for current status.

## Conventions
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`)
- Task IDs: `<PREFIX>-NNN` (KH, LOG, SYMB, LDE, GEN, DIAG, GR, WEB)
- Ports: kh-rust 8001, kh-scala 8002, kh-cpp 8003, kh-fortran 8004, kh-pascal 8005,
         plantuml 8010, julia-symb 8601, clj-reason 8700, etl-bridge 8701
