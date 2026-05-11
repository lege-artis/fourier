# Sonnet handoff — Shad-tier B6: Radioastronomy (pulsar-timing lead)

**Status:** Ready to execute. Best authored after B5 lands (the "1D time-series spectral analysis before generalising to 2D" arc benefits from radar groundwork). Independent of B7.
**Estimated effort:** 1 Sonnet session (~3-4 hours authoring + figures). Possibly 2 if depth wanted.
**Acceptance gate:** all checks in §9 pass.

---

## §0. Read these first (in order)

1. `_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` — your scope context (§4 has B6 line + cross-band coherence rules in §5).
2. `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — the "why a fourth doc tier" framing + Shad-as-audience-proxy + iconography.
3. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy + three doc tiers.
4. `docs/shad/03-vibration.md` — your authoring exemplar. Mirror its structure, density, voice.
5. `examples/shad/b3-vibration/main.py` — your script exemplar.
6. `docs/shad/05-radar.md` + `examples/shad/b5-radar/main.py` (if B5 has already landed) — the closest sibling chapter; B6 is the radioastronomy equivalent of B5's measurement-physics angle, applied to signals from nature.
7. `_handoffs/shad-b5-radar/SONNET-BRIEF.md` — structural pattern reference (B5 brief structure matches B6 expected structure).

---

## §1. Where B6 sits in the Shad-tier arc

The reader leaving B5 (Radar) understands that the DFT can *recover physical quantities* (range from delay, velocity from Doppler shift). **B6's specific contribution:** the same algorithm applied to signals *from nature itself* — not bounced echoes, but emissions from cosmological sources — and at scales >10⁹ × the audio domain, with signals buried 20+ dB below noise. The reader leaves understanding that the DFT is the canonical detection tool across observational astrophysics.

This is the chapter where Fourier crosses from "engineered measurement" to "discovery of natural phenomena."

---

## §2. Required scope (what MUST be covered)

Three sub-topics, in narrative order:

1. **A pulsar's lighthouse beam → harmonic-summed power spectrum**
   - Pulsars are rotating neutron stars emitting a beamed radio signal. The detected signal is approximately periodic: brief pulse every rotation period P_rotation (typical P ≈ 1.5 ms for millisecond pulsars; 1 s for classical pulsars).
   - The pulse profile is narrow but the *period* is exact (timekeeping accuracy comparable to atomic clocks).
   - The DFT of a long time-series reveals the rotation fundamental + many harmonics (pulse profiles are not pure sines — they have content at f₀, 2f₀, 3f₀, ...).
   - **Harmonic summing:** if the fundamental is buried in noise but consistent across many harmonics, sum the power at f, 2f, 3f, ..., kf. Signal accumulates linearly; noise as √k. The detection significance grows.
   - Reader takeaway: harmonic summing = a coherent-detection trick using DFT structure that the bare DFT alone doesn't expose.

2. **Coherent dedispersion — the interstellar medium delays low frequencies**
   - The interstellar medium is a cold plasma. Radio waves passing through it experience a frequency-dependent delay: low-frequency components arrive later than high-frequency.
   - For a pulsar at distance D, the dispersive delay across an observing band is t_DM = 4.15 × DM × (1/f_lo² - 1/f_hi²) ms, where DM is the *dispersion measure* (pc/cm³).
   - A naive DFT of dispersed pulsar data smears the pulse: you see a broadband whoosh, not sharp peaks.
   - **Coherent dedispersion** = applying a frequency-domain phase rotation (per the known DM) to cancel the dispersion before computing the spectrum.
   - Reader takeaway: the DFT lets you *invert physical propagation effects* analytically — phase-correct in the frequency domain, then transform back.

3. **The detection — find a new pulsar in a synthetic survey**
   - Construct a synthesised 60-second observation containing: white noise + one buried pulsar signal (period 1.558 ms, DM 71 pc/cm³ — these are realistic for PSR B1937+21).
   - Show the steps: raw spectrum (no signal visible) → after coherent dedispersion (still buried) → after harmonic summing (peak emerges at the rotation frequency, 16-σ detection significance).
   - Reader takeaway: this is the actual pipeline pulsar-survey teams have used for 50+ years — coherent dedispersion + harmonic summing + threshold. Same DFT, layered processing.

**Hard rule:** sub-topics 1-2-3 in this order. They build: ideal pulsar → real interstellar-medium effects → end-to-end detection.

---

## §3. Optional scope (include only if natural; skip if it dilutes)

- **Pulsar timing arrays for gravitational-wave detection (NANOGrav)** — millisecond-pulsar timing residuals correlated across many pulsars reveals the low-frequency GW background. **Recommendation:** mention as a one-paragraph closer to §3 sub-topic — "this same processing scales up to nanoHertz-frequency GW astronomy" — but don't author full sub-topic.
- **Fast Radio Bursts (FRBs)** — millisecond extragalactic bursts detected by the same dedispersion machinery. **Recommendation:** mention as a sentence in §3 sub-topic — "modern FRB pipelines apply the same dedispersion at survey scale."
- **2D aperture-synthesis imaging (VLA / ALMA / ngVLA)** — visibility-to-brightness 2D Fourier inversion. **Recommendation:** SKIP authoring. Reserve for a separate possible B6.5 chapter or sibling imaging doc. Mention only in the §"What we just did" closer: "this generalises to 2D imaging when many radio dishes are correlated — aperture synthesis — same DFT, two-dimensional."
- **Hilbert-Huang / wavelet for transient pulsar searches** — would step on B7's territory. **Recommendation:** skip.
- **Coherent vs incoherent dedispersion engineering tradeoff** — relevant but technical. **Recommendation:** one-paragraph aside; don't implement both.

---

## §4. Pattern exemplars — mirror these

**Chapter narrative structure** (same as B3/B5):

1. `# B6 — Radioastronomy` heading
2. `## The premise` — one-paragraph hook: what makes radioastronomy different from radar (signals from nature, not bounced)
3. `## The setup` — describe the synthesised pulsar in a table (rotation period, dispersion measure, observation bandwidth, sample rate, integration time, target SNR per pulse)
4. `## The input` — show `fig-b6-input.png` — raw time-series + bare spectrum showing no obvious peak
5. `## The transform — coherent dedispersion then harmonic summing` — show the math + reveal the spectrum + describe the layered processing
6. `## The takeaway — what a pulsar astronomer sees` — annotated harmonic-summed spectrum; identifying the fundamental + harmonics + side-lobes; professional context (pulsar surveys, FRB detection, pulsar timing arrays)
7. `## What we just did` — short closing paragraph + bridge to B7 (reactor noise — same DFT, but now the *system itself* is the source, not a signal in a system)

**Density target:** ~200-260 lines of Markdown. B6 has the same three-sub-topic layered structure as B5.

**Voice:** engineer-meets-astronomer. Pragmatic but with a sense of scale and wonder where appropriate. Specific numbers (rotation periods in ms, DM in pc/cm³, observation frequencies in MHz/GHz, detection significance in σ). Match the B3 voice.

**Figure convention** — three figures, exactly:
- `fig-b6-input.png` — top panel: raw time-series (looks like noise); bottom panel: bare spectrum (no peak visible above baseline)
- `fig-b6-spectrum.png` — power spectrum AFTER coherent dedispersion + harmonic summing; fundamental + 8-10 harmonics labelled
- `fig-b6-takeaway.png` — annotated version of the harmonic-summed spectrum with: fundamental at 1/P, harmonics labelled, detection threshold marked, signal-to-noise ratio quoted in dB and σ

---

## §5. Implementation script — `examples/shad/b6-radioastronomy/main.py`

Mirror `examples/shad/b3-vibration/main.py`:

- **License header:** `#!/usr/bin/env python3` + `# SPDX-License-Identifier: Apache-2.0`
- **Docstring:** describe what the script synthesises + the pulsar parameters
- **Imports:** stdlib + NumPy + Matplotlib only. **No SciPy / astropy.** Implement everything from scratch via `np.fft`.
- **Figure outputs:** save as PNG to `../../../docs/shad/figures/fig-b6-*.png`
- **Reproducibility:** seed RNG (`np.random.seed(20260513)` or similar).

**Concrete numerical parameters** (realistic for PSR B1937+21):
- Rotation period P = 1.5578064 ms (the canonical first-discovered millisecond pulsar)
- Pulse duty cycle = 5% (pulse is sharp; ON for 5% of period)
- Dispersion measure DM = 71.0 pc/cm³
- Observation centre frequency f_c = 1400 MHz (L-band, classic pulsar-survey band)
- Observation bandwidth B = 100 MHz
- Sample rate (after channelisation) = 1 MHz (or full B = 100 MHz, your call — adjust DFT size accordingly)
- Integration time T = 60 s
- Per-sample SNR = -25 dB (signal way below noise per sample; only emerges after coherent integration)

**Coherent-dedispersion math anchor:**
```
The dispersion-induced phase rotation in the frequency domain is:
    Phi(f) = -2*pi * 4.15e3 * DM * f**2 / (f**2 + f_c**2) / f_c**3 * <units factor>
Multiply your channelised data X(f) by exp(-j*Phi(f)) to cancel dispersion.
```

(Verify the exact phase formula against Lorimer & Kramer §5.2.1 before implementing; the formula above is sketched but units matter — pc/cm³, MHz, ms, etc.)

**Harmonic-summing sketch:**
```python
# After coherent dedispersion: dedispersed time-series, sample at high rate
power_spectrum = np.abs(np.fft.rfft(dedispersed))**2
freqs = np.fft.rfftfreq(len(dedispersed), d=1.0/fs)

# For each candidate fundamental f0 in a frequency search range:
#   sum power at f0, 2*f0, 3*f0, ..., k_max*f0
# Peak of this summed series gives the pulsar fundamental.
k_max = 16
summed = np.zeros(len(freqs)//k_max)
for k in range(1, k_max + 1):
    summed[:len(summed)] += power_spectrum[k*np.arange(len(summed))]
# Find peak; convert bin to frequency; report 1/freq = period
```

---

## §6. Citations — what must appear in `refs.bib`

Append to `shared/reference-bibliography/refs.bib`. **Required (3+ citations):**

1. **Lorimer & Kramer — *Handbook of Pulsar Astronomy*** (2nd ed., 2012 or later, Cambridge University Press). Cite for harmonic summing + coherent dedispersion + pulse-detection statistics. ISBN-verifiable. BibTeX key: `lorimer-kramer-pulsar-handbook-2e-2012` (ASCII-only).

2. **PSR B1937+21 discovery paper — Backer et al. (1982)** *Nature*. The discovery of the first millisecond pulsar; canonical reference for the rotation-period + DM parameters used in the example. DOI-verifiable.

3. **NANOGrav 15-year data release paper** (Agazie et al. 2023, *ApJL*). Cite for the pulsar timing array → gravitational-wave detection arc; lets the chapter close-bridge to current cutting-edge astrophysics. ArXiv-verifiable.

**Optional (include only if cited specifically):**
- Hewish et al. (1968) — original pulsar discovery
- Manchester et al. — *ATNF Pulsar Catalogue* (the cosmic phone book)
- Numerical Recipes 3rd ed (already in refs.bib) — for the harmonic-summing algorithmic anchor

---

## §7. Sanitization (re-stated for emphasis)

Before committing, grep:

```bash
cd fourier/
grep -rni -E "supin|bouracka|cap[ck]p|mimt|mim2000|improwave|yamyang|vitez" \
  --include="*.md" --include="*.py" docs/shad/ examples/shad/
# Expected: zero hits
```

Real names in citations are fine (Lorimer, Kramer, Backer, Hewish). Personal info about Pete is not.

---

## §8. Done criteria

- [ ] `docs/shad/06-radioastronomy.md` exists, ~200-260 lines, mirrors B3/B5 structure
- [ ] `examples/shad/b6-radioastronomy/main.py` exists, runs end-to-end, produces 3 figures
- [ ] `docs/shad/figures/fig-b6-{input,spectrum,takeaway}.png` exist + are referenced from `06-radioastronomy.md`
- [ ] `shared/reference-bibliography/refs.bib` has 3+ new entries for B6 sources
- [ ] `docs/shad/README.md` updated to mention B6 (add to the chapter index)
- [ ] `examples/shad/README.md` updated with B6 entry
- [ ] Pre-flight sanitization grep clean
- [ ] Commit message: `feat(shad): B6 Radioastronomy chapter + figures (millisecond-pulsar coherent dedispersion + harmonic summing)`
- [ ] Tag at green: `git tag v0.2.x-shad-b6-shipped`

---

## §9. Acceptance — what "good looks like"

A reader who has read B1+B2+B3+B4+B5 should, after B6:

- Understand that the same DFT detects natural signals buried 20+ dB below noise via coherent processing layers (dedispersion + harmonic summing)
- Be able to read a harmonic-summed power spectrum and identify the fundamental + harmonics
- Understand why coherent dedispersion is *exact* (it inverts a known physical effect analytically) while incoherent dedispersion is approximate (it just delays binned channels) — and why coherent is preferred for narrow pulses
- See B7 coming and intuit that real reactor signals get even MORE buried in noise + system-dynamics, and the toolkit needs to expand beyond pure DFT

If after reading B6 the reader still thinks "pulsars = beep beep from space" without the spectral-detection view, B6 has failed.

---

## §10. Status report convention

At park-time or end-of-session, write `_handoffs/shad-b6-radioastronomy/STATUS-REPORT-FILLED.md` covering:

- What landed (chapter, script, figures, refs.bib entries)
- Any deviations from this brief (and why)
- Numbers that matter (line counts, figure sizes, detection-significance in σ, citation list)
- Decisions deferred to Pete
- Open blockers if any
- Time accounting (estimated vs briefed)

Pete reads this on next ThinkPad session + decides whether to subtree-push to public.

End of B6 SONNET-BRIEF.md
