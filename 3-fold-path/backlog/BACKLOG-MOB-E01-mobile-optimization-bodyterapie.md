# EPIC: MOB-E01 — Mobile Version Optimization: bodyterapie.com
**Created:** 2026-03-21
**Priority:** Medium
**Severity:** High
**Status:** Backlog

---

## Epic Summary

Port and apply mobile design patterns from **zemla.org** and **mim2000.cz** (v1.2.1 fp-mobile-nav baseline) across the **3-fold-path design pattern library**, then implement those patterns on **bodyterapie.com** with full fine-tuning of mobile design and functionality.

## Context & Dependencies

- **Pattern sources:** zemla.org mobile layout baseline; mim2000.cz v1.2.1 (fp-mobile-nav grid, corner-leaf suppression at ≤480px, tablet desc-hide at ≤860px)
- **Target library:** 3-fold-path design pattern library (shared across all three sites)
- **Target site:** bodyterapie.com (current version: v1.1.5, 4-lang, CSS variable baseline)
- **Breakpoint reference:** ≤480px (mobile), ≤860px (tablet)
- **Tap target standard:** 56px interactive elements, `-webkit-tap-highlight-color` for iOS

## Eliminating Constraints

- Changes must not break existing 4-language layout on bodyterapie.com
- CSS variables must remain the single source of truth for theming — no hardcoded colour/spacing values
- Pattern library entries must be portable across all three sites without site-specific overrides where avoidable
- Zemla and mim2000 audits are read-only reference tasks unless regressions are found; no feature scope creep
- Mobile implementation must pass Safari/iOS as primary acceptance gate (known historical failure mode)

---

## User Stories

### bodyterapie.com — Primary Target

**B-MOB-01: Mobile Navigation Grid**
*As a mobile user, I want the bodyterapie.com homepage to render a mobile navigation grid (≤480px) consistent with the mim2000 fp-mobile-nav pattern, so that I can navigate without overflow or layout collapse.*
- Port fp-mobile-nav 2×2 grid pattern from mim2000 v1.2.1
- Suppress absolute-positioned desktop elements at ≤480px
- Apply 56px tap targets with iOS highlight feedback
- **Acceptance:** No horizontal overflow on Safari/iPhone; tapping each card navigates correctly

**B-MOB-02: Responsive Typography & Spacing**
*As a mobile user, I want body copy, headings, and spacing on bodyterapie.com to follow the 3-fold-path scale system at all breakpoints.*
- Align font scale and line-height with 3-fold-path library definitions
- Validate at ≤480px and ≤860px breakpoints
- **Acceptance:** No text truncation, no overflow; scale consistent with zemla.org and mim2000.cz

**B-MOB-03: Mobile Functionality Fine-Tuning**
*As a mobile user, I want all interactive elements — contact form, language switcher, booking links — to be fully operable on touch devices.*
- Audit all interactive elements for touch-accessibility (target size, focus states)
- Fix any known functional regressions on mobile (form submission, switcher dropdown)
- **Acceptance:** All interactive flows complete successfully on iOS Safari + Android Chrome

**B-MOB-04: Breakpoint Alignment with 3-fold-path Library**
*As a developer, I want bodyterapie.com breakpoints to be defined via CSS variables and aligned with the canonical 3-fold-path breakpoint definitions.*
- Replace any hardcoded px breakpoints with library-standard variables
- Document final breakpoint map in pattern library
- **Acceptance:** Single breakpoint definition referenced consistently across all three sites

**B-MOB-05: Mobile Regression & Cross-Device Testing**
*As a QA engineer, I want full cross-browser/device validation of bodyterapie.com mobile after all MOB changes are applied.*
- Test matrix: Safari/iOS (primary), Chrome/Android, Firefox/Android
- Validate all 4 language variants
- **Acceptance:** Zero layout failures across test matrix; all languages render correctly

---

### zemla.org — Pattern Source & Audit

**Z-MOB-01: Mobile Pattern Extraction → 3-fold-path Library**
*As a developer, I want zemla.org mobile design patterns formally documented in the 3-fold-path library so they can be referenced and reused without re-inspection.*
- Extract: navigation patterns, content block layout, breakpoint behaviour, typography scale
- Write pattern library entries with code snippets and usage notes
- **Acceptance:** Pattern entries reviewed and merged into library; no zemla-specific overrides remain undocumented

**Z-MOB-02: zemla.org Mobile Audit (regression check)**
*As a developer, I want to verify zemla.org mobile layout against the v1.6.2 release baseline to confirm no regressions before it is used as a reference source.*
- Smoke-test key mobile breakpoints (≤480px, ≤860px)
- Document any gaps; raise separate fix tasks if regressions found (outside this epic scope)
- **Acceptance:** Baseline confirmed clean OR regression tasks raised and logged separately

---

### mim2000.cz — Pattern Source & Fine-Tuning

**M-MOB-01: Mobile Pattern Extraction → 3-fold-path Library**
*As a developer, I want mim2000.cz v1.2.1 mobile patterns formally documented in the 3-fold-path library.*
- Extract: fp-mobile-nav 2×2 grid, corner-leaf suppression logic, tablet desc-hide rules, iOS tap highlight approach
- Write pattern library entries with annotated CSS and rationale
- **Acceptance:** Pattern entries usable by bodyterapie.com implementation without re-inspecting mim2000 source

**M-MOB-02: mim2000.cz Mobile Fine-Tuning (post v1.2.1)**
*As a mobile user, I want any remaining edge cases from the mim2000 v1.2.1 mobile nav to be resolved.*
- Review open items from v1.2.1 delivery (if any)
- Focus: enso tooltip behaviour on small screens, anchor link scroll on mobile
- **Acceptance:** No reported mobile issues on mim2000.cz after fine-tuning; regression test passes

---

## Task Sequence (suggested)

```
Z-MOB-02 (audit zemla baseline)
    → Z-MOB-01 (extract zemla patterns)
M-MOB-02 (fine-tune mim2000 post v1.2.1)
    → M-MOB-01 (extract mim2000 patterns)
        → B-MOB-04 (align bodyterapie breakpoints)
        → B-MOB-01 (port mobile nav)
        → B-MOB-02 (typography & spacing)
        → B-MOB-03 (interactive/functional)
            → B-MOB-05 (regression & cross-device test)
```

## Definition of Done (Epic)

- All user stories accepted per their individual acceptance criteria
- 3-fold-path library contains documented, reusable entries for all mobile patterns extracted from zemla + mim2000
- bodyterapie.com passes full cross-browser mobile test matrix across all 4 languages
- No hardcoded breakpoints or colours remain in bodyterapie.com mobile CSS
- Release notes drafted for bodyterapie.com next version bump
