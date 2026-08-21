#!/usr/bin/env python3
"""
mu_crown_v01.py

H-MU-CROWN-v0.1 — frozen exploratory rule.

Purpose
-------
Evaluate a gamma-board snapshot at T0 WITHOUT using T1 to decide whether the
board is TRANSITION_ARMED. If a T1 snapshot is supplied, evaluate the realized
outcome separately (ESCAPE_UP / ESCAPE_DOWN / CROWN_CHANGE).

This is NOT a validated trading strategy. It is an in-sample hypothesis
operationalized from the MU 2026-08-20 Rosetta pair.

Frozen v0.1 thresholds
----------------------
CROWN_PRESSURE_MIN = 0.75
POCKET_DENSITY_MAX = 0.30
BOUNDARY_DISTANCE_MAX_PCT = 1.00
CHALLENGER_GROWTH_MIN_PCT = 0.0  # strictly greater than zero

Operational definitions
-----------------------
King:
    strike with maximum absolute GEX at T0.

Challenger:
    non-King strike with maximum absolute GEX at T0.

Negative-GEX boundaries:
    nearest negative-GEX strike below spot and nearest negative-GEX strike
    above spot.

Pocket density:
    sum(abs(GEX)) for strikes strictly between the two negative-GEX boundaries,
    divided by abs(King GEX).

Crown pressure:
    abs(Challenger GEX) / abs(King GEX).

TRANSITION_ARMED:
    - both negative-GEX boundaries exist,
    - both are within 1.00% of spot,
    - pocket density <= 0.30,
    - crown pressure >= 0.75,
    - challenger's T0 growth_pct > 0.

Outcome:
    ESCAPE_UP if T1 spot crosses the T0 upper negative-GEX boundary.
    ESCAPE_DOWN if T1 spot crosses the T0 lower negative-GEX boundary.

CROWN_CHANGE:
    the original T0 challenger exceeds the original T0 King in absolute GEX
    at T1. This is measured against the SAME two strikes to avoid redefining
    the comparison after seeing T1.

CSV format
----------
Required columns:
    strike,gex
Optional:
    growth_pct

Example:
    strike,gex,growth_pct
    935,-1825000,
    940,712700,
    945,347100,
    950,-3815900,
    980,1406300,
    990,-991800,
    1000,2947100,18

Usage
-----
Run built-in MU demo:
    python3 mu_crown_v01.py --demo-mu

Run generic T0 only:
    python3 mu_crown_v01.py --t0 board_t0.csv --spot0 942.5

Run T0 + T1:
    python3 mu_crown_v01.py \
        --t0 board_t0.csv --spot0 942.5 \
        --t1 board_t1.csv --spot1 960
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# -----------------------------
# Frozen v0.1 thresholds
# -----------------------------
CROWN_PRESSURE_MIN = 0.75
POCKET_DENSITY_MAX = 0.30
BOUNDARY_DISTANCE_MAX_PCT = 1.00
CHALLENGER_GROWTH_MIN_PCT = 0.0  # strictly greater than zero


@dataclass(frozen=True)
class Node:
    strike: float
    gex: float
    growth_pct: Optional[float] = None


@dataclass
class T0Result:
    spot: float
    king_strike: float
    king_gex: float
    challenger_strike: float
    challenger_gex: float
    challenger_growth_pct: Optional[float]
    crown_pressure: float
    lower_boundary_strike: Optional[float]
    lower_boundary_gex: Optional[float]
    lower_boundary_distance_pct: Optional[float]
    upper_boundary_strike: Optional[float]
    upper_boundary_gex: Optional[float]
    upper_boundary_distance_pct: Optional[float]
    pocket_abs_gex: Optional[float]
    pocket_density: Optional[float]
    checks: Dict[str, bool]
    state: str


@dataclass
class OutcomeResult:
    spot0: float
    spot1: float
    move_pct: float
    crossed_upper_boundary: bool
    crossed_lower_boundary: bool
    escape_state: str
    original_king_strike: float
    original_king_gex_t0: float
    original_king_gex_t1: Optional[float]
    original_challenger_strike: float
    original_challenger_gex_t0: float
    original_challenger_gex_t1: Optional[float]
    crown_pressure_t1_same_pair: Optional[float]
    crown_change: bool
    t1_actual_king_strike: Optional[float]
    t1_actual_king_gex: Optional[float]


def pct_distance(strike: float, spot: float) -> float:
    return abs(strike / spot - 1.0) * 100.0


def load_csv(path: Path) -> List[Node]:
    if not path.exists():
        raise FileNotFoundError(path)

    nodes: List[Node] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: CSV has no header")

        fields = {x.strip().lower() for x in reader.fieldnames}
        if "strike" not in fields or "gex" not in fields:
            raise ValueError(f"{path}: required columns are strike,gex")

        # Map original header spelling -> normalized
        header_map = {x.strip().lower(): x for x in reader.fieldnames}

        for row_num, row in enumerate(reader, start=2):
            try:
                strike = float(row[header_map["strike"]])
                gex = float(row[header_map["gex"]])
            except Exception as exc:
                raise ValueError(f"{path}:{row_num}: invalid strike/gex") from exc

            growth = None
            if "growth_pct" in header_map:
                raw = (row.get(header_map["growth_pct"]) or "").strip()
                if raw:
                    growth = float(raw)

            nodes.append(Node(strike=strike, gex=gex, growth_pct=growth))

    return validate_nodes(nodes, source=str(path))


def validate_nodes(nodes: Iterable[Node], source: str = "input") -> List[Node]:
    x = sorted(list(nodes), key=lambda n: n.strike)
    if len(x) < 2:
        raise ValueError(f"{source}: need at least 2 nodes")

    seen = set()
    for n in x:
        if not math.isfinite(n.strike) or not math.isfinite(n.gex):
            raise ValueError(f"{source}: non-finite strike/gex")
        if n.strike in seen:
            raise ValueError(f"{source}: duplicate strike {n.strike}")
        seen.add(n.strike)

    return x


def king_and_challenger(nodes: List[Node]) -> Tuple[Node, Node]:
    ranked = sorted(nodes, key=lambda n: abs(n.gex), reverse=True)
    return ranked[0], ranked[1]


def negative_boundaries(nodes: List[Node], spot: float) -> Tuple[Optional[Node], Optional[Node]]:
    below = [n for n in nodes if n.strike < spot and n.gex < 0]
    above = [n for n in nodes if n.strike > spot and n.gex < 0]

    lower = max(below, key=lambda n: n.strike) if below else None
    upper = min(above, key=lambda n: n.strike) if above else None
    return lower, upper


def evaluate_t0(nodes: List[Node], spot: float) -> T0Result:
    if spot <= 0:
        raise ValueError("spot must be > 0")

    king, challenger = king_and_challenger(nodes)
    crown_pressure = abs(challenger.gex) / abs(king.gex) if king.gex != 0 else math.inf

    lower, upper = negative_boundaries(nodes, spot)

    lower_dist = pct_distance(lower.strike, spot) if lower else None
    upper_dist = pct_distance(upper.strike, spot) if upper else None

    pocket_abs_gex = None
    pocket_density = None

    if lower and upper:
        inside = [n for n in nodes if lower.strike < n.strike < upper.strike]
        pocket_abs_gex = sum(abs(n.gex) for n in inside)
        pocket_density = (
            pocket_abs_gex / abs(king.gex) if king.gex != 0 else math.inf
        )

    checks = {
        "two_negative_boundaries": lower is not None and upper is not None,
        "lower_boundary_within_1pct": (
            lower_dist is not None and lower_dist <= BOUNDARY_DISTANCE_MAX_PCT
        ),
        "upper_boundary_within_1pct": (
            upper_dist is not None and upper_dist <= BOUNDARY_DISTANCE_MAX_PCT
        ),
        "pocket_density_le_0_30": (
            pocket_density is not None and pocket_density <= POCKET_DENSITY_MAX
        ),
        "crown_pressure_ge_0_75": crown_pressure >= CROWN_PRESSURE_MIN,
        "challenger_growth_positive": (
            challenger.growth_pct is not None
            and challenger.growth_pct > CHALLENGER_GROWTH_MIN_PCT
        ),
    }

    armed = all(checks.values())
    state = "TRANSITION_ARMED" if armed else "NOT_ARMED"

    return T0Result(
        spot=spot,
        king_strike=king.strike,
        king_gex=king.gex,
        challenger_strike=challenger.strike,
        challenger_gex=challenger.gex,
        challenger_growth_pct=challenger.growth_pct,
        crown_pressure=crown_pressure,
        lower_boundary_strike=lower.strike if lower else None,
        lower_boundary_gex=lower.gex if lower else None,
        lower_boundary_distance_pct=lower_dist,
        upper_boundary_strike=upper.strike if upper else None,
        upper_boundary_gex=upper.gex if upper else None,
        upper_boundary_distance_pct=upper_dist,
        pocket_abs_gex=pocket_abs_gex,
        pocket_density=pocket_density,
        checks=checks,
        state=state,
    )


def node_map(nodes: List[Node]) -> Dict[float, Node]:
    return {n.strike: n for n in nodes}


def evaluate_outcome(
    t0_nodes: List[Node],
    spot0: float,
    t0: T0Result,
    t1_nodes: List[Node],
    spot1: float,
) -> OutcomeResult:
    m1 = node_map(t1_nodes)

    crossed_upper = (
        t0.upper_boundary_strike is not None
        and spot0 < t0.upper_boundary_strike <= spot1
    )
    crossed_lower = (
        t0.lower_boundary_strike is not None
        and spot0 > t0.lower_boundary_strike >= spot1
    )

    if crossed_upper and not crossed_lower:
        escape_state = "ESCAPE_UP"
    elif crossed_lower and not crossed_upper:
        escape_state = "ESCAPE_DOWN"
    elif crossed_upper and crossed_lower:
        # This should be rare/impossible with one endpoint spot, but keep explicit.
        escape_state = "BOTH_BOUNDARIES_CROSSED"
    else:
        escape_state = "NO_ESCAPE"

    old_king_t1 = m1.get(t0.king_strike)
    old_challenger_t1 = m1.get(t0.challenger_strike)

    cp_t1 = None
    crown_change = False
    if old_king_t1 and old_challenger_t1 and old_king_t1.gex != 0:
        cp_t1 = abs(old_challenger_t1.gex) / abs(old_king_t1.gex)
        crown_change = cp_t1 > 1.0

    t1_actual_king = max(t1_nodes, key=lambda n: abs(n.gex)) if t1_nodes else None

    return OutcomeResult(
        spot0=spot0,
        spot1=spot1,
        move_pct=(spot1 / spot0 - 1.0) * 100.0,
        crossed_upper_boundary=crossed_upper,
        crossed_lower_boundary=crossed_lower,
        escape_state=escape_state,
        original_king_strike=t0.king_strike,
        original_king_gex_t0=t0.king_gex,
        original_king_gex_t1=old_king_t1.gex if old_king_t1 else None,
        original_challenger_strike=t0.challenger_strike,
        original_challenger_gex_t0=t0.challenger_gex,
        original_challenger_gex_t1=old_challenger_t1.gex if old_challenger_t1 else None,
        crown_pressure_t1_same_pair=cp_t1,
        crown_change=crown_change,
        t1_actual_king_strike=t1_actual_king.strike if t1_actual_king else None,
        t1_actual_king_gex=t1_actual_king.gex if t1_actual_king else None,
    )


def fmt_money(x: Optional[float]) -> str:
    if x is None:
        return "NA"
    sign = "-" if x < 0 else "+"
    a = abs(x)
    if a >= 1_000_000:
        return f"{sign}${a / 1_000_000:.4f}M"
    if a >= 1_000:
        return f"{sign}${a / 1_000:.1f}K"
    return f"{sign}${a:.2f}"


def fmt_pct(x: Optional[float], digits: int = 3) -> str:
    return "NA" if x is None else f"{x:.{digits}f}%"


def print_t0(r: T0Result) -> None:
    print("\n=== H-MU-CROWN-v0.1 | T0 SIGNAL ONLY ===")
    print(f"Spot                       : {r.spot:.4f}")
    print(f"King                       : {r.king_strike:g}  {fmt_money(r.king_gex)}")
    print(
        f"Challenger                 : {r.challenger_strike:g}  "
        f"{fmt_money(r.challenger_gex)}"
    )
    print(
        f"Challenger growth (T0)     : "
        f"{fmt_pct(r.challenger_growth_pct, 2)}"
    )
    print(f"Crown Pressure             : {r.crown_pressure:.3f}")

    print(
        f"Lower -GEX boundary        : "
        f"{r.lower_boundary_strike if r.lower_boundary_strike is not None else 'NA'}  "
        f"{fmt_money(r.lower_boundary_gex)}  "
        f"dist={fmt_pct(r.lower_boundary_distance_pct)}"
    )
    print(
        f"Upper -GEX boundary        : "
        f"{r.upper_boundary_strike if r.upper_boundary_strike is not None else 'NA'}  "
        f"{fmt_money(r.upper_boundary_gex)}  "
        f"dist={fmt_pct(r.upper_boundary_distance_pct)}"
    )
    print(f"Pocket |GEX|               : {fmt_money(r.pocket_abs_gex)}")
    print(
        f"Pocket Density / |King|    : "
        f"{'NA' if r.pocket_density is None else f'{r.pocket_density:.3f}'}"
    )

    print("\nFrozen checks:")
    for k, v in r.checks.items():
        print(f"  {'PASS' if v else 'FAIL':4}  {k}")

    print(f"\nSTATE                      : {r.state}")


def print_outcome(r: OutcomeResult) -> None:
    print("\n=== OUTCOME | T1 USED ONLY HERE ===")
    print(f"Spot T0 -> T1              : {r.spot0:.4f} -> {r.spot1:.4f}")
    print(f"Move                       : {r.move_pct:+.3f}%")
    print(f"Crossed upper boundary     : {r.crossed_upper_boundary}")
    print(f"Crossed lower boundary     : {r.crossed_lower_boundary}")
    print(f"ESCAPE                     : {r.escape_state}")

    print(
        f"Original King              : {r.original_king_strike:g}  "
        f"{fmt_money(r.original_king_gex_t0)} -> {fmt_money(r.original_king_gex_t1)}"
    )
    print(
        f"Original Challenger        : {r.original_challenger_strike:g}  "
        f"{fmt_money(r.original_challenger_gex_t0)} -> "
        f"{fmt_money(r.original_challenger_gex_t1)}"
    )
    print(
        f"Crown Pressure T1 (same pair): "
        f"{'NA' if r.crown_pressure_t1_same_pair is None else f'{r.crown_pressure_t1_same_pair:.3f}'}"
    )
    print(f"CROWN_CHANGE               : {r.crown_change}")
    print(
        f"Actual T1 King             : "
        f"{r.t1_actual_king_strike if r.t1_actual_king_strike is not None else 'NA'}  "
        f"{fmt_money(r.t1_actual_king_gex)}"
    )


def mu_demo() -> Tuple[List[Node], float, List[Node], float]:
    # Values transcribed from the two MU Skylit cards discussed in-session.
    # T0 growth_pct is ONLY supplied for the challenger (1000) because that
    # is the growth value used in the frozen T0 hypothesis.
    t0 = validate_nodes(
        [
            Node(930, +1_381_400),
            Node(935, -1_825_000),
            Node(940, +712_700),
            Node(945, +347_100),
            Node(950, -3_815_900),
            Node(980, +1_406_300),
            Node(990, -991_800),
            Node(1000, +2_947_100, growth_pct=18.0),
        ],
        source="MU demo T0",
    )

    t1 = validate_nodes(
        [
            Node(930, +1_025_500),
            Node(935, -1_207_200),
            Node(940, +682_300),
            Node(945, +210_300),
            Node(950, -3_809_800),
            Node(960, -88_000),
            Node(980, +1_624_700),
            Node(990, -1_743_400),
            Node(1000, +3_907_300),
        ],
        source="MU demo T1",
    )
    return t0, 942.5, t1, 960.0


def write_json(path: Path, t0: T0Result, outcome: Optional[OutcomeResult]) -> None:
    payload = {
        "model": "H-MU-CROWN-v0.1",
        "frozen_thresholds": {
            "crown_pressure_min": CROWN_PRESSURE_MIN,
            "pocket_density_max": POCKET_DENSITY_MAX,
            "boundary_distance_max_pct": BOUNDARY_DISTANCE_MAX_PCT,
            "challenger_growth_min_pct_exclusive": CHALLENGER_GROWTH_MIN_PCT,
        },
        "t0": asdict(t0),
        "outcome": asdict(outcome) if outcome else None,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Frozen H-MU-CROWN-v0.1 evaluator")
    p.add_argument("--demo-mu", action="store_true", help="Run built-in MU Rosetta pair")
    p.add_argument("--t0", type=Path, help="T0 board CSV")
    p.add_argument("--spot0", type=float, help="T0 spot")
    p.add_argument("--t1", type=Path, help="Optional T1 board CSV")
    p.add_argument("--spot1", type=float, help="Optional T1 spot")
    p.add_argument("--json-out", type=Path, help="Optional JSON result output")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.demo_mu:
        t0_nodes, spot0, t1_nodes, spot1 = mu_demo()
    else:
        if args.t0 is None or args.spot0 is None:
            print("ERROR: use --demo-mu OR provide --t0 and --spot0", file=sys.stderr)
            return 2
        t0_nodes = load_csv(args.t0)
        spot0 = args.spot0

        if (args.t1 is None) ^ (args.spot1 is None):
            print("ERROR: --t1 and --spot1 must be provided together", file=sys.stderr)
            return 2

        if args.t1 is not None:
            t1_nodes = load_csv(args.t1)
            spot1 = args.spot1
        else:
            t1_nodes = None
            spot1 = None

    t0_result = evaluate_t0(t0_nodes, spot0)
    print_t0(t0_result)

    outcome = None
    if t1_nodes is not None and spot1 is not None:
        outcome = evaluate_outcome(t0_nodes, spot0, t0_result, t1_nodes, spot1)
        print_outcome(outcome)

    if args.json_out:
        write_json(args.json_out, t0_result, outcome)
        print(f"\nJSON written to: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
