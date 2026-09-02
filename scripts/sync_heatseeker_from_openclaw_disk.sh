#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="${OPENCLAW_DISK_ROOT:-/Volumes/OPENCLAW/BUREAU_MAC}"
SSH_KEY="${OPENCLAW_SSH_KEY:-$HOME/Downloads/LightsailDefaultKey-us-east-1.pem}"
REMOTE_HOST="${OPENCLAW_REMOTE_HOST:-ubuntu@3.239.230.228}"
REMOTE_INBOX="${OPENCLAW_REMOTE_INBOX:-/opt/openclaw/inbox/heatseeker}"

if [[ ! -d "$SOURCE_ROOT" ]]; then
  echo "ERROR: source disk path not found: $SOURCE_ROOT" >&2
  exit 1
fi

if [[ ! -f "$SSH_KEY" ]]; then
  echo "ERROR: SSH key not found: $SSH_KEY" >&2
  exit 1
fi

chmod 400 "$SSH_KEY"

TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT

# Historical Heatseeker/heatmap candidates only. Read-only scan; no local deletion.
find "$SOURCE_ROOT" -type f \
  \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.webp" \) \
  \( -ipath "*heatseeker*" -o -ipath "*heatmap*" -o -ipath "*heatmaps*" \) \
  -print0 > "$TMP_LIST"

COUNT=$(python3 - "$TMP_LIST" <<'PY'
import sys
from pathlib import Path
raw = Path(sys.argv[1]).read_bytes()
print(0 if not raw else raw.count(b'\0'))
PY
)

echo "[OpenClaw] Heatseeker/heatmap candidates found: $COUNT"
if [[ "$COUNT" -eq 0 ]]; then
  exit 0
fi

ssh -i "$SSH_KEY" "$REMOTE_HOST" "mkdir -p '$REMOTE_INBOX'"

# Copy each file to the VPS inbox. The VPS collector performs SHA-256 deduplication
# and archives every observation; this script never deletes source files.
SENT=0
while IFS= read -r -d '' FILE; do
  BASENAME="$(basename "$FILE")"
  echo "[OpenClaw] -> $BASENAME"
  scp -q -i "$SSH_KEY" "$FILE" "$REMOTE_HOST:$REMOTE_INBOX/"
  SENT=$((SENT + 1))
done < "$TMP_LIST"

echo "[OpenClaw] Transfer complete: $SENT file(s) sent."
echo "[OpenClaw] Local files were not modified or deleted."
