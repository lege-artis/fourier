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
branch: main    → stable, both devices pull
branch: thinkpad-dev → ThinkPad working branch
branch: macbook-main → MacBook working branch
```

Merge strategy: **MacBook merges into main**; ThinkPad rebases from main before each dev session.

---

*Last updated: 2026-03-21 | Device: ThinkPad*
