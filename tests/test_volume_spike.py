from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from trinity.volume_spike import (
    VolumeSpikeConfig,
    VolumeSpikeObservation,
    VolumeSpikeValidationError,
    analyze_volume_spike,
)

ET = ZoneInfo("America/New_York")


def obs(**overrides):
    payload = dict(
        ticker="MU",
        timestamp_et=datetime(2026, 9, 2, 9, 45, tzinfo=ET),
        window_start_et=datetime(2026, 9, 2, 9, 30, tzinfo=ET),
        window_end_et=datetime(2026, 9, 2, 9, 45, tzinfo=ET),
        interval_volume=17000,
        baseline_interval_volumes=(3900, 4100, 4000, 4200, 3800),
        source="thetadata observed trades",
        baseline_source="same-clock prior sessions",
        expiration="2026-09-04",
        strike=315.0,
        option_type="C",
        cumulative_volume=22000,
        oi_j1=8000,
        premium=1.25,
        spot=313.4,
        node_type="king",
        heatseeker_observed=True,
        heatseeker_label="volume_spike",
    )
    payload.update(overrides)
    return VolumeSpikeObservation(**payload)


def test_extreme_spike_and_heatseeker_agree():
    result = analyze_volume_spike(obs())
    assert result.expected_interval_volume == 4000.0
    assert result.spike_ratio == 4.25
    assert result.volume_oi_ratio == 2.125
    assert result.market_state == "EXTREME_SPIKE"
    assert result.heatseeker_state == "OBSERVED_SPIKE"
    assert result.evidence_state == "BOTH_AGREE_SPIKE"
    assert result.directional_bias is None


def test_market_only_spike_keeps_channels_separate():
    result = analyze_volume_spike(obs(heatseeker_observed=None, interval_volume=10000))
    assert result.spike_ratio == 2.5
    assert result.market_state == "SPIKE"
    assert result.heatseeker_state == "NOT_OBSERVED"
    assert result.evidence_state == "MARKET_ONLY"


def test_insufficient_baseline_abstains():
    result = analyze_volume_spike(obs(baseline_interval_volumes=(4000, 4100)))
    assert result.market_state == "INSUFFICIENT_BASELINE"
    assert result.spike_ratio is None
    assert result.evidence_state == "HEATSEEKER_ONLY"
    assert result.warnings


def test_zero_baseline_is_undefined_not_infinite():
    result = analyze_volume_spike(obs(baseline_interval_volumes=(0, 0, 0, 0, 0)))
    assert result.market_state == "ZERO_BASELINE_UNDEFINED"
    assert result.spike_ratio is None


def test_invalid_window_rejected():
    with pytest.raises(VolumeSpikeValidationError):
        analyze_volume_spike(
            obs(
                window_start_et=datetime(2026, 9, 2, 9, 45, tzinfo=ET),
                window_end_et=datetime(2026, 9, 2, 9, 30, tzinfo=ET),
            )
        )


def test_config_requires_frozen_ordered_thresholds():
    with pytest.raises(VolumeSpikeValidationError):
        analyze_volume_spike(obs(), VolumeSpikeConfig(spike_ratio_threshold=4, extreme_ratio_threshold=3))
