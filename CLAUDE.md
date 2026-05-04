# CLAUDE.md — Session Context Restoration
**Project:** VibeCodeProjects workspace
**Owner:** Petr Zemla (petr.yamyang@gmail.com)
**Repo:** GitHub — MacBook + ThinkPad dual-device workflow
**Updated:** 2026-04-25 (CoWork sessions 2026-04-24/25 — v1.6.9 live; mim2000 v1.6.0 live; CC-005 artifact; ADR scans; tier model; credentials)

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

---

## § LOAD ORDER (read these before any work)

```
0.5. _config/SESSION-LIFECYCLE-SOP.md                              — MANDATORY: session lifecycle SOP (phases 1-5, daily smoke, restart gate)
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

## § CURRENT STATE (as of 2026-05-03)

### Versions deployed
| Deliverable | Version | Status |
|------------|---------|--------|
| zemla-theme | **v1.7.4** | LIVE — HOTFIX-ZP-004: dual-init root cause fixed (inline script removed from single-zemla_episode.php) |
| mim2000 | **v1.6.0** | LIVE — deployed 2026-04-24 via Monsta FTP JS. LinkedIn URL live. |
| bodyterapie | **v1.3.0** | LIVE — deployed 2026-04-25 by user via WP Admin Upload |

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
| NUM-KH-FOR-01 | — | **DONE** — kh_constants.f90 + kh_grid.f90 + kh_fft.f90 + TC-NUM-KH-001 test. DRY-RUN (gfortran absent in sandbox). Compile+run on ThinkPad. Commit b68d4e7. (2026-05-03). |
| NUM-KH-FOR-02 | — | **DONE** — kh_poisson.f90 + kh_velocity.f90 + TC-NUM-KH-002. DRY-RUN. Commit 3cfeb8b. (2026-05-03). |
| NUM-KH-FOR-03 | — | **DONE** — kh_nonlinear.f90 (nonlinear RHS + 2/3 de-aliasing) + TC-NUM-KH-005. DRY-RUN. Commit 2374290. (2026-05-03). |
| NUM-KH-FOR-04 | — | **DONE** — kh_etdrk4.f90 (Cox-Matthews 2002 ETDRK4) + TC-NUM-KH-003 (linear scalar). DRY-RUN. Commit 83e926e. (2026-05-03). |
| NUM-KH-VAL | — | **PASS 4/4** — TC-001 2.0e-15, TC-002 1.9e-15, TC-003 5.7e-15, TC-005 0.0 (exact). All near machine epsilon. ThinkPad gfortran validated 2026-05-03. |
| NUM-KH-FOR-05 | — | **DONE** — kh_diagnostics.f90 (KE/enstrophy/max_vort/div_rms) + kh_io.f90 (namelist reader + JSON writer) + TC-NUM-KH-007 (energy conservation, inviscid, 500 steps). DRY-RUN. (2026-05-04). |

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

### Resolved (2026-04-01 session — zemla only)
| ID | Title | Resolution |
|----|-------|------------|
| Z-11 | Gallery full-width — root cause | `.gallery-sidebar` wrapper fix |
| Z-12 | Physics DoF language mismatch | 33 strings added to `inc/translations.php` |
| Z-13 | Gallery card vertical layout | Vertical (image-top, text-below), 3:2 aspect |
| Z-14 | Album related link meta box | `_album_related_url` + `_album_related_label` post meta |
| A-01 | LinkedIn wrong profile | `ZEMLA_LINKEDIN_URL` corrected in `zemla-config.php` |
| A-02 | Footer `/dao/` 404 | Slug corrected via `ZEMLA_SLUG_PHILOSOPHY` |
| A-03 | `/about/` page 404 | `about` added to `zemla_required_pages()` |
| ARCH | Master data component | `inc/zemla-config.php` created |
| REL | Release test matrix | `RELEASE-TESTS.md` created inside theme |

### Delivered (2026-04-12 + 2026-04-16 sessions — pipeline + evidence)
| ID | Title | Resolution |
|----|-------|------------|
| PIL-02..06 | Podcast pipeline T0→T4 | Complete harness: ingest → backbone gate → boundary check → assembler → mix overlay → E2E smoke |
| MI-M-T-P01 | Evidence directory + schema | `3-fold-path/evidence/` — bugs.yaml schema v0.1.0 |
| MI-M-T-P02 | Seed bugs.yaml | 17 bugs across 3 sites (zemla 8, mim2000 6, bodyterapie 2, cross-site 1) |
| MI-M-T-P03 | Seed testcases.yaml | 15 manual test cases, 100% bug coverage |
| MI-M-T-P04 | triage.py CLI | Filter/sort by site, severity, priority, status, component + matrix view |
| MI-M-T-P05 | evidence-report.py | MkDocs markdown exporter (5 section modes + site filter) |
| Z-15/Z-16 | Podcast template bug reports | Formal defect report + fix plan (Option A approved for Z-16 custom player) |
| CONT-01..04 | Content correction track | Registered in TASKS-shared.yaml |

### Delivered (2026-04-17 session part 1 — hotfix artifacts + WP content fixes)
| ID | Title | Resolution |
|----|-------|------------|
| Z-15 | Podcast featured image CSS hotfix | `hotfix-Z15-podcast-cover.css` — **artifact ready, not yet applied** |
| Z-16 | Podcast JS player engine | `zp-engine.js` + CSS — **artifact ready, not yet applied** |
| BUG-003 | Fix artifact ready | `status: fix-in-progress`, `fixed_version: v1.6.7` pending apply |
| BUG-004 | Fix artifact ready | `status: fix-in-progress`, `fixed_version: v1.6.8` pending apply |
| BUG-009 | mim2000 CEO blog CS YouTube embed | Fixed via Gutenberg API on post 39 |
| BUG-010 | mim2000 CEO blog DE YouTube embed | Fixed via Gutenberg API on post 46 |
| BUG-011 | mim2000 CEO blog IT YouTube embed | Fixed via Gutenberg API on post 48 |
| BUG-012 | mim2000 CEO blog EN duplicate References | Inspected post 35 — no duplicate; marked verified |

### Delivered (2026-04-17 session part 2 — CONT artifacts + sync bypass)
| ID | Title | Resolution |
|----|-------|------------|
| CONT-01 | content-corrections.yaml | Created `3-fold-path/backlog/content-corrections.yaml` — CC-001..004 seeded |
| CONT-02 | content-overrides.php artifact | `hotfix-CONT02-content-overrides.php` + deploy guide — **apply via Theme File Editor** |
| CONT-03 | translations.php patch | `hotfix-CONT03-translations-patch.md` — **apply via Theme File Editor** |
| TC-001/002 | testcases.yaml updated | Verified status added; CPT slug corrected to `zemla_episode`; steps expanded |
| MI-M-T-SYNC bypass | Sync protocol documented | `_config/SYNC-BYPASS-MACBOOK-TO-THINKPAD.md` — 3 methods (git bundle / tar / LAN SSH) |
| MANIFEST | Updated | v1.6.7/v1.6.8 pending; zemla live = v1.6.6 (v1.6.7/v1.6.8 not yet applied via TFE) |
| TASKS-shared | Updated | CONT-01 → done; CONT-02/03 → artifact-ready; CPT slug corrected in notes |

### Delivered (2026-04-17 session part 3 — ThinkPad handshake processing)
| ID | Title | Resolution |
|----|-------|------------|
| AUTH-005 | GitHub Actions OIDC token integration | DONE on ThinkPad (KC IdP + RFC8693 endpoint). MacBook TASKS-shared.yaml pre-updated to match. Artifacts: `infra/auth/kc.sh`, `realm-export/vibedev-realm.json`, `docker-compose.r0-lde.yml`. |
| AUTH-006 | Auth smoke test suite (49 tests) | DONE on ThinkPad (49/49 PASS expected). MacBook TASKS-shared.yaml pre-updated. Artifacts: `kh-sim/tests/auth/`, `.github/workflows/kh-sim-ci.yml`. |
| MI-M-T-SYNC | Handshake processed | `_config/MACBOOK-HANDSHAKE-2026-04-17.md` received from ThinkPad and copied to `_config/`. THINKPAD-SYNC-INSTRUCTIONS.md updated with dual-created-file conflict map. MACBOOK-BUNDLE-CREATE.sh tar list updated. |

### Delivered (2026-04-24 session — deployments + bug logging + HOW-TO)
| ID | Title | Resolution |
|----|-------|------------|
| THEMEPORT-02 | mim2000 v1.6.0 deploy | **LIVE** — style.css + functions.php deployed via Monsta FTP JS (2026-04-24). LinkedIn URL: `petr-zemla-75ab675` applied live. |
| THEMEPORT-03 | bodyterapie v1.3.0 artifacts | Artifacts at `3-fold-path/releases/v1.3.0-bodyterapie/` — **apply via WP Admin TFE manually** |
| HOW-TO | Active24/Monsta FTP deploy guide | `_config/HOW-TO-ACTIVE24-DEPLOY.md` created |
| BUG-018 | Podcast player v1.6.8 regression | Logged severity A / priority B. Three sub-symptoms: cover art display, speed inaccuracy, track restart. Hotfix ID: HOTFIX-ZP-001 |
| TC-009/010/011 | Podcast player regression test cases | Added to `testcases.yaml` — cover art, speed accuracy, skip/speed no-restart |
| WORKFLOW-RULE | Deployment rule established | Theme file changes → artifact files → manual TFE import. See `_config/HOW-TO-ACTIVE24-DEPLOY.md` |

### Delivered (2026-04-24 session cont. — theme zips + credentials + lessons learned)
| ID | Title | Resolution |
|----|-------|------------|
| HOTFIX-ZP-001 | zemla-theme-v1.6.9.zip | **READY** — built 2026-04-24: v1.6.6 base + v1.6.8 appends + translations patch + HOTFIX-ZP-001. At `theme-archives/zemla-theme-v1.6.9.zip`. User uploads via WP Admin → Themes → Upload. |
| THEMEPORT-03 | bodyterapie-theme-v1.3.0.zip | **READY** — built 2026-04-24: v1.2.0 base + v1.3.0 appends. At `theme-archives/bodyterapie-theme-v1.3.0.zip`. User uploads via WP Admin → Themes → Upload. |
| CREDENTIALS | _config/credentials.yaml | Created — Active24 service IDs, FTP accounts (zemla + bodyterapie), WP Admin placeholders. Gitignored. Fill in Active24 login + WP Admin passwords. |
| WORKFLOW-V2 | Deployment workflow revised | Tier 1 (theme files) = user uploads complete zip. Tier 2 (non-theme) = Claude via FTP/browser. HOW-TO updated with session recovery procedure + tier model. |
| LESSONS | HOW-TO session recovery section | Added: `getRequestBody` monkey-patch, `LoginPanelController.testConfiguration()` reconnect, credentials.yaml usage pattern. |

### Open / active after 2026-04-25 session
| ID | Title | Priority | Status | Device |
|----|-------|----------|--------|--------|
| THEMEPORT-03-APPLY | Upload bodyterapie-theme-v1.3.0.zip via WP Admin | P1 | **ZIP READY** — user action required | User |
| CC-005-APPLY | Apply v1.7.0 translations patch to zemla inc/translations.php | P2 | **Artifact ready** at `releases/v1.7.0-zemla/` — TFE apply required | User |
| CC-006 | Add 5 ZEMLA_SLUG_* constants + update page-dao.php/page-psychology.php | P3 | Open — fix in next planned theme version | MacBook |
| CREDENTIALS | Fill WP Admin FILL_IN_* passwords in `_config/credentials.yaml` | P2 | Active24 filled; WP Admin passwords for all 3 sites still needed | User |
| MI-M-T-SYNC | Physical transfer of evidence artifacts MacBook → ThinkPad | P1 | **Bypass protocol ready** — user transfers via USB/LAN/cloud | User |
| MI-M-T-P06 | First testrun mim2000 CEO blog | P2 | Pending — unblocked after SYNC | ThinkPad |
| MI-M-T-P07 | Lessons learned | P3 | Pending | ThinkPad |
| PIL-07 | Run pilot podcast harness on ep00 real stems | P2 | Requires stems in podcast/suche-kosti/ep00/raw/ | MacBook |
| ARCH-E01 | Architecture revision epic (incl. bodyterapie blog BUG-015) | P2 | **Parked** — see epic doc | — |
| MOB-E01 | Mobile optimization bodyterapie.com | P3 | Blocked until ARCH-E01 | — |
| GH-UPL-04/05 | Upload theme zips (v1.6.9, v1.3.0) to GitHub Releases | P2 | **Blocked** — GitHub tokens until 2026-05-01 | MacBook |
| AUTH-004 | OAuth2.0 WP SSO plugin | P3 | Not started | MacBook |

### mim2000 CEO blog post IDs (confirmed 2026-04-17)
All CEO blog posts use a single `core/freeform` (Classic Editor) block.
| Locale | Post ID | URL |
|--------|---------|-----|
| CS | 39 | post.php?post=39&action=edit |
| DE | 46 | post.php?post=46&action=edit |
| IT | 48 | post.php?post=48&action=edit |
| EN | 35 | post.php?post=35&action=edit |

### zemla.org podcast CPT — confirmed facts (2026-04-17 live DOM, post 530)
- CPT slug: `zemla_episode` (NOT `podcast_episode` — defect report was wrong)
- Body class: `single single-zemla_episode postid-530 wp-theme-zemla-theme-v154`
- Theme folder: `zemla-theme-v154`
- Audio URL: stored in `data-src` on `.zp-player` div
- Featured image size: `zemla-wide` — 512×512px hard-cropped, inside bare `<div>` (no class)
- Player DOM: `.zp-player[data-src]` → `.zp-play`, `.zp-progress-wrap`, `.zp-time`, `.zp-download`
- `main.js`: zero podcast/audio code — `<audio>` never created — root cause of BUG-004

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
ARCH-*     Architecture revision epic (new)
GH-*       GitHub operations
GEN-*      Generic/workspace tasks
GW-*       Git workflow tasks
MI-M-T-*   4-step-noble-steps-to-MI-M-T project
```

---

## § HANDOFF BLOCK — 2026-05-04 (NUM-KH-FOR-05)
**Last session:** 2026-05-04 (continuation — NUM-KH-FOR-05 diagnostics + IO + TC-007)  
**Closed because:** NUM-KH-FOR-05 complete — kh_diagnostics + kh_io + TC-NUM-KH-007 written. DRY-RUN.  
**Restart reads:** CLAUDE.md → `_config/HANDOVER-V0.2-THINKPAD.md` → `_config/SESSION-LIFECYCLE-SOP.md` → `3-fold-path/code/SESSION-NOTES.md`  
**NUM-KH-FOR-05 delivered:**
- `kh-sim/backends/fortran/src/kh_diagnostics.f90` — KE, enstrophy, max_vort, div_rms (spectral, Parseval-normalised)
- `kh-sim/backends/fortran/src/kh_io.f90` — namelist param reader + JSON snapshot writer (one line per step)
- `kh-sim/backends/fortran/tests/test_num_007_energy.f90` — TC-NUM-KH-007: inviscid run (ν=0), 500 steps, KE drift ≤ 1e-3
- DRY-RUN — compile + validate on ThinkPad (see SESSION-NOTES for PowerShell commands)
**NUM-KH-FOR-01..04 delivered (prior):**
- `kh_constants.f90` + `kh_grid.f90` + `kh_fft.f90` + TC-001 — Commit `b68d4e7`
- `kh_poisson.f90` + `kh_velocity.f90` + TC-002 — Commit `3cfeb8b`
- `kh_nonlinear.f90` + TC-005 — Commit `2374290`
- `kh_etdrk4.f90` + TC-003 — Commit `83e926e`
- ThinkPad validation: 4/4 PASS (all near machine epsilon). Commit `a814cc9`
**KH-01 delivered (earlier):** community files + kh-sim-public branch at `19d7eaa`
**PoC-03 delivered (earlier):** D05-REDMINE-CONTRACT.md + OQ-100..103 + OQ-300
**PoC-04 STOP gate:** O