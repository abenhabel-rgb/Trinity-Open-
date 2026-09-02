"""Provider-agnostic market-volume normalizer for OpenClaw Volume Spike.

This module lets OpenClaw ingest observed option-volume data before any specific
vendor connector exists. Later, ThetaData or another source only needs to map
its fields into this normalized schema.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "ticker",
    "timestamp_et",
    "window_start_et",
    "window_end_et",
    "interval_volume",
    "baseline_interval_volumes",
    "source",
    "baseline_source",
}

OPTIONAL_FIELDS = {
    "expiration",
    "strike",
    "option_type",
    "cumulative_volume",
    "oi_j1",
    "premium",
    "spot",
    "node_type",
    "heatseeker_observed",
    "heatseeker_label",
}


class MarketVolumeNormalizationError(ValueError):
    pass


def _parse_baseline(value: Any) -> list[int]:
    if isinstance(value, list):
        return [int(x) for x in value]
    if value is None:
        raise MarketVolumeNormalizationError("baseline_interval_volumes is required")
    text = str(value).strip()
    if not text:
        raise MarketVolumeNormalizationError("baseline_interval_volumes cannot be empty")
    # Accept JSON list, comma-separated, or semicolon-separated values.
    if text.startswith("["):
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise MarketVolumeNormalizationError("baseline_interval_volumes JSON must be a list")
        return [int(x) for x in parsed]
    separator = ";" if ";" in text else ","
    return [int(part.strip()) for part in text.split(separator) if part.strip()]


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise MarketVolumeNormalizationError(f"missing required fields: {', '.join(sorted(missing))}")

    normalized: dict[str, Any] = {
        "ticker": str(record["ticker"]).strip().upper(),
        "timestamp_et": str(record["timestamp_et"]).strip(),
        "window_start_et": str(record["window_start_et"]).strip(),
        "window_end_et": str(record["window_end_et"]).strip(),
        "interval_volume": int(record["interval_volume"]),
        "baseline_interval_volumes": _parse_baseline(record["baseline_interval_volumes"]),
        "source": str(record["source"]).strip(),
        "baseline_source": str(record["baseline_source"]).strip(),
    }

    for field in OPTIONAL_FIELDS:
        if field in record and record[field] not in (None, ""):
            value: Any = record[field]
            if field in {"strike", "premium", "spot"}:
                value = float(value)
            elif field in {"cumulative_volume", "oi_j1"}:
                value = int(value)
            elif field == "heatseeker_observed":
                if isinstance(value, bool):
                    pass
                else:
                    lowered = str(value).strip().lower()
                    if lowered in {"true", "1", "yes"}:
                        value = True
                    elif lowered in {"false", "0", "no"}:
                        value = False
                    else:
                        raise MarketVolumeNormalizationError(
                            "heatseeker_observed must be true/false when supplied"
                        )
            normalized[field] = value

    return normalized


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return [normalize_record(payload)]
        if isinstance(payload, list):
            return [normalize_record(item) for item in payload]
        raise MarketVolumeNormalizationError("JSON must contain an object or list of objects")

    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [normalize_record(dict(row)) for row in csv.DictReader(handle)]

    raise MarketVolumeNormalizationError("supported input formats are .json and .csv")


def write_payloads(records: list[dict[str, Any]], output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for index, record in enumerate(records, start=1):
        ticker = record["ticker"] or "UNKNOWN"
        timestamp = str(record["timestamp_et"]).replace(":", "-")
        destination = output_dir / f"{ticker}_{timestamp}_{index:04d}.json"
        destination.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        count += 1
    return count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize market-volume data for OpenClaw")
    parser.add_argument("input", type=Path, help="CSV or JSON observed market-volume file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/opt/openclaw/inbox/volume_spike"),
        help="Directory where normalized Volume Spike JSON payloads are written",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    records = load_records(args.input)
    count = write_payloads(records, args.output_dir)
    print(json.dumps({"normalized": count, "output_dir": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
