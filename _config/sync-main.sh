#!/usr/bin/env bash
# sync-main.sh — Merge gate: integrate macbook + thinkpad branches into main
# Run from either device after a session ends and integrity check passes.
# NEVER push macbook:main or thinkpad:main directly — use this script instead.
#
# Usage:
#   bash _config/sync-main.sh
#
# Git alias (run once per device):
#   git config --global alias.sync-main '!bash ~/Documents/VibeCodeProjects/_config/sync-main.sh'
#   Then: git sync-main

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${CYAN}[sync-main]${NC} $*"; }
ok()   { echo -e "${GREEN}[sync-main] ✓${NC} $*"; }
warn() { echo -e "${YELLOW}[sync-main] ⚠${NC} $*"; }
fail() { echo -e "${RED}[sync-main] ✗${NC} $*"; exit 1; }

# ── 0. Pre-flight ─────────────────────────────────────────────────────────────
log "Pre-flight checks..."

if ! git diff --quiet 2>/dev/null; then
  fail "Uncommitted changes detected. Commit or stash before syncing."
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log "Current branch: ${BOLD}${CURRENT_BRANCH}${NC}"

# ── 1. Integrity check ────────────────────────────────────────────────────────
log "Running task integrity checks..."
if command -v pytest &>/dev/null; then
  if ! pytest _tests/test_task_integrity.py -q --tb=short 2>&1; then
    fail "Integrity check failed. Fix violations before syncing to main."
  fi
  ok "Integrity check passed."
else
  warn "pytest not found — skipping local integrity check. CI will validate on push."
fi

# ── 2. Fetch all ──────────────────────────────────────────────────────────────
log "Fetching all remotes..."
git fetch --all --prune
ok "Fetch complete."

# ── 3. Merge macbook branch ───────────────────────────────────────────────────
log "Switching to main..."
git checkout main
git pull --rebase origin main

log "Merging origin/macbook → main..."
# queue-macbook.yaml: always keep incoming macbook version
# TASKS-shared.yaml: semantic merge driver handles it
git merge --no-ff origin/macbook \
  --strategy-option=ours \
  --no-edit \
  -m "sync: merge macbook → main [$(date +%Y-%m-%d)]" || {

  # If merge=ours strategy conflicted on shared files, resolve manually
  warn "Merge conflict on shared files — applying file-level ownership rules..."
  git checkout origin/macbook -- queue-macbook.yaml 2>/dev/null || true
  # TASKS-shared.yaml was handled by merge driver via .gitattributes
  git add -A
  git commit --no-edit -m "sync: resolve ownership conflicts — macbook→main [$(date +%Y-%m-%d)]"
}
ok "macbook merged into main."

# ── 4. Merge thinkpad branch ──────────────────────────────────────────────────
THINKPAD_REF=$(git ls-remote origin thinkpad | cut -f1)
if [ -n "$THINKPAD_REF" ]; then
  log "Merging origin/thinkpad → main..."
  git merge --no-ff origin/thinkpad \
    --strategy-option=ours \
    --no-edit \
    -m "sync: merge thinkpad → main [$(date +%Y-%m-%d)]" || {

    warn "Merge conflict on shared files — applying file-level ownership rules..."
    git checkout origin/thinkpad -- queue-thinkpad.yaml 2>/dev/null || true
    git add -A
    git commit --no-edit -m "sync: resolve ownership conflicts — thinkpad→main [$(date +%Y-%m-%d)]"
  }
  ok "thinkpad merged into main."
else
  warn "origin/thinkpad not found — skipping thinkpad merge."
fi

# ── 5. Update MANIFEST.yaml ───────────────────────────────────────────────────
log "Updating MANIFEST.yaml sync anchor..."
SYNC_COMMIT=$(git rev-parse --short HEAD)
SYNC_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Inline sed update — portable across macOS + Linux
if [[ "$(uname)" == "Darwin" ]]; then
  sed -i '' "s/^last_sync:.*/last_sync: \"${SYNC_TS}\"/" MANIFEST.yaml
  sed -i '' "s/^last_sync_commit:.*/last_sync_commit: \"${SYNC_COMMIT}\"/" MANIFEST.yaml
  sed -i '' "s/^synced_by:.*/synced_by: \"sync-main.sh [${CURRENT_BRANCH}]\"/" MANIFEST.yaml
else
  sed -i "s/^last_sync:.*/last_sync: \"${SYNC_TS}\"/" MANIFEST.yaml
  sed -i "s/^last_sync_commit:.*/last_sync_commit: \"${SYNC_COMMIT}\"/" MANIFEST.yaml
  sed -i "s/^synced_by:.*/synced_by: \"sync-main.sh [${CURRENT_BRANCH}]\"/" MANIFEST.yaml
fi

git add MANIFEST.yaml
git diff --staged --quiet || git commit -m "chore(manifest): update sync anchor [${SYNC_COMMIT}]"
ok "MANIFEST.yaml updated."

# ── 6. Push main ──────────────────────────────────────────────────────────────
log "Pushing main to origin..."
git push origin main
ok "main pushed: $(git rev-parse --short HEAD)"

# ── 7. Return to working branch ───────────────────────────────────────────────
git checkout "$CURRENT_BRANCH"
ok "Back on ${BOLD}${CURRENT_BRANCH}${NC}."

echo ""
echo -e "${GREEN}${BOLD}sync-main complete.${NC}"
echo -e "  main:     $(git rev-parse --short origin/main)"
echo -e "  macbook:  $(git rev-parse --short origin/macbook 2>/dev/null || echo 'n/a')"
echo -e "  thinkpad: $(git rev-parse --short origin/thinkpad 2>/dev/null || echo 'n/a')"
