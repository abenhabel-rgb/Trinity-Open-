"""Observed-only parser for Discord Heatseeker GEX/VEX matrix screenshots.

The parser consumes OCR observations with normalized Vision bounding boxes. It
never interpolates a missing matrix value: unread fields remain absent. Derived
comparisons are kept separate from raw observed fields.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Iterable

DATE_RE = re.compile(r"20\d{2}-\d{2}-\d{2}")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}:\d{2}\b")
FOOTER_RE = re.compile(
    r"\b(?P<ticker>[A-Z][A-Z0-9.\-]{0,8})\s+"
    r"(?P<metric>GEX|VEX)\s*[-–—]\s*"
    r"(?P<date>20\d{2}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{1,2}:\d{2}:\d{2})\s*[-–—]\s*"
    r"Current\s+Price\s*:\s*\$?(?P<spot>[0-9][0-9,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
STRIKE_RE = re.compile(r"^\d{1,5}(?:\.\d{1,3})?$")
MONEY_RE = re.compile(
    r"^(?P<sign>-)?\$?(?P<num>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*(?P<mult>[KMB])?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Token:
    text: str
    confidence: float
    x: float
    y: float
    width: float
    height: float

    @property
    def cx(self) -> float:
        return self.x + self.width / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.height / 2.0


@dataclass(frozen=True)
class Footer:
    ticker: str
    metric: str
    internal_timestamp: str
    spot: float
    raw_text: str


@dataclass(frozen=True)
class MatrixCell:
    strike: float
    expiration: str
    value: float
    raw_text: str
    confidence: float


def normalize_text(text: str) -> str:
    return (
        text.replace("−", "-")
        .replace("–", "-")
        .replace("—", "-")
        .replace("＄", "$")
        .strip()
    )


def parse_money(text: str) -> float | None:
    """Parse observed GEX/VEX labels like -$547.8K or $2.03M.

    Bare numbers without a K/M/B suffix are accepted because OCR sometimes
    drops the dollar sign; this function does not infer a suffix.
    """
    t = normalize_text(text).replace(" ", "")
    # Common OCR punctuation noise at token edges only.
    t = t.strip("|[](){}")
    m = MONEY_RE.match(t)
    if not m:
        return None
    number = float(m.group("num").replace(",", ""))
    if m.group("sign"):
        number *= -1.0
    mult = (m.group("mult") or "").upper()
    if mult == "K":
        number *= 1_000.0
    elif mult == "M":
        number *= 1_000_000.0
    elif mult == "B":
        number *= 1_000_000_000.0
    return number


def _expand_line(line: dict[str, Any]) -> list[Token]:
    text = normalize_text(str(line.get("text", "")))
    if not text:
        return []
    conf = float(line.get("confidence", 0.0) or 0.0)
    x = float(line.get("x", 0.0) or 0.0)
    y = float(line.get("y", 0.0) or 0.0)
    width = float(line.get("width", 0.0) or 0.0)
    height = float(line.get("height", 0.0) or 0.0)

    parts = list(re.finditer(r"\S+", text))
    if len(parts) <= 1 or not width:
        return [Token(text=text, confidence=conf, x=x, y=y, width=width, height=height)]

    total_chars = max(1, len(text))
    tokens: list[Token] = []
    for p in parts:
        start, end = p.span()
        tx = x + width * (start / total_chars)
        tw = width * ((end - start) / total_chars)
        tokens.append(Token(p.group(0), conf, tx, y, tw, height))
    return tokens


def tokenize(lines: Iterable[dict[str, Any]]) -> list[Token]:
    out: list[Token] = []
    for line in lines:
        out.extend(_expand_line(line))
    return out


def parse_footer(lines: list[dict[str, Any]]) -> Footer | None:
    # Footer normally lives at the very bottom; search bottom observations first,
    # then all OCR text as a fallback because Vision can merge neighboring lines.
    ordered = sorted(lines, key=lambda r: float(r.get("y", 0.0) or 0.0))
    candidates: list[str] = []
    bottom = [normalize_text(str(r.get("text", ""))) for r in ordered if float(r.get("y", 0.0) or 0.0) < 0.18]
    if bottom:
        candidates.extend([" ".join(bottom), *bottom])
    all_text = " ".join(normalize_text(str(r.get("text", ""))) for r in ordered)
    candidates.append(all_text)

    for text in candidates:
        # Normalize repeated spaces and OCR dash variants.
        text = re.sub(r"\s+", " ", text)
        m = FOOTER_RE.search(text)
        if not m:
            continue
        try:
            dt = datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y-%m-%d %H:%M:%S")
            spot = float(m.group("spot").replace(",", ""))
        except ValueError:
            continue
        return Footer(
            ticker=m.group("ticker").upper(),
            metric=m.group("metric").upper(),
            internal_timestamp=dt.isoformat(),
            spot=spot,
            raw_text=m.group(0),
        )
    return None


def _dedupe_header_dates(tokens: list[Token]) -> list[tuple[str, float, float]]:
    found: list[tuple[str, float, float]] = []
    for t in tokens:
        m = DATE_RE.search(t.text)
        if not m:
            continue
        # Expiration headers are near the top, unlike footer timestamp.
        if t.cy < 0.72:
            continue
        found.append((m.group(0), t.cx, t.confidence))

    found.sort(key=lambda x: x[1])
    deduped: list[tuple[str, float, float]] = []
    for item in found:
        if deduped and abs(item[1] - deduped[-1][1]) < 0.025:
            if item[2] > deduped[-1][2]:
                deduped[-1] = item
            continue
        deduped.append(item)
    # Matrices in observed samples contain roughly 5 expiration columns. Keep
    # all credible date headers but reject footer-like singleton at far left.
    return deduped


def _strike_tokens(tokens: list[Token], header_xs: list[float]) -> list[Token]:
    if not header_xs:
        return []
    first_col = min(header_xs)
    cutoff = min(0.18, first_col - 0.035)
    strikes: list[Token] = []
    for t in tokens:
        raw = t.text.replace(",", "")
        if t.cx > cutoff or t.cy > 0.82 or t.cy < 0.035:
            continue
        if not STRIKE_RE.match(raw):
            continue
        value = float(raw)
        if value <= 0 or value > 100_000:
            continue
        strikes.append(t)
    # One strike label per row; resolve OCR duplicates by confidence.
    strikes.sort(key=lambda t: -t.cy)
    out: list[Token] = []
    for t in strikes:
        if out and abs(t.cy - out[-1].cy) < max(0.0025, min(t.height, out[-1].height) * 0.45):
            if t.confidence > out[-1].confidence:
                out[-1] = t
        else:
            out.append(t)
    return out


def parse_matrix(lines: list[dict[str, Any]]) -> tuple[list[str], list[float], list[MatrixCell], dict[str, Any]]:
    tokens = tokenize(lines)
    headers = _dedupe_header_dates(tokens)
    expirations = [d for d, _, _ in headers]
    header_xs = [x for _, x, _ in headers]
    strike_tokens = _strike_tokens(tokens, header_xs)

    # Candidate value tokens must be in/near a data column and away from footer.
    values: list[tuple[Token, float]] = []
    for t in tokens:
        value = parse_money(t.text)
        if value is None:
            continue
        if t.cy < 0.035 or t.cy > 0.84:
            continue
        if header_xs and t.cx < min(header_xs) - 0.035:
            continue
        values.append((t, value))

    cells: list[MatrixCell] = []
    used: set[tuple[int, int]] = set()
    strikes_out: list[float] = []

    for st in strike_tokens:
        strike = float(st.text.replace(",", ""))
        strikes_out.append(strike)
        # Row spacing is dense. Derive a local tolerance from OCR box height,
        # bounded so adjacent rows do not collapse into one.
        y_tol = max(0.0032, min(0.012, st.height * 0.75 if st.height else 0.006))
        for col_idx, (expiration, hx, _) in enumerate(headers):
            best: tuple[float, int, Token, float] | None = None
            for idx, (vt, numeric) in enumerate(values):
                if (idx, col_idx) in used:
                    continue
                dy = abs(vt.cy - st.cy)
                if dy > y_tol:
                    continue
                # Columns can be fairly wide; midpoint matching is safer than
                # requiring exact header x because OCR boxes differ in width.
                dx = abs(vt.cx - hx)
                if dx > 0.085:
                    continue
                score = (dy / y_tol) + (dx / 0.085) - 0.15 * vt.confidence
                if best is None or score < best[0]:
                    best = (score, idx, vt, numeric)
            if best is None:
                continue
            _, idx, vt, numeric = best
            used.add((idx, col_idx))
            cells.append(
                MatrixCell(
                    strike=strike,
                    expiration=expiration,
                    value=numeric,
                    raw_text=vt.text,
                    confidence=vt.confidence,
                )
            )

    possible = len(strikes_out) * len(expirations)
    quality = {
        "expiration_count": len(expirations),
        "strike_count": len(strikes_out),
        "cell_count": len(cells),
        "possible_cells": possible,
        "cell_fill_ratio": (len(cells) / possible) if possible else 0.0,
        "mean_cell_confidence": (
            sum(c.confidence for c in cells) / len(cells) if cells else 0.0
        ),
    }
    return expirations, strikes_out, cells, quality


def parse_ocr_result(payload: dict[str, Any]) -> dict[str, Any]:
    lines = list(payload.get("lines") or [])
    footer = parse_footer(lines)
    expirations, strikes, cells, quality = parse_matrix(lines)

    if footer and len(expirations) >= 1 and len(strikes) >= 3 and len(cells) >= 3:
        status = "parsed_matrix"
    elif footer:
        status = "footer_only"
    elif cells:
        status = "matrix_without_footer"
    else:
        status = "unparsed"

    return {
        "parse_status": status,
        "footer": asdict(footer) if footer else None,
        "expirations": expirations,
        "strikes": strikes,
        "cells": [asdict(c) for c in cells],
        "quality": quality,
        "ocr_line_count": len(lines),
        "data_policy": "observed_only",
    }


def parse_capture_filename_time(basename: str) -> str:
    m = re.search(r"2026-08-28[_-](\d{2})-(\d{2})-(\d{2})", basename)
    if not m:
        return ""
    return f"2026-08-28T{m.group(1)}:{m.group(2)}:{m.group(3)}"


def seconds_between_naive(a: str, b: str) -> float | None:
    if not a or not b:
        return None
    try:
        da = datetime.fromisoformat(a)
        db = datetime.fromisoformat(b)
    except ValueError:
        return None
    return (da - db).total_seconds()
