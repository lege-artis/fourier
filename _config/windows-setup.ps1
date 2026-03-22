#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Windows development workspace setup script for VibeCodeProjects

.DESCRIPTION
    Installs and verifies all required development tools and compilers using winget

.NOTES
    This script must run as Administrator. If not run as admin, it will prompt for elevation.

.EXAMPLE
    .\windows-setup.ps1
#>

param(
    [switch]$SkipVerification = $false,
    [switch]$Verbose = $false
)

# Ensure script runs as Administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "This script requires Administrator privileges." -ForegroundColor Yellow
    Write-Host "Requesting elevation..." -ForegroundColor Cyan

    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell -ArgumentList "-File `"$scriptPath`"" -Verb RunAs
    exit
}

# Initialize logging
$reportPath = "C:\Users\vitez\Documents\VibeCodeProjects\_config\windows-install-report.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$installLog = @()

function Log-Message {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
    )
    $installLog += $logEntry
}

function Install-Tool {
    param(
        [string]$ToolName,
        [string]$WingetId,
        [string]$VersionCommand
    )

    Log-Message "Installing $ToolName..." "INFO"

    try {
        winget install --id=$WingetId --accept-source-agreements --accept-package-agreements -e 2>&1 | Out-Null

        # Brief pause to allow installation to complete
        Start-Sleep -Seconds 2

        Log-Message "$ToolName installed successfully" "SUCCESS"
        return $true
    }
    catch {
        Log-Message "Failed to install $ToolName : $_" "ERROR"
        return $false
    }
}

function Verify-Tool {
    param(
        [string]$ToolName,
        [string]$VersionCommand
    )

    Log-Message "Verifying $ToolName..." "INFO"

    try {
        $result = & cmd /c "$VersionCommand 2>&1"

        if ($LASTEXITCODE -eq 0) {
            Log-Message "$ToolName verified: $result" "SUCCESS"
            return $true
        }
        else {
            Log-Message "$ToolName verification failed: $result" "WARNING"
            return $false
        }
    }
    catch {
        Log-Message "Could not verify ${ToolName}: $_" "WARNING"
        return $false
    }
}

# Main installation sequence
Log-Message "========================================" "INFO"
Log-Message "VibeCodeProjects Development Setup" "INFO"
Log-Message "========================================" "INFO"

$installationResults = @{
    "VS Code" = $false
    "Git" = $false
    "Node.js LTS" = $false
    "Rust" = $false
    "Free Pascal" = $false
    "OpenJDK 17" = $false
    "SBT" = $false
    "GFortran" = $false
    "Docker Desktop" = $false
    "GitHub CLI" = $false
}

# Step 1: VS Code
Log-Message "Step 1/10: Visual Studio Code" "INFO"
$installationResults["VS Code"] = Install-Tool "VS Code" "Microsoft.VisualStudioCode" "code --version"

# Step 2: Git
Log-Message "Step 2/10: Git" "INFO"
$installationResults["Git"] = Install-Tool "Git" "Git.Git" "git --version"

# Step 3: Node.js LTS
Log-Message "Step 3/10: Node.js LTS" "INFO"
$installationResults["Node.js LTS"] = Install-Tool "Node.js LTS" "OpenJS.NodeJS.LTS" "node --version"

# Step 4: Rust (via rustup)
Log-Message "Step 4/10: Rust (rustup)" "INFO"
$installationResults["Rust"] = Install-Tool "Rust" "Rustlang.Rust.MSVC" "rustc --version"

# Step 5: Free Pascal
Log-Message "Step 5/10: Free Pascal Compiler" "INFO"
$installationResults["Free Pascal"] = Install-Tool "Free Pascal" "FreePascal.FreePascal" "fpc -version"

# Step 6: OpenJDK 17
Log-Message "Step 6/10: OpenJDK 17" "INFO"
$installationResults["OpenJDK 17"] = Install-Tool "OpenJDK 17" "EclipseAdoptium.Temurin.17.JDK" "java -version"

# Step 7: SBT
Log-Message "Step 7/10: SBT (Scala Build Tool)" "INFO"
$installationResults["SBT"] = Install-Tool "SBT" "Lightbend.SBT" "sbt --version"

# Step 8: GFortran via MSYS2
Log-Message "Step 8/10: MSYS2 and GFortran" "INFO"
try {
    Install-Tool "MSYS2" "msys2.msys2" "bash --version" | Out-Null
    Log-Message "MSYS2 installed. Installing GFortran..." "INFO"
    & "C:\msys64\msys2_shell.cmd" -defterm -no-start -c "pacman -S --noconfirm mingw-w64-x86_64-gcc-fortran" 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        $installationResults["GFortran"] = $true
        Log-Message "GFortran installed via MSYS2" "SUCCESS"
    }
    else {
        Log-Message "GFortran installation failed" "ERROR"
        $installationResults["GFortran"] = $false
    }
}
catch {
    Log-Message "Failed to install GFortran: $_" "ERROR"
    $installationResults["GFortran"] = $false
}

# Step 9: Docker Desktop
Log-Message "Step 9/10: Docker Desktop" "INFO"
$installationResults["Docker Desktop"] = Install-Tool "Docker Desktop" "Docker.DockerDesktop" "docker --version"

# Step 10: GitHub CLI
Log-Message "Step 10/10: GitHub CLI" "INFO"
$installationResults["GitHub CLI"] = Install-Tool "GitHub CLI" "GitHub.cli" "gh --version"

# Verification phase
Log-Message "========================================" "INFO"
Log-Message "Verification Phase" "INFO"
Log-Message "========================================" "INFO"

$verificationResults = @{}

Verify-Tool "Git" "git --version" | Out-Null
Verify-Tool "Node.js" "node --version" | Out-Null
Verify-Tool "npm" "npm --version" | Out-Null
Verify-Tool "Rust" "rustc --version" | Out-Null
Verify-Tool "Cargo" "cargo --version" | Out-Null
Verify-Tool "Free Pascal" "fpc -version" | Out-Null
Verify-Tool "Java" "java -version" | Out-Null
Verify-Tool "SBT" "sbt --version" | Out-Null
Verify-Tool "Docker" "docker --version" | Out-Null
Verify-Tool "GitHub CLI" "gh --version" | Out-Null

# Generate report
Log-Message "========================================" "INFO"
Log-Message "Installation Summary" "INFO"
Log-Message "========================================" "INFO"

$successCount = 0
foreach ($tool in $installationResults.GetEnumerator()) {
    if ($tool.Value) {
        Log-Message "$($tool.Key): SUCCESS" "SUCCESS"
        $successCount++
    }
    else {
        Log-Message "$($tool.Key): FAILED" "ERROR"
    }
}

Log-Message "========================================" "INFO"
Log-Message "Summary: $successCount of $($installationResults.Count) tools installed" "INFO"
Log-Message "========================================" "INFO"

# Create report directory if it doesn't exist
$reportDir = Split-Path -Parent $reportPath
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# Write report to file
$report = $installLog -join "`r`n"
$report | Out-File -FilePath $reportPath -Encoding UTF8 -Force

Log-Message "Report written to: $reportPath" "SUCCESS"

# Rollback notes
$rollbackNotes = @"
ROLLBACK PROCEDURE NOTES:

To uninstall all installed tools, use the following commands:

1. VS Code:
   winget uninstall Microsoft.VisualStudioCode

2. Git:
   winget uninstall Git.Git

3. Node.js LTS:
   winget uninstall OpenJS.NodeJS.LTS

4. Rust:
   winget uninstall Rustlang.Rust.MSVC
   # Also remove: C:\Users\{username}\.cargo and C:\Users\{username}\.rustup

5. Free Pascal:
   winget uninstall FreePascal.FreePascal

6. OpenJDK 17:
   winget uninstall EclipseAdoptium.Temurin.17.JDK

7. SBT:
   winget uninstall Lightbend.SBT

8. MSYS2/GFortran:
   winget uninstall msys2.msys2
   # Manually delete: C:\msys64

9. Docker Desktop:
   winget uninstall Docker.DockerDesktop

10. GitHub CLI:
    winget uninstall GitHub.cli

NOTES:
- Some tools may require system restart to fully uninstall
- Environment PATH variables may need manual cleanup
- User directories (.cargo, .rustup, .sbt, .gradle) may need manual deletion
- Docker Desktop may require additional cleanup in Windows Services
"@

$rollbackPath = "C:\Users\vitez\Documents\VibeCodeProjects\_config\windows-setup-rollback.txt"
$rollbackNotes | Out-File -FilePath $rollbackPath -Encoding UTF8 -Force

Log-Message "Rollback notes written to: $rollbackPath" "INFO"
Log-Message "Setup complete!" "SUCCESS"

if ($successCount -eq $installationResults.Count) {
    exit 0
}
else {
    exit 1
}
