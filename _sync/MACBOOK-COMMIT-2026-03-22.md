# MacBook Commit Package — 2026-03-22
**Session:** CoWork brainstorm + hotfix triage + epic planning
**TASKS.yaml version:** 1.3.0
**Branch:** macbook → merge to main when GEN-008 complete

---

## Commit Command (run after `macbook-bootstrap.sh` completes GEN-008)

```bash
cd ~/Documents/VibeCodeProjects

# Pull latest ThinkPad state first
git fetch origin
git merge origin/main

# Stage MacBook session files
git add TASKS.yaml
git add 3-fold-path/backlog/
git add 3-fold-path/hotfix/
git add 3-fold-path/releases/
git add 8gsp/8GSP-SESSION-HANDOFF-2026-03-21.md
git add _config/MACBOOK-GITHUB-SETUP.md
git add _config/macbook-bootstrap.sh
git add _sync/MACBOOK-COMMIT-2026-03-22.md

# Commit
git commit -m "feat(macbook): GAL-D01 hotfix package + MOB-E01 epic + TASKS v1.3.0 — MacBook session 2026-03-22"

# Push to macbook branch
git push origin macbook
```

---

## Files in This Commit

| File | Change type | Description |
|------|-------------|-------------|
| `TASKS.yaml` | Updated (v1.2.0 → v1.3.0) | MacBook session merged, MAC-S01 task added |
| `3-fold-path/backlog/PROJECT-PLAN-3fold-path-active-backlog.md` | New | Full hotfix + sprint sequencing plan, MI-M-T decoded |
| `3-fold-path/backlog/BACKLOG-MOB-E01-mobile-optimization-bodyterapie.md` | New | Epic with 9 user stories across 3 sites |
| `3-fold-path/hotfix/HOTFIX-GAL-D01-defect-report.md` | New | P1 defect: gallery layout + CSS fix spec |
| `3-fold-path/releases/RELEASE-zemla-v1.6.3-HOTFIX-GAL-D01.md` | New | Hotfix release note stub — zemla v1.6.3 |
| `3-fold-path/releases/RELEASE-mim2000-v1.5.6-HOTFIX-GAL-D01.md` | New | Hotfix release note stub — mim2000 v1.5.6 |
| `3-fold-path/releases/RELEASE-bodyterapie-v1.1.6-HOTFIX-GAL-D01.md` | New | Hotfix release note stub — bodyterapie v1.1.6 |
| `8gsp/8GSP-SESSION-HANDOFF-2026-03-21.md` | New | Sprint handoff doc from MacBook session 2026-03-21 |
| `_config/MACBOOK-GITHUB-SETUP.md` | New | Step-by-step GitHub SSH + clone guide for MacBook |
| `_config/macbook-bootstrap.sh` | New | Automated MacBook SSH + clone bootstrap script |

---

## Next Actions After Commit

1. **Merge macbook → main** once GEN-008 confirmed clean
2. **Run GAL-D01-INV** — open DevTools on zemla.org/galerie, confirm CSS root cause
3. **GEN-007 follow-up** — confirm ThinkPad initial repo (468b993) is visible on GitHub before merging
4. **GH-UPL-01/02/03** — upload theme zips to GitHub Releases once GEN-008 active

---

## MI-M-T Decoded (carry forward note)

**Project:** `4-step-noble-steps-to-MI-M-T`
- Step 1 (D-01): ✅ Done — zemla v1.6.2 (Mermaid classDiagram, 5-locale seeder, page template)
- Step 2 (MI-M-T-D02): ⬜ Pending — scope to confirm in next sprint
- Steps 3–4: ⬜ Deferred
