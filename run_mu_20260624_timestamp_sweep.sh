#!/usr/bin/env bash
set -Eeuo pipefail

# Post-hoc timestamp-sensitivity diagnostic for MU 2026-06-24 H5 FAIL.
# This DOES NOT change or rescue H5. The exact HeatSeeker snapshot time is unknown.
# Every cumulative window uses the frozen v1 classifier unchanged, starting 09:30 ET.

for END in 09:45:00 10:00:00 10:15:00 10:30:00 10:45:00 11:00:00 11:04:00; do
  SAFE="${END//:/}"
  echo "=== collecting through $END ET ==="
  python3 volland_like_frozen_v1.py \
    --symbol MU \
    --date 20260624 \
    --expiration 20260626 \
    --end-time "$END" \
    --spot 1043.24 \
    --output "mu_20260624_20260626_${SAFE}_volland_like_frozen_v1.json"
done

python3 evaluate_mu_20260624_timestamp_sweep.py
