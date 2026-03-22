# GitHub SSH Setup Guide

This guide documents the SSH key setup and GitHub authentication configuration for the VibeCodeProjects development workspace on the ThinkPad running Windows.

## Overview

- **GitHub Account:** petr-yamyang
- **SSH Key Type:** ED25519
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIJLmVhI8CgoLSncnj4fBEj+cUvTmCx0w/UXJfcp7ES petr-yamyang@ThinkPad-dev-2026`
- **SSH Key Location:** `~/.ssh/id_ed25519` (or `C:\Users\vitez\.ssh\id_ed25519` on Windows)
- **Key Fingerprint:** Available via `ssh-keygen -l -f ~/.ssh/id_ed25519`

## Prerequisites

- GitHub account with access to petr-yamyang
- Git installed on Windows (via `windows-setup.ps1`)
- OpenSSH Client installed (included in modern Windows 10/11)
- SSH agent running (automatically manages SSH keys)

## Step 1: Verify SSH Key Exists Locally

### PowerShell Check

```powershell
# Check if SSH key pair exists
Get-Item -Path "$env:USERPROFILE\.ssh\id_ed25519*" -ErrorAction SilentlyContinue

# If files exist, list them
ls $env:USERPROFILE\.ssh\id_ed25519*
```

### Expected Output

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         3/21/2026  10:30 AM            464 id_ed25519
-a----         3/21/2026  10:30 AM            103 id_ed25519.pub
```

### If Keys Don't Exist

If the SSH keys are not present, generate new keys:

```bash
# Generate new ED25519 SSH key pair
ssh-keygen -t ed25519 -C "petr-yamyang@ThinkPad-dev-2026" -f ~/.ssh/id_ed25519 -N ""

# The -N "" flag creates the key with an empty passphrase
# You can omit -N "" to be prompted for a passphrase for better security
```

## Step 2: Get Your SSH Public Key

### Display Public Key

```powershell
# PowerShell: Display the public key content
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

# Or using bash/Git Bash
cat ~/.ssh/id_ed25519.pub
```

### Expected Output Format

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIJLmVhI8CgoLSncnj4fBEj+cUvTmCx0w/UXJfcp7ES petr-yamyang@ThinkPad-dev-2026
```

**Keep this key content handy; you'll need it for the next step.**

## Step 3: Add SSH Key to GitHub Web UI

### Manual Web UI Steps

1. **Log in to GitHub:**
   - Go to https://github.com/login
   - Enter your credentials for petr-yamyang account
   - Complete any 2FA verification if enabled

2. **Navigate to SSH Keys Settings:**
   - Click your profile icon (top right corner)
   - Select "Settings"
   - In the left sidebar, click "SSH and GPG keys"
   - URL: https://github.com/settings/keys

3. **Add New SSH Key:**
   - Click the green "New SSH key" button
   - Fill in the form:
     - **Title:** `ThinkPad-dev-2026`
     - **Key type:** Authentication Key (default)
     - **Key:** Paste the entire content of your public key from Step 2
       - Should start with: `ssh-ed25519`
       - Should end with: `petr-yamyang@ThinkPad-dev-2026`
   - Optionally set an expiration date (e.g., 1 year from now)

4. **Confirm Addition:**
   - Click "Add SSH key"
   - You may be prompted to re-authenticate for security
   - The key should now appear in your SSH keys list with a green checkmark

### Visual Reference

```
GitHub Settings > SSH and GPG keys
├── New SSH key button
│   ├── Title: ThinkPad-dev-2026
│   ├── Key type: Authentication Key
│   ├── Key: [paste your public key here]
│   └── Expiration: [optional, set to 1 year]
└── [Add SSH key button]
```

## Step 4: Start SSH Agent (Windows)

### Option A: Using PowerShell (Recommended)

```powershell
# Check if SSH Agent service is running
Get-Service ssh-agent | Select-Object Status

# Start the SSH Agent service
Start-Service ssh-agent

# Verify it's running
Get-Service ssh-agent | Select-Object Status

# Add your SSH key to the agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

### Option B: Using Git Bash

```bash
# Start SSH agent
eval $(ssh-agent -s)

# Add your SSH key to the agent
ssh-add ~/.ssh/id_ed25519
```

### Make SSH Agent Start Automatically

Create a PowerShell profile to auto-start SSH Agent:

```powershell
# Edit PowerShell profile
notepad $PROFILE

# Add these lines to the profile:
# Start SSH Agent if not running
$sshAgentStatus = Get-Service ssh-agent -ErrorAction SilentlyContinue
if ($sshAgentStatus -and $sshAgentStatus.Status -ne 'Running') {
    Start-Service ssh-agent
    ssh-add $env:USERPROFILE\.ssh\id_ed25519
}
```

## Step 5: Test SSH Connection to GitHub

### SSH Connection Test

```bash
# Test SSH connection to GitHub
ssh -T git@github.com
```

### Expected Success Output

```
Hi petr-yamyang! You've successfully authenticated, but GitHub does not provide shell access.
```

### Troubleshooting Failed Connection

**Error:** "Permission denied (publickey)"

1. **Verify SSH key is added to agent:**
   ```bash
   ssh-add -l
   # Should show: ssh-ed25519 AAAAC3... petr-yamyang@ThinkPad-dev-2026
   ```

2. **Test with verbose output:**
   ```bash
   ssh -vvv git@github.com
   # Review output for detailed error information
   ```

3. **Verify key on GitHub:**
   - Go to https://github.com/settings/keys
   - Confirm your key is listed with a green checkmark
   - Check the key fingerprint matches:
     ```bash
     ssh-keygen -l -f ~/.ssh/id_ed25519
     ```

4. **Check file permissions:**
   ```powershell
   # Ensure proper permissions on SSH directory
   icacls $env:USERPROFILE\.ssh
   # Should show: Administrators, current user with full control
   ```

## Step 6: Generate Personal Access Token (PAT)

A PAT provides an alternative/fallback authentication method for GitHub API and HTTPS operations.

### Create PAT via GitHub Web UI

1. **Navigate to Developer Settings:**
   - Go to https://github.com/settings/tokens
   - Or: Profile icon → Settings → Developer settings → Personal access tokens

2. **Generate New Token:**
   - Click "Generate new token" (or "Generate new token (classic)")
   - For classic tokens: Select appropriate scopes

3. **Required Scopes for Development:**
   - [ ] `repo` — Full control of private repositories
   - [ ] `workflow` — Update GitHub Actions and workflows
   - [ ] `read:org` — Read access to organization data
   - [ ] `admin:public_key` — Manage SSH public keys
   - [ ] `gist` — Create gists (optional)

4. **Set Expiration:**
   - Recommended: 90 days
   - For development machines: 1 year maximum
   - Select expiration date and click "Generate token"

5. **Copy Token:**
   - **Important:** Copy the token immediately. You won't see it again.
   - Token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Example Scopes Checklist

```
[✓] repo
    [✓] repo:status
    [✓] repo_deployment
    [✓] public_repo
    [✓] repo:invite
    [✓] security_events
[✓] workflow
[✓] read:org
[✓] admin:public_key
```

## Step 7: Store and Encrypt the PAT

### Option A: Store in Git Credential Manager (Recommended)

```powershell
# Configure Git to use Windows Credential Manager
git config --global credential.helper manager-core

# When git prompts for credentials, enter:
# Username: petr-yamyang
# Password: (paste your PAT here)

# Git will store credentials securely
```

### Option B: Encrypt PAT with OpenSSL

```powershell
# Generate a random encryption key
$encryptionKey = openssl rand -base64 32

# Save encryption key to secure location
$encryptionKey | Out-File -FilePath "$env:USERPROFILE\.ssh\pat-key.enc" -Encoding UTF8

# Encrypt your PAT (replace YOUR_PAT_HERE with your actual token)
$patToken = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
echo $patToken | openssl enc -aes-256-cbc -salt -pass file:$env:USERPROFILE\.ssh\pat-key.enc -out $env:USERPROFILE\.ssh\pat-encrypted.bin

# To decrypt later:
openssl enc -aes-256-cbc -d -pass file:$env:USERPROFILE\.ssh\pat-key.enc -in $env:USERPROFILE\.ssh\pat-encrypted.bin
```

### Option C: Store in Environment Variable (Less Secure)

```powershell
# NOT RECOMMENDED for sensitive tokens
# Only use for development/testing environments

# Set environment variable
[Environment]::SetEnvironmentVariable("GITHUB_PAT", "ghp_xxxxx", "User")

# Use in scripts:
$token = $env:GITHUB_PAT
```

## Step 8: Configure Git Remote for SSH

### Update Repository Remote

```bash
# Navigate to workspace
cd C:\Users\vitez\Documents\VibeCodeProjects

# View current remotes
git remote -v

# Set remote to use SSH (if it's currently using HTTPS)
git remote set-url origin git@github.com:petr-yamyang/VibeCodeProjects.git

# Add SSH remote if not present
git remote add origin-ssh git@github.com:petr-yamyang/VibeCodeProjects.git

# Verify remotes
git remote -v
```

### Expected Output

```
origin          git@github.com:petr-yamyang/VibeCodeProjects.git (fetch)
origin          git@github.com:petr-yamyang/VibeCodeProjects.git (push)
origin-ssh      git@github.com:petr-yamyang/VibeCodeProjects.git (fetch)
origin-ssh      git@github.com:petr-yamyang/VibeCodeProjects.git (push)
```

## Step 9: Test Git Operations

### Test Clone (SSH)

```bash
# Test cloning via SSH (create in temp directory first)
cd C:\Temp
git clone git@github.com:petr-yamyang/VibeCodeProjects.git test-clone
cd test-clone
git log --oneline -5
```

### Test Push/Pull

```bash
# In your workspace directory
cd C:\Users\vitez\Documents\VibeCodeProjects

# Test pull
git pull origin main

# Create test branch
git checkout -b test-ssh-setup

# Make a test commit
echo "# SSH Setup Verification" >> README.md
git add README.md
git commit -m "Verify SSH setup - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Test push
git push -u origin test-ssh-setup

# Clean up test branch
git checkout main
git push origin --delete test-ssh-setup
git branch -d test-ssh-setup
```

## Step 10: Verify GitHub Actions Access

### Test Workflow Permissions

```bash
# Use GitHub CLI to verify access
gh auth status

# List workflows
gh workflow list

# Manually trigger a workflow (optional)
gh workflow run ci-heartbeat.yml --ref main
```

### Expected Output

```
github.com
  ✓ Logged in to github.com as petr-yamyang (keyring)
  ✓ Git operations via ssh
  ✓ Token scopes: repo, workflow, read:org, admin:public_key
```

## Troubleshooting

### Issue: "No such file or directory" for SSH key

**Solution:**
```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Set proper permissions (important on Windows)
icacls $env:USERPROFILE\.ssh /grant:r "$env:USERNAME:(F)"
icacls $env:USERPROFILE\.ssh\id_ed25519 /grant:r "$env:USERNAME:(F)"
```

### Issue: "Agent admitted failure to sign"

**Solution:**
```bash
# Restart SSH Agent
Stop-Service ssh-agent
Start-Service ssh-agent

# Re-add the key
ssh-add ~/.ssh/id_ed25519
```

### Issue: "Permission denied" after adding SSH key

**Solution:**
1. Wait 5-10 minutes (GitHub caches keys)
2. Test connection: `ssh -T git@github.com`
3. Check key on GitHub: https://github.com/settings/keys
4. Verify key fingerprint matches:
   ```bash
   ssh-keygen -l -f ~/.ssh/id_ed25519
   ```

### Issue: PAT Not Working with Git

**Solution:**
```bash
# Clear cached credentials
git config --global --unset credential.helper

# Reconfigure credential manager
git config --global credential.helper manager-core

# Test with HTTPS URL
git clone https://github.com/petr-yamyang/VibeCodeProjects.git
# When prompted: username = petr-yamyang, password = your PAT
```

## Security Best Practices

1. **Never commit SSH keys** to repositories
2. **Rotate PATs periodically** (every 90 days recommended)
3. **Use SSH over HTTPS** when possible (more secure)
4. **Enable 2FA on GitHub** account
5. **Review authorized keys regularly** at https://github.com/settings/keys
6. **Don't share PATs** via email, chat, or version control
7. **Use minimal scopes** for PATs (principle of least privilege)
8. **Monitor SSH key activity** via GitHub audit logs

## Emergency: Revoked SSH Key

If your SSH key is compromised or needs to be revoked:

1. **Revoke Key on GitHub:**
   - Go to https://github.com/settings/keys
   - Find the key "ThinkPad-dev-2026"
   - Click "Delete"

2. **Generate New Key:**
   ```bash
   ssh-keygen -t ed25519 -C "petr-yamyang@ThinkPad-dev-2026-new" -f ~/.ssh/id_ed25519_new
   ```

3. **Add New Key to GitHub:**
   - Follow Step 3 above with the new public key

4. **Update Local Git Configuration:**
   ```bash
   git config --global core.sshCommand "ssh -i ~/.ssh/id_ed25519_new"
   ```

5. **Test Connection:**
   ```bash
   ssh -T git@github.com
   ```

## Related Documents

- [Windows Setup Script](./windows-setup.ps1)
- [Fallback & Rollback Protocol](./FALLBACK_PROTOCOL.md)
- [CI/CD Workflow](../.github/workflows/ci-heartbeat.yml)

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-21 | 1.0 | Initial creation with ED25519 key setup |

## Additional Resources

- GitHub SSH Documentation: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- GitHub PAT Documentation: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- OpenSSH Key Generation: https://man.openbsd.org/ssh-keygen
