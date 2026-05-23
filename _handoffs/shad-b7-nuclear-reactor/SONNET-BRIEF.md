# Sonnet handoff — Shad-tier B7: Nuclear reactor noise (capstone chapter)

**VOICE UPDATE (2026-05-23):** Read `_handoffs/SHAD-V0.2-VOICE-ADDENDUM-FOR-BRIEFS.md` BEFORE proceeding. The "mirror B3 voice" instruction in this brief is superseded; new exemplars are B0 + B1 v0.2. **ALSO:** the addendum §3 (B7 row) surfaces an unresolved roadmap-vs-brief contradiction (Opus-only vs Sonnet-brief-exists). Surface that to the project owner before authoring B7.

**Status:** Ready to execute. Best authored after B6 (Radioastronomy) lands so the cross-band arc is closed. Independent of any v0.2.x port/test work.
**Estimated effort:** 2 Sonnet sessions per the staging-notes §4 plan; ~4-6 hours each.
**Acceptance gate:** all checks in §10 pass; final tag `v0.2.x-shad-b7-shipped`.
**Predecessor:** `_specs/SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md` — read this in FULL before starting. The staging notes are the design contract; this brief operationalises them.

---

## §0. Read these first (in order)

1. **`_specs/SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md` — the design contract.** Every authoring decision references this doc. §2 (dataset + theory), §3 (pedagogical arc), §4 (two-session plan), §5 (after-B7 framing) are all binding.
2. `_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` — B7's place in the B4-B7 sequence + cross-band coherence rules.
3. `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — the "why a fourth doc tier" framing + Shad-as-audience-proxy + iconography.
4. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy + three doc tiers.
5. `docs/shad/03-vibration.md` + `docs/shad/05-radar.md` — your authoring exemplars. B7 mirrors their structure (input → DFT → interpretation → broaden) but is LONGER + introduces "and beyond Fourier" toolkit.
6. `examples/shad/b3-vibration/main.py` + `examples/shad/b5-radar/main.py` — script exemplars. B7 script is ~150-250 lines (longest of any chapter).
7. `_handoffs/shad-b6-radioastronomy/SONNET-BRIEF.md` — direct sibling brief structure; B7 follows the same skeletal organisation with the added Section 6 toolkit walkthrough.
8. `../../_config/SANITISATION-POLICY-v0.1.md` — public-mirror context applies; zero tolerance for forbidden identifiers.

Optional but useful:
- Pál L., *Theory of Linear Stochastic Reactor-Kinetic Equations* — reference for the synthesised-model derivation
- Pázsit I., Pál L., *Neutron Fluctuations: A Reference Manual* — Lorentzian PSD + Rossi-α + Feynman-α derivations
- Williams M.M.R., *Random Processes in Nuclear Reactors* — Langevin formulation

---

## §1. Where B7 sits in the Shad-tier arc

The reader leaving B6 (Radioastronomy) believes the DFT is universal: 11 orders of magnitude in frequency, same algorithm, same interpretation. **B7's specific contribution:** show where pure DFT *stops being enough*, and equip the reader with the canonical extensions.

This is the chapter where Shad meets a domain (nuclear-reactor noise) where:
- Signals are non-stationary (start-up, scram, control-rod motion)
- Coupling is non-linear (neutron-thermal-hydraulic feedback produces frequency intermodulation)
- Noise is correlated, not white
- The DFT gets the reader ~60% of the way and then needs help

The "and beyond Fourier" toolkit (Welch, STFT, wavelets, Rossi-α, Feynman-α, bispectrum, coherence) IS the chapter's payoff. After B7, Shad knows when bare DFT is enough and when it isn't.

---

## §2. Two-session execution plan (per staging notes §4)

### Session 1 — Real data + theory backbone

**Effort:** 4-6 hours.
**Deliverables:**
- `examples/shad/b7-nuclear-reactor/` directory created
- `examples/shad/b7-nuclear-reactor/data/` populated with selected dataset (or synthesised fallback)
- `examples/shad/b7-nuclear-reactor/main.py` — sections 1-4 of the chapter's analysis pipeline
- `docs/shad/07-nuclear-reactor.md` — chapter sections §1 to §4 authored
- 2 figures rendered: `input_trace.png` + `bare_dft_lorentzian.png` (~300 KB each, ≤500 KB total)
- New citations appended to `shared/reference-bibliography/refs.bib`
- Tag at green: **`v0.2.x-shad-b7-session1-real-and-theory`**

**Sub-tasks (in order):**

1. **Data sourcing** (§3 below). Probe the four candidate paths in order; first acceptable hit wins. Document the choice + provenance + license in `data/PROVENANCE.md`.
2. **Synthesised model** (§4 below). Author the point-kinetics-with-Langevin-source implementation alongside the real data so the chapter can compare them side-by-side.
3. **Sections 1-4 of the chapter** mirroring the pedagogical arc steps 1-4 from staging notes §3.
4. **2 figures**: the real input trace + the bare DFT power spectrum showing the Lorentzian signature.
5. **α-extraction sanity check**: confirm the prompt-neutron decay constant α extracted from the corner frequency matches the dataset's documented value (or the synth model's known input).
6. Commit + tag.

### Session 2 — Toolkit walkthrough + closing

**Effort:** 4-5 hours.
**Deliverables:**
- `main.py` extended with sections 5-7 (limit-test transient + 6-7 toolkit demos + closing)
- `docs/shad/07-nuclear-reactor.md` extended with chapter sections §5 to §7
- 3 additional figures: `transient_dft_vs_spectrogram.png`, `rossi_feynman_alpha.png`, `bispectrum_coupling.png`
- `docs/shad/README.md` updated to mark the seven-band journey complete + cross-link to B7
- (Optional, recommended) `fourier/RELEASE-NOTES-v0.3.0.md` authored with B1-B7 closure note
- Tag at green: **`v0.2.x-shad-b7-shipped`** (final)

**Sub-tasks (in order):**

1. **Limit-test transient** — construct a synthesised scram or control-rod-step trace; show the bare DFT smears the time structure into the frequency domain in a way that loses interpretability. Motivates the "and beyond" pivot.
2. **Toolkit walkthrough** (§5 below). One demo per method; each demo is a small block of `main.py` + a paragraph of narrative in the markdown.
3. **Closing section** — literature pointers (Pál, Pázsit, Williams from staging notes §2.4) + "where Shad graduates" framing per staging notes pedagogical arc step 7.
4. Final ASCII-sanitisation pass on all source files; final grep audit per staging notes §2.5.
5. Tag + (optional) release notes authoring.

---

## §3. Data sourcing procedure (Session 1 sub-task 1)

Per staging notes §2.1: try the four candidate paths IN ORDER. The first one that meets all five evaluation criteria becomes the chapter's hero dataset; the others are fallbacks.

**Evaluation criteria (re-stated from staging notes):**
- (A) Lorentzian-PSD signature visible in raw data
- (B) Sample rate ≥ 1 kHz documented
- (C) Duration 10-60 s workable
- (D) License compatible with CC-BY-SA-4.0 redistribution as a chapter fixture
- (E) Sample size ≤ 1 MB after decimation/excerpting (full original cited separately)

### §3.1 Candidate 1 — OECD-NEA Data Bank / Halden Reactor Project archives

- **Portal:** [`nea.oecd.org/dbforms/data/eva/evatapes/`](https://www.oecd-nea.org/jcms/pl_24812/databank-computer-program-services). Registration required (free for member-state academics).
- **Look for:** HRP noise-diagnostic work packages + IRPHE benchmarks containing time-series.
- **Acceptance pre-check:** Pázsit/Pál/Williams textbooks cite specific Halden experiments — work backwards from textbook figures to find raw-data sources.
- **Risk:** registration friction; "free for academics" definition may require institutional verification.
- **License risk:** OECD-NEA data may be free-to-use but redistribution restrictions could prevent shipping the data as a CC-BY-SA-4.0 repo fixture. If license check fails → cite the source + ship synthesised-fallback as repo fixture.

### §3.2 Candidate 2 — VR-1 "Vrabec" — Czech Technical University Prague (FJFI ČVUT)

- **Portal:** [`vr1.cvut.cz`](https://www.vr1.fjfi.cvut.cz/) + DSpace at ČVUT.
- **Look for:** Kropík, Sklenka, Bilý publications + linked supplementary data.
- **Pedagogical reactor by design** — lowest access friction of the four candidates.
- **License pre-check:** university repository, typically CC or similar permissive licenses; verify per-dataset.
- **STATUS NOTE FROM USER (2026-05-22):** Project owner has local-advantage path for direct contact if needed. **Recommended as default unless Halden has cleaner Lorentzian signature.**

### §3.3 Candidate 3 — TU Wien Atominstitut — TRIGA Mark II

- **Portal:** [`ati.tuwien.ac.at/reactor/EN/`](https://ati.tuwien.ac.at/reactor/EN/) + TU Wien institutional reports + Kerntechnik / Nuclear Engineering & Design publications.
- **Look for:** Atominstitut neutron-noise publications; recent CRAB facility work ([arxiv 2505.15227](https://arxiv.org/pdf/2505.15227)) + UT Austin thesis on TRIGA Mk II noise digital twins ([UT repositories](https://repositories.lib.utexas.edu/items/53305855-dca8-4f56-ba5e-a8f7ec949102)).
- **Risk:** publications include processed data + spectra figures, but raw time-series may require direct contact with the Atominstitut. User flagged 2026-05-22: "not sure Atominstitut is available easily but was for sure on the list."
- **Fallback role:** if Halden + VR-1 both miss, this is the third-pass attempt.

### §3.4 Candidate 4 — Figshare / Zenodo open-data search

- **Portal:** [`figshare.com`](https://figshare.com/) and [`zenodo.org`](https://zenodo.org/) searched for "reactor neutron noise time series", "TRIGA", "Halden".
- **Known hit:** NPPAD (open time-series simulated dataset for NPP accidents) — but this is NPP transients, not zero-power noise, so may NOT exhibit the Lorentzian-PSD signature the chapter needs. Evaluation criterion (A) may fail.
- **Other open-data hits:** arxiv 2305.18242 dataset for neutron/gamma pulse shape discrimination — wrong physics scope for this chapter (single-event analysis, not noise spectrum).
- **Realistic outcome:** Figshare/Zenodo may NOT have a directly suitable dataset; document the search + fall back to synthesised.

### §3.5 Fallback — synthesised reactor-noise as primary

Per staging notes §2.2 + §2.5: if all four candidates miss the evaluation criteria, the synthesised point-kinetics-with-Langevin model becomes the chapter's hero data, with the four candidates referenced as the "what real data looks like, here's what we mimic" cross-reference.

This fallback is **not a failure** — the staging notes explicitly recognise it as a viable path. The chapter's pedagogical value is in the analysis methodology, not in which specific reactor's data is the demo input.

### §3.6 Document the choice + sanitisation audit

Whichever path is chosen, author `examples/shad/b7-nuclear-reactor/data/PROVENANCE.md` containing:
- Dataset name + source institution
- URL + retrieval date + retrieval method (browser download, contact-and-receive, synth-generated, etc.)
- License declared by source + verified compatibility with CC-BY-SA-4.0 redistribution
- Format conversion notes (raw → CSV/NPZ as shipped)
- Decimation / excerpting details (if applied; the goal is the ≤1 MB repo-fixture cap)
- Sanitisation audit pass: confirmed no forbidden-identifier leakage in dataset metadata, no project-owner real-name beyond `Pete Y.`

---

## §4. Synthesised model — point-kinetics + Langevin source

Per staging notes §2.2: required even when real data is the chapter's hero (it's the *explanation* layer that teaches Shad why the signal looks the way it does).

**Components (~150 lines target in `main.py`):**

1. **Point-kinetics equations with 6 delayed-neutron precursor groups** (canonical thermal-reactor model):
   ```
   dn/dt = ((ρ - β)/Λ) · n + Σ_i λ_i · C_i + S(t)
   dC_i/dt = (β_i / Λ) · n - λ_i · C_i      (i = 1..6)
   ```
   where n = neutron population, C_i = precursor group concentrations, ρ = reactivity (perturbed by reactivity-noise input), β = total delayed fraction, Λ = prompt-neutron mean lifetime, λ_i = group decay constants, β_i = group delayed fractions, S(t) = Langevin stochastic source.

2. **Langevin source term** (Pál §4 canonical form): Gaussian white-noise reactivity input scaled to produce the observed signal-to-noise ratio. Document the noise-amplitude calibration.

3. **Numerical integration**: stiff ODE — the precursor decay timescales span 10⁻¹ to 10² seconds while prompt-neutron lifetime is 10⁻⁴ s. Use `scipy.integrate.solve_ivp` with `method='BDF'` for stability.

4. **Optional thermal-feedback** (reactivity ∝ -α_T · T_fuel) — toggleable so the chapter can show "linearised vs feedback-coupled" comparison. Default OFF for the linear-theory match; ON in §6 bispectrum demo to show frequency intermodulation.

5. **Optional xenon-iodine slow loop** (Bateman equations) — explicitly **OUT OF SCOPE** for the 60-second example (timescale is ~10 hours).

**Numerical-method discipline reminder:** the integrator-quality validation is on Pete + the textbook PSD shape, not full doctrine §4.4 C1-C4 acceptance criteria (those apply to the canonical-reference *backend* implementations of FFT, not to example scripts).

---

## §5. Toolkit walkthrough (Session 2 sub-task 2)

Per staging notes §2.3: one demo per method. The seven methods, in chapter order:

| # | Method | Implementation | Demo target | Figure |
|---|---|---|---|---|
| 1 | Welch's PSD | `scipy.signal.welch` | Stationary noise — smoother PSD than bare DFT, confidence-interval narrative | combined with bare-DFT plot for comparison |
| 2 | Spectrogram / STFT | `scipy.signal.spectrogram` | Apply to a control-rod-step or scram transient; show time-frequency localisation | `transient_dft_vs_spectrogram.png` (2-panel: bare DFT smears, spectrogram resolves) |
| 3 | Wavelets | `pywavelets` (cwt) | Same transient as STFT, finer time-frequency tradeoff | (optional inline; can fold into spectrogram figure) |
| 4 | Rossi-α | custom ~50 lines | Time-domain analogue of PSD-corner-frequency α extraction; same α independently verified | `rossi_feynman_alpha.png` (2-panel: Rossi vs Feynman) |
| 5 | Feynman-α | custom ~50 lines | Variance-to-mean ratio; same α from a third method | combined with Rossi-α figure |
| 6 | Bispectrum | custom or via `stingray` | Non-linear coupling detection: with thermal-feedback ON, show signal at f₁+f₂ beyond f₁ and f₂ | `bispectrum_coupling.png` |
| 7 | Coherence + transfer function | `scipy.signal.coherence` | Cross-spectral analysis between simulated sensor pairs | (optional inline; can fold into bispectrum figure if density limits hit) |
| 8 | HHT / EMD | `PyEMD` | Optional — only if chapter density permits | (defer; document in closing as "another path") |

**SciPy + pywavelets + PyEMD exception:** B7 explicitly grants these libraries (vs B1-B6's "pure stdlib"). Document this exception in the chapter's preamble — the math is too involved to reinvent, and the reinvention would distract from the pedagogical payoff.

Per-toolkit-method paragraph in the markdown:
- What the method computes (1 sentence, plain English)
- Why it answers the question bare DFT couldn't (1 sentence)
- Result on the demo data (the figure caption does the heavy lifting)
- Where to learn more (one textbook + one paper, cited per refs.bib)

---

## §6. Implementation discipline (NON-NEGOTIABLE)

Inherited from fourier project conventions and reaffirmed for B7:

- **ASCII-only source files** for `.py`, `.toml`. Markdown narrative may use Unicode (em-dash, multiplication sign, etc.) matching the B3 / B5 exemplar style.
- **Equation-to-code mapping** in `main.py` header docstring + section-header comment blocks.
- **CC-BY-SA-4.0 license header** in the markdown chapter file. Apache-2.0 in the example script.
- **Cross-link discipline** — chapter ends with pointers into the canonical tier (`docs/canonical/en/` if relevant equations are there) + into the `refs.bib` entries used.
- **Sanitisation public-mirror discipline** — per staging notes §2.5: NO SUPIN / Bouracka / Improwave / MIM2000 / Yamyang / Vitez identifiers anywhere. Project-owner name `Pete Y.` only. No private-monorepo paths.
- **Figure constraints** — ≤300 KB each, PNG, dpi 120, figsize ≤(12, 6); deterministic seed for any random-data figure so re-runs produce identical PNGs.
- **Tolerance for synthesised α-extraction vs real α**: ±10% (this is a reactor-noise diagnostic, not a precision measurement; the chapter's claim is "we can read α off the plot," not "we can replicate the textbook value to 4 significant figures").
- **No new external dataset fetch from inside `main.py`** — data lives in `data/` directory + is loaded from there. Fetch logic (if any) is a separate `data/fetch.sh` or `data/fetch.py` that's run manually + documented in PROVENANCE.md.

---

## §7. Out of scope (deliberately)

- **Xenon-iodine slow loop modelling** — ~10-hour timescale, would require multi-hour example simulation. Mentioned in closing as "another regime, another chapter."
- **Stochastic neutron transport at full Monte Carlo resolution** — far beyond Shad-tier scope. Pál's stochastic-kinetics is enough for the spectral signatures.
- **3D spatial-noise modelling** — Demazière/Pázsit Chalmers CORE SIM territory; cited in closing but not implemented.
- **Translations to CS / JA / DE / IT** — separate v0.1.1+ workstream; B7 ships English-first.
- **Doctrine §4.4 C1-C4 application** — those bind backend canonical-reference implementations of FFT/DFT, not Shad-tier example scripts. The B7 script is not a canonical-reference implementation; it's pedagogical analysis using existing scipy primitives.
- **Multi-language port of B7 example** — Python only. The whole Shad-tier is Python-only by design.

---

## §8. References

- `_specs/SHAD-TIER-B7-CAPSTONE-OPUS-NOTES-v0.1.md` — primary design contract
- `_specs/SHAD-TIER-AUTHORING-ROADMAP-B4-B7-v0.1.md` — sequencing
- `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — Shad-tier framing
- `docs/shad/03-vibration.md` + `05-radar.md` — authoring exemplars
- `_handoffs/shad-b6-radioastronomy/SONNET-BRIEF.md` — sibling brief pattern
- Pál L. — *Theory of Linear Stochastic Reactor-Kinetic Equations* (textbook anchor)
- Pázsit I., Pál L. — *Neutron Fluctuations: A Reference Manual*
- Williams M.M.R. — *Random Processes in Nuclear Reactors*
- Search-result references for data candidates (Session 1 sub-task 1):
  - [ATI: Reactor (TU Wien)](https://ati.tuwien.ac.at/reactor/EN/)
  - [VR-1 Vrabec (FJFI ČVUT)](https://www.vr1.fjfi.cvut.cz/)
  - [OECD-NEA Data Bank](https://www.oecd-nea.org/jcms/pl_24812/databank-computer-program-services)
  - [Introduction to neutron noise of a Triga reactor (INIS-IAEA)](https://inis.iaea.org/records/63w74-atb85)
  - [Investigation of TRIGA Mk II reactor noise (UT Austin)](https://repositories.lib.utexas.edu/items/53305855-dca8-4f56-ba5e-a8f7ec949102)
  - [CRAB facility at TU Wien TRIGA (arxiv 2505.15227)](https://arxiv.org/pdf/2505.15227)

---

## §9. STATUS report template

At end of Session 2, author `_handoffs/shad-b7-nuclear-reactor/STATUS-FILLED.md` covering:

1. **Session 1 outcomes:**
   - Data-source path chosen (which of §3.1-§3.5)
   - PROVENANCE.md content summary
   - License-compatibility confirmation
   - Synthesised-model parameters + α target value
   - Real-vs-synth α extraction agreement (numerical comparison)
   - Tag log at session 1 close
2. **Session 2 outcomes:**
   - Toolkit method list with PASS/SKIP per method (7 + optional HHT)
   - Final chapter length (markdown page count or word count)
   - Figure inventory + total size
   - SciPy + pywavelets + PyEMD exception documented in chapter preamble (confirmed)
3. **Sanitisation audit results:**
   - Grep audit clean (forbidden-identifier search)
   - No project-owner real-name beyond Pete Y.
   - No private-monorepo path references
4. **Cross-link verification:**
   - All `[link](path)` references resolve
   - refs.bib entries for new citations present
5. **Acceptance gate** (per §10):
   - All 10 checks PASS or note exceptions
   - Final tag landed
6. **Open questions / Opus-escalations** — particularly: did the data-source decision land on real or synth? If real: which institution + license terms? If synth: what fidelity validation was applied?

---

## §10. Acceptance gates

| # | Gate | Pass condition |
|---|---|---|
| 1 | Data source documented | PROVENANCE.md complete; license verified compatible with CC-BY-SA-4.0 |
| 2 | Lorentzian signature visible | The bare DFT figure shows the characteristic flat-then-rolloff shape; α extractable from corner frequency |
| 3 | Synthesised model validates | Synth-model α matches real-data α (or synth-input α matches synth-output α) to ±10% |
| 4 | Pedagogical arc complete | Sections 1-7 from staging notes §3 all present in chapter markdown |
| 5 | Toolkit walkthrough density | At least 6 of the 7 methods demonstrated (HHT/EMD optional) |
| 6 | Limit-test transient shown | Bare-DFT vs spectrogram side-by-side figure present |
| 7 | Rossi-α + Feynman-α agreement | Both methods extract α matching the PSD-method α within ±15% |
| 8 | Sanitisation grep | No forbidden identifiers; no private-monorepo paths; project-owner only as "Pete Y." |
| 9 | Figure constraints | All 5 figures ≤300 KB each; deterministic seeds; total figure storage ≤1.5 MB |
| 10 | Chapter density | ~10-12 markdown pages; ~150-250 lines in main.py; both within bounds |

When 10/10 gates green: tag `v0.2.x-shad-b7-shipped`; B1-B7 seven-band Shad-tier journey complete. Optional follow-up: author `RELEASE-NOTES-v0.3.0.md` capturing the closure.

---

*End of SONNET-BRIEF.md — Shad-tier B7 nuclear-reactor capstone.*
*Apply against current fourier HEAD (v0.2.0 PUBLIC baseline + any v0.2.x point releases in flight).*
*Two Sonnet sessions; sequence after B6 lands. Final chapter closes the Shad-tier arc.*
