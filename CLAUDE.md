# CLAUDE.md — Session Context Restoration
**Project:** VibeCodeProjects workspace
**Owner:** Petr Zemla (petr.yamyang@gmail.com)
**Repo:** GitHub — MacBook + ThinkPad dual-device workflow
**Updated:** 2026-05-09 (CP-SUPIN-05 + Fourier weekend prep — `lege-artis` org confirmed, R-WORKSPACE-SURVEY-1 / KB-036 added to load order, ADR-05 R-COVERAGE-ZERO, Tracks 4+5 retroactive/planned, device matrix locked, delta-source `_config/CLAUDE-MD-DELTA-2026-05-09.md` ready for retirement)

> Read this file first at the start of every session.
> Then read the files listed under **§ LOAD ORDER** before touching any code.

---

## § PROJECT TOPOLOGY

### 3-fold-path — Primary active project
Three interdependent WordPress sites sharing a common theme base library:

| Site | Domain | Theme version (live) | Focus |
|------|--------|---------------------|-------|
| zemla | zemla.org | **v1.6.9** | Personal: psychology · buddhadharma · philosophy · blog · gallery · podcast |
| mim2000 | mim2000.cz | **v1.6.0** | Professional/practice: contacts · teaching · consulting |
| bodyterapie | bodyterapie.com | v1.2.0 *(v1.3.0 zip ready)* | Service: body therapy, booking, multilingual |

**Conceptual relationship (3-fold-path):**
- Mind → Psychology (Jung, Reich) + Philosophy/Science (physics, mathematics, epistemology)
- Spirit → Buddhadharma (Zen, Vajrayana)
- Body → bodyterapie.com (somatic work, body therapy)
- mim2000.cz bridges all three as the professional/teaching face

**Multilingual scope:** CS · EN · JA · DE · IT (all five on zemla; subset on mim2000/bodyterapie)

**Shared master data:** `inc/zemla-config.php` in each site's theme.
Contains: `ZEMLA_LINKEDIN_URL`, `ZEMLA_SLUG_*` nav constants, `ZEMLA_AUTHOR_NAME`, site URLs.
**Rule:** any value shared across sites lives ONLY in this file. No hard-coding in templates.

### lege-artis GitHub org — Canonical math/logical commons + MI-M-T core

**Confirmed 2026-05-09.** New GitHub organisation `lege-artis` hosts canonical math/logical commons + MI-M-T core repos. Naming: shibboleth (Latin "according to the law of the art") signals depth for those who recognise it, without obstructing those who don't.

| Repo | Purpose | Status |
|------|---------|--------|
| `lege-artis/mimt` | MI-M-T core (FastAPI service, 25-table schema, three deployment modes per OPUS-CYCLE §1.2) | NOT YET CREATED — packaged from `3-fold-path/code/mi_m_t/` at v0.2 → v0.3 transition |
| `lege-artis/fourier` | Canonical FFT/DFT/Partial-Sum reference (Fortran reference v0.1.0; Fortran + C++ + Rust + Pascal v0.2.0; mirrors kh-sim 4-language layout) | **PRIVATE bootstrap LIVE** at v0.0.1-bootstrap (2026-05-09); flips PUBLIC at v0.1.0 release. Sequencing locked 2026-05-09 Q3. |
| `lege-artis/kh-sim` | Sibling math-commons project (Kelvin-Helmholtz instability solver, Fortran reference, 8/8 TCs PASS) | LOCAL ONLY at `VibeCodeProjects/kh-sim/`; subtree-publishable to `lege-artis/kh-sim` when ready (pattern proven via fourier bootstrap; see `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md` revision needed for `--prefix=kh-sim` + subtree flow not transfer) |

**Org creation = GATE-PORT-1 — DONE 2026-05-09.** First public-mirror published via `git subtree push --prefix=fourier lege-artis-fourier main` from VibeCodeProjects monorepo. Pattern: private monorepo as source-of-truth, lege-artis/* repos as published-snapshots-at-version-boundaries.

**License stack across the org:**
- Code: Apache 2.0 (permissive + patent grant + §6 anti-endorsement clause)
- Documentation: CC-BY-SA-4.0 (attribution + share-alike for canonical/engineer doc tiers)
- Name protection: `TRADEMARK.md` + `NOTICE` declaring MIM2000™ / Improwave™ / Petr Yamyang non-licensed; reinforces Apache §6
- Voluntary funding: `.github/FUNDING.yml` with GitHub Sponsors + Patreon + PayPal.me (handles populated by Pete before first PUBLIC push)
- Trademark registration (CZ + EU): deferred until mim2000.cz redesign provides evidence-of-use (per OQ-PORT-2 lock 2026-05-09 sequencing)

**Central reference text across all backend tracks:** Numerical Recipes (Press, Teukolsky, Vetterling, Flannery) — 2007 3rd ed for general FFT recipes; 1986 Pascal edition is direct historical anchor for the Pascal track.

---

## § LOAD ORDER (read these before any work)

```
0.5. _config/SESSION-LIFECYCLE-SOP.md                              — MANDATORY: session lifecycle SOP (phases 1-5, daily smoke, restart gate)
0.6. _config/KB-LESSONS-LEARNED.yaml KB-036 (R-WORKSPACE-SURVEY-1) — MANDATORY: at session start, when uncertainty arises about portfolio state, when proposing structural decisions, when about to invent governance — ALWAYS first survey C:\Users\vitez\Documents\VibeCodeProjects (parent of all projects) for existing structures that may already address the question. Includes reading CLAUDE.md, MANIFEST.yaml, _config/* SOPs, OPUS-CYCLE-v0.2-MASTER.md, and active project folders. Failure mode prevented: reinventing existing infrastructure (the failure mode that produced retired SUPIN/archive/obsolete/portfolio-meta-v0.1/PORTFOLIO-META-v0.1-EN.md).
0. _config/KB-LESSONS-LEARNED.yaml                            — MANDATORY: cross-project KB, howtos, triage rules (read first)
1. MANIFEST.yaml                                              — live versions, pending releases, device state
2. TASKS-shared.yaml                                          — canonical task registry (80+ tasks)
3. 3-fold-path/backlog/PROJECT-PLAN-3fold-path-active-backlog.md  — sprint state + epic map
4. queue-macbook.yaml                                         — MacBook session queue (active/pending/done)
5. 3-fold-path/backlog/EPIC-ARCH-01-architecture-revision.md      — architecture epic (parked)
6. _config/GITHUB-TOKEN-POLICY.md                             — token blackout + budget rules
7. _config/SYNC-BYPASS-MACBOOK-TO-THINKPAD.md                 — inter-device sync without GitHub tokens
8. 3-fold-path/backlog/MI-M-T-POC-PROPOSAL.md                 — MI-M-T evidence system design
9. 3-fold-path/evidence/bugs.yaml                             — 17 bugs, schema v0.1.0
10. 3-fold-path/evidence/testcases.yaml                       — 15 test cases, 100% bug coverage
11. 3-fold-path/backlog/content-corrections.yaml              — CC-001..006 content/translation errors (CC-001..004 fixed in v1.6.9; CC-005 artifact-ready; CC-006 open)
12. _config/PROJECT-CLOSING-HOWTO.md                          — closing procedure checklist (run at project end)
13. 3-fold-path/backlog/MI-M-T-D03-JIRA-CONTRACT.md          — JIRA Cloud REST API v3 interface contract (bidirectional, v0.1.0)
14. 3-fold-path/backlog/MI-M-T-D04-POSTMAN-CONTRACT.md       — Postman/Newman interface contract (v0.1.0)
15. _config/CLAUDE-MD-DELTA-2026-05-09.md                    — DELETE after this merge confirms green; was the delta source for §lege-artis additions, ADR-05, Tracks 4+5, R-WORKSPACE-SURVEY-1
16. _config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md            — operational walkthrough for github.com/lege-artis org creation + repo migrations (NOTE: §3 "transfer" pattern superseded by `git subtree push --prefix=<dir>` workflow per 2026-05-09 empirical bootstrap of lege-artis/fourier)
17. 4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md — Fourier weekend kickoff bootstrap; first content under the previously-empty 4-step folder
```

**If working on a specific site:**
- zemla theme: read `RELEASE-TESTS.md` inside the theme zip before touching CSS/PHP
- mim2000 / bodyterapie: check their version in MANIFEST before applying any zemla patch

---

## § DEPLOYMENT RULE (2026-04-24 — REVISED TIER MODEL)

| Tier | Scope | Who | Method |
|------|-------|-----|--------|
| 1 | Complete theme zip (style.css + functions.php + all includes) | User | WP Admin → Themes → Upload |
| 2 | Non-theme changes (WP content, config, DB edits) | Claude | Active24 FTP / WP Admin browser session |

**Theme file changes** → build complete merged zip (base + ordered append blocks) → save to `theme-archives/` → user uploads via WP Admin.  
**Single-file patches** (e.g. TFE translations insert) → produce insert-ready artifact + `APPLY-*.md` guide → user applies via Theme File Editor.  
Credentials: `_config/credentials.yaml` (gitignored). Deploy guide: `_config/HOW-TO-ACTIVE24-DEPLOY.md`.

## § CURRENT STATE (as of 2026-05-09)

### Versions deployed
| Deliverable | Version | Status |
|------------|---------|--------|
| zemla-theme | **v1.7.4** | LIVE — HOTFIX-ZP-004: dual-init root cause fixed (inline script removed from single-zemla_episode.php) |
| mim2000 | **v1.6.0** | LIVE — deployed 2026-04-24 via Monsta FTP JS. LinkedIn URL live. |
| bodyterapie | **v1.3.0** | LIVE — deployed 2026-04-25 by user via WP Admin Upload |
| `lege-artis/fourier` | **v0.0.1-bootstrap** | PRIVATE — bootstrapped 2026-05-09 via subtree push. Flips PUBLIC at v0.1.0 (Fortran reference + golden vectors + dual-tier docs). |

### MI-M-T Python layer
| Deliverable | Version | Status |
|------------|---------|--------|
| mi_m_t/ FastAPI package | D-08 | **DONE** — SMK9 20/20 PASS (2026-04-30). 40 routes, SQLAlchemy 2.x async. |
| D-09 portability pass | — | **DONE** — MySQL 8: 29/29 + 20/20 PASS. PostgreSQL 14: 29/29 + 20/20 PASS (2026-05-02). |
| T5 /health DB probe | — | **DONE** — `main.py` async SELECT 1 probe; HTTP 503 on failure (2026-05-02). |
| T6 PHP route audit | — | **DONE** — `MI-M-T-PHP-ROUTE-AUDIT.md`; 5 gaps vs Python identified (2026-05-02). |
| T7 pytest suite | — | **DONE** — `tests/conftest.py` + `tests/test_smk9.py` (20 functions); 20/20 PASS (2026-05-02). |
| PoC-01 | — | **DONE** — testcases.yaml v2 (18 TCs, 0 orphans); Topology B run.py + Makefile; Opus v0.2 docs ingested. Pushed `3790ecd` (2026-05-03). |
| PoC-02 | — | **DONE** — Topology A: mimt-app/Dockerfile (multi-stage) + docker-compose.yml (3-container) + Makefile Docker targets + _config/RUNBOOK-DEVOPS.md (7 sections). A1–A5 matrix: DRY-RUN (Docker absent in sandbox — validate on ThinkPad). (2026-05-03). |
| PoC-03 | — | **DONE** — MI-M-T-D05-REDMINE-CONTRACT.md (11 sections, v0.1.0); OQ-100..OQ-103 raised. PoC-04 STOP gate: OQ-100 (org status names) + OQ-101 (instance URL/version) must be answered. (2026-05-03). |
| KH-01 | — | **DONE** — kh-sim community files: README.md, LICENSE (MIT), CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, .gitignore. kh-sim-public branch at 19d7eaa. OQ-300 raised (license confirm). Commits f15bec3 + 47dd769. (2026-05-03). |
| NUM-KH-FOR-01..04 | — | **DONE** — kh_constants/grid/fft + poisson/velocity + nonlinear (2/3 de-aliasing) + ETDRK4. ThinkPad VAL: 4/4 PASS near machine epsilon (2.0e-15 / 1.9e-15 / 5.7e-15 / 0.0). |
| NUM-KH-FOR-05..08 | — | **DONE** — diagnostics + io + solver + main + reference + convergence test. ThinkPad VAL: 8/8 PASS, all near machine epsilon. Reference implementation complete. (2026-05-04). |
| D-10 | — | **DONE (DRY-RUN)** — `public_html/migrate.php` (HTTP entry, env bridge) + `deploy/.env.production` + `deploy/RUNBOOK-ACTIVE24-D10.md` (10 sections) + `deploy/active24-bundle.zip` (80K: 29 SQL + runner.php + full PHP app). Validate on ThinkPad with Active24 credentials. (2026-05-04). |

### Tracks added 2026-05-09 (CP-SUPIN-05 close + Fourier kickoff)

| Track | Owner | Status | Pointer |
|-------|-------|--------|---------|
| Track 4 — SUPIN/Bouračka MI-M-T methodology proof-points | ThinkPad (Opus) + Sonnet branches | **ACTIVE retroactive** (Q1 lock 2026-05-09) — CP-SUPIN-05 v0.5.x in flight; cross-framework parity work landed via `cp-supin-05-cross-framework-parity` branch on `petr-yamyang/bouracka-tests`; Selenium 5P/5S baseline; Cypress BUG-CY-001 parked with Round-4 IPC-114 evidence. Methodology patterns surfaced eligible for export to MI-M-T core: two-book Excel (TestPlan + TES with generated coverage sheets), drift-aware test-skip patterns, IPC-114 Chromium diagnostic methodology, IOC-aware email-deliverable packaging. | `SUPIN/bouracka-tests/SESSION-CLOSE-CP-SUPIN-05-2026-05-09-STATUS.md` + `_config/HANDOVER-V0.2-THINKPAD.md` (existing template) |
| Track 5 — `lege-artis/fourier` weekend kickoff | ThinkPad (Opus authoring + Sonnet implementing once Stage 3 closes per R-SONNET-1) | **BOOTSTRAP LIVE 2026-05-09** at v0.0.1-bootstrap (private during dev). Working spec at `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md`; bootstrap plan at `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md`; weekend Stage 1 (bibliography + canonical equations) ready to start. **Sequencing (Q3 lock 2026-05-09):** v0.1.0 Fortran reference; v0.2.0 adds C++ performance + Rust experimental + Pascal full-scale (mirrors kh-sim's four-language layout); v0.5.0+ stretch goals (GPU bridge, REST microservice form). Numerical Recipes (1986 Pascal edition + 2007 3rd ed) elevated as central reference. | `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` |

### Next pending applies
| ID | Target | Action |
|----|--------|--------|
| GH-UPL-05 | GitHub Releases | Upload bodyterapie-theme-v1.3.0.zip — zip present at theme-archives/ |
| GH-UPL-08 | GitHub Releases | Upload zemla-theme-v1.7.2.zip — zip present at theme-archives/ |
| GH-UPL-10 | GitHub Releases | Upload zemla-theme-v1.7.3.zip — zip found in theme-archives/ 2026-05-01 |
| GH-UPL-04/06/07 | GitHub Releases | **DEFERRED** — v1.6.9/v1.7.0/v1.7.1 zips not in local archive; superseded by v1.7.4 |

### LinkedIn URL (confirmed 2026-04-24)
`https://www.linkedin.com/in/petr-zemla-75ab675/`
Applied to: mim2000 functions.php (live) + zemla `inc/zemla-config.php` + bodyterapie functions.php (both in v1.6.9 / v1.3.0 zips).

### Open / active after 2026-05-09 session
| ID | Title | Priority | Status | Device |
|----|-------|----------|--------|--------|
| THEMEPORT-03-APPLY | Upload bodyterapie-theme-v1.3.0.zip via WP Admin | P1 | **ZIP READY** — user action required | User |
| CC-005-APPLY | Apply v1.7.0 translations patch to zemla inc/translations.php | P2 | **Artifact ready** at `releases/v1.7.0-zemla/` — TFE apply required | User |
| CC-006 | Add 5 ZEMLA_SLUG_* constants + update page-dao.php/page-psychology.php | P3 | Open — fix in next planned theme version | MacBook |
| CREDENTIALS | Fill WP Admin FILL_IN_* passwords in `_config/credentials.yaml` | P2 | Active24 filled; WP Admin passwords for all 3 sites still needed | User |
| MI-M-T-P06 | First testrun mim2000 CEO blog | P2 | Pending | ThinkPad |
| MI-M-T-P07 | Lessons learned | P3 | Pending | ThinkPad |
| PIL-07 | Run pilot podcast harness on ep00 real stems | P2 | Requires stems in podcast/suche-kosti/ep00/raw/ | MacBook |
| ARCH-E01 | Architecture revision epic (incl. bodyterapie blog BUG-015) | P2 | **Parked** — see epic doc | — |
| MOB-E01 | Mobile optimization bodyterapie.com | P3 | Blocked until ARCH-E01 | — |
| GH-UPL-04/05 | Upload theme zips (v1.6.9, v1.3.0) to GitHub Releases | P2 | unblocked (token policy Phase 2) | MacBook |
| AUTH-004 | OAuth2.0 WP SSO plugin | P3 | Not started | MacBook |
| FOURIER-S1 | Fourier weekend Stage 1 — bibliography + canonical equations | P1 | unblocked — `lege-artis/fourier` bootstrap LIVE | ThinkPad |

### GitHub token policy
- **Phase 1 (now → 2026-05-01):** No tokens. All local, manual sync between devices.
- **Phase 2 (May 1+):** ~800 tokens/month. Batch pushes at session boundaries.
- Details: `_config/GITHUB-TOKEN-POLICY.md`

### MI-M-T PoC branch ownership
- **ThinkPad** = primary for MI-M-T deploy infra + coding
- **MacBook** = seeding phase (P01–P05 artefacts, committed)
- Evidence data lives at `3-fold-path/evidence/` — needs manual transfer to ThinkPad before P06

---

## § KEY ARCHITECTURAL DECISIONS (ADRs)

### ADR-01: Single config file for shared identity data
**Decision:** `inc/zemla-config.php` is the master component for all data shared across sites.
**Constraint:** Never hard-code `linkedin.com`, nav slugs, author name, or site URLs in any template.
**Enforcement:** `RELEASE-TESTS.md §7` includes grep command: `grep -rn "linkedin\.com" . --include="*.php" | grep -v zemla-config.php` → must return zero.

### ADR-02: Gallery layout — sidebar wrapper pattern
**Decision:** `.gallery-layout` must always have exactly 2 direct children: `<aside class="gallery-sidebar">` + `.album-grid`.
**Reason:** CSS `grid-template-columns: 220px 1fr` breaks if 3+ direct children are auto-placed.

### ADR-03: Album card — vertical layout
**Decision:** Cards are vertical (image top, 3:2 aspect ratio, text below) not horizontal.
**Reason:** UX review: horizontal placed description to the right of the photograph, not below the title.

### ADR-04: Translation strings — all `_e()` calls must be in translation tables
**Enforcement:** Before any release, run: `grep -o "_e(\s*'[^']*'" page-templates/page-physics-dof.php | sed ... | sort` and cross-check against `inc/translations.php`. Zero missing = pass.

### ADR-05: R-COVERAGE-ZERO — algebraic integrity check on the 6-element-chain
**Decision (2026-05-09).** The 6-element-chain (Stakeholder → Requirement → TT → TC → TR → Evidence per OPUS-CYCLE §2.2) is the canonical traceability data contract across MI-M-T case studies. Integrity of this chain — no orphan TC, no orphan Req, no dead-end chain, no unjustified redundancy — is mandatorily verified at every TestPlan revision before release-candidate declaration. The check is named **R-COVERAGE-ZERO** ("Round Zero coverage audit").

**Algebra.** Relation algebra over finite sets: composition (R∘TT∘TC = end-to-end coverage), projection (which Reqs have at least one TC?), complement (orphans = elements in domain not in projection), transitive closure, symmetric-difference characterisation of orphans.

**Implementation.** Pure-function library; lives initially as a module in `lege-artis/math-commons` (or directly inside `lege-artis/mimt`); extracted to `lege-artis/coverage-algebra` when first non-MI-M-T consumer appears. Each consumer (Bouračka, Fourier, future case study) imports via standard package mechanics; no copy-paste.

**Two-tier docs (per shibboleth aesthetic):**
- Canonical: `docs/canonical/coverage-algebra-formal.md` — relation algebra formalism, theorems with proofs, citations to Tarski / relation calculus textbook
- Engineer: `docs/engineer/coverage-algebra-howto.md` — "open your TestPlan, look at this column, here's what the tool flags" with worked examples

**Output materialisation.** Plain-value Excel sheets generated from canonical TestPlan sheets — no Excel formulas (per the priority-matrix bug lesson — Bouračka v0.4.2 priority formula was wrong for half the matrix because Excel-side IF-ladder was hand-edited; same failure mode prevented for coverage). Generated sheets live inside the TES (TestExecutionSummary) workbook per the two-book Excel convention adopted for SUPIN/Bouračka.

**First proving ground.** Fourier (clean inputs: mathematical properties as Reqs, algorithm × precision × language × property as TT, golden-vector + property + cross-language tests as TC). Once validated, back-port to Bouračka v0.5.2.

---

## § ARCHITECTURE DEFICIT (scope for ARCH-E01)

Identified 2026-04-01. The 3-fold-path has no shared design pattern library.
Specific deficits:

1. **Page template duplication** — zemla, mim2000, bodyterapie each have full copies of templates with no inheritance hierarchy
2. **Cross-content linkage** — albums, blog posts, podcast episodes, philosophy pages have no systematic linking strategy. Only `_album_related_url` (just added) covers one direction.
3. **CSS token inconsistency** — `--gallery-cols`, `--gallery-gap`, `--content-width` are unset on mim2000 and bodyterapie (noted in GAL-D01 report). `zemla-config.php` covers PHP constants but CSS design tokens have no equivalent master.
4. **No shared navigation taxonomy** — each site has its own page structure; cross-domain navigation/linking is ad-hoc
5. **Release process gap** — `RELEASE-TESTS.md` exists on zemla only; mim2000 and bodyterapie have no equivalent

Full scope: `3-fold-path/backlog/EPIC-ARCH-01-architecture-revision.md`

---

## § TASK ID CONVENTIONS

```
GAL-*      Gallery-related tasks
MOB-*      Mobile optimization
Z-*        zemla.org specific
M-*        mim2000.cz specific
B-*        bodyterapie.com specific
ARCH-*     Architecture revision epic
GH-*       GitHub operations
GEN-*      Generic/workspace tasks
GW-*       Git workflow tasks
MI-M-T-*   4-step-noble-steps-to-MI-M-T project
FOURIER-*  lege-artis/fourier project (added 2026-05-09)
```

---

## § DEVICE MATRIX (locked 2026-05-09)

| Device | Owner | Cowork | Personal projects | SUPIN-only projects |
|--------|-------|--------|-------------------|---------------------|
| ThinkPad (Pete personal) | Pete | Opus master + Sonnet branches | ✓ all (3-fold-path, lege-artis/*, MI-M-T core, pavel-50, Improwave, kh-sim) | ✓ all (SUPIN/Bouračka authoring) |
| MacBook (Pete personal) | Pete | Opus analytical + Sonnet branches | ✓ all | ✓ all (SUPIN/Bouračka analytical, methodology export) |
| HP Elite SUPNB001 (SUPIN-owned, intranet, no Cowork) | SUPIN | ✗ never (SUPIN security policy) | ✗ forbidden by ownership policy | ✓ runtime target only — receives email-shipped automation packages, runs them, returns results JSON |

**Rule.** No Cowork session ever runs on HP Elite. No personal / `lege-artis/*` / Fourier / kh-sim work ever lives on HP Elite. SUPNB001 is exclusively the SUPIN testing runtime target. See `SUPIN/bouracka-tests/_specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md` for the IOC-aware packaging convention. See `_config/DEVICES.md` for full device-specific rules and per-device session ergonomics.

**Cross-device sync.** GitHub remains canonical source of truth across personal devices (ThinkPad ↔ MacBook). HP Elite never pulls from GitHub directly (SUPIN network egress restrictions); it only receives scanner-clean email packages.

---

## § HANDOFF BLOCK — 2026-05-09 (CP-SUPIN-05 close + Fourier bootstrap)
**Last session:** 2026-05-09 (extended — workspace mount expanded; existing infra surveyed; PORTFOLIO-META v0.1 retired; CLAUDE-MD-DELTA-2026-05-09.md authored + merged into this CLAUDE.md; lege-artis/fourier bootstrapped private at v0.0.1-bootstrap)
**Closed because:** Fourier weekend Stage 1 ready to start; CP-SUPIN-05 work parked with BUG-CY-001 evidence-captured-fix-deferred; full-portfolio governance updated.
**Restart reads:** CLAUDE.md (this file, now merged) → `_config/SESSION-LIFECYCLE-SOP.md` → `_config/KB-LESSONS-LEARNED.yaml` (KB-036 R-WORKSPACE-SURVEY-1 mandatory) → `MANIFEST.yaml` → relevant project session-close docs.
**Delivered 2026-05-09 (governance):**
- `_config/CLAUDE-MD-DELTA-2026-05-09.md` — delta source (now merged; this file ready for retirement at next Phase 4)
- `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md` — operational walkthrough (NOTE: needs minor update — `--prefix=fourier` not `--prefix=lege-artis/fourier`; transfer pattern for kh-sim superseded by subtree-push pattern)
- `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` — first content under previously-empty 4-step folder
- `_config/KB-LESSONS-LEARNED.yaml` + `_config/KB-LESSONS-LEARNED-OPUS-v0.2.yaml` — KB-036 R-WORKSPACE-SURVEY-1 entries appended
- `SUPIN/archive/obsolete/portfolio-meta-v0.1/PORTFOLIO-META-v0.1-EN.md` + `RETIREMENT-NOTE.md` — retired predecessor doc
- `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` — locked Apache 2.0 + CC-BY-SA-4.0 + TRADEMARK + Pascal v0.2.0 sequencing
**Delivered 2026-05-09 (lege-artis/fourier bootstrap):**
- `lege-artis` GitHub org created (private)
- `lege-artis/fourier` empty repo created (private)
- `VibeCodeProjects/fourier/` subdirectory created with full bootstrap content (LICENSE Apache 2.0, LICENSE-DOCS CC-BY-SA-4.0, NOTICE, TRADEMARK.md, README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, .gitignore, .github/FUNDING.yml, _specs/WORKING-SPEC-v0.2-EN.md, multi-backend directory tree)
- Subtree-push to `lege-artis/fourier` (15 objects, 19.95 KiB) tagged `v0.0.1-bootstrap`
- Pattern empirically validated: private VibeCodeProjects monorepo as source-of-truth, lege-artis/* repos as published-snapshots-at-version-boundaries via `git subtree split` + push
**Open / active:**
- FOURIER-S1 — bibliography + canonical equations (Stage 1 of WORKING-SPEC v0.2, ready to start in `VibeCodeProjects/fourier/shared/reference-bibliography/` + `shared/canonical-equations/`)
- BUG-CY-001 — parked with Round-4 IPC-114 evidence; same-origin persistent connection hypothesis; next diagnostic = headed Cypress + Network DevTools
- VibeCodeProjects monorepo commit pending — captures today's other work (delta + KB + retirement + bootstrap docs); Pete authors per next-session guidance
- LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md needs `--prefix=fourier` correction + subtree-not-transfer pattern note
**NUM-KH-FOR-08 + D-10 carried forward (prior):**
- `kh-sim/backends/fortran/tests/test_num_004_convergence.f90` — TC-NUM-KH-004: Richardson dt-halving (4 levels), rate ≥ 1.2; 8/8 TCs PASS
- `3-fold-path/code/deploy/active24-bundle.zip` — D-10 dry-run; validate on ThinkPad with real Active24 credentials
**KH-01 (earlier):** community files + kh-sim-public branch at `19d7eaa` (local-only; subtree-publishable to `lege-artis/kh-sim` per same pattern as fourier when ready)
**PoC-04 STOP gate:** OQ-100 (org status names) + OQ-101 (instance URL/version) — must be answered before next iteration; see `3-fold-path/backlog/MI-M-T-D05-REDMINE-CONTRACT.md` v0.1.0 §11.
rsion) — must be answered before next iteration; see `3-fold-path/backlog/MI-M-T-D05-REDMINE-CONTRACT.md` v0.1.0 §11.
