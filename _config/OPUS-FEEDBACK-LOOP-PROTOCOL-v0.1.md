# Opus Feedback-Loop Protocol — v0.1
## Tight, GitHub-mediated cadence for Opus ↔ Sonnet sessions during cycle v0.2

**Version:** v0.1.0
**Authority:** Companion to `_config/OPUS-NEXT-SESSION-TRIGGERS.md` (which defines *when* Opus is needed). This doc defines *how* the feedback loop runs — the cadence, the medium, the artefacts each side produces.
**Audience:** the human operator (Petr) running both Opus and Sonnet sessions; the Sonnet sessions themselves (they consume this protocol's expectations).
**Trigger for this protocol:** user direction 2026-05-03 — keep "relatively tight feedback loop with analytical Opus session for this stage of project; GitHub preferred".

---

## §0. The principle

For cycle v0.2, the project is in **inception-to-validation**: lots of plan, lots of new code, lots of decisions that the plan doesn't yet cover. A loose feedback loop (only meet at gates) loses signal — Sonnet drift accumulates, OQs pile up un-answered.

A *tight* feedback loop costs Opus time (a few sessions per week) but removes drift, keeps OQs flowing, and lets the parallel Sonnet sessions stay coordinated without owner intervention.

The medium is **GitHub** (per user direction). Specifically:
- Sonnet writes to its branch + pushes daily;
- Opus pulls both branches, reviews the deltas, and writes back as commits to a special **`opus-feedback`** branch (not in-place on `macbook` or `thinkpad` — keeps authority clean per KB-034);
- The PR `opus-feedback → macbook` carries Opus's responses; both Sonnets read the latest comments before each session.

---

## §1. Cadence (binding for cycle v0.2)

Four trigger types; each has its own cadence + scope:

| # | Trigger | Cadence | Opus session length | What Opus produces |
|:-:|---------|---------|:-------------------:|--------------------|
| **1** | **Daily morning check** | Mon–Fri, ~15 min | 10–20 min | Comment in `OPEN-QUESTIONS-LOG.md` "Daily brief YYYY-MM-DD" |
| **2** | **End-of-iteration close** | Every iteration close (≈ 1–2 per device per day) | 10–30 min | Per-iteration approval / amendment in `SESSION-NOTES.md` |
| **3** | **HIGH / Priority A OQ** | Within ≤ 1 hour of OQ being raised + pushed | 30–60 min | Decision in OQ + amendment to scope doc if needed |
| **4** | **Weekly retrospective** | Friday afternoon | 60–90 min | `_config/OPUS-RETRO-WK<NN>.md` summary + plan adjustment |

If the operator (Petr) cannot run an Opus session for one of these triggers, the trigger queues — Sonnet is allowed to continue *non-blocked* work but must STOP the affected work-item (per `HANDOVER-V0.2-*` Step 8).

---

## §2. Mechanism — GitHub as the medium

### §2.1 The branches involved

Per `_config/GITHUB-ORCH-V0.2.md` §3.1:

| Branch | Owner | Push permission | Role |
|--------|-------|-----------------|------|
| `macbook` | MacBook Sonnet | MacBook only | MacBook tracks: theme work, mim2000 Alpha, philosophy page, KH-02 |
| `thinkpad` | ThinkPad Sonnet | ThinkPad only | ThinkPad tracks: PoC, NUM, PHYS, GRX-PHYSICS, GRX-MIMT |
| `main` | Both via PR | PR-only | Integration |
| **`opus-feedback`** (NEW v0.1) | **Opus session** | Opus only | Opus's responses + amendments without disturbing branch authority |

`opus-feedback` is a **slim branch** — it exists only to carry Opus's responses. It is rebased on `macbook` daily; merged to `macbook` at weekly retrospective; never merged directly to `thinkpad` (ThinkPad pulls amendments via the `macbook → main → thinkpad` flow OR by reading the `opus-feedback` branch directly without merging).

### §2.2 Sonnet → Opus flow (per session close)

Every Sonnet session closes with a push (per `HANDOVER-V0.2-*` Step 8/9). This push is the signal to Opus.

```
ThinkPad / MacBook Sonnet session close
  └── git commit (per Step 9.2 of handover)
  └── git push origin <branch>          (one push per session)
  └── (optional) gh pr comment           — for tight-loop urgent items only
                                           (uses tokens; reserve for HIGH OQs)
```

Sonnet must NOT call Opus directly. The signal is the commit + push.

### §2.3 Opus → Sonnet flow (per response)

```
Opus session opens
  └── git fetch origin
  └── git log --oneline origin/macbook origin/thinkpad   (since last opus-feedback HEAD)
  └── Read: SESSION-NOTES (both), OPEN-QUESTIONS-LOG, recent diff
  └── Produce decisions:
        • Amend a scope doc → commit on opus-feedback
        • Answer an OQ → edit OPEN-QUESTIONS-LOG.md (status: answered) on opus-feedback
        • Open a new OQ → append to OPEN-QUESTIONS-LOG.md on opus-feedback
        • Major plan change → write _config/OPUS-AMENDMENT-vM.N.md on opus-feedback
  └── git push origin opus-feedback
  └── (if amendment must reach ThinkPad immediately):
        gh pr create --base macbook --head opus-feedback --title "Opus brief: YYYY-MM-DD"
        — owner merges into macbook within hours; ThinkPad's daily pull
          picks up the change via main reflow (or directly reading
          origin/opus-feedback at session start)
```

### §2.4 Conflict-prevention rules

- Opus may **read** `macbook` and `thinkpad`; Opus may **not** edit on those branches directly.
- Opus may amend any file on `opus-feedback`; the merge into `macbook` is the operator's call (one merge per day max).
- Sonnet sessions read `opus-feedback` at orientation step (Step 2 of handovers — add to reading list).
- If Sonnet finds an Opus amendment that conflicts with in-flight work on its branch: STOP, file an OQ, surface as a "scope-change-needs-Opus" trigger.

---

## §3. Daily morning check — exact protocol (Trigger #1)

**When:** Mon–Fri, before either Sonnet session opens for the day.
**Duration:** 10–20 minutes Opus session.
**Cost:** ~5–10 GitHub tokens (one fetch + at most one push of opus-feedback).

```
─── DAILY MORNING CHECK ──────────────────────────────────────────────────

Step 1. Fetch + survey
  cd VibeCodeProjects
  git fetch --all
  git log --oneline --since="24 hours ago" origin/macbook origin/thinkpad

Step 2. Scan OPEN-QUESTIONS-LOG
  cat 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md | grep -E "^## OQ-[0-9]+ |Priority:"
  → look for new OQs since yesterday's brief; flag any HIGH / Priority A

Step 3. Scan SESSION-NOTES
  tail -50 3-fold-path/code/SESSION-NOTES.md             (ThinkPad's)
  tail -50 3-fold-path/SESSION-NOTES-MACBOOK.md          (MacBook's)
  → look for "Next session opens here" pointers; verify they're sane

Step 4. Produce the morning brief (5–10 lines)
  Open Opus session; ask:
    "Read OPEN-QUESTIONS-LOG and the last 50 lines of both SESSION-NOTES
     files. Produce a brief: (1) 1-sentence headline of what each Sonnet
     should focus on today; (2) any Priority A OQ that needs my decision
     today; (3) anything that needs to wait for a Mon/Tue (Stage 1 specs)
     or a longer Opus session."

Step 5. Commit + push the brief
  git checkout opus-feedback   (create if missing: git checkout -b opus-feedback macbook)
  Append to 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md a section:
    ## DAILY BRIEF YYYY-MM-DD (Opus)
    ThinkPad focus: <one sentence>
    MacBook focus:  <one sentence>
    Decisions needed today: <list of OQ-NNN, or "none">
    Notes: <anything else>
  git commit -m "opus brief: YYYY-MM-DD daily check"
  git push origin opus-feedback

Step 6. (If a Priority A OQ needs immediate decision)
  Either: produce the decision inline in the brief and amend the OQ; OR
  Open the wider Opus session per §5 below.
```

---

## §4. End-of-iteration approval — exact protocol (Trigger #2)

**When:** Every time a Sonnet closes an iteration (PoC-NN, PHYS-XX-NN, NUM-XX-NN, MIM-NN, PHIL-NN, GRX-NN, KH-NN, DOCK-NN).
**Duration:** 10–30 minutes Opus session.
**Cost:** ~5 GitHub tokens.

```
─── END-OF-ITERATION APPROVAL ────────────────────────────────────────────

Triggered by: a commit on macbook or thinkpad whose message starts with
"<iter-id>:" (e.g. "PoC-01:", "PHYS-KH-01:", "MIM-02:").

Step 1. git pull on the relevant branch
  git checkout opus-feedback     (always work here)
  git fetch --all
  git log -3 --oneline origin/<branch>

Step 2. Read the SESSION-NOTES section for that iteration
  grep -A 50 "<iter-id> — close" <session-notes-file>

Step 3. Verify the validation matrix (per handover §6)
  → pass? amber? red?

Step 4. Decide:
  ✓ Approve  → no commit needed; thumbs-up reaction in chat / email to operator
  ⚠ Amend    → write a 1-paragraph amendment in OPEN-QUESTIONS-LOG.md
              "Iteration <iter-id> review (Opus): <feedback>"
              git commit -m "opus review: <iter-id>"
              git push origin opus-feedback
  ✗ Block    → write a Priority A OQ requesting Sonnet to halt + bounce back
              git commit + push as above
              alert operator out-of-band (chat / email)

Step 5. Update the iteration plan if needed
  If the iteration revealed a scope change, edit the relevant scope doc
  on opus-feedback (e.g. _config/PHYSICS-NUMERICAL-METHODS-v0.1.md):
    git commit -m "opus amendment: <doc> after <iter-id>"
    git push origin opus-feedback
```

---

## §5. HIGH / Priority A OQ — exact protocol (Trigger #3)

**When:** Sonnet pushes an OQ with `Priority: A` (or any HIGH severity in legacy format).
**Duration:** 30–60 minutes Opus session.
**Cost:** ~10 GitHub tokens (more if amendments span multiple docs).
**Latency target:** ≤ 1 hour from push to Opus session opening.

```
─── PRIORITY-A OQ FAST-PATH ─────────────────────────────────────────────

Step 1. The trigger
  Sonnet committed an OQ with Priority A; pushed to its branch.
  Operator notified out-of-band (PR comment / chat).

Step 2. Open Opus session
  Pull both branches; check the OQ in full:
    git checkout opus-feedback
    git fetch --all
    grep -A 30 "OQ-NNN" 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md

Step 3. Read the affected doc(s)
  The OQ template lists "Affects:". Read each in full.

Step 4. Decide
  Use the candidate answers in the OQ as starting points; produce a
  decision with reasoning in 3–10 lines.

Step 5. Amend (one or more)
  • Edit OPEN-QUESTIONS-LOG.md: change status to "answered"; write the
    decision under the OQ.
  • If the decision changes a scope doc: edit it on opus-feedback.
  • If the decision affects the iteration plan: amend the relevant
    plan section on opus-feedback.

Step 6. Commit + push
  git commit -m "opus decision: OQ-NNN — <one-line summary>"
  git push origin opus-feedback

Step 7. Notify
  Operator merges opus-feedback → macbook (or pulls onto thinkpad
  via main if ThinkPad is the affected device).
  Sonnet picks up at next session start.
```

---

## §6. Weekly retrospective — exact protocol (Trigger #4)

**When:** Friday afternoon (or first available slot).
**Duration:** 60–90 minutes Opus session.
**Cost:** ~20 GitHub tokens (multiple commits typical).

```
─── WEEKLY RETROSPECTIVE ────────────────────────────────────────────────

Step 1. Comprehensive pull
  git fetch --all
  git log --oneline --since="7 days ago" origin/macbook origin/thinkpad
  git log --oneline --since="7 days ago" origin/opus-feedback

Step 2. Aggregate state
  • Iterations closed this week: <list>
  • OQs raised this week: <count by priority>
  • OQs answered this week: <count>
  • OQs still open at end of week: <count by priority>
  • Iterations planned for next week: <list>

Step 3. Plan adjustments
  • Promotions / demotions of priority
  • Iteration ordering changes
  • New triggers added to OPUS-NEXT-SESSION-TRIGGERS.md
  • Scope doc amendments

Step 4. Write the retrospective
  Save as _config/OPUS-RETRO-WK<NN>.md (NN = ISO week number).
  Structure:
    §1 Headline (1 sentence)
    §2 Iterations closed (table)
    §3 OQs flow (raised / answered / open)
    §4 Decisions made
    §5 Adjustments to plan
    §6 Next week's focus

Step 5. Commit + push + open PR
  git commit -m "opus retro WK<NN>: <headline>"
  git push origin opus-feedback
  gh pr create --base macbook --head opus-feedback \
       --title "Opus retro WK<NN>" --body "See _config/OPUS-RETRO-WK<NN>.md"

Step 6. Operator merges PR; macbook picks up the amendments;
        thinkpad pulls via main reflow over the weekend.
```

---

## §7. Token budget under tight loop

Per `GITHUB-TOKEN-POLICY.md` ≈ 800 tokens/month. Estimating:

| Cadence | Sessions per week | Tokens per session | Tokens per week |
|---------|:-----------------:|:------------------:|:---------------:|
| Daily morning check | 5 | ~7 | ~35 |
| End-of-iteration approval | ~6 (avg 3 ThinkPad + 3 MacBook iters/wk) | ~5 | ~30 |
| HIGH OQ fast-path | ~2 (estimated) | ~10 | ~20 |
| Weekly retrospective | 1 | ~20 | ~20 |
| **Total per week** | — | — | **~105** |
| **Total per month** | — | — | **~420** |

Comfortably under the ~800/month budget. Leaves ~380 tokens/month for the Sonnet sessions themselves (their session-close pushes).

If push count per week consistently exceeds the projection → Opus produces fewer in-place amendments and more "queue for weekly retro" entries.

---

## §8. Quick-reference: who does what when

```
┌──────────────────────────────────────────────────────────────────────┐
│ TRIGGER                       │ WHO       │ WHERE          │ TOKENS  │
├───────────────────────────────┼───────────┼────────────────┼─────────┤
│ Sonnet session close          │ Sonnet    │ own branch     │ 1 push  │
│ Opus daily brief              │ Opus      │ opus-feedback  │ 1 push  │
│ Opus iteration approval       │ Opus      │ opus-feedback  │ 1 push  │
│ Opus Pri-A OQ decision        │ Opus      │ opus-feedback  │ 1-2     │
│ Opus weekly retro + PR        │ Opus      │ opus-feedback  │ 2 incl PR│
│ Operator PR merge             │ Operator  │ macbook        │ 1       │
│ ThinkPad pull (auto)          │ Sonnet    │ thinkpad pull  │ 1 fetch │
│ MacBook pull (auto)           │ Sonnet    │ macbook pull   │ 1 fetch │
└──────────────────────────────────────────────────────────────────────┘
```

---

## §9. Status footer

| Item | Value |
|------|-------|
| Document | `OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md` |
| Output position | `_config/OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md` |
| Cadence triggers defined | 4 |
| GitHub branches involved | 4 (macbook + thinkpad + main + opus-feedback) |
| Estimated token spend | ~105/wk → ~420/mo (well under 800/mo budget) |
| Bootstrap requirement | Operator creates `opus-feedback` branch on first daily-brief: `git checkout -b opus-feedback macbook && git push -u origin opus-feedback` |
| Status | v0.1 — binding for cycle v0.2 |

---

*OPUS-FEEDBACK-LOOP-PROTOCOL-v0.1.md — 2026-05-03 — MacBook CoWork session — Opus*
