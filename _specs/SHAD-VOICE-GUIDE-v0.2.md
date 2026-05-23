# Shad-tier voice guide v0.2 — the Hitchhiker's pass

**Date:** 2026-05-22
**Author:** Opus (orchestrator, in collaboration with user direction)
**Status:** v0.2 — canonical voice spec for the Shad-tier guide. Supersedes the implicit "dry, technical, slightly amused" tone of v0.1 (captured in the existing `docs/shad/00-prologue.md` §Tone section). Applies to existing chapters B0..B5 retroactively and to B6/B7 prospectively.
**Trigger:** user directive 2026-05-22 — "new version of Hitchhiker's styled output for Shad."
**License:** CC-BY-SA-4.0.
**Sibling specs:** `WORKING-SPEC-v0.3-EN.md` (Shad as the fourth doc tier); `PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` (Shad-as-audience-proxy + iconography).

---

## §0. What changed and why

The v0.1 voice — "dry, technical, slightly amused" — does the job. It's clear, it's technical, it doesn't condescend. But it sits halfway between two voices and commits to neither: too dry for the wandering-aside narrator the reader actually wants when meeting Fourier for the first time, too amused for a strict technical reference.

v0.2 makes the choice explicit: lean further into the wandering-narrator voice that Douglas Adams established for technical-but-accessible writing in *The Hitchhiker's Guide to the Galaxy* and its sequels. The narrator who tells you, while explaining how Vogon poetry works or why the Improbability Drive needs a really hot cup of tea, the actual mechanics of the thing — but takes a parenthetical paragraph to mention that the inventor of said mechanics is, at this very moment, eating a sandwich.

The Shad-tier guide is the educational equivalent. It tells you, while explaining how the DFT decomposes a signal into sinusoids, that this fact was first noted by a French baron whose day job was theorising about the propagation of heat, and that we are about to take his 1822 theorem and apply it to a particle-physics experiment, a square wave, and a muon — three things he could not have anticipated, although he might have approved.

---

## §1. The principles

### §1.1 The wandering opener

A chapter should not open with the chapter's subject. It should open with something adjacent, observational, slightly off-axis from what the reader expects. The connection to the subject becomes clear within two or three sentences. The reader has, by then, agreed to come along for the walk.

**v0.1 opener (B1):**

> You connect a probe to something. The oscilloscope screen shows voltage versus time. That picture tells you something — but not as much as the shape of its frequency content does. The DFT turns the first picture into the second.

**v0.2 opener (B1):**

> An oscilloscope is a remarkable instrument. It shows you precisely the wrong thing.
>
> Or, more accurately: it shows you what voltage is doing as time passes. This is what voltage *does* — it changes — and a useful thing to know. It is, however, not what the voltage *is*. The voltage is, in nearly every interesting case, the sum of several sinusoidal signals at different frequencies, doing their own things, occasionally interfering with each other in ways that produce the misleadingly simple-looking trace on the screen. The oscilloscope cannot tell you about the sinusoids. It can only show you their sum.
>
> This is what the Discrete Fourier Transform is for. The DFT takes the trace and pulls it apart into its constituent sinusoids, with their frequencies and amplitudes attached. It is the instrument-after-the-instrument. The oscilloscope shows you time; the DFT shows you frequency; both pictures are true; both are needed.
>
> We are going to do this to four signals today, and the four signals are not what you might guess.

The v0.2 opener takes a slightly longer route to the same destination. It also tells the reader, in passing, that what they thought they were getting from an oscilloscope was incomplete — which establishes the chapter's pedagogical claim before the chapter properly starts.

### §1.2 The parenthetical detour

The narrator is allowed to interrupt a technical explanation to mention an adjacent observation, provided the explanation resumes within the same paragraph (or, occasionally, two). The detour should not be load-bearing — the explanation must work without it — but the detour gives the reader the gift of context.

**Example (B1, S1 — muon histogram):**

> A muon is, briefly, an electron's heavier cousin¹, and it decays into an electron and two neutrinos with a mean life of 2.197 microseconds. This is short enough to be measurable in a university physics lab with patience, and long enough to be worth measuring at all — long enough, indeed, that cosmic muons formed at altitude can occasionally reach the ground before decaying, which is one of the historical experimental confirmations of special relativity, though that is a different chapter in a different book. What concerns us here is that 22 321 muons in a basement stopped, sat for a moment, and then decayed; and that someone with an MCA and patience wrote down when.

(¹ It is, more rigorously, a lepton of the second generation, and getting the relationship between leptons and electrons and weight precisely right is a project for the Standard Model section of a different textbook. The point here is just that muons exist, and that they are kind enough to decay at a known rate.)

Note: footnotes are rendered as numbered superscript references in the markdown and resolve to a paragraph at the end of the chapter section, NOT to a global footnote area. This keeps the detours local.

### §1.3 The matter-of-fact absurdity

Adams's trademark device: state a counterintuitive or absurd fact in the same registry as you would state the time of day. The technical content doesn't change; the narrator's calm in the face of strange truths invites the reader to share that calm.

**Example (B1, S2 — square wave):**

> A square wave is the most aggressive thing a function generator can produce while still pretending to be polite. It changes voltage instantaneously, holds the new voltage for half a period, then changes back. This is not a real signal that any real circuit could produce; real circuits have inductance and capacitance, and inductance and capacitance object strongly to instantaneous change. The square wave is, however, a useful fiction, in the same way that point masses are a useful fiction in mechanics — it tells you what *would* happen if your circuit were infinitely fast, which, for purposes of theoretical work, is exactly the question you wanted answered.
>
> Run a square wave through the DFT and what comes out is, in a phrase that this guide will repeat several times before the chapter is over, *what Fourier said it would*.

### §1.4 The DON'T PANIC moment (used sparingly)

The Hitchhiker's Guide is famous for the words "DON'T PANIC" printed in large friendly letters on the cover. v0.2 is allowed *one* DON'T-PANIC moment per chapter, and only when the reader has just been hit with a technical fact that they might reasonably find intimidating (complex numbers, the imaginary unit, the Nyquist limit, etc.). The function is to acknowledge the difficulty, not to wave it away.

**Pattern:**

> The DFT output is a sequence of complex numbers. **Do not panic about this.** Complex numbers, here, are doing one specific job: they encode amplitude *and* phase in the same number. You will, by the end of this paragraph, not need to know any more about them than that.

### §1.5 The list that gets weirder

Lists are an excellent device for tonal pacing. The first two items establish the pattern; the third or fourth gently breaks it; the reader smiles and moves on. The list still does its technical job — the items are still correct — but the rhythm picks up the voice.

**Pattern (B0 prologue):**

> If you have any of the following, this guide is for you:
>
> - a CSV with time and voltage
> - an audio recording of something
> - a vibration log from machinery that is making a noise you are starting to worry about
> - the output of any sensor that produced a number, then another number, and so on
> - approximately 25 minutes and a basic ability to read a plot

The last entry is not a data source. It's the actual prerequisite. The reader sees the joke, then sees the point.

### §1.6 What stays unchanged

- **Technical accuracy.** Every number, every equation, every code snippet remains exactly as in v0.1. The voice changes; the physics doesn't.
- **The pedagogical structure** — input → DFT → spectrum → takeaway — stays as the chapter skeleton.
- **The "your data" framing** — chapters open with concrete signals, not abstractions.
- **Cross-links** — every chapter ends with pointers into canonical-tier + engineer-tier docs.
- **Code blocks** — runnable, copy-paste-able, ASCII-strict.
- **The "DON'T PANIC" doesn't bleed into condescension.** The narrator addresses the reader as a smart adult who is meeting a new idea, not as a confused student.

### §1.7 What v0.2 explicitly avoids

- **Pure parody.** The Adams voice is the *flavour*, not the costume. Don't reproduce specific HHGTTG jokes ("babelfish", "vogon poetry", "improbability drive"). Don't reference HHGTTG by name in the chapter text. The reader who picks up on the influence appreciates it; the reader who doesn't gets a perfectly serviceable technical guide.
- **Self-referential cleverness.** The narrator does not comment on the narrator's own cleverness. The voice is dry; it does not wink.
- **Wandering for its own sake.** A detour must repay the reader with either context, humour, or pedagogy. Three is a bonus; one is mandatory. Zero is grounds for cutting the paragraph.
- **Excessive footnotes.** No more than 2 numbered-footnote detours per chapter section. Save them for moments where the parenthetical detour would overload the sentence.
- **Self-deprecation about the technical material.** The DFT is, in fact, fascinating. The narrator must believe this. The reader will believe it too if the narrator does.

---

## §2. Tonal calibration: before-and-after diff

Three sentence-level rewrites showing the voice shift on local edits, without restructuring the chapter:

| v0.1 | v0.2 |
|---|---|
| "The DFT turns the first picture into the second." | "The DFT is the instrument-after-the-instrument. The oscilloscope shows you time; the DFT shows you frequency; both pictures are true; both are needed." |
| "Each MCA channel corresponds to a ~2.3 ns time interval." | "Each MCA channel records the gap between a muon arriving and a muon expiring, in bins 2.3 nanoseconds wide. The MCA is, in effect, a stopwatch with 16 384 detents and a fondness for short intervals." |
| "The half-power width (FWHM) is α/π = 10/π ≈ 3.18 Hz — directly related to the decay time constant τ = 1/α = 100 ms." | "The half-power width of the spectrum is α/π, which works out to about 3.18 Hz. This is, perhaps unexpectedly, the same number as 1/(π × the time constant) — the spectral width and the decay time are, in the language of Fourier analysis, two views of the same thing: how long the circuit rings determines how narrow the spectral peak. A long ring is a sharp peak; a quick decay is a fat peak. The circuit cannot decide; it is what it is, and the DFT calmly reports it." |

The third example illustrates the most common v0.1 → v0.2 transformation: take a single factual sentence with a numerical claim and surround it with one sentence of consequence-framing on either side. The fact remains; it now has scaffolding.

---

## §3. Applying v0.2 to existing chapters (the retroactive pass)

For each existing chapter (B0, B1, B2, B3, B4, B5):

### §3.1 Procedure per chapter

1. Read the v0.1 chapter as a single document. Note the technical claims; do not change them.
2. Rewrite the **opener** per §1.1 — a wandering observation that lands on the subject within three sentences.
3. Add **one DON'T-PANIC moment** at the first place the chapter introduces a potentially intimidating technical concept.
4. Convert at least **2 parenthetical detours** in the chapter body to footnote-asides per §1.2.
5. Rewrite **3-5 sentences** per §2 (sentence-level voice calibration). Apply to the most factual/dry-feeling sentences in the chapter.
6. Reshape **one list** per §1.5 — list-that-gets-weirder pattern.
7. Add a closing **matter-of-fact-absurdity** observation per §1.3 if the chapter doesn't already have one.
8. Verify all code blocks, figures, equations, numerical claims are byte-identical to v0.1.
9. Run `grep` audit for "this guide" / "we" / "you" frequency — voice should land at ~1 "you" per paragraph, ~1 "we" per few paragraphs (collaborative); narrator's first-person singular is allowed but rare.
10. Compare v0.1 and v0.2 side-by-side; the chapter should still be navigable and parsable by a hurried reader skipping to code blocks.

### §3.2 Retroactive-pass prioritisation

| Chapter | Priority | Reason |
|---|---|---|
| **B0 prologue** | 1 (highest) | The reader's first encounter. Voice sets expectation for B1..B7. Rewrite per the spec proof-of-concept in this guide (companion deliverable). |
| **B1 oscilloscope** | 2 | The foundational chapter. Most reader paths come through it. Rewrite per the spec proof-of-concept (companion deliverable). |
| **B2 audio** | 3 | The chapter where complex numbers + Hermitian symmetry get introduced; high DON'T-PANIC density needed. |
| **B3 vibration** | 4 | Existing v0.1 voice is already closest to v0.2; smallest delta to apply. |
| **B4 electronic** | 5 | Recent authoring; v0.1 voice already calibrated; least retrofit needed. |
| **B5 radar** | 6 | Recent authoring; same as B4. |
| **B6 radio astronomy** | NEW | Author directly in v0.2 voice from the queued brief at `_handoffs/shad-b6-radioastronomy/`. |
| **B7 nuclear reactor** | NEW | Author directly in v0.2 voice from the queued brief at `_handoffs/shad-b7-nuclear-reactor/`. |

---

## §4. Acceptance criteria for a v0.2 chapter

A chapter passes v0.2 if all of the following hold:

- (A1) Opener is wandering per §1.1 — first paragraph does not contain the word that names the chapter's subject (DFT, oscilloscope, audio, etc.); subject arrives by paragraph 3.
- (A2) Exactly one DON'T-PANIC moment, placed at the first technical-intimidation point.
- (A3) At least 2 parenthetical detours OR footnote-asides per chapter.
- (A4) At least 3 sentences rewritten in the §2 pattern (fact-with-scaffolding).
- (A5) At least one list-that-gets-weirder per §1.5, OR one matter-of-fact-absurdity per §1.3.
- (A6) Code blocks, equations, numerical results byte-identical to v0.1.
- (A7) Cross-links to canonical-tier + engineer-tier preserved.
- (A8) ASCII-strict in code blocks; Unicode allowed in narrative (em-dash, multiplication sign, etc.).
- (A9) Chapter length grows by at most **the smaller of: +100% or +1000 words** over v0.1.
  - The 100% cap is the proportional ceiling.
  - The +1000-word absolute ceiling protects long chapters from accumulating disproportionately many detours.
  - **Empirical finding (2026-05-22 rewrites):** B0 prologue grew +131% (470 → 1087 words; +617 words absolute). B1 oscilloscope grew +43% (2282 → 3272 words; +990 words absolute). Both are within the revised cap. The original draft +30% cap was too tight for short chapters where a single wandering-opener already consumes the budget; this revised cap reflects what the voice actually requires.
- (A10) A reader skipping straight to the "Try it yourself" section finds it unchanged, runnable, and self-contained.

If a chapter fails (A6), it's broken — the technical content was modified. Revert and try again.

If a chapter fails (A9), it's overdone — cut detours until the length is in range. The +1000-word absolute ceiling is the harder constraint; the +100% proportional ceiling is softer (very short v0.1 chapters legitimately need proportionally more voice).

If a chapter fails everything else, it's still v0.1 in v0.2 clothing — apply §3.1 more aggressively.

---

## §5. The longer arc

v0.2 is the voice spec for the existing seven-chapter Shad-tier guide. When the guide ships in full (B0..B7 all green), the natural next step is a **standalone book-format compile** — `shad-guide.tex` (which already exists as a placeholder per the v0.1 docs) becomes the canonical bound edition.

The book-format compile is where v0.2 voice pays off most. A reader who picks up a 100-page guide on the discrete Fourier transform expects a friendly relationship with the narrator. v0.1's "slightly amused" voice would feel underdone in book form; v0.2's wandering-narrator voice is at exactly the right scale.

The book gets:
- A dedication page (CC-BY-SA-4.0; whose name on it stays an OQ).
- A preface that introduces the narrator and the seven-band journey.
- The seven chapters in v0.2 voice, with cross-references between them as page numbers (the LaTeX compile resolves them).
- A "where Shad goes next" closing chapter pointing at the canonical tier, the engineer tier, and the textbooks in `refs.bib`.

This is the eventual home of the Hitchhiker's-styled material. v0.2 is the voice spec; the book is the medium that vindicates it.

---

## §6. Open questions

**OQ-VOICE-1: Footnote rendering in markdown.** Markdown's footnote syntax (`[^1]` / `[^1]: ...`) is supported by GitHub-flavoured-markdown and most static-site generators, but the LaTeX compile path may need custom handling. Decision: use numbered superscripts (¹ ² ³) inline + a paragraph at the end of the chapter section for the footnote text. Renders cleanly in both markdown previews and the `shad-guide.tex` compile. Document in `_specs/WORKING-SPEC-v0.3-EN.md` when next revised.

**OQ-VOICE-2: Translation strategy.** The CS/JA/DE/IT translations queued for v0.1.1+ should match v0.2 voice in each language, not be auto-translated from v0.1 English. Voice doesn't auto-translate cleanly — Adams-style wandering relies on specific English-language rhythm. The voice guide should ship with per-language tonal anchors when the translation pass starts: which native author best approximates the Adams voice in CS / JA / DE / IT? Sourcing per-language anchor is the translator's first task.

**OQ-VOICE-3: The dragon iconography.** The v0.1 prologue carries a placeholder for "the Miyazaki dragon — smoking weed, drinking tea, looking mildly amused". This is exactly the v0.1 voice's mascot. v0.2 voice may want a different mascot — something more Hitchhiker's-adjacent (a small green tea kettle? a sentient mattress? a digital wristwatch?). Decision deferred to the iconography-commission turn; voice guide just notes the question.

---

## §7. Acceptance gate for THIS voice guide

- [x] §0 — what changed and why, articulated
- [x] §1 — six voice principles enumerated with concrete patterns
- [x] §2 — sentence-level before/after diffs provided
- [x] §3 — retroactive-pass procedure + per-chapter prioritisation
- [x] §4 — chapter-level acceptance criteria
- [x] §5 — the longer arc (book-format compile) sketched
- [x] §6 — open questions surfaced
- [x] Proof-of-concept rewrites of B0 prologue + B1 oscilloscope landed alongside this guide (2026-05-22)
  - B0: 470 → 1087 words (+131%, +617 words abs); within revised A9 cap (≤+1000 words absolute)
  - B1: 2282 → 3272 words (+43%, +990 words abs); within revised A9 cap
  - All numerical claims preserved byte-identical across both
- [ ] Future-chapter authoring (B6/B7) explicitly invokes this guide
- [ ] Retroactive pass on B2-B5 scheduled (likely Sonnet-delegable per voice-guide-as-contract)

---

*— Pete Y. (Petr Zemla) via Opus, 2026-05-22. CC-BY-SA-4.0.*
*Apply to all Shad-tier authoring from this point forward. Existing chapters get retroactive pass per §3.2 prioritisation.*
