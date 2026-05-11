# MacBook orchestrator — Shad-tier first-cut (B4..B6 + Graph-tier-extra)

**Status:** Self-governing MacBook session. ThinkPad is committed to Bouračka V-model TestTargets work in parallel and will NOT be reachable for synchronous coordination during this session.
**Author of this brief:** Petr Yamyang (ThinkPad/Opus 2026-05-11 late evening)
**Target executor:** MacBook Cowork — **Sonnet preferred** (single-band-per-sub-session); **Opus fallback** if scope orchestration exceeds Sonnet context budget
**Locks-in:** lege-artis/fourier v0.2.0 PUBLIC (Fortran + C++ both green); v0.4.3-KP-review workbook adopted; B4 + B5 + B6 Sonnet briefs authored 2026-05-11
**Goal:** Ship the first complete Shad-tier package — **B4 Electronic + B5 Radar + B6 Radioastronomy** chapters with figures + scripts + citations + Graph-tier-extra material — landed on monorepo `thinkpad` branch by end of weekend, ready for ThinkPad subtree-push to public lege-artis/fourier on next ThinkPad session.

---

## §0. Read these first (in this order, do NOT skip)

1. `_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` — the master plan for B4..B7. **Pay particular attention to §3 (sequencing) and §5 (cross-band coherence rules).**
2. `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — the "why a fourth doc tier" framing + Shad-as-audience-proxy + iconography conventions.
3. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy + three doc tiers + Stage 5 gating.
4. `docs/shad/03-vibration.md` — the latest shipped Shad-tier chapter. **Mirror its structure, density, voice exactly.**
5. `examples/shad/b3-vibration/main.py` — the latest shipped Shad-tier script.
6. **The three per-band Sonnet briefs** (each is self-contained for one band):
   - `_handoffs/macbook-v0.2.x-weekend/JOB-1-SHAD-B4-ELECTRONIC.md` — B4 brief
   - `_handoffs/shad-b5-radar/SONNET-BRIEF.md` — B5 brief
   - `_handoffs/shad-b6-radioastronomy/SONNET-BRIEF.md` — B6 brief
7. `_specs/SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md` — B7 staging notes. **B7 is NOT in this session's scope.** Opus-only, sequenced after B6 lands. Read only for context — DO NOT start B7 even if scope time remains.

Optional but useful:
- `_config/KB-LESSONS-LEARNED.yaml` entries KB-037 through KB-042 — six build-chain / numerical / process / packaging traps already eaten.
- `RELEASE-NOTES-v0.2.0.md` — what shipped most recently; sets the framing tone for what release-notes you'll author at the end of this weekend cut.

---

## §1. Scope — what ships from this weekend

| Job | Deliverable | Effort estimate | Owner-pattern recommendation |
|-----|-------------|-----------------|------------------------------|
| **JOB-1** | B4 Electronic chapter — `docs/shad/04-electronic.md` + `examples/shad/b4-electronic/main.py` + 3 figures + 3+ citations | ~2-3 hours | Sonnet sub-session (or you direct-author) |
| **JOB-2** | B5 Radar chapter — `docs/shad/05-radar.md` + `examples/shad/b5-radar/main.py` + 3 figures + 3+ citations | ~3-4 hours | Sonnet sub-session |
| **JOB-3** | B6 Radioastronomy chapter — `docs/shad/06-radioastronomy.md` + `examples/shad/b6-radioastronomy/main.py` + 3 figures + 3+ citations | ~3-4 hours | Sonnet sub-session |
| **JOB-4** | **Graph-tier-extra** — see §3 below for scope interpretation + working definition | ~1-2 hours | Direct authoring (you or Opus) |
| **JOB-5** | Cumulative release-notes for the package | ~30 min | You / Opus |
| **JOB-6** | STATUS-REPORT-FILLED.md back to this folder | ~30 min | You / Opus |

**Total scope estimate:** 10-15 hours of authoring. Achievable in one long weekend session if you parallelize JOB-1 and JOB-2 (no shared scope; independent Sonnet sessions). JOB-3 has a slight dependency on JOB-2 (the "1D before 2D" pedagogical arc benefits) — sequence accordingly.

**Out of scope for this weekend** (regardless of how fast you go):
- B7 Nuclear-reactor capstone — Opus-only, separate session, requires real-data evaluation first (Halden / VR-1 / TU-Wien). See B7 staging notes §2 pre-authoring checklist.
- CS / JA / DE / IT translations of Shad chapters — separate queue.
- 2D aperture-synthesis chapter — out of Shad-tier scope (mentioned only as bridge at end of B6).
- Performance Stage 5 work — gated v0.5+.

---

## §2. Sonnet-vs-Opus fallback decision tree

You'll be making this call repeatedly during this session. Use this rule:

- **Sonnet** for each per-band Sonnet brief execution (JOB-1, JOB-2, JOB-3). The briefs are self-contained, structured, with explicit acceptance gates. This is what Sonnet does well.
- **Opus** for orchestration (deciding sequencing, integrating across bands, evaluating Sonnet outputs, authoring release-notes, writing the STATUS-REPORT). The judgement calls.
- **Opus** if you find a Sonnet session struggling with: pedagogical coherence ("does this read like a Shad chapter?"), citation-quality decisions, or the connective tissue between bands. Don't grind — escalate to Opus and move on.

The orchestrator (you) can be Opus throughout. Sonnet is for parallelizable execution lanes only.

---

## §3. Graph-tier-extra — working interpretation + scope-clarification note

Pete's brief in the session-opener (2026-05-11 evening) included "+ tier of Graph extra" as part of this weekend's scope. The phrase wasn't fully specified. My (Opus authoring this brief) working interpretation, to be **confirmed on next ThinkPad session** if it's wrong:

**Working interpretation:** the per-chapter figures already in scope (`fig-bN-input.png`, `fig-bN-spectrum.png`, `fig-bN-takeaway.png`) are NumPy-computed Matplotlib renderings — they show the *math* but not the *library running*. Graph-tier-extra fills that gap: a supplementary set of scripts under `docs/shad/graph-extras/` (or similar) that re-compute one canonical band's example data using the **actual Fortran or C++ Fourier-library backend**, side-by-side with the NumPy version, demonstrating end-to-end pipeline credibility ("we computed these results with our own reference library").

**Concrete first-cut deliverable for JOB-4:**

- `docs/shad/graph-extras/README.md` — what Graph-tier-extra is, why it exists, how to use it
- `docs/shad/graph-extras/cross-backend-verification.py` — runs one chosen band's example (recommend B3 vibration since it's the most data-realistic of the shipped chapters) through:
  1. NumPy-FFT reference (already in `examples/shad/b3-vibration/main.py`)
  2. Fortran-backend invocation (via subprocess to `backends/fortran/build/test_dft_unit` or equivalent ad-hoc test program; alternatively via a small dedicated CLI hook if you author one)
  3. C++-backend invocation (same pattern)
- `docs/shad/graph-extras/fig-cross-backend-comparison.png` — three superimposed spectra (NumPy / Fortran / C++) with worst-error annotations
- A paragraph in each shipped chapter (B4/B5/B6) pointing at Graph-tier-extras as the "if you want to see this same calculation done by the actual reference library, see graph-extras/"

**If the working interpretation is wrong:** park the question in STATUS-REPORT-FILLED.md §"Open questions for Pete" and ship JOB-1/2/3/5/6 without JOB-4. The chapters stand alone; Graph-tier-extra is an enhancement, not a blocker.

---

## §4. Real-data fetching protocol

The per-band Sonnet briefs (B4/B5/B6) each have a §5 "Implementation script" section with concrete synthesised parameters. **For the first-cut weekend, use the synthesised parameters as the primary chapter content.** Real-data integration (NEXRAD for B5, NANOGrav / PSR archive for B6, public RF captures for B4) is queued for a v0.2.x point-release iteration — NOT this weekend.

**Rationale:** chapter authoring + figure rendering + citation rigor in one weekend is already aggressive. Adding real-data fetching introduces network / format / license verification overhead that risks the whole weekend. Ship the synthesised version first; the chapters become real-data-extensible later via a one-paragraph upgrade-path note at the bottom of each script (see B3 exemplar for the pattern).

**If you DO have time for real data at the end** (after JOB-1/2/3/5/6 all green), append it to JOB-3 (B6 pulsar timing) since that has the richest open-data ecosystem (NANOGrav 15-yr release, Parkes archives, Crab pulsar samples). Time-bound to ≤2 hours; if it slips, ship without it and queue.

---

## §5. Output channels + commit cadence

**Default safe pattern** (mirrors all prior v0.2.x work):
- All commits to monorepo `petr-yamyang/VibeCodeProjects` branch `thinkpad` under the `fourier/` subtree
- **Public flip to lege-artis/fourier is NOT done from MacBook** — Pete subtree-pushes from ThinkPad on next session, after reviewing STATUS-REPORT
- Tag at green per band: `v0.2.x-shad-bN-shipped`
- Cumulative tag at end of weekend if all three bands land: `v0.2.x-shad-b4-b6-package` (or similar)

**Commit cadence — one commit per logical step, NOT one per file:**

1. `feat(shad): B4 Electronic chapter + figures + script` (JOB-1 lands together)
2. `feat(shad): B5 Radar chapter + figures + script` (JOB-2 lands together)
3. `feat(shad): B6 Radioastronomy chapter + figures + script` (JOB-3 lands together)
4. `feat(shad): Graph-tier-extras cross-backend verification` (JOB-4)
5. `docs(release-notes): v0.2.x-shad-b4-b6 package release notes` (JOB-5)
6. `chore(handoff): STATUS-REPORT-FILLED.md for macbook-shad-tier-first-cut` (JOB-6)

Commit messages follow Conventional Commits prefix style.

---

## §6. Decision authority — what MacBook decides vs. ThinkPad escalations

**MacBook can decide independently:**
- Wording, examples, figure aesthetics in every chapter
- Sequencing of JOB-1 / JOB-2 / JOB-3 (the recommended order is B4 → B5 → B6 but you can parallelize B4 + B5 if running two Sonnet sessions; B6 should wait for B5)
- Specific citation choices (so long as real, reachable, authoritative — see each per-band brief's §6)
- Whether to include the optional / depth sub-topics in each band (see each brief's §3)
- Whether to do real-data integration at the end (§4 above — only if all JOB-1/2/3 already green)
- Whether to ship the Graph-tier-extra as scoped in §3 above OR park it pending clarification

**MacBook escalates to ThinkPad (write to STATUS-REPORT-FILLED.md, do NOT publish to lege-artis/fourier until Pete reviews):**
- Any deviation from the B1+B2+B3 chapter pattern that affects pedagogical voice/density/structure
- Any third-party dependency added beyond NumPy + Matplotlib in chapter example scripts (B7 grants SciPy + pywavelets + PyEMD; B4/B5/B6 do NOT)
- Any change to the project's license stack (Apache-2.0 code + CC-BY-SA-4.0 docs + NOTICE / TRADEMARK)
- Any sanitization concern — anything you're not sure is public-safe
- Any "Graph-tier-extra" interpretation that diverges from §3 above
- Any decision that would require changes outside `fourier/` (governance lives in monorepo `_config/` + `CLAUDE.md`)

---

## §7. Sanitization rules (re-stated)

Same as every prior weekend cut. The `fourier/` subtree publishes to lege-artis/fourier PUBLIC, so anything entity-tying must be scrubbed.

**Forbidden in any file under `fourier/`:**
- `SUPIN`, `Bouračka`, `Bouracka`, `ČKP`, `CKP`, `MI-M-T`, `MIM2000`, `Improwave`, `Petr Yamyang` (use `Pete Y.` or `Pete` if unavoidable)
- Any reference to client work, internal tooling, internal hostnames
- Any path containing `\Users\vitez\` or `/sessions/sleepy-amazing-clarke/`

**Pre-flight grep before each commit:**

```bash
cd fourier/
grep -rni -E "supin|bouracka|cap[ck]p|mimt|mim2000|improwave|yamyang|vitez" \
  --include="*.md" --include="*.py" --include="*.toml" --include="*.bib" \
  docs/shad/ examples/shad/
# Expected: zero hits
```

---

## §8. Reporting back

At end of weekend (or whenever you park), write `_handoffs/macbook-shad-tier-first-cut/STATUS-REPORT-FILLED.md` covering:

- §1 Headline — done / partial / blocked per job
- §2 What landed — file paths + line counts + figure counts
- §3 Caveats + deviations from this brief — what you did differently and why
- §4 Numbers that matter — chapter line counts, figure sizes, citation counts; record any cross-language verification numbers if JOB-4 ran
- §5 Decisions deferred to Pete — including the Graph-tier-extra interpretation confirmation
- §6 Open blockers / parked work
- §7 Carried-forward items for next weekend (B7 + translations + real-data integration + 2D aperture synthesis)
- §8 Repo state at park-time — `git log --oneline -10` + tags + HEAD hash
- §9 Time accounting

That report is **the** signal back to ThinkPad. Pete reads it on next ThinkPad session + decides whether to subtree-push the package to lege-artis/fourier PUBLIC + tag v0.2.x final + publish a GitHub Release.

---

## §9. ThinkPad-side parallel context (informational only)

While you're working on Shad-tier, ThinkPad will be working in parallel on Bouračka V-model TestTargets + 1..n coverage map. **The two tracks do not share scope** — no risk of conflicting commits inside the fourier/ subtree, since ThinkPad's parallel work is under `SUPIN/bouracka-tests/`, not `fourier/`.

**Sync points:**
- Both tracks push to monorepo `thinkpad` branch
- MacBook should `git pull --rebase` before each commit (good hygiene; conflicts unlikely because of scope disjointness)
- If you DO see a conflict on `fourier/` files: STOP, write a §"Conflict" note to STATUS-REPORT, do NOT force-push or rebase complex history. Pete will resolve on next ThinkPad session.

---

## §10. Done criteria — when this weekend "succeeds"

**Minimum viable success** (the floor):
- [ ] JOB-1 (B4) chapter + figures + script + citations all land, sanitization-clean, committed
- [ ] STATUS-REPORT-FILLED.md written + committed

**Target success** (the goal):
- [ ] JOB-1 + JOB-2 + JOB-3 all land — three new Shad-tier chapters shipped
- [ ] JOB-5 release-notes authored
- [ ] STATUS-REPORT-FILLED.md complete
- [ ] All commits on origin/thinkpad ready for Pete's review + subtree-push next session

**Stretch success** (if scope permits):
- [ ] JOB-4 Graph-tier-extra also lands (per §3 working interpretation)
- [ ] One band has real-data integration appended (per §4)
- [ ] Tag `v0.2.x-shad-b4-b6-package` applied

**Out-of-scope regardless of pace** (do not attempt this weekend):
- B7 nuclear-reactor capstone (Opus next-session work, requires §2 pre-authoring checklist first)
- 2D aperture synthesis chapter
- Stage 5 performance work
- Translations

---

## §11. If something goes wrong

Same protocol as every prior Cowork session:
- If a per-band Sonnet session fails (chapter doesn't read right, figures look wrong, citations don't verify) — **escalate to Opus** within this orchestrator session. Don't grind Sonnet.
- If a build / library / fetch step burns >30 min on the same failure — **park cleanly** in STATUS-REPORT §6 with: what you tried, what the error says, your hypothesis, suggested-next-action.
- If you spot a sanitization issue at commit-time — STOP commit, scrub, re-grep, then commit. Never push potentially-leaky content to origin (it's the path to public lege-artis/fourier).

End of MASTER-BRIEF.md — start by reading §0 list, then deciding JOB-1 / JOB-2 sequencing.
