"""Deterministic Volume Spike feature for OpenClaw.

The feature deliberately keeps two evidence channels separate:

1. ``heatseeker_observed``: an explicit observation from a Heatseeker card/image.
2. ``market_calculated``: a reproducible calculation from observed option volume
   and a same-clock historical baseline supplied by the caller.

No dealer sign, gamma sign, direction, or proprietary Heatseeker state is inferred
from volume alone. Baselines must use the same intraday window (for example
09:30-09:45 ET compared only with prior 09:30-09:45 ET windows).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any, Sequence
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


class VolumeSpikeValidationError(ValueError):
    """Raised when Volume Spike input is ambiguous or non-reproducible."""


@dataclass(frozen=True)
class VolumeSpikeConfig:
    """Frozen research thresholds; these are hypotheses, not proprietary values."""

    min_baseline_sessions: int = 5
    spike_ratio_threshold: float = 2.0
    extreme_ratio_threshold: float = 4.0

    def validate(self) -> None:
        if self.min_baseline_sessions < 1:
            raise VolumeSpikeValidationError("min_baseline_sessions must be >= 1")
        if self.spike_ratio_threshold <= 1.0:
            raise VolumeSpikeValidationError("spike_ratio_threshold must be > 1")
        if self.extreme_ratio_threshold <= self.spike_ratio_threshold:
            raise VolumeSpikeValidationError(
                "extreme_ratio_threshold must be greater than spike_ratio_threshold"
            )


@dataclass(frozen=True)
class VolumeSpikeObservation:
    ticker: str
    timestamp_et: datetime
    window_start_et: datetime
    window_end_et: datetime
    interval_volume: int
    baseline_interval_volumes: tuple[int, ...]
    source: str
    baseline_source: str
    expiration: str = ""
    strike: float | None = None
    option_type: str = ""
    cumulative_volume: int | None = None
    oi_j1: int | None = None
    premium: float | None = None
    spot: float | None = None
    node_type: str = ""
    heatseeker_observed: bool | None = None
    heatseeker_label: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VolumeSpikeObservation":
        def parse_dt(key: str) -> datetime:
            raw = payload.get(key)
            if not isinstance(raw, str) or not raw:
                raise VolumeSpikeValidationError(f"{key} must be an ISO-8601 string")
            try:
                value = datetime.fromisoformat(raw)
            except ValueError as exc:
                raise VolumeSpikeValidationError(f"invalid {key}: {raw}") from exc
            if value.tzinfo is None:
                raise VolumeSpikeValidationError(f"{key} must include a timezone")
            return value.astimezone(ET)

        baseline = payload.get("baseline_interval_volumes")
        if not isinstance(baseline, list):
            raise VolumeSpikeValidationError("baseline_interval_volumes must be a list")

        return cls(
            ticker=str(payload.get("ticker", "")).strip().upper(),
            timestamp_et=parse_dt("timestamp_et"),
            window_start_et=parse_dt("window_start_et"),
            window_end_et=parse_dt("window_end_et"),
            interval_volume=int(payload.get("interval_volume", 0)),
            baseline_interval_volumes=tuple(int(x) for x in baseline),
            source=str(payload.get("source", "")).strip(),
            baseline_source=str(payload.get("baseline_source", "")).strip(),
            expiration=str(payload.get("expiration", "")).strip(),
            strike=_optional_float(payload.get("strike")),
            option_type=str(payload.get("option_type", "")).strip().upper(),
            cumulative_volume=_optional_int(payload.get("cumulative_volume")),
            oi_j1=_optional_int(payload.get("oi_j1")),
            premium=_optional_float(payload.get("premium")),
            spot=_optional_float(payload.get("spot")),
            node_type=str(payload.get("node_type", "")).strip().lower(),
            heatseeker_observed=_optional_bool(payload.get("heatseeker_observed")),
            heatseeker_label=str(payload.get("heatseeker_label", "")).strip(),
        )

    def validate(self) -> None:
        if not self.ticker:
            raise VolumeSpikeValidationError("ticker is required")
        if not self.source:
            raise VolumeSpikeValidationError("source is required")
        if not self.baseline_source:
            raise VolumeSpikeValidationError("baseline_source is required")
        if self.interval_volume < 0:
            raise VolumeSpikeValidationError("interval_volume cannot be negative")
        if any(value < 0 for value in self.baseline_interval_volumes):
            raise VolumeSpikeValidationError("baseline volumes cannot be negative")
        if self.window_end_et <= self.window_start_et:
            raise VolumeSpikeValidationError("window_end_et must be after window_start_et")
        if not (self.window_start_et <= self.timestamp_et <= self.window_end_et):
            raise VolumeSpikeValidationError("timestamp_et must fall inside the measured window")
        if self.option_type and self.option_type not in {"C", "P", "CALL", "PUT"}:
            raise VolumeSpikeValidationError("option_type must be C/P/CALL/PUT when supplied")
        if self.cumulative_volume is not None and self.cumulative_volume < self.interval_volume:
            raise VolumeSpikeValidationError(
                "cumulative_volume cannot be smaller than interval_volume"
            )
        if self.oi_j1 is not None and self.oi_j1 < 0:
            raise VolumeSpikeValidationError("oi_j1 cannot be negative")


@dataclass(frozen=True)
class VolumeSpikeResult:
    ticker: str
    timestamp_et: str
    window_start_et: str
    window_end_et: str
    interval_volume: int
    expected_interval_volume: float | None
    baseline_sessions: int
    spike_ratio: float | None
    volume_oi_ratio: float | None
    market_state: str
    heatseeker_state: str
    evidence_state: str
    directional_bias: None
    source: str
    baseline_source: str
    expiration: str
    strike: float | None
    option_type: str
    cumulative_volume: int | None
    oi_j1: int | None
    premium: float | None
    spot: float | None
    node_type: str
    heatseeker_label: str
    frozen_config: dict[str, float | int]
    warnings: tuple[str, ...]


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _optional_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    raise VolumeSpikeValidationError("heatseeker_observed must be true/false/null")


def _same_clock_window(values: Sequence[int]) -> float:
    return float(median(values))


def analyze_volume_spike(
    observation: VolumeSpikeObservation,
    config: VolumeSpikeConfig | None = None,
) -> VolumeSpikeResult:
    """Calculate a non-directional Volume Spike feature from observed inputs."""

    cfg = config or VolumeSpikeConfig()
    cfg.validate()
    observation.validate()

    warnings: list[str] = []
    baseline_sessions = len(observation.baseline_interval_volumes)
    expected: float | None = None
    spike_ratio: float | None = None

    if baseline_sessions < cfg.min_baseline_sessions:
        market_state = "INSUFFICIENT_BASELINE"
        warnings.append(
            f"need >= {cfg.min_baseline_sessions} same-clock baseline sessions; "
            f"received {baseline_sessions}"
        )
    else:
        expected = _same_clock_window(observation.baseline_interval_volumes)
        if expected <= 0:
            market_state = "ZERO_BASELINE_UNDEFINED"
            warnings.append("same-clock baseline median is zero; spike ratio is undefined")
        else:
            spike_ratio = observation.interval_volume / expected
            if spike_ratio >= cfg.extreme_ratio_threshold:
                market_state = "EXTREME_SPIKE"
            elif spike_ratio >= cfg.spike_ratio_threshold:
                market_state = "SPIKE"
            else:
                market_state = "NORMAL"

    volume_oi_ratio: float | None = None
    if observation.oi_j1 is not None:
        if observation.oi_j1 == 0:
            warnings.append("OI J-1 is zero; volume/OI ratio is undefined")
        else:
            volume_oi_ratio = observation.interval_volume / observation.oi_j1

    if observation.heatseeker_observed is True:
        heatseeker_state = "OBSERVED_SPIKE"
    elif observation.heatseeker_observed is False:
        heatseeker_state = "OBSERVED_NO_SPIKE"
    else:
        heatseeker_state = "NOT_OBSERVED"

    market_spike = market_state in {"SPIKE", "EXTREME_SPIKE"}
    if observation.heatseeker_observed is True and market_spike:
        evidence_state = "BOTH_AGREE_SPIKE"
    elif observation.heatseeker_observed is True:
        evidence_state = "HEATSEEKER_ONLY"
    elif market_spike:
        evidence_state = "MARKET_ONLY"
    elif observation.heatseeker_observed is False and market_state == "NORMAL":
        evidence_state = "BOTH_AGREE_NO_SPIKE"
    else:
        evidence_state = "UNRESOLVED"

    return VolumeSpikeResult(
        ticker=observation.ticker,
        timestamp_et=observation.timestamp_et.isoformat(),
        window_start_et=observation.window_start_et.isoformat(),
        window_end_et=observation.window_end_et.isoformat(),
        interval_volume=observation.interval_volume,
        expected_interval_volume=expected,
        baseline_sessions=baseline_sessions,
        spike_ratio=spike_ratio,
        volume_oi_ratio=volume_oi_ratio,
        market_state=market_state,
        heatseeker_state=heatseeker_state,
        evidence_state=evidence_state,
        directional_bias=None,
        source=observation.source,
        baseline_source=observation.baseline_source,
        expiration=observation.expiration,
        strike=observation.strike,
        option_type=observation.option_type,
        cumulative_volume=observation.cumulative_volume,
        oi_j1=observation.oi_j1,
        premium=observation.premium,
        spot=observation.spot,
        node_type=observation.node_type,
        heatseeker_label=observation.heatseeker_label,
        frozen_config={
            "min_baseline_sessions": cfg.min_baseline_sessions,
            "spike_ratio_threshold": cfg.spike_ratio_threshold,
            "extreme_ratio_threshold": cfg.extreme_ratio_threshold,
        },
        warnings=tuple(warnings),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw Volume Spike feature")
    parser.add_argument("input", type=Path, help="Observed-data JSON payload")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    observation = VolumeSpikeObservation.from_dict(payload)
    result = analyze_volume_spike(observation)
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
