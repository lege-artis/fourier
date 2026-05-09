# CLAUDE.md additive delta — 2026-05-09

> **Purpose.** Pete reviews this delta, then merges into canonical `CLAUDE.md` during the next Phase 4 (per `SESSION-LIFECYCLE-SOP.md`). Delta is **additive** — does not modify existing CLAUDE.md sections, only proposes new content blocks and one rule reference. Each block below specifies its insertion point in CLAUDE.md.
>
> **Authoring session.** Cowork-Opus on ThinkPad, 2026-05-09. Triggered by R-WORKSPACE-SURVEY-1 (KB-036) discovery of duplicated infrastructure in retired PORTFOLIO-META-v0.1.
>
> **Status.** Draft for review.

---

## Delta 1 — Add R-WORKSPACE-SURVEY-1 to load order section

**Insertion point.** `CLAUDE.md § LOAD ORDER`, immediately after item 0.5 (`SESSION-LIFECYCLE-SOP.md`).

**Add as item 0.6:**

```markdown
0.6. _config/KB-LESSONS-LEARNED.yaml KB-036 (R-WORKSPACE-SURVEY-1) — MANDATORY: at session start, when uncertainty arises about portfolio state, when proposing structural decisions, when about to invent governance — ALWAYS first survey C:\Users\vitez\Documents\VibeCodeProjects (parent of all projects) for existing structures that may already address the question. Includes reading CLAUDE.md, MANIFEST.yaml, _config/* SOPs, OPUS-CYCLE-v0.2-MASTER.md, and the active project folders. Failure to do this leads to reinventing existing infrastructure (the failure mode that produced retired PORTFOLIO-META v0.1).
```

**Rationale.** Without this rule, future Cowork sessions opened with sub-folder mount (e.g. SUPIN/ only) repeat the same failure mode.

---

## Delta 2 — Add `lege-artis` GitHub org to project topology

**Insertion point.** `CLAUDE.md § PROJECT TOPOLOGY`, after the existing 3-fold-path table, as a new subsection.

**Add subsection:**

```markdown
### lege-artis GitHub org — Canonical math/logical commons + MI-M-T core

**Confirmed 2026-05-09.** New GitHub organisation `lege-artis` hosts canonical
math/logical commons + MI-M-T core repos. Naming: shibboleth (Latin "according
to the law of the art") signals the depth signal for those who recognise it,
without obstructing those who don't.

| Repo | Purpose | Status |
|------|---------|--------|
| `lege-artis/mimt` | MI-M-T core (FastAPI service, 25-table schema, three deployment modes per OPUS-CYCLE §1.2) | NOT YET CREATED — packaged from `3-fold-path/code/mi_m_t/` at v0.2 → v0.3 transition |
| `lege-artis/fourier` | Canonical FFT/DFT/Partial-Sum reference (Fortran/C++/Rust parallel implementation; sibling to kh-sim pattern) | NOT YET CREATED — bootstrapped from `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` and `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` |
| `lege-artis/kh-sim` | Migrated from `petr-yamyang/kh-sim` (Kelvin-Helmholtz instability solver, Fortran reference, 8/8 TCs PASS) | MIGRATION PENDING — see `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md` |

**Org creation = GATE-PORT-1 (high priority).** Pete's manual action on
github.com — sign in as petr-yamyang → top-right `+` → New organisation →
"Free" plan → org name `lege-artis` → confirm. ~3-minute action.
Blocks all three repo moves until done.

**License stack across the org:**
- Code: Apache 2.0 (permissive + patent grant + §6 anti-endorsement clause)
- Documentation: CC-BY-SA-4.0 (attribution + share-alike for canonical/engineer
  doc tiers)
- Name protection: `TRADEMARK.md` + `NOTICE` declaring MIM2000™ / Improwave™ /
  Petr Yamyang non-licensed; reinforces Apache §6
- Voluntary funding: `.github/FUNDING.yml` with GitHub Sponsors + Patreon +
  PayPal.me handles (populated by Pete before first push)
- Trademark registration: deferred until mim2000.cz redesign provides
  evidence-of-use (couples cleanly per filing strategy)
```

---

## Delta 3 — Add new track entries under OPUS-CYCLE v0.2 → v0.3 transition

**Insertion point.** `CLAUDE.md § CURRENT STATE`, as a new subsection after the existing MI-M-T Python layer table.

**Add subsection:**

```markdown
### Tracks added 2026-05-09 (CP-SUPIN-05 close + Fourier kickoff)

| Track | Owner | Status | Pointer |
|-------|-------|--------|---------|
| Track 4 — SUPIN/Bouračka MI-M-T methodology proof-points | ThinkPad (Opus) + Sonnet branches | ACTIVE — CP-SUPIN-05 v0.5.x in flight; cross-framework parity work landed via `cp-supin-05-cross-framework-parity` branch on `petr-yamyang/bouracka-tests`; Selenium 5P/5S baseline; Cypress BUG-CY-001 parked with Round-4 IPC-114 evidence | `SUPIN/bouracka-tests/SESSION-CLOSE-CP-SUPIN-05-2026-05-09-STATUS.md` + `_config/HANDOVER-V0.2-THINKPAD.md` (existing template) |
| Track 5 — `lege-artis/fourier` weekend kickoff | ThinkPad (Opus authoring + Sonnet implementing once Stage 3 closes) | PLANNED — working spec authored at `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md`; bootstrapping plan at `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md`; weekend Stage 1 (bibliography + canonical equations) ready to start. **Sequencing (per 2026-05-09 Q3 lock):** v0.1.0 Fortran reference; v0.2.0 adds C++ performance + Rust experimental + Pascal full-scale (mirrors kh-sim four-language layout); v0.5.0+ stretch goals (GPU bridge, REST microservice form). Numerical Recipes (1986 Pascal edition + 2007 3rd ed) elevated as central reference. | `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` |

**Track 4 is retroactive** — work has been ongoing since 2026-05-04; this
documents it inside the cycle rather than continuing as undeclared
external engagement. MI-M-T methodology patterns surfaced from Bouračka work
that deserve formalisation: two-book Excel convention (TestPlan + TES with
generated coverage sheets), drift-aware test-skip patterns, IPC-114 Chromium
diagnostic methodology, email-deliverable IOC-aware packaging.

**Track 5 starts after** GATE-PORT-1 (org creation) closes. Existing kh-sim
pattern reused: `backends/<lang>/src/`, `backends/<lang>/tests/`, community-pack
from kh-sim's KH-01 deliverables, MIT-equivalent license stack via Apache 2.0.
```

---

## Delta 4 — Add HP Elite SUPNB001 to device matrix

**Insertion point.** Reference to `_config/DEVICES.md` (which needs separate update with the same content). For now, add brief note in `CLAUDE.md § HANDOFF BLOCK` template section so any session knows:

**Add note (before HANDOFF BLOCK template):**

```markdown
### Device awareness — three-device topology

| Device | Owner | Cowork | Personal projects | SUPIN-only projects |
|--------|-------|--------|-------------------|---------------------|
| ThinkPad (Pete personal) | Pete | Opus master + Sonnet branches | ✓ all | ✓ all |
| MacBook (Pete personal) | Pete | Opus analytical + Sonnet branches | ✓ all | ✓ all |
| HP Elite SUPNB001 (SUPIN-owned, intranet, no Cowork) | SUPIN | ✗ never | ✗ forbidden by ownership policy | ✓ runtime target only — receives email-shipped automation packages, runs them, returns results JSON |

**Rule.** No Cowork session ever runs on HP Elite. No personal/`lege-artis`/Fourier/
kh-sim work ever lives on HP Elite. SUPNB001 is exclusively the SUPIN testing
runtime target. See `_specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md` (under
`SUPIN/bouracka-tests/_specs/`) for the IOC-aware packaging convention.
```

---

## Delta 5 — Reference R-COVERAGE-ZERO label for the 6-element-chain integrity check

**Insertion point.** `CLAUDE.md § KEY ARCHITECTURAL DECISIONS (ADRs)`, as new ADR-05.

**Add as ADR-05:**

```markdown
### ADR-05: R-COVERAGE-ZERO — algebraic integrity check on the 6-element-chain

**Decision (2026-05-09).** The 6-element-chain (Stakeholder → Requirement →
TT → TC → TR → Evidence per OPUS-CYCLE §2.2) is the canonical traceability
data contract across MI-M-T case studies. The integrity of this chain — no
orphan TC, no orphan Req, no dead-end chain, no unjustified redundancy — is
mandatorily verified at every TestPlan revision before release-candidate
declaration. The check is named **R-COVERAGE-ZERO** ("Round Zero coverage
audit").

**Algebra.** Relation algebra over finite sets: composition (R∘TT∘TC =
end-to-end coverage), projection (which Reqs have at least one TC?),
complement (orphans = elements in domain not in projection), transitive
closure, symmetric-difference characterisation of orphans.

**Implementation.** Pure-function library; lives initially as a module in
`lege-artis/math-commons` (or directly inside `lege-artis/mimt`); extracted
to `lege-artis/coverage-algebra` when first non-MI-M-T consumer appears.
Each consumer (Bouračka, Fourier, future case study) imports via standard
package mechanics; no copy-paste.

**Two-tier docs (per shibboleth aesthetic):**
- Canonical: `docs/canonical/coverage-algebra-formal.md` — relation algebra
  formalism, theorems with proofs, citations to Tarski / relation calculus
  textbook
- Engineer: `docs/engineer/coverage-algebra-howto.md` — "open your TestPlan,
  look at this column, here's what the tool flags" with worked examples

**Output materialisation.** Plain-value Excel sheets generated from canonical
TestPlan sheets — no Excel formulas (per the priority-matrix bug lesson —
Bouračka v0.4.2 priority formula was wrong for half the matrix because
Excel-side IF-ladder was hand-edited; same failure mode prevented for
coverage). Generated sheets live inside the TES (TestExecutionSummary)
workbook per the two-book Excel convention adopted for SUPIN/Bouračka.

**First proving ground.** Fourier (clean inputs: mathematical properties as
Reqs, algorithm × precision × language × property as TT, golden-vector +
property + cross-language tests as TC). Once validated, back-port to Bouračka
v0.5.2.
```

---

## Delta 6 — Update load order with new pointers

**Insertion point.** Append to existing `CLAUDE.md § LOAD ORDER` block, after item 14 (currently the last).

**Add items 15-17:**

```markdown
15. `_config/CLAUDE-MD-DELTA-2026-05-09.md`              — this file (DELETE after merging into CLAUDE.md proper at next Phase 4)
16. `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md`      — operational walkthrough for github.com/lege-artis org creation + repo migrations
17. `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` — Fourier weekend kickoff bootstrap + first content under the previously-empty 4-step folder
```

---

## Delta 7 — Note for next Phase 4 review

**When merging this delta into CLAUDE.md:**

1. Apply Delta 1 (R-WORKSPACE-SURVEY-1 to load order) **first** — it's the highest-leverage rule.
2. Apply Delta 2 (`lege-artis` org topology) — needs to be in PROJECT TOPOLOGY section right after 3-fold-path.
3. Apply Delta 3 (Track 4 + Track 5) — adds to CURRENT STATE.
4. Apply Delta 4 (device matrix) — adds before HANDOFF BLOCK section.
5. Apply Delta 5 (ADR-05 R-COVERAGE-ZERO) — appends to ADRs.
6. Apply Delta 6 (load order updates) — at the end.
7. Bump `CLAUDE.md` "Updated:" line to `2026-05-09 (CP-SUPIN-05 + Fourier weekend prep — lege-artis org locked, R-WORKSPACE-SURVEY-1, ADR-05 R-COVERAGE-ZERO, Tracks 4+5 added)`.
8. Delete this delta file (`_config/CLAUDE-MD-DELTA-2026-05-09.md`) after merge — it has no purpose post-merge.
9. Commit + push to GitHub. MacBook pulls on next session start to receive the same.

**Estimated merge effort.** ~15 minutes. All deltas are additive — no existing CLAUDE.md content needs to be removed or rewritten.

---

## §10. Decisions locked 2026-05-09 chat thread

The following Q1-Q5 + T1-T3 + M1-M2 decisions are now binding for this delta and downstream docs:

| Q/T/M | Decision | Affects |
|---|---|---|
| **Q1** | SUPIN/Bouračka declared as **Track 4 retroactive** of OPUS-CYCLE v0.2 → v0.3. Engagement formalised inside the cycle as MI-M-T methodology proof-point. Patterns eligible for export to MI-M-T core: two-book Excel, drift-aware test-skip, IPC-114 diagnostic methodology, IOC-aware packaging. | Delta 3 unchanged |
| **Q2** | Stage 1 canonical-equations files: **dual-format** (`.md` with embedded LaTeX + parallel `.tex` companion) under `shared/canonical-equations/` of `lege-artis/fourier`. Markdown for inline GitHub rendering; `.tex` for proper math typesetting (MathJax/KaTeX/LaTeX→PDF). Honors WORKING-SPEC v0.2 §11.1 Q-FFP-8 Markdown lock while preserving canonical-tier rigor. | Bootstrap doc §3.2 |
| **Q3** | **Pascal added as fourth language** for `lege-artis/fourier`. Sequencing: v0.1.0 = Fortran reference only; v0.2.0 = Fortran + C++ performance + Rust experimental + **Pascal full-scale**. Numerical Recipes (Press et al.) elevated as central reference material across all four tracks; the 1986 Pascal edition is direct historical anchor for the Pascal track. | Bootstrap doc §1, §4; Track 5 entry in Delta 3 |
| **Q4** | **Pete runs the bootstrap manually** — splits into: (a) manual GitHub UI for org + repo creation, (b) PowerShell script for clone + community-pack mirror + commit + push. First-commit ceremony preserves Pete's authorial signature on the public OSS repo. | Migration plan §4.2 |
| **Q5** | **Pre-flight availability check** added to migration plan §3 as new step 0: visit `https://github.com/lege-artis/kh-sim` before transfer, verify 404 (no squatted name), abort transfer if conflict found. | Migration plan §3 |
| **T1** | R-WORKSPACE-SURVEY-1 placement at item **0.6** in CLAUDE.md load order (between SESSION-LIFECYCLE-SOP at 0.5 and KB-LESSONS-LEARNED at 1) — adjacent to docs it references. | Delta 1 unchanged |
| **T2** | Migration plan §3.1 step 4 wording on kh-sim transfer: leave as-is. | No change |
| **T3** | Bibliography (`shared/reference-bibliography/refs.bib`) ordered alphabetically by citation key per academic standard. Numerical Recipes 3rd ed key: `NumRec3rd`; Pascal-edition cross-reference noted in entry comment. | Bootstrap doc §3.1, T3 footnote |
| **M1+M2** | This delta document is the **consistent merge artefact** Pete reviews before applying to canonical CLAUDE.md. Pete merges at his next Phase 4 cycle (~15 min editorial; instructions in Delta 7). After merge, this file is deleted per Delta 7 step 8. Conversation thread does not directly edit CLAUDE.md — that's Pete's deliberate single-author action when he's ready. | This file's status flag |

**Track 5 entry update (per Q3 decision).** Modify Delta 3 Track 5 row to add: *"Sequencing: v0.1.0 Fortran reference; v0.2.0 adds C++ performance + Rust experimental + Pascal full-scale (per 2026-05-09 lock); v0.5.0+ stretch goals incl. GPU bridge, REST microservice form."* Delta 3 stays additive; this is an inline annotation rather than a new delta.

---

## Status

| Item | Value |
|---|---|
| Doc | `_config/CLAUDE-MD-DELTA-2026-05-09.md` |
| Date | 2026-05-09 |
| Trigger | KB-036 / R-WORKSPACE-SURVEY-1 discovery |
| Companion docs | `_config/KB-LESSONS-LEARNED.yaml` (KB-036), `_config/KB-LESSONS-LEARNED-OPUS-v0.2.yaml` (KB-036), `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md` (drafted next), `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` (drafted next), `SUPIN/archive/obsolete/portfolio-meta-v0.1/RETIREMENT-NOTE.md` (retired source) |
| Status | Draft — awaiting Pete's review and merge |
