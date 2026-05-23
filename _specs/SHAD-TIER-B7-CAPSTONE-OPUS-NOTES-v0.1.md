# Shad-tier B7 capstone — Opus staging notes

**Status:** Pre-authoring research + scope-lock. NOT a Sonnet brief.
**Authoring owner:** Opus (project owner direction — B7 synthesis judgement requires holding the full reader-model across multiple sub-topics).
**Estimated effort:** 2 Opus sessions. Sequenced AFTER B6 lands.
**Updated:** 2026-05-11 — framing flipped from "synthesised primary" to "real primary + synthesised explanation" per project-owner pushback.

---

## §1. Why this chapter is special

B1-B6 each took a single domain and showed how the DFT applies there. **B7 is the synthesis chapter.** It does two things at once:

1. **Stress-tests pure DFT.** A nuclear reactor signal is non-stationary (start-up, scram, control-rod motion), non-linear (neutron-thermal-hydraulic coupling produces frequency intermodulation), and embedded in correlated noise. Pure DFT analysis gets the reader 60% of the way and then stops being useful.
2. **Introduces the "Fourier and beyond" toolkit.** Welch PSD, wavelets, Rossi-α, Feynman-α, bispectrum, HHT-EMD, coherence + transfer-function methods. Each unlocks an analysis the bare DFT can't.

After B7, Shad understands:
- *When* pure DFT is the right tool (stationary, linear, single-source: B1-B6)
- *Where* it breaks down (non-stationary transient, non-linear coupling, system-dynamic feedback: B7)
- *How* to extend beyond it (the toolkit)
- *Why* nuclear-reactor signal analysis is the canonical domain that needs all of this — every constraint matters, and you can read the dynamics off the spectrum if you know what to look for

This is graduation-level material. It needs synthesis judgement, not template-following — which is why it's Opus, not Sonnet.

---

## §2. Pre-authoring research checklist

Before opening the authoring session, complete this checklist:

### §2.1 Primary real-data candidates — pick one at session time

Three real-data sources are pre-cleared as candidates. The authoring session evaluates and picks ONE for the chapter's primary example:

| # | Source | License / Access path | Initial recon |
|---|--------|----------------------|---------------|
| 1 | **OECD-NEA Data Bank — Halden Reactor Project (HRP) archives** | Registration at `nea.oecd.org/dbforms/data/eva/evatapes/` (free for member-state academics). Look specifically for HRP noise-diagnostic work packages + IRPHE benchmarks containing time-series. | Pázsit/Pál/Williams textbooks cite specific Halden experiments — work backwards from textbook figures to find the raw-data source. Probably the highest-quality data, slightly higher access friction. |
| 2 | **VR-1 "Vrabec" — Czech Technical University Prague (FJFI ČVUT)** | Open via university repository (`vr1.cvut.cz` + DSpace at ČVUT). Look for Kropík, Sklenka, Bilý publications. | Pedagogical reactor *by design*. Lowest access friction. Project owner has local-advantage path for direct contact if needed. **Recommended as default unless Halden has cleaner Lorentzian signature.** |
| 3 | **TU Wien Atominstitut — TRIGA Mark II** | Open via TU Wien institutional reports + Kerntechnik / Nuclear Engineering & Design publications. | Alternate if Halden registration drags or VR-1 data unsuitable. Comparable pedagogical scale to VR-1. |

**Evaluation criteria for picking ONE:**
- Lorentzian-PSD signature visible in raw data (the chapter's central reveal)
- Sample rate documented (need ≥1 kHz for prompt-neutron-decay extraction)
- Duration 10-60 seconds workable (smaller for repo fixture; bigger for averaging analysis)
- License compatible with CC-BY-SA-4.0 redistribution as a chapter example
- Sample size ≤1 MB after decimation/excerpting (fits as repo fixture; full original cited)

**Fallback if all three primaries miss:** synthesised reactor-noise as primary (the original conservative framing), with one of the three real datasets referenced + a clear note in the chapter that "the synthesised signal mimics the canonical Halden / VR-1 / TRIGA noise characteristics described in [textbook]."

### §2.2 Synthesised-model implementation — the theoretical backbone

The synthesised reactor-noise model is the *explanation* layer (per the revised framing). Even when real data is the chapter's hero, the synthesised model is what teaches Shad why the signal looks the way it does. Implementation requires:

- Point-kinetics equations with delayed-neutron precursor groups (typically 6 groups for thermal reactors)
- Stochastic source term (Langevin-style; Pál §4 or Williams Ch. 5 gives the canonical form)
- Optional thermal-feedback term (reactivity ∝ -α_T × T_fuel for negative coefficient)
- Optional xenon-iodine slow loop (Bateman equations; shows up as ~10-hour-period feature in long simulations — probably out of scope for 60-second example)

Target ~150 lines of careful numerical work in `examples/shad/b7-nuclear-reactor/main.py`. Allow more if needed — B7 is the longest chapter.

### §2.3 Toolkit walkthrough — "Fourier and beyond"

Each toolkit method gets a small demo + a paragraph + a figure. Plan the sequence:

1. **Welch's method** (`scipy.signal.welch`) — first step beyond bare DFT for stationary signals. The chapter's first "and beyond" tool.
2. **Spectrogram / STFT** (`scipy.signal.spectrogram`) — time-frequency localisation. Apply to a control-rod-step or scram transient.
3. **Wavelets** (`pywavelets`) — finer time-frequency tradeoffs for non-stationary features.
4. **Rossi-α + Feynman-α** (custom, ~50 lines each) — reactor-specific noise diagnostics. THESE are the chapter's specialty payoff — Shad sees diagnostics he can't get any other way.
5. **Bispectrum** (custom or via `stingray`) — detect non-linear coupling. Demonstrate that two coupled frequencies produce signal at f₁+f₂, not just f₁ and f₂.
6. **Coherence + transfer function** (`scipy.signal.coherence`) — cross-spectral analysis between sensor pairs.
7. **HHT / EMD** (`PyEMD`) — non-linear non-stationary decomposition. Optional; may exceed chapter density.

**Granting SciPy + pywavelets + PyEMD in B7 only.** Pure-stdlib-only is a rule for B1-B6 because the math is simple enough to implement from scratch. B7's toolkit is *the point* of the chapter; reinventing Welch from numpy would be a distraction. Document this exception in the chapter's preamble.

### §2.4 Primary references — secured

- **Pál L. — *Theory of Linear Stochastic Reactor-Kinetic Equations***
- **Pázsit I., Pál L. — *Neutron Fluctuations: A Reference Manual***
- **Williams M.M.R. — *Random Processes in Nuclear Reactors***

All three are the standard reactor-noise references. All cite real Halden traces in appendices (useful cross-reference for whatever real dataset gets picked).

### §2.5 Sanitization audit — pre-author

Before opening the authoring session, re-confirm the public-safety surface:
- Real-dataset attribution + license is documented + correct
- No SUPIN / Bouracka / Improwave / MIM2000 / Yamyang / Vitez leaks
- No project-owner real-name beyond `Pete Y.`
- No private-monorepo paths leaking via dataset filenames

### §2.6 Figure budget — explicit grant for B7 (project-owner direction 2026-05-23)

The general Shad-tier convention (per `_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` §5.2) is **3 figures per band**: input + spectrum + takeaway. This convention exists because the underlying project doctrine is **formulas and data first, visualisations second** — the prose, equations, and reported numerical outputs (spectrum-bin tables, fit values, error figures) carry the load; plots are the human-readable cross-check, not the primary artefact.

**B7 is the explicit exception.** Project-owner direction (2026-05-23) locks the following figure-budget guidance into the B7 design contract:

- **Higher figure budget granted.** B7 may carry **8–14 figures** covering the spectral characteristics of the reactor fields. This is a 2-4× expansion over the standard 3-per-band cap, justified because:
  1. The chapter's pedagogical payoff IS reading dynamics off spectra — every additional spectral plot is content, not decoration.
  2. The "Fourier and beyond" toolkit (§2.3) is itself a sequence of spectral representations: bare DFT → Welch → STFT/spectrogram → wavelets → Rossi-α → Feynman-α → bispectrum → coherence. Each method earns its own figure as part of the toolkit walkthrough.
  3. The synthesised model (§2.2) cross-validates the real data; comparing real-vs-synth spectra side-by-side is part of the "the theory matches the data" reveal.
- **Doctrine reaffirmed for B0–B6.** The "formulas and data first" rule stays in force for B0 through B6. B7 is an exception, not a precedent.
- **Embedded vs. extra-file referenced — author's call.** B7 figures may live inline in the chapter (embedded in the primary document) OR as extra files referenced from the chapter (auxiliary appendix, separate figure-pack, supplementary panels). The choice depends on production constraints — chapter PDF length, figure resolution at publication scale, dual-publication targets per §6 below. Recommended default: inline the 4-6 most pedagogically central figures; defer the rest to an auxiliary `figures-supplementary-b7/` directory referenced from the chapter's "for further inspection" section.
- **Three classes of B7 figure, suggested ordering of authoring:**
  1. **Core diagnostic figures (must-have, inline):** raw time-series + bare-DFT spectrum showing Lorentzian + Lorentzian fit overlaid (4 figures minimum)
  2. **Toolkit-walkthrough figures (one per "beyond" method, inline or supplementary):** Welch PSD, spectrogram, wavelet scalogram, Rossi-α histogram, Feynman-α variance curve, bispectrum, coherence — one figure per method (6-8 figures, may be split between inline and supplementary)
  3. **Cross-publication figures (supplementary, designed for §6 reuse):** higher-resolution versions of the most striking spectral plots, sized + styled for web reading (zemla.org / mim2000.cz embedding) rather than for PDF print — see §6

---

## §3. Pedagogical arc — locked

```
─────────────────────────────────────────────────────────────────────
 §  STEP                                          PURPOSE
─────────────────────────────────────────────────────────────────────
 1  Open with real reactor-noise time-series      Establish credibility
                                                  Shad sees real data
─────────────────────────────────────────────────────────────────────
 2  Compute bare DFT power spectrum               First-tool diagnostic
                                                  Lorentzian shape visible
─────────────────────────────────────────────────────────────────────
 3  Introduce point-kinetics + Langevin           Explanation of step 2
    synthesised model                             Synth matches real
─────────────────────────────────────────────────────────────────────
 4  Extract prompt-neutron decay constant α       The headline payoff
    from PSD corner frequency                     "Read alpha off a plot"
─────────────────────────────────────────────────────────────────────
 5  Limit-test pure DFT — show a non-stationary  Motivate "and beyond"
    transient (scram or rod-step) where DFT
    misses the time structure
─────────────────────────────────────────────────────────────────────
 6  Toolkit walkthrough (§2.3 above)              The synthesis arc
    Welch → STFT → wavelets → Rossi-α →
    Feynman-α → bispectrum → coherence
─────────────────────────────────────────────────────────────────────
 7  Closing — "and beyond Fourier"                Hand off to literature
    Literature pointers (Pál, Pázsit, Williams)
    "This is where Shad graduates"
─────────────────────────────────────────────────────────────────────
```

---

## §4. Authoring session plan — two sessions

**Session 1 — Real-data + theory backbone** (4-6 hours):
- §2.1 dataset selection + fetch + format-conversion
- §2.2 synthesised model implementation
- Chapter §1-§4 (open with real → DFT → theory match → α extraction)
- **4 figures (revised 2026-05-23 per §2.6):** raw input + bare-DFT spectrum + Lorentzian fit overlaid + real-vs-synthesised side-by-side
- Tag at green: `v0.2.x-shad-b7-session1-real-and-theory`

**Session 2 — Toolkit walkthrough + closing** (4-5 hours):
- §2.3 toolkit implementation (six or seven methods)
- Chapter §5-§7 (limit-test → toolkit → closing)
- **6-10 figures (revised 2026-05-23 per §2.6):** one per toolkit method (Welch PSD, STFT/spectrogram, wavelet scalogram, Rossi-α histogram, Feynman-α variance curve, bispectrum, coherence) — author's call on inline vs. supplementary split
- Final chapter density target: 12-16 markdown pages (B7 is longest, expanded for figure embedding)
- Tag at green: `v0.2.x-shad-b7-shipped` (final tag)

**Optional Session 3 — Cross-publication figure pack** (1-2 hours, see §6):
- Re-render core spectral figures at web-publication sizing/styling for zemla.org + mim2000.cz reuse
- Document figure-license terms per CC-BY-SA-4.0 to enable site embedding
- Tag at green: `v0.2.x-shad-b7-figure-pack-web-ready`

---

## §5. After B7 — what closes the Shad-tier arc

When B7 ships, the seven-band Shad-tier journey is **complete**. The chapter index `docs/shad/README.md` becomes a coherent reading path from oscilloscope-to-reactor.

**Possible v0.3.0 release marker** for the full B1..B7 package. Earns its own RELEASE-NOTES file.

**Translations queue** — at that point, CS / JA / DE / IT translations of B1..B7 become the highest-leverage doc work. Volunteer-translation-friendly because Shad-tier chapters are short + standalone + non-controversial.

**Out-of-Shad-tier expansion candidates** (only if reader demand surfaces):
- B6.5 aperture-synthesis (2D imaging) as a sibling
- B0 "what is a signal" pre-amble for total beginners
- B8 medical imaging (MRI k-space reconstruction) — same 2D-DFT machinery as aperture synthesis
- B9 quantum spectroscopy (FID → spectrum)

None of these is committed; they're future-expansion candidates only.

---

## §6. Cross-publication scope — B7 spectral figures on zemla.org + mim2000.cz (project-owner direction 2026-05-23)

The expanded B7 figure set per §2.6 is **dual-purpose by design**: the same spectral plots that earn their place in the Shad guide chapter also serve as content for the 3-fold-path sites' science-facing sections. Lock this expectation into the B7 production plan so figures are sized, styled, and licensed for reuse rather than retrofitted later.

### §6.1 Target site sections

- **zemla.org → Philosophy/Science section** (under "Mind → Philosophy/Science: physics, mathematics, epistemology"). Natural home for the conceptual / pedagogical framing of reactor noise as a physics-via-spectra topic. Audience: science-curious readers from the broader zemla.org audience (philosophy, dharma, psychology). Expect long-form prose framing around each figure.
- **mim2000.cz → Teaching section.** Natural home for the technical walkthrough. Cross-links into the MI-M-T section once that lands in v1.18.0 stage-c (see `_config/CLAUDE-MD-DELTA-2026-05-09.md` and the 3FP stage-c sub-briefs). Audience: technical-professional readers from the mim2000.cz teaching/consulting funnel.

### §6.2 Figure production guidance for cross-publication

When authoring B7 figures with §6 reuse in mind:
- Render two output sizes per central figure: print (PDF, 600+ DPI, B5/A4 column-width) AND web (PNG, 1600-2000 px wide, retina-friendly without bloat)
- Use the same color palette across both — keep figures recognisable when a reader moves from PDF to web
- Keep axis labels and legends readable at small sizes — assume web reader on mobile (zemla.org + mim2000.cz are both multilingual mobile-responsive sites)
- Caption text should be self-contained — i.e. a web embed shows the figure + caption with no chapter context required
- Save the matplotlib rcParams / plot config alongside the figure so re-renders are byte-deterministic

### §6.3 Licensing

Figures inherit CC-BY-SA-4.0 from the doc tier (per repo `LICENSE-DOCS`). When embedded on zemla.org or mim2000.cz, the site post must carry the attribution string + link back to the source chapter in `lege-artis/fourier`. Attribution template:

> Figure: [title]. From "Just Shad's Guide to Fourier's Galaxy" chapter B7, lege-artis/fourier. CC-BY-SA-4.0. [link to GitHub source]

### §6.4 Authoring sequencing

The cross-publication figure-pack is a **Session 3 optional add-on** (see §4 above), explicitly NOT in the critical path for B7 ship. Sequence:
1. Sessions 1 + 2 produce the core + toolkit figures sized for PDF inline
2. After `v0.2.x-shad-b7-shipped` tags, Session 3 re-renders the central figures for web publication
3. 3FP stage-c (or later) authoring picks up the figure pack as content for zemla.org Philosophy/Science + mim2000.cz Teaching posts

This separation keeps B7 ship-quality intact and treats web-publication as a follow-on activity rather than a critical-path constraint. If Session 3 slips, B7 still ships; the web pieces can fire later in their own sessions.

### §6.5 Cross-references

- `_config/CLAUDE-MD-DELTA-2026-05-09.md` — mim2000 MI-M-T section v1.18.0 lock (planning context)
- 3FP stage-c sub-briefs in `3-fold-path/backlog/3FP-STAGE-C-*-BRIEF-v0.1.md` — where stage-c work picks up these figures
- `_config/SANITISATION-POLICY-v0.1.md` — public-mirror two-context rule; B7 figures must be sanitisation-clean for both lege-artis and 3FP-site embedding

End of SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md
