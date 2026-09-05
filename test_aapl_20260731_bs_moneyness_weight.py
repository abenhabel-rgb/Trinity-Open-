#!/usr/bin/env python3
"""Diagnostic: third cross-ticker GEX->VEX Black-Scholes moneyness test.

Observed Skylit HeatSeeker pair:
- AAPL, published 2026-07-31 15:43 Paris = 09:43 ET
- GEX panel spot 300.50; VEX panel spot 300.62 (small panel-time mismatch)
- same expiries visible on both panels
- primary deterministic common block: strikes 285.0..355.0 inclusive
- expiries tested: 2026-07-31, 2026-08-03, 2026-08-05

Primary predictor follows the already-used TSLA/NVDA diagnostic:
    W_BS = -sqrt(T) * d2
    VEX ~= alpha * GEX * W_BS
with r=q=0 and strike-level observed ThetaData IV at 09:43 ET.

The GEX-panel spot (300.50) is used deterministically in the transform because
GEX is the source variable. The VEX-panel spot is recorded only as provenance.
No dealer-position inference is made. DIAGNOSTIC_ONLY.
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
SYMBOL = "AAPL"
DATE = "20260731"
SNAPSHOT_ET = "09:43:00"
SPOT = 300.50
VEX_PANEL_SPOT = 300.62
NY = ZoneInfo("America/New_York")
SNAPSHOT_DT = datetime(2026, 7, 31, 9, 43, tzinfo=NY)
OUT = Path("aapl_20260731_bs_moneyness_weight_result.json")

STRIKES = np.array([
    355,352.5,350,347.5,345,342.5,340,337.5,335,332.5,330,327.5,
    325,322.5,320,317.5,315,312.5,310,307.5,305,302.5,300,297.5,
    295,292.5,290,287.5,285
], dtype=float)

# GEX from Image 40 (GEX selected); VEX from Image 41 (VEX selected).
DATA = {
    "20260731": {
        "gex": np.array([
            3.4,65.5,-375.7,27.6,2251.5,243.0,775.2,634.0,36.2,180.9,
            -377.3,-55.9,113.4,-566.0,2257.6,-53.0,849.1,2312.1,11892.1,
            2791.2,7651.7,4132.6,26079.0,88.9,5057.0,872.8,4873.5,-616.3,-609.7
        ]),
        "vex": np.array([
            347.2,1555.8,-4558.2,677.5,32013.9,4697.3,14995.8,9854.2,761.7,
            4017.6,-3486.6,-1259.4,2553.8,-8693.1,38334.5,525.7,9901.1,29090.2,
            140038.9,24801.7,42787.6,10467.0,-24475.7,-808.4,-34724.2,-8956.2,
            -60923.5,11242.4,10061.4
        ]),
    },
    "20260803": {
        "gex": np.array([
            153.2,-2.1,26.5,3.2,28.1,22.2,111.7,20.6,13.9,-358.1,21.1,22.5,
            36.0,90.7,-59.1,14.0,266.4,15.9,306.8,158.8,472.9,-102.0,-79.3,
            513.6,-31.6,504.0,62.5,24.3,25.1
        ]),
        "vex": np.array([
            6943.0,-34.3,2013.9,364.3,2054.9,1110.0,5719.4,1264.7,935.3,-18955.4,
            1531.2,1533.5,2302.6,4944.6,-4979.4,803.8,11659.2,534.8,8182.9,3242.3,
            7606.2,-487.7,139.8,-4867.3,488.4,11279.1,-1759.7,-873.6,-979.8
        ]),
    },
    "20260805": {
        "gex": np.array([
            2.0,10.0,-0.2,39.9,101.4,9.2,-9.2,46.5,42.8,36.6,27.7,1.1,21.0,
            37.0,20.7,82.0,204.0,13.8,139.2,-2362.3,185.7,59.3,-3759.8,235.8,
            31.7,-2.3,43.2,-5.8,-2.6
        ]),
        "vex": np.array([
            201.7,540.2,-49.7,1182.0,4385.3,477.2,-301.6,1147.7,2614.8,2507.4,
            1907.5,75.4,1436.1,1872.7,1214.2,5709.1,11616.1,487.4,3723.6,-43467.3,
            2204.3,365.3,7121.2,-2716.1,-530.1,52.4,-1249.7,200.1,103.6
        ]),
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


print("AAPL 2026-07-31 — BLACK-SCHOLES MONEYNESS WEIGHT THIRD-TICKER DIAGNOSTIC")
print(f"GEX spot={SPOT:.2f}; VEX panel spot={VEX_PANEL_SPOT:.2f}; snapshot={DATE} {SNAPSHOT_ET} ET")
results = {
    "symbol": SYMBOL, "date": DATE, "snapshot_et": SNAPSHOT_ET,
    "gex_spot": SPOT, "vex_panel_spot": VEX_PANEL_SPOT, "expiries": {}
}

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
        "n": int(len(rows)), "T_years": T, "median_iv": float(np.median(sigma)),
        "bs": {"spearman": rho_bs, "pearson": pear_bs, "alpha": a_bs, "alpha_over_spot": a_bs / SPOT,
               "r2": r2(vv, yhat_bs), "sign_hits": sign_hits},
        "sign_baseline": {"spearman": rho_sign, "pearson": pear_sign, "alpha": a_sign, "r2": r2(vv, yhat_sign)},
        "logmoneyness_baseline": {"spearman": rho_log, "pearson": pear_log, "alpha": a_log, "r2": r2(vv, yhat_log)},
        "rows": [
            {"strike": r[0], "iv": r[1], "gex": r[2], "vex": r[3], "w_bs": r[4], "gex_w_bs": r[5]}
            for r in rows
        ],
    }
    results["expiries"][expiration] = exp_result

    print(f"\nexpiry {expiration}  n={len(rows)}  T={T:.6f}y  medianIV={np.median(sigma):.4f}")
    print(f"  BS weight:  Spearman={rho_bs:+.4f}  Pearson={pear_bs:+.4f}  R2={exp_result['bs']['r2']:+.4f}  sign={sign_hits}/{len(rows)}")
    print(f"  sign(K-S):  Spearman={rho_sign:+.4f}  Pearson={pear_sign:+.4f}  R2={exp_result['sign_baseline']['r2']:+.4f}")
    print(f"  log(K/S):   Spearman={rho_log:+.4f}  Pearson={pear_log:+.4f}  R2={exp_result['logmoneyness_baseline']['r2']:+.4f}")
    print(f"  fitted alpha_BS={a_bs:+.6f}  alpha/spot={a_bs/SPOT:+.6f}")

OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nsaved: {OUT.resolve()}")
print("STATUS: DIAGNOSTIC_ONLY_THIRD_TICKER")
