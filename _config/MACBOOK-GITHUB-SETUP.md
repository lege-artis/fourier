# MacBook — GitHub Connection Setup Guide
**Project:** VibeCodeProjects
**GitHub account:** petr-yamyang
**Target repo:** github.com/petr-yamyang/VibeCodeProjects (private)
**Generated:** 2026-03-22 | ThinkPad session

---

## Overview

This guide gets the MacBook connected to the shared GitHub repository so both devices
can push/pull project documentation, task lists, and configuration files.

**What you will do:**
1. Generate a new SSH ED25519 key on MacBook
2. Register the public key on GitHub
3. Clone the repository
4. Configure the macbook branch
5. Verify sync

---

## Step 1 — Generate SSH Key on MacBook

Open Terminal on MacBook and run:

```bash
# Generate ED25519 keypair
ssh-keygen -t ed25519 -C "MacBook-dev-2026" -f ~/.ssh/macbook_github_ed25519

# When prompted for passphrase: press Enter (no passphrase) for frictionless CI/CD
# Or set a passphrase if you prefer extra security

# Verify key was created
ls -la ~/.ssh/macbook_github_ed25519*
# Expected output:
#   ~/.ssh/macbook_github_ed25519      (private key)
#   ~/.ssh/macbook_github_ed25519.pub  (public key)

# Display the public key (you will paste this into GitHub)
cat ~/.ssh/macbook_github_ed25519.pub
```

Copy the full output of the `cat` command — it will look like:
```
ssh-ed25519 AAAA...long string... MacBook-dev-2026
```

---

## Step 2 — Register Public Key on GitHub

### Option A — Via browser (recommended)

1. Open browser → go to: https://github.com/settings/ssh/new
2. Sign in as **petr-yamyang** (email: petr@zemla.org)
3. Fill in:
   - **Title:** `MacBook-dev-2026`
   - **Key type:** Authentication Key
   - **Key:** paste the full output from Step 1
4. Click **Add SSH key**

### Option B — Via GitHub CLI (if `gh` is installed on MacBook)

```bash
# Authenticate gh CLI first
gh auth login --web

# Then add the key
gh ssh-key add ~/.ssh/macbook_github_ed25519.pub --title "MacBook-dev-2026"
```

---

## Step 3 — Configure SSH on MacBook

```bash
# Create or edit SSH config
nano ~/.ssh/config
```

Add this block (or append if config already exists):

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/macbook_github_ed25519
    IdentitiesOnly yes
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano).

```bash
# Lock down key permissions (required by SSH)
chmod 600 ~/.ssh/macbook_github_ed25519
chmod 644 ~/.ssh/macbook_github_ed25519.pub

# Test the connection
ssh -T git@github.com
# Expected response:
# Hi petr-yamyang! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## Step 4 — Clone the Repository

```bash
# Navigate to your Documents (or preferred location)
cd ~/Documents

# Clone via SSH
git clone git@github.com:petr-yamyang/VibeCodeProjects.git

# Enter the repo
cd VibeCodeProjects

# Configure git identity
git config user.name "petr-yamyang"
git config user.email "petr@zemla.org"

# Verify remote
git remote -v
# Expected:
#   origin  git@github.com:petr-yamyang/VibeCodeProjects.git (fetch)
#   origin  git@github.com:petr-yamyang/VibeCodeProjects.git (push)
```

---

## Step 5 — Create MacBook Branch

```bash
# Create and switch to MacBook branch
git checkout -b macbook

# Push branch to remote
git push -u origin macbook

# Verify branches
git branch -a
# Expected:
#   * macbook
#     main
#     remotes/origin/main
#     remotes/origin/macbook
```

---

## Step 6 — Daily Sync Workflow

### Pull latest from main (start of session)
```bash
cd ~/Documents/VibeCodeProjects
git checkout macbook
git fetch origin
git merge origin/main          # merge ThinkPad changes into your branch
```

### Push your work
```bash
git add -A
git commit -m "feat: [description] — MacBook session YYYY-MM-DD"
git push origin macbook
```

### Merge macbook → main (when deliverable is ready)
```bash
git checkout main
git merge macbook
git push origin main
git checkout macbook           # switch back to working branch
```

---

## Step 7 — Set Up gh CLI (Optional but Recommended)

`gh` CLI allows creating GitHub Releases, managing Actions, and uploading theme archives directly.

```bash
# Install via Homebrew
brew install gh

# Authenticate
gh auth login
# Choose: GitHub.com → SSH → select your macbook_github_ed25519 key → authenticate via browser

# Verify
gh auth status
# Expected: Logged in to github.com as petr-yamyang

# Create a release (example for zemla v1.6.3 hotfix)
gh release create v1.6.3 \
  --repo petr-yamyang/zemla \
  --title "v1.6.3 — HOTFIX GAL-D01 Gallery Layout" \
  --notes-file 3-fold-path/releases/RELEASE-zemla-v1.6.3-HOTFIX-GAL-D01.md \
  zemla-theme-v1.6.3.zip
```

---

## Repository Structure Reference

Once cloned, you will find:

```
VibeCodeProjects/
├── TASKS.yaml                          ← Master cross-device task list (v1.2.0)
├── .github/workflows/ci-heartbeat.yml ← 9-job CI/CD heartbeat (runs every 6h)
├── .gitignore
├── _config/
│   ├── DEVICES.md                      ← Device role matrix
│   ├── INFRA_AUDIT.md                  ← Infrastructure audit
│   ├── FALLBACK_PROTOCOL.md            ← Rollback procedures
│   ├── MACBOOK-GITHUB-SETUP.md         ← This file
│   ├── github-ssh-setup.md             ← SSH key registration reference
│   └── windows-setup.ps1               ← ThinkPad tool installer
├── 3-fold-path/
│   ├── backlog/                        ← PROJECT-PLAN + MOB-E01 epic
│   ├── hotfix/                         ← GAL-D01 defect report + bug
│   ├── releases/                       ← Release notes (zemla/mim2000/bodyterapie)
│   └── theme-archives/ARCHIVES-MANIFEST.md
├── 8gsp/
│   └── 8GSP-SESSION-HANDOFF-2026-03-21.md
├── databases/
│   ├── PostgreSQL/config.yaml
│   └── MongoDB/config.yaml
├── platform sources/
│   ├── C++/
│   ├── Fortran/
│   ├── Pascal/
│   ├── React/
│   ├── Rust/
│   └── Scala/
└── _sync/README.md                     ← Sync protocol reference
```

---

## PAT (Personal Access Token) — Optional

For GitHub API access (uploading releases, managing Actions secrets) without the browser:

```bash
# On MacBook — generate a new PAT at:
# https://github.com/settings/tokens/new
# Scopes: repo, workflow, read:org, admin:public_key
# Name: MacBook-vibedev-2026

# Store encrypted (same pattern as ThinkPad)
openssl rand -hex 32 > ~/.pat_key_mac.env
chmod 600 ~/.pat_key_mac.env

# Encrypt the PAT (replace YOUR_PAT with the actual token)
echo "YOUR_PAT" | openssl enc -aes-256-cbc -pbkdf2 \
  -pass file:~/.pat_key_mac.env \
  -out ~/.github_pat_mac.enc

# Decrypt when needed
openssl enc -d -aes-256-cbc -pbkdf2 \
  -pass file:~/.pat_key_mac.env \
  -in ~/.github_pat_mac.enc

# Use with gh CLI
export GH_TOKEN=$(openssl enc -d -aes-256-cbc -pbkdf2 \
  -pass file:~/.pat_key_mac.env -in ~/.github_pat_mac.enc)
```

> **Never commit** `~/.pat_key_mac.env` or `~/.github_pat_mac.enc` — already excluded in `.gitignore`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Permission denied (publickey)` | SSH config not pointing to correct key | Check `~/.ssh/config` — IdentityFile path |
| `Repository not found` | SSH key not registered on GitHub | Repeat Step 2 |
| `WARNING: UNPROTECTED PRIVATE KEY` | File permissions too open | `chmod 600 ~/.ssh/macbook_github_ed25519` |
| `git pull` conflicts on TASKS.yaml | Both devices edited same file | Use `git mergetool` or manually reconcile |
| `gh: command not found` | gh CLI not installed | `brew install gh` |

---

*Reference: `_sync/README.md` for full dual-device sync protocol*
*ThinkPad config: `_config/github-ssh-setup.md`*
