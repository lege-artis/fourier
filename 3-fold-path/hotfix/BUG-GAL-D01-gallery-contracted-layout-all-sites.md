# DEFECT: GAL-D01 — Gallery Contracted Layout + Missing Descriptions (All 3-fold-path Sites)

**Logged:** 2026-03-22
**Priority:** High
**Severity:** High
**Status:** Open / Backlog
**Reporter:** Visual inspection — Safari snapshot provided (2026-03-22)
**Scope:** Cross-site — affects zemla.org, mim2000.cz, bodyterapie.com (all 3-fold-path instances)
**Reproducible:** Yes — confirmed in Safari and Chrome (same behaviour in both)

---

## Observed Behaviour

Screenshot (zemla.org /galerie, Safari, CS locale):
- Gallery grid collapses into a ~440px-wide left-side column
- Right ~60% of viewport is empty dead space
- Image tiles render in a cramped 2-column sub-grid within the contracted container
- No visible text descriptions or captions under any image tile
- Layout does not expand to fill available viewport width

## Expected Behaviour

- Gallery grid spans full content-area width (consistent with body/page container)
- Image tiles distributed across available width using fluid columns (fr units or %-based)
- Tile descriptions/captions rendered and visible below or overlaid on each image
- Behaviour consistent across Safari, Chrome, and Firefox

---

## Root Cause Hypotheses (to validate)

| # | Hypothesis | Probability | Investigation action |
|---|------------|-------------|----------------------|
| 1 | Gallery container has a fixed `max-width` or `width` in px rather than 100% / fluid | High | Inspect `.gallery`, `.gallery-container`, `.wp-block-gallery` CSS rules |
| 2 | Grid column definition uses absolute px values (`grid-template-columns: 220px 220px`) instead of `1fr` or `minmax()` | High | Check grid/flex layout definition on gallery wrapper |
| 3 | Description/caption elements exist in DOM but are hidden via `display: none`, `opacity: 0`, or `visibility: hidden` — possibly a leftover theme rule | Medium | Inspect DOM for caption nodes; check computed styles |
| 4 | A JS initialisation for masonry/lightbox library is failing silently and leaving the gallery in an uninitialised state | Medium | Check browser console for JS errors on gallery page load |
| 5 | CSS specificity conflict — a utility class from 3-fold-path library overrides the gallery layout rule | Low–Medium | Compare rendered vs. inherited styles in DevTools |

---

## Reproduction Steps

1. Navigate to `/galerie` (or equivalent gallery path) on any 3-fold-path site
2. Observe page in full-width desktop viewport (≥1024px)
3. Confirm: gallery column confined to left ~440px; right side empty
4. Confirm: no caption/description text visible under tiles
5. Repeat in Safari and Chrome — behaviour identical

---

## Impact

- **User impact:** Gallery section is visually broken and non-informative on all three sites across all supported browsers — affects all locales
- **SEO impact:** If captions/alt descriptions are suppressed, image indexing may be degraded
- **Brand impact:** High — gallery is a primary content area on all 3-fold-path sites

---

## Suggested Fix Direction

1. Set gallery container to `width: 100%` / `max-width: var(--content-width)` with `margin: 0 auto`
2. Replace any fixed-px column definitions with `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` or equivalent fluid grid
3. Audit caption/description CSS — remove any `display: none` applied to `.gallery-caption`, `.wp-caption-text`, or equivalent selectors
4. If JS-dependent (lightbox/masonry), verify library loads without console errors; add fallback layout for no-JS state
5. Apply fix via shared 3-fold-path library to resolve all three sites in one patch

---

## Acceptance Criteria

- [ ] Gallery spans full content-area width on all three sites at ≥1024px viewport
- [ ] Image descriptions/captions visible on all tiles
- [ ] No layout regression at ≤860px (tablet) or ≤480px (mobile)
- [ ] Verified in Safari, Chrome, and Firefox
- [ ] All language variants confirmed (CS/EN/JA/DE/IT where applicable)
- [ ] Fix delivered via 3-fold-path library patch (not per-site overrides)

---

## Related

- Epic MOB-E01 — Mobile Version Optimization: bodyterapie.com (pattern library work may surface this issue in mobile context too)
- Recommend: Fix GAL-D01 **before** Z-MOB-01 / M-MOB-01 pattern extraction to avoid documenting broken patterns into the library
