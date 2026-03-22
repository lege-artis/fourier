# Fallback & Rollback Protocol

This document provides comprehensive procedures for capturing system state, performing rollbacks, and recovering from configuration failures in the VibeCodeProjects development workspace.

## Table of Contents

1. [Pre-Change State Capture](#pre-change-state-capture)
2. [Rollback Procedures](#rollback-procedures)
3. [Validation Gate Checklist](#validation-gate-checklist)
4. [GitHub SSH Recovery](#github-ssh-recovery)
5. [Per-Platform Rollback](#per-platform-rollback)
6. [Emergency Contact Procedure](#emergency-contact-procedure)

---

## Pre-Change State Capture

Before making any significant changes to the development environment, capture the current state using these procedures.

### Git Stash & Snapshot

Run these commands before major configuration changes:

```bash
# Navigate to workspace root
cd C:\Users\vitez\Documents\VibeCodeProjects

# Stash any uncommitted changes
git stash save "pre-change-stash-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"

# Create a snapshot of the current git state
git log --oneline -20 > .\_config\git-snapshot-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').log
git branch -a > .\_config\git-branches-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').log
git remote -v > .\_config\git-remotes-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').log
```

### Version Snapshots

Record current tool versions before changes:

```powershell
# PowerShell: Create a version snapshot file
$timestamp = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$reportFile = "C:\Users\vitez\Documents\VibeCodeProjects\_config\version-snapshot-$timestamp.txt"

@"
Version Snapshot - $timestamp

Git: $(git --version)
Node.js: $(node --version)
npm: $(npm --version)
Rust: $(rustc --version)
Cargo: $(cargo --version)
Java: $(java -version 2>&1)
SBT: $(sbt --version 2>&1)
Free Pascal: $(fpc -version 2>&1)
GFortran: $(gfortran --version 2>&1)
Docker: $(docker --version 2>&1)
GitHub CLI: $(gh --version 2>&1)
"@ | Out-File -FilePath $reportFile -Encoding UTF8 -Force

Write-Host "Version snapshot saved to: $reportFile"
```

### Environment Variables Snapshot

```powershell
# Export current environment variables related to development
$envSnapshot = @{
    RUST_TOOLCHAIN = $env:RUST_TOOLCHAIN
    JAVA_HOME = $env:JAVA_HOME
    PATH = $env:PATH
    CARGO_HOME = $env:CARGO_HOME
    RUSTUP_HOME = $env:RUSTUP_HOME
    GOPATH = $env:GOPATH
    GOROOT = $env:GOROOT
}

$timestamp = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$envSnapshot | Export-Clixml -Path "C:\Users\vitez\Documents\VibeCodeProjects\_config\env-snapshot-$timestamp.xml"

Write-Host "Environment variables snapshot saved"
```

---

## Rollback Procedures

### Rollback: Git Configuration

If git configuration becomes corrupted or SSH access breaks:

```bash
# View current git config
git config --list --local
git config --list --global
git config --list --system

# Reset local repository configuration
cd C:\Users\vitez\Documents\VibeCodeProjects
git config --local --unset-all user.name
git config --local --unset-all user.email
git config --local user.name "Your Name"
git config --local user.email "your.email@example.com"

# Reset to default remote configuration
git remote set-url origin https://github.com/petr-yamyang/VibeCodeProjects.git
# OR for SSH (after SSH key is restored):
git remote set-url origin git@github.com:petr-yamyang/VibeCodeProjects.git

# Verify git status
git status
git log --oneline -1
```

### Rollback: SSH Key Removal from GitHub

If an SSH key needs to be revoked from GitHub:

1. Go to [GitHub Settings - SSH and GPG keys](https://github.com/settings/keys)
2. Locate the key to revoke (titled "ThinkPad-dev-2026")
3. Click "Delete"
4. Confirm the deletion

**Note:** This breaks SSH access until a new key is added. See [GitHub SSH Recovery](#github-ssh-recovery).

### Rollback: PAT (Personal Access Token) Revocation

If a PAT becomes compromised or needs to be reset:

1. Go to [GitHub Settings - Developer settings - Personal access tokens](https://github.com/settings/tokens)
2. Click on the token you want to revoke
3. Click "Delete" and confirm

After revocation:
- Any workflows or scripts using the PAT will fail
- Generate a new PAT with required scopes (see [GitHub SSH Setup Guide](#github-ssh-setup-guide))
- Update all stored credentials

### Rollback: Database Data Directory Restore

If database changes cause issues:

```bash
# Backup current database state
# (Assuming PostgreSQL in Docker or local installation)

# For PostgreSQL locally:
pg_dumpall -U postgres > "C:\Users\vitez\Documents\VibeCodeProjects\_config\db-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').sql"

# Restore from backup:
psql -U postgres < "C:\Users\vitez\Documents\VibeCodeProjects\_config\db-backup-<timestamp>.sql"

# For Docker PostgreSQL:
docker exec postgres-container pg_dump -U postgres dbname > backup.sql
docker exec -i postgres-container psql -U postgres < backup.sql
```

---

## Validation Gate Checklist

Use this checklist before and after each major change.

### Pre-Change Validation

- [ ] All uncommitted changes stashed: `git status` shows clean working directory
- [ ] Version snapshot created: `version-snapshot-*.txt` exists in `_config/`
- [ ] Git snapshot created: `git-snapshot-*.log` exists in `_config/`
- [ ] Environment snapshot created: `env-snapshot-*.xml` exists in `_config/`
- [ ] Database backup created (if applicable): SQL dump file exists
- [ ] SSH key fingerprint recorded: `ssh-keygen -l -f ~/.ssh/id_ed25519`
- [ ] GitHub web UI accessible: Can log in to github.com
- [ ] Git remote verified: `git remote -v` shows correct repository

### Post-Change Validation

- [ ] No compilation errors: All platform tests pass in CI/CD
- [ ] SSH connectivity restored: `ssh -T git@github.com` succeeds
- [ ] Git operations functional: `git pull`, `git push` work without errors
- [ ] All tools operational: `windows-setup.ps1 -SkipVerification` passes
- [ ] Environment variables correct: Required `*_HOME` and `PATH` variables set
- [ ] Database connectivity verified: `SELECT version()` succeeds
- [ ] GitHub Actions passing: All workflow runs show green status
- [ ] No unexpected file changes: `git status` shows expected changes only

---

## GitHub SSH Recovery

### Scenario: SSH Key Becomes Inaccessible

**Problem:** `ssh -T git@github.com` fails with "Permission denied (publickey)"

**Recovery Steps:**

1. **Verify SSH key exists locally:**
   ```bash
   ls -la ~/.ssh/id_ed25519*
   ```
   If files don't exist, generate new keys (see [GitHub SSH Setup Guide](./github-ssh-setup.md)).

2. **Check SSH agent status:**
   ```bash
   # Windows PowerShell
   Get-Service ssh-agent | Start-Service

   # Or using ssh-add
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Test SSH connection with verbose output:**
   ```bash
   ssh -vvv git@github.com
   ```
   Review output for specific error messages.

4. **If key was deleted from GitHub:**
   - Go to [GitHub Settings - SSH and GPG keys](https://github.com/settings/keys)
   - Click "New SSH key"
   - Paste the public key from `~/.ssh/id_ed25519.pub`
   - Give it a title: "ThinkPad-dev-2026"
   - Set expiration to appropriate duration (e.g., 1 year)
   - Click "Add SSH key"

5. **Verify recovery:**
   ```bash
   ssh -T git@github.com
   # Expected output: "Hi petr-yamyang! You've successfully authenticated..."
   ```

6. **Update git remote if needed:**
   ```bash
   cd C:\Users\vitez\Documents\VibeCodeProjects
   git remote set-url origin git@github.com:petr-yamyang/VibeCodeProjects.git
   git pull
   ```

### Scenario: Need to Use HTTPS Instead of SSH

If SSH cannot be restored quickly, temporarily use HTTPS with PAT:

1. **Generate PAT (if not already done):**
   - Go to [GitHub Settings - Developer settings - Personal access tokens](https://github.com/settings/tokens)
   - Click "Generate new token"
   - Select scopes: `repo`, `workflow`, `read:org`, `admin:public_key`
   - Copy the token (you won't see it again)

2. **Update git remote to HTTPS:**
   ```bash
   cd C:\Users\vitez\Documents\VibeCodeProjects
   git remote set-url origin https://github.com/petr-yamyang/VibeCodeProjects.git
   ```

3. **Configure git to use PAT:**
   ```bash
   # Store PAT in git credential manager (Windows)
   git config --global credential.helper manager-core

   # Or use cached credentials
   git config --global credential.helper cache
   ```

4. **Test connection:**
   ```bash
   git pull
   ```

5. **Switch back to SSH once recovered:**
   ```bash
   git remote set-url origin git@github.com:petr-yamyang/VibeCodeProjects.git
   git pull
   ```

---

## Per-Platform Rollback

### Windows: Visual Studio Code

```powershell
# Uninstall
winget uninstall Microsoft.VisualStudioCode

# Clean up user settings
Remove-Item -Path "$env:APPDATA\Code" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.vscode" -Recurse -Force

# Verify removal
code --version
```

### Windows: Git

```powershell
# Uninstall
winget uninstall Git.Git

# Clean up SSH keys (if desired)
Remove-Item -Path "$env:USERPROFILE\.ssh" -Recurse -Force

# Clean up git configuration
Remove-Item -Path "$env:APPDATA\Git" -Recurse -Force

# Verify removal
git --version
```

### Windows: Node.js & npm

```powershell
# Uninstall Node.js
winget uninstall OpenJS.NodeJS.LTS

# Clean up npm cache and global modules
npm cache clean --force
Remove-Item -Path "$env:APPDATA\npm" -Recurse -Force

# Verify removal
node --version
npm --version
```

### Windows: Rust

```powershell
# Uninstall using rustup
rustup self uninstall

# Or manually uninstall
winget uninstall Rustlang.Rust.MSVC

# Clean up directories
Remove-Item -Path "$env:USERPROFILE\.cargo" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.rustup" -Recurse -Force

# Verify removal
rustc --version
cargo --version
```

### Windows: Free Pascal

```powershell
# Uninstall
winget uninstall FreePascal.FreePascal

# Clean up configuration
Remove-Item -Path "$env:APPDATA\fpc" -Recurse -Force

# Verify removal
fpc -version
```

### Windows: OpenJDK 17

```powershell
# Uninstall
winget uninstall EclipseAdoptium.Temurin.17.JDK

# Clean up environment variables
[Environment]::SetEnvironmentVariable("JAVA_HOME", $null, "User")

# Verify removal
java -version
```

### Windows: SBT

```powershell
# Uninstall
winget uninstall Lightbend.SBT

# Clean up SBT cache
Remove-Item -Path "$env:USERPROFILE\.sbt" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.ivy2" -Recurse -Force

# Verify removal
sbt --version
```

### Windows: MSYS2 & GFortran

```powershell
# Uninstall MSYS2
winget uninstall msys2.msys2

# Manually remove MSYS2 directory
Remove-Item -Path "C:\msys64" -Recurse -Force

# Clean up environment PATH
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = ($path -split ';' | Where-Object { $_ -notlike "*msys64*" }) -join ';'
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# Verify removal
gfortran --version
```

### Windows: Docker Desktop

```powershell
# Uninstall
winget uninstall Docker.DockerDesktop

# Clean up Docker data
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force

# Stop Docker service
Stop-Service -Name "Docker" -Force -ErrorAction SilentlyContinue
Remove-Service -Name "Docker" -ErrorAction SilentlyContinue

# Verify removal
docker --version
```

### Windows: GitHub CLI

```powershell
# Uninstall
winget uninstall GitHub.cli

# Clean up configuration
Remove-Item -Path "$env:APPDATA\GitHub CLI" -Recurse -Force

# Verify removal
gh --version
```

---

## Emergency Contact Procedure

In case of critical system failures or security breaches:

### Immediate Actions (First 15 minutes)

1. **Isolate the system:**
   - Disconnect from network if security breach suspected
   - Stop git push/pull operations
   - Disable auto-sync features

2. **Revoke compromised credentials:**
   - GitHub: Go to Settings → SSH and GPG keys → Delete compromised keys
   - GitHub: Go to Settings → Developer settings → Personal access tokens → Delete compromised tokens
   - Docker: Delete Docker Hub access tokens

3. **Document the incident:**
   ```bash
   $incident = @{
       Time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
       Issue = "DESCRIBE_THE_ISSUE_HERE"
       AffectedSystems = @("Git", "SSH", "Docker", "etc")
       Actions = @("Isolated system", "Revoked PAT", "etc")
   }
   $incident | Out-File -FilePath "C:\Users\vitez\Documents\VibeCodeProjects\_config\incident-log-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').txt"
   ```

### Recovery Steps (Within 1 hour)

1. **Restore from snapshot:**
   - Use version snapshots to verify expected tool versions
   - Use git snapshots to verify commit history integrity
   - Use environment snapshots to restore PATH and variables

2. **Regenerate credentials:**
   - Generate new SSH key pair (if compromised)
   - Generate new PAT with minimal required scopes
   - Add new SSH key to GitHub web UI manually

3. **Verify integrity:**
   - Run: `windows-setup.ps1 -SkipVerification`
   - Run GitHub Actions workflow manually
   - Test all platform builds locally

4. **Re-enable operations:**
   - Reconnect to network once verified
   - Resume git operations
   - Re-enable auto-sync if previously enabled

### Escalation (If unresolved within 2 hours)

- Contact GitHub Support: https://github.com/contact
- Document all actions taken in incident log
- Provide snapshots and logs to support team
- Request security audit if breach suspected

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-21 | 1.0 | Initial creation |

## Related Documents

- [GitHub SSH Setup Guide](./github-ssh-setup.md)
- [Windows Setup Script](./windows-setup.ps1)
- [CI/CD Workflow](../.github/workflows/ci-heartbeat.yml)
