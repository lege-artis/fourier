# Voice Addendum (v0.2) for All Outstanding Shad-Tier Briefs

**Status:** AUTHORED 2026-05-23 (Mac/Cowork, Opus). Mandatory read for any session executing `_handoffs/shad-b5-radar/`, `_handoffs/shad-b6-radioastronomy/`, or `_handoffs/shad-b7-nuclear-reactor/`.

**Why this exists.** The three outstanding Sonnet briefs (B5, B6, B7) were authored 2026-05-11, before the SHAD-VOICE-GUIDE-v0.2 was finalised (2026-05-22/23). Each brief instructs the author to "mirror B3's voice exactly" or "match the B3 voice." That instruction is **superseded** by the v0.2 voice guide. This addendum is what brings the briefs back into compliance.

**Read these in order before starting your chapter:**

1. `fourier/_specs/SHAD-VOICE-GUIDE-v0.2.md` — the canonical voice spec. Read in full. Pay particular attention to the 6 principles (§2) and the A1–A10 acceptance gates (§4).
2. `fourier/docs/shad/00-prologue.md` (v0.2 rewrite, 1087 words) — your **new** prose exemplar #1. Replaces B3 in this role.
3. `fourier/docs/shad/01-oscilloscope.md` (v0.2 rewrite, 3272 words) — your **new** prose exemplar #2. Replaces B3 in this role.
4. **Then** the brief you were assigned (`_handoffs/shad-bN-<domain>/SONNET-BRIEF.md`).

---

## §1 — What changes from the brief as written

| Brief instruction (old) | Override (new) |
|---|---|
| "Mirror B3's voice exactly" / "Match the B3 voice" | Mirror **B0 (00-prologue.md v0.2) and B1 (01-oscilloscope.md v0.2) voice**. B3 in its current form is v0.1 voice and will be retroactively rewritten; do not use it as a voice exemplar. |
| "Density target ~200-260 lines / 6-8 markdown pages" | Density target relaxed per A9: **smaller of +100% over the v0.1 density estimate OR +1000 words absolute**. The v0.1 brief estimates were guesses; empirical v0.2 rewrites went +131% (B0) and +43% (B1). Authoring should not pad — let the voice land at whatever density it lands. |
| "Engineer-meets-astronomer voice" / "Engineer-meets-radar-analyst voice" / etc. (per chapter) | Engineer-meets-domain still holds; but the *overlay* is the Hitchhiker's wandering-narrator from §2 of the voice guide. The domain voice provides authority; the Hitchhiker's overlay provides companionability and the occasional parenthetical detour. |
| All other §s of each brief (scope, sub-topics, structural skeleton, examples, references, acceptance gates other than density, sanitisation, output) | **Unchanged. Honour them.** |

---

## §2 — The six v0.2 principles, in one-paragraph form

The voice guide §2 covers each principle in depth. Brief reminder of all six, in case you skipped:

**(i) Wandering opener.** Start somewhere unexpected — not the chapter title, not "in this chapter we will…" The B0 opener is "Most books about the Fourier transform start by writing the Fourier transform on the page." The B1 opener is "An oscilloscope is a remarkable instrument. It shows you precisely the wrong thing." Find your equivalent for your domain — something true, slightly surprising, and that the reader could not have written themselves.

**(ii) Parenthetical detour.** At least one place per chapter where the prose follows a tangent for a paragraph or two before returning to the main point. The tangent must be relevant — not random — but it does not need to be load-bearing. B0's footnote about "datum" as the Latin singular is a model. The Hitchhiker's voice grants permission to find related things interesting on the reader's behalf.

**(iii) Matter-of-fact absurdity.** State something objectively unusual in a deadpan, technical register. B1's "A square wave is the most aggressive thing a function generator can produce while still pretending to be polite" is canon. The absurdity must be *true*, not invented. The voice is the dryness.

**(iv) DON'T-PANIC.** At least one moment per chapter where complexity is about to bite the reader (a complex exponential, an integral, a transformation that swaps domains), the prose explicitly disarms it: "Don't panic. This will resolve in a paragraph." The phrase need not be literal — "this is less alarming than it looks" works — but the disarming gesture is mandatory at the first hard step.

**(v) List-that-gets-weirder.** When you produce a bulleted or comma'd list, escalate it. The last item should be the funniest or strangest. B0's "what you need to bring" list ends with "nothing else — no calculus, no remembered complex-number rules, no theorem-proving discipline." The structural payoff lives at the list's end.

**(vi) What stays unchanged.** All technical claims, numerical values, source citations, code listings, equation derivations, figures, and tables remain byte-identical to what the brief specifies. The voice does not touch the math. This is the integrity gate. The v0.2 rewrites of B0 and B1 preserved every numerical claim byte-identical (verified via grep); your v0.2 chapter must do the same.

---

## §3 — Specific overrides per outstanding brief

### B5 (Radar)

- Voice exemplar override: B0 + B1 v0.2 (not B3).
- Lead numerical claim (NEXRAD radar range/velocity extraction example): preserve exact numerics from the brief's §2.
- Suggested wandering opener seed (use or replace): *"Radar is the only field in physics where 'I detected nothing' and 'I detected everything that wasn't there' produce identical outputs and require entirely different interpretations."*
- Parenthetical detour seed (use or replace): a paragraph at the AC-mains-vs-NEXRAD section about how the same DFT operates across 14 orders of magnitude of input scale.
- DON'T-PANIC location: at the first appearance of the matched-filter expression in §3 sub-topic 2.

### B6 (Radioastronomy)

- Voice exemplar override: B0 + B1 v0.2 (not B3).
- Lead numerical claim (PSR B1937+21 period 1.558 ms, DM 71 pc/cm³, detection significance 16-σ): preserve byte-identical.
- Suggested wandering opener seed (use or replace): *"A pulsar is what happens when a star approximately the mass of the Sun is compressed into something the size of a small city and then asked to keep time. It does, with a precision that has occasionally embarrassed atomic clocks."*
- Parenthetical detour seed: a paragraph in §3 sub-topic 2 about why "coherent dedispersion" is named for what it *preserves* (phase coherence) rather than what it removes (smearing), with a brief note that the naming convention here is the opposite of the analogous convention in radar matched filtering.
- DON'T-PANIC location: at the first appearance of the dispersion-measure delay formula (`t_DM = 4.15 × DM × (1/f_lo² - 1/f_hi²)` ms).

### B7 (Nuclear reactor noise)

- **First flag:** the roadmap (`_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` §1 + §3) declares B7 "Opus only — capstone synthesis," but a `SONNET-BRIEF.md` exists. This contradiction is unresolved at the time of this addendum. If you are a Sonnet session opening this brief, **stop and surface to the project owner before authoring** — confirm whether B7 is (a) Sonnet first-cut then Opus polish, (b) reassigned to Sonnet entirely, or (c) still Opus-only and the brief was authored speculatively. Do not author B7 without that clarification.
- If clarification lands "Sonnet may proceed": voice exemplar override is B0 + B1 v0.2 (not B3).
- Suggested wandering opener seed (use or replace): *"There comes a point in any signal-processing workflow where the DFT, applied honestly, returns the wrong answer. Reactor noise is the canonical point. Not because the DFT breaks — it doesn't — but because the signal is no longer doing what the DFT assumes signals do."*
- Parenthetical detour seed: a paragraph somewhere in the "introducing Welch / wavelets / Rossi-α / Feynman-α" section about how each of those names is attached to a specific person and each person had a specific reactor in mind when they invented their method, with brief mention that this is one of the few signal-processing fields where the etymology is the curriculum.
- DON'T-PANIC location: at the first transition from pure-DFT analysis to Welch-PSD (the "bare DFT alone is insufficient here" pivot), since this is the chapter's pedagogical hinge.

---

## §4 — Acceptance: the A1–A10 voice-guide gates apply

Each v0.2 chapter must satisfy the A1–A10 acceptance gates in the voice guide §4. Brief summary, in case you don't want to flip back:

A1 wandering opener present · A2 ≥1 parenthetical detour · A3 ≥1 matter-of-fact-absurdity sentence · A4 ≥1 DON'T-PANIC at first hard step · A5 ≥1 list-that-gets-weirder · A6 all numerical claims byte-identical to the brief (verifiable via grep) · A7 all citations present and ASCII-clean · A8 footnote count ≤4 per chapter · A9 length within smaller of +100% or +1000 words absolute over brief estimate · A10 reader-model preserved (writes for "person who already paid attention through B0 and B1").

A6 is non-negotiable. If you find yourself wanting to change a numerical value to make the prose flow better, the prose changes, not the value.

---

## §5 — One-line patch to each brief

After this addendum is committed, each of the three outstanding briefs should receive a 2-line header insert immediately after its first heading:

```
**VOICE UPDATE (2026-05-23):** Read `_handoffs/SHAD-V0.2-VOICE-ADDENDUM-FOR-BRIEFS.md` BEFORE proceeding. The "mirror B3 voice" instruction in this brief is superseded; new exemplars are B0 + B1 v0.2.
```

This patch is applied to all three briefs in the same commit as this addendum. The patch is minimal so the briefs' substantive content (scope, references, structure, acceptance gates) is not disturbed — only the voice exemplar pointer changes.

---

**End SHAD-V0.2-VOICE-ADDENDUM-FOR-BRIEFS.md**
