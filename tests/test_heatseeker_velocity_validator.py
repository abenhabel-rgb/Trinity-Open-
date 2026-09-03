from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_heatseeker_velocity.py"
spec = importlib.util.spec_from_file_location("validate_heatseeker_velocity", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _records(payloads):
    records = []
    for payload in payloads:
        records.extend(module.normalize_payload(payload))
    return records


def test_one_minute_signed_formula_and_denominator():
    records = _records(
        [
            {
                "type": "snapshot",
                "timestamp": "2026-09-03T14:30:00Z",
                "greek": "GEX",
                "expiration": "2026-09-04",
                "cells": [{"strike": 100, "value": 1000}],
            },
            {
                "type": "velocity_update",
                "timestamp": "2026-09-03T14:31:00Z",
                "greek": "GEX",
                "expiration": "2026-09-04",
                "cells": [
                    {
                        "strike": 100,
                        "value": 1200,
                        "delta1Min": 200,
                        "percent1Min": 20,
                    }
                ],
            },
        ]
    )

    evidence = module.analyze(
        records,
        policies=["nearest"],
        max_timing_error_seconds=0,
        atol=1e-8,
        rtol=1e-6,
    )
    row = evidence.iloc[0]
    assert bool(row["delta_exact"])
    assert bool(row["percent_exact__delta_over_prev_signed"])
    assert np.isclose(row["implicit_denominator"], 1000.0)


def test_sign_flip_distinguishes_signed_and_absolute_denominator():
    records = _records(
        [
            {
                "timestamp": "2026-09-03T14:30:00Z",
                "greek": "VEX",
                "expiration": "2026-09-04",
                "strike": 200,
                "value": -100,
            },
            {
                "timestamp": "2026-09-03T14:31:00Z",
                "greek": "VEX",
                "expiration": "2026-09-04",
                "strike": 200,
                "value": 50,
                "delta1Min": 150,
                "percent1Min": -150,
            },
        ]
    )

    evidence = module.analyze(
        records,
        policies=["nearest"],
        max_timing_error_seconds=0,
        atol=1e-8,
        rtol=1e-6,
    )
    row = evidence.iloc[0]
    assert row["case"] == "sign_flip"
    assert bool(row["percent_exact__delta_over_prev_signed"])
    assert not bool(row["percent_exact__delta_over_prev_abs"])
    assert np.isclose(row["implicit_denominator"], -100.0)


def test_zero_reference_is_isolated_not_divided():
    records = _records(
        [
            {
                "timestamp": "2026-09-03T14:30:00Z",
                "greek": "GEX",
                "expiration": "2026-09-04",
                "strike": 300,
                "value": 0,
            },
            {
                "timestamp": "2026-09-03T14:31:00Z",
                "greek": "GEX",
                "expiration": "2026-09-04",
                "strike": 300,
                "value": 10,
                "delta1Min": 10,
                "percent1Min": None,
            },
        ]
    )

    evidence = module.analyze(
        records,
        policies=["nearest"],
        max_timing_error_seconds=0,
        atol=1e-8,
        rtol=1e-6,
    )
    row = evidence.iloc[0]
    assert row["case"] == "zero_reference"
    assert np.isnan(row["predicted_percent__delta_over_prev_signed"])
