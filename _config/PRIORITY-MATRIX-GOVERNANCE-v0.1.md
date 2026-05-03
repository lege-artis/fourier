# Priority Matrix Governance + Automation-Tool Docking + Claude-Specific Mode 3 — v0.1
## The 3 final pre-handover guidelines locked in one place

**Version:** v0.1.0
**Authority:** This doc adds three project-wide governance items the user mandated 2026-05-03:
1. **Priority Matrix governance** (§1) — Severity × Urgency → Priority; applied to every OQ, iteration, and deliverable.
2. **Automation-tool docking strategy** (§2) — Postman / SoapUI / Playwright / Newman / etc. dock to MI-M-T from early stage; strict governance; tool-agnostic.
3. **Mode 3 LLM-TDD interface = Claude Code + CoWork specifically** (§3) — supersedes the generic LLM-bridge sketch in `_config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` §4.3.

**Audience:** every Sonnet session from this point onward; every prior strategic doc that uses "priority", "severity", "OQ" must be reinterpreted through §1 of this manual.

---

## §1. Priority Matrix Governance (binding, project-wide)

### 1.1 The matrix (locked)

Two inputs, one output. Each takes the values **A / B / C / D**:

| Code | Numeric | Severity meaning | Urgency meaning |
|:----:|:-------:|------------------|-----------------|
| A | 1 | Major | Major |
| B | 2 | Standard | Standard |
| C | 3 | Minor | Minor |
| D | undef | Not yet defined | Not yet defined |

**Priority is computed as the sum of Severity + Urgency numeric values:**

| Severity + Urgency = N | Priority |
|:----------------------:|:--------:|
| 2 (1+1) | **A** |
| 3 (1+2 or 2+1) | **A** |
| 4 (1+3, 2+2, 3+1) | **B** |
| 5 (2+3, 3+2) | **C** |
| 6 (3+3) | **C** |
| any dimension = D | **D** (not yet defined) |

### 1.2 Visual matrix

```
                           SEVERITY
                    A=1     B=2     C=3     D=undef
              ┌─────┬───────┬───────┬───────┬───────┐
        A=1   │  A  │   A   │   A   │   B   │   D   │
              ├─────┼───────┼───────┼───────┼───────┤
URGENCY B=2   │     │   A   │   B   │   C   │   D   │
              ├─────┼───────┼───────┼───────┼───────┤
        C=3   │     │   B   │   C   │   C   │   D   │
              ├─────┼───────┼───────┼───────┼───────┤
        D=ud  │     │   D   │   D   │   D   │   D   │
              └─────┴───────┴───────┴───────┴───────┘
```

**Distribution check:** of 9 defined cells, 3 are A, 3 are B, 3 are C — balanced.

### 1.3 Application rules

**R-PR-1** Every **Open Question (OQ-NNN)** gets the triplet `severity=X / urgency=Y / priority=Z` written into its body where Z is computed via §1.1. Sonnet sessions append OQs in this format from now on. Existing OQs are re-tagged in the migration table (§1.5 below).

**R-PR-2** Every **iteration** (PoC-NN, PHYS-NN, NUM-XX-YY, MIM-NN, PHIL-NN, KH-NN, GRX-NN) carries a Priority assigned at planning time. Used for ordering when multiple iterations are parallel-eligible.

**R-PR-3** Every **deliverable** (a physical file: doc, migration, theme zip, Sonnet-shipped artifact) carries a Priority based on the iteration it ships in.

**R-PR-4** **D = Not yet defined** is **not** "low" — it means "needs Opus or user to define before priority can be computed". A D-priority item blocks if it's on the critical path; it doesn't block if it's parallelizable.

**R-PR-5** Sonnet **may not** raise an item from C to A (or B to A) without an OQ-NNN bouncing back to Opus / user. Lowering is OK if an iteration completes faster than expected and resources free up.

**R-PR-6** **Reporting:** every session-close `SESSION-NOTES` block must include a 1-line "Priority distribution worked this session: <count by code>" summary.

### 1.4 Where to record Severity + Urgency for each thing

- **OQs:** in the OQ template (§1.6 below) — already structured.
- **Iterations:** in the iteration row of the relevant scope doc (§7 of master plan, §10 of POC scope, etc.); add columns `Sev` `Urg` `Pri` to existing iteration tables in next session pass — see §1.5 retro-tagging table.
- **MI-M-T entities:** the existing `severity_confirmed` + `priority_confirmed` columns in `users` table become **deprecated**; new columns `severity_field` (A/B/C/D) and `urgency_field` (A/B/C/D) are introduced in a v0.2.1 migration; `priority_field` is **derived** (not stored — computed in app layer per §1.1). Migration: `111_replace_severity_priority_with_sev_urg_pri.sql`. The CAST 4-value enum (A/B/C/X) maps to (A/B/C/D) by `X→D`.

### 1.5 Retro-tagging table (existing OQs + iterations)

> Sonnet sessions update this table as they touch each item. First pass is done here (Opus best-effort).

**Open Questions — retro-tagged:**

| OQ | Title | Severity | Urgency | **Priority** |
|----|-------|:--------:|:-------:|:------------:|
| OQ-100 | Org Redmine workflow status names | B | A | A |
| OQ-101 | Proprietary SOAP/REST script invocation convention | B | A | A |
| OQ-102 | DevOps Linux distro target | C | C | C |
| OQ-103 | Org-permitted secret-management | B | C | C |
| OQ-104 | Backup retention policy | C | C | C |
| OQ-105 | Port 8080 OK on org infra | C | C | C |
| OQ-200 | mim2000 slug strategy (/projects vs /projects-services) | C | B | C |
| OQ-201 | Show empty cards before public repos? | C | A | B |
| OQ-202 | Translation completeness DE/IT/JA | C | C | C |
| OQ-203 | Screenshot/visual asset for cards | C | C | C |
| OQ-300 | License choice (MIT vs Apache-2.0) | C | A | B |
| OQ-301 | Existing CI workflow auth secrets in public mode | A | A | A |
| OQ-302 | KH-VAL ship now or defer | C | B | C |
| OQ-303 | LinkedIn copy tone | C | C | C |
| OQ-PHYS-01 | physics-first_examples repo home for KH/GR/Ising? | C | B | C |
| OQ-PHYS-02 | SymPy vs Symbolics.jl for GR | B | B | B |
| OQ-PHYS-03 | ED-only vs SSE-QMC for 2D TFIM | C | C | C |
| OQ-PHYS-04 | Public-repo timing for physics-gr / physics-ising | C | C | C |
| OQ-PHYS-05 | Add 2 cards (GR + Ising) now or wait? | B | A | A |
| OQ-PHYS-06 | LinkedIn narrative — combined or separate posts | C | C | C |
| OQ-PHIL-01 | DOM read of /philosophy/ | B | A | A |
| OQ-PHIL-02 | Other seeders deserve hooks too? | C | B | C |
| OQ-PHIL-03 | Translation priority CS+EN sufficient? | B | B | B |
| OQ-PHIL-04 | OG image source | C | C | C |
| OQ-PHIL-05 | Method notes pages — author now? | C | C | C |
| OQ-PHIL-06 | Math + Epistemology calibration treatment | C | C | C |
| OQ-NUM-01 | FFT lib (FFTW3 vs FFTPACK 5.1) — license | B | A | A |
| OQ-NUM-02 | Pascal gRPC support — REST-only acceptable? | C | C | C |
| OQ-NUM-03 | NetCDF vs HDF5 for file dump | C | B | C |
| OQ-NUM-04 | OpenMP for Fortran inner loops | C | C | C |
| OQ-NUM-05 | Single canonical recipe vs recipe family | C | B | C |
| OQ-NUM-06 | Pascal/C validation gate decision authority | B | C | C |
| OQ-NUM-07 | symbolica fallback to FFI-SymPy for Kerr | C | B | C |
| OQ-NUM-08 | SSE QMC v0.2 or defer to v0.2.x | C | C | C |
| OQ-GRX-01 | Font file source of truth | C | A | B |
| OQ-GRX-02 | Single design-tokens.css across all sites? | A | A | A |
| OQ-GRX-03 | Sandstone opacity 0.30 vs alternatives | C | B | C |
| OQ-GRX-04 | bodyterapie nav simplification entries | C | B | C |
| OQ-GRX-05 | Inter on Czech glyphs at all sizes | B | B | B |
| OQ-GRX-06 | Light-mode-only or include dark-mode mapping | C | C | C |

**Critical-path Priority A items** (these block other work):
- OQ-100 (Redmine status mapping — blocks PoC-04)
- OQ-101 (script invocation — blocks PoC-06)
- OQ-301 (kh-sim CI auth secrets — blocks Track 3 KH-03 visibility flip)
- OQ-PHYS-05 (add 2 physics cards now — blocks MIM-01 closure)
- OQ-PHIL-01 (DOM read — blocks PHIL-02)
- OQ-NUM-01 (FFT licensing — blocks public release of any port)
- OQ-GRX-02 (single design-tokens source) — blocks ALL theme + frontend work

**Iterations — first-pass Priority assignment** (Sonnet refines per session):

| Iteration | Sev | Urg | **Pri** | Notes |
|-----------|:---:|:---:|:-------:|-------|
| PoC-01 | A | A | A | First Stage 0 deliverable; testcases v2 + Topology B entrypoint |
| PoC-02 | A | A | A | Dockerfile + RUNBOOK; DevOps colleague hand-off blocker |
| PoC-03 | B | A | A | Redmine contract |
| PoC-04 | B | A | A | Redmine adapter; gates Mode 2 demo |
| PoC-05 | B | B | B | Playwright |
| PoC-06 | B | B | B | SOAP/REST runners |
| PoC-07/08 | A | B | A | TestCase UI — JIRA-inspired centerpiece |
| PoC-09 | B | B | B | Test cycle UI |
| PoC-10 | A | B | A | Issue tracking + Redmine round-trip |
| PoC-11 | B | C | C | Basic reporting |
| PoC-12 | A | C | B | Hooks + Mode 3 happy path |
| PoC-13 | B | D | D | Stage 1 readiness audit (urgency depends on Mon/Tue specs) |
| MIM-01 | B | A | A | mim2000 Alpha + tokens + GRX-MIM merged |
| MIM-02 | B | A | A | Theme build |
| MIM-03 | B | B | B | Tier 1 deploy |
| PHIL-01 | B | A | A | DOM verification |
| PHIL-02 | B | A | A | Theme v1.7.6 build |
| PHIL-03 | B | B | B | Tier 1 deploy |
| PHIL-04A/B/C | C | C | C | Triggered JSON updates |
| KH-01 | B | C | C | kh-sim audit |
| KH-02 | C | B | C | LinkedIn copy |
| PHYS-KH-01 | B | B | B | KH calibration suite |
| PHYS-GR-01 | B | C | C | Minkowski + Schwarzschild |
| PHYS-GR-02 | B | C | C | Kerr |
| PHYS-IS-01 | C | C | C | Classical Ising |
| PHYS-IS-02 | C | C | C | Quantum TFIM |
| NUM-KH-FOR-01..09 | A | B | A | Fortran reference watermark for KH |
| NUM-KH-RUST-01..09 | B | B | B | Rust port |
| NUM-KH-SCALA-01..09 | B | C | C | Scala port |
| NUM-KH-PASCAL/CGCC | C | D | D | Gated; urgency undefined until validation |
| NUM-GR-PY-01..05 | A | B | A | SymPy canonical for GR |
| NUM-IS-FOR-01..09 | A | B | A | Fortran reference for Ising |
| GRX-01 | A | A | A | Design tokens + fonts (blocks everything visual) |
| GRX-02 | A | A | A | Self-host fonts |
| GRX-MIM-01 | B | A | A | mim2000 v1.10.0 (merged with MIM-02) |
| GRX-MIM-02 | B | B | B | Tier 1 deploy mim2000 |
| GRX-BOD-01 | C | B | C | bodyterapie v1.8.0 |
| GRX-BOD-02 | C | C | C | Tier 1 deploy bodyterapie |
| GRX-PHYSICS-01-* | B | B | B | Physics frontend skeletons (3 models) |
| GRX-MIMT-01 | A | B | A | MI-M-T frontend (centerpiece) |

### 1.6 OQ template — updated for Priority Matrix

```markdown
## OQ-NNN — <one-line subject>
**Date:** YYYY-MM-DD
**Session:** <iter-id>
**Discovered by:** ThinkPad Sonnet | MacBook Sonnet | Opus | User
**Severity:** A (major) | B (standard) | C (minor) | D (undefined)
**Urgency:** A (major) | B (standard) | C (minor) | D (undefined)
**Priority (computed):** A | B | C | D
**Affects:** <list of input docs / sections / iterations>

### Context
<what you were doing when the question arose>

### Question
<the actual question>

### Candidate answers
- **A1.** <option> — pros / cons
- **A2.** <option> — pros / cons

### Recommended next step
<what Opus / user / next-Sonnet should do>
```

### 1.7 Sorting + filtering rule for SESSION-NOTES summaries

`SESSION-NOTES` summary lines now read like:

```
2026-05-04 PoC-01 closed: green | OQs opened: 2 (highest A) | priority distribution: A=1, B=1
```

Sonnet can sort the OPEN-QUESTIONS-LOG by priority via `grep` on the `**Priority:**` line.

---

## §2. Automation-Tool Docking Strategy (binding, project-wide)

### 2.1 Why this matters now

The user mandate (2026-05-03):
> "Automation tools like SoapUI, Postman, Playwright etc. which will execute on demand automated testsuites must be docked to whole solution from early stage ⇒ architecture must now reflect how to integrate this tools easily and be strictly governed and respond to MI-M-T."

Without an explicit docking strategy now, each adapter (PostmanAdapter, PlaywrightAdapter, SoapTestAdapter, RestTestAdapter, plus future ones — k6, JMeter, Robot Framework, ...) will accrete inconsistent shapes — making the system harder to maintain and harder to extend to new tools.

This section locks the **docking contract** that every automation-tool adapter must satisfy from PoC-05 onward.

### 2.2 The docking contract (binding)

Every "automation-tool adapter" (anything that executes a test suite and feeds results back to MI-M-T) implements **the same `ScriptRunnerAdapter` contract** — already defined in MI-M-T-V0.2-POC-ONPREM-SCOPE.md §4.4 — extended here:

```python
# mi_m_t/adapters/_script_runner_contract.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

@dataclass
class ScriptDescriptor:
    """Discovered automation-test artefact found on filesystem."""
    adapter_name: str          # 'postman', 'soapui', 'playwright', 'newman', ...
    path: Path
    item_code_hint: str        # filename-derived; user can override
    descr_hint: str            # first-line/comment-derived
    detected_runtime: str      # 'newman 6.0.0', 'playwright 1.42.0', ...

@dataclass
class ScriptResult:
    verdict: str               # 'pass' | 'fail' | 'skip' | 'blocked' | 'partial'
    actual: str                # human-readable
    evidence_path: Path | None # screenshot / log / trace / report file
    duration_ms: int
    exit_code: int
    raw_stdout: str
    raw_stderr: str
    sub_results: list["ScriptResult"]   # nested (e.g. each Postman test in a collection)

class ScriptRunnerAdapter(ABC):
    """Every automation-tool adapter implements this."""

    name: str                  # 'postman' | 'soapui' | 'playwright' | ...
    detected_runtime: str      # set during health()

    @abstractmethod
    async def health(self) -> bool:
        """Confirm tool runtime is installed + invocable. Sets detected_runtime."""

    @abstractmethod
    async def discover(self, root_path: Path) -> list[ScriptDescriptor]:
        """Walk filesystem; return descriptors of unregistered scripts."""

    @abstractmethod
    async def execute(self,
                       script_path: Path,
                       test_data: dict | None,
                       env: dict | None) -> ScriptResult:
        """Run a registered script with optional test data + env."""

    @abstractmethod
    async def stream_execute(self,
                              script_path: Path,
                              test_data: dict | None,
                              env: dict | None) -> AsyncIterator[ScriptResult]:
        """As execute() but yields sub-results as they complete (for the
           WebSocket frontend). Optional — adapters may raise NotImplementedError."""

    @abstractmethod
    async def cancel(self, run_id: str) -> bool:
        """Cancel an in-flight run. Best-effort."""

    @abstractmethod
    def manifest(self) -> dict:
        """Return adapter manifest:
           { name, version, supported_extensions, supported_features,
             runtime_requirements, license, docs_url }"""
```

### 2.3 Plugin discovery (so MI-M-T finds adapters at start-up)

Adapters register via Python entry-points (PEP 621) — package `pyproject.toml`:

```toml
[project.entry-points."mi_m_t.script_runners"]
postman    = "mi_m_t.adapters.newman:NewmanAdapter"
soapui     = "mi_m_t.adapters.soapui:SoapUIAdapter"
playwright = "mi_m_t.adapters.playwright:PlaywrightAdapter"
rest       = "mi_m_t.adapters.rest_runner:RestRunnerAdapter"
soap       = "mi_m_t.adapters.soap_runner:SoapRunnerAdapter"
# Future: k6, jmeter, robotframework, cypress, ...
```

MI-M-T discovers adapters at start-up via:
```python
from importlib.metadata import entry_points
runners = {ep.name: ep.load()() for ep in entry_points(group="mi_m_t.script_runners")}
```

This means **adding a new tool = ship a new package implementing the contract + register the entry-point**. No core MI-M-T change. This is the "open to different tools from now onwards" guarantee the user mandated.

### 2.4 The 5 adapters in v0.2 + planned for v0.3

| Adapter | Tool | Status v0.2 | Notes |
|---------|------|-------------|-------|
| `newman` | Postman / Newman CLI | **DONE** (D-04) | Reference adapter; review against §2.2 contract; add manifest() if missing |
| `playwright` | Playwright | **NEW** PoC-05 | Per MI-M-T-V0.2-POC-ONPREM-SCOPE §4.3 |
| `rest_runner` | Generic REST script (org proprietary) | **NEW** PoC-06a | Per §4.4 |
| `soap_runner` | Generic SOAP script (org proprietary) | **NEW** PoC-06b | Per §4.4 |
| `soapui` | SoapUI Pro/OSS | **NEW** PoC-06c | NEW ITEM v0.2.3; runs `.xml` projects via SoapUI testrunner CLI |
| `k6` | Grafana k6 (load testing) | v0.3 | Stretch — load tests for MI-M-T API itself |
| `jmeter` | Apache JMeter | v0.3 | Stretch |
| `robot` | Robot Framework | v0.3 | Stretch |

### 2.5 Strict governance for adapter PRs

Every adapter PR must:
1. Implement all 5 abstract methods of `ScriptRunnerAdapter`.
2. Pass a generic conformance test suite `tests/test_adapter_conformance.py` that calls every method on a fixture script.
3. Carry adapter-specific replay smoke tests (mirror D03 / D04 pattern).
4. Document in `mi_m_t/adapters/<name>/README.md`: runtime requirements, license, supported file formats, known limitations.
5. Be tagged in `MANIFEST.yaml` `automation_adapters` block with name + version + status.

Sonnet may not merge an adapter PR that misses any of these.

### 2.6 Frontend surface for adapters (consistent UI)

MI-M-T frontend (per Graphics Manual §7) auto-discovers adapters via `GET /api/v1/adapters` and renders:
- Adapter dropdown on the test-script execute form (label = `manifest.name`; subtitle = `detected_runtime`).
- Adapter health badge on each script row (green / red dot per `health()` result, refreshed periodically).
- "Adapter manifest" link from each script detail page.

### 2.7 Iteration plan additions for docking

| Iteration | Owner | Goal |
|-----------|-------|------|
| **DOCK-01** | ThinkPad | Author `mi_m_t/adapters/_script_runner_contract.py` per §2.2; refactor existing `NewmanAdapter` + `JiraAdapter` (where applicable) to subclass the new ABC; add conformance test suite |
| **DOCK-02** | ThinkPad | SoapUI adapter (`mi_m_t/adapters/soapui.py`); ships in PoC-06 alongside SOAP/REST runners |
| **DOCK-03** (post-v0.2) | ThinkPad | Adapter SDK doc (`mi_m_t/adapters/SDK.md`) — how third parties write a new adapter |

DOCK-01 is **Priority A** (blocks the entire automation-tool track from being well-governed) and runs **before** PoC-05 / PoC-06.

---

## §3. Mode 3 — Claude-specific LLM-TDD interface

### 3.1 What changes

The `_config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` §4.3 sketched a generic LLM-bridge. Per user direction: **for v0.2 / v0.3, Mode 3 = Claude only, accessed via Claude Code (CLI) or CoWork (desktop).** No generic LLM provider abstraction at this stage.

**Why this matters:**
- The Testbase Context schema can be tuned to what Claude consumes well (system + user prompt structure, file-attachment patterns, tool-use conventions).
- Bring-Your-Own-LLM stays as v0.4+ plumbing; v0.2 / v0.3 don't waste cycles on it.
- The hand-off between MI-M-T and Claude is a *file-and-shell* contract — exactly what Claude Code + CoWork operate on natively.

### 3.2 Two integration paths (binding for v0.2.x / v0.3)

**Path A — Claude Code (CLI; ThinkPad-friendly, scriptable)**

```
ThinkPad Sonnet (Mode 3 PoC-12 / future MI-M-T runs)
└── 1. Operator (or MI-M-T) runs:
        mimt llm export --tt TT-005 --out /tmp/testbase-context-001/
└── 2. The export dir contains:
        ├── README.md                  (LLM-facing overview; "Your task is...")
        ├── testbase.json              (the structured Testbase Context per §3.4 schema)
        ├── requirements.md            (REQs in human-readable form)
        ├── test_targets.md            (TT in human-readable form)
        ├── test_cases.md              (TC in human-readable form)
        ├── seed_data/                 (test_data + environment seeds; deterministic)
        │   ├── fixture_001.json
        │   └── ...
        └── prior_results.md           (recent test runs, if any)
└── 3. Operator opens Claude Code in /tmp/testbase-context-001/
        and types: "Read README.md and proceed."
└── 4. Claude Code reads → produces code suggestions → user reviews + applies
└── 5. Operator runs:
        mimt llm import-results --run-id <id> --code-diff /tmp/code-diff.patch
└── 6. MI-M-T runs the test cases against the new code; results feed back
        into MI-M-T as a normal TestRun + TestRunResults
```

**Path B — CoWork (desktop; MacBook-friendly, conversational)**

```
MacBook user (Mode 3 v0.3)
└── 1. User opens CoWork (desktop app); points at the project folder
        VibeCodeProjects/3-fold-path/
└── 2. User runs the same export from Path A or via a CoWork skill:
        Skill: "mimt-export-testbase-context"
        Args: --tt TT-005 --out ./mode3/testbase-001/
└── 3. CoWork now has the testbase folder mounted; conversation begins:
        User: "Read mode3/testbase-001/README.md and propose code changes."
        Claude: <reads, proposes, applies via Edit/Write tools>
└── 4. CoWork-applied code is committed (CoWork has git access)
└── 5. MI-M-T runs the test cases; feedback loop closes
```

### 3.3 Why both paths

- **Claude Code** is the right tool for headless / batch / scriptable runs (CI integration; nightly TDD passes).
- **CoWork** is the right tool for interactive / exploratory / human-in-the-loop sessions (architect + Claude + MI-M-T forming a triad).

Both paths consume the **same** Testbase Context contract (§3.4) — only the front-end client differs.

### 3.4 Testbase Context schema (refined for Claude consumption)

```yaml
# testbase.json (or .yaml; Claude prefers either)
testbase_context_version: "0.1.1"      # bump on schema change
schema_url: "https://mim2000.cz/specs/testbase-context-v0.1.1.json"

generated_at: "2026-MM-DDTHH:MM:SSZ"
generated_by: "mi_m_t v0.2.x"

# ── What this context is FOR ────────────────────────────────────────────
purpose: |
  Short paragraph. Plain English. What the LLM should accomplish.
  Example: "Generate code that makes test cases TC-005..TC-008 pass.
  The cases test the podcast player (test target TT-005). Existing
  implementation file is page-templates/zp-engine.js. Do not change
  the test data or environment seeds."

# ── HARD CONSTRAINTS (LLM must NOT violate) ─────────────────────────────
hard_constraints:
  - id: "HC-001"
    rule: "Do not modify any file in seed_data/ or environment_seeds/"
    rationale: "These are deterministic inputs; changing them invalidates calibration."
  - id: "HC-002"
    rule: "All new code must be reviewable; no minified or obfuscated output."
  - id: "HC-003"
    rule: "Outbound HTTPS calls inside a database transaction are forbidden."
  - id: "HC-004"
    rule: "Use canonical types (ARCH-SPEC §0.3); no engine-specific syntax."

# ── SCOPE (what the LLM should touch) ───────────────────────────────────
scope:
  test_target_refs: ["TT-005"]
  primary_files:
    - path: "page-templates/zp-engine.js"
      reason: "implementation under test"
    - path: "page-templates/single-zemla_episode.php"
      reason: "DOM the JS reads from"
  reference_files:
    - path: "page-templates/page-physics-dof.php"
      reason: "stylistic + structural reference for similar code"

# ── REQUIREMENTS (acceptance language) ──────────────────────────────────
requirements:
  - id: REQ-005
    title: "Podcast player must initialise exactly once per page load"
    acceptance_criteria:
      - "Given a fresh single-episode page load, when JS executes, then
         exactly one Audio element is created."
      - "Given the same page already with an Audio element, when init
         is re-invoked, then no second element is created."

# ── TEST CASES (the executable contract) ────────────────────────────────
test_cases:
  - id: TC-001
    title: "Player init creates exactly one Audio element"
    test_target_ref: TT-005
    requirement_ref: REQ-005
    phases:
      - phase_type: pre
        description: "Load page; capture initial DOM"
      - phase_type: exec
        description: "Run zp-engine.js init"
      - phase_type: post
        description: "Count document.querySelectorAll('audio').length"
    expected: "audio count = 1"

# ── TEST DATA (deterministic seeds) ─────────────────────────────────────
test_data:
  - id: TD-005-01
    payload_path: "seed_data/locked-user-fixture.json"
    description: "Locked user account fixture (constant)"

# ── ENVIRONMENT SEEDS ───────────────────────────────────────────────────
environment_seeds:
  - id: TE-001
    description: "Staging — ThinkPad LDE"
    base_url: "http://localhost:8080"
    capabilities: ["javascript", "dom", "fetch"]

# ── PRIOR RESULTS (recent runs; LLM may use as hints) ───────────────────
prior_results:
  - test_case_ref: TC-001
    last_run_date: "2026-04-30T11:00:00Z"
    last_verdict: "fail"
    last_actual: "audio count = 2 (double-init regression)"
    notes: "BUG-018 — root cause: inline <script> initPlayer block in single-zemla_episode.php was creating Audio #2 before engine fired."

# ── OUTPUT EXPECTATIONS (how Claude should respond) ─────────────────────
output_format:
  preferred: "unified_diff"            # or 'full_file' or 'narrative'
  follow_up_test_run: "yes"            # if 'yes', expect MI-M-T to run TCs after applying

# ── METADATA + INTROSPECTION ────────────────────────────────────────────
metadata:
  project_id: 1
  project_code: "MIMT"
  generated_recipe_path: "recipes/tt-005-podcast-init.toml"
  reference_hash: "sha256:abc123..."   # for reproducibility
```

### 3.5 The `mimt llm` CLI (Claude Code-friendly)

```
mimt llm export             --tt TT-NNN [--include-prior-results] --out <dir>
mimt llm export-batch       --reqs REQ-* --out <dir>
mimt llm validate-context   <dir>          # schema check
mimt llm import-results     --run-id <id> --code-diff <patch>
mimt llm dry-run            <dir>          # render the LLM-facing prompt without sending
```

Implemented in PoC-12 per the OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM iteration.

### 3.6 What Claude needs that off-the-shelf LLMs don't

This contract is tuned to Claude's strengths:

- **File-first**: Claude Code + CoWork operate on local files with Read/Edit/Write tools — the Testbase folder is a natural unit.
- **Markdown overview** (`README.md`) plus structured JSON — Claude reads both well; the markdown gives it conversational anchor, the JSON gives it deterministic data.
- **Hard constraints as numbered list with rationale** — Claude respects this format and cites it back.
- **Bounded scope (`scope.primary_files` + `scope.reference_files`)** — keeps the agent from drifting into unrelated parts of the repo.
- **Output format directive (`unified_diff`)** — Claude produces these well; downstream tooling (`git apply`) handles them natively.

### 3.7 What stays out of v0.2.x scope

- Multi-LLM provider abstraction (BYOL pattern) — v0.4+.
- Automated LLM invocation from MI-M-T (no API keys in v0.2.x; human stays in the loop).
- Cost / token budget tracking — out of scope.
- Multi-turn context management — Claude Code + CoWork handle this themselves.

---

## §4. Cross-cutting impact on existing docs (apply on next pass)

These docs need light edits to reference §1 / §2 / §3 above. Edits are queued for the next pass — Sonnet may apply when touching the doc for an iteration:

| Doc | Edit needed |
|-----|-------------|
| `_config/OPUS-CYCLE-v0.2-MASTER.md` | Add §0.6 pointer: "Priority Matrix per `PRIORITY-MATRIX-GOVERNANCE-v0.1.md`" |
| `_config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` | Replace §4.3 LLM-bridge sketch with pointer to §3 of this doc |
| `3-fold-path/backlog/MI-M-T-V0.2-POC-ONPREM-SCOPE.md` | §4 (script runners) — add pointer to §2 docking contract; add SoapUI as fifth adapter |
| `3-fold-path/backlog/OPEN-QUESTIONS-LOG.md` | Apply §1.5 retro-tagging to all existing OQs |
| `_config/HANDOVER-V0.2-THINKPAD.md` and `MACBOOK.md` | Add Step "0a — Read PRIORITY-MATRIX-GOVERNANCE before any decision" |
| `_config/PHYSICS-NUMERICAL-METHODS-v0.1.md` | Apply §1 priority to Iteration plan §8 (already partial — verify) |
| `3-fold-path/backlog/PHYSICS-CALIBRATION-MODELS-v0.1.md` | Apply §1 priority |
| `3-fold-path/backlog/MIM2000-ALPHA-V0.2.md` | Apply §1 priority |
| `3-fold-path/backlog/ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md` | Apply §1 priority |
| `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` | Apply §1 priority |
| `_config/OPUS-NEXT-SESSION-TRIGGERS.md` | Add column "Priority" to §2 ranked Opus sessions |

---

## §5. Status footer

| Item | Value |
|------|-------|
| Document | `PRIORITY-MATRIX-GOVERNANCE-v0.1.md` |
| Output position | `_config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md` |
| Sections | 3 mandates + cross-cutting impact + status |
| OQs retro-tagged | 41 |
| Iterations retro-tagged | ~45 |
| Critical-path Priority A items | 7 |
| Adapter contract methods | 5 (health, discover, execute, stream_execute, cancel) + manifest |
| Mode 3 paths | 2 (Claude Code + CoWork) |
| Status | v0.1 — binding from this point onward |

---

*PRIORITY-MATRIX-GOVERNANCE-v0.1.md — 2026-05-03 — MacBook CoWork session — Opus*
