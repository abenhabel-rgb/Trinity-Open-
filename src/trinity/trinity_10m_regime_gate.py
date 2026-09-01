"""Observed-feature classifier for the Trinity first-ten-minute hypothesis.

The classifier formalizes one narrow rule inferred from an observed Skylit
description: an upside trend regime requires SPX upside route evidence plus
tested-and-held floors in SPY and QQQ.  It consumes timestamped observations;
it does not reconstruct gamma, infer missing features, or evaluate returns.

A TREND_UP row is a mechanically reproduced signal, not economic validation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence


SIGNAL_NAME = "TRINITY_10M_TREND_UP_V0"

REQUIRED_COLUMNS = {
    "session_id",
    "market_open_et",
    "decision_time_et",
    "spx_air_pocket_up",
    "spx_route_clear",
    "spy_spot",
    "spy_floor",
    "spy_floor_tested",
    "spy_floor_held",
    "qqq_spot",
    "qqq_floor",
    "qqq_floor_tested",
    "qqq_floor_held",
    "spx_source",
    "spy_source",
    "qqq_source",
}

FEATURE_NAMES = (
    "spx_air_pocket_up",
    "spx_route_clear",
    "spy_spot",
    "spy_floor",
    "spy_floor_tested",
    "spy_floor_held",
    "qqq_spot",
    "qqq_floor",
    "qqq_floor_tested",
    "qqq_floor_held",
)


class DataValidationError(ValueError):
    """Raised when an input value is invalid rather than merely absent."""


@dataclass(frozen=True)
class TrinityObservation:
    session_id: str
    market_open: datetime | None
    decision_time: datetime | None
    spx_air_pocket_up: bool | None
    spx_route_clear: bool | None
    spy_spot: float | None
    spy_floor: float | None
    spy_floor_tested: bool | None
    spy_floor_held: bool | None
    qqq_spot: float | None
    qqq_floor: float | None
    qqq_floor_tested: bool | None
    qqq_floor_held: bool | None
    spx_source: str
    spy_source: str
    qqq_source: str
    notes: str = ""


@dataclass(frozen=True)
class GateConfig:
    max_minutes_after_open: float = 10.0
    floor_tolerance_bps: float = 5.0


@dataclass(frozen=True)
class TrinityResult:
    session_id: str
    signal_name: str
    lifecycle: str
    reason: str
    market_open_et: str
    decision_time_et: str
    minutes_after_open: float | None
    spx_air_pocket_up: bool | None
    spx_route_clear: bool | None
    spy_spot: float | None
    spy_floor: float | None
    spy_floor_distance_bps: float | None
    spy_floor_tested: bool | None
    spy_floor_held: bool | None
    spy_above_floor: bool | None
    qqq_spot: float | None
    qqq_floor: float | None
    qqq_floor_distance_bps: float | None
    qqq_floor_tested: bool | None
    qqq_floor_held: bool | None
    qqq_above_floor: bool | None
    spx_source: str
    spy_source: str
    qqq_source: str
    notes: str


def parse_optional_bool(value: str, *, field: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"", "na", "n/a", "null", "none"}:
        return None
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise DataValidationError(f"{field}: expected boolean or blank, got {value!r}")


def parse_optional_float(value: str, *, field: str) -> float | None:
    raw = value.strip()
    if raw.lower() in {"", "na", "n/a", "null", "none"}:
        return None
    try:
        parsed = float(raw)
    except ValueError as exc:
        raise DataValidationError(f"{field}: expected number or blank, got {value!r}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise DataValidationError(f"{field}: expected a finite positive value")
    return parsed


def parse_optional_timestamp(value: str, *, field: str) -> datetime | None:
    raw = value.strip()
    if raw.lower() in {"", "na", "n/a", "null", "none"}:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataValidationError(f"{field}: invalid ISO-8601 timestamp {raw!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DataValidationError(f"{field}: timezone offset is required")
    return parsed


def _require_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(fieldnames or []))
    if missing:
        raise DataValidationError(f"{path}: missing columns: {', '.join(missing)}")


def load_observations(path: Path) -> list[TrinityObservation]:
    observations: list[TrinityObservation] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, path)
        for line_number, row in enumerate(reader, start=2):
            prefix = f"{path}:{line_number}"
            session_id = row["session_id"].strip()
            if not session_id:
                raise DataValidationError(f"{prefix}: session_id is required")
            if session_id in seen:
                raise DataValidationError(f"{prefix}: duplicate session_id {session_id!r}")
            seen.add(session_id)

            observations.append(
                TrinityObservation(
                    session_id=session_id,
                    market_open=parse_optional_timestamp(
                        row["market_open_et"], field=f"{prefix}:market_open_et"
                    ),
                    decision_time=parse_optional_timestamp(
                        row["decision_time_et"], field=f"{prefix}:decision_time_et"
                    ),
                    spx_air_pocket_up=parse_optional_bool(
                        row["spx_air_pocket_up"], field=f"{prefix}:spx_air_pocket_up"
                    ),
                    spx_route_clear=parse_optional_bool(
                        row["spx_route_clear"], field=f"{prefix}:spx_route_clear"
                    ),
                    spy_spot=parse_optional_float(
                        row["spy_spot"], field=f"{prefix}:spy_spot"
                    ),
                    spy_floor=parse_optional_float(
                        row["spy_floor"], field=f"{prefix}:spy_floor"
                    ),
                    spy_floor_tested=parse_optional_bool(
                        row["spy_floor_tested"], field=f"{prefix}:spy_floor_tested"
                    ),
                    spy_floor_held=parse_optional_bool(
                        row["spy_floor_held"], field=f"{prefix}:spy_floor_held"
                    ),
                    qqq_spot=parse_optional_float(
                        row["qqq_spot"], field=f"{prefix}:qqq_spot"
                    ),
                    qqq_floor=parse_optional_float(
                        row["qqq_floor"], field=f"{prefix}:qqq_floor"
                    ),
                    qqq_floor_tested=parse_optional_bool(
                        row["qqq_floor_tested"], field=f"{prefix}:qqq_floor_tested"
                    ),
                    qqq_floor_held=parse_optional_bool(
                        row["qqq_floor_held"], field=f"{prefix}:qqq_floor_held"
                    ),
                    spx_source=row["spx_source"].strip(),
                    spy_source=row["spy_source"].strip(),
                    qqq_source=row["qqq_source"].strip(),
                    notes=row.get("notes", "").strip(),
                )
            )
    return observations


def _base_result(
    observation: TrinityObservation,
    *,
    lifecycle: str,
    reason: str,
    minutes_after_open: float | None,
    spy_distance: float | None = None,
    spy_above: bool | None = None,
    qqq_distance: float | None = None,
    qqq_above: bool | None = None,
) -> TrinityResult:
    return TrinityResult(
        session_id=observation.session_id,
        signal_name=SIGNAL_NAME,
        lifecycle=lifecycle,
        reason=reason,
        market_open_et=observation.market_open.isoformat() if observation.market_open else "",
        decision_time_et=(
            observation.decision_time.isoformat() if observation.decision_time else ""
        ),
        minutes_after_open=minutes_after_open,
        spx_air_pocket_up=observation.spx_air_pocket_up,
        spx_route_clear=observation.spx_route_clear,
        spy_spot=observation.spy_spot,
        spy_floor=observation.spy_floor,
        spy_floor_distance_bps=spy_distance,
        spy_floor_tested=observation.spy_floor_tested,
        spy_floor_held=observation.spy_floor_held,
        spy_above_floor=spy_above,
        qqq_spot=observation.qqq_spot,
        qqq_floor=observation.qqq_floor,
        qqq_floor_distance_bps=qqq_distance,
        qqq_floor_tested=observation.qqq_floor_tested,
        qqq_floor_held=observation.qqq_floor_held,
        qqq_above_floor=qqq_above,
        spx_source=observation.spx_source,
        spy_source=observation.spy_source,
        qqq_source=observation.qqq_source,
        notes=observation.notes,
    )


def classify_observation(
    observation: TrinityObservation, config: GateConfig
) -> TrinityResult:
    if observation.market_open is None or observation.decision_time is None:
        return _base_result(
            observation,
            lifecycle="BLOCKED",
            reason="missing_timestamp",
            minutes_after_open=None,
        )

    elapsed = (observation.decision_time - observation.market_open).total_seconds() / 60.0
    if elapsed < 0:
        return _base_result(
            observation,
            lifecycle="BLOCKED",
            reason="decision_before_market_open",
            minutes_after_open=elapsed,
        )
    if elapsed > config.max_minutes_after_open:
        return _base_result(
            observation,
            lifecycle="BLOCKED",
            reason="decision_after_frozen_cutoff",
            minutes_after_open=elapsed,
        )

    missing_sources = [
        symbol
        for symbol, source in (
            ("SPX", observation.spx_source),
            ("SPY", observation.spy_source),
            ("QQQ", observation.qqq_source),
        )
        if not source
    ]
    if missing_sources:
        return _base_result(
            observation,
            lifecycle="BLOCKED",
            reason=f"missing_source:{','.join(missing_sources)}",
            minutes_after_open=elapsed,
        )

    missing_features = [
        name for name in FEATURE_NAMES if getattr(observation, name) is None
    ]
    if missing_features:
        return _base_result(
            observation,
            lifecycle="BLOCKED",
            reason=f"missing_feature:{','.join(missing_features)}",
            minutes_after_open=elapsed,
        )

    assert observation.spy_spot is not None and observation.spy_floor is not None
    assert observation.qqq_spot is not None and observation.qqq_floor is not None
    spy_distance = (observation.spy_spot / observation.spy_floor - 1.0) * 10_000.0
    qqq_distance = (observation.qqq_spot / observation.qqq_floor - 1.0) * 10_000.0
    spy_above = spy_distance >= -config.floor_tolerance_bps
    qqq_above = qqq_distance >= -config.floor_tolerance_bps

    checks = {
        "spx_air_pocket_up": observation.spx_air_pocket_up is True,
        "spx_route_clear": observation.spx_route_clear is True,
        "spy_floor_tested": observation.spy_floor_tested is True,
        "spy_floor_held": observation.spy_floor_held is True,
        "spy_above_floor": spy_above,
        "qqq_floor_tested": observation.qqq_floor_tested is True,
        "qqq_floor_held": observation.qqq_floor_held is True,
        "qqq_above_floor": qqq_above,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        return _base_result(
            observation,
            lifecycle="UNCONFIRMED",
            reason=f"failed:{','.join(failed)}",
            minutes_after_open=elapsed,
            spy_distance=spy_distance,
            spy_above=spy_above,
            qqq_distance=qqq_distance,
            qqq_above=qqq_above,
        )

    return _base_result(
        observation,
        lifecycle="TREND_UP",
        reason="trinity_upside_confluence",
        minutes_after_open=elapsed,
        spy_distance=spy_distance,
        spy_above=spy_above,
        qqq_distance=qqq_distance,
        qqq_above=qqq_above,
    )


def classify(
    observations: Sequence[TrinityObservation], config: GateConfig
) -> list[TrinityResult]:
    return [classify_observation(observation, config) for observation in observations]


def summarize(results: Sequence[TrinityResult], config: GateConfig) -> dict[str, object]:
    states = ("TREND_UP", "UNCONFIRMED", "BLOCKED")
    counts = {state: sum(row.lifecycle == state for row in results) for state in states}
    eligible = counts["TREND_UP"] + counts["UNCONFIRMED"]
    return {
        "signal_name": SIGNAL_NAME,
        "n_sessions": len(results),
        "n_trend_up": counts["TREND_UP"],
        "n_unconfirmed": counts["UNCONFIRMED"],
        "n_blocked": counts["BLOCKED"],
        "signal_rate_among_complete": counts["TREND_UP"] / eligible if eligible else None,
        "max_minutes_after_open": config.max_minutes_after_open,
        "floor_tolerance_bps": config.floor_tolerance_bps,
        "note": (
            "Observed-feature signal reconstruction only; no outcome or economic "
            "validation is performed."
        ),
    }


def write_results(path: Path, results: Sequence[TrinityResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(TrinityResult.__dataclass_fields__)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify the observed Trinity SPX/SPY/QQQ first-10-minute regime."
    )
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--max-minutes-after-open", type=float, default=10.0)
    parser.add_argument("--floor-tolerance-bps", type=float, default=5.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_minutes_after_open <= 0:
        raise SystemExit("--max-minutes-after-open must be positive")
    if args.floor_tolerance_bps < 0:
        raise SystemExit("--floor-tolerance-bps must be non-negative")

    config = GateConfig(
        max_minutes_after_open=args.max_minutes_after_open,
        floor_tolerance_bps=args.floor_tolerance_bps,
    )
    observations = load_observations(args.observations)
    results = classify(observations, config)
    summary = summarize(results, config)
    write_results(args.out, results)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
