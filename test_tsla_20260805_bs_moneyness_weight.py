#!/usr/bin/env python3
"""Diagnostic: test whether the GEX->VEX transform is explained by the Black-Scholes
vanna/gamma moneyness factor on TSLA 2026-08-05.

Observed HeatSeeker snapshot:
- published 2026-08-05 18:54 Paris = 12:54 ET
- spot shown on GEX panel: 324.26
- same-expiry GEX/VEX values transcribed previously for 2026-08-05, 08-07, 08-10

Primary theoretical factor:
    W_BS = -sqrt(T) * d2
with r=q=0 for this short-dated diagnostic and strike-level observed IV from ThetaData.
Then test VEX ~= alpha_expiry * GEX * W_BS, where alpha_expiry is a single
no-intercept scale factor per expiry (units/convention absorber).

This is DIAGNOSTIC_ONLY. It does not identify dealer positioning or Skylit's
proprietary formula.
"""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import spearmanr, pearsonr

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "TSLA"
DATE = "20260805"
SNAPSHOT_ET = "12:54:00"
SPOT = 324.26
NY = ZoneInfo("America/New_York")
SNAPSHOT_DT = datetime(2026, 8, 5, 12, 54, tzinfo=NY)
OUT = Path("tsla_20260805_bs_moneyness_weight_result.json")

STRIKES = np.array([
    372.5,370,367.5,365,362.5,360,357.5,355,352.5,350,347.5,345,
    342.5,340,337.5,335,332.5,330,327.5,325,322.5,320,317.5,315,
    312.5,310,307.5,305,302.5,300,297.5,295,292.5,290,287.5
], dtype=float)

DATA = {
    "20260805": {
        "gex": np.array([22.1,-1.3,-11.8,44.1,-5.7,27.3,-50.6,8.2,50.8,189.1,-56.5,-129.1,-14.9,-299.2,70.4,-254.8,1934.1,6993.3,10147.2,37858.7,18623.9,11354.7,-1774.0,-849.9,131.3,-393.6,84.8,198.2,52.5,-246.1,24.4,44.0,21.9,1.6,9.1]),
        "vex": np.array([892.4,-66.9,-466.7,999.9,-137.2,617.8,-1108.2,187.3,1030.1,3901.6,-1076.2,-2374.5,-318.5,-4754.2,1063.4,-3852.1,19917.5,68577.2,60893.2,57326.8,-68509.7,-96081.0,22593.7,11793.9,-3112.2,5977.3,-1254.6,-3285.2,-995.5,3665.0,-570.1,-725.2,-403.0,-28.2,-210.9]),
    },
    "20260807": {
        "gex": np.array([13.0,-16.9,-153.3,76.9,160.5,-43.1,-8.9,-46.3,-13.6,-1004.2,-94.1,1492.5,-605.4,192.4,-19.5,435.3,-1582.7,-1180.1,-471.7,942.7,2636.9,2908.5,2511.7,2860.0,919.4,327.0,56.4,619.9,49.9,328.2,-28.6,281.8,16.4,112.2,1.7]),
        "vex": np.array([756.2,-1331.6,-8631.1,4200.1,8584.0,-2182.4,-439.2,-1795.9,-617.8,-43118.8,-3860.0,55081.7,-20159.6,5432.9,-409.1,9062.9,-25129.4,-13770.9,-3168.6,1826.4,-8442.9,-24148.3,-33269.7,-52521.1,-20762.9,-9328.4,-1582.6,-22306.8,-2265.4,-14271.4,1205.6,-13420.0,-823.1,-5612.0,-95.0]),
    },
    "20260810": {
        "gex": np.array([2.3,9.9,2.4,-304.3,2.0,-193.9,-11.8,7.0,-4.5,-150.7,-28.2,59.4,-11.0,116.0,51.1,276.5,-191.5,376.2,553.9,-183.9,382.5,821.2,128.5,-10.7,46.9,14.3,109.9,-188.7,0.2,3.5,-2.0,13.4,4.6,18.1,25.9]),
        "vex": np.array([188.8,329.0,190.3,-22995.5,144.1,-13652.5,-646.6,448.8,-279.5,-8743.7,-1331.6,2861.1,-461.6,4393.6,1747.1,7344.3,-3968.3,5807.2,4738.4,-431.2,-1502.8,-8463.2,-2105.8,135.4,-1280.3,-464.9,-4176.7,8042.8,-2.3,-200.7,121.4,-837.0,-300.0,-1261.8,-992.0]),
    },
}


def fetch_iv(expiration: str):
    params = {
        "symbol": SYMBOL,
        "expiration": expiration,
        "date": DATE,
        "strike": "*",
        "right": "both",
        "start_time": SNAPSHOT_ET,
        "end_time": SNAPSHOT_ET,
        "interval": "1m",
        "version": "latest",
        "format": "json",
    }
    url = BASE + "/option/history/greeks/implied_volatility?" + urllib.parse.urlencode(params)
    print(url)
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def extract_items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("response", "data", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def fnum(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def parse_iv_by_strike(payload):
    """Return strike -> {'call': iv, 'put': iv}; accepts common ThetaData nested shapes."""
    out = {}
    for item in extract_items(payload):
        if not isinstance(item, dict):
            continue
        contract = item.get("contract") if isinstance(item.get("contract"), dict) else item
        strike = None
        for k in ("strike", "strike_price"):
            if k in contract:
                strike = fnum(contract.get(k))
                break
        right = str(contract.get("right", contract.get("option_right", ""))).lower()
        if strike is None:
            continue
        rows = item.get("data") if isinstance(item.get("data"), list) else [item]
        vals = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            iv = None
            for key in ("implied_vol", "implied_volatility", "iv", "value"):
                if key in row:
                    iv = fnum(row.get(key))
                    if iv is not None:
                        break
            if iv is not None and iv > 0:
                # Normalize percent-looking values if provider emits 50 instead of 0.50.
                if iv > 5:
                    iv /= 100.0
                vals.append(iv)
        if not vals:
            continue
        rv = float(np.median(vals))
        side = "call" if right.startswith("c") else "put" if right.startswith("p") else "unknown"
        out.setdefault(round(strike, 4), {})[side] = rv
    return out


def effective_iv(side_map):
    """Frozen proxy for this diagnostic: arithmetic mean of available call/put IVs."""
    vals = [v for k, v in side_map.items() if k in ("call", "put") and v is not None and v > 0]
    if not vals:
        vals = [v for v in side_map.values() if v is not None and v > 0]
    return float(np.mean(vals)) if vals else None


def expiry_T(expiration: str):
    dt = datetime.strptime(expiration, "%Y%m%d").replace(hour=16, minute=0, tzinfo=NY)
    return max((dt - SNAPSHOT_DT).total_seconds(), 1.0) / (365.0 * 24 * 3600)


def no_intercept_alpha(x, y):
    den = float(np.dot(x, x))
    return float(np.dot(x, y) / den) if den > 0 else float("nan")


def r2(y, yhat):
    ssr = float(np.sum((y - yhat) ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ssr / sst if sst > 0 else float("nan")


def corr(a, b):
    if len(a) < 3:
        return float("nan"), float("nan")
    return float(spearmanr(a, b).statistic), float(pearsonr(a, b).statistic)


print("TSLA 2026-08-05 — BLACK-SCHOLES MONEYNESS WEIGHT DIAGNOSTIC")
print(f"spot={SPOT:.2f}; snapshot={DATE} {SNAPSHOT_ET} ET")
results = {"symbol": SYMBOL, "date": DATE, "snapshot_et": SNAPSHOT_ET, "spot": SPOT, "expiries": {}}

for expiration, d in DATA.items():
    payload = fetch_iv(expiration)
    iv_map = parse_iv_by_strike(payload)
    T = expiry_T(expiration)

    g = d["gex"]
    v = d["vex"]
    rows = []
    for i, K in enumerate(STRIKES):
        sigma = effective_iv(iv_map.get(round(float(K), 4), {}))
        if sigma is None or sigma <= 0 or g[i] == 0 or v[i] == 0:
            continue
        # r=q=0 diagnostic. d2 = [ln(S/K) - 0.5*sigma^2*T]/(sigma*sqrt(T))
        d2 = (math.log(SPOT / K) - 0.5 * sigma * sigma * T) / (sigma * math.sqrt(T))
        w_bs = -math.sqrt(T) * d2
        x_bs = g[i] * w_bs
        x_sign = g[i] * (1.0 if K > SPOT else -1.0)
        x_log = g[i] * math.log(K / SPOT)
        rows.append((float(K), float(sigma), float(g[i]), float(v[i]), float(w_bs), float(x_bs), float(x_sign), float(x_log)))

    if len(rows) < 5:
        print(f"\n{expiration}: insufficient IV rows n={len(rows)}")
        results["expiries"][expiration] = {"n": len(rows), "status": "INSUFFICIENT_IV"}
        continue

    arr = np.array(rows, dtype=float)
    K, sigma, gg, vv, wbs, xbs, xsign, xlog = arr.T

    a_bs = no_intercept_alpha(xbs, vv)
    a_sign = no_intercept_alpha(xsign, vv)
    a_log = no_intercept_alpha(xlog, vv)
    yhat_bs = a_bs * xbs
    yhat_sign = a_sign * xsign
    yhat_log = a_log * xlog

    rho_bs, pear_bs = corr(xbs, vv)
    rho_sign, pear_sign = corr(xsign, vv)
    rho_log, pear_log = corr(xlog, vv)
    sign_hits = int(np.sum(np.sign(xbs) == np.sign(vv)))

    exp_result = {
        "n": int(len(rows)),
        "T_years": T,
        "median_iv": float(np.median(sigma)),
        "bs": {"spearman": rho_bs, "pearson": pear_bs, "alpha": a_bs, "r2": r2(vv, yhat_bs), "sign_hits": sign_hits},
        "sign_baseline": {"spearman": rho_sign, "pearson": pear_sign, "alpha": a_sign, "r2": r2(vv, yhat_sign)},
        "logmoneyness_baseline": {"spearman": rho_log, "pearson": pear_log, "alpha": a_log, "r2": r2(vv, yhat_log)},
        "rows": [
            {"strike": r[0], "iv": r[1], "gex": r[2], "vex": r[3], "w_bs": r[4], "gex_w_bs": r[5]}
            for r in rows
        ],
    }
    results["expiries"][expiration] = exp_result

    print(f"\nexpiry {expiration}  n={len(rows)}  T={T:.6f}y  medianIV={np.median(sigma):.4f}")
    print(f"  BS weight:       Spearman={rho_bs:+.4f}  Pearson={pear_bs:+.4f}  R2={exp_result['bs']['r2']:+.4f}  sign={sign_hits}/{len(rows)}")
    print(f"  sign(K-S):       Spearman={rho_sign:+.4f}  Pearson={pear_sign:+.4f}  R2={exp_result['sign_baseline']['r2']:+.4f}")
    print(f"  log(K/S):        Spearman={rho_log:+.4f}  Pearson={pear_log:+.4f}  R2={exp_result['logmoneyness_baseline']['r2']:+.4f}")
    print(f"  fitted alpha_BS={a_bs:+.6f}")

OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nsaved: {OUT.resolve()}")
print("STATUS: DIAGNOSTIC_ONLY")
