# RUNBOOK-DEVOPS.md — MI-M-T On-Prem Topology A Operations
<!-- tags:    [PoC-02][TOPO-A] -->
<!-- date:    2026-05-03 -->
<!-- citation: OPUS-CYCLE-v0.2-MASTER.md §6.1 G-09; HANDOVER-V0.2-THINKPAD.md PoC-02 -->
<!-- scope:   3-fold-path MI-M-T evidence system — Topology A (Docker 3-container) -->

---

## 1. Prerequisites

### 1.1 Host requirements

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Docker Engine | 24.x | `docker --version` |
| Docker Compose | v2.x | `docker compose version` (v2 = plugin; v1 = standalone `docker-compose`) |
| Available RAM | 2 GB free | postgres + mysql + uvicorn combined |
| Available disk | 5 GB | DB volumes + image layers |
| OS | Linux / WSL2 | Native Docker. Windows Docker Desktop also works. |
| Python 3.11+ | optional | Only needed for Topology B (run.py) or local migration runs |

### 1.2 Credentials and configuration

```bash
# One-time setup — run from 3-fold-path/code/mimt-app/
cp .env.example .env
```

Edit `.env` — minimum required changes:

| Variable | Default | Action required |
|----------|---------|-----------------|
| `SECRET_KEY` | `change-me-...` | **Replace** with a 32+ char random string |
| `DB_DRIVER` | `postgres` | Leave for default backend; set `mysql` to use MySQL |
| `DB_PASS` | `postgres` | Change in production; must match docker-compose service value |

All other variables are functional as shipped for local PoC use.

### 1.3 Network port map

| Host port | Container | Service |
|-----------|-----------|---------|
| 8000 | 8000 | FastAPI (mimt-app) |
| 5433 | 5432 | PostgreSQL 14 (mimt-pg14) — avoids conflict with Windows-native PG17 on 5432 |
| 3306 | 3306 | MySQL 8 (mimt-mysql8) |

---

## 2. Initial Deploy

### 2.1 Build image

```bash
# From 3-fold-path/code/mimt-app/
make build
# Equivalent: docker compose -f docker-compose.yml build mimt-app
```

Build time ~3–5 min on first run (downloads base images + pip installs all deps).
Subsequent builds use layer cache and finish in <30 s if pyproject.toml unchanged.

### 2.2 Start all containers

```bash
make up
# docker compose -f docker-compose.yml up -d
```

Expected startup order (enforced by healthchecks):
1. `mimt-pg14` starts → pg_isready passes → healthy
2. `mimt-app` starts (depends_on mimt-pg14:healthy)
3. `mimt-mysql8` starts in parallel (no app dependency)

Verify all services running:

```bash
docker compose -f docker-compose.yml ps
# NAME           STATUS         PORTS
# mimt-app       Up (healthy)   0.0.0.0:8000->8000/tcp
# mimt-pg14      Up (healthy)   0.0.0.0:5433->5432/tcp
# mimt-mysql8    Up (healthy)   0.0.0.0:3306->3306/tcp
```

### 2.3 Run migrations

**Against PostgreSQL (default):**

```bash
make migrate-pg
# Inside container: python migrations/runner.py --engine postgres
```

**Against MySQL (optional — for portability validation):**

```bash
make migrate-mysql
# Inside container: python migrations/runner.py --engine mysql
```

Migration runner applies pending SQL files from `migrations/` directory.
Idempotent — safe to re-run; SHA-256 checksum prevents double-apply.
Expected: `29 migrations applied` on a fresh schema.

### 2.4 Validate

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"...","db_driver":"postgres","db_status":"ok"}
```

HTTP 200 with `db_status: ok` = deployment successful.
HTTP 503 = application running but DB probe failed — check migrations and DB logs.

---

## 3. Smoke Test

### 3.1 Health probe (mandatory)

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

Pass criteria: `status == "ok"` and `db_status == "ok"`.

### 3.2 SMK9 suite (20-item)

```bash
make test-docker
# docker compose exec mimt-app python -m pytest tests/ -v
```

Expected: `20 passed` in ~10–30 s.
All 20 tests are async (pytest-asyncio, `asyncio_mode = auto`).
Tests use an in-memory or temp SQLite DB by default; for Postgres, set
`DB_DRIVER=postgres` env inside the container prior to the run if needed.

### 3.3 Manual spot check — key routes

```bash
BASE=http://localhost:8000

# Evidence routes
curl -s $BASE/v1/bugs          | python -m json.tool | head -20
curl -s $BASE/v1/testcases     | python -m json.tool | head -20

# OQ-028 upsert idempotency
curl -s -X POST $BASE/v1/request_test_cases \
  -H "Content-Type: application/json" \
  -d '{"tc_ids":["TC-001","TC-002"]}' | python -m json.tool
```

---

## 4. Updating

### 4.1 Application code update

```bash
# 1. Pull latest changes (git fetch / merge / rebase as appropriate)
git pull origin thinkpad

# 2. Rebuild image (only changed layers rebuild)
make build

# 3. Rolling restart — zero-downtime for single-node (compose recreate)
docker compose -f docker-compose.yml up -d --no-deps mimt-app

# 4. Verify
curl http://localhost:8000/health
```

### 4.2 New migrations

After pulling code that includes new migration SQL files:

```bash
make migrate-pg      # or migrate-mysql
```

Always run migrations before restarting the app when schema changes are involved.

### 4.3 Dependency updates (pyproject.toml changed)

```bash
# Force full image rebuild — no cache
docker compose -f docker-compose.yml build --no-cache mimt-app
make up
```

---

## 5. Backup and Restore

### 5.1 PostgreSQL backup

```bash
# Dump (logical, all schemas)
docker exec mimt-pg14 pg_dump -U postgres mimt_dev \
  > backups/mimt-pg14-$(date +%Y%m%d-%H%M%S).sql

# Compressed dump
docker exec mimt-pg14 pg_dump -U postgres -Fc mimt_dev \
  > backups/mimt-pg14-$(date +%Y%m%d-%H%M%S).dump
```

### 5.2 MySQL backup

```bash
docker exec mimt-mysql8 mysqldump -u root mimt_dev \
  > backups/mimt-mysql8-$(date +%Y%m%d-%H%M%S).sql
```

### 5.3 PostgreSQL restore

```bash
# From SQL dump
docker exec -i mimt-pg14 psql -U postgres mimt_dev \
  < backups/mimt-pg14-20260503-120000.sql

# From compressed dump
docker exec -i mimt-pg14 pg_restore -U postgres -d mimt_dev \
  < backups/mimt-pg14-20260503-120000.dump
```

### 5.4 MySQL restore

```bash
docker exec -i mimt-mysql8 mysql -u root mimt_dev \
  < backups/mimt-mysql8-20260503-120000.sql
```

### 5.5 Volume backup (cold — requires stop)

```bash
make docker-down
# tar the volume mount point — inspect with: docker volume inspect mimt-pg14-data
tar czf backups/pg14-vol-$(date +%Y%m%d).tar.gz \
  $(docker volume inspect mimt-pg14-data --format '{{.Mountpoint}}')
make up
```

---

## 6. Rollback

### 6.1 Image rollback

```bash
# Tag current image before deploying, e.g.:
docker tag mimt-app:poc02 mimt-app:poc02-backup

# After a failed deploy, rollback:
docker compose -f docker-compose.yml stop mimt-app
docker tag mimt-app:poc02-backup mimt-app:poc02
docker compose -f docker-compose.yml up -d mimt-app
```

### 6.2 Schema rollback

The migration runner does **not** generate automatic down-migrations.
To roll back a schema change:

1. Restore the DB from the pre-migration backup (§5.3 or §5.4).
2. Deploy the previous code version.
3. Re-validate with `curl .../health`.

Document rollback decisions in `_config/KB-LESSONS-LEARNED.yaml` as `LL-OPS-*` entries.

### 6.3 Git-based rollback (code only)

```bash
# Identify the last known-good commit
git log --oneline -10 origin/thinkpad

# Roll back image to that commit's code
git checkout <commit> -- 3-fold-path/code/mi_m_t/
make build
docker compose -f docker-compose.yml up -d --no-deps mimt-app
```

---

## 7. Troubleshooting

### 7.1 Container won't start

```bash
make logs
# or
docker compose -f docker-compose.yml logs mimt-app --tail 50
```

Common causes:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: mi_m_t` | Build context wrong; Dockerfile not finding package | Confirm `docker-compose.yml` uses `context: ..` and `dockerfile: mimt-app/Dockerfile` |
| `Connection refused` to pg | mimt-app started before pg14 healthy | Check `depends_on` condition; `docker compose ps` for pg14 health status |
| `SECRET_KEY not set` | `.env` not copied | `cp .env.example .env` and fill SECRET_KEY |
| Port 8000 already in use | Topology B (run.py dev=8080) not relevant; check other process | `lsof -i :8000` or `netstat -tlnp \| grep 8000` |
| Port 5433 already in use | Another postgres14 container running | `docker ps` — check for orphan containers; `make docker-down` first |

### 7.2 Health returns 503

```bash
curl -v http://localhost:8000/health
# {"status":"degraded","db_status":"error","detail":"..."}
```

Steps:
1. Check DB is healthy: `docker compose ps` — look for `(healthy)` on mimt-pg14.
2. Verify env vars inside container: `docker exec mimt-app env | grep DB_`
3. Run migrations if schema is missing: `make migrate-pg`
4. Check DB logs: `docker compose logs mimt-pg14 --tail 30`

### 7.3 Migration fails

```bash
docker compose exec mimt-app python migrations/runner.py --engine postgres --verbose
```

| Error | Likely cause |
|-------|--------------|
| `relation already exists` | Migration already applied; idempotency check may have missed it — inspect `migrations/_applied` table |
| `password authentication failed` | DB_PASS mismatch between .env and docker-compose environment block |
| `could not connect to server` | DB container not healthy yet; wait 10–20 s and retry |

### 7.4 SQLite WAL disk I/O error (Topology B only)

This error (`sqlite3.OperationalError: disk I/O error`) occurs when SQLite WAL mode
is used on a Windows NTFS filesystem mounted via 9P (WSL2). It does **not** occur in
Topology A (Postgres/MySQL never touch the Windows-mounted path).

Topology B workaround: `cp dev.sqlite /tmp/mimt-dev.sqlite` before running
any write workload, or use `make test` which handles this automatically.

See KB-ENV-010 in `_config/KB-LESSONS-LEARNED.yaml`.

### 7.5 Windows NTFS index.lock

If `git` operations in VibeCodeProjects fail with `index.lock: File exists`:

```powershell
# PowerShell — remove stale lock
Remove-Item .git\index.lock -Force
```

This does NOT affect Topology A (Docker runs in Linux containers).

### 7.6 Useful diagnostic commands

```bash
# All container statuses
docker compose -f docker-compose.yml ps

# Live resource usage
docker stats mimt-app mimt-pg14 mimt-mysql8

# Shell into app container
docker compose -f docker-compose.yml exec mimt-app bash

# Shell into postgres
docker compose -f docker-compose.yml exec mimt-pg14 psql -U postgres mimt_dev

# Shell into mysql
docker compose -f docker-compose.yml exec mimt-mysql8 mysql -u root mimt_dev

# Network inspection
docker network inspect mimt-topo-a
```

---

*Document owner: ThinkPad / MI-M-T PoC team*
*Next review: PoC-03 or first production deployment*
