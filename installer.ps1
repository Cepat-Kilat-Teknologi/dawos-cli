# ──────────────────────────────────────────────────────────────────────
# dawos-cli installer for Windows
# Usage: irm https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.ps1 | iex
#    or: .\installer.ps1
# ──────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"

$APP = "dawos-cli"
$BIN = "dawos"
$MIN_PY_MAJOR = 3
$MIN_PY_MINOR = 9
$REPO_URL = "https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git"

function Write-Info  { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

# ── Header ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "+======================================+" -ForegroundColor White
Write-Host "|      dawos-cli installer v0.1.0       |" -ForegroundColor White
Write-Host "+======================================+" -ForegroundColor White
Write-Host ""

# ── 1. Check Python ──────────────────────────────────────────────────
Write-Info "Checking Python..."

$py = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -gt $MIN_PY_MAJOR -or ($major -eq $MIN_PY_MAJOR -and $minor -ge $MIN_PY_MINOR)) {
                $py = $cmd
                break
            }
        }
    } catch { }
}

if (-not $py) {
    Write-Fail "Python ${MIN_PY_MAJOR}.${MIN_PY_MINOR}+ required. Download from https://www.python.org/downloads/"
}
$pyVer = & $py --version 2>&1
Write-Ok "$pyVer"

# ── 2. Check / Install pipx ─────────────────────────────────────────
Write-Info "Checking pipx..."

$hasPipx = $false
try {
    $pipxVer = & pipx --version 2>&1
    $hasPipx = $true
    Write-Ok "pipx $pipxVer"
} catch { }

if (-not $hasPipx) {
    Write-Warn "pipx not found. Installing..."
    try {
        & $py -m pip install --user pipx
        & $py -m pipx ensurepath
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + $env:PATH
        $pipxVer = & pipx --version 2>&1
        Write-Ok "pipx $pipxVer installed"
    } catch {
        Write-Fail "Could not install pipx. Install manually: https://pipx.pypa.io"
    }
}

# ── 3. Install dawos-cli ─────────────────────────────────────────────
Write-Info "Installing $APP..."

# Detect source: local directory or remote git
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$pyprojectPath = Join-Path $scriptDir "pyproject.toml"

if (Test-Path $pyprojectPath) {
    Write-Info "Installing from local source: $scriptDir"
    & pipx install --force $scriptDir
} else {
    Write-Info "Installing from GitHub..."
    & pipx install --force "git+$REPO_URL"
}

# ── 4. Verify ────────────────────────────────────────────────────────
Write-Host ""

# Refresh PATH for current session
$userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath) { $env:PATH = "$userPath;$env:PATH" }

try {
    $installedVer = & $BIN --version 2>&1
    Write-Ok "$installedVer installed successfully!"
} catch {
    Write-Fail "Installation completed but '$BIN' not found. Restart your terminal and try: dawos --version"
}

# ── 5. Quick start ───────────────────────────────────────────────────
Write-Host ""
Write-Host "Quick start:" -ForegroundColor White
Write-Host "  1. Add your BNG node:"
Write-Host "     dawos profile add prod http://192.168.1.1:8470 YOUR_API_KEY"
Write-Host ""
Write-Host "  2. Check connection:"
Write-Host "     dawos status"
Write-Host ""
Write-Host "  3. View sessions:"
Write-Host "     dawos session list"
Write-Host ""
Write-Host "Uninstall:" -ForegroundColor White
Write-Host "  pipx uninstall dawos-cli"
Write-Host ""
