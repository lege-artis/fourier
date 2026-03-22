#!/bin/bash
# MacBook Bootstrap — VibeCodeProjects GitHub Connection
# Run this script on MacBook to set up Git sync with GitHub
# Usage: chmod +x macbook-bootstrap.sh && ./macbook-bootstrap.sh

set -e

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  VibeCodeProjects — MacBook Bootstrap"
echo "  GitHub account: petr-yamyang"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── Step 1: SSH Key Generation ────────────────────────────────────────────────
echo "[1/5] Generating SSH ED25519 key for MacBook..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh

if [ -f ~/.ssh/macbook_github_ed25519 ]; then
    echo "  SSH key already exists at ~/.ssh/macbook_github_ed25519 — skipping generation."
else
    ssh-keygen -t ed25519 -C "MacBook-dev-2026" -f ~/.ssh/macbook_github_ed25519 -N ""
    echo "  Key generated."
fi

chmod 600 ~/.ssh/macbook_github_ed25519
chmod 644 ~/.ssh/macbook_github_ed25519.pub

echo ""
echo "  *** IMPORTANT — Add this public key to GitHub before continuing ***"
echo "  Go to: https://github.com/settings/ssh/new"
echo "  Title: MacBook-dev-2026"
echo "  Key:"
echo ""
cat ~/.ssh/macbook_github_ed25519.pub
echo ""
read -p "  Press Enter after you have added the key to GitHub..."

# ── Step 2: SSH Config ────────────────────────────────────────────────────────
echo ""
echo "[2/5] Configuring SSH..."

SSH_CONFIG="$HOME/.ssh/config"
if grep -q "github.com" "$SSH_CONFIG" 2>/dev/null; then
    echo "  SSH config already has github.com entry — skipping."
else
    cat >> "$SSH_CONFIG" << 'SSHCONF'

Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/macbook_github_ed25519
    IdentitiesOnly yes
SSHCONF
    chmod 600 "$SSH_CONFIG"
    echo "  SSH config updated."
fi

# ── Step 3: Test SSH ──────────────────────────────────────────────────────────
echo ""
echo "[3/5] Testing SSH connection to GitHub..."
SSH_RESULT=$(ssh -T git@github.com 2>&1 || true)
if echo "$SSH_RESULT" | grep -q "successfully authenticated"; then
    echo "  ✓ SSH auth OK: $SSH_RESULT"
else
    echo "  ✗ SSH test failed: $SSH_RESULT"
    echo "  Check that you added the key at https://github.com/settings/keys"
    exit 1
fi

# ── Step 4: Clone Repository ──────────────────────────────────────────────────
echo ""
echo "[4/5] Cloning VibeCodeProjects..."

CLONE_DIR="$HOME/Documents/VibeCodeProjects"
if [ -d "$CLONE_DIR/.git" ]; then
    echo "  Repo already exists at $CLONE_DIR — pulling latest..."
    cd "$CLONE_DIR"
    git fetch origin
    git merge origin/main
else
    git clone git@github.com:petr-yamyang/VibeCodeProjects.git "$CLONE_DIR"
    cd "$CLONE_DIR"
fi

# Configure identity
git config user.name "petr-yamyang"
git config user.email "petr@zemla.org"

echo "  ✓ Cloned to $CLONE_DIR"

# ── Step 5: Create MacBook Branch ─────────────────────────────────────────────
echo ""
echo "[5/5] Setting up macbook branch..."

cd "$CLONE_DIR"
if git show-ref --verify --quiet refs/heads/macbook; then
    echo "  Branch 'macbook' already exists — switching."
    git checkout macbook
    git merge origin/main --no-edit 2>/dev/null || true
else
    git checkout -b macbook
    git push -u origin macbook
    echo "  ✓ Branch 'macbook' created and pushed."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Bootstrap complete!"
echo ""
echo "  Repo location: $CLONE_DIR"
echo "  Active branch: macbook"
echo ""
echo "  Daily sync commands:"
echo "    git fetch origin && git merge origin/main   (pull ThinkPad changes)"
echo "    git add -A && git commit -m 'msg' && git push origin macbook"
echo ""
echo "  Full guide: $CLONE_DIR/_config/MACBOOK-GITHUB-SETUP.md"
echo "═══════════════════════════════════════════════════════════"
echo ""
