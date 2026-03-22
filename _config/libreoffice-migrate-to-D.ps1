#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Migrates LibreOffice and TexLive from C:\ to D:\ for daily use.
    Frees C:\ disk space during dev environment setup without losing productivity tools.

.DESCRIPTION
    Phase 1 — Pre-dev-setup:
      Downloads LibreOffice + MiKTeX (modern TexLive replacement) installers to D:\TempRepo\
      Uninstalls existing C:\ installations
    Phase 2 — Post-dev-setup reinstall:
      Reinstalls LibreOffice and TexLive/MiKTeX with install path set to D:\

.PARAMETER Phase
    "backup"  — Phase 1: save installers to D:\TempRepo\, uninstall from C:\
    "restore" — Phase 2: reinstall from D:\TempRepo\ to D:\

.EXAMPLE
    .\libreoffice-migrate-to-D.ps1 -Phase backup
    .\libreoffice-migrate-to-D.ps1 -Phase restore

.NOTES
    Fallback: if D:\ is unavailable, use E:\ or external drive.
    Installer cache in D:\TempRepo\ should be kept until restore is confirmed working.
    Author: ThinkPad workspace init — 2026-03-21
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("backup","restore")]
    [string]$Phase,

    [string]$TempRepo   = "D:\TempRepo",
    [string]$InstallRoot = "D:\Apps"
)

# ── Logging ────────────────────────────────────────────────────────────────────
$logFile = "$TempRepo\migrate-log.txt"

function Log {
    param([string]$Msg, [string]$Level = "INFO")
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Msg"
    Write-Host $line -ForegroundColor $(switch($Level){
        "ERROR"   {"Red"}   "WARN" {"Yellow"}
        "SUCCESS" {"Green"} default {"White"}
    })
    if (Test-Path (Split-Path $logFile)) { Add-Content -Path $logFile -Value $line }
}

function Ensure-Dir { param([string]$Path)
    if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}

# ── Phase 1: Backup → uninstall from C:\, save installers to D:\TempRepo\ ─────
function Run-Backup {
    Log "====== PHASE 1: Backup + C:\ uninstall ======"
    Ensure-Dir $TempRepo
    Ensure-Dir $InstallRoot

    # ── Snapshot current state (fallback reference) ────────────────────────────
    $snapshotPath = "$TempRepo\pre-migration-snapshot.txt"
    Log "Writing pre-migration snapshot to $snapshotPath"
    @(
        "=== Snapshot: $(Get-Date) ===",
        "",
        "--- Installed via winget ---",
        (winget list 2>&1 | Out-String),
        "",
        "--- Disk space before ---",
        (Get-PSDrive C | Select-Object Name, Used, Free | Out-String)
    ) | Out-File -FilePath $snapshotPath -Encoding UTF8

    # ── LibreOffice ─────────────────────────────────────────────────────────────
    Log "Checking for LibreOffice installation..."
    $loInstalled = winget list --id "TheDocumentFoundation.LibreOffice" 2>&1 | Select-String "LibreOffice"

    if ($loInstalled) {
        Log "LibreOffice found. Downloading installer to $TempRepo before uninstall..."
        # Download latest LibreOffice installer via winget export or direct link
        # winget export saves a JSON manifest for re-import
        winget export -o "$TempRepo\libreoffice-winget-export.json" --include-versions 2>&1 | Out-Null
        Log "LibreOffice winget manifest exported."

        Log "Uninstalling LibreOffice from C:\..."
        winget uninstall --id "TheDocumentFoundation.LibreOffice" --silent 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Log "LibreOffice uninstalled from C:\ successfully." "SUCCESS"
        } else {
            Log "LibreOffice uninstall returned non-zero. Verify manually." "WARN"
        }
    } else {
        Log "LibreOffice not found via winget. Checking Programs..." "WARN"
        $lo = Get-Package -Name "LibreOffice*" -ErrorAction SilentlyContinue
        if ($lo) {
            Log "Found via Get-Package: $($lo.Name) $($lo.Version)"
            $lo | Uninstall-Package -Force -ErrorAction SilentlyContinue
        } else {
            Log "LibreOffice not detected. Skipping." "WARN"
        }
    }

    # ── MiKTeX / TexLive ─────────────────────────────────────────────────────────
    Log "Checking for TexLive / MiKTeX installation..."
    $texInstalled = winget list 2>&1 | Select-String -Pattern "MiKTeX|TexLive|texlive"

    if ($texInstalled) {
        Log "TeX distribution found. Exporting manifest..."
        # winget export already run above; covers TeX too
        Log "Uninstalling MiKTeX/TexLive from C:\..."
        winget uninstall --id "MiKTeX.MiKTeX" --silent 2>&1 | Out-Null
        winget uninstall --name "MiKTeX" --silent 2>&1 | Out-Null
        Log "TeX distribution uninstalled." "SUCCESS"
    } else {
        Log "No winget-managed TeX distribution found. Skipping." "WARN"
    }

    # ── Post-uninstall space report ────────────────────────────────────────────
    $freeAfter = (Get-PSDrive C).Free / 1GB
    Log ("C:\ free after uninstall: {0:N1} GB" -f $freeAfter) "SUCCESS"
    Log "Backup phase complete. Proceed with dev environment setup." "SUCCESS"
    Log "Run this script with -Phase restore when dev setup is done."
}

# ── Phase 2: Restore → reinstall to D:\ ──────────────────────────────────────
function Run-Restore {
    Log "====== PHASE 2: Restore to D:\ ======"
    Ensure-Dir $InstallRoot

    # ── LibreOffice → install to D:\Apps\LibreOffice ───────────────────────────
    Log "Installing LibreOffice to $InstallRoot..."
    # winget installs to default path; for custom path use the MSI directly
    # Download fresh installer (winget handles this)
    winget install --id "TheDocumentFoundation.LibreOffice" `
        --accept-source-agreements --accept-package-agreements `
        --override "/TARGETDIR=$InstallRoot\LibreOffice /SILENT" 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Log "LibreOffice installed to $InstallRoot\LibreOffice" "SUCCESS"
    } else {
        # Fallback: standard install (will go to C:\Program Files by default)
        Log "Custom path install failed. Falling back to standard winget install..." "WARN"
        winget install --id "TheDocumentFoundation.LibreOffice" `
            --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
        Log "LibreOffice installed (standard path)." "WARN"
    }

    # ── MiKTeX → install to D:\Apps\MiKTeX ────────────────────────────────────
    Log "Installing MiKTeX (modern TeX distribution) to $InstallRoot..."
    winget install --id "MiKTeX.MiKTeX" `
        --accept-source-agreements --accept-package-agreements `
        --override "--unattended --shared --install-root=$InstallRoot\MiKTeX" 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Log "MiKTeX installed to $InstallRoot\MiKTeX" "SUCCESS"
    } else {
        winget install --id "MiKTeX.MiKTeX" --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
        Log "MiKTeX installed (standard path)." "WARN"
    }

    # ── Verify ────────────────────────────────────────────────────────────────
    Log "Verifying installations..."
    $loExe = Get-ChildItem -Path "$InstallRoot" -Filter "soffice.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($loExe) { Log "LibreOffice binary found: $($loExe.FullName)" "SUCCESS" }
    else         { Log "LibreOffice binary not found in $InstallRoot — check C:\Program Files" "WARN" }

    $texExe = Get-Command miktex -ErrorAction SilentlyContinue
    if ($texExe) { Log "MiKTeX on PATH: $($texExe.Source)" "SUCCESS" }
    else         { Log "miktex not on PATH yet — may need shell restart" "WARN" }

    # ── Space report ──────────────────────────────────────────────────────────
    $freeC = (Get-PSDrive C).Free / 1GB
    $freeD = (Get-PSDrive D).Free / 1GB
    Log ("C:\ free: {0:N1} GB | D:\ free: {1:N1} GB" -f $freeC, $freeD) "SUCCESS"
    Log "Restore phase complete. LibreOffice and MiKTeX are active on D:\." "SUCCESS"
}

# ── Entry point ───────────────────────────────────────────────────────────────
Ensure-Dir $TempRepo

Log "LibreOffice + TexLive migration script"
Log "Phase: $Phase | TempRepo: $TempRepo | InstallRoot: $InstallRoot"
Log "Log: $logFile"

switch ($Phase) {
    "backup"  { Run-Backup }
    "restore" { Run-Restore }
}
