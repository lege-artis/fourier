<#
.SYNOPSIS
    GEN-013 -- VS Code IDE setup for ThinkPad (VibeCodeProjects).

.DESCRIPTION
    Installs all required VS Code extensions for the active language stack
    (Rust, Scala, C++, Fortran, Pascal, Python) plus Git integration and
    diagram tooling (PlantUML, draw.io).

    Does NOT require Administrator privileges -- code --install-extension
    operates per-user.

.NOTES
    Part of release R0 -- Infrastructure Baseline.
    Task registry: GEN-013 (TASKS-shared.yaml v1.6.1+)
    Run from any PowerShell terminal (no elevation needed).

.EXAMPLE
    .\vscode-extensions-setup.ps1
    .\vscode-extensions-setup.ps1 -Verify    # audit only, no installs
#>

param(
    [switch]$Verify   # Run verification pass only (no installs)
)

# ---------------------------------------------------------------------------
# Extension manifest  (ASCII strings only -- no em dashes)
# ---------------------------------------------------------------------------
$extensions = [ordered]@{

    # Language servers
    "rust-lang.rust-analyzer"             = "Rust: rust-analyzer LSP"
    "scalameta.metals"                    = "Scala: Metals LSP"
    "ms-vscode.cpptools"                  = "C/C++: Microsoft IntelliSense + debugger"
    "hansec.fortran-ls"                   = "Fortran: fortls language server"
    "Wosi.omnipascal"                     = "Pascal: OmniPascal (FPC 3.2.2)"
    "ms-python.python"                    = "Python: Pylance + debugger (PINN scripts)"

    # Git integration
    "eamodio.gitlens"                     = "GitLens: blame, history, branch compare"
    "mhutchie.git-graph"                  = "Git Graph: cross-device branch visualisation"
    "vivaxy.vscode-conventional-commits"  = "Conventional Commits: semantic commit helper"

    # Diagram tooling
    "hediet.vscode-drawio"                = "draw.io: C4 structural + dashboard wireframes"
    "jebbs.plantuml"                      = "PlantUML: sequence/component/ADR diagrams"
}

# ---------------------------------------------------------------------------
# Acceptance-test map -- file to open per language server
# ---------------------------------------------------------------------------
$acceptancePaths = @{
    "rust-lang.rust-analyzer" = "kh-sim\backends\rust\src\main.rs"
    "scalameta.metals"        = "kh-sim\backends\scala\src\main\scala\khsim\Main.scala"
    "hansec.fortran-ls"       = "kh-sim\backends\fortran"
    "Wosi.omnipascal"         = "kh-sim\backends\pascal\src\kh_server.pas"
    "ms-vscode.cpptools"      = "kh-sim\backends\cpp"
    "ms-python.python"        = "kh-sim\shared\physics\kh_physics.py"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Status {
    param([string]$Msg, [string]$Level = "INFO")
    $colour = switch ($Level) {
        "OK"    { "Green"  }
        "SKIP"  { "Cyan"   }
        "WARN"  { "Yellow" }
        "ERROR" { "Red"    }
        default { "White"  }
    }
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts][$Level] $Msg" -ForegroundColor $colour
}

function Assert-CodeCli {
    $cmd = Get-Command code -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Status "VS Code CLI not found in PATH." "ERROR"
        Write-Status "Install VS Code first (windows-setup.ps1), then re-open PowerShell." "WARN"
        exit 1
    }
    $ver = & code --version 2>&1 | Select-Object -First 1
    Write-Status "VS Code detected: $ver" "OK"
}

function Get-InstalledExtensions {
    & code --list-extensions 2>&1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  GEN-013 -- VS Code IDE Extension Setup (ThinkPad)"         -ForegroundColor Cyan
Write-Host "  VibeCodeProjects R0 -- Infrastructure Baseline"            -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Assert-CodeCli

$installed    = Get-InstalledExtensions
$results      = [ordered]@{}
$installCount = 0
$skipCount    = 0
$errorCount   = 0

# ---------------------------------------------------------------------------
# Install / verify pass
# ---------------------------------------------------------------------------
foreach ($id in $extensions.Keys) {
    $desc = $extensions[$id]

    if ($installed -contains $id) {
        Write-Status "ALREADY INSTALLED  $id  -- $desc" "SKIP"
        $results[$id] = "already-installed"
        $skipCount++
        continue
    }

    if ($Verify) {
        Write-Status "MISSING  $id  -- $desc" "WARN"
        $results[$id] = "missing"
        $errorCount++
        continue
    }

    Write-Status "Installing  $id  -- $desc" "INFO"
    $out = & code --install-extension $id --force 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Status "OK  $id" "OK"
        $results[$id] = "installed"
        $installCount++
    } else {
        Write-Status "FAILED  $id  -> $out" "ERROR"
        $results[$id] = "failed"
        $errorCount++
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$total = $extensions.Count
Write-Status "Total extensions in manifest : $total"
Write-Status "Already installed (skipped)  : $skipCount" "SKIP"
if (-not $Verify) {
    Write-Status "Newly installed              : $installCount" "OK"
}
if ($errorCount -gt 0) {
    Write-Status "Failed / Missing             : $errorCount" "ERROR"
} else {
    Write-Status "Failed / Missing             : 0" "OK"
}

# ---------------------------------------------------------------------------
# Post-install verification (re-read installed list)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "--- Installed extension audit ---" -ForegroundColor Cyan
$installed2 = Get-InstalledExtensions
$allPresent = $true

foreach ($id in $extensions.Keys) {
    $desc = $extensions[$id]
    if ($installed2 -contains $id) {
        Write-Status "PASS  $id  -- $desc" "OK"
    } else {
        Write-Status "FAIL  $id  -- $desc" "ERROR"
        $allPresent = $false
    }
}

# ---------------------------------------------------------------------------
# Acceptance hints
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "--- Acceptance-test checklist (manual) ---" -ForegroundColor Cyan
Write-Host "Open VS Code in VibeCodeProjects root, verify each language server activates:" -ForegroundColor White
foreach ($id in $acceptancePaths.Keys) {
    $path = $acceptancePaths[$id]
    $desc = $extensions[$id]
    Write-Host "  [ ] $desc" -ForegroundColor White
    Write-Host "      Open: $path" -ForegroundColor DarkGray
}
Write-Host "  [ ] Git: Source Control panel shows branch 'thinkpad' or 'main', remote origin reachable" -ForegroundColor White
Write-Host "  [ ] PlantUML: Docker plantuml/plantuml-server:jetty must be running on port 8010" -ForegroundColor Yellow
Write-Host "      docker run -d -p 8010:8080 plantuml/plantuml-server:jetty" -ForegroundColor DarkGray
Write-Host ""

if ($allPresent) {
    Write-Status "GEN-013 PASS -- all extensions present. Status already marked done in TASKS-shared.yaml." "OK"
    exit 0
} else {
    Write-Status "GEN-013 INCOMPLETE -- one or more extensions missing. Re-run without -Verify." "ERROR"
    exit 1
}
