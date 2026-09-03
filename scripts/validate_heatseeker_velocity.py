#!/usr/bin/env python3
"""
Heatseeker velocity formula validator.

Purpose
-------
Validate, from observed frontend payloads only, how reported velocity fields such as
``delta1Min`` and ``percent1Min`` relate to the historical value of the same node.

The script never claims to reproduce a private backend. It:
1. ingests timestamped snapshots / ``velocity_update`` events;
2. indexes each cell by (Greek, strike, expiration);
3. reconstructs candidate historical references for each reported horizon;
4. tests several percentage formulas and reference-selection policies;
5. reconstructs the implicit denominator reported_percent = 100 * delta / denominator;
6. labels zero, null, sign-change and new-node cases;
7. writes row-level evidence plus an aggregate ranking.

Input
-----
JSONL is recommended. Each line may be either a single normalized cell, a snapshot
containing ``cells`` / ``nodes`` / ``rows`` / ``data``, or an event carrying one of those
containers. Common field aliases are accepted.

Minimal row:
{
  "type": "velocity_update",
  "timestamp": "2026-09-03T14:31:00-04:00",
  "greek": "GEX",
  "strike": 100,
  "expiration": "2026-09-04",
  "value": 1200,
  "delta1Min": 200,
  "percent1Min": 20
}

Usage
-----
python scripts/validate_heatseeker_velocity.py analyze capture.jsonl --out-dir reports/velocity
python scripts/validate_heatseeker_velocity.py capture --output data/heatseeker_velocity_raw.jsonl

``capture`` reads JSON objects/arrays from stdin and appends a local receive timestamp.
It is deliberately transport-agnostic: pipe or paste frontend/network payloads into it.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import numpy as np
import pandas as pd


TIMESTAMP_KEYS = ("timestamp", "ts", "asOf", "as_of", "time", "eventTime", "event_time")
GREEK_KEYS = ("greek", "metric", "exposureType", "exposure_type")
EXPIRATION_KEYS = ("expiration", "expiry", "exp", "expirationDate", "expiration_date")
STRIKE_KEYS = ("strike", "strikePrice", "strike_price")
VALUE_KEYS = ("value", "currentValue", "current_value", "exposure", "amount")
CONTAINER_KEYS = ("cells", "nodes", "rows", "data", "payload", "values")

HORIZON_RE = re.compile(
    r"^(?P<kind>percent|delta)[_\-]?(?P<num>\d+)[_\-]?"
    r"(?P<unit>m|min|mins|minute|minutes|h|hr|hrs|hour|hours|d|day|days)$",
    re.IGNORECASE,
)
CAMEL_HORIZON_RE = re.compile(
    r"^(?P<kind>percent|delta)(?P<num>\d+)(?P<unit>Min|Mins|Minute|Minutes|"
    r"Hour|Hours|Hr|Hrs|Day|Days|M|H|D)$",
    re.IGNORECASE,
)

DEFAULT_ATOL = 1e-8
DEFAULT_RTOL = 1e-6


@dataclass(frozen=True, order=True)
class NodeKey:
    greek: str
    strike: float
    expiration: str


@dataclass
class CellRecord:
    timestamp: pd.Timestamp
    key: NodeKey
    value: float | None
    event_type: str | None
    reported_delta: dict[str, float | None]
    reported_percent: dict[str, float | None]
    raw: Mapping[str, Any]


def _first(mapping: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _parse_timestamp(value: Any) -> pd.Timestamp | None:
    if value is None or value == "":
        return None
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts


def _normalize_greek(value: Any, row: Mapping[str, Any]) -> str | None:
    if value is not None:
        text = str(value).strip().upper()
        if text:
            return text
    for candidate in ("gex", "vex", "dex", "charm", "gamma", "vanna"):
        if candidate in row and row[candidate] is not None:
            return candidate.upper()
    return None


def _extract_value(row: Mapping[str, Any], greek: str | None) -> float | None:
    value = _first(row, VALUE_KEYS)
    if value is not None:
        return _as_float(value)
    if greek:
        for key in (greek, greek.lower(), greek.upper()):
            if key in row:
                return _as_float(row[key])
    return None


def _unit_to_seconds(number: int, unit: str) -> int:
    unit = unit.lower()
    if unit in {"m", "min", "mins", "minute", "minutes"}:
        return number * 60
    if unit in {"h", "hr", "hrs", "hour", "hours"}:
        return number * 3600
    if unit in {"d", "day", "days"}:
        return number * 86400
    raise ValueError(f"Unsupported horizon unit: {unit}")


def _canonical_horizon(number: int, unit: str) -> str:
    seconds = _unit_to_seconds(number, unit)
    if seconds % 86400 == 0:
        return f"{seconds // 86400}d"
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    return f"{seconds // 60}m"


def horizon_seconds(horizon: str) -> int:
    match = re.fullmatch(r"(\d+)([mhd])", horizon)
    if not match:
        raise ValueError(f"Invalid canonical horizon: {horizon}")
    number = int(match.group(1))
    unit = match.group(2)
    return number * {"m": 60, "h": 3600, "d": 86400}[unit]


def _extract_horizon_fields(
    row: Mapping[str, Any],
) -> tuple[dict[str, float | None], dict[str, float | None]]:
    deltas: dict[str, float | None] = {}
    percents: dict[str, float | None] = {}

    for key, value in row.items():
        text = str(key)
        match = HORIZON_RE.match(text) or CAMEL_HORIZON_RE.match(text)
        if not match:
            continue
        horizon = _canonical_horizon(int(match.group("num")), match.group("unit"))
        target = percents if match.group("kind").lower() == "percent" else deltas
        target[horizon] = _as_float(value)

    for kind, target in (("delta", deltas), ("percent", percents)):
        nested = row.get(kind)
        if not isinstance(nested, Mapping):
            continue
        for key, value in nested.items():
            text = str(key).strip()
            match = re.fullmatch(r"(\d+)\s*(m|min|h|hr|d|day)s?", text, re.IGNORECASE)
            if not match:
                continue
            horizon = _canonical_horizon(int(match.group(1)), match.group(2))
            target[horizon] = _as_float(value)

    return deltas, percents


def _inherit_context(parent: Mapping[str, Any], child: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(child)
    for keys in (TIMESTAMP_KEYS, GREEK_KEYS, EXPIRATION_KEYS):
        value = _first(merged, keys)
        if value is None:
            inherited = _first(parent, keys)
            if inherited is not None:
                merged[keys[0]] = inherited
    if "type" not in merged and parent.get("type") is not None:
        merged["type"] = parent.get("type")
    if "event" not in merged and parent.get("event") is not None:
        merged["event"] = parent.get("event")
    return merged


def iter_candidate_rows(
    payload: Any, parent: Mapping[str, Any] | None = None
) -> Iterator[Mapping[str, Any]]:
    if isinstance(payload, list):
        for item in payload:
            yield from iter_candidate_rows(item, parent)
        return
    if not isinstance(payload, Mapping):
        return

    row = _inherit_context(parent or {}, payload)
    has_strike = _first(row, STRIKE_KEYS) is not None
    has_velocity = any(
        HORIZON_RE.match(str(k)) or CAMEL_HORIZON_RE.match(str(k)) for k in row.keys()
    )
    has_value = _first(row, VALUE_KEYS) is not None or any(
        key in row for key in ("gex", "vex", "dex", "gamma", "vanna", "charm")
    )
    if has_strike and (has_value or has_velocity):
        yield row

    for key in CONTAINER_KEYS:
        child = payload.get(key)
        if isinstance(child, (list, Mapping)):
            yield from iter_candidate_rows(child, row)


def normalize_payload(payload: Any) -> list[CellRecord]:
    records: list[CellRecord] = []
    for row in iter_candidate_rows(payload):
        timestamp = _parse_timestamp(_first(row, TIMESTAMP_KEYS))
        greek = _normalize_greek(_first(row, GREEK_KEYS), row)
        strike = _as_float(_first(row, STRIKE_KEYS))
        expiration = _first(row, EXPIRATION_KEYS)
        if timestamp is None or greek is None or strike is None or expiration is None:
            continue

        deltas, percents = _extract_horizon_fields(row)
        value = _extract_value(row, greek)
        event_type = row.get("type") or row.get("event") or row.get("event_type")
        records.append(
            CellRecord(
                timestamp=timestamp,
                key=NodeKey(greek=greek, strike=strike, expiration=str(expiration)),
                value=value,
                event_type=str(event_type) if event_type is not None else None,
                reported_delta=deltas,
                reported_percent=percents,
                raw=row,
            )
        )
    return records


def load_jsonl(path: Path) -> list[CellRecord]:
    records: list[CellRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if isinstance(payload, Mapping) and "payload" in payload and "received_at" in payload:
                payload = payload["payload"]
            records.extend(normalize_payload(payload))
    return records


def load_json(path: Path) -> list[CellRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, Mapping) and "payload" in payload and "received_at" in payload:
        payload = payload["payload"]
    return normalize_payload(payload)


def load_csv(path: Path) -> list[CellRecord]:
    records: list[CellRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            records.extend(normalize_payload(row))
    return records


def load_records(path: Path) -> list[CellRecord]:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return load_jsonl(path)
    if suffix == ".json":
        return load_json(path)
    if suffix == ".csv":
        return load_csv(path)
    raise ValueError(f"Unsupported input type: {suffix}; use .jsonl/.ndjson/.json/.csv")


def _history_by_key(records: Sequence[CellRecord]) -> dict[NodeKey, list[CellRecord]]:
    history: dict[NodeKey, list[CellRecord]] = {}
    for record in records:
        history.setdefault(record.key, []).append(record)
    for bucket in history.values():
        bucket.sort(key=lambda r: r.timestamp)
    return history


def _reference(
    bucket: Sequence[CellRecord],
    current: CellRecord,
    horizon: str,
    policy: str,
    max_timing_error_seconds: int | None,
) -> tuple[CellRecord | None, float | None]:
    target = current.timestamp - pd.Timedelta(seconds=horizon_seconds(horizon))
    candidates = [row for row in bucket if row.timestamp < current.timestamp and row.value is not None]
    if not candidates:
        return None, None

    if policy == "at_or_before":
        eligible = [row for row in candidates if row.timestamp <= target]
        if not eligible:
            return None, None
        ref = max(eligible, key=lambda row: row.timestamp)
    elif policy == "nearest":
        ref = min(candidates, key=lambda row: abs((row.timestamp - target).total_seconds()))
    elif policy == "at_or_after":
        eligible = [row for row in candidates if row.timestamp >= target]
        if not eligible:
            return None, None
        ref = min(eligible, key=lambda row: row.timestamp)
    else:
        raise ValueError(f"Unknown reference policy: {policy}")

    error = abs((ref.timestamp - target).total_seconds())
    if max_timing_error_seconds is not None and error > max_timing_error_seconds:
        return None, error
    return ref, error


def _safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0 or not math.isfinite(denominator):
        return None
    out = numerator / denominator
    return out if math.isfinite(out) else None


def percentage_candidates(current: float, reference: float) -> dict[str, float | None]:
    delta = current - reference
    abs_reference = abs(reference)
    abs_current = abs(current)
    return {
        "delta_over_prev_signed": 100.0 * _safe_div(delta, reference) if reference != 0 else None,
        "delta_over_prev_abs": (
            100.0 * _safe_div(delta, abs_reference) if abs_reference != 0 else None
        ),
        "abs_change_over_prev_abs": (
            100.0 * _safe_div(abs_current - abs_reference, abs_reference)
            if abs_reference != 0
            else None
        ),
        "delta_over_current_signed": 100.0 * _safe_div(delta, current) if current != 0 else None,
        "delta_over_current_abs": (
            100.0 * _safe_div(delta, abs_current) if abs_current != 0 else None
        ),
    }


def _is_close(
    observed: float | None, predicted: float | None, atol: float, rtol: float
) -> bool | None:
    if observed is None or predicted is None:
        return None
    return bool(math.isclose(observed, predicted, abs_tol=atol, rel_tol=rtol))


def classify_case(current: float | None, reference: float | None, has_history: bool) -> str:
    if current is None:
        return "current_null"
    if reference is None:
        return "new_node_or_no_reference" if not has_history else "no_reference_for_horizon"
    if reference == 0:
        if current == 0:
            return "zero_to_zero"
        return "zero_reference"
    if current == 0:
        return "current_zero"
    if math.copysign(1.0, current) != math.copysign(1.0, reference):
        return "sign_flip"
    return "regular"


def analyze(
    records: Sequence[CellRecord],
    policies: Sequence[str],
    max_timing_error_seconds: int | None,
    atol: float,
    rtol: float,
) -> pd.DataFrame:
    history = _history_by_key(records)
    rows: list[dict[str, Any]] = []

    for current in sorted(records, key=lambda r: (r.timestamp, r.key)):
        horizons = sorted(
            set(current.reported_delta) | set(current.reported_percent), key=horizon_seconds
        )
        if not horizons:
            continue

        bucket = history[current.key]
        earlier = [r for r in bucket if r.timestamp < current.timestamp and r.value is not None]
        has_history = bool(earlier)

        for horizon in horizons:
            observed_delta = current.reported_delta.get(horizon)
            observed_percent = current.reported_percent.get(horizon)

            for policy in policies:
                ref, timing_error = _reference(
                    bucket, current, horizon, policy, max_timing_error_seconds
                )
                ref_value = ref.value if ref is not None else None
                case = classify_case(current.value, ref_value, has_history)

                base: dict[str, Any] = {
                    "timestamp": current.timestamp.isoformat(),
                    "event_type": current.event_type,
                    "greek": current.key.greek,
                    "strike": current.key.strike,
                    "expiration": current.key.expiration,
                    "horizon": horizon,
                    "reference_policy": policy,
                    "reference_timestamp": ref.timestamp.isoformat() if ref else None,
                    "reference_timing_error_seconds": timing_error,
                    "current_value": current.value,
                    "reference_value": ref_value,
                    "reported_delta": observed_delta,
                    "reported_percent": observed_percent,
                    "case": case,
                }

                predicted_delta = None
                implicit_denominator = None
                if current.value is not None and ref_value is not None:
                    predicted_delta = current.value - ref_value
                if observed_delta is not None and observed_percent not in (None, 0):
                    implicit_denominator = 100.0 * observed_delta / observed_percent

                base["predicted_delta_current_minus_reference"] = predicted_delta
                base["delta_exact"] = _is_close(observed_delta, predicted_delta, atol, rtol)
                base["delta_error"] = (
                    observed_delta - predicted_delta
                    if observed_delta is not None and predicted_delta is not None
                    else None
                )
                base["implicit_denominator"] = implicit_denominator
                base["implicit_denominator_vs_reference"] = (
                    implicit_denominator - ref_value
                    if implicit_denominator is not None and ref_value is not None
                    else None
                )
                base["implicit_denominator_vs_abs_reference"] = (
                    implicit_denominator - abs(ref_value)
                    if implicit_denominator is not None and ref_value is not None
                    else None
                )

                candidates: dict[str, float | None] = {}
                if current.value is not None and ref_value is not None:
                    candidates = percentage_candidates(current.value, ref_value)

                for name in (
                    "delta_over_prev_signed",
                    "delta_over_prev_abs",
                    "abs_change_over_prev_abs",
                    "delta_over_current_signed",
                    "delta_over_current_abs",
                ):
                    predicted = candidates.get(name)
                    base[f"predicted_percent__{name}"] = predicted
                    base[f"percent_exact__{name}"] = _is_close(
                        observed_percent, predicted, atol, rtol
                    )
                    base[f"percent_error__{name}"] = (
                        observed_percent - predicted
                        if observed_percent is not None and predicted is not None
                        else None
                    )

                if observed_percent == 0 and observed_delta not in (None, 0):
                    base["edge_note"] = "reported_percent_zero_with_nonzero_delta"
                elif observed_percent is None:
                    base["edge_note"] = "reported_percent_null"
                elif observed_delta is None:
                    base["edge_note"] = "reported_delta_null"
                else:
                    base["edge_note"] = None
                rows.append(base)

    return pd.DataFrame(rows)


def summarize(evidence: pd.DataFrame) -> pd.DataFrame:
    if evidence.empty:
        return pd.DataFrame()

    out: list[dict[str, Any]] = []
    formula_names = [
        "delta_over_prev_signed",
        "delta_over_prev_abs",
        "abs_change_over_prev_abs",
        "delta_over_current_signed",
        "delta_over_current_abs",
    ]

    for (horizon, policy), group in evidence.groupby(
        ["horizon", "reference_policy"], dropna=False
    ):
        delta_valid = group["delta_exact"].dropna()
        delta_errors = pd.to_numeric(group["delta_error"], errors="coerce").dropna()
        out.append(
            {
                "horizon": horizon,
                "reference_policy": policy,
                "target": "delta",
                "formula": "current_minus_reference",
                "n": int(len(delta_valid)),
                "exact_n": int(delta_valid.astype(bool).sum()) if len(delta_valid) else 0,
                "exact_rate": float(delta_valid.astype(bool).mean()) if len(delta_valid) else np.nan,
                "mae": float(delta_errors.abs().mean()) if len(delta_errors) else np.nan,
                "rmse": (
                    float(np.sqrt(np.mean(np.square(delta_errors))))
                    if len(delta_errors)
                    else np.nan
                ),
                "max_abs_error": (
                    float(delta_errors.abs().max()) if len(delta_errors) else np.nan
                ),
                "median_reference_timing_error_seconds": float(
                    pd.to_numeric(group["reference_timing_error_seconds"], errors="coerce").median()
                ),
            }
        )

        for formula in formula_names:
            exact = group[f"percent_exact__{formula}"].dropna()
            errors = pd.to_numeric(group[f"percent_error__{formula}"], errors="coerce").dropna()
            out.append(
                {
                    "horizon": horizon,
                    "reference_policy": policy,
                    "target": "percent",
                    "formula": formula,
                    "n": int(len(exact)),
                    "exact_n": int(exact.astype(bool).sum()) if len(exact) else 0,
                    "exact_rate": float(exact.astype(bool).mean()) if len(exact) else np.nan,
                    "mae": float(errors.abs().mean()) if len(errors) else np.nan,
                    "rmse": (
                        float(np.sqrt(np.mean(np.square(errors)))) if len(errors) else np.nan
                    ),
                    "max_abs_error": float(errors.abs().max()) if len(errors) else np.nan,
                    "median_reference_timing_error_seconds": float(
                        pd.to_numeric(
                            group["reference_timing_error_seconds"], errors="coerce"
                        ).median()
                    ),
                }
            )

    summary = pd.DataFrame(out)
    return summary.sort_values(
        ["target", "horizon", "exact_rate", "mae"],
        ascending=[True, True, False, True],
        na_position="last",
    ).reset_index(drop=True)


def edge_summary(evidence: pd.DataFrame) -> pd.DataFrame:
    if evidence.empty:
        return pd.DataFrame(columns=["case", "edge_note", "n"])
    return (
        evidence.groupby(["case", "edge_note"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .reset_index(drop=True)
    )


def denominator_summary(evidence: pd.DataFrame, atol: float, rtol: float) -> pd.DataFrame:
    if evidence.empty:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for (horizon, policy), group in evidence.groupby(
        ["horizon", "reference_policy"], dropna=False
    ):
        usable = group.dropna(subset=["implicit_denominator", "reference_value"]).copy()
        if usable.empty:
            continue

        denom = pd.to_numeric(usable["implicit_denominator"], errors="coerce")
        ref = pd.to_numeric(usable["reference_value"], errors="coerce")
        abs_ref = ref.abs()

        matches_signed = [
            math.isclose(float(d), float(r), abs_tol=atol, rel_tol=rtol)
            for d, r in zip(denom, ref, strict=False)
            if math.isfinite(float(d)) and math.isfinite(float(r))
        ]
        matches_abs = [
            math.isclose(float(d), float(r), abs_tol=atol, rel_tol=rtol)
            for d, r in zip(denom, abs_ref, strict=False)
            if math.isfinite(float(d)) and math.isfinite(float(r))
        ]

        rows.append(
            {
                "horizon": horizon,
                "reference_policy": policy,
                "n": int(len(usable)),
                "implicit_denominator_matches_signed_reference_rate": (
                    float(np.mean(matches_signed)) if matches_signed else np.nan
                ),
                "implicit_denominator_matches_abs_reference_rate": (
                    float(np.mean(matches_abs)) if matches_abs else np.nan
                ),
                "median_abs_error_vs_signed_reference": float((denom - ref).abs().median()),
                "median_abs_error_vs_abs_reference": float((denom - abs_ref).abs().median()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        [
            "implicit_denominator_matches_signed_reference_rate",
            "implicit_denominator_matches_abs_reference_rate",
        ],
        ascending=False,
        na_position="last",
    )


def write_report(
    out_dir: Path,
    records: Sequence[CellRecord],
    evidence: pd.DataFrame,
    summary: pd.DataFrame,
    denom: pd.DataFrame,
    edges: pd.DataFrame,
    input_path: Path,
    atol: float,
    rtol: float,
    max_timing_error_seconds: int | None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence.to_csv(out_dir / "velocity_evidence.csv", index=False)
    summary.to_csv(out_dir / "velocity_formula_ranking.csv", index=False)
    denom.to_csv(out_dir / "velocity_denominator_audit.csv", index=False)
    edges.to_csv(out_dir / "velocity_edge_cases.csv", index=False)

    percent = summary[summary["target"] == "percent"].copy() if not summary.empty else summary
    exact = (
        percent[(percent["n"] > 0) & np.isclose(percent["exact_rate"], 1.0)]
        if not percent.empty
        else percent
    )

    lines = [
        "# Heatseeker velocity validation report",
        "",
        "## Scope",
        "",
        f"- Input: `{input_path}`",
        f"- Normalized cell records: **{len(records)}**",
        f"- Row/policy/horizon comparisons: **{len(evidence)}**",
        f"- Absolute tolerance: `{atol}`",
        f"- Relative tolerance: `{rtol}`",
        f"- Maximum reference timing error: `{max_timing_error_seconds}` seconds",
        "",
        "This report validates only relationships reproducible from observed frontend payloads.",
        "It does **not** claim access to or proof of a private server-side implementation.",
        "",
        "## Exact reproductions",
        "",
    ]

    if exact.empty:
        lines.append(
            "No candidate percentage formula/reference-policy pair reproduced 100% of usable observations."
        )
    else:
        for row in exact.itertuples(index=False):
            lines.append(
                f"- `{row.horizon}` / `{row.reference_policy}` / `{row.formula}`: "
                f"{int(row.exact_n)}/{int(row.n)} exact."
            )

    lines.extend(
        [
            "",
            "## Interpretation rule",
            "",
            "- **Confirmed directly**: observed fields, horizons, timestamps, strikes, expirations and values.",
            "- **Reconstructed**: a formula/reference policy only when it reproduces observed values within the frozen tolerances.",
            "- **Not confirmed**: backend snapshot selection or edge-case handling unless the observed corpus distinguishes it.",
            "",
            "## Output files",
            "",
            "- `velocity_evidence.csv`: row-level references, candidates, errors and edge labels.",
            "- `velocity_formula_ranking.csv`: aggregate formula ranking.",
            "- `velocity_denominator_audit.csv`: implicit denominator versus signed/absolute historical value.",
            "- `velocity_edge_cases.csv`: zeros, sign flips, nulls and missing/new nodes.",
            "",
        ]
    )
    (out_dir / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def capture_stdin(output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("a", encoding="utf-8") as handle:
        for line_no, line in enumerate(sys.stdin, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"stdin:{line_no}: ignored invalid JSON: {exc}", file=sys.stderr)
                continue
            wrapped = {
                "received_at": datetime.now(timezone.utc).isoformat(),
                "payload": payload,
            }
            handle.write(json.dumps(wrapped, separators=(",", ":"), ensure_ascii=False) + "\n")
            handle.flush()
            count += 1
    return count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Heatseeker velocity formulas.")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser(
        "capture", help="Append JSON payloads from stdin to a timestamped JSONL capture."
    )
    capture.add_argument("--output", type=Path, required=True)

    analyze_cmd = sub.add_parser(
        "analyze", help="Analyze observed snapshot / velocity_update payloads."
    )
    analyze_cmd.add_argument("input", type=Path)
    analyze_cmd.add_argument(
        "--out-dir", type=Path, default=Path("reports/heatseeker_velocity")
    )
    analyze_cmd.add_argument(
        "--policies",
        nargs="+",
        choices=["at_or_before", "nearest", "at_or_after"],
        default=["at_or_before", "nearest", "at_or_after"],
    )
    analyze_cmd.add_argument(
        "--max-timing-error-seconds",
        type=int,
        default=15,
        help="Reject a historical reference farther from target horizon than this; -1 disables.",
    )
    analyze_cmd.add_argument("--atol", type=float, default=DEFAULT_ATOL)
    analyze_cmd.add_argument("--rtol", type=float, default=DEFAULT_RTOL)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "capture":
        count = capture_stdin(args.output)
        print(f"Captured {count} JSON payload(s) -> {args.output}")
        return 0

    max_error = None if args.max_timing_error_seconds < 0 else args.max_timing_error_seconds
    records = load_records(args.input)
    if not records:
        print("No normalized node records found in input.", file=sys.stderr)
        return 2

    evidence = analyze(
        records,
        policies=args.policies,
        max_timing_error_seconds=max_error,
        atol=args.atol,
        rtol=args.rtol,
    )
    summary = summarize(evidence)
    denom = denominator_summary(evidence, atol=args.atol, rtol=args.rtol)
    edges = edge_summary(evidence)

    write_report(
        out_dir=args.out_dir,
        records=records,
        evidence=evidence,
        summary=summary,
        denom=denom,
        edges=edges,
        input_path=args.input,
        atol=args.atol,
        rtol=args.rtol,
        max_timing_error_seconds=max_error,
    )

    print(f"Normalized records: {len(records)}")
    print(f"Evidence rows: {len(evidence)}")
    print(f"Report: {args.out_dir / 'REPORT.md'}")
    if not summary.empty:
        top = (
            summary[summary["target"] == "percent"]
            .sort_values(["exact_rate", "mae"], ascending=[False, True], na_position="last")
            .head(5)
        )
        if not top.empty:
            print("\nTop percentage candidates:")
            print(top.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
