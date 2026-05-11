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
- 2 figures: input + bare-DFT spectrum
- Tag at green: `v0.2.x-shad-b7-session1-real-and-theory`

**Session 2 — Toolkit walkthrough + closing** (4-5 hours):
- §2.3 toolkit implementation (six or seven methods)
- Chapter §5-§7 (limit-test → toolkit → closing)
- 2-3 figures: time-frequency comparison, Rossi-α, Feynman-α
- Final chapter density target: 10-12 markdown pages (B7 is longest)
- Tag at green: `v0.2.x-shad-b7-shipped` (final tag)

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

End of SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md
