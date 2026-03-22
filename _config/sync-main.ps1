# sync-main.ps1 â€” Merge gate for ThinkPad (Windows PowerShell)
# Pre-requisite: all local changes must be committed before running.
# Usage: cd ~\Documents\VibeCodeProjects ; .\_config\sync-main.ps1

$ErrorActionPreference = "Stop"

function Log  { param($msg) Write-Host "[sync-main] $msg" -ForegroundColor Cyan }
function Ok   { param($msg) Write-Host "[sync-main] OK  $msg" -ForegroundColor Green }
function Warn { param($msg) Write-Host "[sync-main] WARN $msg" -ForegroundColor Yellow }
function Fail { param($msg) Write-Host "[sync-main] FAIL $msg" -ForegroundColor Red; exit 1 }

$RepoRoot = git rev-parse --show-toplevel 2>$null
if (-not $RepoRoot) { Fail "Not inside a git repository." }
Set-Location $RepoRoot

# 0. Pre-flight
Log "Pre-flight checks..."
$dirty = git status --porcelain
if ($dirty) {
    Write-Host "[sync-main] FAIL Uncommitted changes - commit or stash first:" -ForegroundColor Red
    $dirty | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    exit 1
}
$CurrentBranch = git rev-parse --abbrev-ref HEAD
Log "On branch: $CurrentBranch"

# 1. Integrity check
Log "Running task integrity checks..."
$pytest = Get-Command pytest -ErrorAction SilentlyContinue
if ($pytest) {
    pytest _tests/test_task_integrity.py -q --tb=short
    if ($LASTEXITCODE -ne 0) { Fail "Integrity check failed. Fix before syncing." }
    Ok "Integrity check passed."
} else {
    Warn "pytest not found - skipping. CI will validate on push."
}

# 2. Fetch
Log "Fetching all remotes..."
git fetch --all --prune
if ($LASTEXITCODE -ne 0) { Fail "git fetch failed." }
Ok "Fetch complete."

# 3. Rebase main onto origin
Log "Rebasing main onto origin/main..."
git checkout main
git pull --rebase origin main
if ($LASTEXITCODE -ne 0) { Fail "git pull --rebase failed. Resolve and retry." }
Ok "main is current with origin."

# Helper: merge a device branch into main
function Merge-DeviceBranch {
    param([string]$Branch, [string]$OwnedFile)

    $ref = (git ls-remote --heads origin $Branch) -replace '\s.*', ''
    if (-not $ref) {
        Warn "origin/$Branch not found - skipping."
        return
    }

    Log "Merging origin/$Branch -> main..."
    git merge --no-ff origin/$Branch --no-edit -m "sync: merge $Branch -> main [$(Get-Date -Format 'yyyy-MM-dd')]"

    if ($LASTEXITCODE -eq 0) {
        Ok "$Branch merged cleanly."
        return
    }

    Warn "Conflict detected - applying ownership rules..."

    # Branch owns its queue file: prefer MERGE_HEAD version
    if ($OwnedFile) {
        git ls-files --error-unmatch $OwnedFile 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            try { git checkout MERGE_HEAD -- $OwnedFile }
            catch { Warn "Could not restore $OwnedFile from MERGE_HEAD." }
            git add $OwnedFile
        }
    }

    # All other conflicts: keep main (HEAD)
    $conflicted = git diff --name-only --diff-filter=U 2>$null
    foreach ($f in $conflicted) {
        git checkout HEAD -- $f
        git add $f
    }

    git commit --no-edit -m "sync: resolve $Branch conflicts - ownership applied [$(Get-Date -Format 'yyyy-MM-dd')]"
    if ($LASTEXITCODE -ne 0) { Fail "Auto-resolution of $Branch failed. Fix manually and re-run." }
    Ok "$Branch merged (conflicts resolved by ownership rules)."
}

# 4 & 5. Merge device branches
Merge-DeviceBranch -Branch "macbook"  -OwnedFile "queue-macbook.yaml"
Merge-DeviceBranch -Branch "thinkpad" -OwnedFile "queue-thinkpad.yaml"

# 6. Update MANIFEST.yaml
Log "Updating MANIFEST.yaml sync anchor..."
if (-not (Test-Path "MANIFEST.yaml")) {
    Warn "MANIFEST.yaml not found - skipping."
} else {
    $SyncCommit = git rev-parse --short HEAD
    $SyncTs     = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    $manifest   = Get-Content MANIFEST.yaml -Raw

    $updates = [ordered]@{
        "last_sync"        = "`"$SyncTs`""
        "last_sync_commit" = "`"$SyncCommit`""
        "synced_by"        = "`"sync-main.ps1 [$CurrentBranch]`""
    }
    foreach ($key in $updates.Keys) {
        if ($manifest -match "(?m)^${key}:") {
            $manifest = $manifest -replace "(?m)^${key}:.*", "${key}: $($updates[$key])"
        } else {
            $manifest = $manifest.TrimEnd() + "`n${key}: $($updates[$key])`n"
        }
    }

    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Resolve-Path "MANIFEST.yaml").Path, $manifest, $utf8)
    git add MANIFEST.yaml
    if (git diff --staged --name-only) {
        git commit -m "chore(manifest): update sync anchor [$SyncCommit]"
    }
    Ok "MANIFEST.yaml updated."
}

# 7. Push main
Log "Pushing main to origin..."
git push origin main
if ($LASTEXITCODE -ne 0) { Fail "git push failed." }
$mainHead = git rev-parse --short HEAD
Ok "main pushed: $mainHead"

# 8. Restore working branch
if ($CurrentBranch -ne "main") {
    git checkout $CurrentBranch
    Ok "Restored to $CurrentBranch."
}

Write-Host ""
Write-Host "sync-main complete." -ForegroundColor Green
Write-Host "  main:     $(git rev-parse --short origin/main)"
$mb = git rev-parse --short origin/macbook  2>$null; if ($mb) { Write-Host "  macbook:  $mb" }
try { $tp = git rev-parse --short origin/thinkpad 2>$null } catch { $tp = $null }; if ($tp) { Write-Host "  thinkpad: $tp" }