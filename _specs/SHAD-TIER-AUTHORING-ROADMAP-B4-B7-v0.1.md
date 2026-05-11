# Shad-tier authoring roadmap — bands B4..B7

**Status:** scope locked, datasets pre-selected, sequencing approved
**Date:** 2026-05-11
**License:** CC-BY-SA-4.0 (this is a docs roadmap)
**Authoring owner:** Pete Y. (project owner); Sonnet sessions for B4-B6 execution; B7 capstone reserved for Opus authoring

> Companion to `PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` (the "why a fourth doc tier" framing). This file plans WHAT lands per band + WHO authors + WHEN.

---

## §1. The four queued bands at a glance

| Band | Title | Pedagogical add | Toolkit add | Authoring owner | Sessions |
|------|-------|-----------------|-------------|-----------------|----------|
| **B4** | Electronic systems | Power electronics + RF + mixed-signal; same maths, different domain | + intermodulation, RF context | Sonnet | 1 |
| **B5** | Radar | Pulse-Doppler returns; range-velocity cross-correlation | + matched filter, Doppler bins | Sonnet | 1 |
| **B6** | Radioastronomy | Radio interferometry + pulsar timing; same maths, bigger scale | + visibility data, dynamic range | Sonnet | 1 (possibly 2 if depth wanted) |
| **B7** | **Nuclear reactor — CAPSTONE** | Spectral analysis as window into dynamic stability — *"Fourier and beyond"* | + Welch PSD, wavelets, Rossi-alpha, Feynman-alpha, higher-order spectra, HHT/EMD | **Opus** | 2 |

**Total queued:** 5-6 sessions for B4-B7. Spread across 2-3 weeks at owner discretion. Each lands independently as a v0.2.x point release on lege-artis/fourier.

**Why B7 stays Opus.** B7 is the *synthesis* chapter — it introduces the entire "beyond DFT" toolkit (Welch / wavelets / bispectrum / Rossi-alpha / Feynman-alpha / HHT-EMD) and shows where pure-DFT analysis becomes insufficient. The pedagogical arc — taking Shad from "find peaks" to "read system dynamics" — needs an author who can hold the full reader-model across multiple sub-topics and decide where to inline math, where to defer to references, where to add a figure. That synthesis judgement is what Opus authoring brings.

---

## §2. Pedagogical progression — why this order works

B1 → B2 → B3 built the reader from "single tone" → "polyphony" → "diagnostic harmonics + non-integer fault peaks." The reader leaves B3 with a working intuition for **time-domain → frequency-domain** as a diagnostic operation.

B4 → B5 → B6 escalate the engineering domain while keeping the math constant:

- **B4 (Electronic):** the math doesn't change, but the *system* now influences the spectrum (filters, mixers, oscillators). Reader learns that a circuit's behaviour can be *predicted* from its frequency response. Cross-over from "describing signals" to "describing systems."
- **B5 (Radar):** the spectrum becomes a *measurement* — range from delay, velocity from Doppler shift, both extracted simultaneously via matched filtering. Reader learns that the DFT can recover physical quantities, not just describe them.
- **B6 (Radioastronomy):** the spectrum reveals nature's signals — pulsar fundamental periods, Doppler from binary orbits, cosmological redshifts. Reader sees the same algorithm applied at >10⁹ × the audio scale, to detect signals buried 20+ dB below noise.

B7 then closes the arc with the *limits* of pure DFT, introducing the "beyond" toolkit needed for non-stationary, non-linear, system-dynamic problems. Nuclear-reactor noise is the canonical domain where this matters operationally.

---

## §3. Authoring sequence + Sonnet delegation pattern

**Order of execution** (per project-owner direction):
1. **B4 Electronic** (lowest research overhead — RF context only). Sonnet brief: `_handoffs/macbook-v0.2.x-weekend/JOB-1-SHAD-B4-ELECTRONIC.md` (already authored as part of weekend briefcase).
2. **B5 Radar** (NEXRAD as lead, well-documented). Sonnet brief: `_handoffs/shad-b5-radar/SONNET-BRIEF.md`.
3. **B6 Radioastronomy** (pulsar timing as lead). Sonnet brief: `_handoffs/shad-b6-radioastronomy/SONNET-BRIEF.md`.
4. **B7 Nuclear reactor capstone** (synthesised reactor-noise + "Fourier and beyond"). Opus staging notes: `_specs/SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md`.

**Sessions in parallel?** Yes — B4 and B5 can be authored in parallel Sonnet sessions (no shared scope). B6 should wait for B5 to land (the "lead with 1D time-series before generalising to 2D aperture-synthesis" arc benefits from the radar groundwork). B7 must wait for B6.

**Output channels per band** (same as v0.2.0 cut, proven):
- Author + commit to monorepo `thinkpad` branch under `fourier/`
- Pete subtree-pushes to public `lege-artis/fourier` from ThinkPad at green
- Tag: `vN.M.K-shad-bX-shipped` at each band's commit
- Cumulate to a v0.2.x point release when 1-3 bands land together; B7 alone earns a v0.3.0 release

---

## §4. Per-band scope summary

### B4 — Electronic systems
- **Lead example:** PWM switching converter (typical 100 kHz switching frequency) → harmonic spectrum → intermodulation when load modulates switching pattern
- **Three sub-topics:** AC mains harmonics → Sallen-Key active filter → heterodyne mixer
- **Primary references:** Sedra & Smith *Microelectronic Circuits* (Sallen-Key topology), Razavi *RF Microelectronics* (mixer math), IEEE 519-2022 (THD)
- **Brief location:** `fourier/_handoffs/macbook-v0.2.x-weekend/JOB-1-SHAD-B4-ELECTRONIC.md`

### B5 — Radar
- **Lead example:** NEXRAD weather radar (NOAA Level-II archives) — Doppler spectrum reveals wind velocity vs reflectivity
- **Math anchor:** matched-filter pulse compression + range-Doppler cross-correlation (same DFT, two-dimensional)
- **Primary references:** Skolnik *Radar Handbook* (3rd or later), Richards *Principles of Modern Radar*, NOAA NEXRAD documentation
- **Brief location:** `fourier/_handoffs/shad-b5-radar/SONNET-BRIEF.md`

### B6 — Radioastronomy
- **Lead example:** pulsar timing series — short-period millisecond pulsar (PSR B1937+21, period 1.558 ms) — DFT of timing residuals over hours reveals pulse frequency with razor-sharp precision
- **Math anchor:** harmonic summing + coherent dedispersion (same DFT, frequency-locked)
- **Brief mention:** VLA aperture synthesis as "where this generalises to 2D Fourier inversion (visibility → brightness)"
- **Primary references:** Lorimer & Kramer *Handbook of Pulsar Astronomy*, NANOGrav published pulsar timing arrays
- **Brief location:** `fourier/_handoffs/shad-b6-radioastronomy/SONNET-BRIEF.md`

### B7 — Nuclear reactor (capstone) — OPUS ONLY
- **Framing:** real primary data + synthesised model as theoretical explanation (revised 2026-05-11 — earlier "synthesised primary" framing was over-conservative).
- **Three primary real-data candidates** — authoring session evaluates all three and picks best fit:
  1. **OECD-NEA Data Bank — Halden Reactor Project (HRP) archives** (registration; canonical reactor-noise research source from HBWR 1958-2018)
  2. **VR-1 "Vrabec" — Czech Technical University Prague (FJFI ČVUT)** (open university-published; pedagogical reactor by design; Kropík/Sklenka/Bilý publications; local-advantage path)
  3. **TU Wien Atominstitut — TRIGA Mark II** (open institutional reports; published in Kerntechnik / Nuclear Engineering & Design)
- **Pedagogical arc:** open with real signal → compute PSD → Lorentzian shape revealed → introduce point-kinetics theory to *explain* what the signal is doing → α measured from spectrum → introduces Welch / wavelets / Rossi-α / Feynman-α / bispectrum / HHT-EMD toolkit
- **Synthesised model retained** as theoretical-explanation backbone (point-kinetics + delayed-neutron groups + thermal feedback), not as primary example
- **Primary references:** Pál *Theory of Linear Stochastic Reactor-Kinetic Equations*, Pázsit & Pál *Neutron Fluctuations*, Williams *Random Processes in Nuclear Reactors* (all three reactor-noise textbooks cite real Halden traces in their appendices — useful cross-reference for dataset interpretation)
- **Staging notes:** `fourier/_specs/SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md`

---

## §5. Cross-band coherence — pattern rules every brief enforces

Every band must obey the patterns already proven in B1+B2+B3:

1. **Chapter structure** — 7 sections: premise → setup → input figure → transform (with method) → spectrum figure → takeaway-annotated figure → "what we just did" closer
2. **3 figures per band** — `fig-bN-input.png`, `fig-bN-spectrum.png`, `fig-bN-takeaway.png`. B7 may justify a 4th comparison figure (PSD vs spectrogram of same data).
3. **Density target** — 6-8 markdown pages (~150-250 lines). B7 may run 10-12.
4. **Reproducibility** — `np.random.seed(<numeric>)` at top of example script; figures byte-reproducible on re-run.
5. **Dependencies** — stdlib + NumPy + Matplotlib only. NO SciPy / pandas / FFTW / domain-specific libraries in B4/B5/B6 example scripts (B7 may grant Welch via `scipy.signal.welch` since it's the toolkit-introduction chapter).
6. **Citation rigour** — each band's example script + chapter must cite ≥3 real published sources in `shared/reference-bibliography/refs.bib`. Citation keys ASCII-only.
7. **Real-data extension** — bottom-of-script comment in each example script pointing at the cataloged primary dataset (NEXRAD URL, NANOGrav release, Halden reactor-noise paper). Keeps script runnable without internet, documents upgrade path.
8. **Sanitization** — public CC-BY-SA-4.0 surface. No project-owner real-name beyond `Pete Y.`, no client entity-tying terms. Pre-flight grep per existing roadmap §5.

---

## §6. Out of scope (parking lot)

- **LIGO/VIRGO** — moved out of Shad-tier into the GW-solver portfolio project (parallel to kh-sim, queued behind it). Not in B4-B7.
- **2D aperture-synthesis imaging** — mentioned at end of B6 as "where pulsars generalise to" but NOT authored in B6. Reserved for a possible future B6.5 or a separate imaging-focused doc.
- **Quantum-spectroscopy / NMR** — not in B4-B7 scope. Different mathematical context (FID + Fourier transform of free-induction decay); would justify its own band if pursued.
- **Optical-spectroscopy** — not in B4-B7 scope. Same reason; better suited as a sibling chapter set.
- **Cumulative v0.2.x release engineering** — when each band lands, the release-notes update is a separate small step (NOT part of the Sonnet authoring brief).

---

## §7. Status report convention (each Sonnet session reports back)

Each Sonnet authoring session writes a `STATUS-REPORT-FILLED.md` to its own briefcase folder (`_handoffs/shad-b5-radar/`, `_handoffs/shad-b6-radioastronomy/`) at park-time or end-of-session, mirroring the macbook-v0.2.x-weekend pattern. Pete reads it on next ThinkPad session and decides:

- Whether to subtree-push the band to public lege-artis/fourier
- Whether to bump v0.2.x tag
- Whether the band needs another iteration before public

End of SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md
