# RELEASE NOTES — mim2000.cz v1.5.6 | HOTFIX GAL-D01

**Release type:** Hotfix patch
**Version:** 1.5.6
**Previous:** 1.5.5 (A-F1-01 Noto Serif JP port)
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
- [ ] All applicable locales verified
- [ ] Safari + Chrome + Firefox regression pass
- [ ] No conflicts with v1.5.5 Noto Serif JP changes
- [ ] No conflicts with v1.2.1 fp-mobile-nav mobile grid (verify gallery/mobile-nav coexistence at ≤480px)
