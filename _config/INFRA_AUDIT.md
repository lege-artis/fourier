# Infrastructure Audit — VibeCodeProjects ThinkPad
**Audit date:** 2026-03-21
**Auditor:** Claude / Cowork session
**Scope:** Linux VM sandbox (dev sandbox) + Windows host (ThinkPad)
**Standard:** IT infrastructure documentation v1.0

---

## 1. Device & OS Profile

| Attribute        | Value                                               |
|------------------|-----------------------------------------------------|
| Codename         | ThinkPad                                            |
| Host OS          | Windows (version TBC — audit from VM)               |
| Sandbox OS       | Ubuntu 22.04.5 LTS (Jammy Jellyfish)                |
| Kernel           | Linux 6.8.0-94-generic x86_64                       |
| Sandbox user     | funny-zen-pascal (uid=1004, non-root)               |
| Sandbox home     | `/sessions/funny-zen-pascal` (9.8 GB, 9.3 GB free) |
| System disk (/)  | 9.6 GB total, 7.1 GB used, 2.5 GB free (75%)        |
| Workspace mount  | `/sessions/funny-zen-pascal/mnt/VibeCodeProjects` → `C:\Users\vitez\Documents\VibeCodeProjects` |
| Memory           | 3.8 GB total, ~2.3 GB available                     |

---

## 2. Sandbox Runtime Environment — Current State

### 2.1 Available and Verified

| Tool             | Version                          | Path                  | Status       |
|------------------|----------------------------------|-----------------------|--------------|
| GCC              | 11.4.0 (Ubuntu)                  | `/usr/bin/gcc`        | ✅ ACTIVE     |
| G++              | 11.4.0 (Ubuntu)                  | `/usr/bin/g++`        | ✅ ACTIVE     |
| OpenJDK          | 11.0.30 (2026-01-20)             | `/usr/bin/java`       | ✅ ACTIVE     |
| Node.js          | v22.22.0 (x64, V8 12.4.254.21)  | `/usr/bin/node`       | ✅ ACTIVE     |
| npm              | 10.9.4                           | `/usr/bin/npm`        | ✅ ACTIVE     |
| Python 3         | 3.10.12 (GCC 11.4.0, x86_64)    | `/usr/bin/python3`    | ✅ ACTIVE     |
| pip3             | 25.3                             | system dist-packages  | ✅ ACTIVE     |
| Git              | 2.34.1                           | `/usr/bin/git`        | ✅ ACTIVE     |
| curl             | 7.81.0 (OpenSSL 3.0.2)          | `/usr/bin/curl`       | ✅ ACTIVE (no outbound HTTP) |
| wget             | 1.21.2                           | `/usr/bin/wget`       | ✅ ACTIVE (no outbound HTTP) |
| pandoc           | present                          | `/usr/bin/pandoc`     | ✅ ACTIVE     |

### 2.2 Missing — Require Windows-side Installation

| Tool             | Platform       | Install Method                    | Priority |
|------------------|----------------|-----------------------------------|----------|
| rustc / cargo    | Rust           | `winget install Rustlang.Rust.MSVC` | HIGH   |
| gfortran         | Fortran        | MSYS2 → `pacman -S mingw-w64-x86_64-gcc-fortran` | HIGH |
| fpc              | Pascal (FPC)   | `winget install FreePascal.FreePascal` | HIGH  |
| scalac / sbt     | Scala          | `winget install Lightbend.SBT`    | HIGH     |
| docker           | CI/CD          | `winget install Docker.DockerDesktop` | HIGH  |
| gh               | GitHub CLI     | `winget install GitHub.cli`       | HIGH     |
| act              | Local Actions  | download from https://github.com/nektos/act | MEDIUM |
| psql             | PostgreSQL CLI | bundled with PostgreSQL install   | MEDIUM   |
| mongosh          | MongoDB CLI    | bundled with MongoDB install      | MEDIUM   |
| javac / javap    | Java JDK       | `winget install EclipseAdoptium.Temurin.17.JDK` | MEDIUM |

### 2.3 Python Packages Available

| Package    | Status   | Notes                          |
|------------|----------|--------------------------------|
| numpy      | ✅       | available                      |
| pandas     | ✅       | available                      |
| requests   | ✅       | available                      |
| opencv     | ✅       | opencv-python + headless       |
| onnxruntime| ✅       | available                      |
| matplotlib | ✅       | available                      |
| psycopg2   | ❌       | needs install (network blocked)|
| pymongo    | ❌       | needs install (network blocked)|
| pytest     | ❌       | needs install (network blocked)|
| sqlalchemy | ❌       | needs install (network blocked)|

---

## 3. Network Constraints

| Constraint                              | Impact                                           |
|-----------------------------------------|--------------------------------------------------|
| Bash outbound HTTP: **BLOCKED**         | Cannot `curl`/`wget` from shell                  |
| npm registry: **BLOCKED** from VM       | Cannot `npm install` new packages                |
| pip PyPI: **BLOCKED** from VM           | Cannot `pip install` new packages                |
| apt-get: **NO ROOT** + packages limited | Cannot install system tools via apt              |
| Browser (Chrome): **OPEN**             | Full internet access via browser MCP tools       |
| Workspace folder mount: **OPEN**        | Files written here are accessible on Windows     |

**Workaround:** All downloads/installs are performed via browser automation or Windows-side scripts.

---

## 4. Platform Sources — Readiness Matrix

| Platform   | Test File           | Compiler (VM) | Compiler (Win) | Test Run (VM) | Test Run (Win) |
|------------|---------------------|---------------|----------------|---------------|----------------|
| C++        | `hello_test.cpp`    | GCC 11.4 ✅   | MSVC / MinGW   | ✅ PASSED      | Pending        |
| Fortran    | `hello_test.f90`    | ❌ gfortran missing | MSYS2 GFortran | ❌ Pending | Pending    |
| Pascal     | `hello_test.pas`    | ❌ fpc missing | FPC 3.x        | ❌ Pending    | Pending        |
| Rust       | `hello_test/`       | ❌ cargo missing | rustup stable | ❌ Pending  | Pending        |
| Scala      | `HelloTest.scala`   | ❌ sbt missing | SBT 1.x        | ❌ Pending    | Pending        |
| React      | `App.test.jsx`      | Node ✅ (npm blocked) | Node.js LTS | ❌ Pending | Pending  |

---

## 5. Database Infrastructure — Target Configuration

### 5.1 PostgreSQL

| Parameter        | Value                                |
|------------------|--------------------------------------|
| Licence          | PostgreSQL Licence (free / open)     |
| Target version   | PostgreSQL 16.x                      |
| Install target   | Windows host — standard install      |
| Data directory   | `C:\Users\vitez\Documents\VibeCodeProjects\databases\PostgreSQL\data` |
| Port             | 5432 (default)                       |
| Default DB       | `vibedev`                            |
| Dev user         | `vibedev_user`                       |
| Auth method      | md5 (localhost), peer (socket)       |
| Status           | ⏳ PENDING — Windows install via `windows-setup.ps1` |

### 5.2 MongoDB

| Parameter        | Value                                |
|------------------|--------------------------------------|
| Licence          | Server Side Public Licence (SSPL) — free for dev |
| Target version   | MongoDB 7.x Community Edition        |
| Install target   | Windows host — standard install      |
| Data directory   | `C:\Users\vitez\Documents\VibeCodeProjects\databases\MongoDB\data` |
| Port             | 27017 (default)                      |
| Default DB       | `vibedev`                            |
| Auth             | Disabled for local dev               |
| Status           | ⏳ PENDING — Windows install via `windows-setup.ps1` |

---

## 6. CI/CD Architecture

| Component               | Technology          | Status          | Location                              |
|-------------------------|---------------------|-----------------|---------------------------------------|
| Remote CI               | GitHub Actions      | ✅ CONFIGURED   | `.github/workflows/ci-heartbeat.yml`  |
| Heartbeat schedule      | Every 6 hours       | ✅ CONFIGURED   | cron: `0 */6 * * *`                   |
| C++ job                 | ubuntu-latest       | ✅ READY        | CI workflow                           |
| Rust job                | ubuntu-latest       | ✅ READY        | CI workflow                           |
| Scala job               | ubuntu-latest       | ✅ READY        | CI workflow                           |
| Pascal job              | ubuntu-latest       | ✅ READY        | CI workflow                           |
| Fortran job             | ubuntu-latest       | ✅ READY        | CI workflow                           |
| React unit test         | ubuntu-latest       | ✅ READY        | CI workflow                           |
| Browser Chrome test     | windows-latest      | ✅ READY        | CI workflow (Playwright)              |
| Browser Firefox test    | ubuntu-latest       | ✅ READY        | CI workflow (Playwright crosscheck)   |
| DB connectivity test    | ubuntu-latest       | ✅ READY        | CI workflow (PostgreSQL service)      |
| Local runner (act)      | Docker-based        | ⏳ PENDING      | Needs Docker Desktop on Windows       |
| GitHub CLI (gh)         | CLI tool            | ⏳ PENDING      | Needs Windows install                 |

---

## 7. GitHub Integration — Status

| Item                    | Status             | Notes                                      |
|-------------------------|--------------------|--------------------------------------------|
| Account                 | `petr-yamyang`     | Email: petr@zemla.org                      |
| SSH key (ED25519)       | ✅ GENERATED        | Fingerprint: `SHA256:QNK7Sj...`            |
| SSH key added to GitHub | ⏳ PENDING          | Browser reconnect required                 |
| PAT (scoped)            | ⏳ PENDING          | Browser reconnect required                 |
| Git global config       | ⏳ PENDING          | Will set after SSH key confirmed           |
| Workspace repo          | ⏳ PENDING          | `git init` + remote add after SSH done     |

---

## 8. LibreOffice + TexLive — Migration Plan

| Phase     | Action                                        | Script                              |
|-----------|-----------------------------------------------|-------------------------------------|
| Pre-setup | Export winget manifest → uninstall from C:\   | `libreoffice-migrate-to-D.ps1 -Phase backup` |
| Post-setup| Reinstall to `D:\Apps\`                       | `libreoffice-migrate-to-D.ps1 -Phase restore` |
| Temp repo | `D:\TempRepo\`                                | Installers + manifests stored here  |
| Daily use | LibreOffice + MiKTeX run from `D:\Apps\`      | Persistent post-migration           |

---

## 9. Known Constraints & Workarounds

| Constraint                              | Workaround                                    |
|-----------------------------------------|-----------------------------------------------|
| VM bash: no outbound network            | Use browser MCP for downloads                 |
| VM: no root / no apt installs           | User-space installs to `$HOME`, Windows scripts |
| VM: Docker TUN device unavailable       | Docker runs on Windows host via Docker Desktop |
| VM: npm/pip registry blocked            | React/Python dev runs on Windows Node.js      |
| Browser MCP: disconnected at session start | All browser tasks queued, pending reconnect |

---

## 10. Next Actions Checklist

- [ ] **Connect browser** → add SSH key to github.com/petr-yamyang → generate PAT → encrypt
- [ ] **Run on Windows**: `windows-setup.ps1` (as Administrator) — installs all dev tools
- [ ] **Run on Windows**: `libreoffice-migrate-to-D.ps1 -Phase backup` — frees C:\ before installs
- [ ] **Run on Windows**: `libreoffice-migrate-to-D.ps1 -Phase restore` — reinstates to D:\ after
- [ ] **Initialize Git repo**: `git init` in workspace, `git remote add origin git@github.com:petr-yamyang/<repo>.git`
- [ ] **Validate databases**: run connection tests after PostgreSQL + MongoDB Windows install
- [ ] **Validate all platforms**: run hello_test for each language after Windows install
- [ ] **Sync with MacBook**: paste MacBook task list here to merge into `TASKS.yaml`
- [ ] **Configure act**: `act --list` after Docker Desktop is running
- [ ] **Push initial commit**: push workspace scaffold to GitHub via SSH

---

*Document generated: 2026-03-21 | Device: ThinkPad | Session: workspace-init*
