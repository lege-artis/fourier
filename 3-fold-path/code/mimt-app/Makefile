# =============================================================================
# mimt-app/Makefile — Topology B runner (Windows-portable via WSL/POSIX make)
# tags:    [PoC-01][TOPO-B]
# date:    2026-05-03
# citation: HANDOVER-V0.2-THINKPAD.md PoC-01; OPUS-CYCLE-v0.2-MASTER.md §2
#
# Targets:
#   make dev           — boot DEV app (SQLite dev.sqlite, port 8080)
#   make prod          — boot PROD app (SQLite prod.sqlite, port 8090)
#   make migrate-dev   — run schema migrations against dev.sqlite
#   make migrate-prod  — run schema migrations against prod.sqlite
#   make smoke         — run SMK9 smoke suite against dev.sqlite
#   make test          — run full pytest suite against d06.sqlite (canonical)
#   make down          — print kill instructions (Topology B has no containers)
#   make check         — validate testcases.yaml has no orphan TCs
#
# Prerequisite: copy .env.example to .env and review before first run.
# =============================================================================

PYTHON       ?= python3
PKG_ROOT      = ../mi_m_t
MIGRATE_RUNNER = $(PKG_ROOT)/migrations/runner.py
TESTCASES_YAML = ../../3-fold-path/evidence/testcases.yaml
MIGRATE_SCRIPT = ../../../_config/migrate-testcases-v1-to-v2.py

MIMT_PORT_DEV  ?= 8080
MIMT_PORT_PROD ?= 8090
MIMT_HOST      ?= 0.0.0.0

# Load .env if it exists (POSIX only; Windows users source manually)
-include .env
export

.PHONY: dev prod migrate-dev migrate-prod smoke test down check help

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
	@TMP_DB=$$(mktemp /tmp/pytest-XXXXXX.sqlite); \
	cp $(PKG_ROOT)/d06.sqlite $$TMP_DB; \
	cd $(PKG_ROOT) && \
	SQLITE_PATH=$$TMP_DB DB_DRIVER=sqlite \
	$(PYTHON) -m pytest tests/ -v; \
	EXIT=$$?; rm -f $$TMP_DB; exit $$EXIT

check: ## Validate testcases.yaml — exit 1 if any TC missing test_target_ref/requirement_ref
	$(PYTHON) $(MIGRATE_SCRIPT) --check --input $(TESTCASES_YAML)

# ── Lifecycle ─────────────────────────────────────────────────────────────────

down: ## Stop Topology B processes (no containers — manual kill required)
	@echo "Topology B has no containers to stop."
	@echo ""
	@echo "Kill DEV process (port $(MIMT_PORT_DEV)):"
	@echo "  Linux/WSL:  pkill -f 'run.py --env=dev'   or  fuser -k $(MIMT_PORT_DEV)/tcp"
	@echo "  Windows:    taskkill /IM python.exe /F  (kills ALL python — use with care)"
	@echo ""
	@echo "Kill PROD process (port $(MIMT_PORT_PROD)):"
	@echo "  Linux/WSL:  pkill -f 'run.py --env=prod'  or  fuser -k $(MIMT_PORT_PROD)/tcp"

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*## "}; {printf "  %-18s %s\n", $$1, $$2}'
