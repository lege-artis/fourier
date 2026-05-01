# Device Configuration — Dual-Node Workspace

## Node Registry

| Codename  | Hardware  | OS           | Primary Role             | Browser Target       |
|-----------|-----------|--------------|--------------------------|----------------------|
| ThinkPad  | Lenovo    | Windows      | Development + Sandbox    | Chrome (Windows)     |
| MacBook   | Apple     | macOS        | Analytics + Coordination | Safari (macOS)       |

---

## ThinkPad — Responsibilities

- **Development**: Active coding, refactoring, integration builds across all projects
- **Testing infrastructure**: Runs all sandbox environments (Docker, local services, emulators)
- **Browser target**: Windows Chrome — functional, regression, and integration test execution
- **Platforms in scope**: Web/browser, API/backend services, Desktop/Electron

## MacBook — Responsibilities

- **Analytics**: Primary analytical review, reporting, deliverable authoring
- **Coordination**: Master task list ownership, documentation publishing
- **Browser target**: macOS Safari — cross-browser compatibility and rendering validation
- **Platforms in scope**: Web/browser, API/backend services, Desktop/Electron (read-only review)

---

## Sync Protocol

| Asset                  | Source of Truth | Sync Method              | Frequency        |
|------------------------|-----------------|--------------------------|------------------|
| Task lists (`*.yaml`)  | MacBook         | Git push/pull            | Per session      |
| Documentation (`*.md`) | MacBook         | Git push/pull            | Per deliverable  |
| Test configs           | ThinkPad        | Git push/pull            | Per test run     |
| Deliverables (`*.docx`)| MacBook         | Git LFS or cloud storage | Per release      |
| Claude session context | Per-device      | Manual paste / export    | Per session init |

---

## Git Remote Convention

```
remote: origin  → shared repo (GitHub / GitLab)
branch: main    → stable, both devices pull (PR only — no direct push)
branch: macbook → MacBook working branch — MacBook push authority ONLY
branch: thinkpad → ThinkPad working branch — ThinkPad push authority ONLY
```

Merge strategy: **MacBook merges into main**; ThinkPad rebases from main before each dev session.

---

## Branch Authority Rules (MANDATORY — established 2026-05-02)

**Rule:** Each device owns its branch exclusively. Cross-device push is prohibited.

| Branch   | Push authority | Direct push | Notes |
|----------|---------------|-------------|-------|
| main     | Neither       | Prohibited  | PR merge only |
| macbook  | MacBook only  | Prohibited for ThinkPad | GitHub branch protection required |
| thinkpad | ThinkPad only | Prohibited for MacBook  | GitHub branch protection required |

**Enforcement:** GitHub branch protection rules (Settings → Branches).
`merge=ours` in `.gitattributes` is a merge hint only — it does NOT prevent force-push.
Branch protection is the hard enforcement layer.

**Setup (owner action required — one time):**
```
GitHub → Settings → Branches → Add rule
  Branch name pattern: macbook
  ☑ Restrict pushes that create matching branches
  (or: require pull request before merging)
Repeat for: thinkpad
```

**Background:** ThinkPad force-pushed `macbook` twice in session 2026-05-02
(`+ 2eb73f3...1364eb8 forced update`), reverting `queue-macbook.yaml` and
generating merge conflicts in CI workflow files. See KB-034 in KB-LESSONS-LEARNED.yaml.

---

*Last updated: 2026-05-02 | Device: MacBook*
