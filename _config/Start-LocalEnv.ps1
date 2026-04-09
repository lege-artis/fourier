# Start-LocalEnv.ps1  --  Local development environment controller
# Project: VibeCodeProjects / KH-Sim  |  Tasks: LDE-001..004, LOG-001..003
#
# SYNOPSIS
#   Unified wrapper for docker compose stacks.
#   -Stack lde  (default): KH-sim backends + PlantUML diagram server
#   -Stack elk:            Elasticsearch + Kibana + Fluent Bit log pipeline
#   -Stack all:            Both stacks together
#
# LDE stack services:
#   kh-rust          :8001
#   kh-scala         :8002
#   kh-cpp           :8003
#   kh-fortran       :8004
#   kh-pascal        :8005
#   kh-log-service   :8006
#   plantuml-server  :8010
#
# ELK stack services:
#   elasticsearch    :9200
#   kibana           :5601
#   fluent-bit       :24224 (TCP input), :2020 (HTTP API)
#
# USAGE
#   .\Start-LocalEnv.ps1 -Action up                # Start LDE stack (default)
#   .\Start-LocalEnv.ps1 -Action up -Stack elk     # Start ELK stack
#   .\Start-LocalEnv.ps1 -Action up -Stack all     # Start both stacks
#   .\Start-LocalEnv.ps1 -Action down              # Stop LDE stack
#   .\Start-LocalEnv.ps1 -Action down -Stack elk   # Stop ELK stack
#   .\Start-LocalEnv.ps1 -Action status            # Show LDE container state
#   .\Start-LocalEnv.ps1 -Action health            # HTTP health-check active stack
#   .\Start-LocalEnv.ps1 -Action build             # Rebuild images
#   .\Start-LocalEnv.ps1 -Action logs              # Tail logs (Ctrl+C to exit)
#   .\Start-LocalEnv.ps1 -Action restart           # Stop then start
#   .\Start-LocalEnv.ps1 -Action restart -Service kh-rust  # Single service
#
# REQUIREMENTS
#   Docker Desktop running (or Docker Engine on WSL2)
#   PowerShell 5.1+ or PowerShell 7+
#
# NOTE: ASCII-only characters throughout -- PS 5.1 parse errors on em dashes.
#       Do NOT introduce UTF-8 em dashes or smart quotes.

[CmdletBinding()]
param(
    [ValidateSet("up","down","status","health","build","logs","restart")]
    [string]$Action = "up",

    [ValidateSet("lde","elk","all")]
    [string]$Stack = "lde",         # Which compose stack to operate on

    [string]$Service = "",          # Optional: target a single service

    [switch]$NoHealthCheck,         # Skip post-start health check

    [int]$HealthTimeout = 120       # Seconds to wait for services to become healthy
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Paths ─────────────────────────────────────────────────────────────────────
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeLDE  = Join-Path $ProjectRoot "infra\docker\docker-compose.r0-lde.yml"
$ComposeELK  = Join-Path $ProjectRoot "infra\docker\elasticsearch\docker-compose.yml"

# Select active compose file based on -Stack
switch ($Stack) {
    "lde" { $ComposeFile = $ComposeLDE }
    "elk" { $ComposeFile = $ComposeELK }
    "all" { $ComposeFile = $ComposeLDE }   # primary; ELK handled separately in dispatch
}

if (-not (Test-Path $ComposeLDE)) {
    Write-Error "LDE compose file not found: $ComposeLDE"
    exit 1
}
if (($Stack -eq "elk" -or $Stack -eq "all") -and -not (Test-Path $ComposeELK)) {
    Write-Error "ELK compose file not found: $ComposeELK"
    exit 1
}

# ── Service health maps ────────────────────────────────────────────────────────
$HealthMapLDE = [ordered]@{
    "kh-rust"          = "http://localhost:8001/health"
    "kh-scala"         = "http://localhost:8002/health"
    "kh-cpp"           = "http://localhost:8003/health"
    "kh-fortran"       = "http://localhost:8004/health"
    "kh-pascal"        = "http://localhost:8005/health"
    "kh-log-service"   = "http://localhost:8006/health"
    "plantuml-server"  = "http://localhost:8010"
}

$HealthMapELK = [ordered]@{
    "elasticsearch"    = "http://localhost:9200/_cluster/health"
    "kibana"           = "http://localhost:5601/api/status"
    "fluent-bit"       = "http://localhost:2020/api/v1/health"
}

switch ($Stack) {
    "lde" { $HealthMap = $HealthMapLDE }
    "elk" { $HealthMap = $HealthMapELK }
    "all" {
        $HealthMap = [ordered]@{}
        foreach ($k in $HealthMapLDE.Keys) { $HealthMap[$k] = $HealthMapLDE[$k] }
        foreach ($k in $HealthMapELK.Keys) { $HealthMap[$k] = $HealthMapELK[$k] }
    }
}

# ── Helpers ────────────────────────────────────────────────────────────────────
function Write-Header([string]$Text) {
    $line = "-" * 60
    Write-Host ""
    Write-Host $line -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor DarkCyan
}

function Write-OK([string]$Text)   { Write-Host "  [OK]   $Text" -ForegroundColor Green  }
function Write-FAIL([string]$Text) { Write-Host "  [FAIL] $Text" -ForegroundColor Red    }
function Write-INFO([string]$Text) { Write-Host "  [INFO] $Text" -ForegroundColor Yellow }

function Invoke-Compose {
    # NOTE: do NOT name this param $Args -- that is a PowerShell automatic variable
    # (holds unbound positional args) and always resolves to empty inside a param block,
    # silently dropping the subcommand and causing docker compose to print help.
    param(
        [string[]]$CmdArgs,
        [string]$File = $ComposeFile
    )
    $allArgs = @("-f", $File) + $CmdArgs
    Write-INFO "docker compose $($allArgs -join ' ')"
    & docker compose @allArgs
    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "docker compose exited with code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

function Test-DockerRunning {
    $null = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "Docker is not running. Start Docker Desktop and retry."
        exit 1
    }
}

function Invoke-HealthChecks {
    $stackLabel = $Stack.ToUpper()
    Write-Header "Health Check -- $stackLabel services"

    $deadline = (Get-Date).AddSeconds($HealthTimeout)
    $results  = @{}

    foreach ($svc in $HealthMap.Keys) {
        $results[$svc] = $false
    }

    # Poll until all pass or timeout
    $allPassed = $false
    while ((Get-Date) -lt $deadline) {
        $pending = @()
        foreach ($svc in $HealthMap.Keys) {
            if ($results[$svc]) { continue }
            $url = $HealthMap[$svc]
            try {
                $resp = Invoke-WebRequest -Uri $url -UseBasicParsing `
                        -TimeoutSec 3 -ErrorAction Stop
                if ($resp.StatusCode -lt 400) {
                    $results[$svc] = $true
                } else {
                    $pending += $svc
                }
            } catch {
                $pending += $svc
            }
        }
        if ($pending.Count -eq 0) {
            $allPassed = $true
            break
        }
        Write-INFO "Waiting for: $($pending -join ', ')  (${HealthTimeout}s budget)"
        Start-Sleep -Seconds 5
    }

    # Print final results
    $passCount = 0
    foreach ($svc in $HealthMap.Keys) {
        $url = $HealthMap[$svc]
        if ($results[$svc]) {
            Write-OK  "$svc  -->  $url"
            $passCount++
        } else {
            Write-FAIL "$svc  -->  $url  [no response within ${HealthTimeout}s]"
        }
    }

    Write-Host ""
    if ($allPassed) {
        Write-OK  "All $($HealthMap.Count) services healthy -- $stackLabel ready."
    } else {
        $failCount = $HealthMap.Count - $passCount
        Write-FAIL "$failCount of $($HealthMap.Count) services did not respond."
        Write-INFO "Run:  docker compose -f $ComposeFile logs  to diagnose."
    }
    return $allPassed
}

# ── Main dispatch ──────────────────────────────────────────────────────────────
Test-DockerRunning

switch ($Action) {

    "up" {
        Write-Header "Starting $($Stack.ToUpper()) stack"
        if ($Stack -eq "all") {
            $upArgs = @("up", "-d")
            if ($Service) { $upArgs += $Service }
            Invoke-Compose -CmdArgs $upArgs -File $ComposeLDE
            Invoke-Compose -CmdArgs $upArgs -File $ComposeELK
            # fluent-bit mounts a config file -- Docker does not detect bind-mount
            # content changes, so force-recreate ensures the latest config is loaded.
            if (-not $Service -or $Service -eq "fluent-bit") {
                Write-INFO "Force-recreating fluent-bit to pick up latest config..."
                Invoke-Compose -CmdArgs @("up", "-d", "--force-recreate", "fluent-bit") -File $ComposeELK
            }
        } elseif ($Stack -eq "elk") {
            $upArgs = @("up", "-d")
            if ($Service) { $upArgs += $Service }
            Invoke-Compose $upArgs
            # Force-recreate fluent-bit so mounted fluent-bit.conf is always fresh.
            if (-not $Service -or $Service -eq "fluent-bit") {
                Write-INFO "Force-recreating fluent-bit to pick up latest config..."
                Invoke-Compose -CmdArgs @("up", "-d", "--force-recreate", "fluent-bit")
            }
        } else {
            $upArgs = @("up", "-d")
            if ($Service) { $upArgs += $Service }
            Invoke-Compose $upArgs
        }
        if (-not $NoHealthCheck) {
            $ok = Invoke-HealthChecks
            if (-not $ok) { exit 1 }
        }
    }

    "down" {
        Write-Header "Stopping $($Stack.ToUpper()) stack"
        if ($Stack -eq "all") {
            $downArgs = @("down")
            if ($Service) { $downArgs += $Service }
            Invoke-Compose -CmdArgs $downArgs -File $ComposeLDE
            Invoke-Compose -CmdArgs $downArgs -File $ComposeELK
        } else {
            $downArgs = @("down")
            if ($Service) { $downArgs += $Service }
            Invoke-Compose $downArgs
        }
        Write-OK "Stack stopped."
    }

    "status" {
        Write-Header "$($Stack.ToUpper()) container status"
        if ($Stack -eq "all") {
            Invoke-Compose -CmdArgs @("ps") -File $ComposeLDE
            Invoke-Compose -CmdArgs @("ps") -File $ComposeELK
        } else {
            Invoke-Compose @("ps")
        }
    }

    "health" {
        $ok = Invoke-HealthChecks
        if (-not $ok) { exit 1 }
    }

    "build" {
        Write-Header "Building $($Stack.ToUpper()) images"
        $buildArgs = @("build")
        if ($Service) { $buildArgs += $Service }
        Invoke-Compose $buildArgs
        Write-OK "Build complete. Run: .\Start-LocalEnv.ps1 -Action up -Stack $Stack"
    }

    "logs" {
        Write-Header "Streaming $($Stack.ToUpper()) logs (Ctrl+C to exit)"
        $logsArgs = @("logs", "-f")
        if ($Service) { $logsArgs += $Service }
        Invoke-Compose $logsArgs
    }

    "restart" {
        Write-Header "Restarting $($Stack.ToUpper()) stack"
        $downArgs = @("down")
        if ($Service) { $downArgs += $Service }
        Invoke-Compose $downArgs

        $upArgs = @("up", "-d")
        if ($Service) { $upArgs += $Service }
        Invoke-Compose $upArgs

        if (-not $NoHealthCheck) {
            $ok = Invoke-HealthChecks
            if (-not $ok) { exit 1 }
        }
    }
}
