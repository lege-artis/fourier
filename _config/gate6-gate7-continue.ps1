# gate6-gate7-continue.ps1
# Gate 6  -  Docker Desktop + act  |  Gate 7  -  LibreOffice migration
# Run in PowerShell 5.1 (not PS7)  -  paste full block
# ---------------------------------------------------------------

Write-Host "`n=== GATE 6: Docker Desktop + act ===" -ForegroundColor Cyan

# --- 6A: Docker daemon check ---
$dockerOk = $false
try {
    $info = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerOk = $true
        Write-Host "  Docker daemon: RUNNING" -ForegroundColor Green
        docker version --format "  Client: {{.Client.Version}}  |  Server: {{.Server.Engine.Version}}" 2>$null
    } else {
        Write-Host "  Docker daemon: NOT RUNNING" -ForegroundColor Yellow
        Write-Host "  ACTION REQUIRED: Open Docker Desktop from Start menu, wait for whale icon in taskbar," -ForegroundColor Yellow
        Write-Host "  then re-run this script." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  docker not found on PATH" -ForegroundColor Red
}

# --- 6B: act check ---
$actPath = (Get-Command act -ErrorAction SilentlyContinue)
if ($actPath) {
    $actVer = act --version 2>&1
    Write-Host "  act: $actVer" -ForegroundColor Green
} else {
    Write-Host "  act: NOT FOUND  -  installing..." -ForegroundColor Yellow
    winget install --id nektos.act --accept-source-agreements --accept-package-agreements
}

if ($dockerOk) {
    Write-Host "`n  Listing workflow jobs via act..." -ForegroundColor Cyan
    Set-Location "C:\Users\vitez\Documents\VibeCodeProjects"
    act --list 2>&1 | Select-Object -First 30
    Write-Host "`n  Gate 6: COMPLETE" -ForegroundColor Green
} else {
    Write-Host "`n  Gate 6: PENDING  -  start Docker Desktop first, then re-run" -ForegroundColor Yellow
}

# ---------------------------------------------------------------
Write-Host "`n=== GATE 7: LibreOffice D:\ migration ===" -ForegroundColor Cyan

$loPathC86  = "C:\Program Files (x86)\LibreOffice"
$loPathC64  = "C:\Program Files\LibreOffice"
$dDrive     = "D:\"
$loDestD    = "D:\LibreOffice"

# Find installation
$loSource = $null
if (Test-Path $loPathC64) { $loSource = $loPathC64 }
elseif (Test-Path $loPathC86) { $loSource = $loPathC86 }

if (-not $loSource) {
    Write-Host "  LibreOffice not found at standard paths." -ForegroundColor Yellow
    Write-Host "  Checking Add/Remove Programs..." -ForegroundColor Cyan
    Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* 2>$null |
        Where-Object DisplayName -like "*LibreOffice*" |
        Select-Object DisplayName, InstallLocation, DisplayVersion
    Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* 2>$null |
        Where-Object DisplayName -like "*LibreOffice*" |
        Select-Object DisplayName, InstallLocation, DisplayVersion
    Write-Host "  Gate 7: SKIPPED (LibreOffice not installed on C:\)" -ForegroundColor Yellow
} else {
    Write-Host "  Found LibreOffice at: $loSource" -ForegroundColor Green
    $loVersion = (Get-ItemProperty "$loSource\program\soffice.exe").VersionInfo.ProductVersion 2>$null
    Write-Host "  Version: $loVersion"

    # D:\ availability
    if (-not (Test-Path $dDrive)) {
        Write-Host "  D:\ drive not available  -  Gate 7 skipped" -ForegroundColor Yellow
    } else {
        $dFree = (Get-PSDrive D).Free
        $dFreeGB = [math]::Round($dFree / 1GB, 1)
        $loSize = (Get-ChildItem $loSource -Recurse -ErrorAction SilentlyContinue |
                   Measure-Object -Property Length -Sum).Sum
        $loSizeGB = [math]::Round($loSize / 1GB, 2)
        Write-Host "  LibreOffice size on C:\: ${loSizeGB} GB"
        Write-Host "  D:\ free space:          ${dFreeGB} GB"

        if ($dFree -lt $loSize * 1.2) {
            Write-Host "  Not enough free space on D:\   -  Gate 7 skipped" -ForegroundColor Yellow
        } else {
            Write-Host "`n  Copying LibreOffice to D:\..." -ForegroundColor Cyan
            Copy-Item -Path $loSource -Destination $loDestD -Recurse -Force
            Write-Host "  Copy complete." -ForegroundColor Green

            # Uninstall from C:\ via uninstaller
            Write-Host "  Locating uninstaller..." -ForegroundColor Cyan
            $uninstall = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*,
                                          HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* 2>$null |
                         Where-Object DisplayName -like "*LibreOffice*" |
                         Select-Object -First 1 -ExpandProperty UninstallString

            if ($uninstall) {
                Write-Host "  Uninstaller: $uninstall"
                Write-Host "  Run manually with /quiet flag if needed (requires elevation):" -ForegroundColor Yellow
                Write-Host "  $uninstall /quiet" -ForegroundColor White
            }

            # Verify D:\ install by checking soffice.exe
            if (Test-Path "$loDestD\program\soffice.exe") {
                Write-Host "  soffice.exe verified at D:\LibreOffice\program\" -ForegroundColor Green

                # Update PATH
                $machinePath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
                if ($machinePath -notlike "*$loDestD\program*") {
                    $newPath = $machinePath.TrimEnd(";") + ";$loDestD\program"
                    [System.Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
                    Write-Host "  Machine PATH updated: +D:\LibreOffice\program" -ForegroundColor Green
                } else {
                    Write-Host "  PATH already contains D:\LibreOffice\program" -ForegroundColor Green
                }

                Write-Host "`n  Gate 7: COMPLETE" -ForegroundColor Green
                Write-Host "  NOTE: Uninstall C:\ copy manually to reclaim space." -ForegroundColor Yellow
            } else {
                Write-Host "  soffice.exe NOT found at D:\   -  copy may have failed" -ForegroundColor Red
            }
        }
    }
}

# ---------------------------------------------------------------
Write-Host "`n=== Git push: infra docs + connectors ===" -ForegroundColor Cyan
Set-Location "C:\Users\vitez\Documents\VibeCodeProjects"

git add infra/ ml/ 2>&1
$status = git status --short 2>&1
if ($status) {
    Write-Host "  Staged changes:" -ForegroundColor Green
    $status
    git commit -m "feat(infra): add log+ML architecture docs and connector specs" 2>&1
    git push origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Push OK" -ForegroundColor Green
    } else {
        Write-Host "  Push failed - check GH_TOKEN" -ForegroundColor Red
    }
} else {
    Write-Host "  Nothing to commit  -  already up to date" -ForegroundColor Green
    git push origin main 2>&1
}

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "  Gate 6 (Docker): $(if ($dockerOk) { 'DONE' } else { 'PENDING  -  start Docker Desktop' })"
Write-Host "  Gate 7 (LibreOffice): see output above"
Write-Host "  Git push: see output above"
Write-Host ""
Write-Host "  NEXT  -  after Docker Desktop is running:"
Write-Host "  1. Re-run this script to complete Gate 6 (act --list)"
Write-Host "  2. winget install DDEV.DDEV   (WEB-002)"
Write-Host "  3. Run platform validation scripts (PLT-001..006)"
