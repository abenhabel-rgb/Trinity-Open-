"""Build the canonical observed-only Heatseeker image manifest.

The ingest ledger is append-only and may contain repeated transfers.  This
module collapses those records by SHA-256, explicitly excludes known synthetic
health-check images, and extracts only metadata that can be read from filenames
without guessing a timezone or ticker.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


KNOWN_TEST_FILENAMES = {"test_heatseeker.png"}

_SCREENSHOT_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})[_ ]at[_ ](?P<hour>\d{1,2})[._](?P<minute>\d{2})[._](?P<second>\d{2})[_ ](?P<ampm>AM|PM)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ManifestRow:
    sha256: str
    original_filename: str
    archived_path: str
    bytes: int
    first_received_at_utc: str
    filename_timestamp_naive: str
    filename_timestamp_source: str
    timezone_status: str
    data_policy: str
    state: str


def _filename_timestamp(filename: str) -> tuple[str, str]:
    match = _SCREENSHOT_RE.search(filename)
    if not match:
        return "", ""

    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    second = int(match.group("second"))
    ampm = match.group("ampm").upper()
    if hour < 1 or hour > 12 or minute > 59 or second > 59:
        return "", ""
    if ampm == "AM":
        hour = 0 if hour == 12 else hour
    else:
        hour = 12 if hour == 12 else hour + 12

    value = datetime.fromisoformat(match.group("date")).replace(
        hour=hour,
        minute=minute,
        second=second,
    )
    return value.isoformat(), "filename"


def _load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on ledger line {line_number}") from exc
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def build_manifest(ledger_path: Path) -> tuple[list[ManifestRow], list[dict[str, Any]], dict[str, int]]:
    ledger_rows = _load_ledger(ledger_path)
    by_sha: dict[str, dict[str, Any]] = {}
    duplicate_records = 0

    for row in ledger_rows:
        sha = str(row.get("sha256", "")).strip()
        if not sha:
            continue
        if sha in by_sha:
            duplicate_records += 1
            continue
        by_sha[sha] = row

    manifest: list[ManifestRow] = []
    exclusions: list[dict[str, Any]] = []

    for sha, row in by_sha.items():
        filename = str(row.get("original_filename", "")).strip()
        basename = Path(filename).name
        if basename in KNOWN_TEST_FILENAMES:
            exclusions.append(
                {
                    "sha256": sha,
                    "original_filename": filename,
                    "reason": "synthetic_healthcheck_image",
                    "archived_path": str(row.get("archived_path", "")),
                }
            )
            continue

        filename_ts, ts_source = _filename_timestamp(filename)
        manifest.append(
            ManifestRow(
                sha256=sha,
                original_filename=filename,
                archived_path=str(row.get("archived_path", "")),
                bytes=int(row.get("bytes", 0) or 0),
                first_received_at_utc=str(row.get("received_at_utc", "")),
                filename_timestamp_naive=filename_ts,
                filename_timestamp_source=ts_source,
                timezone_status="unresolved" if filename_ts else "not_present",
                data_policy="observed_only",
                state="canonical_raw_observed",
            )
        )

    manifest.sort(key=lambda x: (x.filename_timestamp_naive or "9999", x.original_filename, x.sha256))
    exclusions.sort(key=lambda x: (x["original_filename"], x["sha256"]))

    stats = {
        "ledger_records": len(ledger_rows),
        "unique_sha": len(by_sha),
        "duplicate_records": duplicate_records,
        "canonical_research_images": len(manifest),
        "excluded_images": len(exclusions),
        "filename_timestamps_parsed": sum(bool(row.filename_timestamp_naive) for row in manifest),
    }
    return manifest, exclusions, stats


def write_outputs(
    manifest: list[ManifestRow],
    exclusions: list[dict[str, Any]],
    stats: dict[str, int],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = output_dir / "heatseeker_manifest.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in manifest:
            handle.write(json.dumps(asdict(row), ensure_ascii=False, separators=(",", ":")) + "\n")

    csv_path = output_dir / "heatseeker_manifest.csv"
    fieldnames = list(ManifestRow.__dataclass_fields__)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in manifest:
            writer.writerow(asdict(row))

    exclusions_path = output_dir / "heatseeker_exclusions.jsonl"
    with exclusions_path.open("w", encoding="utf-8") as handle:
        for row in exclusions:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    (output_dir / "heatseeker_manifest_stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build canonical Heatseeker image manifest")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("/opt/openclaw/data/derived/heatseeker_ingest.jsonl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/opt/openclaw/data/derived"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, exclusions, stats = build_manifest(args.ledger)
    write_outputs(manifest, exclusions, stats, args.output_dir)
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
