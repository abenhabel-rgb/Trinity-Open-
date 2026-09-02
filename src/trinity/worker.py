from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import time
from datetime import UTC, datetime
from pathlib import Path

_STOP = False


def _handle_stop(signum: int, frame: object) -> None:
    del signum, frame
    global _STOP
    _STOP = True


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_heartbeat(state_path: Path, sequence: int) -> dict[str, object]:
    payload: dict[str, object] = {
        "service": "openclaw-worker",
        "status": "alive",
        "timestamp_utc": _utc_now(),
        "sequence": sequence,
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "data_policy": "observed_only",
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(state_path)
    return payload


def run(interval_seconds: int, state_path: Path, once: bool = False) -> int:
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    sequence = 0
    while not _STOP:
        sequence += 1
        payload = write_heartbeat(state_path, sequence)
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
        help="Heartbeat interval in seconds (default: 60)",
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        default=Path("/opt/openclaw/logs/worker_heartbeat.json"),
        help="Path of the atomic heartbeat JSON file",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Write one heartbeat and exit (health check mode)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.interval < 1:
        raise SystemExit("--interval must be >= 1")
    return run(args.interval, args.state_path, once=args.once)


if __name__ == "__main__":
    raise SystemExit(main())
