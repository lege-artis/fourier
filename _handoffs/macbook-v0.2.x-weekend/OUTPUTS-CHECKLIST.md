# Outputs checklist — what lands where, in what order

**Audience:** the MacBook session executing this briefcase.
**Use:** tick off as you go. Each ☐ becomes ☑ when committed. Don't skip ahead.

---

## §1. Source-tree placement (alphabetized by destination)

```
fourier/
├── _specs/
│   ├── ADR-001-PERF-NOISY-MULTIDIM-v0.1.md        ← JOB-3 main deliverable
│   └── adr-001-poc/                                ← JOB-3 POC artifacts
│       ├── poc-1-perf-baseline.md
│       ├── poc-1-perf-baseline.py
│       ├── poc-2-perf-cpp-fast.md
│       ├── poc-2-perf-cpp-fast.py
│       ├── poc-3-row-then-column.md
│       ├── poc-3-row-then-column.py
│       ├── poc-4-robust-preprocessing.md
│       ├── poc-4-robust-preprocessing.py
│       └── poc-4-figures/
│           ├── raw-fft.png
│           ├── windowed-detrended.png
│           └── welch-psd.png
│
├── backends/
│   └── pascal/                                     ← JOB-2 main deliverable
│       ├── Makefile
│       ├── src/
│       │   └── dft_kernel.pas
│       └── tests/
│           ├── test_dft_unit.pas
│           ├── test_dft_property.pas
│           ├── test_dft_physics.pas
│           └── test_dft_golden.pas
│
├── docs/
│   └── shad/
│       ├── 04-electronic.md                        ← JOB-1 chapter
│       ├── README.md                                ← UPDATE: add B4 to chapter index
│       └── figures/
│           ├── fig-b4-input.png                    ← JOB-1 fig 1
│           ├── fig-b4-spectrum.png                 ← JOB-1 fig 2
│           └── fig-b4-takeaway.png                 ← JOB-1 fig 3
│
├── examples/
│   └── shad/
│       ├── b4-electronic/                           ← JOB-1 script home
│       │   └── main.py
│       └── README.md                                ← UPDATE: add B4 entry
│
├── shared/
│   └── reference-bibliography/
│       └── refs.bib                                 ← APPEND: 3+ new entries (Sedra-Smith, Razavi, IEEE 519)
│
├── _handoffs/
│   └── macbook-v0.2.x-weekend/
│       ├── MASTER-BRIEF.md                          (this briefcase — already committed by ThinkPad)
│       ├── JOB-1-SHAD-B4-ELECTRONIC.md              (already committed)
│       ├── JOB-2-FOURIER-V0.2-PASCAL.md             (already committed)
│       ├── JOB-3-PERF-NOISY-MULTIDIM-SCOPING.md     (already committed)
│       ├── OUTPUTS-CHECKLIST.md                     (this file — already committed)
│       ├── STATUS-REPORT-TEMPLATE.md                (already committed)
│       └── STATUS-REPORT-FILLED.md                  ← YOU WRITE THIS at end of weekend
│
└── RELEASE-NOTES-v0.2.1.md                          ← YOU AUTHOR THIS at end of weekend
```

---

## §2. Commit sequence — in this order

(One commit per logical step. Commit messages use Conventional Commits prefix style consistent with the existing log.)

### Phase A — JOB-1 (Shad B4)

- [ ] Step A1: author + run `examples/shad/b4-electronic/main.py` until the 3 figures land at `docs/shad/figures/fig-b4-*.png`
- [ ] Step A2: author `docs/shad/04-electronic.md`
- [ ] Step A3: update `docs/shad/README.md` (chapter index) + `examples/shad/README.md` (script index)
- [ ] Step A4: append 3+ new entries to `shared/reference-bibliography/refs.bib`
- [ ] Step A5: pre-flight grep (MASTER-BRIEF §5) — must return zero hits
- [ ] **Commit A:** `feat(shad): B4 Electronic systems chapter + figures (AC mains harmonics + active filter + heterodyne mixer)`

### Phase B — JOB-2 (Pascal port)

Run incrementally; each test-suite-green is a commit boundary.

- [ ] Step B1: kernel + Makefile + `unit DftKernel` interface
- [ ] Step B2: write + green `test_dft_unit.pas` (5 tests at 1e-13)
- [ ] **Commit B1:** `feat(backends/pascal): kernel + unit tests green (5/5)`
- [ ] Step B3: write + green `test_dft_property.pas` (6 tests; P8 = 9.1e-13 documented)
- [ ] **Commit B2:** `feat(backends/pascal): property tests green (6/6 with P8 = 9.1e-13)`
- [ ] Step B4: write + green `test_dft_physics.pas` (14 tests; PT-DFT-03B = 1e-10 documented)
- [ ] **Commit B3:** `feat(backends/pascal): physics testbed green (14/14 with PT-DFT-03B = 1e-10)`
- [ ] Step B5: write + green `test_dft_golden.pas` (6 vectors, ~748 element-checks, Option G gate)
- [ ] **Commit B4:** `feat(backends/pascal): golden vectors green (6/6 vectors, Option G 1e-13*sqrt(N) per element)`
- [ ] Step B6: cross-language verify — Pascal worst-error numbers match Fortran + C++ to within 2.22e-16 (or document delta in STATUS-REPORT)
- [ ] **Tag:** `git tag v0.0.6-pascal-port-green`

### Phase C — JOB-3 (ADR-001)

- [ ] Step C1: draft ADR-001 §"Context" + §"Decision drivers"
- [ ] Step C2: enumerate options in §"Considered options" (Q1 + Q2 + Q3, 3-5 bullets each on pros/cons/cost/risk)
- [ ] Step C3: run POC-1 + POC-2 (timing baselines) — store under `_specs/adr-001-poc/`
- [ ] Step C4: run POC-3 (row-then-column 2D) — store
- [ ] Step C5: run POC-4 (noisy-data robust preprocessing) — store with 3 figures
- [ ] Step C6: write ADR-001 §"Decision" + §"Consequences" + §"Compliance with project principles", informed by POC numbers
- [ ] Step C7: pre-flight grep on ADR + POCs
- [ ] **Commit C:** `docs(adr): ADR-001 perf+noisy+multidim direction (Proposed state; recommendation + 4 POCs)`

### Phase D — Wrap-up

- [ ] Step D1: author `RELEASE-NOTES-v0.2.1.md` mirroring `RELEASE-NOTES-v0.2.0.md` structure
- [ ] **Commit D1:** `docs(release-notes): v0.2.1 RC1 — Pascal port + Shad B4 + ADR-001`
- [ ] Step D2: tag the RC: `git tag v0.2.1-rc1`
- [ ] Step D3: write `_handoffs/macbook-v0.2.x-weekend/STATUS-REPORT-FILLED.md` per template
- [ ] **Commit D2:** `chore(handoff): STATUS-REPORT-FILLED.md for macbook-v0.2.x-weekend`
- [ ] Push everything to `petr-yamyang/VibeCodeProjects` branch `thinkpad`. Do **NOT** push to `lege-artis/fourier` directly — Pete handles the public subtree-push from ThinkPad after reviewing STATUS-REPORT.

---

## §3. Pre-flight grep (run before each commit)

```bash
# From repo root:
cd fourier/

# Sanitization — must return zero
grep -rni -E "supin|bouracka|cap[ck]p|mimt|mim2000|improwave|yamyang|vitez" \
  --include="*.md" --include="*.pas" --include="*.py" --include="*.toml" --include="*.bib" \
  .

# ASCII-only source check (Pascal + Python)
file backends/pascal/src/*.pas backends/pascal/tests/*.pas \
     examples/shad/b4-electronic/main.py \
  2>&1 | grep -v "ASCII text" || true   # this should print nothing if all are ASCII

# SPDX-License-Identifier present on every source file
grep -L "SPDX-License-Identifier" backends/pascal/src/*.pas \
                                  backends/pascal/tests/*.pas \
                                  examples/shad/b4-electronic/main.py
# (empty output = all files OK)
```

Any failure here parks the commit — fix before committing.

---

## §4. Tagging convention

Mid-progress tags (lightweight, no GitHub Release behind them):
- `v0.0.6-pascal-port-green` — after Phase B all green
- (no specific tag for JOB-1 or JOB-3 — they land in the v0.2.1-rc1 tag instead)

End-of-weekend tag (annotated):
- `git tag -a v0.2.1-rc1 -m "v0.2.1 release candidate: Pascal port + Shad B4 + ADR-001"`

Pete handles `v0.2.1` final tag + GitHub Release publication from ThinkPad after reviewing STATUS-REPORT.

---

## §5. What NOT to do

- ❌ Do **NOT** subtree-push to `lege-artis/fourier` from MacBook. Public-flip authority stays on ThinkPad.
- ❌ Do **NOT** rewrite history (no `git rebase -i`, no `git commit --amend` on commits already pushed).
- ❌ Do **NOT** add files outside `fourier/` (governance lives in monorepo `_config/` + `CLAUDE.md` and is ThinkPad-owned).
- ❌ Do **NOT** modify v0.1.0 Fortran kernel or v0.2.0 C++ kernel (locked references).
- ❌ Do **NOT** publish a v0.2.1 GitHub Release. That's Pete's call after reading STATUS-REPORT.

End of OUTPUTS-CHECKLIST.md
