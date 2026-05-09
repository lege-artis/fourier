# lege-artis GitHub org — migration & bootstrap plan v0.1

> **Trigger.** 2026-05-09 — Pete confirmed the new `lege-artis` GitHub org as canonical home for math/logical commons + MI-M-T core. Three-repo target: `lege-artis/mimt`, `lege-artis/fourier`, `lege-artis/kh-sim` (migrated from `petr-yamyang/kh-sim`).
>
> **Audience.** Pete (operator — manual GitHub UI steps); ThinkPad + MacBook devices (post-migration `git remote set-url` rotation); future Cowork sessions referencing repos under the new org.
>
> **Status.** v0.1 draft. Pete reviews + executes; updates with execution-time observations land in v0.2.

---

## §1. Pre-flight checklist (Pete)

| Check | Status (Pete confirms) |
|---|---|
| Pete signed in to github.com as `petr-yamyang` | ☐ |
| `petr-yamyang/kh-sim` has no external links yet (LinkedIn / mim2000.cz / zemla.org) — migration window still open per Track 3 KH-02 not yet executed | ☐ |
| `petr-yamyang/bouracka-tests` is on a separate name and stays on `petr-yamyang/` (it's a case study, not a `lege-artis` repo) | ☐ confirmed by §3 below |
| ThinkPad has a clean working tree on any kh-sim or other affected repos before remote URL rotation | ☐ |
| MacBook has a clean working tree on any kh-sim or other affected repos before remote URL rotation | ☐ |

---

## §2. Step-by-step — org creation (~3 minutes)

1. Open browser, sign in to https://github.com as `petr-yamyang`.
2. Top-right `+` button → **New organisation**.
3. Plan selection: **Free** (sufficient for current scope; can upgrade later if private-repo limits hit).
4. Organization account name: `lege-artis` — enter exactly.
5. Contact email: `petr.yamyang@gmail.com`.
6. "This organization belongs to": choose **My personal account**.
7. Verify email if prompted.
8. Skip the "Invite members" step (Pete is solo owner for now).
9. Confirm at https://github.com/lege-artis — should show empty org page.

**Verification.** `https://github.com/lege-artis/` resolves and shows the empty org listing. No repos yet.

---

## §3. Step-by-step — kh-sim transfer (~5 minutes + per-device URL rotation)

### §3.0 Pre-flight availability check (mandatory)

Before initiating transfer, verify the target slot is unoccupied:

1. Open browser to `https://github.com/lege-artis/kh-sim`.
2. **Expected:** HTTP 404 / "404 — page not found" / GitHub's standard not-found page.
3. **If page resolves to a real repo** (some other party squatted the name during the brief window between org creation and your transfer attempt): **ABORT transfer**. Investigate; consider fallback name `lege-artis/kelvin-helmholtz-sim` or contact GitHub support if the squatter is malicious.
4. If 404 confirmed → proceed to §3.1.

This check costs ~10 seconds and prevents an unrecoverable transfer-rejection error mid-flow.

### §3.1 Transfer the GitHub repo

1. Navigate to `https://github.com/petr-yamyang/kh-sim`.
2. **Settings** tab (top of repo, may need to scroll right).
3. Scroll all the way down to **Danger Zone** section.
4. Click **Transfer ownership**.
5. New owner's account name: `lege-artis`.
6. Type repo name to confirm: `kh-sim`.
7. Click **I understand, transfer this repository**.
8. GitHub redirects you; URL is now `https://github.com/lege-artis/kh-sim`.

**What's preserved.** Issues, PRs, branches (including `kh-sim-public` at `19d7eaa`), tags, stars, watchers, contributors. Old URL `https://github.com/petr-yamyang/kh-sim` redirects to the new one for ~1 year automatically.

### §3.2 Rotate ThinkPad clone

```powershell
cd C:\Users\vitez\Documents\VibeCodeProjects\kh-sim
git remote -v                                          # confirm current origin = petr-yamyang
git remote set-url origin https://github.com/lege-artis/kh-sim.git
git remote -v                                          # confirm new origin = lege-artis
git fetch origin                                       # validate connection works
git branch -a                                          # all remote branches still visible
```

### §3.3 Rotate MacBook clone

```bash
cd ~/Documents/VibeCodeProjects/kh-sim
git remote -v
git remote set-url origin https://github.com/lege-artis/kh-sim.git
git remote -v
git fetch origin
git branch -a
```

### §3.4 Update any documentation references

Files in `VibeCodeProjects/` that may reference `petr-yamyang/kh-sim`:

```bash
# From Linux mount or via PowerShell ripgrep
grep -rln "petr-yamyang/kh-sim" --include="*.md" --include="*.yaml" --include="*.yml" .
# Update each match to lege-artis/kh-sim
```

Notable likely hits: `CLAUDE.md` (current state table), `MANIFEST.yaml`, `3-fold-path/backlog/KH-SIM-PUBLIC-V0.1.md` (Track 3 plan), any session-close docs that mention kh-sim public release.

---

## §4. Step-by-step — `lege-artis/fourier` bootstrap

### §4.1 Create empty repo on GitHub

1. Navigate to `https://github.com/lege-artis`.
2. Click **New repository** (or `+` → New repository, ensuring owner = `lege-artis`).
3. Repository name: `fourier`.
4. Description: `Canonical reference implementation of FFT, DFT, and Numerical Partial Sum of Fourier Series — Fortran reference + C++ performance + Rust experimental. Two-tier docs (canonical math + engineer "Fourier for dummies"). Apache 2.0 + CC-BY-SA-4.0 (docs).`
5. Visibility: **Public** (per Pete's intent — academic / hacker community).
6. Initialize with: ☑ Add a README file, ☑ Add .gitignore (template: `Fortran` if available, otherwise none — replace later), ☑ Choose a license (template: `Apache License 2.0`).
7. Click **Create repository**.

### §4.2 Local clone + bootstrap on ThinkPad

> **Q4 lock 2026-05-09:** Pete runs §4.2 manually as PowerShell script (preserves Pete's authorial signature on first commit of the public OSS repo). Split: §4.1 above = manual GitHub UI clicks; §4.2 below = paste-and-run script in PowerShell.

```powershell
cd C:\Users\vitez\Documents\VibeCodeProjects
git clone https://github.com/lege-artis/fourier.git
cd fourier
# Working spec lives in SUPIN for now — copy across:
cp ..\SUPIN\FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md _specs\WORKING-SPEC-v0.2-EN.md
mkdir _specs, backends, backends\fortran, backends\fortran\src, backends\fortran\tests, docs, docs\canonical, docs\engineer, shared, shared\golden-vectors, shared\reference-bibliography, ci
# Community-pack files (mirror kh-sim's KH-01 deliverables):
# Pull from kh-sim repo as reference:
# Copy CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md from local kh-sim clone
# (manual review + adaptation per the lege-artis branding)
git add .
git commit -m "chore: initial bootstrap from kh-sim community-pack pattern + working spec v0.2"
git push origin main
```

### §4.3 Add `lege-artis`-specific files

Beyond what GitHub auto-created:

| File | Content source |
|---|---|
| `LICENSE-DOCS` | full CC-BY-SA-4.0 text from creativecommons.org |
| `NOTICE` | Apache 2.0 NOTICE: copyright holder, year, project name, reference to TRADEMARK.md |
| `TRADEMARK.md` | Declaration: MIM2000™, Improwave™, Petr Yamyang names not licensed for derivative use; reinforces Apache §6 |
| `.github/FUNDING.yml` | GitHub Sponsors username + Patreon URL + PayPal.me URL (Pete fills before first push) |
| `_specs/WORKING-SPEC-v0.2-EN.md` | Migrated from `SUPIN/FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` (after migration, retire the SUPIN copy) |

---

## §5. Step-by-step — `lege-artis/mimt` bootstrap (deferred to v0.2 → v0.3 transition)

### §5.1 When this happens

Per OPUS-CYCLE v0.2-MASTER.md, the MI-M-T core (currently at `3-fold-path/code/mi_m_t/`, FastAPI service with 25-table schema, D-08 done with SMK9 20/20 PASS, D-09 portability proven, D-10 Active24 deploy bundle ready) packages into its own repo at the **v0.2 → v0.3 transition** — i.e. after the on-prem PoC Track 1 closes (PoC-12 acceptance gate). Not before.

### §5.2 What the bootstrap will involve (preview)

1. Create empty `lege-artis/mimt` repo on GitHub (similar to §4.1).
2. Extract `3-fold-path/code/mi_m_t/` content with full git history (via `git filter-repo` or manual subtree split — TBD per migration session).
3. Push extracted content as initial commit on `main`.
4. Update `3-fold-path/code/` to reference `lege-artis/mimt` as a submodule, OR remove the duplicated content from `3-fold-path/` (decision deferred — Track 1 PoC was using the in-tree path).
5. Update `MANIFEST.yaml`, `CLAUDE.md`, all session-close docs that point at `3-fold-path/code/mi_m_t/` to point at the new location.

**This is non-trivial** and deserves its own dedicated Opus session. Not part of the 2026-05-09 migration scope.

---

## §6. Risk register — migration-specific

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|:-:|:-:|---|
| R-MIG-1 | kh-sim transfer breaks an external link that's not yet known about | L | M | Search Pete's email + zemla.org draft posts for any pre-published link before transfer; abort migration if found |
| R-MIG-2 | ThinkPad or MacBook git pull after URL rotation hits credential cache mismatch (the same failure mode as the bouracka-tests vstembera bug 2026-05-08) | M | L | Document expected prompt + PAT use; use GitHub CLI `gh auth login` for fresh auth before push attempts |
| R-MIG-3 | `lege-artis` org name conflicts with a squatted name | L | H | Verify availability before announcing; if conflict, fallback names: `lege-artis-foundations`, `mim-foundations` |
| R-MIG-4 | GitHub auto-redirect from `petr-yamyang/kh-sim` to `lege-artis/kh-sim` expires before all references updated | L | L | 1-year window is generous; treat ripgrep-and-fix step (§3.4) as immediate post-transfer task |
| R-MIG-5 | Fourier repo bootstrap accidentally commits SUPIN/-only content | L | M | Strict `_specs/WORKING-SPEC-v0.2-EN.md` migration only; nothing else from SUPIN crosses the boundary |
| R-MIG-6 | `lege-artis/mimt` extraction loses git history when split from monorepo | M | M | Use `git filter-repo` (preserves history); validate with `git log --follow` on representative file after split |

---

## §7. Verification checklist — post-migration (Pete confirms each)

- [ ] `https://github.com/lege-artis` exists, listing 1 repo (kh-sim) plus the new fourier repo
- [ ] `git clone https://github.com/lege-artis/kh-sim.git` succeeds on a clean shell with no cached credentials
- [ ] `git clone https://github.com/lege-artis/fourier.git` succeeds same way
- [ ] ThinkPad's local kh-sim repo has `origin` pointing at lege-artis
- [ ] MacBook's local kh-sim repo has `origin` pointing at lege-artis
- [ ] `kh-sim/main` and `kh-sim-public` branches both visible after fetch on both devices
- [ ] `petr-yamyang/kh-sim` URL still redirects (test by clicking once in browser; should land on lege-artis)
- [ ] Documentation references updated (ripgrep returns zero matches for `petr-yamyang/kh-sim` outside of historical/archived files)

---

## §8. Status

| Item | Value |
|---|---|
| Doc | `_config/LEGE-ARTIS-ORG-MIGRATION-PLAN-v0.1.md` |
| Version | v0.1 |
| Date | 2026-05-09 |
| Author | Cowork-Opus on ThinkPad |
| Trigger | Pete's confirmation of `lege-artis` org as canonical home |
| Companion docs | `_config/CLAUDE-MD-DELTA-2026-05-09.md`, `_config/KB-LESSONS-LEARNED.yaml` (KB-036), `4-step-noble-steps to MI-M-T/lege-artis-fourier-bootstrap.md` |
| Sequencing | (1) §2 org creation by Pete → (2) §3 kh-sim transfer + URL rotation → (3) §4 fourier repo bootstrap → (later, v0.2→v0.3) §5 mimt extraction |
| Estimated total effort | ~15-20 minutes for §2-§4 (Pete time); §5 is its own dedicated session |
| Status | Draft — Pete reviews + executes |
