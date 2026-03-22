# zemla-theme v1.6.2 — Release Notes
**Date:** 2026-03-21
**Tag:** `v1.6.2`
**Asset:** `zemla-theme-v1.6.2.zip`

This release covers three version increments (v1.6.0 → v1.6.1 → v1.6.2) delivering architectural
foundations, multilingual rendering fixes, gallery cross-browser compatibility, and the first
public rendering of the MI-M-T entity model.

---

## What's New

### v1.6.2 — D-01 / ARCH-03: MI-M-T Entity Model page

**New page template: `page-templates/page-mi-m-t.php`**
- Landing hero with ⟳ symbol, multilingual lead from `_zemla_mi_m_t_lead_{lang}` post meta
- Full Mermaid.js classDiagram — 17 entity classes across 5 domains:
  `TestImpuls` → `TestAnalyticals` → `TestExecDeployment` → `IssueTracking` → `Reporting`
- 4-step domain legend with per-locale descriptions (EN/CS/JA/DE/IT)
- Breadcrumb auto-resolves from WP page hierarchy
- Mobile: overflow-x scroll wrapper for diagram on narrow viewports

**Mermaid.js v10.9.1 conditional enqueue (`functions.php`)**
- Fires only on `page-mi-m-t.php` template OR any post with `zemla_mermaid = 1` custom field
- CDN: jsDelivr; theme: `neutral`; securityLevel: `loose`; fontFamily: `inherit`

**`zemla_seed_mi_m_t_page()` seeder**
- Guard: `_zemla_mi_m_t_seed_v1`; hooks: `admin_init` + `template_redirect`
- Creates `/mi-m-t/` WP page if absent, assigns template
- Seeds `_zemla_content_{lang}` in all 5 locales: Overview + Design Principles + Entity Model sections
- Seeds `_zemla_mi_m_t_lead_{lang}` lead sentence per locale

---

### v1.6.1 — Z-09 Multilingual Fix + A-F1-01 Noto Serif JP + Z-02 Gallery

**Z-09 — zen-arts language mismatch fix**
- `page-art-topic.php`: `the_excerpt()` now suppressed for non-EN locales
  (post_excerpt is not multilingual-aware; was causing EN+translated double-render)
- `zemla_seed_zen_arts_content_v1()`: seeds `_zemla_content_{lang}` for `/art/zen-arts/`
  in all 5 locales; guard `_zemla_zen_arts_content_v1`

**A-F1-01 — Noto Serif JP activation (cookie-locale aware)**
- `style.css`: `.lang-ja, :lang(ja)` dual-selector activates Noto Serif JP for cookie-based
  locale switch (body class path) AND WP `html[lang]` path simultaneously
- `zemla_html_lang_attribute()`: filters `language_attributes` — overrides `<html lang>` to
  match active zemla cookie locale (BCP 47 mapping: en/cs/ja/de/it)
- `zemla_body_lang_class()`: filters `body_class` — adds `lang-{code}` on every page load
- Style enqueue version now dynamic: `wp_get_theme()->get('Version')` — cache-busts on deploy

**Z-02 — Gallery cross-browser fix (Safari/Chrome)**
- `.gallery-grid`: removed `clamp()` from `minmax()` — Safari <15 bug with nested clamp
- `.gallery-item--photo`: added `aspect-ratio: 4/3` for uniform grid row height
- `.gallery-item--photo img`: added `height: 100%` — required for `object-fit: cover` in Safari
- `.album-card__link`: replaced `grid-template-rows: 1fr` with `align-items: stretch`
- `.album-card__thumb img`: added `height: 100%` + `display: block` — Safari thumb alignment
- Wikimedia: `referrerpolicy="no-referrer"` on 45 cross-origin `<img>` tags in seeders

---

### v1.6.0 — ARCH-01 Photo Registry + ARCH-02 Inline Meta Editing

**ARCH-01 — Photo Registry (ADR-001 ACCEPTED)**
- `zemla_seed_photo_registry()`: idempotent seeder mapping semantic names → WP attachment IDs
  via exact `_wp_attached_file` lookup; stored in `zemla_photo_registry` WP option
- `zemla_resolve_photo_tokens(string $content)`: replaces `[photo:semantic-name]` tokens
  with `wp_get_attachment_url($id)` at render time; graceful miss returns empty string
- `zemla_meta_token_filter()`: transparent `get_post_metadata` filter for all `_zemla_content_{lang}`
  keys — zero template changes required
- One-time migration replaces hotfix v2 hardcoded URLs with `[photo:name]` tokens in stored metas
- Re-run: `delete_option('zemla_photo_registry')` triggers fresh attachment ID resolution

**ARCH-02 — Inline meta editing (ADR-002 PROPOSED → IMPLEMENTED)**
- `zemla_lang_meta_box_register()`: custom meta box on WP page edit screen (no plugin dependency)
- Renders 5 `<textarea>` fields (EN/CS/JA/DE/IT) for `_zemla_content_{lang}` post meta
- CSRF-protected via `wp_nonce_field`; saves via `save_post` hook with capability check
- Bypasses token filter for raw token editing (inline `[photo:name]` authoring)

---

## Upgrade Notes

1. Deploy `zemla-theme-v1.6.2.zip` via WordPress > Appearance > Themes or FTP
2. Visit any admin page or front-end URL — seeders auto-run on `admin_init` / `template_redirect`
3. For Photo Registry: upload Aikido/Kinorenma photos via WP Media Library matching the
   semantic names in `zemla_seed_photo_registry()`. Re-run registry by deleting the
   `zemla_photo_registry` option if attachment IDs change after re-upload.
4. MI-M-T page: create a WP page at `/mi-m-t/` and assign template "MI-M-T — Methodology
   Entity Model" — or let `zemla_seed_mi_m_t_page()` auto-create it on first load.

---

## Files Changed

| File | Change |
|------|--------|
| `page-templates/page-mi-m-t.php` | NEW — MI-M-T entity model page template |
| `page-templates/page-art-topic.php` | FIX — Z-09 multilingual lead guard |
| `functions.php` | ARCH-01/02, Mermaid enqueue, seeders (mi-m-t, zen-arts, photo registry, meta box) |
| `style.css` | v1.6.2; A-F1-01 Noto Serif JP; Z-02 gallery CSS fixes |
| `CHANGELOG.md` | Updated v1.6.0–v1.6.2 |

**Full changelog:** see `CHANGELOG.md` in the theme package.
