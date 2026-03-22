# HOTFIX: GAL-D01 — Gallery Contracted Layout + Missing Descriptions
**All 3-fold-path Sites: zemla.org / mim2000.cz / bodyterapie.com**

---

**Classification:** HOTFIX
**Priority:** P1 — Critical (elevated from High, aligned to highest active 3-fold-path task)
**Severity:** High
**Status:** Open — awaiting fix implementation
**Logged:** 2026-03-22
**Evidence:** Safari snapshot provided (2026-03-22), confirmed Chrome identical

---

## Symptom Summary

| Symptom | Observed value | Expected value |
|---------|---------------|----------------|
| Gallery container width | ~440px, left-aligned | Full content-area width (100% of `--content-width`) |
| Right-side viewport usage | Dead space (~60% of viewport) | Populated with gallery tiles |
| Image tile captions / descriptions | Not visible | Readable text below or overlaid on each tile |
| Affected browsers | Safari + Chrome (both) | All browsers |
| Affected sites | All 3 (zemla, mim2000, bodyterapie) | All 3 |
| Affected locales | All (CS confirmed, assumed all) | All |

---

## Diagnosis Path (DevTools — run on any affected site)

### Step 1 — Identify contracted container

Open DevTools → Elements panel. Select the gallery wrapper element.

```
Inspect: .gallery | .gallery-container | .wp-block-gallery | figure.wp-block-gallery
Check:   width, max-width, flex-basis, grid-column
```

**Most probable offenders:**

```css
/* CASE A — hardcoded max-width */
.gallery { max-width: 440px; }

/* CASE B — fixed grid column in parent */
.content-area { grid-template-columns: 440px 1fr; }
/* → gallery lands in first column only */

/* CASE C — flex child with constrained basis */
.gallery-wrap { flex: 0 0 440px; }

/* CASE D — WordPress block width lock */
.wp-block-gallery { width: 440px; align-self: flex-start; }
```

### Step 2 — Identify missing captions/descriptions

```
Inspect: figcaption | .gallery-caption | .wp-caption-text | .gallery-item p
Check:   display, visibility, opacity, color, font-size, height
```

**Most probable offenders:**

```css
/* CASE A — outright hidden */
.gallery-caption { display: none; }
figcaption { visibility: hidden; }

/* CASE B — invisible against background */
.gallery-caption { color: var(--c-bg); }       /* text same as background */
.gallery-caption { color: transparent; }

/* CASE C — zero-height container */
.gallery-caption { height: 0; overflow: hidden; }

/* CASE D — font-size zeroed */
.gallery-caption { font-size: 0; }
```

---

## Fix Specification

### FIX-1: Restore full-width gallery container

**Target file:** `style.css` or `gallery.css` in 3-fold-path base theme

```css
/* REPLACE contracted rule with: */
.gallery,
.wp-block-gallery,
.gallery-container {
  width: 100%;
  max-width: var(--content-width, 100%);
  margin-inline: auto;
  box-sizing: border-box;
}
```

If gallery is a grid child — fix the parent column definition:

```css
/* Parent layout: ensure gallery spans full column */
.page-content,
.entry-content {
  display: block;           /* or: grid with single-column template */
  width: 100%;
}
```

### FIX-2: Restore caption/description visibility

```css
/* Ensure captions render */
.gallery-caption,
.gallery .gallery-caption,
figcaption,
.wp-caption-text {
  display: block;
  visibility: visible;
  opacity: 1;
  color: var(--c-text);
  font-size: var(--fs-sm, 0.85rem);
  line-height: 1.5;
  padding: 0.4rem 0.25rem 0;
  height: auto;
  overflow: visible;
}
```

### FIX-3: Apply via 3-fold-path shared library (not per-site)

Both fixes must land in the **shared base stylesheet** of the 3-fold-path library.
Do NOT apply per-site overrides — this resolves all three sites in a single patch.

```
File target:  /wp-content/themes/[3fp-base]/gallery.css
              OR /wp-content/themes/[3fp-base]/style.css (gallery section)
Version bump: patch increment on all 3 sites
```

---

## Test Checklist (post-fix, all 3 sites)

- [ ] Gallery spans full content-area width at 1440px viewport
- [ ] Gallery spans full content-area width at 1024px viewport
- [ ] No horizontal overflow at ≤860px (tablet)
- [ ] No layout regression at ≤480px (mobile)
- [ ] Caption/description text visible on all tiles
- [ ] Caption text colour passes WCAG AA contrast ratio vs. background
- [ ] Verified: Safari (macOS + iOS)
- [ ] Verified: Chrome (desktop + Android)
- [ ] Verified: Firefox
- [ ] All language variants pass (CS / EN / JA / DE / IT where applicable)
- [ ] No JS console errors on gallery page load

---

## Sequencing Note

Fix GAL-D01 **before** Z-MOB-01 / M-MOB-01 (pattern extraction into 3-fold-path library).
Extracting patterns from a broken gallery state would formalise defects into the library.
