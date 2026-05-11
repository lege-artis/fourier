# JOB-1 — Shad-tier B4: Electronic systems

**Status:** Ready to execute. Depends on nothing except the published B1/B2/B3 chapters as exemplars.
**Estimated effort:** 2-3 hours (Opus-quality narrative + ~30 min figure-script work).
**Acceptance gate:** all checks in §9 pass.

---

## §1. Where B4 sits in the Shad-tier arc

The linear B1→B7 progression (per `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md`):

| Band | Chapter | What it adds to the reader's intuition |
|------|---------|----------------------------------------|
| B1 | Oscilloscope (shipped) | Single tone → single peak. The bedrock claim. |
| B2 | Audio / music (shipped) | Multiple tones → multiple peaks. Polyphony. |
| B3 | Vibration / accelerometer (shipped) | Harmonics + non-integer fault peaks. Diagnostic reading. |
| **B4** | **Electronic systems (this job)** | **Active circuits change the spectrum. Filters, oscillators, mixers — the spectrum-domain view of what each does.** |
| B5 | Radar (queued) | Doppler. Range-Doppler. Pulse compression. |
| B6 | Radioastronomy (queued) | Faint signals + integration time. Cosmic spectra. |
| B7 | Nuclear-reactor capstone (queued) | Beyond-Fourier toolkit (Welch PSD, Rossi-alpha, HHT/EMD). Closes the arc. |

**B4's specific contribution:** the reader leaves with a working intuition that a circuit's behaviour can be *predicted* from its frequency response, and that the spectrum view is the primary tool for designing/diagnosing analog electronics. This is the chapter where Fourier crosses over from "describing signals" to "describing systems."

---

## §2. Required scope (what MUST be covered)

Three sub-topics, in narrative order:

1. **AC mains spectrum — what's "clean" 50/60 Hz actually look like?**
   - The mains line has harmonics from non-linear loads (rectifiers, switching power supplies, dimmers).
   - 3rd, 5th, 7th, 9th odd harmonics dominate in single-phase loads; 5th, 7th, 11th, 13th in three-phase.
   - Total Harmonic Distortion (THD) is the standard metric: `THD = sqrt(sum(V_h^2 for h>=2)) / V_1`.
   - Why this matters: power-quality monitoring, EMC compliance, motor heating, transformer derating.

2. **Active filter — the spectrum-domain view of "high-pass / low-pass / band-pass"**
   - A 2nd-order Sallen-Key low-pass filter has a well-defined |H(f)|² that suppresses content above cutoff at -40 dB/decade.
   - Show the spectrum BEFORE filtering (broadband signal: tones + noise) and AFTER filtering (same signal after the filter response is applied).
   - The reader leaves understanding that a filter is a multiplier in the frequency domain.

3. **Mixer / heterodyne — spectrum-shifting**
   - Multiplying two signals in time = convolution in frequency = spectrum-shifting (sum + difference frequencies).
   - Show RF signal + LO signal → IF spectrum.
   - Why this matters: superheterodyne radios, software-defined radio (SDR), every radio receiver since 1918.

**Hard rule:** sub-topics 1-2-3 in this order. They build: passive observation → active filtering → active mixing. The reader's mental model accretes layer by layer.

---

## §3. Optional scope (include if natural; skip if it dilutes)

- **Crystal-oscillator phase noise** — closely related to mixer (LO purity matters), but veers into the noise-floor / Allan-variance territory which fits better in B6 Radioastronomy. **Recommendation:** skip; mention as a one-line bridge to B5/B6.
- **Class-D audio amplifier switching artifacts** — relevant but adds complexity. **Recommendation:** skip; B2 already touched harmonic content.
- **EMC pre-compliance scan** — relevant industrial application of #1. **Recommendation:** include as a one-paragraph "and this is what compliance engineers do for a living" connector at the end of §1.

---

## §4. Pattern exemplars — mirror these

Open `docs/shad/03-vibration.md` and `examples/shad/b3-vibration/main.py` and study their structure. **Mirror them.** Specifically:

**Chapter narrative structure** (from B3 — same pattern for B4):
1. `# B4 — Electronic systems` heading
2. `## The premise` — one-paragraph hook: what makes B4 different from B3
3. `## The setup` — describe the synthesized signal in a table (frequencies, amplitudes, physical interpretation)
4. `## The input` — show `fig-b4-input.png` + 1-2 paragraph time-domain description
5. `## The transform — <method>` — show the spectrum + describe the method (windowing choice, sample rate, frequency resolution)
6. `## The takeaway — what an electronics engineer sees` — annotated spectrum, diagnostic reading, professional context
7. `## What we just did` — short closing paragraph + bridge to B5

**Density target:** ~150-220 lines of Markdown (B3 is 154 lines; B4 has three sub-topics so it'll run slightly longer, target ~200-250 lines).

**Voice:** engineer talking to engineer. Pragmatic, not academic. Use specific numbers (frequencies in Hz, amplitudes as ratios, dB values). Match the B3 voice — re-read it before authoring.

**Figure convention** — three figures, exactly:
- `fig-b4-input.png` — time-domain snapshot (200 ms or whatever's most readable for the chosen example signal)
- `fig-b4-spectrum.png` — bare spectrum (linear or log-magnitude, your judgment)
- `fig-b4-takeaway.png` — same spectrum but **annotated**: peaks labelled with their physical meaning, filter cutoffs marked, mixer output bands highlighted

---

## §5. Implementation script — `examples/shad/b4-electronic/main.py`

Mirror `examples/shad/b3-vibration/main.py`:

- **License header:** `#!/usr/bin/env python3` + `# SPDX-License-Identifier: Apache-2.0`
- **Docstring:** describe what the script synthesizes, why, output filenames
- **Imports:** stdlib + NumPy + Matplotlib only. No SciPy, no pandas. Keep dependencies thin — anyone with `pip install numpy matplotlib` should be able to run it.
- **Figure outputs:** save as PNG to the script's directory? **No** — save to `../../../docs/shad/figures/fig-b4-*.png` (the chapter Markdown references that path). Use `Path(__file__).resolve().parent / "../../../docs/shad/figures"` to construct.
- **Reproducibility:** seed the RNG (`np.random.seed(20260511)` or similar). Hard requirement — figures must be byte-reproducible on re-runs for CI sanity.
- **No FFTW, no scipy.signal.** Use `np.fft.fft`, `np.hanning`, etc. Keep it bare.

For the **active filter** sub-topic, you'll need a 2nd-order low-pass filter response. Implement it analytically — don't use `scipy.signal.lfilter`. The transfer function for Sallen-Key 2nd-order LP:

```
H(f) = 1 / (1 + j*(f/f_c)/Q - (f/f_c)^2)
```

Apply by multiplication in the frequency domain (`spec_filtered = spec * H(f)`).

For the **mixer**, just multiply two time-domain signals (`rf * lo`).

For the **AC mains harmonics**, synthesize as `sum(A_h * sin(2*pi*h*50*t) for h in [1, 3, 5, 7, 9])` with realistic amplitudes (THD ~5% is typical for residential mains).

---

## §6. Citations — what must appear in `refs.bib`

Append to `shared/reference-bibliography/refs.bib`. Each entry must be real, reachable, and authoritative.

**Required (3 citations minimum):**

1. **Sedra & Smith — *Microelectronic Circuits*** (any recent edition, 7th or 8th). The standard analog circuits textbook. Cite for the Sallen-Key topology + the active-filter transfer-function derivation. ISBN-verifiable.

2. **Razavi — *RF Microelectronics*** (2nd ed, 2011 or later). The standard RF / mixer reference. Cite for the heterodyne / mixer math. ISBN-verifiable.

3. **IEEE 519-2022 — *IEEE Standard for Harmonic Control in Electric Power Systems*** (or its current revision). Cite for THD definition + acceptable harmonic content thresholds. IEEE-Xplore URL or DOI.

**Optional (include if you cite specifically):**
- Numerical Recipes 3rd ed (already in refs.bib) — cite for the windowing maths if you discuss window choice in detail
- Oppenheim & Schafer — *Discrete-Time Signal Processing* (already in refs.bib) — cite for the multiplication-in-time = convolution-in-frequency identity if you discuss the mixer in detail

Citation style: BibTeX format, ASCII-only keys (`sedra-smith-microelectronic-circuits-8e-2014`, not unicode), one entry per real published source.

---

## §7. Sanitization (re-stated for emphasis)

Before committing, grep:

```bash
cd fourier/
grep -rni -E "supin|bouracka|cap[ck]p|mimt|mim2000|improwave|yamyang|vitez" \
  --include="*.md" --include="*.py" docs/shad/ examples/shad/
# Expected: zero hits
```

Real names in citations are fine (`Sedra`, `Razavi`, `Vetterling`). Personal info about Pete is not.

---

## §8. Done criteria

- [ ] `docs/shad/04-electronic.md` exists, ~200-250 lines, mirrors B3 structure
- [ ] `examples/shad/b4-electronic/main.py` exists, runs end-to-end, produces 3 figures
- [ ] `docs/shad/figures/fig-b4-{input,spectrum,takeaway}.png` exist + are referenced from `04-electronic.md`
- [ ] `shared/reference-bibliography/refs.bib` has 3+ new entries for B4 sources
- [ ] `docs/shad/README.md` updated to mention B4 (add to the chapter index)
- [ ] Pre-flight sanitization grep clean
- [ ] Commit message: `feat(shad): B4 Electronic systems chapter + figures (AC mains harmonics + active filter + heterodyne mixer)`

---

## §9. Acceptance — what "good looks like"

A reader who has read B1+B2+B3 should, after B4:
- Understand that a circuit's frequency response is a *multiplication* in the spectrum domain
- Be able to look at a power-quality spectrum and identify which harmonics indicate which kind of load
- Understand why a mixer produces sum and difference frequencies, and what that buys you in a radio
- See B5 Radar coming and intuit why Doppler is the natural next step

If after reading B4 the reader still thinks "spectrum analyser shows what frequencies are in a signal" without the active-system view, B4 has failed. The whole point of B4 is the *system* view.

End of JOB-1-SHAD-B4-ELECTRONIC.md
