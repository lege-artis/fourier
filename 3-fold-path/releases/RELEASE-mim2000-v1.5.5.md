# mim2000-theme v1.5.5 — Release Notes
**Date:** 2026-03-21
**Tag:** `v1.5.5`
**Asset:** `mim2000-theme-v1.5.5.zip`

Port of the Noto Serif JP activation fix from zemla-theme v1.6.1 (A-F1-01).

---

## What's New

### A-F1-01 PORT — Noto Serif JP global activation

**Root cause:** WordPress `language_attributes()` outputs the WP site locale (`html[lang]`),
not the active cookie locale. The `:lang(ja)` CSS selector never fired for JA users because
the site locale remained `cs_CZ`/`en_US` regardless of cookie selection.

**Fix:**

- `mim_html_lang_attribute(string $output): string` — filters `language_attributes` hook;
  overrides `<html lang="...">` to match active `mim_lang` cookie locale
  (BCP 47 mapping: `en → en`, `cs → cs`, `ja → ja`, `de → de`, `it → it`)
- `mim_body_lang_class(array $classes): array` — filters `body_class` hook;
  adds `lang-{code}` body class on every page load (reliable cross-browser fallback
  for browsers that don't honour `html[lang]` overrides)
- `style.css`: `.lang-ja, :lang(ja) { font-family: "Noto Serif JP", "Yu Mincho", "YuMincho", serif; }`
  — activates Noto Serif JP via both selector paths simultaneously

Port source: zemla-theme v1.6.1 / A-F1-01 (same root cause across all 3-fold-path sites).

---

## Upgrade Notes

Deploy `mim2000-theme-v1.5.5.zip` via WordPress > Appearance > Themes or FTP. No seeder
action required — filter hooks activate immediately on deploy.

---

## Files Changed

| File | Change |
|------|--------|
| `functions.php` | ADD `mim_html_lang_attribute()` + `mim_body_lang_class()` |
| `style.css` | v1.5.5; ADD `.lang-ja, :lang(ja)` Noto Serif JP rule |
| `CHANGELOG.md` | Updated v1.5.5 |
