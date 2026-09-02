#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${OPENCLAW_REPO_URL:-https://github.com/abenhabel-rgb/Trinity-Open-.git}"
INSTALL_DIR="${OPENCLAW_HOME:-/opt/openclaw}"
BRANCH="${OPENCLAW_BRANCH:-main}"
RUN_USER="${SUDO_USER:-$USER}"

log() { printf '\n[OpenClaw] %s\n' "$*"; }
fail() { printf '\n[OpenClaw] ERROR: %s\n' "$*" >&2; exit 1; }

if [[ "$(uname -s)" != "Linux" ]]; then
  fail "This bootstrap is intended for a Linux VPS."
fi

if ! command -v sudo >/dev/null 2>&1 && [[ "${EUID}" -ne 0 ]]; then
  fail "Run as root or install sudo first."
fi

SUDO=""
if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
fi

log "Installing system packages"
if command -v apt-get >/dev/null 2>&1; then
  $SUDO apt-get update
  $SUDO apt-get install -y git curl ca-certificates python3 python3-venv python3-pip
else
  fail "Unsupported package manager. Current bootstrap supports Debian/Ubuntu (apt)."
fi

PYTHON_BIN="$(command -v python3)"
PYTHON_VERSION="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

$PYTHON_BIN - <<'PY' || fail "OpenClaw requires Python >= 3.12. Install Python 3.12+ on this VPS and rerun the bootstrap."
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY

log "Using Python ${PYTHON_VERSION}"

if [[ ! -d "$INSTALL_DIR" ]]; then
  log "Cloning OpenClaw into $INSTALL_DIR"
  $SUDO mkdir -p "$(dirname "$INSTALL_DIR")"
  $SUDO git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$INSTALL_DIR"
else
  log "OpenClaw directory already exists; updating $BRANCH"
  $SUDO git -C "$INSTALL_DIR" fetch origin "$BRANCH"
  $SUDO git -C "$INSTALL_DIR" checkout "$BRANCH"
  $SUDO git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
fi

$SUDO chown -R "$RUN_USER":"$RUN_USER" "$INSTALL_DIR"

log "Creating virtual environment"
cd "$INSTALL_DIR"
rm -rf .venv
$PYTHON_BIN -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[dev]'

log "Running test suite"
python -m pytest -q

mkdir -p data/raw data/derived reports logs

cat > .openclaw_vps_state <<EOF
installed_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
branch=$BRANCH
python=$(python --version 2>&1)
install_dir=$INSTALL_DIR
EOF

log "Bootstrap complete"
printf '%s\n' \
  "Install dir : $INSTALL_DIR" \
  "Python      : $(python --version 2>&1)" \
  "Branch      : $BRANCH" \
  "Healthcheck : cd $INSTALL_DIR && source .venv/bin/activate && python -m pytest -q"
