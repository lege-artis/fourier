# MacBook weekend briefcase — Fourier v0.2.x (Shad-tier B4 + Rust port)

**Status:** Ready to delegate
**Author:** Petr Yamyang (ThinkPad/Opus session 2026-05-11)
**Target executor:** Any MacBook Cowork session — Opus orchestrating Sonnet sub-sessions, or a single Opus pass for the chapter + a single Sonnet pass for the port
**Locks-in version:** lege-artis/fourier v0.2.0 PUBLIC (Fortran + C++ both green at bit-identical worst-error numbers)
**Goal:** drive lege-artis/fourier from v0.2.0 → v0.2.1-rc1 (3 backends green; first engineer-tier Electronic-systems chapter shipped) + lock direction for v0.3+ (ADR-001)
**Why this brief exists:** ThinkPad is fully committed to Bouračka HP Elite delivery today. This briefcase ships the next Fourier weekend cut as a self-contained packet MacBook can run independently — no live coordination needed.
**License:** Apache-2.0 (same as the project)

---

## §0. Read these first (in order)

These files contain everything you need. **Do not re-derive what they already specify.**

1. `_specs/SONNET-HANDOFF-v0.2.0-CPP-PORT.md` — the proven port handoff template, validated end-to-end for C++. Sections §0 (read-first list), §1 (implementation discipline — ASCII-only, equation-to-code mapping, build-flag conformance), §1.1 (port-specific constraints — translate canonical equation directly, NOT Fortran-syntax-to-target-syntax), §3 (tolerance gates) **all apply identically to Rust** with the language-specific adaptations listed in JOB-2.
2. `_specs/SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md` — original Stage-4 handoff; sections §5 (out of scope), §6 (cross-job context), §7 (failure-mode escalation) apply unchanged.
3. `_specs/WORKING-SPEC-v0.3-EN.md` — implementation philosophy + three doc tiers (canonical / engineer / Shad). Stage 5 (performance) is **gated v0.5+** and out of scope here.
4. `_specs/PLANNED-SHADDACK-TIER-SCOPE-v0.1.md` — the linear B1→B7 Shad-tier plan. B4 Electronic is your authoring target in JOB-1.
5. `docs/shad/03-vibration.md` — the latest Shad-tier exemplar (B3). Mirror its narrative structure, density, and figure cadence in B4.
6. `examples/shad/b3-vibration/main.py` — the latest Shad-tier exemplar script. Mirror its docstring, imports, figure-output convention.
7. `backends/cpp/Makefile` + `backends/cpp/include/lege_artis_fourier/dft_kernel.hpp` + `backends/cpp/src/dft_kernel.cpp` + `backends/cpp/tests/*` — proven C++ port. Your Rust port mirrors this layout idiomatically.
8. `shared/canonical-equations/dft.md` — Eq. DFT-1; the **only** authoritative source for what the algorithm computes.
9. `RELEASE-NOTES-v0.2.0.md` — what shipped last; sets the tone + framing for v0.2.1 release notes you'll author at the end.

Optional but useful:
- `_config/KB-LESSONS-LEARNED.yaml` entries KB-037 through KB-041 — five build-chain / numerical / process traps already eaten. Don't re-eat them.
- `_specs/SONNET-CLOSE-v0.1.0-RC-2026-05-10.md` — the close-out template that drove v0.1.0 PUBLIC; informs the shape of `STATUS-REPORT-FILLED.md` you'll write at the end of the weekend.

---

## §1. Scope — Option B locked (REVISED 2026-05-11)

Pete overrode the original Rust-port plan in favor of **Pascal**, citing: (a) the Numerical Recipes 1986 Pascal-edition historical anchor, (b) personal nostalgia (first language he learned in depth), (c) cross-check value — three independent linguistic translations of Eq. DFT-1 (Fortran + C++ + Pascal) producing bit-identical worst-error numbers is much stronger evidence of equation-fidelity than two (Fortran + C++) plus a third in a related language paradigm. Rust port queued for v0.2.2 after Pascal proves the 3-way pattern.

Pete also added a JOB-3 scoping spike for performance + multidim + noisy-data direction-setting. Framed as a decision-document deliverable (ADR-001), not a code rollout. Constraint: stays inside the existing Stage 5 / v0.5+ gating philosophy.

| Job | Deliverable | Estimated effort | Owner-pattern |
|-----|-------------|------------------|---------------|
| **JOB-1** | Shad-tier B4 — Electronic systems chapter (`docs/shad/04-electronic.md`) + example script (`examples/shad/b4-electronic/main.py`) + 3 figures + new citations appended to `shared/reference-bibliography/refs.bib` | ~2-3 hours authoring | Opus-quality narrative; Sonnet fine for the script + figures if delegated |
| **JOB-2** | Pascal port at `backends/pascal/` — kernel + 4 test programs (unit + property + physics + golden) + Makefile, green at the same tolerance gates as Fortran + C++ | ~4-6 hours implementation + debug | Sonnet-suitable; mirrors C++ port effort, plus FPC idiom adaptations |
| **JOB-3** | `_specs/ADR-001-PERF-NOISY-MULTIDIM-v0.1.md` + `_specs/adr-001-poc/` (4 small POCs) — answers the perf / multidim / noisy-data scope question for v0.3+ direction | ~2-4 hours analysis + POC numbers | Opus-quality decision-doc (the analysis is the deliverable); Sonnet OK for POC measurement |

All three jobs are independent. Run in parallel if you have two or three Cowork sub-sessions; run sequentially otherwise. **Suggested order if sequential:** JOB-1 first (lowest dependency, highest reader-impact), JOB-3 second (informs sequencing for the rest of v0.3+), JOB-2 last (most code, can be hand-paused mid-job without leaving the repo in a bad state — committable per test-suite-green checkpoint).

**OUT of scope for this weekend:**
- Rust port (queued for v0.2.2 — once Pascal lands, the 3-way cross-language baseline is in place and Rust can be added as a 4-way verification)
- Shad-tier B5+ chapters (Radar, Radioastronomy, Nuclear-reactor capstone — queued for v0.2.x point releases)
- Stage 5 performance builds (gated v0.5+; ADR-001 informs sequencing but doesn't pull the gate forward)
- Actual implementation of FFTW integration or native 2D DFT in v0.2.x backends (v0.3+ work, gated by ADR-001 acceptance)
- Translations of B1-B4 to CS / JA / DE / IT (queued for v0.1.1+)
- Any changes to canonical equations or the Fortran reference (locked at v0.1.0)
- GW-solver-project work (parallel project; separate briefcase when ready)

---

## §2. Implementation discipline (NON-NEGOTIABLE)

These rules are project-wide and have been validated by the v0.1.0 + v0.2.0 cuts. Re-read §1 of `SONNET-HANDOFF-v0.2.0-CPP-PORT.md`; everything there applies.

Cliff-notes:

- **ASCII-only source files** (KB-039). No Unicode in `.rs`, `.toml`, `.py`, `.md` source-code blocks. Narrative prose in `docs/shad/04-electronic.md` may use Unicode for readability (em-dash, multiplication sign, etc. — match the B3 exemplar style).
- **Equation-to-code mapping** in module header comments. Every implementation file opens with a doc-comment block mapping math expressions to specific code lines.
- **Translate the canonical equation directly into idiomatic target-language code.** Do NOT translate Fortran or C++ syntactically into Rust. The implementation philosophy is "canonical equation → code", not "Fortran → Rust" or "C++ → Rust".
- **No third-party FFT libraries.** Specifically: NO `rustfft`, NO `realfft`. The Rust port is a reference implementation of Eq. DFT-1, same as the Fortran and C++ kernels. External-library use is forbidden in v0.1.x/v0.2.x per WORKING-SPEC §4.
- **Clarity flags, NOT performance flags.** Stage 5 (`-O3 -march=native`) is gated v0.5+ and out of scope. Build profile for the reference is debug + release-no-LTO. See JOB-2 §4.

---

## §3. Output channels

**Default safe pattern** (mirrors v0.2.0):
- All commits to monorepo `petr-yamyang/VibeCodeProjects` branch `thinkpad` under the `fourier/` subtree
- Public flip to `lege-artis/fourier` is **NOT** done from MacBook — Pete subtree-pushes from ThinkPad when next at the device, after reviewing the green state
- Tag points to lock at green: `v0.0.6-rust-port-green` after JOB-2 passes all gates; `v0.0.7-shad-b4-shipped` after JOB-1 figures + chapter are committed; `v0.2.1-rc1` once both are green and `STATUS-REPORT-FILLED.md` is written

**Commit cadence** — one commit per logical step, NOT one commit per file. Suggested boundaries:
1. `feat(shad): B4 Electronic chapter narrative + figure-generating script` (JOB-1 lands together)
2. `feat(backends/pascal): kernel + unit tests green` (JOB-2 step 1)
3. `feat(backends/pascal): property tests green` (JOB-2 step 2)
4. `feat(backends/pascal): physics testbed + golden vectors green` (JOB-2 step 3)
5. `docs(adr): ADR-001 perf+noisy+multidim direction (recommendation + POCs)` (JOB-3 lands together)
6. `docs(release-notes): v0.2.1 RC1 — Pascal port + Shad B4 + ADR-001`
7. `chore(handoff): STATUS-REPORT-FILLED.md`

Commit messages follow the Conventional Commits prefix style already in the log (`feat(scope):`, `fix(scope):`, `docs(scope):`, `chore(scope):`).

---

## §4. Decision authority — what MacBook decides vs. what ThinkPad locks

**MacBook can decide independently:**
- Wording, examples, figure aesthetics in B4
- Rust idioms — `Vec<Complex64>` vs `[Complex64; N]`, error handling style (panic vs Result for kernel — recommend panic, see JOB-2 §1.1), module structure
- Specific citation choices for B4 (so long as they're real, reachable, and authoritative; see JOB-1 §6)
- Order of execution between JOB-1 and JOB-2 (run either first)

**MacBook escalates to ThinkPad (write to `STATUS-REPORT-FILLED.md`, do NOT publish until Pete confirms):**
- Any deviation from gate values (1e-13 unit/property, Option G `1e-13·sqrt(N)` for golden, P8 9.1e-13, PT-DFT-03B 1e-10) — these are bit-identity-meaningful and stay locked
- Any change to canonical equations
- Any inclusion of a third-party FFT library in JOB-2 (FORBIDDEN per §2; if you think it's needed, you've misread the project — re-read WORKING-SPEC §4)
- Any change to the project's license stack (Apache-2.0 code + CC-BY-SA-4.0 docs + NOTICE/TRADEMARK)
- Any use of `inline assembler` or platform-specific intrinsics in the Pascal kernel (the reference is portable FPC; if you think you need them, escalate — this is Stage 5 / v0.5+ scope)
- Any JOB-3 decision that pulls Stage 5 perf work into v0.2.x or v0.3 without an explicit ADR-001 §"Decision" sentence justifying it
- Anything that would require changes outside `fourier/` (project-wide governance lives in monorepo `_config/` + `CLAUDE.md`)

---

## §5. Sanitization rules (pre-publication)

Same as the v0.1.0 + v0.2.0 cuts. The `fourier/` subtree publishes to `lege-artis/fourier` PUBLIC, so anything entity-tying must be scrubbed.

**Forbidden in any file under `fourier/`:**
- `SUPIN`, `Bouračka`, `Bouracka`, `ČKP`, `CKP`, `MI-M-T`, `MIM2000`, `Improwave`, `Petr Yamyang` (real name; use `Petr Y.` or just `Pete` if unavoidable)
- Any reference to client work, internal tooling, internal hostnames
- Any path containing `\\Users\\vitez\\` or `/sessions/sleepy-amazing-clarke/`

**Allowed:**
- `lege-artis/fourier` (the public org/project name)
- `kh-sim`, `fourier` (sibling math-commons projects)
- Generic Czech words in citations (`Vetterling` is a real name; `bouracka` would be a project-specific term)

Pre-flight grep before commit:
```bash
cd fourier/
grep -rni -E "supin|bouracka|cap[ck]p|mimt|mim2000|improwave|yamyang|vitez" \
  --include="*.md" --include="*.rs" --include="*.toml" --include="*.py" .
# Expected: zero hits
```

---

## §6. Reporting back

At the end of the weekend (or whenever you park the session), write a status report to `fourier/_handoffs/macbook-v0.2.x-weekend/STATUS-REPORT-FILLED.md` using the template at `STATUS-REPORT-TEMPLATE.md`. Commit it. Push.

The status report is **the** signal back to ThinkPad. Pete reads it on next session and decides:
- Whether to subtree-push to `lege-artis/fourier` PUBLIC
- Whether to tag `v0.2.1` final
- Whether to publish a GitHub Release
- Whether the work needs another iteration

**Be honest in the status report.** "Got 3/4 test suites green, golden-vector test still off by 2.3e-12 on N=4096, see §X for details" is infinitely more useful than "all done, ship it" when reality is murky.

---

## §7. Done criteria for the weekend cut

The weekend is "done" when **all** of these are true:

- [ ] JOB-1: `docs/shad/04-electronic.md` exists, reads end-to-end at the same density as `03-vibration.md`, references 3 figures generated by `examples/shad/b4-electronic/main.py`, cites real published sources from `refs.bib`.
- [ ] JOB-1: `examples/shad/b4-electronic/main.py` runs end-to-end on a fresh checkout (`python main.py`), produces the 3 figures, no Unicode issues on Windows/Mac/Linux (test on at least one).
- [ ] JOB-1: New citations appended to `shared/reference-bibliography/refs.bib`, each verifiable (DOI / ISBN / authoritative URL).
- [ ] JOB-2: `make -C backends/pascal test` passes 4/4 suites at the locked gates (1e-13 unit + property; physics PT-DFT-03B 1e-10; golden Option G `1e-13*sqrt(N)`).
- [ ] JOB-2: Pascal kernel produces **bit-identical** worst-error numbers to Fortran + C++ reference for the same input vectors (the 3-way cross-language baseline match — see JOB-2 §3 for what "bit-identical" means in IEEE-754 terms; allow ±2.22e-16 = 1 ULP for `Cos`/`Sin` runtime variance).
- [ ] JOB-3: `_specs/ADR-001-PERF-NOISY-MULTIDIM-v0.1.md` committed in Proposed state, all template sections (Context / Decision drivers / Considered options / Decision / Consequences / Compliance) filled in defensibly. 4 POCs reproducible at `_specs/adr-001-poc/`.
- [ ] All jobs: clean ASCII-only source files, equation-to-code header mapping, Apache-2.0 SPDX line in every source file.
- [ ] `RELEASE-NOTES-v0.2.1.md` authored mirroring `RELEASE-NOTES-v0.2.0.md` shape.
- [ ] `STATUS-REPORT-FILLED.md` committed with all sections filled.
- [ ] Pre-flight sanitization grep clean.
- [ ] Final commit pushed to monorepo `thinkpad` branch + tags applied.

Anything NOT on this list = not in scope for the weekend. Park it in `STATUS-REPORT-FILLED.md` §"Carried forward" and Pete will sequence in a future weekend cut.

---

## §8. If something goes wrong

Same protocol as the C++ port:
- If a tolerance gate fails, **first** assume you've mis-implemented the equation. Re-read `shared/canonical-equations/dft.md`. The gate is empirically set against the Fortran reference; if Fortran passes and Rust doesn't, Rust has the bug.
- If a build error baffles, check KB-037/038/039/040/041 — odds are good it's already been catalogued.
- If you've burned >30 min on the same failure mode, park it cleanly in `STATUS-REPORT-FILLED.md` §"Open blockers" with: what you tried, what the error says, what your hypothesis is. Do NOT keep grinding — the human gets more value from a clean parked-state than from sunk-cost completion.

End of MASTER-BRIEF.md
