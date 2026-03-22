#Requires -RunAsAdministrator
<#
.SYNOPSIS
    GitHub workspace initialisation — Windows side.
    Run AFTER windows-setup.ps1 has installed Git and configured SSH.

.DESCRIPTION
    1. Tests SSH connection to GitHub using the ThinkPad ED25519 key
    2. Initialises git repo in the workspace folder
    3. Creates initial commit with all scaffolded files
    4. Pushes to github.com/petr-yamyang/<RepoName>

    SSH private key location: C:\Users\vitez\.ssh\github_ed25519
    (Copy from Linux VM sandbox OR run ssh-keygen on Windows to generate a Windows key
     and add the new public key to GitHub as well — both keys can coexist)

.PARAMETER RepoName
    GitHub repository name (default: VibeCodeProjects)

.PARAMETER CreateRepo
    If set, attempts to create the repo via gh CLI before pushing

.EXAMPLE
    .\github-init.ps1
    .\github-init.ps1 -RepoName "VibeCodeProjects" -CreateRepo

.NOTES
    PRE-REQUISITES:
    - Git installed (via windows-setup.ps1)
    - GitHub CLI (gh) installed (via windows-setup.ps1)
    - SSH key added to github.com/settings/keys (DONE — ThinkPad-dev-2026)
    - SSH private key at C:\Users\vitez\.ssh\github_ed25519

    FALLBACK: If SSH fails, see _config\FALLBACK_PROTOCOL.md → Section 4
#>

param(
    [string]$RepoName   = "VibeCodeProjects",
    [string]$GHUser     = "petr-yamyang",
    [string]$Workspace  = "C:\Users\vitez\Documents\VibeCodeProjects",
    [string]$SSHKey     = "C:\Users\vitez\.ssh\github_ed25519",
    [switch]$CreateRepo = $false
)

# ── Logging ───────────────────────────────────────────────────────────────────
function Log {
    param([string]$Msg, [string]$Level = "INFO")
    $color = switch($Level) {
        "ERROR"   {"Red"}   "WARN"    {"Yellow"}
        "SUCCESS" {"Green"} "GATE"    {"Cyan"}
        default   {"White"}
    }
    Write-Host "[$Level] $Msg" -ForegroundColor $color
}

# ── VALIDATION GATE 0: SSH key file exists ────────────────────────────────────
Log "====== GitHub Workspace Init — ThinkPad ======" "GATE"
Log "Repo:      git@github.com:$GHUser/$RepoName.git"
Log "Workspace: $Workspace"
Log ""

Log "[Gate 0] Checking SSH key..." "GATE"
if (-not (Test-Path $SSHKey)) {
    Log "SSH key not found at $SSHKey" "ERROR"
    Log "Options:" "WARN"
    Log "  A) Copy from Linux VM: the key is at /sessions/funny-zen-pascal/.ssh/github_ed25519" "WARN"
    Log "     Copy to C:\Users\vitez\.ssh\github_ed25519 (no extension = private key)" "WARN"
    Log "  B) Generate a new Windows SSH key:" "WARN"
    Log "     ssh-keygen -t ed25519 -C 'petr-yamyang@ThinkPad-win' -f C:\Users\vitez\.ssh\github_ed25519_win" "WARN"
    Log "     Then add the .pub to github.com/settings/keys" "WARN"
    exit 1
}
Log "SSH key found: $SSHKey" "SUCCESS"

# ── VALIDATION GATE 1: SSH connection test ────────────────────────────────────
Log ""
Log "[Gate 1] Testing SSH connection to GitHub..." "GATE"
$sshResult = & ssh -T -i $SSHKey -o StrictHostKeyChecking=no git@github.com 2>&1
if ($sshResult -match "successfully authenticated") {
    Log "SSH authentication: OK — $sshResult" "SUCCESS"
} else {
    Log "SSH authentication failed: $sshResult" "ERROR"
    Log "Fallback: see _config\FALLBACK_PROTOCOL.md → SSH Recovery" "WARN"
    exit 1
}

# ── VALIDATION GATE 2: Git available ─────────────────────────────────────────
Log ""
Log "[Gate 2] Checking Git..." "GATE"
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Log "Git not found. Run windows-setup.ps1 first." "ERROR"
    exit 1
}
Log "Git: $gitVersion" "SUCCESS"

# ── Configure git SSH command to use our specific key ─────────────────────────
$env:GIT_SSH_COMMAND = "ssh -i $SSHKey -o StrictHostKeyChecking=no"
git config --global user.name  $GHUser
git config --global user.email "petr@zemla.org"
git config --global core.autocrlf false
git config --global init.defaultBranch main
Log "Git identity configured: $GHUser / petr@zemla.org" "SUCCESS"

# ── OPTIONAL: Create repo via gh CLI ─────────────────────────────────────────
if ($CreateRepo) {
    Log ""
    Log "[Optional] Creating GitHub repo via gh CLI..." "GATE"
    $ghVersion = gh --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        gh repo create "$GHUser/$RepoName" --private --description "VibeCodeProjects — ThinkPad/MacBook dual-device workspace" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Log "Repo created: github.com/$GHUser/$RepoName" "SUCCESS"
        } else {
            Log "Repo creation failed (may already exist — continuing)" "WARN"
        }
    } else {
        Log "gh CLI not found — create repo manually at github.com/new" "WARN"
    }
}

# ── VALIDATION GATE 3: Init + commit ─────────────────────────────────────────
Log ""
Log "[Gate 3] Initialising git repository..." "GATE"
Set-Location $Workspace

if (-not (Test-Path ".git")) {
    git init
    Log "Git repo initialised" "SUCCESS"
} else {
    Log "Git repo already exists" "SUCCESS"
}

# Add remote
$remoteUrl = "git@github.com:$GHUser/$RepoName.git"
$existingRemote = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    git remote add origin $remoteUrl
    Log "Remote added: $remoteUrl" "SUCCESS"
} else {
    Log "Remote already set: $existingRemote" "SUCCESS"
}

# Stage all scaffold files
git add .gitignore TASKS.yaml 2>$null
git add _config\ _sync\ _templates\ .github\ 2>$null
git add "platform sources\" databases\ sandboxes\ Generic\ 2>$null

$status = git status --short
Log "Files staged:" "SUCCESS"
$status | ForEach-Object { Log "  $_" }

# Commit
$date = Get-Date -Format "yyyy-MM-dd"
git commit -m "chore: ThinkPad workspace scaffold — $date

- Infrastructure audit + device config (INFRA_AUDIT.md, DEVICES.md)
- Platform hello-world tests: C++, Rust, Scala, Fortran, Pascal, React
- GitHub Actions CI/CD heartbeat (9 jobs: all platforms + Chrome/Firefox/DB)
- Database configs: PostgreSQL + MongoDB (local dev instances)
- Windows setup script + LibreOffice D:\ migration script
- Fallback/rollback protocol
- SSH key: ThinkPad-dev-2026 (ED25519) registered on GitHub
- PAT: ThinkPad-vibedev-2026 (encrypted, never committed)"

if ($LASTEXITCODE -eq 0) {
    Log "Initial commit created" "SUCCESS"
} else {
    Log "Nothing to commit or commit failed" "WARN"
}

# ── VALIDATION GATE 4: Push ───────────────────────────────────────────────────
Log ""
Log "[Gate 4] Pushing to GitHub..." "GATE"
git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Log "Pushed to github.com/$GHUser/$RepoName" "SUCCESS"
    Log ""
    Log "====== Init complete ======" "GATE"
    Log "MacBook clone: git clone git@github.com:$GHUser/$RepoName.git" "SUCCESS"
    Log "ThinkPad pull: git pull origin main" "SUCCESS"
} else {
    Log "Push failed. Likely cause: repo does not exist yet on GitHub." "ERROR"
    Log "Fix: go to github.com/new and create '$RepoName' (private), then re-run this script." "WARN"
    Log "Or run with -CreateRepo flag if gh CLI is installed." "WARN"
    exit 1
}
