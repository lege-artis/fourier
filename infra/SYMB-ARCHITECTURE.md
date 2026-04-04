# Symbolic / Reasoning / Log Architecture — ADR
**Project:** VibeCodeProjects — symb-infra
**Task:** SYMB-001
**Version:** 1.0.0 | **Date:** 2026-04-04
**Status:** Accepted — architecture confirmed 2026-03-28
**Author:** ThinkPad / CoWork session 2026-04-04

---

## Context

The KH-SIM platform has five validated physics backends (Rust, Scala, C++, Fortran, Pascal), a PINN
layer (DeepXDE + JAX/Equinox, documented in `infra/PINN-ARCHITECTURE.md`), and an ELK log
infrastructure (LOG-001 through LOG-006, all complete as of 2026-04-03). The next architectural
layer introduces symbolic computation, logic-based reasoning, and a structured bridge from raw log
events into a queryable knowledge representation.

The architecture spans three tiers:

| Layer | Role | Primary technology |
|-------|------|--------------------|
| L1 — Physics symbolic | Symbolic manipulation of PDEs and their residuals | Julia (Symbolics.jl, ModelingToolkit.jl) |
| L2 — Reasoning | Inference rules over system state; structured knowledge queries | Clojure (core.logic, Datahike) |
| L3 — Log bridge | Projection of ELK raw events into a Datalog-queryable fact store | ETL pipeline → Datahike |

The architecture was reviewed and accepted on 2026-03-28. This document records the five design
decisions that gate SYMB-002 through SYMB-005.

---

## Decision 1 — Julia as the Physics Symbolic Layer Boundary

### Decision

Julia owns all symbolic computation over PDE structure. The Python/PINN layer retains
numerical execution (DeepXDE, JAX). The boundary is explicit: symbolic artefacts cross into
Python as serialised expressions or numerical evaluation endpoints; numerical training results
cross into Julia only for post-hoc symbolic consistency checks, not during training.

### Rationale

Julia's `Symbolics.jl` + `ModelingToolkit.jl` stack provides native symbolic differentiation of
PDE residual terms, expression simplification, and dimensional consistency checks without the
overhead of a CAS process boundary. Python-side equivalents (SymPy, JAX symbolic transforms) are
either slower for PDE-scale expressions or structurally incompatible with the PINN training loop.

Keeping numerical training in Python avoids re-implementing the DeepXDE/JAX pipeline. The
boundary is stable: Julia produces symbolic Jacobians and constraint flags; Python consumes them
via a REST sidecar or PyCall.jl (see Decision 4).

### Scope of Julia symbolic layer

- **In scope:** Symbolic representation of the KH vorticity equation
  `ω_t + u·ω_x + v·ω_y = ν·∇²ω`; AD of PDE residual terms via ModelingToolkit symbolic AD;
  expression simplification and dimensional consistency checks; REST sidecar exposing symbolic
  query endpoints (port allocation: Decision 5).

- **Out of scope:** Neural-network training, loss gradient computation, physics-informed
  collocation sampling — these remain in the Python/DeepXDE layer (`infra/PINN-ARCHITECTURE.md`,
  port 8600).

### Acceptance criterion

Julia layer can return the symbolic Jacobian of the vorticity RHS with respect to `Re`, verified
against a finite-difference approximation computed by the Python PINN layer.

---

## Decision 2 — Clojure as the Reasoning Layer

### Decision

Clojure is the implementation language for the reasoning layer. It uses two complementary
sub-systems:

- `core.logic` (miniKanren) for relational/logic inference rules over symbolic and operational
  predicates.
- `Datahike` with Datalog for entity-attribute-value structured storage and query.

The Clojure process runs on the JVM alongside the Scala backends. JVM placement enables direct
interop (no extra process hop) between Clojure reasoning and Scala service code where required.

### Rationale

**Why Clojure over Prolog or Python/Z3?**
Clojure provides an idiomatic Lisp on the JVM with a mature core.logic implementation of
miniKanren. Unlike Prolog, it integrates cleanly with the existing JVM ecosystem (Scala interop,
standard build tooling via `deps.edn`). Z3/Python SMT solvers are heavier-weight and are
oriented toward constraint satisfaction over bounded domains, not relational logic over dynamic
operational state.

**Why Datahike over raw Elasticsearch queries?**
Datahike's entity-attribute-value model gives the reasoning layer a stable, versioned, Datalog-
queryable view of system state. This eliminates the impedance mismatch between ES's document-
retrieval interface and the relational predicate structure that core.logic inference rules require.
ELK remains the raw event store; Datahike is a *projection* layer, not a replacement (see
Decision 3).

**Datalog as pivot point:**
Datalog is both the query language for Datahike and the structural substrate for core.logic
rules. This unification means that inference rules and structured queries share a single
representational vocabulary, eliminating translation overhead at the L2 internal boundary.

### Scope of Clojure reasoning layer

- `deps.edn` Clojure project
- `core.logic` rules: e.g., "backend X is healthy if the last N log events for X contain no
  `error`-level entries AND measured `latency_ms < threshold`"
- Datahike schema: EAV model for backend state, simulation runs, validation results
- Datalog queries over Datahike DB, unified with core.logic for hybrid logical queries
- JVM interop test: Clojure namespace callable from Scala (or via HTTP)

### Acceptance criterion

A `core.logic` query over a Datahike database correctly infers backend health state from
injected test events and returns well-formed EDN / JSON.

---

## Decision 3 — Log Data Bridge: ELK → Datahike ETL Projection

### Decision

ELK (Elasticsearch + Fluent Bit) remains the primary raw log event store (immutable, append-only,
full-fidelity). A lightweight ETL projection pipeline reads from ES, normalises events into the
Datahike EAV schema, and transacts them into Datahike. The reasoning layer queries *only*
Datahike, never ES directly.

### Architecture

```
GitHub Actions / Backends / Playwright
          │
          ▼
   Fluent Bit (:24224)
          │
          ▼
 Elasticsearch  ci-logs-*, test-results-*, db-slow-*
          │
     ETL bridge (Python script or Clojure consumer)
          │  reads ES, maps to EAV tuples
          ▼
    Datahike (Datalog fact store)
          │
     core.logic + Datalog queries
          ▼
   Reasoning results / inferences
```

### Rationale

**Separation of concerns:** ELK is optimised for high-throughput ingestion and full-text search
with time-series indexing. Datahike is optimised for structured, versioned, relational queries.
Conflating these into a single store would require either compromising ES's schema-free model
with rigid mappings or implementing a custom Datalog engine on top of Lucene — neither is
warranted for the current project scale.

**Query shape unification:** The bridge translates ES document fields into Datahike EAV
triples (entity=`session_id`, attribute=`level|app|latency_ms`, value=measured value). After
projection, both live backend state and historical log events are queryable via identical Datalog
predicate syntax.

**Projection is idempotent and re-runnable:** Events are keyed by ES `_id`. Re-running the ETL
pipeline against the same ES documents produces no duplicate facts in Datahike (Datahike's
transactional model handles upserts cleanly).

### MongoDB relationship

`vibedev.logs` (MongoDB, TTL 30d) is the runtime app log store for Node.js/React/Python. It is
*not* projected into Datahike in the initial implementation — only ES indices are bridged. MongoDB
remains the lightweight operational log sink; Datahike receives structured CI/test/diagnostic
projections from ES.

### Acceptance criterion

A Datalog query over Datahike correctly retrieves backend health facts derived from ingested
`test-results-*` ES events; results are equivalent to a direct ES `_search` against the same
documents (verified by a contract test).

---

## Decision 4 — Inter-Layer Contracts

### Decision

Three inter-layer communication paths are defined. Each has a primary mechanism and a permitted
fallback.

| Path | Primary | Fallback | Rationale |
|------|---------|----------|-----------|
| Julia ↔ Python (L1 ↔ PINN) | Julia REST sidecar (HTTP.jl, port 8601) | PyCall.jl | REST sidecar avoids Python GIL interaction and allows independent restart; PyCall.jl permitted for local dev smoke tests |
| Clojure ↔ Scala (L2 ↔ backends) | Direct JVM interop (Clojure calls Scala namespace) | HTTP over localhost | JVM colocation makes direct interop zero-overhead; HTTP fallback for service isolation during testing |
| Julia ↔ Clojure (L1 ↔ L2) | REST (Julia sidecar → Clojure HTTP endpoint) | Shared EDN file (dev only) | JVM and Julia run in separate runtimes; REST is the minimal stable boundary; EDN file permitted for local dev integration tests only |

### Contract surface definitions

**Julia REST sidecar (port 8601) — symbolic query API:**
```
GET  /symbolic/jacobian?equation=kh_vorticity&wrt=Re
     → { "expression": "<symbolic expr>", "evaluated_at": { "Re": 1000, "value": 3.14 } }

GET  /symbolic/constraint?equation=kh_vorticity&check=divergence_free
     → { "satisfied": true|false, "residual_norm": 0.0001 }
```

**Clojure HTTP endpoint (port 8700) — reasoning query API:**
```
POST /reason/backend-health
     body: { "backend": "kh-rust", "window_ms": 60000 }
     → { "healthy": true|false, "inferred_from": ["event-id-1", ...], "rule": "health-v1" }

POST /reason/query
     body: { "datalog": "[:find ?e :where [?e :backend/status :error]]" }
     → { "results": [[...], ...] }
```

**Data exchange format:** JSON over HTTP for all REST paths. EDN for Clojure-internal
representations (core.logic terms, Datahike transactions). Julia → Clojure payloads serialised
as JSON; Clojure deserialises to EDN before asserting into Datahike.

### Contract test requirements

Each inter-layer boundary requires at least one contract test (see SYMB-005):
- Julia sidecar returns valid JSON for `/symbolic/jacobian` with known KH parameters
- Clojure endpoint infers correct health state from injected synthetic events
- Julia → Clojure round-trip: symbolic constraint flag returned by Julia is correctly asserted
  as a Datahike fact by the ETL bridge and retrievable via Datalog

---

## Decision 5 — Port Allocation for New Services

### Decision

New symbolic/reasoning services are assigned dedicated ports in the 86xx–87xx range, contiguous
with the existing PINN service at 8600.

| Service | Port | Protocol | Status |
|---------|------|----------|--------|
| PINN Python FastAPI (existing) | 8600 | HTTP | Live — `pinn.test:8080 → :8600` |
| Julia symbolic sidecar (L1) | 8601 | HTTP | Reserved — SYMB-002 |
| Clojure reasoning HTTP API (L2) | 8700 | HTTP | Reserved — SYMB-003 |
| Datahike ETL bridge (L3 ingestion) | 8701 | HTTP (internal only) | Reserved — SYMB-004 |

### Rationale

- 86xx range keeps physics-layer services (PINN + Julia symbolic) co-located in the namespace.
- 87xx range separates JVM reasoning services (Clojure + ETL bridge) from physics services —
  reflecting the architectural tier boundary.
- Gap between 8601 and 8700 is intentional: 86xx may expand to additional Julia services
  (e.g., ModelingToolkit batch evaluator, AD harness) without encroaching on 87xx.
- All new ports must be registered in `_config/Start-LocalEnv.ps1` before SYMB-002 or SYMB-003
  are marked `in-progress`.

### Vhost pre-allocation

The Nginx vhost configuration (`kh-sim/vhost/*.conf`) already handles port-per-service routing
on :8080. New vhosts for `julia-symb.test` → `:8601` and `clj-reason.test` → `:8700` should be
added in SYMB-002 and SYMB-003 respectively, following the pattern established in KH-016.

---

## Dependency Graph

```
SYMB-001  ← this ADR (done)
    │
    ├── SYMB-002   Julia symbolic physics layer prototype
    │               depends_on: SYMB-001
    │
    ├── SYMB-003   Clojure reasoning + Datahike scaffold
    │               depends_on: SYMB-001
    │
    ├── SYMB-004   ELK → Datahike bridge (ETL)
    │               depends_on: SYMB-001, LOG-001
    │
    └── SYMB-005   Integration test — Julia ↔ Clojure contract
                    depends_on: SYMB-002, SYMB-003
```

---

## Open Items / Tech Debt

| Item | Detail | Owner |
|------|--------|-------|
| PyCall.jl version pinning | Verify PyCall compatibility with Python 3.11 (PINN env) before SYMB-002 starts | SYMB-002 |
| ES keyword mapping | `session_id` field needs explicit `keyword` mapping to avoid `.keyword` workaround in ETL bridge | LOG backlog |
| Fluent Bit per-index routing | Current catch-all output; per-prefix split (`ci-logs-*`, `test-results-*`, `db-slow-*`) needed before ETL bridge can rely on index routing | LOG backlog |
| Clojure + Scala JVM version alignment | Both must target JVM 17 (Scala already on Temurin 17 per CI); Clojure `deps.edn` should pin `:jvm-opts ["-source" "17"]` | SYMB-003 |
| EDN ↔ JSON round-trip fidelity | Clojure `cheshire` library handles JSON; verify `Long` vs `Double` type preservation for `duration_ms` and numeric fields from ES | SYMB-004 |

---

## References

| Document | Path |
|----------|------|
| PINN Architecture ADR | `infra/PINN-ARCHITECTURE.md` |
| Log Infrastructure Architecture | `infra/LOG-ARCHITECTURE.md` |
| Task registry | `TASKS-shared.yaml` — project block `symb-infra` |
| KH-016 vhost config | `kh-sim/vhost/*.conf` |
| LDE compose stack | `infra/docker/` |
| CI heartbeat workflow | `.github/workflows/ci-heartbeat.yml` |
