# Check-SessionEnv.ps1 -- Session-startup environment health probe
# Project: VibeCodeProjects  |  Task: HK-001
#
# PURPOSE
#   Run at the START of every ThinkPad dev/test session.
#   Verifies all active infrastructure components and writes a one-line
#   status summary to the console.  Exit code 0 = all green, 1 = degraded.
#
# CHECKS
#   LDE stack  : kh-rust/scala/cpp/fortran/pascal (:8001-8005), log-service (:8006),
#                plantuml (:8010), keycloak (:8090/realms/master)
#                NOTE: KC24 health endpoint is on mgmt port 9000 (container-internal).
#                      Host-side probe uses /realms/master on port 8090.
#   ELK stack  : elasticsearch (:9200), kibana (:5601), fluent-bit (:2020)
#   MongoDB    : Windows service "MongoDB" + TCP :27017
#   Git state  : active branch NOT main, remote origin reachable
#
# USAGE
#   .\Check-SessionEnv.ps1                     # full check, exit 0/1
#   .\Check-SessionEnv.ps1 -Stack lde          # LDE only
#   .\Check-SessionEnv.ps1 -Stack elk          # ELK only
#   .\Check-SessionEnv.ps1 -Stack all          # LDE + ELK + MongoDB + Git (default)
#   .\Check-SessionEnv.ps1 -UpdateHandoff      # append status block to SESSION-HANDOFF.md
#
# NOTE: ASCII-only characters throughout -- PS 5.1 parse errors on em dashes.
#       Do NOT introduce UTF-8 em dashes or smart quotes.

[CmdletBinding()]
param(
    [ValidateSet("lde","elk","all")]
    [string]$Stack = "all",

    [switch]$UpdateHandoff      # Append env snapshot to SESSION-HANDOFF.md
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"   # Don't abort on probe failures

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$HandoffFile = Join-Path $ScriptDir "SESSION-HANDOFF.md"

# ── Colour helpers ────────────────────────────────────────────────────────────
function Write-Header([string]$Text) {
    $line = "-" * 62
    Write-Host ""
    Write-Host $line -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor DarkCyan
}
function Write-OK([string]$Text)   { Write-Host "  [OK]   $Text" -ForegroundColor Green  }
function Write-FAIL([string]$Text) { Write-Host "  [FAIL] $Text" -ForegroundColor Red    }
function Write-WARN([string]$Text) { Write-Host "  [WARN] $Text" -ForegroundColor Yellow }
function Write-INFO([string]$Text) { Write-Host "  [INFO] $Text" -ForegroundColor Gray   }

# ── HTTP probe (returns $true/$false, no throw) ───────────────────────────────
function Test-Http {
    param([string]$Url, [int]$TimeoutSec = 4)
    try {
        $r = Invoke-WebRequest -Uri $Url -UseBasicParsing `
                -TimeoutSec $TimeoutSec -ErrorAction Stop
        return ($r.StatusCode -lt 400)
    } catch {
        return $false
    }
}

# ── TCP probe (for MongoDB :27017) ────────────────────────────────────────────
function Test-Tcp {
    # NOTE: do NOT name the host param $Host -- that is a PowerShell automatic variable
    # (holds the host UI object) and is read-only inside function scope.
    param([string]$Hostname = "localhost", [int]$Port, [int]$TimeoutMs = 2000)
    try {
        $tcp = [System.Net.Sockets.TcpClient]::new()
        $ar  = $tcp.BeginConnect($Hostname, $Port, $null, $null)
        $ok  = $ar.AsyncWaitHandle.WaitOne($TimeoutMs)
        if ($ok -and $tcp.Connected) { $tcp.Close(); return $true }
        $tcp.Close(); return $false
    } catch { return $false }
}

# ── Counters ──────────────────────────────────────────────────────────────────
$totalChecks = 0
$passChecks  = 0
$results     = [System.Collections.Generic.List[PSCustomObject]]::new()

function Record {
    param([string]$Component, [string]$Target, [bool]$Pass, [string]$Note = "")
    $script:totalChecks++
    if ($Pass) { $script:passChecks++ }
    $obj = [PSCustomObject]@{
        Component = $Component
        Target    = $Target
        Pass      = $Pass
        Note      = $Note
    }
    $script:results.Add($obj)
    if ($Pass) { Write-OK  "$Component  -->  $Target$(if($Note){`"  ($Note)`"})" }
    else        { Write-FAIL "$Component  -->  $Target$(if($Note){`"  ($Note)`"})" }
}

# ── LDE stack probe ───────────────────────────────────────────────────────────
function Invoke-LdeCheck {
    Write-Header "LDE Stack (KH-Sim backends + log service + PlantUML)"
    $endpoints = [ordered]@{
        "kh-rust"         = "http://localhost:8001/health"
        "kh-scala"        = "http://localhost:8002/health"
        "kh-cpp"          = "http://localhost:8003/health"
        "kh-fortran"      = "http://localhost:8004/health"
        "kh-pascal"       = "http://localhost:8005/health"
        "kh-log-service"  = "http://localhost:8006/health"
        "plantuml-server" = "http://localhost:8010"
        "keycloak"        = "http://localhost:8090/realms/master"
    }
    foreach ($svc in $endpoints.Keys) {
        $url  = $endpoints[$svc]
        $pass = Test-Http -Url $url
        Record -Component $svc -Target $url -Pass $pass
    }
}

# ── ELK stack probe ───────────────────────────────────────────────────────────
function Invoke-ElkCheck {
    Write-Header "ELK Stack (Elasticsearch + Kibana + Fluent Bit)"
    $endpoints = [ordered]@{
        "elasticsearch" = "http://localhost:9200/_cluster/health"
        "kibana"        = "http://localhost:5601/api/status"
        "fluent-bit"    = "http://localhost:2020/api/v1/health"
    }
    foreach ($svc in $endpoints.Keys) {
        $url  = $endpoints[$svc]
        $pass = Test-Http -Url $url
        Record -Component $svc -Target $url -Pass $pass
    }
}

# ── MongoDB probe ─────────────────────────────────────────────────────────────
function Invoke-MongoCheck {
    Write-Header "MongoDB"

    # Windows service check
    $svc = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
    $svcOk = ($null -ne $svc -and $svc.Status -eq "Running")
    Record -Component "MongoDB service" -Target "Windows service 'MongoDB'" -Pass $svcOk `
           -Note $(if ($svc) { $svc.Status } else { "service not found" })

    # TCP port probe
    $tcpOk = Test-Tcp -Hostname "localhost" -Port 27017
    Record -Component "MongoDB TCP"    -Target "localhost:27017"              -Pass $tcpOk
}

# ── Git state probe ───────────────────────────────────────────────────────────
function Invoke-GitCheck {
    Write-Header "Git Workspace State"

    Push-Location $ProjectRoot
    try {
        # Active branch -- must not be main
        $branch = (git rev-parse --abbrev-ref HEAD 2>&1).Trim()
        $branchOk = ($branch -ne "main" -and $branch -ne "master" -and $branch -ne "")
        Record -Component "Git branch" -Target $branch `
               -Pass $branchOk `
               -Note $(if (-not $branchOk) { "WARNING: on protected branch!" } else { "not main -- OK" })

        # Remote origin reachable (ls-remote with 5s timeout via git)
        $lsOut  = git ls-remote --exit-code origin HEAD 2>&1
        $remoteOk = ($LASTEXITCODE -eq 0)
        Record -Component "Git remote" -Target "origin" -Pass $remoteOk `
               -Note $(if ($remoteOk) { "reachable" } else { "unreachable or no network" })

        # Uncommitted changes (warn only, not a failure)
        $dirty = (git status --porcelain 2>&1)
        if ($dirty) {
            Write-WARN "Uncommitted changes present ($( ($dirty -split "`n").Count ) files)"
        } else {
            Write-INFO "Working tree clean."
        }

    } finally {
        Pop-Location
    }
}

# ── Main ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkCyan
Write-Host "  Check-SessionEnv.ps1  --  VibeCodeProjects startup probe" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')   Stack: $($Stack.ToUpper())" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor DarkCyan

switch ($Stack) {
    "lde" {
        Invoke-LdeCheck
    }
    "elk" {
        Invoke-ElkCheck
        Invoke-MongoCheck
    }
    "all" {
        Invoke-LdeCheck
        Invoke-ElkCheck
        Invoke-MongoCheck
        Invoke-GitCheck
    }
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkCyan
$allPass = ($passChecks -eq $totalChecks)
if ($allPass) {
    Write-Host ("  RESULT: {0}/{1} checks PASSED -- environment GREEN" -f $passChecks, $totalChecks) `
        -ForegroundColor Green
} else {
    $failCount = $totalChecks - $passChecks
    Write-Host ("  RESULT: {0} of {1} checks FAILED -- environment DEGRADED" -f $failCount, $totalChecks) `
        -ForegroundColor Red
    Write-Host "  Run:  .\_config\Start-LocalEnv.ps1 -Action up -Stack all  to restore." `
        -ForegroundColor Yellow
}
Write-Host "================================================================" -ForegroundColor DarkCyan
Write-Host ""

# ── Optional SESSION-HANDOFF.md update ────────────────────────────────────────
if ($UpdateHandoff) {
    $ts     = Get-Date -Format "yyyy-MM-dd HH:mm"
    $status = if ($allPass) { "GREEN" } else { "DEGRADED" }

    $block = @"

---
## Session-Start Env Snapshot -- $ts

| Component | Target | Status |
|---|---|---|
"@
    foreach ($r in $results) {
        $mark = if ($r.Pass) { "OK" } else { "FAIL" }
        $note = if ($r.Note) { " ($($r.Note))" } else { "" }
        $block += "`n| $($r.Component) | $($r.Target)$note | $mark |"
    }
    $block += "`n`n**Overall: $status ($passChecks/$totalChecks)**`n"

    Add-Content -Path $HandoffFile -Value $block -Encoding UTF8
    Write-INFO "Env snapshot appended to SESSION-HANDOFF.md"
}

exit $(if ($allPass) { 0 } else { 1 })
