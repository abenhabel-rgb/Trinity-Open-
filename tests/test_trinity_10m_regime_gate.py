import csv
from datetime import datetime
import json
from pathlib import Path
import tempfile
import unittest

from trinity.trinity_10m_regime_gate import (
    DataValidationError,
    GateConfig,
    TrinityObservation,
    classify_observation,
    main,
    parse_optional_timestamp,
)


def ts(value: str) -> datetime:
    parsed = parse_optional_timestamp(value, field="fixture")
    assert parsed is not None
    return parsed


def observation(**overrides: object) -> TrinityObservation:
    values: dict[str, object] = {
        "session_id": "fixture-1",
        "market_open": ts("2026-09-01T09:30:00-04:00"),
        "decision_time": ts("2026-09-01T09:39:00-04:00"),
        "spx_air_pocket_up": True,
        "spx_route_clear": True,
        "spy_spot": 750.74,
        "spy_floor": 751.00,
        "spy_floor_tested": True,
        "spy_floor_held": True,
        "qqq_spot": 687.39,
        "qqq_floor": 686.00,
        "qqq_floor_tested": True,
        "qqq_floor_held": True,
        "spx_source": "fixture:spx",
        "spy_source": "fixture:spy",
        "qqq_source": "fixture:qqq",
        "notes": "synthetic logic fixture",
    }
    values.update(overrides)
    return TrinityObservation(**values)  # type: ignore[arg-type]


class TrinityTenMinuteGateTests(unittest.TestCase):
    def test_complete_first_ten_minute_confluence_is_trend_up(self) -> None:
        result = classify_observation(observation(), GateConfig())

        self.assertEqual(result.lifecycle, "TREND_UP")
        self.assertEqual(result.reason, "trinity_upside_confluence")
        self.assertAlmostEqual(result.minutes_after_open or 0.0, 9.0)
        self.assertTrue(result.spy_above_floor)
        self.assertTrue(result.qqq_above_floor)

    def test_floor_tolerance_is_explicit_and_configurable(self) -> None:
        strict = classify_observation(
            observation(), GateConfig(floor_tolerance_bps=0.0)
        )
        tolerant = classify_observation(
            observation(), GateConfig(floor_tolerance_bps=5.0)
        )

        self.assertEqual(strict.lifecycle, "UNCONFIRMED")
        self.assertIn("spy_above_floor", strict.reason)
        self.assertEqual(tolerant.lifecycle, "TREND_UP")

    def test_missing_source_is_blocked(self) -> None:
        result = classify_observation(observation(qqq_source=""), GateConfig())

        self.assertEqual(result.lifecycle, "BLOCKED")
        self.assertEqual(result.reason, "missing_source:QQQ")

    def test_missing_feature_is_blocked_not_imputed(self) -> None:
        result = classify_observation(
            observation(spx_air_pocket_up=None), GateConfig()
        )

        self.assertEqual(result.lifecycle, "BLOCKED")
        self.assertEqual(result.reason, "missing_feature:spx_air_pocket_up")

    def test_decision_after_cutoff_is_blocked(self) -> None:
        result = classify_observation(
            observation(decision_time=ts("2026-09-01T09:41:00-04:00")),
            GateConfig(max_minutes_after_open=10.0),
        )

        self.assertEqual(result.lifecycle, "BLOCKED")
        self.assertEqual(result.reason, "decision_after_frozen_cutoff")

    def test_naive_timestamp_is_rejected(self) -> None:
        with self.assertRaisesRegex(DataValidationError, "timezone offset is required"):
            parse_optional_timestamp("2026-09-01T09:39:00", field="fixture")

    def test_cli_reads_csv_and_writes_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observations_path = root / "observations.csv"
            results_path = root / "results.csv"
            summary_path = root / "summary.json"
            fields = [
                "session_id",
                "market_open_et",
                "decision_time_et",
                "spx_air_pocket_up",
                "spx_route_clear",
                "spy_spot",
                "spy_floor",
                "spy_floor_tested",
                "spy_floor_held",
                "qqq_spot",
                "qqq_floor",
                "qqq_floor_tested",
                "qqq_floor_held",
                "spx_source",
                "spy_source",
                "qqq_source",
                "notes",
            ]
            with observations_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow(
                    {
                        "session_id": "fixture-1",
                        "market_open_et": "2026-09-01T09:30:00-04:00",
                        "decision_time_et": "2026-09-01T09:39:00-04:00",
                        "spx_air_pocket_up": "true",
                        "spx_route_clear": "true",
                        "spy_spot": "750.74",
                        "spy_floor": "751",
                        "spy_floor_tested": "true",
                        "spy_floor_held": "true",
                        "qqq_spot": "687.39",
                        "qqq_floor": "686",
                        "qqq_floor_tested": "true",
                        "qqq_floor_held": "true",
                        "spx_source": "fixture:spx",
                        "spy_source": "fixture:spy",
                        "qqq_source": "fixture:qqq",
                        "notes": "synthetic logic fixture",
                    }
                )

            status = main(
                [
                    "--observations",
                    str(observations_path),
                    "--out",
                    str(results_path),
                    "--summary",
                    str(summary_path),
                ]
            )

            self.assertEqual(status, 0)
            with results_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["lifecycle"], "TREND_UP")
            with summary_path.open("r", encoding="utf-8") as handle:
                summary = json.load(handle)
            self.assertEqual(summary["n_trend_up"], 1)


if __name__ == "__main__":
    unittest.main()
