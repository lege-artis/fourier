# laragon-vhosts-setup.ps1
# WEB-003: Configure Laragon virtual hosts for local dev sites
# Requires: Laragon 8.x installed, run as Administrator
# ---------------------------------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "`n=== WEB-003: Laragon Vhost Configuration ===" -ForegroundColor Cyan

# --- Detect Laragon root ---
$laragonCandidates = @(
    "C:\laragon",
    "C:\Users\vitez\AppData\Local\laragon",
    "C:\Program Files\laragon",
    "D:\laragon"
)
$laragonRoot = $null
foreach ($c in $laragonCandidates) {
    if (Test-Path "$c\bin\apache") { $laragonRoot = $c; break }
    if (Test-Path "$c\bin\nginx")  { $laragonRoot = $c; break }
}

if (-not $laragonRoot) {
    Write-Host "  Laragon not found at standard paths." -ForegroundColor Yellow
    Write-Host "  Checking registry..." -ForegroundColor Cyan
    $regKey = Get-ItemProperty "HKCU:\Software\Laragon" -ErrorAction SilentlyContinue
    if ($regKey) { Write-Host "  Registry: $($regKey | Format-List | Out-String)" }
    Write-Host "  Set `$laragonRoot manually and re-run." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  Laragon root: $laragonRoot" -ForegroundColor Green
}

# --- Site definitions ---
$sites = @(
    @{ domain = "zemla.test";        docroot = "C:\Users\vitez\Documents\VibeCodeProjects\sandboxes\zemla-test" },
    @{ domain = "mim2000.test";      docroot = "C:\Users\vitez\Documents\VibeCodeProjects\sandboxes\mim2000-test" },
    @{ domain = "bodyterapie.test";  docroot = "C:\Users\vitez\Documents\VibeCodeProjects\sandboxes\bodyterapie-test" }
)

# --- Create docroot directories (WordPress placeholders) ---
foreach ($site in $sites) {
    if (-not (Test-Path $site.docroot)) {
        New-Item -ItemType Directory -Path $site.docroot -Force | Out-Null
        # Minimal index.php so Apache can serve something immediately
        $indexContent = "<?php echo '<h1>" + $site.domain + " — Laragon sandbox</h1><p>WordPress install pending.</p>'; ?>"
        Set-Content "$($site.docroot)\index.php" $indexContent -Encoding UTF8
        Write-Host "  Created docroot: $($site.docroot)" -ForegroundColor Green
    } else {
        Write-Host "  Docroot exists: $($site.docroot)" -ForegroundColor Green
    }
}

# --- Apache vhost snippets ---
$apacheVhostDir = "$laragonRoot\etc\apache2\sites-enabled"
if (-not (Test-Path $apacheVhostDir)) {
    # Laragon 6+ may use this path
    $apacheVhostDir = "$laragonRoot\usr\apache2\conf\extra"
    if (-not (Test-Path $apacheVhostDir)) {
        New-Item -ItemType Directory -Path $apacheVhostDir -Force | Out-Null
    }
}

foreach ($site in $sites) {
    $vhostFile = "$apacheVhostDir\$($site.domain).conf"
    $vhostContent = @"
<VirtualHost *:80>
    ServerName $($site.domain)
    ServerAlias www.$($site.domain)
    DocumentRoot "$($site.docroot)"
    <Directory "$($site.docroot)">
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog  "$laragonRoot/logs/$($site.domain)-error.log"
    CustomLog "$laragonRoot/logs/$($site.domain)-access.log" combined
</VirtualHost>
"@
    [System.IO.File]::WriteAllText($vhostFile, $vhostContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  Apache vhost written: $vhostFile" -ForegroundColor Green
}

# --- Nginx server blocks (if Laragon uses nginx) ---
$nginxVhostDir = "$laragonRoot\etc\nginx\sites-enabled"
if (Test-Path "$laragonRoot\bin\nginx") {
    if (-not (Test-Path $nginxVhostDir)) {
        New-Item -ItemType Directory -Path $nginxVhostDir -Force | Out-Null
    }
    foreach ($site in $sites) {
        $nginxFile = "$nginxVhostDir\$($site.domain).conf"
        $nginxContent = @"
server {
    listen 80;
    server_name $($site.domain) www.$($site.domain);
    root $($site.docroot);
    index index.php index.html;

    location / {
        try_files `$uri `$uri/ /index.php?`$args;
    }
    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME `$document_root`$fastcgi_script_name;
    }
    error_log  $laragonRoot/logs/$($site.domain)-error.log;
    access_log $laragonRoot/logs/$($site.domain)-access.log;
}
"@
        [System.IO.File]::WriteAllText($nginxFile, $nginxContent, [System.Text.UTF8Encoding]::new($false))
        Write-Host "  Nginx block written: $nginxFile" -ForegroundColor Green
    }
}

# --- Windows hosts file update ---
Write-Host "`n  Updating C:\Windows\System32\drivers\etc\hosts..." -ForegroundColor Cyan
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$hostsContent = [System.IO.File]::ReadAllText($hostsPath)

foreach ($site in $sites) {
    $entry = "127.0.0.1    $($site.domain)"
    $entryWww = "127.0.0.1    www.$($site.domain)"
    if ($hostsContent -notlike "*$($site.domain)*") {
        $hostsContent = $hostsContent.TrimEnd() + "`r`n$entry`r`n$entryWww`r`n"
        Write-Host "  + $entry" -ForegroundColor Green
    } else {
        Write-Host "  Already in hosts: $($site.domain)" -ForegroundColor Green
    }
}
[System.IO.File]::WriteAllText($hostsPath, $hostsContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "  hosts file updated." -ForegroundColor Green

# --- Laragon logs dir ---
if (-not (Test-Path "$laragonRoot\logs")) {
    New-Item -ItemType Directory -Path "$laragonRoot\logs" -Force | Out-Null
}

Write-Host "`n=== WEB-003 COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "  Sites configured:" -ForegroundColor Cyan
foreach ($site in $sites) {
    Write-Host "    http://$($site.domain)  ->  $($site.docroot)"
}
Write-Host ""
Write-Host "  ACTION: Restart Laragon (right-click tray icon -> Restart All)" -ForegroundColor Yellow
Write-Host "  Then open http://zemla.test in browser to verify." -ForegroundColor Yellow
Write-Host ""
Write-Host "  WordPress install (when ready):"
Write-Host "    1. Download wordpress.org/latest.zip"
Write-Host "    2. Extract to docroot (e.g. sandboxes\zemla-test\)"
Write-Host "    3. Create DB in Laragon -> phpMyAdmin (or via cli)"
Write-Host "    4. Browse http://zemla.test and run WP installer"
