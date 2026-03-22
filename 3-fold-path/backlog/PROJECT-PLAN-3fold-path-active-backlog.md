# PROJECT PLAN — 3-fold-path Active Backlog
**Sites:** zemla.org / mim2000.cz / bodyterapie.com
**Updated:** 2026-03-22
**Model:** Hotfix track (parallel) + Sprint backlog (sequential)

---

## Priority Legend

| Symbol | Level | Description |
|--------|-------|-------------|
| 🔴 | P1 — Critical | Hotfix — production-broken, bypass sprint queue |
| 🟠 | P2 — High | Sprint top — next scheduled release |
| 🟡 | P3 — Medium | Backlog — queued for upcoming sprint |
| ⚪ | P4 — Low | Deferred |

---

## HOTFIX TRACK — Active (parallel to sprint, deploy independently)

### 🔴 GAL-D01 — Gallery Contracted Layout + Missing Descriptions
**Type:** Hotfix | **Priority:** P1 Critical | **Severity:** High
**Scope:** All 3 sites — single patch via 3-fold-path shared base stylesheet
**Blocks:** Z-MOB-01, M-MOB-01 (pattern extraction must not happen over broken gallery)

**Patch versions on release:**
- zemla.org → **v1.6.3**
- mim2000.cz → **v1.5.6**
- bodyterapie.com → **v1.1.6**

**Implementation tasks:**

| Task ID | Description | State |
|---------|-------------|-------|
| GAL-D01-INV | DevTools root cause confirmation (contracted container + caption CSS) | ⬜ Open |
| GAL-D01-FIX | Apply CSS fix to 3-fold-path base stylesheet | ⬜ Open |
| GAL-D01-TEST | Cross-browser / cross-device / all-locale regression test | ⬜ Open |
| GAL-D01-REL | Tag and release patch versions on all 3 sites | ⬜ Open |

**Reference docs:**
- `HOTFIX-GAL-D01-defect-report.md` — diagnosis path + fix spec
- `RELEASE-zemla-v1.6.3-HOTFIX-GAL-D01.md`
- `RELEASE-mim2000-v1.5.6-HOTFIX-GAL-D01.md`
- `RELEASE-bodyterapie-v1.1.6-HOTFIX-GAL-D01.md`

---

## SPRINT BACKLOG — Sequenced

> GAL-D01 hotfix must be **closed** before Z-MOB-01 / M-MOB-01 pattern extraction begins.

---

### EPIC MOB-E01 — Mobile Version Optimization: bodyterapie.com
**Priority:** P3 Medium | **Severity:** High
**Depends on:** GAL-D01 closed (pattern sources must be clean before extraction)

#### Phase 1 — Pattern Source Audit & Extraction

```
GAL-D01 ✓ (hotfix closed)
    │
    ├── Z-MOB-02  Zemla mobile baseline regression audit
    │       ↓
    │   Z-MOB-01  Extract zemla mobile patterns → 3-fold-path library
    │
    └── M-MOB-02  mim2000 mobile fine-tuning (post v1.2.1 edge cases)
            ↓
        M-MOB-01  Extract mim2000 mobile patterns → 3-fold-path library
```

| Task ID | Description | Priority | State |
|---------|-------------|----------|-------|
| Z-MOB-02 | zemla.org mobile audit — confirm v1.6.2 baseline clean | P2 | ⬜ Open |
| Z-MOB-01 | Extract zemla mobile patterns into 3-fold-path library | P2 | ⬜ Open |
| M-MOB-02 | mim2000.cz mobile fine-tune post v1.2.1 | P2 | ⬜ Open |
| M-MOB-01 | Extract mim2000 mobile patterns into 3-fold-path library | P2 | ⬜ Open |

#### Phase 2 — bodyterapie.com Implementation

```
Z-MOB-01 ✓  +  M-MOB-01 ✓  (library populated)
    │
    ├── B-MOB-04  Align breakpoints to 3-fold-path CSS variables
    ├── B-MOB-01  Port mobile nav grid (fp-mobile-nav pattern)
    ├── B-MOB-02  Typography & spacing alignment
    └── B-MOB-03  Interactive / functional fine-tuning (forms, lang switcher)
            ↓
        B-MOB-05  Cross-browser / cross-device regression test (all 4 langs)
```

| Task ID | Description | Priority | State |
|---------|-------------|----------|-------|
| B-MOB-04 | Align bodyterapie breakpoints to 3-fold-path CSS variables | P3 | ⬜ Open |
| B-MOB-01 | Port fp-mobile-nav grid from mim2000 v1.2.1 | P3 | ⬜ Open |
| B-MOB-02 | Typography & spacing alignment at ≤480px / ≤860px | P3 | ⬜ Open |
| B-MOB-03 | Mobile functionality fine-tune (forms, language switcher, booking) | P3 | ⬜ Open |
| B-MOB-05 | Full cross-browser / cross-device / 4-language regression test | P3 | ⬜ Open |

**Epic release versions on close:**
- bodyterapie.com → **v1.2.x** (post-hotfix baseline v1.1.6)
- zemla.org → **v1.6.x** (post-hotfix baseline v1.6.3)
- mim2000.cz → **v1.5.x** (post-hotfix baseline v1.5.6)

---

## Full Sequencing View

```
NOW
 │
 ▼
[HOTFIX TRACK — parallel, deploy immediately on fix]
 🔴 GAL-D01-INV   Root cause confirmation (DevTools)
 🔴 GAL-D01-FIX   CSS fix in 3-fold-path base stylesheet
 🔴 GAL-D01-TEST  Regression test
 🔴 GAL-D01-REL   Release: zemla v1.6.3 / mim2000 v1.5.6 / bodyterapie v1.1.6
 │
 ▼
[SPRINT — after GAL-D01 closed]
 🟠 Z-MOB-02 / M-MOB-02   Audit reference sites (can run in parallel)
 🟠 Z-MOB-01 / M-MOB-01   Pattern extraction → library (can run in parallel)
 │
 ▼
 🟡 B-MOB-04  Breakpoint alignment
 🟡 B-MOB-01  Mobile nav grid port
 🟡 B-MOB-02  Typography alignment
 🟡 B-MOB-03  Functional fine-tuning
 │
 ▼
 🟡 B-MOB-05  Final regression test
 │
 ▼
CLOSE MOB-E01 EPIC
```

---

## Open Backlog Items (not yet scheduled)

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| C-00 | Sci & Buddha Keynote | P1 | Blocked on source files from user |
| MI-M-T | [to be decoded — related to zemla v1.6.2 D-01] | TBD | Carry forward from v1.6.2 release |

---

*Reference docs: `BACKLOG-MOB-E01-mobile-optimization-bodyterapie.md`, `HOTFIX-GAL-D01-defect-report.md`, `8GSP-SESSION-HANDOFF-2026-03-21.md`*
