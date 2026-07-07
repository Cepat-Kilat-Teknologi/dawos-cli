#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# dawos-cli installer
# Usage: curl -fsSL <raw-url>/installer.sh | bash
#    or: ./installer.sh
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

APP="dawos-cli"
BIN="dawos"
MIN_PY="3.9"
REPO_URL="https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git"

# ── Colors ───────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Header ───────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       dawos-cli installer v0.1.0      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""

# ── 1. Check Python ──────────────────────────────────────────────────
info "Checking Python..."

if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    fail "Python not found. Install Python ${MIN_PY}+ first."
fi

PY_VER=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PY -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PY -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]; }; then
    fail "Python ${MIN_PY}+ required (found ${PY_VER})"
fi
ok "Python ${PY_VER}"

# ── 2. Check / Install pipx ─────────────────────────────────────────
info "Checking pipx..."

if command -v pipx &>/dev/null; then
    ok "pipx $(pipx --version)"
else
    warn "pipx not found. Installing..."
    if command -v brew &>/dev/null; then
        brew install pipx
        pipx ensurepath
    elif command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq pipx
        pipx ensurepath
    else
        $PY -m pip install --user pipx
        $PY -m pipx ensurepath
    fi

    if ! command -v pipx &>/dev/null; then
        export PATH="$HOME/.local/bin:$PATH"
    fi

    if command -v pipx &>/dev/null; then
        ok "pipx installed"
    else
        fail "Could not install pipx. Install manually: https://pipx.pypa.io"
    fi
fi

# ── 3. Install dawos-cli ─────────────────────────────────────────────
info "Installing ${APP}..."

# Detect source: local directory or remote git
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null || echo ".")" && pwd)"

if [ -f "${SCRIPT_DIR}/pyproject.toml" ]; then
    # Running from cloned repo
    info "Installing from local source: ${SCRIPT_DIR}"
    pipx install --force "${SCRIPT_DIR}"
else
    # Running via curl | bash — install from git
    info "Installing from GitHub..."
    pipx install --force "git+${REPO_URL}"
fi

# ── 4. Verify ────────────────────────────────────────────────────────
echo ""
if command -v "$BIN" &>/dev/null; then
    INSTALLED_VER=$($BIN --version 2>&1 || true)
    ok "${INSTALLED_VER} installed successfully!"
else
    # pipx might need PATH refresh
    export PATH="$HOME/.local/bin:$PATH"
    if command -v "$BIN" &>/dev/null; then
        INSTALLED_VER=$($BIN --version 2>&1 || true)
        ok "${INSTALLED_VER} installed successfully!"
        warn "Restart your terminal or run: export PATH=\"\$HOME/.local/bin:\$PATH\""
    else
        fail "Installation completed but '${BIN}' not found in PATH."
    fi
fi

# ── 5. Quick start ───────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Quick start:${NC}"
echo "  1. Add your BNG node:"
echo "     dawos profile add prod http://192.168.1.1:8470 YOUR_API_KEY"
echo ""
echo "  2. Check connection:"
echo "     dawos status"
echo ""
echo "  3. View sessions:"
echo "     dawos session list"
echo ""
echo -e "${BOLD}Uninstall:${NC}"
echo "  pipx uninstall dawos-cli"
echo ""
