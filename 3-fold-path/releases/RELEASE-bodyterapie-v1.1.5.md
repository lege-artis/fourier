# bodyterapie-theme v1.1.5 — Release Notes
**Date:** 2026-03-21
**Tag:** `v1.1.5`
**Asset:** `bodyterapie-theme-v1.1.5.zip`

Port of the Noto Serif JP activation fix from zemla-theme v1.6.1 (A-F1-01).

---

## What's New

### A-F1-01 PORT — Noto Serif JP global activation

**Root cause:** Same as zemla/mim2000 — WordPress `language_attributes()` outputs the WP
site locale, not the active cookie locale. The `:lang(ja)` CSS selector never fired for
JA users on bodyterapie.com.

**Fix:**

- `bth_html_lang_attribute(string $output): string` — filters `language_attributes` hook;
  overrides `<html lang="...">` to match active `bth_lang` cookie locale
  (BCP 47 mapping: `en → en`, `cs → cs`, `ja → ja`, `de → de`; 4 active langs — no IT)
- `bth_body_lang_class(array $classes): array` — filters `body_class` hook;
  adds `lang-{code}` body class on every page load
- `style.css`: `.lang-ja, :lang(ja) { font-family: var(--3fp-noto-serif-jp); }`
  — uses existing `--3fp-noto-serif-jp: 'Noto Serif JP', 'Yu Mincho', serif` CSS variable

Note: bodyterapie has 4 active locales (EN/CS/JA/DE) — no IT, consistent with
`bth_active_langs()` definition. Lang map accordingly has 4 entries.

Port source: zemla-theme v1.6.1 / A-F1-01.

---

## Upgrade Notes

Deploy `bodyterapie-theme-v1.1.5.zip` via WordPress > Appearance > Themes or FTP.
No seeder action required.

---

## Files Changed

| File | Change |
|------|--------|
| `functions.php` | ADD `bth_html_lang_attribute()` + `bth_body_lang_class()` |
| `style.css` | v1.1.5; ADD `.lang-ja, :lang(ja)` Noto Serif JP rule via CSS variable |
| `CHANGELOG.md` | Updated v1.1.5 |
