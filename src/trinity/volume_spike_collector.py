from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .volume_spike import VolumeSpikeObservation, analyze_volume_spike


def _utc_now() -> datetime:
    return datetime.now(UTC)


def process_volume_spike_inbox(
    inbox: Path,
    archive_root: Path,
    rejected_root: Path,
    result_ledger: Path,
) -> tuple[int, int]:
    """Process all JSON Volume Spike payloads once.

    Returns ``(processed, rejected)``. Input files are moved out of the inbox after
    each attempt so a bad payload cannot poison the persistent worker loop.
    """

    inbox.mkdir(parents=True, exist_ok=True)
    archive_root.mkdir(parents=True, exist_ok=True)
    rejected_root.mkdir(parents=True, exist_ok=True)
    result_ledger.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    rejected = 0

    for source in sorted(inbox.glob("*.json")):
        received_at = _utc_now()
        date_key = received_at.strftime("%Y-%m-%d")
        success_dir = archive_root / date_key
        reject_dir = rejected_root / date_key
        success_dir.mkdir(parents=True, exist_ok=True)
        reject_dir.mkdir(parents=True, exist_ok=True)

        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("top-level JSON payload must be an object")
            observation = VolumeSpikeObservation.from_dict(payload)
            result = analyze_volume_spike(observation)
            record = {
                "dataset": "volume_spike_result",
                "data_policy": "observed_only",
                "processed_at_utc": received_at.isoformat(),
                "input_filename": source.name,
                **asdict(result),
            }
            with result_ledger.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            destination = success_dir / source.name
            counter = 1
            while destination.exists():
                destination = success_dir / f"{source.stem}_{counter}{source.suffix}"
                counter += 1
            shutil.move(str(source), str(destination))
            processed += 1
        except Exception as exc:
            destination = reject_dir / source.name
            counter = 1
            while destination.exists():
                destination = reject_dir / f"{source.stem}_{counter}{source.suffix}"
                counter += 1
            shutil.move(str(source), str(destination))
            error_record = {
                "dataset": "volume_spike_rejected",
                "data_policy": "observed_only",
                "processed_at_utc": received_at.isoformat(),
                "input_filename": source.name,
                "error": f"{type(exc).__name__}: {exc}",
                "archived_path": str(destination),
            }
            with result_ledger.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(error_record, ensure_ascii=False, separators=(",", ":")) + "\n"
                )
            rejected += 1

    return processed, rejected
