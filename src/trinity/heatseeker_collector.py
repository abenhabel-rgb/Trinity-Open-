from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _seen_hashes(ledger_path: Path) -> set[str]:
    if not ledger_path.exists():
        return set()
    seen: set[str] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        value = payload.get("sha256")
        if isinstance(value, str):
            seen.add(value)
    return seen


def ingest_once(
    inbox: Path,
    archive_root: Path,
    ledger_path: Path,
) -> list[dict[str, object]]:
    inbox.mkdir(parents=True, exist_ok=True)
    archive_root.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    seen = _seen_hashes(ledger_path)
    records: list[dict[str, object]] = []

    for source in sorted(inbox.iterdir()):
        if not source.is_file() or source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        sha = _sha256(source)
        received_at = datetime.now(UTC)
        date_dir = archive_root / received_at.strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)

        duplicate = sha in seen
        prefix = "duplicate" if duplicate else "observed"
        destination = date_dir / f"{prefix}_{sha[:12]}_{source.name}"
        counter = 1
        while destination.exists():
            destination = date_dir / f"{prefix}_{sha[:12]}_{counter}_{source.name}"
            counter += 1

        shutil.move(str(source), str(destination))

        record: dict[str, object] = {
            "dataset": "heatseeker_raw_image",
            "data_policy": "observed_only",
            "state": "duplicate" if duplicate else "raw_observed_unparsed",
            "received_at_utc": received_at.isoformat(),
            "original_filename": source.name,
            "archived_path": str(destination),
            "sha256": sha,
            "bytes": destination.stat().st_size,
            "source": "openclaw_heatseeker_inbox",
            "parsed": False,
        }
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

        records.append(record)
        seen.add(sha)

    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest raw observed Heatseeker images")
    parser.add_argument(
        "--inbox",
        type=Path,
        default=Path("/opt/openclaw/inbox/heatseeker"),
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=Path("/opt/openclaw/data/raw/heatseeker"),
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("/opt/openclaw/data/derived/heatseeker_ingest.jsonl"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    records = ingest_once(args.inbox, args.archive_root, args.ledger)
    print(json.dumps({"ingested": len(records), "timestamp_utc": _utc_now()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
