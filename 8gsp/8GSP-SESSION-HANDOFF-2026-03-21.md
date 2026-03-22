# 8GSP Sprint — Session Handoff
**Date:** 2026-03-21
**Next session baseline:** Claude Cowork v1.1.7203+
**Sprint iteration:** v0.2 (continuation)

---

## 1. Delivered This Session

### A workstream — 3-fold-path (all 3 sites)
| Item | Deliverable | Notes |
|------|-------------|-------|
| ARCH-01 Photo Registry | zemla v1.6.0 | `zemla_photo_registry` option + `[photo:name]` token + `get_post_metadata` filter |
| ARCH-02 Inline meta box | zemla v1.6.0 | 5-lang `_zemla_content_{lang}` textarea in WP admin |
| Z-02 Gallery cross-browser | zemla v1.6.1 | 5 Safari/Chrome CSS fixes + Wikimedia referrerpolicy |
| Z-09 zen-arts i18n | zemla v1.6.1 | `the_excerpt()` suppressed for non-EN; zen-arts seeder added |
| A-F1-01 Noto Serif JP | all 3 themes | `language_attributes` + `body_class` filters in all 3 functions.php |
| D-01 MI-M-T Step 1 | zemla v1.6.2 | Mermaid classDiagram, 5-locale seeder, page template |

### B workstream — CV ecosystem
| Item | Deliverable | Notes |
|------|-------------|-------|
| B-01 audit | `8gsp-b01-cv-audit-v1.0.docx` | 7 sections, R-01–R-07, LinkedIn gap analysis |
| R-01 | `CV-Zemla-C-Standard-EN.docx` | "Project Experience" → "Project Portfolio" |
| R-02 | `CV-Zemla-B-Technical-EN.docx` | Intellectual Framework abstract added |
| R-03 | A + C tracks | AI & Test Augmentation section added |
| R-04 | `CV-Zemla-B-Technical-EN.docx` | Career Summary 5-row timeline table added |
| R-05 | folder | 5 legacy CV files renamed with `_ARCHIVED` suffix |
| R-06 | `CV-Zemla-B-Technical-DE.docx` | German B-track CV (full translation, validated 53 para) |

### Documentation
| File | Notes |
|------|-------|
| `3fold-path-devref-v159.docx` | Session documentation: ARCH-01/02, Z-02/09, A-F1-01, D-01, R-06, audits |
| `RELEASE-zemla-v1.6.2.md` | GitHub release notes for zemla v1.6.0–v1.6.2 |
| `RELEASE-mim2000-v1.5.5.md` | GitHub release notes for mim2000 v1.5.5 |
| `RELEASE-bodyterapie-v1.1.5.md` | GitHub release notes for bodyterapie v1.1.5 |

---

## 2. Current Version State

| Component | Version | Status | Zip archive |
|-----------|---------|--------|-------------|
| zemla.org theme | **v1.6.2** | LIVE | `zemla-theme-v1.6.2.zip` |
| mim2000.cz theme | **v1.5.5** | LIVE | `mim2000-theme-v1.5.5.zip` |
| bodyterapie.com theme | **v1.1.5** | LIVE | `bodyterapie-theme-v1.1.5.zip` |
| CV Master EN | v2026-03-21 | CURRENT | `CV track and actual versions/` |
| CV A-track EN | R-03 applied | CURRENT | `CV-Zemla-A-Principal-EN.docx` |
| CV B-track EN | R-02/04 applied | CURRENT | `CV-Zemla-B-Technical-EN.docx` |
| CV B-track DE | R-06 new | CURRENT | `CV-Zemla-B-Technical-DE.docx` |
| CV C-track EN | R-01/03 applied | CURRENT | `CV-Zemla-C-Standard-EN.docx` |

---

## 3. Remaining Sprint Items (carry forward)

### Blocked on external resources
| ID | Item | Blocker |
|----|------|---------|
| C-00 | Sci&Buddha Keynote baseline recovery | Awaiting user source files |
| C-02a | Topic hierarchy (≤150 slides) | Requires C-00 |
| C-02b | Source placement map | Requires C-02a |
| C-02c | Lecturer notes | Requires C-02b |
| C-02d | Slide expansion 43→150 | Multi-sprint; requires C-02a/b/c |

### Requires manual user action
| ID | Item | Action required |
|----|------|-----------------|
| B-02 / R-07 | LinkedIn profile alignment | Manual LinkedIn write access |

### Deferred to future phases
| ID | Item | Phase |
|----|------|-------|
| DELTA-01 | bodyterapie Phase 5 multilingual seeder arch | Phase 5 |
| Z-06 | Lorenz Attractor interactive simulator | Low priority |
| A-F1-03 | HMSW33 mim2000 carousel evaluation | Low priority |

---

## 4. GitHub Upload Checklist

### zemla.org (private repo)
```
[ ] Upload: zemla-theme-v1.6.2.zip  →  GitHub Release v1.6.2
[ ] Release notes: RELEASE-zemla-v1.6.2.md  →  paste as release description
[ ] Tag: v1.6.2
```

### mim2000.cz (private repo)
```
[ ] Upload: mim2000-theme-v1.5.5.zip  →  GitHub Release v1.5.5
[ ] Release notes: RELEASE-mim2000-v1.5.5.md  →  paste as release description
[ ] Tag: v1.5.5
```

### bodyterapie.com (private repo)
```
[ ] Upload: bodyterapie-theme-v1.1.5.zip  →  GitHub Release v1.1.5
[ ] Release notes: RELEASE-bodyterapie-v1.1.5.md  →  paste as release description
[ ] Tag: v1.1.5
```

### 8GSP documentation repo / drive
```
[ ] 3fold-path-devref-v159.docx
[ ] 8gsp-b01-cv-audit-v1.0.docx
[ ] 8gsp-sprint-v02.docx  (current sprint spec)
[ ] CV-Zemla-B-Technical-DE.docx  (new German B-track)
```

---

## 5. New Session Startup Instructions

On next session start (Claude Cowork v1.1.7203+), to resume development:

### Unpack working theme sources
```bash
# zemla (working source)
mkdir -p zemla-v162-work
cd zemla-v162-work
cp "mnt/CV and personal/zemla-theme-v1.6.2.zip" .
unzip zemla-theme-v1.6.2.zip
cd ..

# mim2000
mkdir -p mim2000-work
cd mim2000-work
cp "mnt/CV and personal/mim2000-theme-v1.5.5.zip" .
unzip mim2000-theme-v1.5.5.zip
cd ..

# bodyterapie
mkdir -p bodyterapie-work
cp "mnt/CV and personal/bodyterapie-theme-v1.1.5.zip" bodyterapie-work/
cd bodyterapie-work && unzip bodyterapie-theme-v1.1.5.zip && cd ..
```

### Docx generation setup
```bash
# NODE_PATH is required for all gen-*.js scripts
export NODE_PATH=/usr/local/lib/node_modules_global/lib/node_modules

# Validate any .docx
python /sessions/.../mnt/.skills/skills/docx/scripts/office/validate.py file.docx
```

### First tasks on next session
1. Provide Sci&Buddha Keynote source → unblock C-00 → C-02a topic hierarchy
2. CV B-02 LinkedIn alignment (R-07) — manual action on LinkedIn profile
3. Review `8gsp-sprint-v02.docx` for any new sprint items to add

---

## 6. Translation Coverage Status (confirmed PASS)

| Component | EN | CS | JA | DE | IT | Status |
|-----------|----|----|----|----|-----|--------|
| zemla dao card descs | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| zemla physics sub-topics | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| bodyterapie schools/wholeness/support | ✅ | ✅ | ✅ | ✅ | ✅ (IT bonus) | PASS |
| mim2000 MI-M-T module labels | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |

---

## 7. Architecture Decision Records — Status

| ADR | Status | Implemented in |
|-----|--------|----------------|
| ADR-001 Photo Registry | ACCEPTED + IMPLEMENTED | zemla v1.6.0 |
| ADR-002 Inline meta editing | PROPOSED + IMPLEMENTED | zemla v1.6.0 |
| ADR-003 MI-M-T Step 1 | ACCEPTED + IMPLEMENTED | zemla v1.6.2 |
| ADR-004 bodyterapie delta | ACCEPTED, DELTA-01 pending | Phase 5 |
| ADR-005 CEO Blog multilingual | ACCEPTED + IMPLEMENTED | mim2000 v1.5.2 |

---

*Generated by Claude Cowork session 2026-03-21*
*Sprint reference: 8gsp-sprint-v02.docx · devref: 3fold-path-devref-v159.docx*
