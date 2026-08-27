#!/usr/bin/env python3
"""
Skylit FLOOR candidate auditor
==============================

Purpose
-------
Test *behavioral hypotheses* for the Midas/Peregrine `floor` and `floor_pok`
against observed HeatSeeker gamma matrices and observed setup payloads.

This script does NOT claim to recover Skylit's proprietary server code.
It uses only observed inputs/outputs. It does not reconstruct IV, Greeks,
dealer positioning, or synthetic GEX/VEX.

Supported HeatSeeker-like matrix keys
-------------------------------------
Spot:         CurrentSpot | currentSpot | spot
Strikes:      Strikes | strikes
Expirations:  Expirations | expirations
Gamma matrix: GammaValues | gammaValues | values

Matrix orientation is assumed strikes x expirations.

Setup payload
-------------
May be a single setup dict, a top-level {"setups":[...]}, a list of setups,
or JSONL. Expected observed fields where present:
symbol, floor, floor_pok, setup_class, spot/last_px, guard.

Candidate families
------------------
H1  front_strongest_below_all
H2  front_nearest_below_all
H3  front_strongest_below_significant
H4  front_nearest_below_significant
H5  front_strongest_positive_below_significant
H6  front_nearest_positive_below_significant
H7  front_king_at_spot

Significance semantics copied from the recovered HeatSeeker client read:
z >= 1 OR pctOfKing >= 0.25.

Important
---------
A match means "compatible with the observed sample", not proof of identity.
Freeze a candidate before chronological holdout testing.
"""

from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFAULT_Z_MIN = 1.0
DEFAULT_POK_MIN = 0.25
STRIKE_STEPS = {"SPY": 0.5, "QQQ": 0.5, "SPX": 5.0, "SPXW": 5.0}


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def first(d: dict, *keys):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def normalize_symbol(x):
    if x is None:
        return None
    return str(x).upper().replace("$", "").strip()


def walk_dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk_dicts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_dicts(v)


def find_matrix_obj(obj):
    """Find first dict that looks like a HeatSeeker gamma matrix."""
    for d in walk_dicts(obj):
        strikes = first(d, "Strikes", "strikes")
        exps = first(d, "Expirations", "expirations")
        vals = first(d, "GammaValues", "gammaValues", "values")
        spot = first(d, "CurrentSpot", "currentSpot", "spot")
        if isinstance(strikes, list) and isinstance(exps, list) and isinstance(vals, list) and num(spot) is not None:
            return d
    raise ValueError("No HeatSeeker-like gamma matrix found.")


def load_json(path: Path):
    txt = path.read_text(encoding="utf-8")
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        rows = []
        for line in txt.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows


def extract_setups(obj):
    out = []
    if isinstance(obj, dict):
        if isinstance(obj.get("setups"), list):
            out.extend([x for x in obj["setups"] if isinstance(x, dict)])
        elif "floor" in obj or "floor_pok" in obj:
            out.append(obj)
        else:
            for v in obj.values():
                out.extend(extract_setups(v))
    elif isinstance(obj, list):
        for x in obj:
            out.extend(extract_setups(x))
    return out


def matrix_data(obj):
    d = find_matrix_obj(obj)
    spot = num(first(d, "CurrentSpot", "currentSpot", "spot"))
    strikes = [num(x) for x in first(d, "Strikes", "strikes")]
    exps = [str(x) for x in first(d, "Expirations", "expirations")]
    vals = first(d, "GammaValues", "gammaValues", "values")
    if not strikes or not exps:
        raise ValueError("Empty strikes/expirations.")
    return d, spot, strikes, exps, vals


def get_col(strikes, vals, col):
    rows = []
    for i, k in enumerate(strikes):
        if k is None:
            continue
        row = vals[i] if i < len(vals) and isinstance(vals[i], list) else []
        v = num(row[col]) if 0 <= col < len(row) else None
        if v is not None and v != 0:
            rows.append({"strike": k, "exposure": v})
    return rows


def enrich_significance(cells, z_min=DEFAULT_Z_MIN, pok_min=DEFAULT_POK_MIN):
    if not cells:
        return []
    mags = [abs(c["exposure"]) for c in cells]
    mean = sum(mags) / len(mags)
    sigma = math.sqrt(sum((x - mean) ** 2 for x in mags) / len(mags))
    king = max(mags)
    out = []
    for c, mag in zip(cells, mags):
        z = (mag - mean) / sigma if sigma > 0 else 0.0
        pok = mag / king if king > 0 else 0.0
        x = dict(c)
        x.update({
            "abs_exposure": mag,
            "z": z,
            "pok_col": pok,
            "significant": (z >= z_min or pok >= pok_min),
        })
        out.append(x)
    return out


def attach_global_pok(cells, all_cells):
    denom = max((abs(c["exposure"]) for c in all_cells), default=0.0)
    for c in cells:
        c["pok_global_matrix"] = abs(c["exposure"]) / denom if denom > 0 else 0.0
    return cells


def strongest(rows):
    return max(rows, key=lambda x: abs(x["exposure"])) if rows else None


def nearest(rows, spot):
    return min(rows, key=lambda x: (abs(x["strike"] - spot), -abs(x["exposure"]))) if rows else None


def candidates(front, spot, symbol):
    below = [x for x in front if x["strike"] <= spot]
    sig = [x for x in below if x["significant"]]
    pos_sig = [x for x in sig if x["exposure"] > 0]
    king = strongest(front)
    step = STRIKE_STEPS.get(symbol or "", None)
    king_at = None
    if king and step is not None and abs(king["strike"] - spot) <= step:
        king_at = king

    return {
        "H1_front_strongest_below_all": strongest(below),
        "H2_front_nearest_below_all": nearest(below, spot),
        "H3_front_strongest_below_significant": strongest(sig),
        "H4_front_nearest_below_significant": nearest(sig, spot),
        "H5_front_strongest_positive_below_significant": strongest(pos_sig),
        "H6_front_nearest_positive_below_significant": nearest(pos_sig, spot),
        "H7_front_king_at_spot": king_at,
    }


def match_setup(setups, symbol):
    if not setups:
        return None
    if symbol:
        same = [s for s in setups if normalize_symbol(first(s, "symbol", "ticker")) == symbol]
        if same:
            return same[0]
    return setups[0]


def fmt(x):
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.10g}"
    return str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heatmap", required=True, type=Path, help="Observed HeatSeeker matrix JSON/JSONL")
    ap.add_argument("--setup", type=Path, help="Observed Midas/Peregrine setup JSON/JSONL")
    ap.add_argument("--symbol", help="Ticker, e.g. MU, SPY")
    ap.add_argument("--front-col", type=int, default=0, help="Candidate Column-1 index (default 0)")
    ap.add_argument("--guard-col", type=int, default=1, help="Candidate Column-2 index (default 1)")
    ap.add_argument("--z-min", type=float, default=DEFAULT_Z_MIN)
    ap.add_argument("--pok-min", type=float, default=DEFAULT_POK_MIN)
    ap.add_argument("--floor-tol", type=float, default=1e-9)
    ap.add_argument("--pok-tol", type=float, default=0.02)
    ap.add_argument("--outdir", type=Path, default=Path("SKYLIT_FLOOR_AUDIT"))
    args = ap.parse_args()

    hobj = load_json(args.heatmap)
    _, spot, strikes, exps, vals = matrix_data(hobj)

    symbol = normalize_symbol(args.symbol)
    setups = extract_setups(load_json(args.setup)) if args.setup else []
    setup = match_setup(setups, symbol)
    if setup and not symbol:
        symbol = normalize_symbol(first(setup, "symbol", "ticker"))

    if args.front_col < 0 or args.front_col >= len(exps):
        raise SystemExit(f"--front-col {args.front_col} outside 0..{len(exps)-1}")

    all_cells = []
    for col in range(len(exps)):
        for c in get_col(strikes, vals, col):
            x = dict(c)
            x["expiration"] = exps[col]
            x["col"] = col
            all_cells.append(x)

    front = get_col(strikes, vals, args.front_col)
    front = enrich_significance(front, args.z_min, args.pok_min)
    attach_global_pok(front, all_cells)

    cands = candidates(front, spot, symbol)
    obs_floor = num(setup.get("floor")) if setup else None
    obs_pok = num(setup.get("floor_pok")) if setup else None
    setup_class = setup.get("setup_class") if setup else None

    args.outdir.mkdir(parents=True, exist_ok=True)

    node_csv = args.outdir / "front_column_nodes.csv"
    with node_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "strike", "exposure", "abs_exposure", "z", "pok_col",
            "pok_global_matrix", "significant", "below_spot"
        ])
        w.writeheader()
        for c in sorted(front, key=lambda x: x["strike"]):
            row = dict(c)
            row["below_spot"] = c["strike"] <= spot
            w.writerow({k: row.get(k) for k in w.fieldnames})

    cand_csv = args.outdir / "floor_candidates.csv"
    cand_rows = []
    for name, c in cands.items():
        row = {
            "candidate": name,
            "candidate_floor": c["strike"] if c else None,
            "candidate_exposure": c["exposure"] if c else None,
            "candidate_z": c["z"] if c else None,
            "candidate_pok_col": c["pok_col"] if c else None,
            "candidate_pok_global_matrix": c["pok_global_matrix"] if c else None,
            "observed_floor": obs_floor,
            "observed_floor_pok": obs_pok,
            "floor_abs_error": abs(c["strike"] - obs_floor) if c and obs_floor is not None else None,
            "floor_exact_within_tol": (abs(c["strike"] - obs_floor) <= args.floor_tol) if c and obs_floor is not None else None,
            "pok_col_abs_error": abs(c["pok_col"] - obs_pok) if c and obs_pok is not None else None,
            "pok_col_within_tol": (abs(c["pok_col"] - obs_pok) <= args.pok_tol) if c and obs_pok is not None else None,
            "pok_global_abs_error": abs(c["pok_global_matrix"] - obs_pok) if c and obs_pok is not None else None,
            "pok_global_within_tol": (abs(c["pok_global_matrix"] - obs_pok) <= args.pok_tol) if c and obs_pok is not None else None,
        }
        cand_rows.append(row)

    with cand_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cand_rows[0].keys()))
        w.writeheader()
        w.writerows(cand_rows)

    guard_rows = []
    if 0 <= args.guard_col < len(exps):
        guard = enrich_significance(get_col(strikes, vals, args.guard_col), args.z_min, args.pok_min)
        attach_global_pok(guard, all_cells)
        for c in guard:
            if c["significant"] and c["strike"] <= spot:
                guard_rows.append(c)

    audit = {
        "doctrine": {
            "claim": "behavioral candidate audit only",
            "server_source_recovered": False,
            "synthetic_gex_vex": False,
            "reconstructed_iv": False,
        },
        "input": {
            "heatmap": str(args.heatmap),
            "setup": str(args.setup) if args.setup else None,
            "symbol": symbol,
            "spot": spot,
            "expirations": exps,
            "front_col": args.front_col,
            "front_expiration": exps[args.front_col],
            "guard_col": args.guard_col if args.guard_col < len(exps) else None,
            "guard_expiration": exps[args.guard_col] if args.guard_col < len(exps) else None,
        },
        "recovered_client_semantics_used": {
            "z_min": args.z_min,
            "pok_min": args.pok_min,
            "combinator": "OR",
            "pok_formula": "abs(exposure)/max(abs(exposure))",
        },
        "observed_setup": {
            "floor": obs_floor,
            "floor_pok": obs_pok,
            "setup_class": setup_class,
        } if setup else None,
        "candidates": cand_rows,
        "guard_column_significant_below_spot": guard_rows,
    }
    (args.outdir / "audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    exact = [r for r in cand_rows if r["floor_exact_within_tol"] is True]
    both_col = [r for r in exact if r["pok_col_within_tol"] is True]
    both_global = [r for r in exact if r["pok_global_within_tol"] is True]

    lines = [
        "# Skylit FLOOR candidate audit",
        "",
        "## Doctrine",
        "",
        "- This is a behavioral compatibility test, not recovery of proprietary server code.",
        "- No synthetic GEX/VEX, reconstructed IV, Black-Scholes gamma or hypothetical dealer positioning.",
        "",
        "## Snapshot",
        "",
        f"- symbol: `{symbol or 'unknown'}`",
        f"- spot: **{fmt(spot)}**",
        f"- assumed Column-1: index **{args.front_col}**, expiration `{exps[args.front_col]}`",
    ]
    if args.guard_col < len(exps):
        lines.append(f"- assumed Column-2: index **{args.guard_col}**, expiration `{exps[args.guard_col]}`")
    if setup:
        lines += [
            f"- observed server floor: **{fmt(obs_floor)}**",
            f"- observed server floor_pok: **{fmt(obs_pok)}**",
            f"- observed setup_class: `{setup_class}`",
        ]
    else:
        lines.append("- no setup payload supplied: candidates generated, but no server-output match can be scored.")

    lines += [
        "",
        "## Client semantics reused as candidate vocabulary",
        "",
        f"- `pctOfKing = abs(exposure) / max(abs(exposure))`",
        f"- significant if `z >= {args.z_min:g} OR pctOfKing >= {args.pok_min:g}`",
        "",
        "## Candidate results",
        "",
        "| candidate | floor | POK(col1) | z | floor match | POK match |",
        "|---|---:|---:|---:|:---:|:---:|",
    ]
    for r in cand_rows:
        lines.append(
            f"| {r['candidate']} | {fmt(r['candidate_floor'])} | "
            f"{fmt(r['candidate_pok_col'])} | {fmt(r['candidate_z'])} | "
            f"{'YES' if r['floor_exact_within_tol'] else ('NO' if r['floor_exact_within_tol'] is False else 'n/a')} | "
            f"{'YES' if r['pok_col_within_tol'] else ('NO' if r['pok_col_within_tol'] is False else 'n/a')} |"
        )

    lines += ["", "## Interpretation", ""]
    if setup:
        if both_col:
            lines.append("- At least one candidate matches both observed `floor` and observed `floor_pok` using a Column-1 denominator.")
            lines.append("- Status: **COMPATIBLE ON THIS SAMPLE ONLY**. Freeze candidate before testing new chronological samples.")
        elif both_global:
            lines.append("- Floor candidate match found, but `floor_pok` fits the whole-matrix King denominator better than the Column-1 denominator.")
            lines.append("- Status: **DENOMINATOR HYPOTHESIS NEEDS MORE SAMPLES**.")
        elif exact:
            lines.append("- At least one candidate reproduces the floor strike, but not `floor_pok` within tolerance.")
            lines.append("- Status: **PARTIAL MATCH**; selection and node-strength normalization may use different universes.")
        else:
            lines.append("- None of the enumerated simple Column-1 candidates reproduces the observed floor.")
            lines.append("- Status: **FALSIFIED FOR THIS SNAPSHOT** for these candidate families.")
    else:
        lines.append("- A synchronized setup payload is required to rank/falsify the candidate rules.")

    lines += [
        "",
        "## Required next proof",
        "",
        "Use synchronized pairs: one observed `/midas/setups` or `/peregrine/setups` object and the HeatSeeker gamma matrix from the same symbol/time.",
        "Do not tune after seeing holdout outcomes; freeze the candidate rule first.",
        "",
    ]

    (args.outdir / "AUDIT_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")

    print("Wrote:", args.outdir / "AUDIT_SUMMARY.md")
    print("Wrote:", cand_csv)
    print("Wrote:", node_csv)
    print("Wrote:", args.outdir / "audit.json")
    if setup:
        print("Observed floor:", obs_floor, "floor_pok:", obs_pok)
        print("Exact floor candidates:", len(exact))
    else:
        print("No setup payload supplied; candidate generation only.")


if __name__ == "__main__":
    main()
