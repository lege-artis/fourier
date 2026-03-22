#!/bin/bash
# GitHub workspace initialisation script
# Run AFTER: SSH key has been added to github.com/petr-yamyang
# Run AFTER: PAT has been generated and saved to ~/.github_pat.enc
#
# Usage: bash github-init.sh <github-repo-name>
# Example: bash github-init.sh VibeCodeProjects

set -e

REPO_NAME="${1:-VibeCodeProjects}"
GH_USER="petr-yamyang"
WORKSPACE="/sessions/funny-zen-pascal/mnt/VibeCodeProjects"

echo "=== GitHub Workspace Init ==="
echo "User:      $GH_USER"
echo "Repo:      $REPO_NAME"
echo "Workspace: $WORKSPACE"
echo ""

# ── 1. Test SSH connection ────────────────────────────────────────────────────
echo "[1/5] Testing SSH connection to GitHub..."
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && \
  echo "  ✅ SSH authentication OK" || \
  { echo "  ❌ SSH auth failed — check that key is added at github.com/settings/keys"; exit 1; }

# ── 2. Initialise git repo if not already ────────────────────────────────────
echo "[2/5] Initialising git repository..."
cd "$WORKSPACE"
if [ ! -d ".git" ]; then
  git init
  echo "  ✅ Git repository initialised"
else
  echo "  ℹ  Git repo already exists — skipping init"
fi

# ── 3. Add remote origin ─────────────────────────────────────────────────────
echo "[3/5] Configuring remote origin..."
if git remote get-url origin 2>/dev/null; then
  echo "  ℹ  Remote 'origin' already set"
else
  git remote add origin "git@github.com:$GH_USER/$REPO_NAME.git"
  echo "  ✅ Remote added: git@github.com:$GH_USER/$REPO_NAME.git"
fi

# ── 4. Initial commit ─────────────────────────────────────────────────────────
echo "[4/5] Creating initial commit..."
git add .gitignore _config/ _sync/ _templates/ TASKS.yaml .github/ 2>/dev/null || true
git add "platform sources/" databases/ sandboxes/ Generic/ 2>/dev/null || true
git status --short | head -20

git diff --cached --quiet && \
  echo "  ℹ  Nothing to commit" || \
  git commit -m "chore: ThinkPad workspace scaffold — $(date +%Y-%m-%d)

- Infrastructure audit and config docs
- Platform hello-world test files (C++, Rust, Scala, Fortran, Pascal, React)
- GitHub Actions CI/CD heartbeat workflow (all platforms + Chrome/Firefox)
- Database configs (PostgreSQL, MongoDB)
- LibreOffice D:\\ migration script
- Fallback/rollback protocol
- SSH setup guide
- Windows dev environment setup script"

# ── 5. Push to GitHub ─────────────────────────────────────────────────────────
echo "[5/5] Pushing to GitHub..."
git push -u origin main && \
  echo "  ✅ Pushed to github.com/$GH_USER/$REPO_NAME" || \
  echo "  ⚠  Push failed — create repo at github.com/new first, then re-run"

echo ""
echo "=== Init complete ==="
echo "Next: MacBook can clone with: git clone git@github.com:$GH_USER/$REPO_NAME.git"
