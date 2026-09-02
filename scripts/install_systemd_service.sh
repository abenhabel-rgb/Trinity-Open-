#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-/opt/openclaw}"
SERVICE_NAME="${OPENCLAW_SERVICE_NAME:-openclaw-worker}"
RUN_USER="${OPENCLAW_RUN_USER:-${SUDO_USER:-$USER}}"
PYTHON_BIN="$OPENCLAW_HOME/.venv/bin/python"
WORKER_STATE="$OPENCLAW_HOME/logs/worker_heartbeat.json"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "ERROR: OpenClaw virtualenv not found at $PYTHON_BIN" >&2
  exit 1
fi

sudo mkdir -p "$OPENCLAW_HOME/logs"
sudo chown -R "$RUN_USER":"$RUN_USER" "$OPENCLAW_HOME/logs"

TMP_UNIT="$(mktemp)"
trap 'rm -f "$TMP_UNIT"' EXIT

cat > "$TMP_UNIT" <<EOF
[Unit]
Description=OpenClaw persistent research worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$OPENCLAW_HOME
ExecStart=$PYTHON_BIN -m trinity.worker --interval 60 --state-path $WORKER_STATE
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo install -m 0644 "$TMP_UNIT" "$UNIT_PATH"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

sleep 2
sudo systemctl --no-pager --full status "$SERVICE_NAME"

echo
echo "Heartbeat:"
cat "$WORKER_STATE"
