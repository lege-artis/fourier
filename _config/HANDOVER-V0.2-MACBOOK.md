# HANDOVER v0.2.3 — MacBook Sonnet (DETAILED SCRIPT)
## Self-contained, paste-ready prompt for the MacBook Sonnet session
## Owns Track 2 (mim2000.cz Alpha), Track ZP (zemla philosophy + physics page hookups), Track 3 tail (KH-02 LinkedIn), Track GRX-MIM/BOD (theme revisions per `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md`)

**Version:** v0.2.3 (2026-05-03 — adds Track GRX-MIM/BOD + design tokens + Priority Matrix governance to v0.2.2 detailed-script)
**Authority:** MacBook-side hand-off from Opus session 2026-05-03.

> **What v0.2.3 adds beyond v0.2.2:**
> - **Track GRX-MIM** (mim2000-theme v1.10.0 revision per `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` §4 — font system + sandstone pattern + spacing) merged into Track 2 MIM-02 build.
> - **Track GRX-BOD** (bodyterapie-theme v1.8.0 revision per `3-fold-path/backlog/GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` §5 — same revisions + nav simplification + content-hierarchy work).
> - **Track GRX-01/02** (design-tokens.css + self-hosted fonts) — prerequisite for all theme bumps.
> - **Priority Matrix governance** locked (per `_config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md`) — every OQ, iteration, and deliverable carries Severity × Urgency → Priority.
> - **Constraint addition:** every CSS file MUST `@import "design-tokens.css"` and use the variables — no hard-coded colour, font, spacing, or breakpoint values.
**Use:** Copy §1 (everything between `BEGIN PROMPT` and `END PROMPT` markers) verbatim into a fresh Claude Sonnet session on the MacBook with file/bash tools and the workspace mounted.
**Companion:** `_config/HANDOVER-V0.2-THINKPAD.md` (paired session on ThinkPad); `_config/OPUS-NEXT-SESSION-TRIGGERS.md` (when to bounce back).

---

## §0. Pre-flight (operator side)

- **Model:** `claude-sonnet-4-6`.
- **Workspace:** `VibeCodeProjects/` mounted; sub-paths `_config/`, `3-fold-path/`, `MANIFEST.yaml`, `CLAUDE.md` visible.
- **Tools required:** Read / Write / Edit / Grep / Glob / bash. **Optional but useful for Track ZP:** Claude-in-Chrome (for live DOM read of `https://zemla.org/philosophy/`) — if not available, use `curl` from bash.
- **Branch:** local working branch is `macbook`. Refuses to operate on any other branch.
- **WordPress / theme work:** MacBook does NOT have FTP write access in this session model. Theme changes are produced as `theme-archives/<theme>-vX.Y.Z.zip` artifacts; the user uploads via WP Admin (Tier 1) or applies single-file patches via TFE (Tier 2). Per `_config/HOW-TO-ACTIVE24-DEPLOY.md`.
- **Token budget:** ≤ 1 push per session boundary.

---

## §1. PASTE-READY PROMPT (DETAILED SCRIPT)

```
═══════════════════════ BEGIN PROMPT ════════════════════════════════════════
You are MacBook Sonnet for the MI-M-T project. Iteration cycle v0.2 is in
flight. Your scope is Track 2 (mim2000.cz Projects & Services Alpha
redesign, 3 iterations), Track ZP (zemla.org/philosophy rework + physics
hooks, 3 + 3 iterations), and Track 3 tail (kh-sim public — LinkedIn
copy + zemla.org Physics page link spec). Track 1 (PoC) and Track PHYS
(physics implementation) belong to ThinkPad Sonnet — do not touch their
files.

This prompt is a SCRIPT. Run the steps in order. STOP when a step says
STOP. Do not skip steps.

═════════════════════════════════════════════════════════════════════════════
STEP 1 ── ENVIRONMENT VERIFICATION (mandatory)
═════════════════════════════════════════════════════════════════════════════
Run these commands in the bash sandbox; capture each output:

  1.1   uname -srm                         # expect Darwin
  1.2   git rev-parse --abbrev-ref HEAD    # MUST output "macbook"
  1.3   git status                         # MUST be clean
  1.4   git log -5 --oneline macbook
  1.5   git log -3 --oneline origin/thinkpad   # READ-ONLY check
  1.6   git fetch origin                   # bring remote refs up to date
  1.7   php -v 2>&1 || echo "PHP not present (acceptable on MacBook)"
  1.8   which curl

If 1.2 outputs anything other than "macbook" → STOP. Run
  git checkout macbook
and re-verify.

If 1.3 shows uncommitted changes → STOP. Either commit them under the
prior session's iteration or stash with a named tag.

Append the verification output to a NEW or existing file
3-fold-path/SESSION-NOTES-MACBOOK.md (create if absent) under heading:
"<iter-id> — environment verification".

═════════════════════════════════════════════════════════════════════════════
STEP 2 ── REQUIRED READING (read before any content/theme change)
═════════════════════════════════════════════════════════════════════════════
Read in this order. Do NOT edit any of them in this session.

  ORIENTATION (every session refresh):
   2.1  CLAUDE.md                                        — operating manual
   2.2  MANIFEST.yaml                                    — version registry
   2.3  3-fold-path/SESSION-NOTES-MACBOOK.md             — your prior log
        (read its tail; create with this session if absent)

  STRATEGIC FRAME (re-read on first session of cycle, skim later):
   2.4  _config/OPUS-CYCLE-v0.2-MASTER.md                — read AMENDMENT box at top
   2.5  _config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md     — Stage 0/1/2 + topologies

  TRACK-SPECIFIC (per the iteration you'll run):
   2.6  3-fold-path/backlog/MIM2000-ALPHA-V0.2.md        — Track 2 (mim2000)
   2.7  3-fold-path/backlog/ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md
                                                          — Track ZP
   2.8  3-fold-path/backlog/KH-SIM-PUBLIC-V0.1.md        — Track 3 (your KH-02 piece)
   2.9  3-fold-path/backlog/PHYSICS-CALIBRATION-MODELS-v0.1.md
                                                          — physics narrative + page
                                                            hookup matrix §6

  REFERENCE (consult only when relevant):
   2.10 _config/HOW-TO-ACTIVE24-DEPLOY.md                — Tier 1/2 deploy
   2.11 _config/GITHUB-ORCH-V0.2.md                      — repo topology
   2.12 _config/OPUS-NEXT-SESSION-TRIGGERS.md            — when to bounce back

After reading, write a single paragraph in
3-fold-path/SESSION-NOTES-MACBOOK.md under heading "<iter-id> —
orientation confirmation" stating:
  • the renamed full name of MI-M-T (Meta Informed/Inferred/Integrated
    Measurement (which do) Testing) and the messaging discipline
    (master plan §1.3: do not push Mode 3 idea publicly;
     demonstrate via PoCs)
  • the visual identity invariants (mim2000: dual-layer SVG sandstone-sq
    + brushstone-sq, azure symbols, Ω↔0 corner swap;
     zemla: per CLAUDE.md ADR-01..04 + existing v1.7.5 design)
  • the iteration you will run this session (Step 4)

═════════════════════════════════════════════════════════════════════════════
STEP 3 ── BRANCH AUTHORITY GUARD
═════════════════════════════════════════════════════════════════════════════
Per KB-034:
  • You write commits ONLY to the "macbook" branch.
  • You NEVER `git checkout thinkpad`.
  • You NEVER push to origin/thinkpad.

ThinkPad-owned files (READ permitted, WRITE forbidden):
  • 3-fold-path/code/mi_m_t/**       (Python FastAPI service)
  • 3-fold-path/code/mimt-app/**     (PoC Docker bundle when it lands)
  • 3-fold-path/code/physics-gr/**   (physics package — ThinkPad creates)
  • 3-fold-path/code/physics-ising/** (physics package — ThinkPad creates)
  • 3-fold-path/evidence/testcases.yaml (ThinkPad authors v2)
  • 3-fold-path/evidence/bugs.yaml      (ThinkPad authority)
  • 3-fold-path/code/SESSION-NOTES.md   (ThinkPad authority)
  • kh-sim/**                            (ThinkPad codebase)
  • _config/HANDOVER-V0.2-THINKPAD.md   (ThinkPad's own prompt)
  • _config/migrate-*.py                 (ThinkPad migration scripts)
  • MANIFEST.yaml                        (sync-main.sh authority; merge=ours)

You ARE allowed to write to:
  • 3-fold-path/themes/mim2000-theme/** (build your theme zip artifacts)
  • 3-fold-path/themes/zemla-theme/**   (build your theme zip artifacts)
  • 3-fold-path/theme-archives/         (deliver theme zips here)
  • 3-fold-path/backlog/MIM2000-*.md    (your Track 2 working docs)
  • 3-fold-path/backlog/ZEMLA-*.md      (your Track ZP working docs)
  • 3-fold-path/backlog/KH-02-*.md      (your Track 3 tail drafts)
  • 3-fold-path/SESSION-NOTES-MACBOOK.md (append-only)
  • 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md (append-only)
  • queue-macbook.yaml                   (your task queue)
  • _config/HANDOVER-V0.2-MACBOOK.md    (this prompt's home)

If you find yourself wanting to edit a forbidden file → STOP. Open OQ-NNN
severity HIGH titled "branch-authority collision: <file>".

═════════════════════════════════════════════════════════════════════════════
STEP 4 ── CHOOSE THIS SESSION'S ITERATION (decision tree)
═════════════════════════════════════════════════════════════════════════════
Read the last "Next session opens here" line from
3-fold-path/SESSION-NOTES-MACBOOK.md. If absent, use this decision tree:

  IF MIM-01 has not run yet:
        → run MIM-01 (the user-content + OQ resolution iteration)

  IF MIM-01 closed AND MIM-02 not yet run AND OQ-200..203 are answered:
        → run MIM-02 (build mim2000-theme v1.10.0 zip)

  IF MIM-02 zip ready, MIM-03 awaiting user upload:
        → run KH-02 (LinkedIn portfolio copy + zemla.org Physics link spec)

  IF MIM-03 deployed AND PHIL-01 not yet run:
        → run PHIL-01 (live DOM read of zemla.org/philosophy/ +
          ZEMLA-PHILOSOPHY-PAGE-REWORK §1 verification)

  IF PHIL-01 closed AND OQ-PHIL-01..05 are answered:
        → run PHIL-02 (build zemla-theme v1.7.6 with hook block + JSON +
          template part + CSS + translations)

  IF ThinkPad's PHYS-KH-01 just closed AND PHIL-03 deployed:
        → run PHIL-04A (JSON update for KH card — flip pending→ready)

  Same trigger for PHIL-04B (after PHYS-GR-02) and PHIL-04C (after PHYS-IS-02).

  IF none of the above clearly fires (ambiguity):
        → write a question paragraph in SESSION-NOTES-MACBOOK.md under
          "Iteration choice ambiguity" and STOP.

Record the chosen iteration as <iter-id> in SESSION-NOTES-MACBOOK.md
under heading "<iter-id> — plan" with a 3-line plan
(goal, deliverables, validation).

═════════════════════════════════════════════════════════════════════════════
STEP 5 ── EXECUTE THE ITERATION
═════════════════════════════════════════════════════════════════════════════
Find the iteration's row in the relevant scope doc:
  • MIM-01 / MIM-02 / MIM-03    → MIM2000-ALPHA-V0.2.md §5
  • PHIL-01..PHIL-04C            → ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md §7
  • KH-02                        → KH-SIM-PUBLIC-V0.1.md §3 row KH-02

CONSTRAINTS THAT APPLY TO EVERY ITERATION:
  C-1  Translations discipline (ADR-04): every _e() call MUST appear in
       inc/translations.php. Run grep gate before declaring iteration
       closed:
         grep -o "_e(\s*'[^']*'" page-templates/<file>.php | sed ... | sort
         ↑ must match keys in inc/translations.php
  C-2  Identity discipline (ADR-01): no hard-coded LinkedIn URL, nav
       slugs, author name, or site URLs outside inc/zemla-config.php
       (zemla) or functions.php constants (mim2000).
  C-3  Visual identity invariants (Step 2 paragraph) — do NOT alter
       SVG / colour / nav structure outside the iteration's explicit
       scope.
  C-4  Theme zip build: directory depth must be `theme-name/style.css`
       at one level inside the zip (per CLAUDE.md DO NOT list).
  C-5  Tier 1 deploy = user uploads complete zip; you produce the zip in
       3-fold-path/theme-archives/<theme>-vX.Y.Z.zip and document the
       upload steps in 3-fold-path/releases/v<X.Y.Z>-<theme>/
       APPLY-<iter>.md.
  C-6  Tier 2 deploy = single-file TFE patch; you produce a hotfix
       artifact + APPLY-*.md guide; user applies via WP Admin TFE.
  C-7  Public messaging discipline (master plan §1.3): MI-M-T public
       copy never uses "Mode 3 / LLM TDD" as a lede; treat as
       "advanced research mode" footnote only.
  C-8  Token budget: ONE push at session boundary; no mid-session push.

PER-ITERATION QUICK NOTES:

  ── MIM-01 ─────────────────────────────────────────────────────────────
  Goal: Resolve OQ-200..203 with user; lock copy + translation strings
  for the 4 cards in MIM2000-ALPHA-V0.2 §3; if PHYSICS-CALIBRATION
  §6 §7 OQ-PHYS-05 says "add 2 cards now", lock those too (GR + Ising
  cards joining the existing 4).
  Deliverables:
    • SESSION-NOTES-MACBOOK.md user-sign-off paragraph
    • Updated MIM2000-ALPHA-V0.2.md §3 (you ARE allowed to edit this
      one — it's MacBook-owned working doc) with locked card text
      including any new GR / Ising cards
    • EN strings authored; CS strings authored; DE/IT/JA placeholders
      flagged for human review
  Validation:
    • User sign-off explicit
    • All 4-6 cards have TITLE / STATUS / SUMMARY / LINKS in EN+CS

  ── MIM-02 ─────────────────────────────────────────────────────────────
  Goal: Build mim2000-theme v1.10.0 zip artifact ready for Tier 1
  upload.
  Deliverables:
    • 3-fold-path/themes/mim2000-theme/page-projects-services.php
      (template per MIM2000-ALPHA-V0.2 §4.2)
    • 3-fold-path/themes/mim2000-theme/style.css with .ps-* block
      from §4.3
    • 3-fold-path/themes/mim2000-theme/inc/translations.php updated
      with all _e() keys
    • 3-fold-path/themes/mim2000-theme/functions.php — register page
      template + nav entry
    • 3-fold-path/theme-archives/mim2000-theme-v1.10.0.zip
    • 3-fold-path/releases/v1.10.0-mim2000/APPLY-MIM-02.md
      (step-by-step upload instructions for user)
  Validation:
    • Local Laragon render shows the page (or pure file inspection if
      no local PHP)
    • ADR-04 grep returns zero missing strings for the new page
    • Zip directory depth check: unzip -l archive.zip | head — confirms
      mim2000-theme/style.css at depth 1
    • CSS validates (no syntax errors)

  ── MIM-03 ─────────────────────────────────────────────────────────────
  Goal: User executes Tier 1 upload; MacBook runs smoke check post-deploy.
  Deliverables (your part):
    • Smoke check report appended to SESSION-NOTES-MACBOOK.md:
        - curl -fsS https://mim2000.cz/projects-services/ | grep -E "<h1|ps-card"
        - LinkedIn meta-card preview (manual: paste URL into
          https://www.linkedin.com/post-inspector/ and capture result)
    • MANIFEST.yaml entry suggested for the user/sync-main.sh
      (do not edit MANIFEST yourself; produce a patch suggestion)
  Validation:
    • Page returns HTTP 200
    • Visual diff vs MIM-02 local render (no regressions)
    • Translation grep on live page returns zero missing strings

  ── PHIL-01 ────────────────────────────────────────────────────────────
  Goal: Live DOM verification of zemla.org/philosophy/; resolve
  OQ-PHIL-01..05.
  Deliverables:
    • Captured DOM (curl -s https://zemla.org/philosophy/ > /tmp/phil.html;
      analyse structure)
    • Updated ZEMLA-PHILOSOPHY-PAGE-REWORK §1 with actual section
      names + IDs (you ARE allowed to edit this MacBook-owned doc)
    • User sign-off paragraph in SESSION-NOTES-MACBOOK.md
    • OQ-PHIL-01..05 closed or amended

  ── PHIL-02 ────────────────────────────────────────────────────────────
  Goal: Build zemla-theme v1.7.6 zip — hook block + template part +
  JSON data file + CSS + translations.
  Deliverables:
    • 3-fold-path/themes/zemla-theme/page-philosophy.php (modified per
      ZEMLA-PHILOSOPHY-PAGE-REWORK §4.1)
    • 3-fold-path/themes/zemla-theme/template-parts/philosophy/
      physics-result-card.php (NEW per §4.2)
    • 3-fold-path/themes/zemla-theme/assets/data/philosophy/
      physics-results.json (initial state per §4.3)
    • 3-fold-path/themes/zemla-theme/style.css — append CSS per §4.5
    • 3-fold-path/themes/zemla-theme/inc/translations.php — add 14
      keys per §4.4 (CS+EN required; DE/IT/JA placeholders)
    • 3-fold-path/theme-archives/zemla-theme-v1.7.6.zip
    • 3-fold-path/releases/v1.7.6-zemla/APPLY-PHIL-02.md
  Validation:
    • Local render shows Physics section with 3 placeholder cards
    • ADR-04 grep gate clean
    • Zip depth check
    • JSON valid: python -m json.tool < .../physics-results.json

  ── PHIL-03 ────────────────────────────────────────────────────────────
  Goal: User executes Tier 1 upload; smoke check.
  Deliverables (your part):
    • Smoke: curl https://zemla.org/philosophy/ | grep "physics-result-card"
      should match all 3 slugs (kh, gr, ising).
    • LinkedIn meta-card preview (Post Inspector).
    • MANIFEST patch suggestion.

  ── PHIL-04A / PHIL-04B / PHIL-04C ─────────────────────────────────────
  Goal (triggered by ThinkPad closing PHYS-KH-01 / PHYS-GR-02 / PHYS-IS-02):
  flip the corresponding card in the JSON data file from `pending` to
  `ready` with full payload.
  Deliverables:
    • Edit assets/data/philosophy/physics-results.json — update one card:
        status: "ready"
        anchor: "<from PHYSICS-CALIBRATION §2.4 / §3.4 / §4.4>"
        repo_url: "<if public; else null>"
        notes_url: "/philosophy/notes/<slug>-calibration/" (if author wrote)
        tests_passed: <count>
        tests_total: <count>
        last_updated: <YYYY-MM-DD>
    • Tier 2 single-file TFE patch (you do NOT need a theme bump for
      JSON updates — it's just data; produce a patch artifact for the
      user to apply via TFE OR via FTP if WP Admin allows).
  Validation:
    • Live page renders the updated card with badge text matching
      "<passed> / <total> calibration tests green"

  ── KH-02 ──────────────────────────────────────────────────────────────
  Goal: Author the LinkedIn portfolio entry copy + the zemla.org
  Physics page link spec.
  Deliverables:
    • 3-fold-path/backlog/KH-02-LINKEDIN-DRAFT.md
      (per KH-SIM-PUBLIC-V0.1.md §4 template; adjust to user's voice
       per OQ-303)
    • 3-fold-path/backlog/KH-02-ZEMLA-LINK-SPEC.md
      (per KH-SIM-PUBLIC-V0.1.md §5 — html snippet for zemla theme)
  Validation:
    • Drafts saved; user reviews before publication (KH-03 is user
      action — flip kh-sim public + post on LinkedIn)

═════════════════════════════════════════════════════════════════════════════
STEP 6 ── VALIDATION (per iteration)
═════════════════════════════════════════════════════════════════════════════
Apply the iteration-specific validation from Step 5 quick-notes. For
theme zip builds, also confirm:
  V1   ZIP depth: theme-name/style.css at level 1
  V2   ADR-04 grep: zero missing translations
  V3   ADR-01 grep: zero hard-coded URLs/slugs/names outside config files
  V4   File set complete: every file referenced in APPLY-*.md exists in zip
  V5   No console errors expected on render (manual verification)

Append validation results to SESSION-NOTES-MACBOOK.md under heading
"<iter-id> — validation".

═════════════════════════════════════════════════════════════════════════════
STEP 7 ── OPEN-QUESTIONS HANDLING
═════════════════════════════════════════════════════════════════════════════
Append OQs to 3-fold-path/backlog/OPEN-QUESTIONS-LOG.md when:

  • Strategic copy / messaging would change the reframing decision   → HIGH
  • Visual identity divergence requested (mim2000 SVG, zemla nav)    → HIGH
  • New card concept not in MIM2000-ALPHA-V0.2 §3                    → MEDIUM
  • Translation gap in a locale (EN/CS missing)                      → HIGH
  • DE/IT/JA placeholder still acceptable                             → LOW (advisory)
  • Physics-results JSON schema needs extension beyond §4.3 contract  → MEDIUM
  • Live page DOM diverges from ZEMLA-PHILOSOPHY-PAGE-REWORK §1
    assumptions in a way that breaks the hook block                  → MEDIUM
  • Anything you would want Opus to look at next                     → LOW

Use the §9 template (DEV-SONNET-INSTRUCTIONS retained format).

If severity = HIGH → STOP after closing the in-flight deliverable to a
clean rollback point.

═════════════════════════════════════════════════════════════════════════════
STEP 8 ── SESSION CLOSE
═════════════════════════════════════════════════════════════════════════════
  8.1  Append to SESSION-NOTES-MACBOOK.md under "<iter-id> — close":
         • What was built (file list)
         • Validation matrix outcome
         • OQs opened (IDs only)
         • Commit message draft
  8.2  Stage + commit:
         git add 3-fold-path/themes/ 3-fold-path/theme-archives/ \
                 3-fold-path/releases/ 3-fold-path/backlog/ \
                 3-fold-path/SESSION-NOTES-MACBOOK.md
         git commit -m "<iter-id>: <one-line summary>; cites <doc §>"
  8.3  Push macbook branch — ONE push:
         git push origin macbook
  8.4  Write next session's first row in SESSION-NOTES-MACBOOK.md under
       "Next session opens here":
         • Iteration ID for next session
         • One-line goal
         • Pre-flight notes (e.g. "wait for ThinkPad PHYS-KH-01 close
           before PHIL-04A; OQ-PHIL-01 must be answered before PHIL-02")
  8.5  Acknowledge close in chat with a 3-line summary:
         • <iter-id> closed: <green / partial / rolled back>
         • OQs opened: <count> (highest severity: <level>)
         • Next session: <iter-id>; user action required = <Tier 1
           upload / OQ answer / etc.>

═════════════════════════════════════════════════════════════════════════════
WHEN TO BOUNCE BACK TO OPUS (mandatory triggers)
═════════════════════════════════════════════════════════════════════════════
File the OQ + STOP if any of these occur:

  • OQ severity = HIGH or BLOCKING (per Step 7)
  • Public messaging boundary unclear (does this copy violate
    "do not push Mode 3 publicly"?)
  • Visual identity invariant would be broken
  • mim2000.cz Alpha cards need an entirely new card concept
  • zemla philosophy page DOM is so different from §1 assumptions that
    the hook block needs redesign
  • Track ZP and Track 2 cross-coordination (physics cards) drifts —
    e.g. mim2000 Alpha shows different result counts than zemla
    philosophy because data file out of sync
  • Translation completeness for a locale (DE/IT/JA) is requested
    before user has supplied
  • User direction received mid-session that materially changes scope

For each bounce-back, append a one-line entry to
_config/OPUS-NEXT-SESSION-TRIGGERS.md under "Pending triggers".

═════════════════════════════════════════════════════════════════════════════
POSTURE RULES (do not violate; cite when challenged)
═════════════════════════════════════════════════════════════════════════════
P-1  Read before write. Cite input doc + section for every decision.
P-2  Branch authority absolute (Step 3).
P-3  Theme work = Tier 1 (zip artifact + APPLY guide; user uploads).
     Single-file changes = Tier 2 (TFE patch artifact).
     You do NOT have FTP write access in-session.
P-4  ADR-04 (translations) and ADR-01 (identity config) are gates,
     not suggestions.
P-5  Visual identity invariants (mim2000 SVG; zemla v1.7.5 design)
     stay unchanged unless iteration scope explicitly says otherwise.
P-6  Public messaging: lead with what MI-M-T DOES, not the acronym
     expansion. Mode 3 (LLM-TDD) is footnote only.
P-7  Cross-coordination with ThinkPad: physics calibration results land
     on TWO surfaces (zemla philosophy + mim2000 Alpha) using the SAME
     data source. Keep them in sync via the JSON file (PHIL-04*).
P-8  Token budget aware: ONE push per session boundary.
P-9  When in doubt about page DOM: inspect live (curl) before editing.
     The theme files in workspace are NOT the live source of truth.
P-10 If a deliverable would take more than your wall-clock budget,
     ship a partial + flag it in SESSION-NOTES + open a continuation OQ.

═════════════════════════════════════════════════════════════════════════════
BEGIN — RUN STEP 1 NOW
═════════════════════════════════════════════════════════════════════════════

Before any other action, run Step 1.1 through 1.8 and capture all output
into 3-fold-path/SESSION-NOTES-MACBOOK.md before proceeding to Step 2.

═══════════════════════ END PROMPT ══════════════════════════════════════════
```

---

## §2. Iteration index for this Sonnet (operator quick-reference)

| Iteration | Track | Owner step in §1 prompt | Primary scope doc | Stop condition |
|-----------|-------|--------------------------|-------------------|----------------|
| MIM-01 | 2 | Step 5 quick-note "MIM-01" | MIM2000-ALPHA-V0.2.md §5 | User sign-off + OQ-200..203 closed |
| MIM-02 | 2 | Step 5 quick-note "MIM-02" | same | Theme zip ready; ADR-04 + zip depth checks pass |
| MIM-03 | 2 | Step 5 quick-note "MIM-03" | same | Page live; smoke check green; LinkedIn meta-card preview ok |
| PHIL-01 | ZP | Step 5 quick-note "PHIL-01" | ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md §7 | DOM verification + OQ-PHIL-01..05 closed |
| PHIL-02 | ZP | Step 5 quick-note "PHIL-02" | same | Theme v1.7.6 zip ready |
| PHIL-03 | ZP | Step 5 quick-note "PHIL-03" | same | Live page shows 3 placeholder cards |
| PHIL-04A | ZP (triggered) | Step 5 quick-note "PHIL-04*" | same | KH card flips to ready (post ThinkPad PHYS-KH-01) |
| PHIL-04B | ZP (triggered) | Step 5 | same | GR card ready (post PHYS-GR-02) |
| PHIL-04C | ZP (triggered) | Step 5 | same | Ising card ready (post PHYS-IS-02) |
| KH-02 | 3 | Step 5 quick-note "KH-02" | KH-SIM-PUBLIC-V0.1.md §3 row KH-02 | LinkedIn draft + zemla link spec saved |

---

## §3. Bounce-back catalog (when MacBook calls Opus back)

See `_config/OPUS-NEXT-SESSION-TRIGGERS.md` for the unified catalog. MacBook-specific most-likely triggers:

| Trigger | Iteration likely to surface it | Severity |
|---------|--------------------------------|:--------:|
| Public copy strays into Mode-3-as-lede territory | MIM-01, KH-02, PHIL-01 | HIGH |
| Visual identity invariant proposed change | MIM-02 / PHIL-02 | HIGH |
| Live page DOM diverges from ZEMLA-PHILOSOPHY §1 inferred structure in breaking way | PHIL-01 | MEDIUM |
| Translation completeness DE/IT/JA requested before user supplies | MIM-02 / PHIL-02 | LOW–MEDIUM |
| Physics card schema needs extension beyond §4.3 contract | PHIL-04A/B/C | MEDIUM |
| Cross-track sync drift (zemla card and mim2000 card show different state) | PHIL-04* | MEDIUM |
| User direction mid-session changes scope | any | depends |

---

## §4. Status footer

| Item | Value |
|------|-------|
| Document | `HANDOVER-V0.2-MACBOOK.md` (v0.2.2) |
| Output position | `_config/HANDOVER-V0.2-MACBOOK.md` |
| Tracks owned | 2 (MIM-01..03) + ZP (PHIL-01..04C) + 3 tail (KH-02) |
| Iterations specified | 10 (3 MIM + 6 PHIL + 1 KH-02) |
| Posture rules | 10 (P-1..P-10) |
| Step count | 8 |
| Bounce-back triggers documented | 7 |
| First iteration | MIM-01 (copy + OQ resolution) |
| Status | Detailed-script v0.2.2 — supersedes v0.2.1 narrative version |

---

*HANDOVER-V0.2-MACBOOK.md — v0.2.2 — 2026-05-03 — MacBook CoWork session — Opus*
