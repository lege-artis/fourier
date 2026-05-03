# =============================================================================
# mimt-app/Makefile — Topology A (Docker) + Topology B (SQLite) runner
# tags:    [PoC-01][PoC-02][TOPO-A][TOPO-B]
# date:    2026-05-03
# citation: HANDOVER-V0.2-THINKPAD.md PoC-01/PoC-02; OPUS-CYCLE-v0.2-MASTER.md §6.1
#
# ── Topology B (SQLite, no Docker) ───────────────────────────────────────────
#   make dev             — boot DEV app (SQLite dev.sqlite, port 8080)
#   make prod            — boot PROD app (SQLite prod.sqlite, port 8090)
#   make migrate-dev     — run schema migrations against dev.sqlite
#   make migrate-prod    — run schema migrations against prod.sqlite
#   make smoke           — run SMK9 smoke suite against dev.sqlite
#   make test            — run full pytest suite against d06.sqlite (canonical)
#   make down            — print kill instructions (Topology B has no containers)
#   make check           — validate testcases.yaml has no orphan TCs
#
# ── Topology A (Docker 3-container) ──────────────────────────────────────────
#   make build           — docker compose build mimt-app image
#   make up              — docker compose up -d (pg14 + mysql8 + mimt-app)
#   make docker-down     — docker compose down (keep volumes)
#   make docker-wipe     — docker compose down -v (destroy volumes)
#   make migrate-pg      — run migrations inside container against postgres
#   make migrate-mysql   — run migrations inside container against mysql
#   make logs            — follow mimt-app logs
#   make test-docker     — run pytest suite inside mimt-app container (postgres)
#
# Prerequisite: copy .env.example to .env and review before first run.
# =============================================================================

PYTHON       ?= python3
PKG_ROOT      = ../mi_m_t
MIGRATE_RUNNER = $(PKG_ROOT)/migrations/runner.py
TESTCASES_YAML = ../../evidence/testcases.yaml
MIGRATE_SCRIPT = ../../../_config/migrate-testcases-v1-to-v2.py

MIMT_PORT_DEV  ?= 8080
MIMT_PORT_PROD ?= 8090
MIMT_HOST      ?= 0.0.0.0

# Topology A: Docker compose
COMPOSE        = docker compose -f docker-compose.yml
APP_CONTAINER  = mimt-app
MIMT_PORT_DOCKER ?= 8000

# Load .env if it exists (POSIX only; Windows users source manually)
-include .env
export

.PHONY: dev prod migrate-dev migrate-prod smoke test down check \
        build up docker-down docker-wipe migrate-pg migrate-mysql \
        logs test-docker help

# ── Runtime targets ───────────────────────────────────────────────────────────

dev: ## Boot DEV instance (SQLite dev.sqlite, port $(MIMT_PORT_DEV))
	MIMT_PORT_DEV=$(MIMT_PORT_DEV) MIMT_HOST=$(MIMT_HOST) \
	$(PYTHON) run.py --env=dev

prod: ## Boot PROD instance (SQLite prod.sqlite, port $(MIMT_PORT_PROD))
	MIMT_PORT_PROD=$(MIMT_PORT_PROD) MIMT_HOST=$(MIMT_HOST) \
	$(PYTHON) run.py --env=prod

# ── Migration targets ─────────────────────────────────────────────────────────

migrate-dev: ## Run schema migrations against dev.sqlite
	cd $(PKG_ROOT) && \
	SQLITE_PATH=dev.sqlite DB_DRIVER=sqlite \
	$(PYTHON) migrations/runner.py

migrate-prod: ## Run schema migrations against prod.sqlite
	cd $(PKG_ROOT) && \
	SQLITE_PATH=prod.sqlite DB_DRIVER=sqlite \
	$(PYTHON) migrations/runner.py

# ── Validation targets ────────────────────────────────────────────────────────

smoke: ## Run SMK9 20-item smoke suite against dev.sqlite
	cd $(PKG_ROOT) && \
	SQLITE_PATH=dev.sqlite DB_DRIVER=sqlite \
	$(PYTHON) smoke_test.py

test: ## Run full pytest suite (20 async functions) — copies d06.sqlite to /tmp to avoid Windows-mount I/O errors
	@TMP_DB=$$(mktemp /tmp/pyt