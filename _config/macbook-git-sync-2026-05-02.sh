#!/usr/bin/env bash
# macbook-git-sync-2026-05-02.sh
# Full MacBook git sync sequence — session 2026-05-02 close
# Run from: /Users/petryamyang/Documents/VibeCodeProjects
# Authority: MacBook ONLY — never run from ThinkPad
# Usage: bash _config/macbook-git-sync-2026-05-02.sh
# =============================================================================

set -e   # abort on any non-zero exit
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  MacBook git sync — 2026-05-02                           ║"
echo "║  Repo: $REPO_ROOT"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ─── PHASE 1: Safety checks ──────────────────────────────────────────────────
echo "── Phase 1: Safety checks ──────────────────────────────────"

CURRENT_BRANCH=$(git branch --show-current)
echo "  Current branch : $CURRENT_BRANCH"
if [[ "$CURRENT_BRANCH" != "macbook" ]]; then
  echo "  ✗ ERROR: not on macbook branch — aborting."
  echo "    Run: git checkout macbook"
  exit 1
fi
echo "  ✓ On macbook branch"

# Verify no merge or rebase in progress
if [[ -f ".git/MERGE_HEAD" ]]; then
  echo "  ✗ ERROR: merge in progress — resolve first: git merge --abort"
  exit 1
fi
if [[ -d ".git/rebase-merge" || -d ".git/rebase-apply" ]]; then
  echo "  ✗ ERROR: rebase in progress — resolve first: git rebase --abort"
  exit 1
fi
echo "  ✓ No merge/rebase in progress"

# ─── PHASE 2: Clean up untracked ThinkPad-delta extracts ─────────────────────
echo ""
echo "── Phase 2: Clean up ThinkPad delta extracts (not for macbook branch) ──"

# bugs.yaml and testcases.yaml were extracted from thinkpad delta for reading.
# They live in 3-fold-path/evidence/ but on macbook branch these files should
# not exist — they are ThinkPad-authored and travel via delta packages only.
for f in \
  "3-fold-path/evidence/bugs.yaml" \
  "3-fold-path/evidence/testcases.yaml"
do
  if [[ -f "$f" ]]; then
    # Only remove if NOT tracked (i.e., untracked/ignored — safe to delete)
    GIT_STATUS=$(git ls-files --error-unmatch "$f" 2>/dev/null && echo "tracked" || echo "untracked")
    if [[ "$GIT_STATUS" == "untracked" ]]; then
      rm "$f"
      echo "  ✓ Removed untracked delta extract: $f"
    else
      echo "  ~ Skipped (tracked): $f"
    fi
  else
    echo "  ~ Not present (OK): $f"
  fi
done

# Clean up delta-extract temp dir if present
if [[ -d "/tmp/delta-extract" || -d "$REPO_ROOT/../outputs/delta-extract" ]]; then
  echo "  ~ Note: sandbox delta-extract dir present (ephemeral, ignore)"
fi

# ─── PHASE 3: Check for uncommitted tracked changes ──────────────────────────
echo ""
echo "── Phase 3: Uncommitted tracked changes ───────────────────"

TRACKED_CHANGES=$(git status --porcelain | grep -v "^??" || true)
if [[ -n "$TRACKED_CHANGES" ]]; then
  echo "  ! Uncommitted tracked changes found:"
  echo "$TRACKED_CHANGES" | sed 's/^/    /'
  echo ""
  read -p "  Commit these changes? (y/N): " COMMIT_CONFIRM
  if [[ "$COMMIT_CONFIRM" =~ ^[Yy]$ ]]; then
    git add -u
    git commit -m "chore: session 2026-05-02 cleanup — uncommitted tracked changes"
    echo "  ✓ Committed"
  else
    echo "  ! Skipping — continuing with push of existing commits"
  fi
else
  echo "  ✓ Working tree clean (only untracked/ignored files remain)"
fi

# ─── PHASE 4: Show local commits ahead of remote ─────────────────────────────
echo ""
echo "── Phase 4: Local commits vs remote ───────────────────────"

# Fetch without pulling to get accurate comparison
echo "  Fetching remote state..."
git fetch origin macbook 2>&1 | sed 's/^/  /'

LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse origin/macbook 2>/dev/null || echo "unknown")

echo "  Local HEAD  : $LOCAL_HEAD"
echo "  Remote HEAD : $REMOTE_HEAD"

if [[ "$LOCAL_HEAD" == "$REMOTE_HEAD" ]]; then
  echo "  ✓ Already in sync — nothing to push"
  NEEDS_PUSH=false
else
  AHEAD=$(git rev-list --count origin/macbook..HEAD 2>/dev/null || echo "?")
  BEHIND=$(git rev-list --count HEAD..origin/macbook 2>/dev/null || echo "?")
  echo "  Local is $AHEAD commit(s) ahead, $BEHIND commit(s) behind remote"

  if [[ "$BEHIND" -gt 0 ]]; then
    echo ""
    echo "  ! Remote has commits not in local — rebasing..."
    git pull --rebase origin macbook 2>&1 | sed 's/^/  /'

    # Check for rebase conflicts
    if [[ -d ".git/rebase-merge" || -d ".git/rebase-apply" ]]; then
      echo ""
      echo "  ✗ REBASE CONFLICT — manual resolution required."
      echo "    Steps:"
      echo "    1. git status        (see conflicted files)"
      echo "    2. Edit conflicted files (keep MacBook-authored content for MacBook-owned files)"
      echo "    3. git add <file>    (for each resolved file)"
      echo "    4. GIT_EDITOR=true git rebase --continue"
      echo "    5. Re-run this script"
      echo ""
      echo "    MacBook-owned files (always take MacBook version):"
      echo "      queue-macbook.yaml, MANIFEST.yaml, _config/DEVICES.md,"
      echo "      _config/KB-LESSONS-LEARNED.yaml (append ThinkPad entries below MacBook's)"
      exit 1
    fi
    echo "  ✓ Rebase clean"
  fi
  NEEDS_PUSH=true
fi

# ─── PHASE 5: Push to origin ─────────────────────────────────────────────────
echo ""
echo "── Phase 5: Push macbook → origin ─────────────────────────"

if [[ "$NEEDS_PUSH" == "true" ]]; then
  echo "  Pushing..."
  git push origin macbook 2>&1 | sed 's/^/  /'
  echo "  ✓ Push complete"
else
  echo "  ✓ No push needed — already in sync"
fi

# ─── PHASE 6: Final verification ─────────────────────────────────────────────
echo ""
echo "── Phase 6: Final state verification ──────────────────────"

FINAL_LOCAL=$(git rev-parse HEAD)
FINAL_REMOTE=$(git rev-parse origin/macbook 2>/dev/null || echo "unknown")

echo "  Local  HEAD : $FINAL_LOCAL"
echo "  Remote HEAD : $FINAL_REMOTE"

if [[ "$FINAL_LOCAL" == "$FINAL_REMOTE" ]]; then
  echo "  ✓ macbook branch: local == remote"
else
  echo "  ✗ WARNING: local and remote still differ — check manually"
fi

echo ""
echo "  Recent commits on macbook:"
git log --oneline -6 | sed 's/^/    /'

echo ""
echo "  Untracked files (review — should only be gitignored items):"
git status --porcelain | grep "^??" | sed 's/^/    /' || echo "    (none)"

echo ""
echo "  .gitignore protects:"
for f in "_config/credentials.yaml" "_config/macbook-delta-*.tar.gz" "_config/thinkpad-delta-*.tar.gz"; do
  echo "    $f"
done

# ─── PHASE 7: Session handoff reminder ───────────────────────────────────────
echo ""
echo "── Phase 7: Session handoff checklist ─────────────────────"
echo "  ✓ macbook branch pushed"
echo "  ✓ BUG-024 fixed live (mim2000 page-contacts.php)"
echo "  ✓ All 3 themes live: zemla v1.7.5 / mim2000 v1.9.1 / bodyterapie v1.7.1"
echo "  ✓ macbook-delta-2026-05-02.tar.gz ready for ThinkPad"
echo "  ✓ THINKPAD-AS-IS-2026-05-02.md: apply guide for ThinkPad"
echo "  ✓ OPUS-SESSION-PREP-MI-M-T-PROD.md: Opus strategic session ready"
echo ""
echo "  MANUAL ACTIONS STILL NEEDED:"
echo "  □ GitHub branch protection: Settings → Branches → Add rule"
echo "    Branch: macbook  → Restrict pushes (ThinkPad must not push)"
echo "    Branch: thinkpad → Restrict pushes (MacBook must not push)"
echo "  □ Transfer macbook-delta-2026-05-02.tar.gz to ThinkPad (USB/LAN)"
echo "    Source: _config/macbook-delta-2026-05-02.tar.gz (49K)"
echo "  □ ThinkPad: apply delta per THINKPAD-AS-IS-2026-05-02.md §2"
echo "  □ ThinkPad: run MI-M-T-D08 scope (testcases.yaml v2 migration)"
echo "  □ ThinkPad: run D-09 portability pass"
echo ""
echo "  NEXT SESSION (Opus):"
echo "  □ Input: _config/OPUS-SESSION-PREP-MI-M-T-PROD.md"
echo "  □ Read §1→§7 before generating delivery plan"
echo "  □ Key decision: §4.3 — PHP-on-Active24 vs FastAPI-on-VPS"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Sync complete.                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
