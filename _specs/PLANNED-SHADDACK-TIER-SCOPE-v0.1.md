# Planned: Just Shad's Guide to Fourier's Galaxy

**Status:** SCOPE LOCKED · IMPLEMENTATION ON-DECK (raised priority — see §7)
**Target version:** runs alongside v0.2.0 code work (not after); first deliverable batch covers bands B1+B2+B3 as a coherent published package
**Author:** Petr Yamyang
**Date:** 2026-05-10 (v0.2 — name "Shaddack" replaced by "Shad" / "Just Shad" per project owner 2026-05-10; first-deliverable scope expanded from B1-only to B1+B2+B3; priority raised to alongside-code-and-tests)
**License:** CC-BY-SA-4.0 (this is a docs scope-doc)
**Filename note:** the file path retains `PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` for path continuity from v0.1.0 release; treat the filename as historical paper-trail. The active name for this doc tier is **"Shad-tier"** or, in deliverable titles, **"Just Shad's Guide"**.

> "Standard technical documentation is must-have. But extra layer 'Fourier
> for dummies especially for Shaddack' or 'Shaddack's Guide to Fourier's
> Galaxy' would be appreciated."  — Pete Y., 2026-05-09

---

## 1. Why a fourth doc tier

The three tiers locked in `WORKING-SPEC-v0.3-EN.md` §6 (canonical /
engineer / performance) cover the standard rigour gradient — math
formalism → working examples → optimisation. They are written for
readers who are already comfortable with Fourier as a concept.

A fourth tier — **engineer-narrated**, dry-humour, anchored in
real-world data — serves a different reader profile:

- Sharp technical mind with poor formal-math comfort
- Wants to see the algorithm work on data that resembles their day job
- Will not read 40 pages of theory before touching code
- Will read 8 pages of "here is an oscilloscope trace, here is what its
  Fourier transform tells us, here is how we got from one to the other"

This tier exists to make the library reach **practising engineers /
hackers** who would otherwise bounce off the canonical-tier stack. It
also serves as a continuous integration test for the engineer-tier docs:
if a worked example doesn't run cleanly through the public API, the
public API has a usability bug.

## 2. Audience proxy

**Shad** (close-friend nickname; "Just Shad" in deliverable titles where
extra warmth is appropriate) — friend of the project owner; superb
hacker; sober technical humour; approaching 50; comfortable with
`oscilloscope.csv` and very uncomfortable with
`\hat{f}(\xi) = \int f(x) e^{-2\pi i \xi x} dx`.

If a doc page successfully takes Shad from "what is this Fourier thing"
to "I have my data on a graph and the algorithm worked", that page
passes the Shad-tier acceptance gate.

### 2.1. Iconography (locked 2026-05-09)

Pages, examples and outputs aimed at the Shaddack reader profile carry
a recurring avatar mark:

> **Miyazaki-style dragon, smoking weed, drinking tea.**

Visual register: hand-drawn / watercolour / Studio-Ghibli line work;
calm, slightly amused expression; tea cup over teapot, smoke curl
ambient (not foregrounded). Style coexists with the canonical-tier's
serif-mathematical aesthetic and the engineer-tier's clean-geometric
aesthetic — three tiers, three visual registers, one shared layout grid.

**Dual purpose.** Same avatar will be used as the replacement
practitioner-mark on **mim2000.cz** (3-fold-path professional face),
swapping out the current placeholder asset. This means the Shaddack
icon is a strategic visual asset, not just a docs flourish — it crosses
project boundaries (lege-artis/fourier docs <-> 3-fold-path/mim2000).

**Asset task (deferred).** Find or commission. Open options:
- (A) Source from public-domain / CC-BY illustrator portfolios
  matching the Ghibli-adjacent register
- (B) Commission custom artwork (preferred long-term — avatar becomes
  identity asset, not a borrowed token)
- (C) Generate via image model under explicit licence-compatible
  workflow, then redraw / adjust

Recommend (B) for the v0.2.x rollout window. Budget + commission
sourcing tracked separately when v0.1.0 closes green and the docs tier
gets greenlit for authoring.

**Non-negotiable**: the asset must be license-clean for use in (1)
Apache-2.0 + CC-BY-SA-4.0 lege-artis docs, (2) commercial mim2000.cz
practitioner site. CC-BY-SA-4.0 or full assignment to project owner.

## 3. Progression spine — five complexity bands

Each band is one self-contained chapter with: input dataset (real,
public, citable) → input plot → Fourier-coefficient table → output
spectrum plot → step-by-step code walkthrough → "what this told us"
takeaway.

| Band | Source | Data shape | Take-away the chapter teaches |
|------|--------|------------|-------------------------------|
| B1 — Oscilloscope trace | Public scope-capture archives (e.g. EEVblog forum, GitHub `*.csv` traces) | scalar(t) · single channel · ~10 kHz–100 MHz sample rate | "DFT turns a time-domain trace into a frequency spectrum. Peaks = real signals." |
| B2 — Audio sample (single tone family) | Wikipedia Commons audio · LibriSpeech · Freesound CC0 | scalar(t) · 44.1 kHz mono · ≤10 s | "Multiple tones stack additively in the spectrum. Windowing matters." |
| B3 — Vibration / accelerometer telemetry | NASA Bearing Dataset · MIMII · Kaggle vibration sets | scalar(t) per axis · ≤5 kHz · seconds–minutes | "Real industrial signals carry harmonics + sidebands. Fault diagnosis = spectral pattern matching." |
| B4 — Geophysical / atmospheric | USGS earthquake waveforms · NOAA wind-speed · ERA5 surface pressure | scalar(t) · seconds-to-days · noisy | "Long records → frequency-domain methods are how you find the periodic component buried in the noise." |
| B5 — Cutting-edge: radio interferometry | EHT public data release · LIGO open data (gravitational waves) · LOFAR archives | calibrated visibility / strain time-series | "FFT is the workhorse of modern observational physics. Same algorithm, bigger dataset, harder I/O." |

**B1 → B5 progression**: each band introduces *exactly one* new
challenge. The reader who finishes B5 has been escalated through:
windowing (B2), industrial-signal nuance (B3), long-record / noise (B4),
big-data / calibrated-pipeline considerations (B5).

## 4. Style commitments

- **Tone:** dry, technical, sober humour; no pop-culture hot takes;
  occasional one-liner where it actually clarifies a concept
- **Math density:** equations appear with intuition first, formula
  second, link to canonical-tier proof third
- **Code:** every chapter ships a runnable `examples/shaddack/<bandN>/`
  directory with public-data download script + transform script + plot
  script. No "exercise for the reader."
- **Plots:** ASCII fallback for terminal-only readers + PNG/SVG for
  web/docs. Minimum 3 plots per chapter (input, spectrum, annotated
  takeaway).
- **Length:** ≤ 12 pages per chapter. If a chapter exceeds 12 pages
  it gets split.
- **Reference linkage:** every claim links back to either canonical
  tier (`docs/canonical/`) or the source paper / dataset DOI. No
  freestanding hand-waving.

## 5. Public-data sourcing rules

Hard rules on what counts as a usable dataset for the Shaddack tier:

1. **Licence-clear**: CC0, CC-BY, CC-BY-SA, public-domain, or
   explicit-permission. No grey-area scraping.
2. **Citable**: stable DOI or stable archive URL (Zenodo, NASA NSSDC,
   USGS, NOAA, ESA, NRAO, …). GitHub-only sources are tolerated for
   B1/B2 but not for B4/B5.
3. **Reproducible**: every dataset is fetched by a script committed
   to the repo. We commit the **fetch script + a small fixture
   sample**, not the full dataset (size constraints).
4. **Cross-checked**: where possible, the Shaddack chapter shows that
   the same dataset, processed via NumPy/SciPy as oracle, agrees with
   our `dft()` / FFT output to within engineering tolerance.
5. **Anonymous**: no personally-identifying data in any band.
   B2 audio uses public-domain or anonymised samples only.

## 6. Layout in the repo (planned)

```
docs/
├── canonical/          # tier 1 — present
├── engineer/           # tier 2 — present
├── performance/        # tier 3 — v0.5+
└── shaddack/           # tier 4 — THIS DOC'S TARGET
    ├── 00-prologue.md           # what + why + how to use this guide
    ├── 01-oscilloscope.md       # B1 — public scope traces
    ├── 02-audio.md              # B2 — audio analysis
    ├── 03-vibration.md          # B3 — accelerometer / vibration
    ├── 04-geophysical.md        # B4 — long-record geophysical
    ├── 05-interferometry.md     # B5 — EHT / LIGO / radio
    └── examples/
        ├── b1-scope/
        │   ├── fetch.sh         # downloads dataset + cites DOI
        │   ├── transform.f90    # OR python: chooses whichever is clearest
        │   └── plot.py          # matplotlib output
        ├── b2-audio/
        ├── b3-vibration/
        ├── b4-geophysical/
        └── b5-interferometry/
```

Each `examples/bN-*/` is a self-contained, runnable directory. Each is
also wired into CI so we discover when an external dataset URL rots.

## 7. Sequencing — when does this start

Locked sequencing per Pete 2026-05-10 (raised priority from v0.1's "after v0.2.0" to "alongside v0.2.0"):

- **v0.1.0 — DONE 2026-05-10.** Fortran reference public; Stage 4 closed green.
- **v0.2.0 work runs in parallel with Shad-tier work.** Multi-language ports (C++ / Rust / Pascal) and Shad-tier B1+B2+B3 first-deliverable batch progress on parallel tracks rather than sequentially. Rationale: Shad-tier examples need the public API but don't need ALL languages — B1+B2+B3 can be authored against the Fortran v0.1.0 + the first ported language (whichever lands first), and ported to other languages in the same v0.2.x sweep where natural.
- **First deliverable = B1 + B2 + B3 as a coherent published package** (not B1 alone). Rationale: a single-band first cut undersells the progression; three bands together demonstrate the escalation pattern (oscilloscope trace → audio with windowing → industrial vibration with harmonics) and let the reader form a real opinion about the doc tier's value. Better-formatted output, balanced graphs/numbers/text in the first shot.
- **B4 + B5 follow.** Once B1-B3 lands and Shad reviews, B4 (geophysical / long-record) and B5 (radio interferometry / EHT / LIGO) ship in subsequent v0.2.x point releases.
- **Stage 5 perf coupling.** Stage 5 (performance build, gated v0.5+) provides real-world performance numbers for the Shad-tier docs to display: when datasets get large (B4 long-record, B5 EHT/LIGO), the difference between O(N²) reference and FFT-optimised becomes a teaching point. The coupling is intentional — perf benchmarks supply the graphs/numbers for the upper-band Shad chapters; Shad-tier chapters supply the validation that perf optimisations didn't break correctness.
- **Birthday-aware target.** Shad approaches 50; B1+B2+B3 first batch aimed to be reviewable-quality before that birthday. Concrete target-date locked when v0.2.0 first-port lands.

## 8. Acceptance gate for the tier as a whole

The tier is "done" (i.e. exits planned-status, becomes maintained-tier)
when:

- All five chapters (B1–B5) are published
- Each chapter's example code runs to green in CI on at least one
  Shaddack-tier maintainer's box
- One independent reader (Shaddack himself preferred) confirms via
  recorded feedback that they followed B1 end-to-end without prior
  Fourier exposure
- Cross-references with canonical-tier and engineer-tier are
  bidirectional and current

## 9. Risks + mitigations

| Risk | Mitigation |
|------|-----------|
| Tone drift toward "tech bro" or alienating humour | Strict tone-review gate; project owner has veto on humour that doesn't land sober-technical |
| Public dataset URL rot | Fetch scripts in CI; fixtures committed alongside; multiple-mirror fallback for B5 |
| Dataset licence ambiguity | Hard rule §5.1; legal-review pass before any chapter ships |
| Tier becomes "the only tier people read", canonical tier neglected | Every Shaddack chapter ends with link-back box: "if you want to know WHY this works, here is the canonical-tier chapter that proves it" |
| Reader misreads engineering tolerance as mathematical proof | Each chapter has explicit "this is empirical / numerical, not a theorem" sidebar |

## 10. Open questions

- ~~Q-SHAD-1: Will Shaddack consent to having his nickname used as the named tier?~~ **Resolved 2026-05-10**: deliverable name is "Shad" / "Just Shad" (slight familiarity, less direct than "Shaddack"). Final consent for the named tier still wanted before publishing the first batch — but the name reduction de-risks the consent step.
- Q-SHAD-2: Does B5 use EHT specifically, or LIGO (which has friendlier public-data tooling via `gwpy`)? Decide when authoring B5. Pete's lean (2026-05-10): include both — EHT for the radio-interferometry-as-imaging story, LIGO for the strain-as-time-series story. They illustrate different aspects of the same FFT machinery.
- Q-SHAD-3: Does the tier ship in EN-only at v0.2.x, or simultaneously with CS / JA / DE / IT? Suggest EN-only first, translate after one full review pass.
- Q-SHAD-4 (new 2026-05-10): Which of the v0.2.0 ported languages (C++, Rust, Pascal) is the right "first co-published" language for Shad-tier examples? Shad's habit-set leans C++ / hacker-stack — likely C++. Pascal is anchor for v0.2.0 historical-fidelity but not the natural Shad-reader language. Decide when v0.2.0 first port lands.

---

## Cross-links

- `_specs/WORKING-SPEC-v0.3-EN.md` §6 — three current doc tiers
- `docs/canonical/en/` — formal-rigour tier (v0.1.0)
- `docs/engineer/en/` — worked-examples tier (v0.1.0)

When v0.4 of the WORKING-SPEC lands, this scope-doc becomes the §6.4
expansion of the canonical four-tier model.

---

*This file is a planning artefact. It does not commit code or docs;
it commits the project to a particular shape of docs that will be
authored at v0.2.x.*
