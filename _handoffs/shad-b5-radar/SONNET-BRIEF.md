# Sonnet handoff — Shad-tier B5: Radar (NEXRAD lead)

**Status:** Ready to execute. Independent session; no prior dependency beyond shipped B1+B2+B3.
**Estimated effort:** 1 Sonnet session (~3-4 hours authoring + figures).
**Acceptance gate:** all checks in §9 pass.

---

## §0. Read these first (in order)

1. `_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` — your scope context (§4 has B5 line + cross-band coherence rules in §5).
2. `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — the "why a fourth doc tier" framing + Shad-as-audience-proxy + iconography conventions.
3. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy + three doc tiers + Stage 5 gating.
4. `docs/shad/03-vibration.md` — your authoring exemplar (B3, latest shipped Shad chapter). **Mirror its structure, density, voice exactly.**
5. `examples/shad/b3-vibration/main.py` — your script exemplar (B3). Mirror imports, docstring, figure-saving convention, reproducibility seed.
6. `_handoffs/macbook-v0.2.x-weekend/JOB-1-SHAD-B4-ELECTRONIC.md` — B4 brief in the same family; read for structure pattern, especially §2 (Required scope) and §4 (Pattern exemplars).

---

## §1. Where B5 sits in the Shad-tier arc

The reader leaving B4 (Electronic) understands that a circuit's behaviour shapes the spectrum — that the spectrum can *describe systems*, not just signals. **B5's specific contribution:** the spectrum becomes a *measurement* — range from delay, velocity from Doppler shift, both extracted simultaneously via matched filtering and the same DFT machinery. The reader leaves understanding that the DFT recovers physical quantities directly.

This is the chapter where Fourier crosses over from "characterising signals" to "doing measurement physics."

---

## §2. Required scope (what MUST be covered)

Three sub-topics, in narrative order. They build progressively:

1. **A single radar pulse → matched-filter compression**
   - Transmit a short pulse with linear-FM (chirp) modulation at carrier frequency f_c.
   - Receive a delayed echo from a static target at range R; round-trip delay τ = 2R/c.
   - Cross-correlate received echo with the known transmit waveform = matched filter = "pulse compression."
   - Peak of correlation gives target range. Show that the DFT of the cross-correlation reveals the range cleanly even when the raw echo is buried in noise.
   - Reader takeaway: matched filtering = correlation = inverse FFT of (X·conj(X_ref)) in the frequency domain. Same DFT, used for extraction not description.

2. **A moving target → Doppler shift**
   - Same setup, but target now has radial velocity v_r toward the radar.
   - The returned signal has a frequency shift Δf = 2 v_r f_c / c (Doppler effect).
   - Show the spectrum of the received pulse-train (multiple pulses, pulse-repetition-frequency PRF) — the Doppler shift appears as a frequency offset in the spectrum.
   - For a typical NEXRAD case: PRF ≈ 1000 Hz, f_c = 2.7-3 GHz (S-band), wind targets at radial velocities ±50 m/s → Δf ≈ ±900 Hz (in the unambiguous range, since PRF/2 = 500 Hz allows ± half-PRF Doppler bins via folding mitigation).
   - Reader takeaway: Doppler measurement = a DFT across the pulse-train direction.

3. **NEXRAD lead — range-Doppler matrix from a real(istic) volume scan**
   - Construct a 2D matrix: rows = range bins (fast-time samples within one pulse), columns = Doppler bins (slow-time samples across pulse train).
   - Apply 1D DFT down each column = Doppler dimension; apply 1D DFT across each row = range dimension.
   - Result is the **range-Doppler map**: a 2D image where each cell shows (range, radial velocity, reflectivity).
   - Use a synthesised volume that mimics a NEXRAD precipitation scan: multiple targets at different ranges + a wind-gradient producing distributed Doppler shifts.
   - Reader takeaway: this is **how a weather radar produces wind-velocity maps in real time** — by computing 2D DFTs of pulse-train returns.

**Hard rule:** sub-topics 1-2-3 in this order. Each layer adds one dimension: single pulse → pulse train → 2D matrix.

---

## §3. Optional scope (include only if natural; skip if it dilutes)

- **Pulse-repetition-frequency ambiguity** — at high PRF, Doppler unambiguous but range ambiguous (can't tell which pulse the echo came from); at low PRF, range unambiguous but Doppler folds. The classic engineering trade-off. **Recommendation:** include as a one-paragraph note at end of §3 sub-topic.
- **Range-side-lobe suppression via tapering** — applying a Hamming/Hann window before the matched filter reduces range side-lobes but broadens the main peak. Mirrors B2 windowing. **Recommendation:** mention only; do not implement.
- **Clutter rejection via MTI (moving-target indicator) filtering** — stationary clutter has zero Doppler, moving targets non-zero; a high-pass filter on the Doppler dimension removes ground clutter. **Recommendation:** skip; B7 will revisit clutter-vs-signal discrimination via PSD methods.
- **Synthetic Aperture Radar (SAR)** — would require introducing aperture synthesis (range-Doppler → 2D image via the cross-track FFT). **Recommendation:** SKIP entirely. SAR is a chapter of its own; mention at end of B5 only as "this generalises to 2D imaging in SAR."

---

## §4. Pattern exemplars — mirror these

**Chapter narrative structure** (from B3 — same pattern for B5):

1. `# B5 — Radar` heading
2. `## The premise` — one-paragraph hook: what makes radar's use of Fourier different from B4's electronics
3. `## The setup` — describe the synthesised pulse + target geometry in a table (carrier frequency, pulse duration, PRF, target range/velocity/RCS)
4. `## The input` — show `fig-b5-input.png` — time-domain trace of a single pulse + its received echo with noise; 2-3 paragraph description
5. `## The transform — matched-filter compression then Doppler` — show the math + the spectrum + describe the method
6. `## The takeaway — what a radar engineer sees` — annotated range-Doppler map; reading peaks as (range, velocity, reflectivity) tuples; professional context (storm cells, wind shear detection)
7. `## What we just did` — short closing paragraph + bridge to B6 (radioastronomy — same maths, signals from nature instead of bounced echoes)

**Density target:** ~200-260 lines of Markdown (B3 is 154; B5 has three sub-topics with progressive layering so it'll run slightly longer).

**Voice:** engineer talking to engineer. Pragmatic, not academic. Specific numbers (carrier frequency in GHz, PRF in Hz, target velocities in m/s, range in km). Match the B3 voice — re-read it before authoring.

**Figure convention** — three figures, exactly:
- `fig-b5-input.png` — time-domain: one transmit pulse + the noisy received echo; show the time delay clearly
- `fig-b5-spectrum.png` — bare 2D range-Doppler map (heatmap); axes = range (km) × radial velocity (m/s)
- `fig-b5-takeaway.png` — same range-Doppler map but **annotated**: multiple targets labelled, wind-gradient region highlighted, range-Doppler ambiguity zone marked

---

## §5. Implementation script — `examples/shad/b5-radar/main.py`

Mirror `examples/shad/b3-vibration/main.py`:

- **License header:** `#!/usr/bin/env python3` + `# SPDX-License-Identifier: Apache-2.0`
- **Docstring:** describe what the script synthesises, why, output filenames
- **Imports:** stdlib + NumPy + Matplotlib only. **No SciPy.** Implement matched filtering manually via `np.fft` (multiply in frequency domain, inverse-FFT).
- **Figure outputs:** save as PNG to `../../../docs/shad/figures/fig-b5-*.png`
- **Reproducibility:** seed RNG (`np.random.seed(20260512)` or similar). Hard requirement.

**Concrete numerical parameters** (target a realistic NEXRAD-style setup):
- Carrier frequency f_c = 2.8 GHz (S-band)
- Pulse duration τ_pulse = 1.6 µs (typical NEXRAD long-pulse mode)
- Pulse repetition frequency PRF = 1000 Hz (giving unambiguous range ≈ 150 km)
- Number of pulses per coherent processing interval = 64
- Sample rate within a pulse = 2 MHz (Nyquist for the chirp bandwidth)
- Targets: place 3 distinct returns
  - T1: range 30 km, radial velocity +20 m/s, RCS 1.0 (a precipitation cell moving toward radar)
  - T2: range 65 km, radial velocity 0 m/s, RCS 0.5 (a stationary target — ground clutter analogue)
  - T3: range 110 km, radial velocity -35 m/s, RCS 0.7 (precipitation cell receding)
- Noise: white Gaussian, SNR ≈ 0 dB on the raw single-pulse echo, ≈ 20 dB after pulse compression × pulse-train integration (this is the *gain* the reader will see)

**Matched filter implementation sketch:**
```python
# Transmit waveform = linear-FM chirp
t = np.arange(0, n_samples_pulse) / fs
chirp_rate = bandwidth / pulse_duration
tx = np.exp(2j * np.pi * (0.5 * chirp_rate * t**2))

# Received echo (for one pulse) = delayed + Doppler-shifted + noise
rx = ...  # synthesise per §2

# Matched-filter compression = correlate, equivalently:
TX = np.fft.fft(tx, n=N_fft)
RX = np.fft.fft(rx, n=N_fft)
compressed = np.fft.ifft(RX * np.conj(TX))   # range profile for this pulse
```

For the 2D range-Doppler map: stack `compressed` for each of 64 pulses → 2D matrix → DFT along the slow-time (pulse-train) axis → range-Doppler map.

---

## §6. Citations — what must appear in `refs.bib`

Append to `shared/reference-bibliography/refs.bib`. **Required (3+ citations):**

1. **Skolnik — *Radar Handbook*** (3rd ed., 2008, McGraw-Hill). Cite for matched-filter pulse-compression theory + range-Doppler processing. ISBN-verifiable. BibTeX key: `skolnik-radar-handbook-3e-2008` (ASCII-only).

2. **Richards — *Principles of Modern Radar: Basic Principles*** (2010 or later, SciTech). Cite for the range-Doppler matrix construction + clutter / target separation. ISBN-verifiable.

3. **NOAA NEXRAD Level-II documentation** — Federal Meteorological Handbook FMH-11 Part C (NWS Radar Operations Center). Cite for the NEXRAD parameter set + scan strategies + Doppler signal processing standards. NOAA public-domain. URL-verifiable via NWS website.

**Optional (include only if cited specifically):**
- Doviak & Zrnić *Doppler Radar and Weather Observations* — for the meteorological-applications context
- Numerical Recipes 3rd ed (already in refs.bib) — for the FFT-correlation algorithmic anchor

---

## §7. Sanitization (re-stated for emphasis)

Before committing, grep:

```bash
cd fourier/
grep -rni -E "supin|bouracka|cap[ck]p|mimt|mim2000|improwave|yamyang|vitez" \
  --include="*.md" --include="*.py" docs/shad/ examples/shad/
# Expected: zero hits
```

Real names in citations are fine (Skolnik, Richards, Doviak). Personal info about Pete is not.

---

## §8. Done criteria

- [ ] `docs/shad/05-radar.md` exists, ~200-260 lines, mirrors B3 structure
- [ ] `examples/shad/b5-radar/main.py` exists, runs end-to-end, produces 3 figures
- [ ] `docs/shad/figures/fig-b5-{input,spectrum,takeaway}.png` exist + are referenced from `05-radar.md`
- [ ] `shared/reference-bibliography/refs.bib` has 3+ new entries for B5 sources
- [ ] `docs/shad/README.md` updated to mention B5 (add to the chapter index)
- [ ] `examples/shad/README.md` updated with B5 entry
- [ ] Pre-flight sanitization grep clean
- [ ] Commit message: `feat(shad): B5 Radar chapter + figures (NEXRAD-style matched-filter compression + range-Doppler matrix)`
- [ ] Tag at green: `git tag v0.2.x-shad-b5-shipped`

---

## §9. Acceptance — what "good looks like"

A reader who has read B1+B2+B3+B4 should, after B5:

- Understand that the DFT can *recover physical quantities* (range from delay, velocity from Doppler shift), not just describe signal content
- Be able to read a range-Doppler map and identify (range, radial velocity, reflectivity) for each target
- Understand why a matched filter is "the optimal detector for a known signal in white Gaussian noise" without needing the formal proof
- See B6 coming and intuit that the same processing applies to signals *from nature* (pulsars), not just bounced echoes

If after reading B5 the reader still thinks "radar = beep beep beep" without the spectral-measurement view, B5 has failed.

---

## §10. Status report convention

At park-time or end-of-session, write `_handoffs/shad-b5-radar/STATUS-REPORT-FILLED.md` covering:

- What landed (chapter, script, figures, refs.bib entries)
- Any deviations from this brief (and why)
- Numbers that matter (line counts, figure sizes, citation list)
- Decisions deferred to Pete (any judgement calls you flagged)
- Open blockers if any (per the same "30-min rule" — park cleanly rather than grinding)
- Time accounting (estimated vs briefed)

Pete reads this on next ThinkPad session + decides whether to subtree-push to public.

End of B5 SONNET-BRIEF.md
