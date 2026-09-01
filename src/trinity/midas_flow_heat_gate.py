"""Observed-data research scaffold for the Midas Flow -> Heat timing hypothesis.

This module does not reconstruct GEX/VEX and does not predict prices.  It tests
whether delaying a long-option entry from an observed Flowseeker-like event to
an observed Heatseeker-like trigger improves drawdown while retaining upside.

Both strategies use executable-side marks:

* entry: first observed ask at or after the event timestamp;
* liquidation / path valuation: observed bid;
* evaluation end: the same predeclared timestamp for both strategies.

Mechanical signal reproduction is not economic validation.  Results become
evidence only on untouched out-of-sample sessions with complete source data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import fmean
from typing import Iterable, Sequence


REQUIRED_EVENT_COLUMNS = {
    "candidate_id",
    "ticker",
    "contract",
    "direction",
    "flow_time_et",
    "heat_time_et",
    "evaluation_end_et",
    "flow_observed",
    "heat_observed",
    "heat_event",
    "breadth_confirmed",
    "flow_source",
    "heat_source",
}

REQUIRED_QUOTE_COLUMNS = {"candidate_id", "timestamp_et", "bid", "ask"}


class DataValidationError(ValueError):
    """Raised when an input would make a result ambiguous or non-reproducible."""


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    ticker: str
    contract: str
    direction: str
    flow_time: datetime
    heat_time: datetime | None
    evaluation_end: datetime
    flow_observed: bool
    heat_observed: bool
    heat_event: str
    breadth_confirmed: bool
    flow_source: str
    heat_source: str
    node_level: str = ""
    net_gex: str = ""
    net_vex: str = ""


@dataclass(frozen=True)
class Quote:
    candidate_id: str
    timestamp: datetime
    bid: float
    ask: float


@dataclass(frozen=True)
class PathMetrics:
    entry_time: str
    entry_ask: float
    end_time: str
    end_bid: float
    mae_pct: float
    mfe_pct: float
    end_return_pct: float


@dataclass(frozen=True)
class AnalysisRow:
    candidate_id: str
    ticker: str
    contract: str
    direction: str
    session_date: str
    lifecycle: str
    reason: str
    heat_event: str
    breadth_confirmed: bool
    node_level: str
    net_gex_observed: str
    net_vex_observed: str
    flow_entry_time: str = ""
    flow_entry_ask: float | None = None
    flow_mae_pct: float | None = None
    flow_mfe_pct: float | None = None
    flow_end_return_pct: float | None = None
    gated_entry_time: str = ""
    gated_entry_ask: float | None = None
    gated_mae_pct: float | None = None
    gated_mfe_pct: float | None = None
    gated_end_return_pct: float | None = None
    mae_improvement_pp: float | None = None
    mfe_retention_ratio: float | None = None
    end_return_lift_pp: float | None = None


@dataclass(frozen=True)
class GateConfig:
    allowed_heat_events: frozenset[str] = frozenset({"NODE_FLIP"})
    require_breadth: bool = False


def parse_bool(value: str, *, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n", ""}:
        return False
    raise DataValidationError(f"{field}: expected boolean, got {value!r}")


def parse_timestamp(value: str, *, field: str, optional: bool = False) -> datetime | None:
    raw = value.strip()
    if not raw and optional:
        return None
    if not raw:
        raise DataValidationError(f"{field}: timestamp is required")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataValidationError(f"{field}: invalid ISO-8601 timestamp {raw!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DataValidationError(f"{field}: timezone offset is required")
    return parsed


def _require_columns(fieldnames: Sequence[str] | None, required: set[str], path: Path) -> None:
    actual = set(fieldnames or [])
    missing = sorted(required - actual)
    if missing:
        raise DataValidationError(f"{path}: missing columns: {', '.join(missing)}")


def load_candidates(path: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, REQUIRED_EVENT_COLUMNS, path)
        for line_number, row in enumerate(reader, start=2):
            prefix = f"{path}:{line_number}"
            candidate_id = row["candidate_id"].strip()
            if not candidate_id:
                raise DataValidationError(f"{prefix}: candidate_id is required")
            if candidate_id in seen:
                raise DataValidationError(f"{prefix}: duplicate candidate_id {candidate_id!r}")
            seen.add(candidate_id)

            flow_observed = parse_bool(row["flow_observed"], field=f"{prefix}:flow_observed")
            heat_observed = parse_bool(row["heat_observed"], field=f"{prefix}:heat_observed")
            flow_source = row["flow_source"].strip()
            heat_source = row["heat_source"].strip()
            if flow_observed and not flow_source:
                raise DataValidationError(f"{prefix}: observed flow requires flow_source")
            if heat_observed and not heat_source:
                raise DataValidationError(f"{prefix}: observed heat trigger requires heat_source")

            flow_time = parse_timestamp(row["flow_time_et"], field=f"{prefix}:flow_time_et")
            heat_time = parse_timestamp(
                row["heat_time_et"], field=f"{prefix}:heat_time_et", optional=True
            )
            evaluation_end = parse_timestamp(
                row["evaluation_end_et"], field=f"{prefix}:evaluation_end_et"
            )
            assert flow_time is not None and evaluation_end is not None

            candidates.append(
                Candidate(
                    candidate_id=candidate_id,
                    ticker=row["ticker"].strip().upper(),
                    contract=row["contract"].strip().upper(),
                    direction=row["direction"].strip().upper(),
                    flow_time=flow_time,
                    heat_time=heat_time,
                    evaluation_end=evaluation_end,
                    flow_observed=flow_observed,
                    heat_observed=heat_observed,
                    heat_event=row["heat_event"].strip().upper(),
                    breadth_confirmed=parse_bool(
                        row["breadth_confirmed"], field=f"{prefix}:breadth_confirmed"
                    ),
                    flow_source=flow_source,
                    heat_source=heat_source,
                    node_level=row.get("node_level", "").strip(),
                    net_gex=row.get("net_gex", "").strip(),
                    net_vex=row.get("net_vex", "").strip(),
                )
            )
    return candidates


def load_quotes(path: Path) -> dict[str, list[Quote]]:
    quotes: dict[str, list[Quote]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, REQUIRED_QUOTE_COLUMNS, path)
        for line_number, row in enumerate(reader, start=2):
            prefix = f"{path}:{line_number}"
            candidate_id = row["candidate_id"].strip()
            timestamp = parse_timestamp(row["timestamp_et"], field=f"{prefix}:timestamp_et")
            assert timestamp is not None
            try:
                bid = float(row["bid"])
                ask = float(row["ask"])
            except ValueError as exc:
                raise DataValidationError(f"{prefix}: bid/ask must be numeric") from exc
            if not math.isfinite(bid) or not math.isfinite(ask) or bid < 0 or ask <= 0:
                raise DataValidationError(f"{prefix}: invalid bid/ask {bid}/{ask}")
            if ask < bid:
                raise DataValidationError(f"{prefix}: crossed quote {bid}/{ask}")
            quotes.setdefault(candidate_id, []).append(
                Quote(candidate_id=candidate_id, timestamp=timestamp, bid=bid, ask=ask)
            )
    for candidate_quotes in quotes.values():
        candidate_quotes.sort(key=lambda quote: quote.timestamp)
    return quotes


def compute_path_metrics(
    quotes: Sequence[Quote], *, entry_time: datetime, evaluation_end: datetime
) -> PathMetrics | None:
    path = [quote for quote in quotes if entry_time <= quote.timestamp <= evaluation_end]
    if not path:
        return None
    entry = path[0]
    entry_ask = entry.ask
    bid_returns = [(quote.bid / entry_ask - 1.0) * 100.0 for quote in path]
    end = path[-1]
    return PathMetrics(
        entry_time=entry.timestamp.isoformat(),
        entry_ask=entry_ask,
        end_time=end.timestamp.isoformat(),
        end_bid=end.bid,
        mae_pct=min(bid_returns),
        mfe_pct=max(bid_returns),
        end_return_pct=bid_returns[-1],
    )


def analyze_candidate(
    candidate: Candidate, quotes: Sequence[Quote], config: GateConfig
) -> AnalysisRow:
    common = dict(
        candidate_id=candidate.candidate_id,
        ticker=candidate.ticker,
        contract=candidate.contract,
        direction=candidate.direction,
        session_date=candidate.flow_time.date().isoformat(),
        heat_event=candidate.heat_event,
        breadth_confirmed=candidate.breadth_confirmed,
        node_level=candidate.node_level,
        net_gex_observed=candidate.net_gex,
        net_vex_observed=candidate.net_vex,
    )

    if not candidate.flow_observed:
        return AnalysisRow(**common, lifecycle="BLOCKED", reason="flow_not_observed")
    if candidate.evaluation_end <= candidate.flow_time:
        return AnalysisRow(**common, lifecycle="BLOCKED", reason="invalid_evaluation_window")

    flow_metrics = compute_path_metrics(
        quotes, entry_time=candidate.flow_time, evaluation_end=candidate.evaluation_end
    )
    if flow_metrics is None:
        return AnalysisRow(**common, lifecycle="BLOCKED", reason="missing_flow_entry_quote")

    flow_values = dict(
        flow_entry_time=flow_metrics.entry_time,
        flow_entry_ask=flow_metrics.entry_ask,
        flow_mae_pct=flow_metrics.mae_pct,
        flow_mfe_pct=flow_metrics.mfe_pct,
        flow_end_return_pct=flow_metrics.end_return_pct,
    )

    if not candidate.heat_observed or candidate.heat_time is None:
        return AnalysisRow(
            **common, **flow_values, lifecycle="WATCHING", reason="heat_trigger_not_observed"
        )
    if candidate.heat_time < candidate.flow_time:
        return AnalysisRow(
            **common, **flow_values, lifecycle="BLOCKED", reason="heat_precedes_flow"
        )
    if candidate.heat_time > candidate.evaluation_end:
        return AnalysisRow(
            **common, **flow_values, lifecycle="WATCHING", reason="heat_after_evaluation_end"
        )
    if candidate.heat_event not in config.allowed_heat_events:
        return AnalysisRow(
            **common, **flow_values, lifecycle="WATCHING", reason="heat_event_not_allowed"
        )
    if config.require_breadth and not candidate.breadth_confirmed:
        return AnalysisRow(
            **common, **flow_values, lifecycle="WATCHING", reason="breadth_not_confirmed"
        )

    gated_metrics = compute_path_metrics(
        quotes, entry_time=candidate.heat_time, evaluation_end=candidate.evaluation_end
    )
    if gated_metrics is None:
        return AnalysisRow(
            **common, **flow_values, lifecycle="BLOCKED", reason="missing_gated_entry_quote"
        )

    retention = None
    if flow_metrics.mfe_pct > 0:
        retention = gated_metrics.mfe_pct / flow_metrics.mfe_pct

    return AnalysisRow(
        **common,
        **flow_values,
        lifecycle="TRIGGERED",
        reason="gate_passed",
        gated_entry_time=gated_metrics.entry_time,
        gated_entry_ask=gated_metrics.entry_ask,
        gated_mae_pct=gated_metrics.mae_pct,
        gated_mfe_pct=gated_metrics.mfe_pct,
        gated_end_return_pct=gated_metrics.end_return_pct,
        mae_improvement_pp=gated_metrics.mae_pct - flow_metrics.mae_pct,
        mfe_retention_ratio=retention,
        end_return_lift_pp=gated_metrics.end_return_pct - flow_metrics.end_return_pct,
    )


def analyze(
    candidates: Iterable[Candidate], quotes_by_candidate: dict[str, list[Quote]], config: GateConfig
) -> list[AnalysisRow]:
    return [
        analyze_candidate(candidate, quotes_by_candidate.get(candidate.candidate_id, []), config)
        for candidate in candidates
    ]


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile requires observations")
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def cluster_bootstrap_mean_ci(
    rows: Sequence[AnalysisRow], *, samples: int = 10_000, seed: int = 20_260_901
) -> tuple[float, float] | None:
    by_session: dict[str, list[float]] = {}
    for row in rows:
        if row.lifecycle == "TRIGGERED" and row.mae_improvement_pp is not None:
            by_session.setdefault(row.session_date, []).append(row.mae_improvement_pp)
    session_means = [fmean(values) for values in by_session.values()]
    if len(session_means) < 2 or samples <= 0:
        return None

    rng = random.Random(seed)
    bootstrap_means = [
        fmean(rng.choice(session_means) for _ in session_means) for _ in range(samples)
    ]
    return _percentile(bootstrap_means, 0.025), _percentile(bootstrap_means, 0.975)


def summarize(rows: Sequence[AnalysisRow], *, bootstrap_samples: int = 10_000) -> dict[str, object]:
    states = {"TRIGGERED", "WATCHING", "BLOCKED"}
    counts = {state: sum(row.lifecycle == state for row in rows) for state in states}
    triggered = [row for row in rows if row.lifecycle == "TRIGGERED"]

    def mean_of(field: str) -> float | None:
        values = [getattr(row, field) for row in triggered]
        numeric = [float(value) for value in values if value is not None]
        return fmean(numeric) if numeric else None

    ci = cluster_bootstrap_mean_ci(triggered, samples=bootstrap_samples)
    return {
        "n_candidates": len(rows),
        "n_sessions": len({row.session_date for row in rows}),
        "n_triggered": counts["TRIGGERED"],
        "n_watching": counts["WATCHING"],
        "n_blocked": counts["BLOCKED"],
        "mean_flow_mae_pct": mean_of("flow_mae_pct"),
        "mean_gated_mae_pct": mean_of("gated_mae_pct"),
        "mean_mae_improvement_pp": mean_of("mae_improvement_pp"),
        "mean_flow_mfe_pct": mean_of("flow_mfe_pct"),
        "mean_gated_mfe_pct": mean_of("gated_mfe_pct"),
        "mean_mfe_retention_ratio": mean_of("mfe_retention_ratio"),
        "mean_end_return_lift_pp": mean_of("end_return_lift_pp"),
        "mae_improvement_cluster_bootstrap_95ci": list(ci) if ci else None,
        "bootstrap_samples": bootstrap_samples,
        "note": "Mechanical observed-quote comparison; not economic validation.",
    }


def write_rows(path: Path, rows: Sequence[AnalysisRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(AnalysisRow.__dataclass_fields__)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare immediate flow entries with observed Heatseeker-timed entries."
    )
    parser.add_argument("--events", type=Path, required=True, help="candidate/event CSV")
    parser.add_argument("--quotes", type=Path, required=True, help="observed option NBBO CSV")
    parser.add_argument("--out", type=Path, required=True, help="per-candidate result CSV")
    parser.add_argument("--summary", type=Path, required=True, help="aggregate summary JSON")
    parser.add_argument(
        "--allowed-event",
        action="append",
        default=None,
        help="accepted observed Heat event; repeatable (default: NODE_FLIP)",
    )
    parser.add_argument(
        "--require-breadth",
        action="store_true",
        help="keep candidates in WATCHING unless breadth_confirmed=true",
    )
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    events = frozenset(event.strip().upper() for event in (args.allowed_event or ["NODE_FLIP"]))
    if not events:
        raise SystemExit("At least one allowed Heat event is required")
    if args.bootstrap_samples < 0:
        raise SystemExit("--bootstrap-samples must be non-negative")

    candidates = load_candidates(args.events)
    quotes = load_quotes(args.quotes)
    rows = analyze(
        candidates,
        quotes,
        GateConfig(allowed_heat_events=events, require_breadth=args.require_breadth),
    )
    summary = summarize(rows, bootstrap_samples=args.bootstrap_samples)
    write_rows(args.out, rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
