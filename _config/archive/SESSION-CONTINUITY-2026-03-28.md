# Session Continuity Document
**Generated:** 2026-03-28T23:07 (ThinkPad / CoWork)
**Registry version:** TASKS-shared.yaml v1.6.1 — 142 tasks (34 done, 2 in-progress, 96 pending/deferred/planned)
**Purpose:** Full handoff for Claude restart. Read this before any other file.

---

## 1. What Was Completed This Session

### KH-007 — Pascal backend (DONE — prior session)
Full Cooley-Tukey + RK4 pseudo-spectral KH-instability simulation in Free Pascal 3.2.2, Win32/i386.
Validation: kinetic_energy err=1.48e-13%, enstrophy err=6.50e-14%, div_rms=8.63e-15. HTTP smoke test PASS (port 8005).

### GEN-013 — VS Code IDE setup ThinkPad (DONE — this session)
All 11 extensions installed and verified. Language servers confirmed active.

**Extensions installed (11/11 PASS):**
- rust-lang.rust-analyzer, scalameta.metals, ms-vscode.cpptools, hansec.fortran-ls
- Wosi.omnipascal, ms-python.python
- eamodio.gitlens, mhutchie.git-graph, vivaxy.vscode-conventional-commits
- hediet.vscode-drawio, jebbs.plantuml

**Acceptance matrix (all PASS):**

| Server | Evidence |
|---|---|
| rust-analyzer | PID confirmed; main.rs open, 0 errors |
| Metals 1.6.6 | java PID confirmed; `run\|debug` codelens visible on Scala; 0 errors |
| cpptools | PIDs confirmed; kh_server.cpp open |
| fortls 3.2.2 | Binary confirmed; kh_server.f90 open; explicit path in settings.json |
| OmniPascal | Extension-host hosted; kh_server.pas open; 0 errors |
| Pylance | Confirmed in exthost.log (vscode-pylance-2026.1.1) |
| GitLens / Git Graph / Conv. Commits | Installed and verified |
| draw.io / PlantUML | Installed; PlantUML Docker HTTP 200 on port 8010 |
| Git | branch=main, remote=git@github.com:petr-yamyang/VibeCodeProjects.git |
| PlantUML Docker | plantuml/plantuml-server:jetty running, port 8010, HTTP 200 |

**Fixes applied during acceptance:**
1. `metals.serverVersion: "latest.release"` removed from .vscode/settings.json
   — was causing Coursier "Invalid Version" error; Metals now uses extension-bundled default (1.6.6)
2. fortls PATH fix: MS Store Python installs scripts to non-standard path, not on PATH
   — Added to user PATH permanently (SetEnvironmentVariable User scope)
   — Full explicit path wired into settings.json: `fortran.fortls.path`
   — Path: `C:\Users\vitez\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\fortls.exe`

**Files created/modified this session:**
- `_config/vscode-extensions-setup.ps1` — idempotent installer + auditor (NEW)
- `.vscode/extensions.json` — workspace recommendations (NEW)
- `.vscode/settings.json` — full language server + tool config (NEW)
- `TASKS-shared.yaml` — GEN-013 status=done, v1.6.0→v1.6.1

---

## 2. Current KH-Sim Backend Status

| Backend | Language | Port | Validate | HTTP | Task |
|---|---|---|---|---|---|
| Rust | Rust | 8001 | PASS | PASS | KH-003 done |
| Scala | Scala/Akka | 8002 | PASS | PASS | KH-004 done |
| C++ | C++17/httplib | 8003 | PASS | PASS | KH-005 done |
| Fortran | F90/httplib shim | 8004 | PASS | PASS | KH-006 done |
| Pascal | FPC 3.2.2 | 8005 | PASS | PASS | KH-007 done |
| PINN | (not started) | 8600 | — | — | PINN-001+ |

All 5 backends: bit-identical to Python/NumPy reference, div_rms < 1e-14.

---

## 3. Release Map (R0-R4)

### R0 — Infrastructure Baseline (in-progress)
Gate tasks:
- `LOG-001..006` — ELK stack (Elasticsearch + Logstash + Kibana) live
- `GEN-013` — VS Code IDE ThinkPad **DONE**
- `GEN-014` — VS Code IDE MacBook parity (next sprint)
- `GEN-015` — Commit workflow validation (pre-commit hooks, semantic commits)
- `KH-016` — Docker compose for all 5 backends + React F/E
- `KH-017` — CI/CD (GitHub Actions: build + validate + lint)
- `SYMB-001` — Tri-layer symbolic/reasoning/log ADR written

### R1 — KH-Instability Showcase (planned, depends R0)
Gate tasks: KH-008..015, WEB-001..005

### R2 — Symbolic / GR Framework (planned, depends R1)
Gate tasks: SYMB-002..005, GR-001..003, DASH-001..003

### R3 — MI-M-T Initial Release (planned, depends R1)
Gate tasks: MI-M-T-D01 (done), D02, D03, D04, D05

### R4 — Nonlinear Physics Framework (planned, depends R2+R3)
Gate tasks: GR-003..005, PINN-002/003, SOLV-001..004, KH-VAL

---

## 4. Architecture Decisions Locked

### Diagram tooling
- **draw.io:** VS Code extension `hediet.vscode-drawio` (C4 structural + dashboard wireframes)
- **PlantUML:** VS Code extension `jebbs.plantuml` + Docker service `plantuml/plantuml-server:jetty`
  on port 8010. VS Code settings: `"plantuml.server": "http://localhost:8010"`, `"plantuml.render": "PlantUMLServer"`
- Mermaid: zero-install fallback (built into GitHub/GitLab rendering)

### Symbolic layer
- Layer 1: Julia + Symbolics.jl + ModelingToolkit.jl
- Layer 2: Clojure + core.logic + Datahike
- Layer 3: ELK as raw event store -> Datahike ETL projection

### GR test cases
- Source: Podolsky & Griffiths, "Exact Space-Times in Einstein's General Relativity", Cambridge 2009
- Families: Minkowski, Schwarzschild, pp-waves, Kerr
- QNM acceptance: omegaM ~ 0.3737 - 0.0890i (Leaver 1985, <0.1%)

### Classical solver (SOLV-001 scopes final choice)
- Recommended: Julia (Symbolics.jl interop + DifferentialEquations.jl), port 8006

---

## 5. Next Tasks on Critical Path

**Immediate (ThinkPad, this machine):**
1. `DIAG-001` — draw.io + PlantUML Docker service smoke test
   - PlantUML Docker already running on port 8010 (done during GEN-013 acceptance)
   - Remaining: create a test .puml file, preview in VS Code, confirm render
   - draw.io: open a .drawio file in VS Code, confirm editor loads

**Next sprint (MacBook):**
2. `GEN-014` — IDE parity on MacBook
   NOTE: fortls fix needed — MS Store Python PATH issue will recur on MacBook if Python is also
   from MS Store. Apply same fix: pip install fortls, add Scripts to PATH, set explicit path in settings.
3. `WEB-001` — Pull WP theme repos, confirm local dev workflow
4. `SYMB-001` — Write tri-layer ADR

**Blocking R0:**
- LOG-001 (ELK compose) and KH-016 (Docker) are the heaviest remaining R0 items

---

## 6. Key File Paths

```
VibeCodeProjects/
  .vscode/
    settings.json      # Workspace settings -- all LSP configs, PlantUML server, fortls path
    extensions.json    # Workspace recommendations (11 extensions)
  _config/
    vscode-extensions-setup.ps1  # GEN-013 installer/auditor -- run with -Verify to audit
    windows-setup.ps1            # Compiler/tool installer (VS Code, Git, Node, Rust, Pascal, Java, SBT...)
  kh-sim/
    backends/pascal/
      src/kh_physics.pas       # Physics kernel
      src/kh_server.pas        # HTTP server -- fphttpserver, port 8005, DONE
      tests/kh_validate.pas    # Validator -- lx=1.0/ly=0.5/dt=0.001, DONE
      build.ps1
    shared/physics/
      kh_physics.py            # Python reference (lx=1.0, ly=0.5, dt=0.001, nx=64, ny=32)
      kh_reference_output.json # Reference diagnostics
  TASKS-shared.yaml            # v1.6.1, 142 tasks
  SESSION-CONTINUITY-2026-03-28.md  # This file
```

---

## 7. Known Constraints & Gotchas

### FPC 3.2.2 Windows
- `httpmod` unit ABSENT — use `fphttpserver` directly with `TFPHttpServer`
- `Server.Active := True` blocks (accept loop) — correct for single-threaded server

### MS Store Python 3.10 (ThinkPad)
- Scripts install to non-standard path NOT on system PATH:
  `C:\Users\vitez\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\`
- Fix applied: added to user PATH + explicit path in .vscode/settings.json
- Affects: fortls (and any other pip-installed CLI tools)
- Will recur on MacBook if same Python source — check before GEN-014

### Metals (Scala)
- Do NOT set `metals.serverVersion` in settings.json — "latest.release" is not valid Coursier semver
- Let extension use bundled default (currently resolves to 1.6.6)
- First-run requires "Finish Setup" click in VS Code OR run `sbt bloopInstall` from terminal
- Uses Java from Eclipse Adoptium Temurin 17.0.18

### PlantUML Docker
- Container name: `plantuml-server`, port mapping: 8010:8080
- Not auto-started on boot — add to Docker Desktop startup or re-run:
  `docker run -d -p 8010:8080 --name plantuml-server plantuml/plantuml-server:jetty`
- For subsequent starts (container exists): `docker start plantuml-server`

### PS1 script encoding
- All PowerShell scripts MUST use ASCII-only string literals
- Em dashes and smart quotes cause parse errors under Windows-1252/CP850 console code pages
- Use `--` and `:` as separators in hash table values

---

## 8. Build Commands Reference

### Pascal backend (ThinkPad, PowerShell)
```powershell
cd kh-sim\backends\pascal
.\build.ps1 validate
.\build.ps1 server
.\build\kh_server.exe  # start on port 8005 (blocking)

# Smoke test
Invoke-RestMethod http://localhost:8005/health
$b='{"nx":64,"ny":32,"lx":1.0,"ly":0.5,"dt":0.001,"steps":10,"re":1000,"u0":1.0,"amp":0.01,"mode":2}'
Invoke-RestMethod -Method Post http://localhost:8005/simulate -Body $b -ContentType 'application/json'
```

### PlantUML Docker
```powershell
# First run (pulls image)
docker run -d -p 8010:8080 --name plantuml-server plantuml/plantuml-server:jetty
# Subsequent runs
docker start plantuml-server
# Health check
Invoke-WebRequest http://localhost:8010 -UseBasicParsing
```

### GEN-013 extension audit (re-run anytime)
```powershell
cd C:\Users\vitez\Documents\VibeCodeProjects
.\_config\vscode-extensions-setup.ps1 -Verify
```

---

## 9. TASKS-shared.yaml Quick Reference

```
Registry: TASKS-shared.yaml (root of VibeCodeProjects/)
Version:  v1.6.1 (schema 2.0.0)
Tasks:    142 total | 34 done | 2 in-progress | 96 pending/deferred/planned

Done this session: GEN-013
Next immediate:    DIAG-001 (draw.io + PlantUML smoke test)
Next sprint:       GEN-014 (MacBook IDE parity), WEB-001, SYMB-001
Blocking R0:       LOG-001, KH-016, KH-017, GEN-015, SYMB-001
```

---

*End of session continuity document. Begin next session by reading this file, then check TASKS-shared.yaml for current task statuses.*
