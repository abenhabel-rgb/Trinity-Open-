#!/usr/bin/env python3
"""Probe ThetaData Standard historical implied-volatility data for MU.

Purpose: inspect observed intraday IV/underlying fields before any gamma reconstruction.
No HeatSeeker fit is performed. No reconstructed gamma is accepted by this script.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:25503/v3"
OUT = Path("mu_20260624_1104_intraday_iv_raw.json")

params = {
    "symbol": "MU",
    "expiration": "20260626",
    "date": "20260624",
    "strike": "*",
    "right": "both",
    "start_time": "10:59:00",
    "end_time": "11:04:00",
    "interval": "1m",
    "version": "latest",
    "format": "json",
}

url = BASE + "/option/history/greeks/implied_volatility?" + urllib.parse.urlencode(params)
print(url)
with urllib.request.urlopen(url, timeout=180) as r:
    payload = json.loads(r.read().decode("utf-8"))

OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

items = payload
if isinstance(payload, dict):
    for key in ("response", "data", "results"):
        if isinstance(payload.get(key), list):
            items = payload[key]
            break

print(f"saved: {OUT.resolve()}")
if not isinstance(items, list):
    print(f"top-level type: {type(payload).__name__}")
    if isinstance(payload, dict):
        print("top-level keys:", sorted(payload.keys()))
    raise SystemExit(0)

print(f"top-level rows/blocks: {len(items)}")
if not items:
    raise SystemExit(0)

first = items[0]
print("first item keys:", sorted(first.keys()) if isinstance(first, dict) else type(first).__name__)
if isinstance(first, dict):
    contract = first.get("contract")
    data = first.get("data")
    if isinstance(contract, dict):
        print("first contract:", json.dumps(contract, sort_keys=True))
    if isinstance(data, list):
        print(f"first data rows: {len(data)}")
        if data and isinstance(data[0], dict):
            print("first data keys:", sorted(data[0].keys()))
            print("first data sample:", json.dumps(data[0], indent=2)[:3000])
    else:
        print("first item sample:", json.dumps(first, indent=2)[:3000])
