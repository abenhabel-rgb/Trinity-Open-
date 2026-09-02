from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import time
from datetime import UTC, datetime
from pathlib import Path

from .heatseeker_collector import ingest_once

_STOP = False

DEFAULT_HEATSEEKER_INBOX = Path("/opt/openclaw/inbox/heatseeker")
DEFAULT_HEATSEEKER_ARCHIVE = Path("/opt/openclaw/data/raw/heatseeker")
DEFAULT_HEATSEEKER_LEDGER = Path("/opt/openclaw/data/derived/heatseeker_ingest.jsonl")


def _handle_stop(signum: int, frame: object) -> None:
    del signum, frame
    global _STOP
    _STOP = True


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_heartbeat(
    state_path: Path,
    sequence: int,
    *,
    heatseeker_ingested: int = 0,
    heatseeker_error: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "service": "openclaw-worker",
        "status": "alive",
        "timestamp_utc": _utc_now(),
        "sequence": sequence,
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "data_policy": "observed_only",
        "heatseeker": {
            "collector": "enabled",
            "ingested_this_cycle": heatseeker_ingested,
            "error": heatseeker_error,
        },
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(state_path)
    return payload


def run(
    interval_seconds: int,
    state_path: Path,
    once: bool = False,
    *,
    heatseeker_inbox: Path = DEFAULT_HEATSEEKER_INBOX,
    heatseeker_archive: Path = DEFAULT_HEATSEEKER_ARCHIVE,
    heatseeker_ledger: Path = DEFAULT_HEATSEEKER_LEDGER,
) -> int:
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    sequence = 0
    while not _STOP:
        sequence += 1
        heatseeker_count = 0
        heatseeker_error: str | None = None
        try:
            records = ingest_once(
                heatseeker_inbox,
                heatseeker_archive,
                heatseeker_ledger,
            )
            heatseeker_count = len(records)
        except Exception as exc:  # keep daemon alive; expose failure in heartbeat/journal
            heatseeker_error = f"{type(exc).__name__}: {exc}"

        payload = write_heartbeat(
            state_path,
            sequence,
            heatseeker_ingested=heatseeker_count,
            heatseeker_error=heatseeker_error,
        )
        print(json.dumps(payload, separators=(",", ":")), flush=True)
        if once:
            return 0
        for _ in range(interval_seconds):
            if _STOP:
                break
            time.sleep(1)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw persistent VPS worker")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Heartbeat/collector interval in seconds (default: 60)",
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        default=Path("/opt/openclaw/logs/worker_heartbeat.json"),
        help="Path of the atomic heartbeat JSON file",
    )
    parser.add_argument("--heatseeker-inbox", type=Path, default=DEFAULT_HEATSEEKER_INBOX)
    parser.add_argument("--heatseeker-archive", type=Path, default=DEFAULT_HEATSEEKER_ARCHIVE)
    parser.add_argument("--heatseeker-ledger", type=Path, default=DEFAULT_HEATSEEKER_LEDGER)
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one collector/heartbeat cycle and exit (health check mode)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.interval < 1:
        raise SystemExit("--interval must be >= 1")
    return run(
        args.interval,
        args.state_path,
        once=args.once,
        heatseeker_inbox=args.heatseeker_inbox,
        heatseeker_archive=args.heatseeker_archive,
        heatseeker_ledger=args.heatseeker_ledger,
    )


if __name__ == "__main__":
    raise SystemExit(main())
