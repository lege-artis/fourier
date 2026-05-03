# Hand-off Commit & Push Checklist — v0.1
## Exact commands for the operator to commit + push the v0.2 inception package to GitHub

**Version:** v0.1.0
**Audience:** the human operator (Petr) executing the formal hand-off.
**Branch:** `macbook` (Opus output goes on the MacBook branch per KB-034).
**Token budget:** ONE push at the end (per `GITHUB-TOKEN-POLICY.md` ≈ 800 tokens/month).
**Estimated time:** 5–10 minutes including the read-back verification.

---

## §0. Pre-flight (verify before staging)

Run from the workspace root (`VibeCodeProjects/`):

```bash
# 1. Confirm you are on the macbook branch
git rev-parse --abbrev-ref HEAD
# expect: macbook

# 2. Confirm credentials file is gitignored (must NOT be committed)
git check-ignore _config/credentials.yaml
# expect: _config/credentials.yaml   (i.e. it IS ignored)
# if EMPTY output → STOP; add `_config/credentials.yaml` to .gitignore first

# 3. Look at what's about to be committed (sanity scan)
git status --short
```

**Stop conditions** (do not proceed if any of these):
- Branch is not `macbook` → `git checkout macbook` first.
- `credentials.yaml` is NOT gitignored → add to `.gitignore`, commit that fix separately.
- Any `?? code/` paths show up that you don't recognise → triage first; don't bulk-add.

---

## §1. Stage the v0.2 inception package

Stage in two batches for clean commit messages.

### §1.1 Batch A — strategic + planning docs (the new files)

```bash
git add \
    _config/OPUS-CYCLE-v0.2-MASTER.md \
    _config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md \
    _config/GITHUB-ORCH-V0.2.md \
    _config/HANDOVER-V0.2-THINKPAD.md \
    _config/HANDOVER-V0.2-MACBOOK.md \
    _config/OPUS-NEXT-SESSION-TRIGGERS.md \
    _config/PHYSICS-NUMERICAL-METHODS-v0.1.md \
    _config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md \
    _config/HANDOVER-COMMIT-CHECKLIST-v0.1.md \
    _config/OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md \
    _config/SESSION-START-CHEAT-SHEET-v0.1.md \
    3-fold-path/backlog/MI-M-T-V0.2-POC-ONPREM-SCOPE.md \
    3-fold-path/backlog/MIM2000-ALPHA-V0.2.md \
    3-fold-path/backlog/KH-SIM-PUBLIC-V0.1.md \
    3-fold-path/backlog/PHYSICS-CALIBRATION-MODELS-v0.1.md \
    3-fold-path/backlog/ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md \
    3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md \
    3-fold-path/backlog/OPEN-QUESTIONS-LOG.md
```

### §1.2 Batch B — in-place edits (the rename + Opus pointer)

```bash
git add \
    MANIFEST.yaml \
    _config/OPUS-SESSION-PREP-MI-M-T-PROD.md \
    3-fold-path/code/mi_m_t/pyproject.toml \
    3-fold-path/code/mi_m_t/mi_m_t/main.py
```

### §1.3 Verify staged set (no surprises)

```bash
git status --short
# expected:
#   A   _config/OPUS-CYCLE-v0.2-MASTER.md
#   A   _config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md
#   ... (all the new files: A status)
#   M   MANIFEST.yaml
#   M   _config/OPUS-SESSION-PREP-MI-M-T-PROD.md
#   M   3-fold-path/code/mi_m_t/pyproject.toml
#   M   3-fold-path/code/mi_m_t/mi_m_t/main.py

# Sanity: NO `??` lines should remain among the v0.2.x docs.
# `??` lines for credentials.yaml or other unrelated files are OK to leave unstaged.
```

---

## §2. Commit (two commits)

### §2.1 Commit A — strategic + planning docs

```bash
git commit -m "feat(opus-v0.2): inception package for cycle 2

Adds the strategic + planning artefacts produced in the MacBook/Opus
session 2026-05-03:

Master plan + addendum:
  • _config/OPUS-CYCLE-v0.2-MASTER.md          (master strategic plan)
  • _config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md (Stage 0/1/2 + topologies)

Track-specific scopes (3-fold-path/backlog/):
  • MI-M-T-V0.2-POC-ONPREM-SCOPE.md            (Track 1 PoC)
  • MIM2000-ALPHA-V0.2.md                       (Track 2 Alpha redesign)
  • KH-SIM-PUBLIC-V0.1.md                       (Track 3 public release)
  • PHYSICS-CALIBRATION-MODELS-v0.1.md          (Track PHYS, 3 models)
  • ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md        (Track ZP)
  • GRAPHICAL-COMPONENTS-MANUAL-v0.1.md         (design system + components)

Numerical methods + governance + handovers (_config/):
  • PHYSICS-NUMERICAL-METHODS-v0.1.md           (Track NUM, 4-channel μS)
  • PRIORITY-MATRIX-GOVERNANCE-v0.1.md          (Sev × Urg → Pri + DOCK + Mode 3)
  • GITHUB-ORCH-V0.2.md                         (repo topology + sync)
  • HANDOVER-V0.2-THINKPAD.md (v0.2.3)          (paste-ready ThinkPad prompt)
  • HANDOVER-V0.2-MACBOOK.md (v0.2.3)           (paste-ready MacBook prompt)
  • OPUS-NEXT-SESSION-TRIGGERS.md               (when to call Opus back)
  • HANDOVER-COMMIT-CHECKLIST-v0.1.md           (this checklist)
  • OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md         (tight-loop cadence)
  • SESSION-START-CHEAT-SHEET-v0.1.md           (operator one-page reference)

Bootstrap:
  • 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md   (seeded with 41 retro-tagged OQs)

Cycle 2 hand-off ready. Sonnet sessions open from
SESSION-START-CHEAT-SHEET §1; tight Opus feedback per
OPUS-FEEDBACK-LOOP-PROTOCOL §2."
```

### §2.2 Commit B — in-place rename + Opus pointer

```bash
git commit -m "refactor(mi-m-t): rename to Meta Informed/Inferred/Integrated Measurement (which do) Testing

Rename MI-M-T expansion across 4 files (per OPUS-CYCLE-v0.2-MASTER §1):
  • MANIFEST.yaml — full_name + 3 modes block + revised positioning
  • _config/OPUS-SESSION-PREP-MI-M-T-PROD.md — historical-context note +
    supersession pointer to OPUS-CYCLE-v0.2-MASTER.md
  • 3-fold-path/code/mi_m_t/pyproject.toml — package description
  • 3-fold-path/code/mi_m_t/mi_m_t/main.py — FastAPI description string

Old expansion 'Methodology for Integrated Manual Testing' is preserved
in two deliberate historical references (OPUS-SESSION-PREP §3.1 +
OPUS-CYCLE-v0.2-MASTER §0) with explicit supersession marker."
```

---

## §3. Push (single push; observe token budget)

```bash
git push origin macbook
# expect: "* [new commit] macbook -> macbook" or similar
# tokens used: ≈ 2 (one push, two commits batched)
```

If push fails with **non-fast-forward** (origin/macbook moved while you worked):

```bash
git fetch origin
git pull --rebase origin macbook
# resolve any conflicts (likely none — macbook authority in this session)
git push origin macbook
```

If push fails with **branch protection rejection**:
- Check the GitHub UI rule on the `macbook` branch.
- Per `_config/GITHUB-ORCH-V0.2.md` §3.1, the `macbook` branch requires that the pusher's SSH key fingerprint matches MacBook's `J7xkMdGfpsTbw7tCNrnAMc0yfOnm/O4QRrT+4l+1MPQ`.
- If you're pushing from a different identity, switch SSH config or generate a temporary exception (then revert).

---

## §4. Post-push verification

```bash
# 1. Confirm origin caught up
git log -2 --oneline origin/macbook
# expect to see both commits at HEAD

# 2. Tag the v0.2 inception state for easy reference (optional but recommended)
git tag -a opus-v0.2-handover -m "Opus cycle 2 inception package; ready for parallel Sonnet sessions"
git push origin opus-v0.2-handover

# 3. (Optional) Open a draft PR macbook → main as the integration point
gh pr create \
    --base main \
    --head macbook \
    --draft \
    --title "Opus cycle 2 inception (v0.2)" \
    --body "Strategic + planning artefacts for the v0.2 cycle. Merge after the first round of Sonnet iterations confirms the plan holds."
```

---

## §5. Notify the parallel Sonnet sessions

GitHub-mediated sync is now live. The two Sonnet sessions can be opened any time after the push completes.

### §5.1 ThinkPad Sonnet — opening sequence

1. On the **ThinkPad**, in the local clone of `VibeCodeProjects`:
   ```bash
   git fetch origin
   git checkout thinkpad
   git pull origin thinkpad
   git log -2 --oneline origin/macbook   # see Opus cycle 2 commits
   ```
2. Open Claude Code (`claude-sonnet-4-6`) in the workspace folder.
3. Paste the §1 prompt from `_config/HANDOVER-V0.2-THINKPAD.md`.

### §5.2 MacBook Sonnet — opening sequence

The MacBook is currently the Opus host. To open the MacBook *Sonnet* session, exit this Opus session and either:

- Open a fresh Claude Sonnet session pointing at the same workspace, OR
- If you prefer to keep Opus available for the tight feedback loop (per §6 below): open Claude Sonnet on a *different* identity / window, with the workspace mounted.

Then:
1. Confirm `git rev-parse --abbrev-ref HEAD` outputs `macbook` and `git status` is clean (Opus has just pushed).
2. Paste the §1 prompt from `_config/HANDOVER-V0.2-MACBOOK.md`.

---

## §6. After parallel Sonnets are running — tight Opus feedback loop

See `_config/OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md` for the full protocol. TL;DR:

| Trigger | Cadence | Action |
|---------|---------|--------|
| Daily morning check | Once per day | Open Opus; pull both branches; review last 24h commits + new OQs; produce a "morning brief" comment |
| End-of-iteration close | Every iteration close | Sonnet pushes; Opus reviews within ≤ 4 h |
| HIGH/A-priority OQ raised | Within hour | Opus opens immediately (per OPUS-NEXT-SESSION-TRIGGERS §1.1) |
| Weekly retrospective | Once per week (Friday) | Opus produces a week-summary + adjusts plan |

---

## §7. Status footer

| Item | Value |
|------|-------|
| Document | `HANDOVER-COMMIT-CHECKLIST-v0.1.md` |
| Output position | `_config/HANDOVER-COMMIT-CHECKLIST-v0.1.md` |
| Files in Batch A (new) | 18 |
| Files in Batch B (in-place edits) | 4 |
| Commits | 2 |
| Pushes | 1 (token-budget safe) |
| Tag (recommended) | `opus-v0.2-handover` |
| Status | v0.1 — execute now to formally hand off |

---

*HANDOVER-COMMIT-CHECKLIST-v0.1.md — 2026-05-03 — MacBook CoWork session — Opus*
