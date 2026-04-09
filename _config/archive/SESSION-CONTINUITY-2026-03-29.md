# Session Continuity Document
**Generated:** 2026-03-29 end-of-session (ThinkPad / CoWork)
**Supersedes:** SESSION-CONTINUITY-2026-03-28.md
**Registry version:** TASKS-shared.yaml v1.6.4
**Purpose:** Full handoff for Claude restart. Read this before any other file.

---

## 1. What Was Completed This Session

### DIAG-001 -- Diagram tooling (DONE, 2026-03-28)
draw.io + PlantUML VS Code extensions + Docker server on port 8010.

### LDE-001 -- draw.io desktop (DONE, 2026-03-29)
`winget install JGraph.drawio` confirmed by user.

### LDE-002 -- Docker image builds (DONE, 2026-03-29)
All 5 KH-sim backend images built successfully.
Fixes applied during build:
- Pascal: removed `-Cs67108864` (Windows-only FPC stack flag, illegal on Linux ppcx64)
- C++/Fortran: added `if(EXISTS ...)` guard around validation test targets in CMakeLists.txt
  (Docker context only contains src/; tests/ is host-only -- CMake generate failed without guard)
- All 3 compose files: removed `version: "3.9"` (obsolete attribute)

### LDE-003 -- Full stack startup (DONE, 2026-03-29)
`Start-LocalEnv.ps1 -Action up` starts all 6 services, all health checks green.
Fix: `$Args` PS automatic variable conflict in `Invoke-Compose` -- renamed to `$CmdArgs`.
Fix: orphan standalone `plantuml-server` container (from DIAG-001 `docker run`) blocked compose.

### LDE-004 -- Start-LocalEnv.ps1 acceptance (DONE, 2026-03-29)
All action modes verified: up, down, status, health, restart -Service kh-rust.

### R0-LDE gate -- CLOSED (2026-03-29)
All four LDE tasks done. R0-LDE release gate passed.

### Post-gate fixes (2026-03-29)
- Added `curl` to runtime apt install in Rust, C++, Fortran Dockerfiles
  (Docker HEALTHCHECK uses curl inside container; bookworm-slim has none)
  These images need rebuild: `docker compose -f infra\docker\docker-compose.backends.yml build kh-rust kh-cpp kh-fortran`

### LOG-001 -- ELK stack scaffolded (in-progress)
Files created:
- `infra/docker/elasticsearch/docker-compose.yml` -- ES 8.13.0 + Kibana 8.13.0 + Fluent Bit 3.0
- `infra/docker/elasticsearch/fluent-bit.conf` -- TCP input active, file-tail inputs stubbed
`Start-LocalEnv.ps1` extended with `-Stack` parameter: `lde` (default), `elk`, `all`.
LOG-001 status set to `in-progress` -- needs `docker compose up` + health check to close.

---

## 2. Immediate Next Actions

### 1. Rebuild Rust/C++/Fortran images (curl fix)
```powershell
docker compose -f infra\docker\docker-compose.backends.yml build kh-rust kh-cpp kh-fortran
.\_config\Start-LocalEnv.ps1 -Action restart -Service kh-rust
.\_config\Start-LocalEnv.ps1 -Action restart -Service kh-cpp
.\_config\Start-LocalEnv.ps1 -Action restart -Service kh-fortran
```
After ~15s Docker healthcheck cycle: all 3 should flip to `(healthy)`.

### 2. Complete LOG-001 -- start ELK stack
```powershell
.\_config\Start-LocalEnv.ps1 -Action up -Stack elk
```
Expected: ES :9200, Kibana :5601, Fluent Bit :2020 all green.
Note: ES takes ~30s cold start, Kibana ~60s (waits for ES healthy).
After up: `curl http://localhost:9200/_cluster/health` should return `"status":"green"` or `"yellow"`.

### 3. LOG-002 -- Wire kh-sim backends to Fluent Bit
Each backend needs to POST structured JSON to `http://fluent-bit:24224` (or host TCP on 24224).
Backends are containerised -- use host.docker.internal:24224 or elk-net bridge.

---

## 3. Current Docker Stack Status

### LDE stack (docker-compose.r0-lde.yml)
| Service | Port | Docker healthcheck | Script health |
|---|---|---|---|
| kh-rust | 8001 | unhealthy (curl missing -- fix pending rebuild) | OK |
| kh-scala | 8002 | healthy | OK |
| kh-cpp | 8003 | unhealthy (curl missing -- fix pending rebuild) | OK |
| kh-fortran | 8004 | unhealthy (curl missing -- fix pending rebuild) | OK |
| kh-pascal | 8005 | healthy | OK |
| plantuml-server | 8010 | healthy | OK |

### ELK stack (infra/docker/elasticsearch/docker-compose.yml)
Not yet started. Compose file + fluent-bit.conf written. Ready for `up -Stack elk`.

---

## 4. Release Map

### R0 -- Infrastructure Baseline (in-progress)
Remaining gate tasks:
- `LOG-001` -- ELK stack up (in-progress, compose scaffolded)
- `LOG-002..006` -- pipeline config, Kibana, SDK, retention, smoke test
- `GEN-014` -- MacBook IDE parity
- `GEN-015` -- Commit workflow (pre-commit hooks)
- `KH-017` -- CI/CD pipeline
- `SYMB-001` -- Tri-layer ADR

Done gate tasks (this session):
- `GEN-013` DONE, `DIAG-001` DONE, `LDE-001..004` DONE

### R0-LDE -- Local Dev Environment (CLOSED 2026-03-29)
All 4 gate tasks done. R1 depends on this gate.

### R1 -- KH-Instability Showcase (planned, depends R0-LDE)
### R2 -- Symbolic / GR Framework (planned, depends R1)

---

## 5. Key File Paths

```
VibeCodeProjects/
  _config/
    Start-LocalEnv.ps1           # LDE + ELK controller (-Stack lde|elk|all)
    vscode-extensions-setup.ps1  # GEN-013 auditor (-Verify flag)
  infra/
    LOG-ARCHITECTURE.md          # Hybrid log stack design (Fluent Bit + ES + Kibana)
    docker/
      docker-compose.r0-lde.yml  # LDE: 5 backends + plantuml (version attr removed)
      docker-compose.backends.yml
      docker-compose.diag.yml
      elasticsearch/
        docker-compose.yml       # ELK: ES 8.13 + Kibana 8.13 + Fluent Bit 3.0 (NEW)
        fluent-bit.conf          # Pipeline config (TCP active, file-tail stubbed) (NEW)
  kh-sim/backends/
    rust/Dockerfile              # curl added to runtime (rebuild pending)
    cpp/Dockerfile               # curl added to runtime (rebuild pending)
    fortran/Dockerfile           # curl added to runtime (rebuild pending)
    pascal/Dockerfile            # curl already present, healthy
    rust/   cpp/   fortran/
      CMakeLists.txt             # EXISTS guard on validation test target (Docker fix)
  TASKS-shared.yaml              # v1.6.4
  SESSION-CONTINUITY-2026-03-29.md  # This file
```

---

## 6. Known Constraints and Gotchas

### ELK resource footprint
- ES: 1 GB RAM, ~30s cold start. Start before Kibana (compose handles via depends_on).
- Kibana: 256 MB, ~60s start (waits for ES healthy). health endpoint: /api/status
- Fluent Bit: 32 MB, instant start. health: /api/v1/health
- Total additional: ~1.3 GB RAM -- start only when doing log pipeline work.

### Fluent Bit file-tail inputs (LOG-001 follow-on)
- PG and Mongo log file-tail inputs in fluent-bit.conf are disabled by default.
- To enable: uncomment volume mounts in elasticsearch/docker-compose.yml +
  uncomment [INPUT] blocks in fluent-bit.conf.
- Host paths: C:/Users/vitez/pgdata/pg.log, C:/Users/vitez/mongodata/mongod.log

### Backend log emission (LOG-002/LOG-004)
- Backends run in kh-sim-net network, ELK in elk-net.
- Fluent Bit TCP input (24224) is host-mapped, so backends can reach it via:
  host.docker.internal:24224 from within their containers.

### Start-LocalEnv.ps1 -Stack all
- Runs `up` on both compose files sequentially.
- Health check covers all 9 endpoints (6 LDE + 3 ELK).
- HealthTimeout default 120s may need raising to 180s for ELK cold start.

### Docker healthcheck vs script health (Rust/C++/Fortran)
- Docker's own HEALTHCHECK (runs curl inside container) reports unhealthy.
- Script's Invoke-WebRequest (runs from host through port mapping) reports OK.
- Root cause: curl not installed in bookworm-slim runtime. Fix committed; rebuild pending.
- After rebuild + container restart, all 6 will show (healthy) in `docker ps`.

### PowerShell $Args conflict (documented, fixed)
- $Args is a PS automatic variable -- never use as function param name.
- Invoke-Compose uses $CmdArgs. All future PS functions must avoid $Args.

### draw.io XML structure
- All mxCell elements must have parent="1" (flat structure).
- Never use nested swimlane containers -- causes null getAttribute crash.

---

## 7. Build and Run Reference

### Full LDE startup
```powershell
.\_config\Start-LocalEnv.ps1 -Action up
```

### ELK startup
```powershell
.\_config\Start-LocalEnv.ps1 -Action up -Stack elk
# ELK takes ~60-90s for all 3 services to reach healthy
```

### Both stacks
```powershell
.\_config\Start-LocalEnv.ps1 -Action up -Stack all -HealthTimeout 180
```

### Rebuild Rust/C++/Fortran (curl fix)
```powershell
docker compose -f infra\docker\docker-compose.backends.yml build kh-rust kh-cpp kh-fortran
```

### ES cluster health check
```powershell
Invoke-RestMethod http://localhost:9200/_cluster/health | Select status, number_of_nodes
```

---

## 8. TASKS-shared.yaml Quick Reference

```
Registry: TASKS-shared.yaml (root)
Version:  v1.6.4

Done this session:  DIAG-001, LDE-001, LDE-002, LDE-003, LDE-004
In-progress:        LOG-001 (compose scaffolded, needs up + health verify)
Next immediate:     rebuild kh-rust/cpp/fortran images (curl fix)
                    Start-LocalEnv.ps1 -Action up -Stack elk (LOG-001 completion)
                    LOG-002 Fluent Bit pipeline wiring to backends
Blocking R0:        LOG-001..006, GEN-014, GEN-015, KH-017, SYMB-001
```

---

*End of session continuity document. Begin next session by reading this file, then check TASKS-shared.yaml for current task statuses.*
