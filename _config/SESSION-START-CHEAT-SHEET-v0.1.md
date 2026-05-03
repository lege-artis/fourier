# Session-Start Cheat Sheet — v0.1
## One-page operator reference for opening parallel Sonnet sessions + Opus feedback loop

**Print or pin near the workstation. Everything you need on one page.**

---

## The four hands you'll be running

```
   ┌──────────────────────────────────────────────────────────────┐
   │  ROLE        │  HOST       │  BRANCH         │  WHAT IT DOES  │
   ├──────────────┼─────────────┼─────────────────┼────────────────┤
   │  Operator    │  any        │  none           │  push, merge,   │
   │  (Petr)      │             │                 │  open sessions  │
   ├──────────────┼─────────────┼─────────────────┼────────────────┤
   │  Opus        │  MacBook    │  opus-feedback  │  daily brief,   │
   │  analyst     │             │                 │  amendments,    │
   │              │             │                 │  retros         │
   ├──────────────┼─────────────┼─────────────────┼────────────────┤
   │  Sonnet TP   │  ThinkPad   │  thinkpad       │  PoC, NUM,     │
   │              │             │                 │  PHYS, GRX-PHY  │
   ├──────────────┼─────────────┼─────────────────┼────────────────┤
   │  Sonnet MB   │  MacBook    │  macbook        │  themes, MIM,   │
   │              │             │                 │  PHIL, KH-02    │
   └──────────────────────────────────────────────────────────────┘
```

---

## 1. Hand-off (one-time, do this first)

```bash
cd VibeCodeProjects
git rev-parse --abbrev-ref HEAD              # expect: macbook
git status --short                             # confirm what's about to commit
# Run §1 + §2 + §3 of _config/HANDOVER-COMMIT-CHECKLIST-v0.1.md
git push origin macbook                       # ONE push; uses ~2 tokens

# Bootstrap the opus-feedback branch:
git checkout -b opus-feedback macbook
git push -u origin opus-feedback              # 1 token

# Optional: tag the hand-off
git tag -a opus-v0.2-handover -m "Opus cycle 2 inception ready for Sonnet"
git push origin opus-v0.2-handover
```

Verify GitHub branch protection rules per `_config/GITHUB-ORCH-V0.2.md` §3.1 are enforced
on `macbook` and `thinkpad`. (One-time UI action.)

---

## 2. Open the ThinkPad Sonnet session

On the **ThinkPad**:
```bash
cd VibeCodeProjects
git fetch origin
git checkout thinkpad
git pull origin thinkpad
git log -2 --oneline origin/macbook        # see Opus cycle 2 commits
```

Open Claude Code (`claude-sonnet-4-6`); paste **§1 of `_config/HANDOVER-V0.2-THINKPAD.md`** verbatim.

First iteration: **NUM-KH-FOR-01** (Fortran reference watermark for Kelvin-Helmholtz, Step 1 of 9 — constants + grid + FFT wrappers).
Alternative if the operator prefers PoC-first: **PoC-01** (testcases v2 + Topology B entrypoint).

---

## 3. Open the MacBook Sonnet session

On the **MacBook** (this device — exit Opus or open in a separate window):
```bash
cd VibeCodeProjects
git rev-parse --abbrev-ref HEAD              # expect: macbook
git status --short                             # expect clean
git fetch origin
git pull origin macbook
git log -3 --oneline origin/thinkpad         # read-only check on ThinkPad state
```

Open Claude Sonnet (`claude-sonnet-4-6`); paste **§1 of `_config/HANDOVER-V0.2-MACBOOK.md`** verbatim.

First iteration: **GRX-01** (author `assets/css/design-tokens.css` + `assets/css/fonts.css` per `GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` §3 — this BLOCKS all other theme + frontend work, hence Priority A).
Alternative if user wants user-content review first: **MIM-01** (Projects & Services Alpha copy + OQ resolution).

---

## 4. Tight Opus feedback loop (daily / per-iteration / on-Pri-A-OQ / weekly)

Per `_config/OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md`. Most-common cadence:

```bash
# Daily morning — 10–20 min
git fetch --all
git log --since="24 hours ago" origin/macbook origin/thinkpad
# Open Opus; ask: "Read OQ-LOG + last 50 lines of both SESSION-NOTES;
#                 produce a daily brief: ThinkPad focus / MacBook focus /
#                 decisions needed / things that wait."
# Append brief to 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md §5
git checkout opus-feedback
git commit -am "opus brief: $(date +%F) daily check"
git push origin opus-feedback
```

```bash
# After a Sonnet pushes an iteration close — 10–30 min
git checkout opus-feedback
git fetch --all
git log -3 --oneline origin/<branch>
# Open Opus; ask: "Read SESSION-NOTES section for <iter-id>; verify
#                 validation matrix; approve / amend / block."
git commit + push if amend or block
```

```bash
# A Priority A OQ landed — within 1 hour
git checkout opus-feedback
git fetch --all
grep -A 30 "OQ-NNN" 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md
# Open Opus; ask: "Read OQ-NNN; produce decision; amend any affected scope docs."
git commit + push
# Operator merges opus-feedback → macbook within hours; Sonnet picks up next session.
```

```bash
# Friday afternoon weekly retro — 60–90 min
git fetch --all
git log --since="7 days ago" origin/macbook origin/thinkpad origin/opus-feedback
# Open Opus; ask: "Produce weekly retro per OPUS-FEEDBACK-LOOP §6:
#                 iterations closed, OQs flow, decisions, plan adjustments."
# Save as _config/OPUS-RETRO-WK<NN>.md
git commit + push
gh pr create --base macbook --head opus-feedback --title "Opus retro WK<NN>"
# Merge PR after review
```

---

## 5. Branch authority (DO NOT VIOLATE — KB-034)

```
   ┌──────────────────────────────────────────────────────────────────┐
   │  YOU ARE         │  YOU CAN PUSH TO                              │
   ├──────────────────┼───────────────────────────────────────────────┤
   │  ThinkPad Sonnet │  thinkpad ONLY                                │
   │  MacBook Sonnet  │  macbook ONLY                                 │
   │  Opus session    │  opus-feedback ONLY                           │
   │  Operator        │  may merge opus-feedback → macbook            │
   │                  │  may merge macbook ↔ main via PR              │
   │                  │  may merge thinkpad ↔ main via PR             │
   └──────────────────────────────────────────────────────────────────┘
```

GitHub branch protection rules enforce. If push fails: re-read this table.

---

## 6. Token budget (≈ 800/month)

| Activity | Tokens / event | Tokens / week (est.) |
|----------|:--------------:|:--------------------:|
| Sonnet session close (push) | 1 | ~10–15 |
| Opus daily brief | 1 | ~5 |
| Opus iteration approval | 1 | ~6 |
| Opus Pri-A OQ decision | 1–2 | ~3 |
| Opus weekly retro + PR | 2 | ~2 |
| Operator PR merge | 1 | ~1 |
| **Total weekly** | — | **~30** |
| **Total monthly** | — | **~120** |

Comfortably under 800/month even with the tight loop.

---

## 7. Key documents (in priority of consult)

| When | Read |
|------|------|
| Opening any session | This cheat sheet → relevant HANDOVER (§1 paste-ready prompt) |
| Lost on which iteration | `SESSION-NOTES.md` (your branch) → "Next session opens here" line |
| Lost on which doc to read | `HANDOVER-V0.2-<DEVICE>.md` Step 2 (reading list) |
| Question on priority | `_config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md` §1 (matrix) |
| Question on architecture | `_config/OPUS-CYCLE-v0.2-MASTER.md` (read AMENDMENT box) → `_config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` |
| Question on numerical method | `_config/PHYSICS-NUMERICAL-METHODS-v0.1.md` (per-model section) |
| Question on graphics | `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` |
| Need to call Opus back | `_config/OPUS-NEXT-SESSION-TRIGGERS.md` (find the trigger; assemble package per §2) |
| How does the feedback loop work | `_config/OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md` |
| Existing OQ status | `3-fold-path/backlog/OPEN-QUESTIONS-LOG.md` (grep on Priority) |

---

## 8. Quick "is this normal?" decision tree

```
Sonnet wants to do something the prompt doesn't cover
  ├── Is it a bug / micro-decision in scope? → do it; note in SESSION-NOTES
  ├── Does it touch a forbidden file? → STOP, OQ-NNN, severity HIGH
  └── Does it change scope? → STOP, OQ-NNN with candidate answers, push

Opus daily brief shows nothing happened in 24 h
  ├── Operator on a break? → fine; skip the brief
  └── Both Sonnets blocked? → triage the OPEN-QUESTIONS-LOG; resolve top Priority A

Pri-A OQ raised; Opus session can't open within 1 h
  ├── Sonnet should STOP the affected work-item (per HANDOVER Step 8)
  └── Sonnet may continue non-blocked work on other iterations
```

---

## 9. Status footer

| Item | Value |
|------|-------|
| Document | `SESSION-START-CHEAT-SHEET-v0.1.md` |
| Output position | `_config/SESSION-START-CHEAT-SHEET-v0.1.md` |
| Length | one-page reference |
| Audience | Operator (Petr) |
| Status | print + pin; refresh at v0.3 |

---

*SESSION-START-CHEAT-SHEET-v0.1.md — 2026-05-03 — MacBook CoWork session — Opus*
