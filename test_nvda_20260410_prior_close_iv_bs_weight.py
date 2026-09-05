#!/usr/bin/env python3
"""Diagnostic only: NVDA 2026-04-10 GEX->VEX Black-Scholes moneyness test
using ONLY prior-close observed IV from 2026-04-09 15:59 ET.

Why this exists:
- the HeatSeeker GEX/VEX snapshot was published 2026-04-10 08:59 ET (premarket)
- ThetaData has no same-instant option IV rows at 08:59 ET
- this script therefore uses the last pre-existing IV snapshot from the prior session
  and never uses 2026-04-10 post-open IV (no look-ahead)

Observed HeatSeeker snapshot:
- symbol NVDA
- card snapshot/publish time used for T: 2026-04-10 08:59 ET
- spot shown on both panels: 184.03
- same-expiry GEX/VEX values already transcribed for 2026-04-10, 04-13, 04-15

Theoretical factor:
    W_BS = -sqrt(T) * d2
with r=q=0 for this short-dated diagnostic, spot from the HeatSeeker card,
and strike-level IV taken from 2026-04-09 15:59 ET.

Test:
    VEX ~= alpha_expiry * GEX * W_BS
and compare with:
    GEX * sign(K-S)
    GEX * log(K/S)

This does NOT identify dealer positioning or Skylit's proprietary formula.
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
SYMBOL = "NVDA"
IV_DATE = "20260409"
IV_TIME_ET = "15:59:00"
CARD_DATE = "20260410"
CARD_TIME_ET = "08:59:00"
SPOT = 184.03
NY = ZoneInfo("America/New_York")
CARD_DT = datetime(2026, 4, 10, 8, 59, tzinfo=NY)
OUT = Path("nvda_20260410_prior_close_iv_bs_weight_result.json")

STRIKES = np.array([
    200,197.5,195,194,193,192.5,192,191,190,189,188,187.5,187,186,
    185,184,183,182.5,182,181,180,179,178,177.5,177,176,175
], dtype=float)

GEX = {
    "20260410": np.array([-22.6,115.4,1425.6,0,0,860.0,0,0,20292.7,0,0,10096.3,0,0,24814.4,0,0,68835.1,0,0,1168.7,0,0,8946.1,0,0,6655.0]),
    "20260413": np.array([-68.2,6.9,234.5,0,0,-33.8,0,0,3439.6,0,0,-1579.0,0,0,-6271.1,0,0,-2358.7,0,0,-84.7,0,0,-606.3,0,0,262.8]),
    "20260415": np.array([44.5,61.0,96.0,0,0,-100.2,0,0,-391.5,0,0,-211.9,0,0,-231.0,0,0,-590.4,0,0,-536.2,0,0,-50.1,0,0,256.3]),
}

VEX = {
    "20260410": np.array([-272.9,2711.5,32527.2,0,0,18888.3,0,0,374573.0,0,0,121377.0,0,0,89584.3,0,0,-306918.4,0,0,-12724.7,0,0,-127357.4,0,0,-112342.0]),
    "20260413": np.array([-3103.6,301.7,9166.3,0,0,-1131.3,0,0,86351.4,0,0,-23879.5,0,0,-27253.9,0,0,13594.3,0,0,1022.9,0,0,13436.1,0,0,-7042.4]),
    "20260415": np.array([2256.1,2845.5,3783.1,0,0,-3230.5,0,0,-9085.9,0,0,-2864.1,0,0,-923.8,0,0,2960.5,0,0,7055.0,0,0,1023.0,0,0,-7664.5]),
}


def fetch_iv(expiration: str):
    params = {
        "symbol": SYMBOL,
        "expiration": expiration,
        "date": IV_DATE,
        "strike": "*",
        "right": "both",
        "start_time": IV_TIME_ET,
        "end_time": IV_TIME_ET,
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
    return max((dt - CARD_DT).total_seconds(), 1.0) / (365.0 * 24 * 3600)


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


print("NVDA 2026-04-10 — PRIOR-CLOSE IV BLACK-SCHOLES MONEYNESS DIAGNOSTIC")
print(f"card spot={SPOT:.2f}; card={CARD_DATE} {CARD_TIME_ET} ET")
print(f"IV source={IV_DATE} {IV_TIME_ET} ET (prior close; no look-ahead)")

results = {
    "symbol": SYMBOL,
    "card_date": CARD_DATE,
    "card_time_et": CARD_TIME_ET,
    "spot": SPOT,
    "iv_date": IV_DATE,
    "iv_time_et": IV_TIME_ET,
    "expiries": {},
}

for expiration in GEX:
    payload = fetch_iv(expiration)
    iv_map = parse_iv_by_strike(payload)
    T = expiry_T(expiration)
    g = GEX[expiration]
    v = VEX[expiration]

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
        print(f"\n{expiration}: insufficient prior-close IV rows n={len(rows)}")
        results["expiries"][expiration] = {"n": len(rows), "status": "INSUFFICIENT_PRIOR_CLOSE_IV"}
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
        "bs": {
            "spearman": rho_bs,
            "pearson": pear_bs,
            "alpha": a_bs,
            "alpha_over_spot": a_bs / SPOT,
            "r2": r2(vv, yhat_bs),
            "sign_hits": sign_hits,
        },
        "sign_baseline": {
            "spearman": rho_sign,
            "pearson": pear_sign,
            "alpha": a_sign,
            "r2": r2(vv, yhat_sign),
        },
        "logmoneyness_baseline": {
            "spearman": rho_log,
            "pearson": pear_log,
            "alpha": a_log,
            "r2": r2(vv, yhat_log),
        },
    }
    results["expiries"][expiration] = exp_result

    print(f"\nexpiry {expiration}  n={len(rows)}  T={T:.6f}y  medianIV={np.median(sigma):.4f}")
    print(f"  BS prior-close:  Spearman={rho_bs:+.4f}  Pearson={pear_bs:+.4f}  R2={exp_result['bs']['r2']:+.4f}  sign={sign_hits}/{len(rows)}")
    print(f"  sign(K-S):       Spearman={rho_sign:+.4f}  Pearson={pear_sign:+.4f}  R2={exp_result['sign_baseline']['r2']:+.4f}")
    print(f"  log(K/S):        Spearman={rho_log:+.4f}  Pearson={pear_log:+.4f}  R2={exp_result['logmoneyness_baseline']['r2']:+.4f}")
    print(f"  fitted alpha_BS={a_bs:+.6f}  alpha/spot={a_bs / SPOT:+.6f}")

OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nsaved: {OUT.resolve()}")
print("STATUS: DIAGNOSTIC_ONLY_PRIOR_CLOSE_IV")
