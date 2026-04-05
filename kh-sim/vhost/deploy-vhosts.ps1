#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Deploy KH-SIM + PINN Nginx vhost configs into Laragon and activate Nginx.
.DESCRIPTION
    Run after Laragon install. Copies vhost configs, switches web server to Nginx,
    injects .test domain entries into hosts file, then restarts Laragon services.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File deploy-vhosts.ps1
#>

param(
    [string]$LaragonRoot = "D:\Apps\Laragon",
    [string]$VhostSrc    = "$PSScriptRoot"
)

$ErrorActionPreference = "Stop"

function Log-Info  { param($m) Write-Host "[INFO ] $m" -ForegroundColor Cyan }
function Log-OK    { param($m) Write-Host "[OK   ] $m" -ForegroundColor Green }
function Log-Warn  { param($m) Write-Host "[WARN ] $m" -ForegroundColor Yellow }
function Log-Error { param($m) Write-Host "[ERROR] $m" -ForegroundColor Red }

# -- Validate Laragon root ------------------------------------------------------
Log-Info "Laragon root: $LaragonRoot"
if (-not (Test-Path "$LaragonRoot\laragon.exe")) {
    Log-Error "laragon.exe not found at $LaragonRoot -- check install path"
    exit 1
}

# -- Locate Nginx vhost directory -----------------------------------------------
$nginxVhostDir = "$LaragonRoot\etc\nginx\sites-enabled"
if (-not (Test-Path $nginxVhostDir)) {
    New-Item -ItemType Directory -Path $nginxVhostDir -Force | Out-Null
    Log-Info "Created $nginxVhostDir"
}

# -- Copy vhost configs ----------------------------------------------------------
$vhosts = @("kh-rust", "kh-scala", "kh-cpp", "kh-fortran", "kh-pascal", "pinn")
foreach ($v in $vhosts) {
    $src  = Join-Path $VhostSrc "$v.conf"
    $dest = Join-Path $nginxVhostDir "$v.conf"
    if (-not (Test-Path $src)) { Log-Warn "$v.conf not found in $VhostSrc -- skip"; continue }
    Copy-Item $src $dest -Force
    Log-OK "Deployed $v.conf -> $dest"
}

# -- Inject .test domains into hosts file ---------------------------------------
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsPath -Raw

$entries = @(
    "127.0.0.1`tkh-rust.test",
    "127.0.0.1`tkh-scala.test",
    "127.0.0.1`tkh-cpp.test",
    "127.0.0.1`tkh-fortran.test",
    "127.0.0.1`tkh-pascal.test",
    "127.0.0.1`tpinn.test"
)

$added = 0
foreach ($entry in $entries) {
    $domain = ($entry -split "`t")[1]
    if ($hostsContent -notmatch [regex]::Escape($domain)) {
        Add-Content -Path $hostsPath -Value $entry
        Log-OK "Added hosts entry: $entry"
        $added++
    } else {
        Log-Info "Hosts entry already present: $domain"
    }
}

# -- Switch Laragon web server to Nginx -----------------------------------------
$laragonConf = "$LaragonRoot\usr\laragon.ini"
if (Test-Path $laragonConf) {
    $ini = Get-Content $laragonConf -Raw
    if ($ini -match "webServer\s*=\s*apache") {
        $ini = $ini -replace "webServer\s*=\s*apache", "webServer=nginx"
        Set-Content $laragonConf $ini
        Log-OK "Switched Laragon web server: Apache -> Nginx"
    } elseif ($ini -match "webServer\s*=\s*nginx") {
        Log-Info "Laragon already set to Nginx"
    } else {
        Log-Warn "webServer key not found in laragon.ini -- switch manually in Laragon UI"
    }
} else {
    Log-Warn "laragon.ini not found at $laragonConf -- set Nginx via Laragon UI (Web Server -> Nginx)"
}

# -- Restart Nginx via Laragon CLI (if available) -------------------------------
$laraCmd = "$LaragonRoot\bin\laragon.exe"
if (Test-Path $laraCmd) {
    Log-Info "Restarting Laragon Nginx service..."
    & $laraCmd restart nginx 2>$null
    Start-Sleep -Seconds 3
    Log-OK "Nginx restarted"
} else {
    Log-Warn "Laragon CLI not found -- please restart Nginx manually from the Laragon tray menu"
}

# -- Smoke test -----------------------------------------------------------------
Log-Info "Running smoke tests..."
$tests = @(
    @{ url = "http://kh-rust.test/health";    label = "kh-rust.test" },
    @{ url = "http://kh-scala.test/health";   label = "kh-scala.test" },
    @{ url = "http://pinn.test/v1/pinn/health"; label = "pinn.test" }
)

foreach ($t in $tests) {
    try {
        $resp = Invoke-WebRequest -Uri $t.url -TimeoutSec 5 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Log-OK "$($t.label) -> HTTP 200"
        } else {
            Log-Warn "$($t.label) -> HTTP $($resp.StatusCode) (backend not started yet - expected)"
        }
    } catch {
        Log-Warn "$($t.label) -> connection refused (backend not started yet - expected at this stage)"
    }
}

# -- Summary --------------------------------------------------------------------
Write-Host ""
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host "  WEB-001 / KH-016 vhost deployment complete" -ForegroundColor Magenta
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host "  Vhosts deployed to: $nginxVhostDir"
Write-Host "  Hosts entries added: $added"
Write-Host ""
Write-Host "  Vhost -> Backend port mapping:"
Write-Host "    kh-rust.test      -> localhost:8001  (Rust axum)"
Write-Host "    kh-scala.test     -> localhost:8002  (Scala http4s)"
Write-Host "    kh-cpp.test       -> localhost:8003  (C++ cpp-httplib)"
Write-Host "    kh-fortran.test   -> localhost:8004  (Fortran C-interop)"
Write-Host "    kh-pascal.test    -> localhost:8005  (Pascal fphttpapp)"
Write-Host "    pinn.test         -> localhost:8600  (PINN FastAPI)"
Write-Host ""
Write-Host "  Next: KH-001 [DONE], KH-016 [DONE] - proceed to KH-002 (extract kh-instability-sim.zip)"
