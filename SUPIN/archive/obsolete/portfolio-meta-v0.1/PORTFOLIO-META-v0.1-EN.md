# Portfolio Meta — v0.1 (EN)

> **Trigger.** 2026-05-09 — Pete Y., recognising that an expanding portfolio of interconnected projects (SUPIN/Bouračka, MI-M-T, Fourier Foundations, pavel-50 retrospective, mim2000.cz, zemla.org, bodyterapie.com, Improwave, future case studies) cannot be managed coherently if portfolio-level decisions live inside individual project repos.
>
> **Audience.** Pete (operator), every Cowork session (Opus or Sonnet, ThinkPad or MacBook) on entry, future MI-M-T methodology contributors, eventual OSS community evaluating the methodology pilots.
>
> **Status.** v0.1 — first lock. Locks: org `lege-artis`, repo layout, R-COVERAGE-ZERO methodology rule, two-book Excel convention, shibboleth aesthetic as first principle, six maps + Gate catalogue conventions, Sonnet orchestration patterns. Future revisions per documented amendment process (§14).
>
> **Provisional location.** `SUPIN\PORTFOLIO-META-v0.1-EN.md`. Proper future home is `C:\Users\vitez\Documents\VibeCodeProjects\_portfolio-meta\` once that sibling folder exists. Do not move until next workspace-folder reorganisation Gate (§6.4).

---

## §1. Why this document exists

Portfolio-level decisions propagate across projects. License choice ratified once flows into every repo's `LICENSE` file; the two-book Excel convention adopted once becomes the schema every TestPlan must respect; the shibboleth aesthetic as a first principle informs every name from org down to component. Without a stable place to record these decisions, each session re-derives them from the project session-close docs, which is wasteful, lossy, and produces drift. This document is that stable place.

The companion files referenced throughout (`_maps/*.md`, `_gates/*.md`, `_tasks.md`) are the operational surfaces where individual decisions accumulate. This document is the *index and constitution* — the layer above them that establishes the conventions and locks the architectural ground.

It is intended to be **the first file every Cowork session reads on entry**, before opening any project-specific session-close doc. Roughly 600 lines. Reading it cold should take fifteen minutes and orient a fresh session sufficiently to know what is locked, what is open, and where to find current state per project.

---

## §2. The three layers — portfolio architecture

Every project in the portfolio belongs to exactly one of three layers. The layers have different stability profiles, different review cadences, and different relationships to external audiences.

| Layer | Role | Stability | Citable? | Examples (current) | Examples (projected) |
|---|---|---|---|---|---|
| **Math/logical commons** (`lege-artis` org on GitHub) | Source of truth for canonical algorithms, algebraic primitives, mathematical logic, lege-artis-grade prose. | High — version once shipped, semver discipline. | Yes — by DOI / release tag / permalink. | (none yet — first content lands with Fourier weekend cut) | `lege-artis/math-commons` (umbrella + index + first modules), `lege-artis/fourier`, `lege-artis/coverage-algebra` |
| **Case studies** (project-named repos) | Apply the commons + add domain-specific patterns. Live, project-paced, opinionated. | Medium — releases per project iteration. | Within the repo, by tag. | `petr-yamyang/bouracka-tests` | future MI-M-T pilots, pavel-50 if formalised |
| **Publication tier** (websites under personal/brand domains) | Render selected content for distinct audiences across distinct sites. | Low — content churn, but URL stability is contractual. | URLs are themselves citable surfaces. | `mim2000.cz` (commercial product surface + tech blog), `zemla.org` (deeper science), `bodyterapie.com` (integrative reflections — body, attention, embodied cognition) | (no new sites planned this iteration) |

The dataflow is downward in steady state — commons → case studies → publication — with feedback loops *only* for new patterns being recognised in case studies and lifted up into the commons. Publication tier renders from commons + case study content; it never originates content.

This three-layer division is what makes the portfolio coherent rather than a federation of unrelated projects. Each new project on entry asks itself: *which layer am I?* and follows the conventions of that layer.

---

## §3. Org and repo layout — locked

### §3.1 GitHub org `lege-artis`

The math/logical commons layer lives under a dedicated GitHub organisation named `lege-artis`. Rationale: shibboleth naming (see §9) — Latin phrase "according to the law of the art" carries the depth signal for those who recognise it, while not blocking those who don't. The org must be created manually by Pete on github.com (Pete's account `petr-yamyang` becomes the org owner). Creating the org is a Gate (§6.1).

Repos under the org, in projected order of creation:

| Repo | Purpose | Created when |
|---|---|---|
| `lege-artis/math-commons` | Umbrella + index + first content as modules. Hosts shared mathematical primitives that don't yet justify their own repo. | First, immediately after org creation. |
| `lege-artis/fourier` | Canonical FFT/DFT/Partial-Sum reference implementation. Replaces the earlier working name `fourier-foundations`. | C-1 checkpoint of Fourier weekend cut (§5 of `FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md`). |
| `lege-artis/coverage-algebra` | Extracted module: relation algebra over finite sets for Round Zero coverage audits. | When the first non-Fourier consumer appears — likely Bouračka v0.5.2 back-port. Until then the algebra lives as a module inside `math-commons`. |

The case-study layer continues with the existing repo:

| Repo | Owner | Purpose |
|---|---|---|
| `petr-yamyang/bouracka-tests` | Personal | First MI-M-T case study; F/E + UI testing of Czech Insurance Bureau accident-record web app. Public, MIT-equivalent license stack per `_specs/PUBLIC-VISIBILITY-AUDIT-v0.1-CS.md`. |

The publication tier is not GitHub-hosted in the same sense; the websites are deployed via their respective hosting (mim2000.cz currently has its own deployment story that needs a separate redesign sub-project, see §13 OQ-PORT-3).

### §3.2 What does NOT go into `lege-artis`

The org is *for the math/logical commons only*. It does not host:

- MI-M-T methodology core itself (lives separately, eventual sibling org or under Pete's personal account — TBD per OQ-PORT-1).
- Bouračka-tests (case study, lives at `petr-yamyang/bouracka-tests`).
- Personal projects of any kind.
- Pavel-50 or other one-shot retrospectives.

This separation matters because `lege-artis` will be cited by external academic and engineering work; its contents should be defensibly canonical. Mixing it with everything else dilutes the signal.

### §3.3 Naming convention recap

| Layer | Prefix / convention |
|---|---|
| Math commons | `lege-artis/<topic>` — short topical names, no `-foundations` suffix |
| Case studies | `<owner>/<project>-<purpose>` — e.g. `petr-yamyang/bouracka-tests` |
| MI-M-T core (future) | TBD per OQ-PORT-1 |

---

## §4. License decision stack — referenced

Already locked in `FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` §11. Summary table for portfolio reference:

| Layer | Code license | Doc license | Name protection |
|---|---|---|---|
| `lege-artis/*` | Apache 2.0 | CC-BY-SA-4.0 | `TRADEMARK.md` + `NOTICE` declaring MIM2000™ / Improwave™ / Petr Yamyang non-licensed; reinforces Apache §6 anti-endorsement |
| MI-M-T base / free tier | Apache 2.0 | CC-BY-SA-4.0 | Same `TRADEMARK.md` + `NOTICE` overlay |
| MI-M-T paid tier | Proprietary EULA in separate repo | Proprietary EULA | Apache §6 + registered trademark (CZ + EU, separate sub-task per OQ-PORT-2) |
| Bouračka-tests | MIT (existing) | MIT | None at present (case study, no name protection beyond MI-M-T parent project's eventual trademark) |
| Publication tier | Per-site (mim2000.cz CC-BY-NC, zemla.org CC-BY-SA, bodyterapie.com TBD) | Same | Site-specific |

Voluntary funding (`.github/FUNDING.yml` with GitHub Sponsors + Patreon + PayPal.me) is independent of license and applies to all `lege-artis/*` repos.

---

## §5. The maps — convention + initial inventory

The portfolio maintains a small set of cross-cutting maps that capture relationships across projects. Each map lives in `_maps/<map-name>.md` (provisional location: `SUPIN/_maps/`; final home `_portfolio-meta/_maps/`). Maps are *living documents* — updated as the portfolio evolves — with their own update cadences.

### §5.1 The six maps

| # | Map | Captures | Update cadence | Format |
|---|---|---|---|---|
| 1 | **Mind/Idea Map** (merged) | Topical space of each project (mind) + ideas in flight, where they came from, where they want to go (idea). Two views or two layers in one document. | Per-major-shift in topical scope or per-new-idea-introduced. | Markdown with embedded Mermaid mindmap diagrams; one section per project. |
| 2 | **Architecture Map** | Structural / component view across projects: repos, services, devices, interface layers, dataflow between three portfolio layers. | Per-architectural-decision (Gate closure) or per-major-refactor. | Markdown + ArchiMate-style ASCII diagrams + PlantUML where worth the rendering cost. |
| 3 | **Map of Methods** | Methodology patterns: R-rules (R-CONFIRM-1, R-PACKAGE-1, R-DECOUPLED-1, R-DESIGN-1, R-COVERAGE-ZERO, …), MI-M-T governance patterns, named conventions adopted. | Per-new-pattern-recognised; quarterly review for retirement of obsolete patterns. | Markdown table (id, name, definition, where-it-applies, when-introduced, status). |
| 4 | **Hack and Tech Map** | Techniques, snippets, workarounds catalogue — cross-project reusable. Cypress same-origin WebSocket workaround, Selenium React-controlled-input dispatchEvent recipe, IOC-sanitisation-on-pack pattern, the `bouracka.py` pure-Python orchestrator pattern, the `cy.intercept` stub list, the `--disable-features=WebSocket` Chromium diagnostic flag, etc. | Per-new-technique-discovered (cheap to add, never delete). | Markdown table grouped by technology / context, each entry: name, problem-it-solves, code-snippet-or-pointer, originating-session, projects-using-it. |
| 5 | **Provenance Map** | Which idea came from which session, which artefact triggered which decision. Essential raw material for retrospective essays (including the eventual "Fourier's story") and for traceability when a decision is questioned later. | Per-decision (small entry); never deleted. | Append-only chronological log; one entry per significant decision with timestamp, session-context, contributors, decision, supersedes-or-revises pointer. |
| 6 | **Cadence/State Map** | What's actively in-flight, what's parked-waiting-on-X, what's blocked-on-Y, what has natural recurring cadence (daily test runs, weekly status, per-release coverage refresh). Also hosts the central CLAUDE task-list index (§12). | Per-session entry (read state), per-session exit (write state delta). | Markdown table per project with status column + dependencies column + next-trigger column. |

### §5.2 Initial population

For v0.1 of the meta document, the maps themselves remain unpopulated stubs. Population happens in subsequent sessions as each map proves its first content:

- Mind/Idea Map: first populated when Fourier weekend cut Stage 1 begins (introduces a new top-level project with topical scope + several open ideas).
- Architecture Map: first populated when `lege-artis/math-commons` repo is created (introduces multi-repo architecture spanning portfolio).
- Map of Methods: should be populated **immediately** after this document is reviewed — every R-rule already exists; the map just gives them a single home. Suggested first task post-meta.
- Hack and Tech Map: should be populated **immediately** by harvesting from existing `_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` and the various install gotcha catalogues. Cheap, valuable, won't change the architectural ground.
- Provenance Map: starts now — first entry is the locking of this v0.1 document. Subsequent entries accumulate as decisions land.
- Cadence/State Map: starts now — first content is the table of currently in-flight + parked work across all projects (data already exists across various session-close docs; just needs consolidating).

### §5.3 Map update protocol

Every Cowork session that ends with a significant outcome (a decision, a milestone, a new technique discovered, a new pattern named) is responsible for updating at least one map. The session-close artefact lists which maps were touched. Opus sessions update Provenance + Cadence/State as a matter of course; Sonnet sessions touch only the specific maps relevant to their bounded scope (typically Hack and Tech for technique additions, occasionally Map of Methods for new R-rule introductions).

---

## §6. Gate-with-Window catalogue convention

Every project has a decision lattice where some decisions are cheap to reverse, some are medium-cost, and some are effectively one-way doors. The methodology contribution: enumerate the Gates explicitly per project, document the window for each, and treat hitting a Gate without a positive decision as a process bug (analogous to a compile-time error rather than a runtime surprise).

### §6.1 Gate catalogue file format

Each project carries a `_gates.md` at its root listing its Gates. Schema per Gate entry:

```
## GATE-<id>: <short name>
- **What closes:** <description of what becomes irreversible after this Gate>
- **Trigger:** <event that closes the Gate>
- **Window status:** open | closing-soon | closed
- **Required decision:** <what must be decided before close>
- **Default if no decision:** <fallback that takes effect if window expires>
- **Cost of reversal:** <estimate of effort to undo if closed Gate must be revisited>
- **Dependencies:** <other Gates this depends on or that depend on it>
```

### §6.2 Portfolio-level Gates currently open

| GATE-id | Short name | Window status | Required decision | Default | Owner |
|---|---|---|---|---|---|
| GATE-PORT-1 | `lege-artis` GitHub org creation | open | Pete creates org manually on github.com | Stays open until done; blocks all `lege-artis/*` repo work | Pete |
| GATE-PORT-2 | First trademark registration (CZ + EU) | open, low urgency | Pete files MIM2000™ + Improwave™ marks; couples with mim2000.cz redesign for evidence-of-use | Continue with declarative `TRADEMARK.md` only; legal teeth deferred | Pete |
| GATE-PORT-3 | mim2000.cz redesign sub-project initiation | open, blocks Fourier publication chain | Author `MIM2000-REDESIGN-SEED-v0.1.md` and start cleanup | Fourier publication chain stalls at "code shipped, no public landing page links to it" | Pete |
| GATE-PORT-4 | Workspace folder reorganisation (move portfolio meta + maps + gates to `_portfolio-meta/` sibling of SUPIN) | open, low urgency | Pete creates `C:\Users\vitez\Documents\VibeCodeProjects\_portfolio-meta\`, moves files | Provisional location at `SUPIN/` works fine; reorganisation is cosmetic | Pete |
| GATE-FOUR-1 | Fourier license stack (Apache 2.0 + CC-BY-SA-4.0 + TRADEMARK.md) | **closed** 2026-05-09 | (locked in `FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` §11) | n/a — closed | Pete |
| GATE-FOUR-2 | First community PR accepted into `lege-artis/fourier` | not-yet-open (no community presence) | Whether to require Contributor License Agreement | Defer decision; first PR triggers Gate | Pete |
| GATE-FOUR-3 | First external mim2000.cz link to `lege-artis/fourier` | not-yet-open (depends on GATE-PORT-3) | Whether the linked repo URL is permanent (commitment) | Once linked, repo rename becomes high-cost | Pete |
| GATE-BOUR-1 | Two-book Excel split for Bouračka (TestPlan + TES) | closing soon (planned v0.5.2 after Fourier proves pattern) | Migration tool ready, diff reviewed | Stays single-workbook indefinitely (acceptable for current scale) | Pete + Opus |
| GATE-BOUR-2 | First Sonnet-on-MacBook session for Bouračka governance review | open | Whether MacBook gets independent Sonnet branch (`macbook-sonnet/...`) | Continue with manual MacBook-Pete workflow | Pete |

### §6.3 Per-project Gate catalogues (referenced)

Each project's own `_gates.md` lists project-specific Gates that don't propagate to portfolio level. Example Bouračka Gates: TestCafe formal removal timing, ReadyAPI/SoapUI sandbox token request to ČKP, etc. These remain in project repos.

### §6.4 Gate review cadence

Portfolio-level Gates reviewed at the start of every Opus session. Project-level Gates reviewed at the start of every session relevant to that project. A Gate marked "closing soon" must be addressed within the current session or explicitly deferred with a written reason.

---

## §7. R-COVERAGE-ZERO — methodology rule

**Rule.** Every TestPlan revision must pass a Round Zero coverage audit before being declared release-candidate.

### §7.1 Definition

Round Zero is the algebra-applied-to-documentation gate that runs *before* any executable test fires. It operates on the documentation triple (Requirements, TestTargets, TestCases) and detects:

| Failure mode | Algebraic characterisation | Operational meaning | Default remediation |
|---|---|---|---|
| Orphan TC | TC ∈ TestCases, no TT in TestTargets references it | Test exists with no documented TT — possible drift, possible value-add awaiting documentation | Author to resolve: either add TT or archive TC |
| Orphan Req | Req ∈ Requirements, no TT in TestTargets covers it | Requirement stated but no test plan covers it — coverage gap | Test designer to add TT chain |
| Orphan TT | TT ∈ TestTargets, no TC in TestCases implements it | Target identified but no TC implements it — incomplete test design | Test designer to add TC or retire TT |
| Dead-end chain | Req → TT → no TC, or Req → no TT at all | Requirement has incomplete coverage chain | Same as above, traced upstream |
| Redundancy | Multiple TCs covering same (Req, TT) pair without diversification rationale | Effort duplication, possible quality issue if rationale missing | Author to mark "diversification: Y / N + rationale" |
| Ambiguous TC | TC references TT that doesn't exist or has been renamed | Documentation rot | Auto-detect via name lookup, flag for repair |

### §7.2 Implementation

`tools/coverage_audit.py` reads canonical TestPlan sheets (Requirements, TestTargets, TestCases) and writes derived sheets (CoverageMatrix, CoverageGapsRoundZero) into the TestExecutionSummary workbook. Plain-value sheets — no Excel formulas, no Python eval. The algebra lives in code; the workbook holds materialised results.

The Python implementation lives in `lege-artis/coverage-algebra` once extracted (currently planned as a module of `lege-artis/math-commons`). Each consumer (Bouračka, Fourier, future case study) imports the module via standard package mechanics — no copy-paste.

### §7.3 Two-tier documentation

Per the shibboleth aesthetic (§9):

- **Canonical tier** (`docs/canonical/coverage-algebra-formal.md` in `lege-artis/coverage-algebra`): relation algebra over finite sets, composition, projection, complement, transitive closure, symmetric-difference characterisation of orphans, theorems with proofs, citations to standard sources (Tarski / relation calculus textbooks).
- **Engineer tier** (`docs/engineer/coverage-algebra-howto.md`): "open your TestPlan, look at this column, here's what the tool flags and what each finding means in plain language." Worked examples with screenshots. No formal notation.

Both tiers cite the same source-of-truth implementation. A consistency-lint script (deferred to v0.2 of the algebra) verifies they don't contradict each other.

### §7.4 Where R-COVERAGE-ZERO is proved first

Fourier is the testbed (per Pete's 2026-05-09 decision). Reasons:

- Fourier requirements are mathematical statements with bivalent truth values
- Fourier TestTargets decompose along clean orthogonal axes (algorithm × precision × language × property)
- Fourier TestCases are golden-vector comparisons or property assertions
- Round Zero output in Fourier domain will be *clean* — easy to validate the algebra
- In Bouračka's messier domain, every orphan would prompt "is this a genuine algebra finding or a documentation-extraction failure?" — debug nightmare for the first version

After Fourier proves the pattern (probably v0.1.0 weekend cut + v0.2.0 follow-up), Bouračka v0.5.2 back-ports it.

---

## §8. Two-book Excel convention

Adopted 2026-05-09 (Pete's decision). Replaces the single-workbook approach used by current Bouračka.

### §8.1 The split

| Book | Role | Churn | Audience |
|---|---|---|---|
| `<project>-testplan.xlsx` | Design-time artefact: Requirements, TestTargets, TestCases, Codelists, GoldenVectorPointers (or equivalent reference data). | Low — one commit per design revision, rare. | Test designer, mathematician/engineer authoring requirements. |
| `<project>-tes.xlsx` (TestExecutionSummary) | Run-time artefact: TestRuns, Results, AssertionGates, **CoverageMatrix (generated)**, **CoverageGapsRoundZero (generated)**, PrecisionRegression (generated, where applicable), CrossLanguageEquivalence (generated, where applicable). | High — one commit per test run, regenerated frequently. | QA reviewer, release manager, audit. |

### §8.2 Why the split

TestPlan and TES have different update cadences (low vs high), different reviewers in mature workflows (designer vs QA), and different stability requirements (TestPlan is a stable contract; TES is a running log). Co-locating them in one workbook conflates these concerns and has caused real bugs in Bouračka history (the priority-matrix Excel formula bug, where derived computation was attempted in formulas and went undetected because the workbook is too big to hand-audit).

The split also enables the generated coverage sheets (CoverageMatrix, CoverageGapsRoundZero) to live cleanly in TES — they are functions of the TestPlan + run results, regenerated on demand, never hand-edited.

### §8.3 Where coverage lives

Coverage report sheets are part of TES, not a third workbook. Reasons: they are derived from TestPlan + run state, cadence matches TES (regenerate per run), audit reads TES end-to-end already, splitting into a third workbook adds VLOOKUP-across-files fragility without proportional benefit.

A third workbook split *can* be triggered later if MI-M-T enters commercial pilot and the customer's QA process requires separate documents (see GATE-MIMT-1 once MI-M-T core is staged).

### §8.4 Bouračka back-port

Current Bouračka `BOURACKA-TESTPLAN-v0.4.2.xlsx` will be split into `BOURACKA-TESTPLAN-v0.5.2.xlsx` (sheets 00-05) + `BOURACKA-TES-v0.5.2.xlsx` (sheets 06-17 plus new generated coverage sheets). Migration script writes itself once Fourier proves the pattern. Planned v0.5.2 task; not blocked, just deferred behind Fourier validation.

### §8.5 No-Excel-formulas-for-derived-computation rule

Strong consequence of two-book + generated sheets: **derived computation lives in Python, results materialise as plain-value Excel cells**. No `IF(CODE(K)+CODE(L)…)` priority-matrix patterns, no VLOOKUP across sheets for inferred relationships. If a value can be computed from other values, it gets computed by `tools/<thing>.py` and written as a plain cell. Excel's role is *display + hand-edited input*, not *runtime derivation*.

This rule has its own R-id: **R-EXCEL-PLAIN-1**. Add to Map of Methods first pass.

---

## §9. Shibboleth aesthetic — first principle

**Principle.** Surface stays simple and accessible for the paying / drive-by user; core stays rigorously classical for the curious / contributing user. The depth is *signaled* (not hidden, not flaunted) by exactly the kind of cultural-anchor naming that says "there is insight behind this."

### §9.1 The three-tier visibility layer

| Layer | Visible to | Style | Example |
|---|---|---|---|
| **Surface** | Every paying user, every drive-by community visitor, mim2000.cz reader | Plain, accessible, everyday words. Never requires Latin / formal notation to use the product. | "Run your tests. See what passed and failed. Find what's missing." |
| **Core** | Curious user who wants to understand, academic reviewer, contributor | Rigorous. Cites primary sources. Uses domain notation correctly. Doesn't apologise for depth. | Relation-algebra formalism in `docs/canonical/coverage-algebra-formal.md` with theorem-proof structure |
| **Naming layer** | Both tiers | Shibboleth. `lege-artis`, `Improwave`, `MIM2000`. Readable enough not to obstruct, encodes a pointer for those who recognise it. | `lege-artis` org name |

### §9.2 Operational consequences

- Every commons component ships **both doc tiers** (canonical + engineer). Authored independently. Cross-checked for non-contradiction by a consistency lint pass (deferred to v0.2 of each component).
- Every product surface (mim2000.cz pages, README files, error messages) optimises for the surface tier. If the curious user wants to dig deeper, the link to canonical-tier is prominent but not required.
- Names carry information. `lege-artis` is the org name, not "high-quality-math-commons." The Latin term filters self-selecting power users to the canonical-tier docs naturally — they will read further.
- The principle generalises: same energy as Stripe naming a primitive `Idempotency-Key` (banking nerds nod, everyone else uses it correctly without needing to know why), or Knuth calling a constant `e`. Naming carries information for those who can decode it, without obstructing those who can't.

### §9.3 What this principle does NOT mean

- Not "make everything obscure." Surface tier is *more* accessible than typical academic output, not less.
- Not "intentionally unclear." Names that are merely opaque (no cultural anchor) violate the principle — they obstruct without rewarding.
- Not "Latin-only." Czech names with similar shibboleth quality are equally valid (`Bouračka` itself qualifies — Czech-specific traffic-collision colloquialism that signals locality of the SUT to those who recognise it).

### §9.4 Adoption check

When introducing a new component, ask: *does the surface tier require classical knowledge to use?* If yes, simplify the surface. *Does the core tier apologise for depth or hide rigorous treatment behind handwaving?* If yes, add the canonical-tier doc. *Does the name carry information for those who can decode it without obstructing those who can't?* If neither, rename.

---

## §10. Device placement matrix

Three devices in current rotation. Each project lives on a defined subset.

| Project | ThinkPad (Pete personal, Cowork-Opus primary) | MacBook (Pete personal, Cowork analytical) | HP Elite SUPNB001 (SUPIN-owned, intranet, no Cowork) | Notes |
|---|---|---|---|---|
| SUPIN/Bouračka analytical work | ✓ (primary authoring) | ✓ (analytical review, MacBook-Sonnet branches) | — | HP Elite is for runtime, not authoring |
| SUPIN/Bouračka test runtime | ✓ (validation runs only) | ✓ (validation runs only) | ✓ (official runner — daily test execution against DEMO + production-test) | HP Elite results are the official Cíl-1+ baseline |
| `lege-artis/math-commons` | ✓ | ✓ | ✗ (SUPIN-owned, personal projects forbidden) | Personal portfolio — cannot live on SUPIN-owned hardware |
| `lege-artis/fourier` | ✓ | ✓ | ✗ | Same as above |
| `lege-artis/coverage-algebra` (when extracted) | ✓ | ✓ | ✗ | Same |
| MI-M-T core (when staged) | ✓ | ✓ | ✗ | Same — though SUPIN may eventually license MI-M-T as a customer; that's a different deployment story |
| pavel-50 (parked) | ✓ (archive) | ✓ (archive) | ✗ | Retrospective only |
| mim2000.cz admin | ✓ | ✓ | ✗ | Public website, no SUPIN dependency |
| zemla.org admin | ✓ | ✓ | ✗ | Same |
| bodyterapie.com admin | ✓ | ✓ | ✗ | Same |
| Improwave (TBD scope) | ✓ | ✓ | ✗ | Personal brand work |

### §10.1 Device-specific rules

**ThinkPad (this device, Pete personal):**
- Cowork session here is the *master* (Opus governance + cross-project coordination).
- Sonnet branch sessions can run here for ThinkPad-side execution work (e.g. cross-framework parity, just completed).
- Workspace root: `C:\Users\vitez\Documents\VibeCodeProjects\`. Each project as a sibling folder.

**MacBook (Pete personal):**
- Cowork session here runs analytical / methodology-export work in parallel.
- Sonnet branch sessions can run here for MacBook-side execution (e.g. methodology refinement, governance reviews — see GATE-BOUR-2).
- Workspace root: `~/Documents/VibeCodeProjects/`. Mirrors ThinkPad layout.

**HP Elite SUPNB001 (SUPIN-owned):**
- *No Cowork sessions ever* — security policy.
- *No personal projects ever* — device ownership policy.
- Receives email-shipped automation packages (per `_specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md`), runs them, returns results JSON.
- Treated as a *runtime target*, not a development device. Pete operates it but does not develop on it.

### §10.2 Cross-device sync

- GitHub remains the canonical source of truth across personal devices. ThinkPad and MacBook clone from same repos.
- HP Elite receives email packages — never pulls from GitHub directly (network egress restrictions + SUPIN security policy).
- For SUPIN-internal sync (MacBook ↔ ThinkPad), GitHub repos are the bridge; same `git pull` / `git push` workflow.

---

## §11. Sonnet orchestration patterns

This section is operational meat for the next phase. Pete's directive 2026-05-09: *"2 independent Sonnet sessions run independently on ThinkPad and MacBook orchestrated by this Opus session as a master. As realised, Sonnet must be tightly managed and Opus must manage it carefully."*

Lessons learned from earlier Sonnet handoff (cross-framework parity work just completed on ThinkPad-Sonnet) inform every pattern below.

### §11.1 When to spawn a Sonnet session

Spawn Sonnet for work that is:

1. **Bounded** — clear scope boundary, finite file set to touch.
2. **Well-specified** — pre-existing master spec doc that Sonnet reads first.
3. **Mostly-execution** — not novel architectural decisions.
4. **Branch-isolated** — never touches `main`.
5. **Hand-back-able** — produces a SYNCHRO doc + branch + optional PR for Opus to review.

Do NOT spawn Sonnet for:

- Architectural decisions (those need Opus + Pete in dialogue).
- Cross-project coordination (only Opus master has that scope).
- Methodology rule introductions (those need ratification).
- Anything where the right answer requires reading 5+ session-close docs to figure out.

### §11.2 Branch isolation per session

Every Sonnet session works on a dedicated git branch. Naming convention:

```
<device>-sonnet/<short-task-slug>-<YYYY-MM-DD>
```

Examples:
- `thinkpad-sonnet/cross-framework-parity-2026-05-08`
- `macbook-sonnet/methodology-export-2026-05-09`
- `thinkpad-sonnet/fourier-stage-1-bibliography-2026-05-10`

Two sessions on different devices working on the same project use separate branches with no overlap on file paths. Opus master reconciles by reviewing both SYNCHRO docs and merging in the order that minimises conflict.

### §11.3 Cold-start prompt requirements

Every Sonnet session opens with a paste-block prompt authored by Opus. The prompt must contain:

| Section | Content |
|---|---|
| **Context** | Pre-read list — exact file paths in repo, in reading order. Sonnet reads these BEFORE acting. |
| **Master spec pointer** | The single document that defines acceptance criteria for the work. |
| **What I'm asking you to do** | The work scope, in imperative bullets, with day-by-day plan if multi-session. |
| **Constraints (DO NOT)** | Hard out-of-scope list. "DO NOT modify X" / "DO NOT touch Y". Prevents drift. |
| **Per-framework / per-tool cheat sheets** | Inline code patterns Sonnet would otherwise google. Reduces error rate. |
| **Acceptance per deliverable** | Concrete checks the work must satisfy. Sonnet self-verifies before hand-back. |
| **Hand-back protocol** | What artefact to produce (SYNCHRO doc), where to commit, what PR to open. |
| **If you hit a hard blocker** | Author `BLOCKER-{slug}.md`, describe what blocked, what was tried, recommended Opus action. Continue with whatever IS unblocked. |
| **Out of scope** | Explicit list of things NOT to do (matches §11.5 anti-patterns). |

Reference template: `_specs/SONNET-HANDOFF-PROMPT-CROSS-FRAMEWORK-PARITY-v0.1.md` already authored for the cross-framework parity work. Future handoffs follow the same shape. Per-handoff customisation in the §1 paste block.

### §11.4 Bounded scope + acceptance criteria

Scope boundary expressed as a tight file-set or task-list. Acceptance criteria as concrete checks. Example from completed parity handoff:

- Acceptance per TC port (must satisfy all 5):
  1. Same TC code in test title
  2. Same `covers(...)` annotation pointing to same TT codes
  3. Same fixture data via `loadFixture()`
  4. Same expected outcome as Playwright counterpart
  5. Drift guard if applicable

If Sonnet cannot self-verify these checks, the prompt was under-specified — that's Opus's bug, fix in next handoff.

### §11.5 Sync-back protocol (SYNCHRO docs)

Hand-back artefact is `SYNCHRO-OPUS-FROM-<device>-SONNET-<task>-{YYYY-MM-DD}.md` at repo root. Required sections:

| § | Content |
|---|---|
| §1 | What was done — matrix of completed work items with PASS/SKIP/FAIL |
| §2 | Easy / hard / failed per work item — 2-3 lines each |
| §3 | Cross-axis findings (e.g. framework-divergence findings, methodology gaps surfaced) |
| §4 | Recommended downstream document updates (e.g. PLATFORM-ASSESSMENT v0.x score updates) |
| §5 | Open issues blocking next-version ship |
| §6 | Verified output samples / consolidate report |

Plus updated `CHANGELOG.md` with entries under appropriate version section. Plus committed branch + opened PR (if branch model dictates) or branch ready-for-merge (if Opus reviews then merges).

### §11.6 Tight-management checklist for Opus

Before spawning Sonnet:

- [ ] Master spec doc exists and is committed
- [ ] Pre-read list is verified to point at real files
- [ ] Acceptance criteria are concrete and self-verifiable
- [ ] Out-of-scope list explicitly names things Sonnet might drift into
- [ ] Hand-back artefact format is templated
- [ ] Estimated session-budget is set (4 days, 2 days, etc.) — over-budget = signal to re-scope
- [ ] Branch isolation: target branch name agreed in advance
- [ ] No overlap with other in-flight Sonnet session on same files

After Sonnet hand-back:

- [ ] SYNCHRO doc reviewed end-to-end
- [ ] Branch diff reviewed for unexpected file changes
- [ ] Acceptance criteria verified independently (don't trust self-report alone)
- [ ] Map updates harvested (Map of Methods, Hack and Tech, Provenance)
- [ ] Findings propagated to relevant project session-close docs
- [ ] Branch merged or PR opened with explicit review comments
- [ ] Cadence/State Map updated to reflect new state

### §11.7 Two-parallel-Sonnet-sessions specifics

When ThinkPad-Sonnet and MacBook-Sonnet run in parallel:

- **Different scopes** — never give them overlapping file paths. Even if both work on Bouračka, partition by directory (e.g. ThinkPad-Sonnet on `cypress/`, MacBook-Sonnet on `_specs/`).
- **Different branches** — `thinkpad-sonnet/...` vs `macbook-sonnet/...`. They are visible to each other on origin but should not depend on each other in-flight.
- **Sequential merge to main** — Opus master reviews both SYNCHRO docs after both complete, merges in chosen order, resolves any conflicts as Opus.
- **No cross-Sonnet communication** — they don't read each other's branches in-flight. If MacBook-Sonnet needs ThinkPad-Sonnet's output, that's a sign the work was wrongly split — re-scope as sequential rather than parallel.
- **Synchronisation point** — Opus session marks the parallel-work-complete moment in the Cadence/State Map and Provenance Map.

### §11.8 Sonnet anti-patterns to prevent

Documented from the earlier Sonnet handoff retrospective:

- Sonnet drifting into adjacent file changes "while it was already there" → fix: explicit out-of-scope list per §11.3
- Sonnet inventing new conventions instead of following existing ones → fix: per-framework cheat sheets per §11.3
- Sonnet failing silently and reporting success → fix: independent verification per §11.6
- Sonnet hand-back missing required sections → fix: SYNCHRO doc template enforcement
- Sonnet trying to bridge to another in-flight session's work → fix: §11.7 isolation rule

---

## §12. Central task index

The Cadence/State Map (§5.1 #6) hosts the central task list. File: `_maps/cadence-state.md` (provisional path `SUPIN/_maps/cadence-state.md` until reorganisation).

### §12.1 Schema

Per project, a section with three tables:

```
## <project-name>

### In-flight
| Task | Owner | Started | Branch | Estimated complete |

### Parked / waiting
| Task | Reason parked | Unblock trigger | Re-evaluate by |

### Recurring cadence
| Activity | Cadence | Last run | Next run |
```

### §12.2 Read protocol for new sessions

Every Cowork session (Opus or Sonnet, ThinkPad or MacBook) reads `_maps/cadence-state.md` before starting work. Updates happen at session end: state changes (in-flight → done, parked → unblocked, recurring → next-run-pinned) are written back.

### §12.3 First-population content

Initial population reflects current 2026-05-09 state across portfolio. Will be authored next pass alongside this meta document's first ratification.

---

## §13. Open questions (Pete to answer before Fourier Stage 1)

Six questions remain open. None block this v0.1 ratification, but all should be answered before Fourier weekend Stage 1 starts.

| OQ-PORT- | Question | Default if no answer | Affects |
|---|---|---|---|
| OQ-PORT-1 | Where does MI-M-T core live? Sibling org (`mimt-core`?) under Pete, or separate org, or `lege-artis/mimt`? | `lege-artis/mimt` (within the commons org) — this might be wrong if MI-M-T grows commercial offerings | §3 repo layout |
| OQ-PORT-2 | Trademark registration timing — file CZ + EU marks now, or after mim2000.cz redesign provides evidence-of-use? | Defer to mim2000.cz redesign (cheaper, stronger filing later) | GATE-PORT-2 |
| OQ-PORT-3 | mim2000.cz redesign — start sub-project seed doc this weekend or defer? | Defer until Fourier v0.1.0 ships (Fourier publication chain is the trigger) | GATE-PORT-3 |
| OQ-PORT-4 | Workspace folder reorganisation — move `_portfolio-meta/`, `_maps/`, `_gates/` to sibling of `SUPIN/` now or later? | Later (cosmetic, current location works) | GATE-PORT-4 |
| OQ-PORT-5 | First-population content for the six maps — author all in one pass after this meta ratifies, or one at a time as triggered? | One at a time (avoid stale population) | §5.2 |
| OQ-PORT-6 | Two-parallel-Sonnet split for the upcoming work — what's the first work item that justifies parallel Sonnet sessions? Cross-framework parity is done; what next? | Hold parallel-Sonnet pattern until first concrete two-track work item appears | §11.7 |

---

## §14. Status, version, amendment process

| Item | Value |
|---|---|
| Doc | `PORTFOLIO-META-v0.1-EN.md` |
| Version | v0.1 — first lock |
| Date | 2026-05-09 |
| Author | Pete Y. + Cowork Opus session |
| Audience | Every Cowork session on entry; Pete; future MI-M-T contributors |
| Provisional location | `SUPIN/PORTFOLIO-META-v0.1-EN.md` |
| Final location | `_portfolio-meta/PORTFOLIO-META-v<latest>-EN.md` (after GATE-PORT-4 closes) |
| Companion files (deferred) | `_maps/mind-idea-map.md`, `_maps/architecture-map.md`, `_maps/methods-map.md`, `_maps/hack-tech-map.md`, `_maps/provenance-map.md`, `_maps/cadence-state.md`, `_gates/portfolio-gates.md` |
| Status | Ready for Pete review + ratification |

### §14.1 Amendment process

This document is versioned. Substantive changes (new lock, new principle, retired pattern) bump the version (v0.1 → v0.2 → ...). Editorial changes (typos, clarifications) bump the date stamp inline without version change. Each version supersedes the previous; old versions remain in repo history but are not authoritative.

A new version is authored when:
- A new portfolio-level decision is locked
- A new map or convention is added or retired
- A Gate definition changes
- The Sonnet orchestration pattern is updated based on new lessons learned
- Pete explicitly requests review

Drafting authority: Opus master sessions. Ratification: Pete.

### §14.2 Read order on session entry

Every Cowork session reads, in this order:

1. `PORTFOLIO-META-v<latest>-EN.md` (this document)
2. `_maps/cadence-state.md` (current portfolio state)
3. Project-specific session-close doc for the project being worked on
4. Any Gate-status updates relevant to the session's planned work

Total reading time at v0.1 scale: ~25 minutes. Worth the cost — saves hours of re-derivation per session.

---

## §15. What this document does NOT do

- Does not create the `lege-artis` GitHub org (that's GATE-PORT-1, Pete's manual action)
- Does not populate the maps (that's §5.2 follow-up)
- Does not migrate Bouračka to two-book Excel (that's v0.5.2 Bouračka task, blocked behind Fourier validation)
- Does not author the first Sonnet handoff under the new orchestration patterns (that's per-task)
- Does not lock MI-M-T core repo location (that's OQ-PORT-1)
- Does not mandate a specific map population schedule (that's per-trigger per §5.3)

The above are all explicit follow-ups. Tracking them is the Cadence/State Map's job once it exists.

---

## §16. End

This v0.1 establishes the architectural ground. Fourier weekend Stage 1 starts on top of stable conventions. Future portfolio expansions (additional case studies, additional commons modules, additional publication-tier sites) plug into the same conventions without needing to renegotiate the basics.

Read it, ratify it, then everything else proceeds.
