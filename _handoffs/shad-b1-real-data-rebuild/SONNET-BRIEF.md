# Shad-tier B1 Oscilloscope — real-data rebuild

**Date authored:** 2026-05-13
**Author:** Opus (Mac orchestrator)
**Target executor:** Claude Code (`claude` CLI), Sonnet
**Predecessor:** B0 real-data pipeline (committed in 87037da; the `b1-scope/`
  workspace at `fourier/examples/shad/b1-scope/` is where B0 lives — see
  `render_components.py`, `render_s1/s2/s3.py`, kernel CLIs, data fixtures
  S1/S2a/S2b/S2c/S4). B1 chapter currently uses **synthesised** data per
  ThinkPad's first-deliverable batch (commit `d74b0cc`); this brief
  rebuilds it around real captures.
**Estimated effort:** 6-8 Sonnet hours (most time is in data acquisition + parse +
  render scripting; the kernel cross-check is already-working B0 infrastructure).

---

## §0. Why this brief exists

The shipped B1 chapter at `fourier/docs/shad/01-oscilloscope.md` synthesises
its scope trace via `synth_scope_trace()` in `b1-scope/main.py`: 240 Hz sine
at 1 V, 10 kHz sample rate, 10% noise floor, 50 ms total. Clean tutorial
data — but contradicts the lege-artis project's "real data, not synthesised"
discipline established for B0 (where the entire Step 6 component-invocation
pipeline runs on actual muon / audio / etc. captures).

The B1 rebuild applies the **B0 pattern** to the foundational
"raw scope trace" tier. The output is a chapter that walks the reader through
3-5 actual scope captures, each annotated with what the DFT reveals about that
specific physical phenomenon — exactly mirroring B0 in scope and discipline,
but framed for the most foundational tier (raw voltage-vs-time).

The B5 radar chapter (Mac-authored, in tree at `fourier/docs/shad/05-radar.md`)
is a useful structural reference for how a multi-fixture B-tier chapter reads.

---

## §1. The 4 deliverables

### §1.1 Deliverable A — Fixture matrix: 3-5 real scope captures

The B1 chapter's role in the shad-tier ladder is **"raw voltage vs time on
an oscilloscope screen"** — most foundational, no audio context, no
vibration context, no domain-specific filtering. Fixtures should reflect
that: signals that look like what you'd see on a benchtop scope's screen
the moment you connect a probe to something.

**Pre-planned S1: Rodriguez muon scope trace.** Probe script already exists
at `fourier/examples/shad/b1-scope/probe_b1_muon.py`. Run it first:

```bash
cd fourier/examples/shad/b1-scope
python probe_b1_muon.py
```

That fetches the Rodriguez MuonLifetimeData.zip, unpacks into `data/muon/`,
and dumps the structure. **Paste the script's stdout into STATUS-FILLED §3
verbatim — the chapter prose then references the actual file layout** rather
than speculating.

Per the probe-script header: the dataset is **not redistributed** with
lege-artis/fourier. The chapter embeds first-N-row snippets under fair-use
educational citation with full attribution to Santiago Rodriguez's site, and
the reader-side workflow fetches the zip via the probe script.

**Candidate S2-S5 fixtures (pick 2-4):**

| ID | Candidate fixture | Why it fits B1 | Source / license |
|---|---|---|---|
| S2 | Square-wave clock signal | Canonical "Fourier 101" — shows odd-harmonic series exactly as Fourier predicted in 1822. Demonstrates that even a "simple" digital signal contains infinite frequency content. | Wikimedia Commons public-domain scope shots (search: `square wave oscilloscope`); or generate from a real function-generator capture if reader has one. Many public-domain CC0/PD examples exist. |
| S3 | Triangle wave (or sawtooth) | Contrasts with square wave: same fundamental, different harmonic falloff (1/n² vs 1/n). Lets the chapter make the "DFT measures *shape*, not just frequency" point. | Same source class as S2. |
| S4 | RLC damped oscillation transient | Step response of a real RLC circuit. Shows decaying sinusoid → smooth spectrum (no harmonics) → introduces the contrast between periodic + transient content. | Public-domain physics-lab scope captures, or NIST / NPL educational resources. |
| S5 | Sine wave buried in noise (real SNR test) | Foundational signal-detection demo: time-domain trace looks like noise; DFT reveals the buried tone. Bridge to B2 (audio) where signal-in-noise becomes the main theme. | Pulsar dataset (early millisecond pulsar pulses in radio-telescope scope captures), or noise-floor measurements from public radiometric data. |
| S6 | Pendulum + photogate transient | Physics-lab classic: photogate output during pendulum swing. Slow signal, but lets the chapter discuss "low-frequency" Fourier analysis where sample rate >> signal bandwidth. | University physics-lab open datasets; PhET or similar. |
| S7 | Mains-power transient (lightning, brownout) | If electric-power-grid open data is accessible, a real transient capture shows the "single event surrounded by background" detection problem. **Risk: overlaps with B4 Electronic** — only include if scope differs meaningfully (B4 is steady-state harmonics; S7 here would be transient detection). | Public power-quality datasets (NREL?). |

**Recommended fixture set: S1 (muon) + S2 (square wave) + S3 (triangle) + S4 (RLC damped) — 4 fixtures.** Hits the four canonical regimes:
- S1: single sharp pulse (transient)
- S2: pure harmonic series (periodic)
- S3: tapered harmonic series (also periodic, but different content)
- S4: decaying sinusoid (transient with internal periodicity)

If time runs short, S1 + S2 + S3 alone is sufficient for a complete chapter.
S5/S6/S7 are optional stretches.

### §1.2 Deliverable B — Probe + fetch + parse scripts per fixture

Mirror the B0 pattern (`render_s1.py`, `render_s2.py`, `render_s3.py` in
`b1-scope/`) but renamed for B1's fixtures:

```
fourier/examples/shad/b1-scope/
  ├── probe_b1_muon.py           (already exists)
  ├── probe_b1_squarewave.py     NEW — sources S2
  ├── probe_b1_triangle.py       NEW — sources S3
  ├── probe_b1_rlc.py            NEW — sources S4 (skip if S4 not selected)
  ├── render_b1_s1.py            NEW — renders muon fixture (3 figs: input/spectrum/takeaway)
  ├── render_b1_s2.py            NEW — renders square wave (3 figs)
  ├── render_b1_s3.py            NEW — renders triangle (3 figs)
  ├── render_b1_s4.py            NEW — renders RLC (3 figs, if selected)
  └── data/
      └── muon/                  (data/ exists from probe_b1_muon.py)
      └── b1_s2_squarewave.csv   NEW — small CSV of head + tail
      └── b1_s2_head.txt         NEW — first 30 rows for chapter embed
      └── (similar for S3, S4)
```

Each `probe_*.py` script:
- Fetches the source (or, where licensing forbids redistribution, stages a
  reader-side fetch from the original URL with attribution comment)
- Parses to a NumPy-friendly array (time, voltage) and/or CSV
- Writes `data/b1_<sN>_head.txt` (30 rows) for chapter embed
- Optionally caches the full capture under `data/<sN>/` if license permits

Each `render_b1_sN.py` script:
- Loads the fixture data
- Computes DFT (NumPy `np.fft.fft`)
- Generates 3 PNG figures using matplotlib at the project's existing style:
  - `figures/fig-b1-s<N>-input.png` (time domain)
  - `figures/fig-b1-s<N>-spectrum.png` (frequency domain)
  - `figures/fig-b1-s<N>-takeaway.png` (annotated single-frame key insight)
- Prints to stdout: peak frequency, peak amplitude, noise floor, SNR
  estimate (for the chapter to cite)

### §1.3 Deliverable C — Rewrite `fourier/docs/shad/01-oscilloscope.md`

Re-author the chapter around the 3-5 real fixtures. Match the B5 radar
chapter's structure (`fourier/docs/shad/05-radar.md`) as the closest
in-tree precedent:

1. **Premise** (1-2 paras) — what an oscilloscope sees, why frequency
   content is richer than amplitude-vs-time
2. **The fixtures** — list the 3-5 real datasets with source attribution,
   why each was chosen, links to the probe scripts
3. **For each fixture** (one section per):
   - Brief context (1 para — what generated this signal in the physical
     world)
   - Input fig (`fig-b1-sN-input.png`)
   - Pipeline snippet (the 3-5 lines of NumPy + the head-of-data table)
   - Spectrum fig (`fig-b1-sN-spectrum.png`)
   - Takeaway fig (`fig-b1-sN-takeaway.png`)
   - Real-data observations (peak freq, harmonic structure, leakage, SNR)
4. **Cross-fixture synthesis** — what the 4 fixtures together teach about
   what the DFT does (a clean periodic, a tapered periodic, a transient, a
   pulse — each in turn). This is the chapter's pedagogical payload.
5. **Try it yourself** — clone, install, run `python render_b1_s*.py` to
   regenerate. Each probe script's licence/attribution note repeated for
   the reader.
6. **Cross-references** — same `..canonical/en/01-dft-definition.md` +
   `..engineer/en/...` + `../../backends/fortran/` + `../../backends/cpp/`
   block as the existing chapter; verbatim if no changes needed.

**Length target:** 200-350 lines of markdown. The current chapter is 75
lines. This rebuild is substantially longer because the multi-fixture
narrative + real-data observations carry more content per chapter.

**Sanity check:** the chapter must read as **complementary, not duplicative**
with B5 radar (`05-radar.md`). B5 is domain-specific (radar techniques);
B1 is signal-level foundational (what a scope shows). Don't drift into
domain content here.

### §1.4 Deliverable D — Update `fourier/docs/shad/shad-guide.tex` Chapter 1

The Mac-authored standalone TeX (`shad-guide.tex`) contains a Chapter 1 (B1)
that matches the synthesised-data narrative. After the markdown rebuild
(§1.3) is locked, port the new prose + fixture references into the TeX
source. The TeX source's chapter numbering is **-π-i, -π, 0, 1, 2, 3, 4, 5**
where chapter 1 = B1 oscilloscope. Update chapter 1 only; leave others
alone.

Once TeX updated, regenerate the PDF:

```bash
cd fourier/docs/shad
./build-pdf.sh
```

The rebuilt `shad-guide.pdf` should be in the same directory.

### §1.5 Deliverable E — Step 6 multi-kernel cross-check (optional, recommended)

For ONE of the fixtures (recommend S2 — square wave, since its DFT has
sharp predictable peaks), run the existing 3-kernel cross-check pipeline
(`render_components.py` from B0 work):

```bash
cd fourier/examples/shad/b1-scope
.venv/bin/python render_components.py --fixture=b1_s2 --N=64
```

Modify `render_components.py` if needed to accept an `--fixture` arg
that selects which fixture's first-N samples to feed through all three
kernels (NumPy + lege-artis/fourier C++ + lege-artis/fourier Fortran).
Expected outcome: per-kernel max abs error vs NumPy oracle ~1e-13 or
better. Add a sub-section to the B1 chapter showing the 3-kernel
agreement table (mirroring B0's component-invocation pattern).

If `render_components.py` cannot be cleanly extended without refactoring,
defer Deliverable E to a phase-7b cross-check brief and emit a 3-line
note in the chapter acknowledging "kernel cross-check at B0".

---

## §2. Acceptance gate

- [ ] Deliverable A — 3-5 fixture probe scripts authored and tested; data fetched
- [ ] Deliverable B — render scripts produce 3 PNG figures per fixture
- [ ] Deliverable C — `fourier/docs/shad/01-oscilloscope.md` rewritten;
      matches B5-style structure; cites real-data observations per fixture
- [ ] Deliverable D — `fourier/docs/shad/shad-guide.tex` Chapter 1 updated;
      PDF regenerated cleanly via `./build-pdf.sh`
- [ ] Deliverable E (optional) — 3-kernel cross-check section added for at
      least one fixture
- [ ] `fourier/docs/shad/README.md` updated if needed (the chapter-list
      table may need updates to reflect the B1 rebuild — likely just
      version bump, but check)
- [ ] `fourier/shared/reference-bibliography/refs.bib` augmented with
      attribution entries for any newly-cited datasets (Rodriguez muon
      data, square-wave source, etc.)
- [ ] STATUS-FILLED.md written per template in §4
- [ ] No forbidden identifiers introduced (SUPIN/Bouracka/MI-M-T/MIM2000/Yamyang/Improwave)

---

## §3. Probe script output capture format (S1 muon — what to paste back)

The `probe_b1_muon.py` script outputs structure + first-30-rows. Capture
**all stdout** to `STATUS-FILLED.md §3` so the chapter authoring can
reference exact file layout. Example placeholder:

```
=== probe_b1_muon.py stdout ===

(paste full output here — file listing with sizes, first-30 lines of each
ASCII text file, hex dump of binary files, summary heuristic)

=== end probe_b1_muon.py stdout ===
```

Same convention for S2/S3/S4 probe scripts when they're authored.

---

## §4. STATUS-FILLED.md template

```markdown
# Shad-tier B1 real-data rebuild: STATUS-FILLED

**Date completed:** YYYY-MM-DD
**Agent:** Claude Sonnet 4.6 (b1-rebuild task)
**Scope:** Re-author B1 chapter around 3-5 real oscilloscope fixtures
  (was synthesised in current shipped state).

## §1 Acceptance gate

[Fill the §2 checklist from SONNET-BRIEF.md, status per item]

## §2 Fixture matrix landed

| ID | Fixture | Source / license | Probe script | Render script | Figures |
|---|---|---|---|---|---|
| S1 | Rodriguez muon | (cite) | probe_b1_muon.py | render_b1_s1.py | fig-b1-s1-{input,spectrum,takeaway}.png |
| S2 | Square wave | (cite) | probe_b1_squarewave.py | render_b1_s2.py | ... |
| S3 | Triangle wave | (cite) | probe_b1_triangle.py | render_b1_s3.py | ... |
| S4 | RLC damped (or "skipped") | (cite) | ... | ... | ... |

## §3 Probe-script captures

=== probe_b1_muon.py stdout ===
[paste]
=== probe_b1_s2_squarewave.py stdout ===
[paste]
... (etc.)

## §4 Chapter prose summary

[Brief description of how the 3-5 fixtures are woven together. What
pedagogical arc the chapter establishes (e.g., "pure periodic → tapered
periodic → transient → pulse — building up the DFT's repertoire"). Word
count of final chapter.]

## §5 Cross-references updated

- README.md chapter listing: [updated/unchanged]
- refs.bib entries added: [list, with cite-keys]
- shad-guide.tex Chapter 1: [updated/unchanged]
- PDF regenerated: [size, build OK?]

## §6 Open questions for Opus

[Anything that needs Opus decision before next phase — e.g., chapter
length, fixture selection rationale, cross-link strategy.]

## §7 Backends / fixtures that resisted

[Empty if none. Otherwise: which fixture, why, what was tried.]
```

---

## §5. Failure-mode escalation

- **Probe script can't fetch its source** (URL dead, license shifted, etc.)
  → escalate by listing fallback fixtures from §1.1's candidate table;
  pick replacement; document in STATUS-FILLED §7.

- **Render produces visually-broken figures** → debug matplotlib /
  binning; if persistent, regenerate the canonical B0 figures with
  matplotlib version specified in `pyproject.toml` / `.venv` to confirm
  toolchain stability.

- **Step 6 multi-kernel cross-check produces mismatch** → indicates a
  fixture-specific data-flow bug (e.g., complex array layout differs from
  B0's). Skip Deliverable E for that fixture; emit chapter without it.
  Do NOT modify the kernel sources — they're locked at v0.2.0.

- **TeX rebuild fails** → most common cause is unicode in listings env
  or unmatched braces. Compare against the B0 chapter's TeX listing
  pattern; replicate. Worst case: emit markdown-only B1; TeX update
  becomes a Phase 6c follow-up.

- **Chapter drifts longer than 350 lines** → split into B1a + B1b
  sub-sections, or trim fixture count from 5 to 3-4.

---

## §6. Open questions

**OQ-B1-1: Fixture S5 (sine in noise) vs S4 (RLC damped) — which is the
better 4th pick?** S4 introduces transient analysis cleanly; S5 introduces
SNR discussion bridging to B2 audio. Author's call; document in STATUS-FILLED.

**OQ-B1-2: Should the B1 rebuild kill the `synth_scope_trace()` function in
`b1-scope/main.py`?** If yes, that script becomes a "real-data-only" driver.
If kept as fallback, it's a "synthetic-or-real" hybrid. Recommend: keep
`synth_scope_trace()` as an internal utility but mark it as fallback-only
(remove from chapter's "Try it yourself" section).

**OQ-B1-3: Multilingual rendering of B1 — should this chapter exist in
CS/JA/DE/IT at v0.1.1+?** Per CLAUDE.md, multilingual translations are
queued v0.1.1+. B1 rebuild authors only the EN version; translations
follow.

**OQ-B1-4: Stretch: should the B1 chapter reference the Shaddack-tier
oscilloscope→EHT/LIGO progression doc (`_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`)?** This would tie B1 to the deeper engineer-narrated
documentation track. Probably wait for v0.2.x Shad-tier B1+B2+B3 batch
(per ThinkPad commit `d74b0cc`) to complete first; defer cross-link.

---

## §7. What Opus picks up next, after this brief closes

1. **Phase 6b — kh-sim golden-vector generation** is the next kh-sim track
   item (Sonnet-executable per `_audit/PHASE-6A-GOLDEN-VECTOR-MATRIX-DESIGN-v0.1.md` §9).
   That's a parallel track to this B1 rebuild — both can run independently.

2. **3-fold-path design consolidation** (task #26) is the last pending item
   in this session's planned order; opens after B1 closes.

3. **Phase 5c Gate B on ThinkPad** still pending — when STATUS-FILLED
   arrives back, kh-sim phase 6 unblocks fully.

---

*End of Shad-tier B1 SONNET-BRIEF.md.*
*Phase 6b (kh-sim golden-vector generation) is the parallel Sonnet track;*
*either can start first.*
