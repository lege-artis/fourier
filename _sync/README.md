# Sync Layer — ThinkPad ↔ MacBook

## Quick Sync Procedure

### ThinkPad (start of session)
```bash
git pull origin main
git checkout -b thinkpad-dev   # or rebase existing
```

### MacBook (start of session)
```bash
git pull origin main
```

### End of session — ThinkPad
```bash
git add TASKS.yaml <project>/TASKS.yaml
git commit -m "ThinkPad: <date> session update"
git push origin thinkpad-dev
# Open PR or merge to main via MacBook
```

### End of session — MacBook
```bash
git add .
git commit -m "MacBook: <date> — task sync + deliverables"
git push origin main
```

---

## Claude Session Sync (manual bootstrap)

When starting a new Claude session on either device:

1. Open `TASKS.yaml` from workspace root
2. Paste relevant sections into Claude chat with prompt:
   > "Here is the current master task list. Continue from where we left off on [ThinkPad/MacBook]."
3. Claude will update task statuses and generate session notes in `_sync/session-log.yaml`

---

## Sync Status Flags (used in TASKS.yaml)

| Flag                   | Meaning                                      |
|------------------------|----------------------------------------------|
| `sync_status: current` | Both devices have pulled latest main         |
| `sync_status: pending-macbook-merge` | ThinkPad has changes not yet on MacBook |
| `sync_status: pending-thinkpad-pull` | MacBook updated, ThinkPad needs pull   |
| `sync_status: conflict` | Manual merge required                       |

---

*Workspace initialised: 2026-03-21 on ThinkPad*
