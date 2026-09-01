#!/usr/bin/env python3
"""Capture observed Dashboard.gg Discord panels from Safari on macOS.

The collector is intentionally observational: it reads text already rendered in the
user's Safari session. It does not log in, call private APIs, or reconstruct missing
market data.

Outputs (gitignored under data/raw and data/derived):
- raw JSONL snapshots, preserving the observed panel text;
- a deduplicated normalized CSV with channel, displayed time, ticker and alert type.

Safari requirement: Develop > Allow JavaScript from Apple Events must be enabled.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_CHANNELS = ("uw-premium-bot", "volume-spike")
URL_FRAGMENT = "dashboard.gg/dashboard"
TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b")
TICKER_RE = re.compile(r"(?:^|\s|\$)([A-Z]{1,6})(?=\s|$|\b)")
ALERT_RE = re.compile(
    r"(Bright\s+(?:Yellow|Orange)\s*-\s*\d+|Net\s+Flow|contract[_ ]volume|"
    r"volume[- ]spike|options?\s+bot|holdings?\s+net\s+put\s*/\s*call\s+premium)",
    re.IGNORECASE,
)
EXCLUDED_TICKERS = {
    "APP", "BOT", "THE", "AND", "FOR", "WITH", "TODAY", "USED", "NET", "FLOW",
    "CALL", "PUT", "PREMIUM", "BRIGHT", "YELLOW", "ORANGE", "DISCORD",
}
CSV_FIELDS = [
    "event_id",
    "captured_at_utc",
    "captured_at_local",
    "source_url",
    "channel",
    "message_time_display",
    "ticker",
    "alert_type",
    "text",
]


@dataclass(frozen=True)
class SafariPage:
    url: str
    text: str


def _run_osascript(script: str) -> str:
    proc = subprocess.run(
        ["osascript", "-e", script],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        if "JavaScript from Apple Events" in err or "not allowed" in err.lower():
            raise RuntimeError(
                "Safari bloque JavaScript depuis Apple Events. Activez Safari > "
                "Develop/Developpeur > Allow JavaScript from Apple Events."
            )
        raise RuntimeError(err or f"osascript exited with {proc.returncode}")
    return proc.stdout


def read_dashboard_page(url_fragment: str = URL_FRAGMENT) -> SafariPage:
    # ASCII record separator keeps URL and page text unambiguous.
    sep = "__OPENCLAW_PAGE_SEP__"
    fragment = url_fragment.replace('"', '\\"')
    js = "document.body ? document.body.innerText : ''"
    script = f'''
    tell application "Safari"
        if (count of documents) is 0 then error "Safari has no open documents"
        repeat with d in documents
            try
                set u to URL of d
                if u contains "{fragment}" then
                    set bodyText to do JavaScript "{js}" in d
                    return u & "{sep}" & bodyText
                end if
            end try
        end repeat
        error "No Safari tab matched {fragment}"
    end tell
    '''
    out = _run_osascript(script)
    if sep not in out:
        raise RuntimeError("Unexpected Safari response")
    url, text = out.split(sep, 1)
    return SafariPage(url=url.strip(), text=text.strip())


def extract_channel_sections(text: str, channels: Iterable[str]) -> dict[str, str]:
    """Best-effort split of Dashboard.gg body text by channel headings.

    Raw snapshots are always preserved, so parser improvements can be applied later
    without changing the historical observation.
    """
    channels = tuple(channels)
    lower = text.lower()
    starts: list[tuple[int, str]] = []
    for channel in channels:
        pos = lower.find(channel.lower())
        if pos >= 0:
            starts.append((pos, channel))
    starts.sort()
    sections: dict[str, str] = {}
    for i, (start, channel) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        sections[channel] = text[start:end].strip()
    return sections


def split_message_blocks(section: str) -> list[str]:
    """Split visible channel text into coarse message/card blocks."""
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        return []
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        # Dashboard bot rows normally expose a displayed HH:MM or HH:MM:SS time.
        # Treat a new timed line as a likely message boundary.
        if current and TIME_RE.search(line):
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return ["\n".join(block).strip() for block in blocks if block]


def infer_ticker(text: str) -> str:
    for match in TICKER_RE.finditer(text):
        ticker = match.group(1)
        if ticker not in EXCLUDED_TICKERS:
            return ticker
    return ""


def infer_alert_type(text: str) -> str:
    match = ALERT_RE.search(text)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def normalize_blocks(
    channel: str,
    section: str,
    source_url: str,
    captured_local: datetime,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    captured_utc = captured_local.astimezone(timezone.utc)
    for block in split_message_blocks(section):
        time_match = TIME_RE.search(block)
        ticker = infer_ticker(block)
        alert_type = infer_alert_type(block)
        # Skip heading-only/navigation fragments while retaining actual bot/card text.
        if not time_match and not ticker and not alert_type:
            continue
        stable = f"{channel}\n{block}".encode("utf-8", errors="replace")
        event_id = hashlib.sha256(stable).hexdigest()[:24]
        rows.append(
            {
                "event_id": event_id,
                "captured_at_utc": captured_utc.isoformat(),
                "captured_at_local": captured_local.isoformat(),
                "source_url": source_url,
                "channel": channel,
                "message_time_display": time_match.group(0) if time_match else "",
                "ticker": ticker,
                "alert_type": alert_type,
                "text": block,
            }
        )
    return rows


def existing_event_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            event_id = row.get("event_id", "")
            if event_id:
                ids.add(event_id)
    return ids


def append_csv(path: Path, rows: list[dict[str, str]], seen: set[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_rows = [row for row in rows if row["event_id"] not in seen]
    if not new_rows:
        return 0
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)
    seen.update(row["event_id"] for row in new_rows)
    return len(new_rows)


def append_raw_snapshot(
    root: Path,
    channel: str,
    section: str,
    source_url: str,
    captured_local: datetime,
    previous_hashes: dict[str, str],
) -> bool:
    digest = hashlib.sha256(section.encode("utf-8", errors="replace")).hexdigest()
    if previous_hashes.get(channel) == digest:
        return False
    previous_hashes[channel] = digest
    day = captured_local.date().isoformat()
    path = root / day / f"{channel}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "captured_at_utc": captured_local.astimezone(timezone.utc).isoformat(),
        "captured_at_local": captured_local.isoformat(),
        "source_url": source_url,
        "channel": channel,
        "sha256": digest,
        "text": section,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


def capture_once(args: argparse.Namespace, seen: set[str], hashes: dict[str, str]) -> tuple[int, int]:
    page = read_dashboard_page(args.url_fragment)
    sections = extract_channel_sections(page.text, args.channels)
    missing = [channel for channel in args.channels if channel not in sections]
    if missing:
        print(f"WARN channels not found in rendered page: {', '.join(missing)}", file=sys.stderr)
    captured_local = datetime.now().astimezone()
    raw_changes = 0
    normalized: list[dict[str, str]] = []
    for channel, section in sections.items():
        raw_changes += int(
            append_raw_snapshot(
                args.raw_root, channel, section, page.url, captured_local, hashes
            )
        )
        normalized.extend(normalize_blocks(channel, section, page.url, captured_local))
    new_events = append_csv(args.events_csv, normalized, seen)
    return raw_changes, new_events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture observed Dashboard.gg channel text from an existing Safari session."
    )
    parser.add_argument("--channels", nargs="+", default=list(DEFAULT_CHANNELS))
    parser.add_argument("--interval", type=float, default=5.0, help="poll interval in seconds")
    parser.add_argument("--once", action="store_true", help="capture one snapshot then exit")
    parser.add_argument("--url-fragment", default=URL_FRAGMENT)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw/dashboard_gg"))
    parser.add_argument(
        "--events-csv", type=Path, default=Path("data/derived/dashboard_gg/events_observed.csv")
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if sys.platform != "darwin":
        print("ERROR this collector must run on the Mac that owns the Safari session.", file=sys.stderr)
        return 2
    if args.interval < 1.0:
        print("ERROR --interval must be >= 1 second", file=sys.stderr)
        return 2
    seen = existing_event_ids(args.events_csv)
    hashes: dict[str, str] = {}
    print(
        "OpenClaw Dashboard.gg capture started | "
        f"channels={','.join(args.channels)} | interval={args.interval:g}s"
    )
    print(f"raw={args.raw_root} | events={args.events_csv}")
    try:
        while True:
            try:
                raw_changes, new_events = capture_once(args, seen, hashes)
                stamp = datetime.now().astimezone().strftime("%H:%M:%S")
                print(f"[{stamp}] raw_changes={raw_changes} new_events={new_events}", flush=True)
            except RuntimeError as exc:
                print(f"ERROR {exc}", file=sys.stderr, flush=True)
                if args.once:
                    return 1
            if args.once:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nCapture stopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
