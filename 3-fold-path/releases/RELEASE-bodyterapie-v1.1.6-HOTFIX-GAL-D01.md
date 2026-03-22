# RELEASE NOTES — bodyterapie.com v1.1.6 | HOTFIX GAL-D01

**Release type:** Hotfix patch
**Version:** 1.1.6
**Previous:** 1.1.5 (A-F1-01 port, 4-lang, CSS variable)
**Date:** TBD — pending fix implementation
**Priority:** P1 Critical

---

## Changes

### GAL-D01 — Gallery contracted layout + missing descriptions [HOTFIX]

- **Fix:** Restored gallery container to full content-area width via 3-fold-path base stylesheet patch
- **Fix:** Restored caption/description visibility on all gallery tile elements
- **Scope:** Shared 3-fold-path library fix — same patch resolves zemla, mim2000, bodyterapie simultaneously
- **Root cause:** [to be confirmed during implementation — see HOTFIX-GAL-D01-defect-report.md]

---

## Validation

- [ ] Gallery full-width confirmed: desktop / tablet / mobile
- [ ] Captions visible across all tile types
- [ ] All 4 language variants verified: CS / EN / DE / (+ others)
- [ ] Safari + Chrome + Firefox regression pass
- [ ] No conflicts with v1.1.5 CSS variable baseline
- [ ] CSS variables remain single source of truth — no hardcoded values introduced
