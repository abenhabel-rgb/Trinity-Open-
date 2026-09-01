import csv
from datetime import datetime
import json
from pathlib import Path
import tempfile
import unittest

from trinity.midas_flow_heat_gate import (
    Candidate,
    DataValidationError,
    GateConfig,
    Quote,
    analyze_candidate,
    main,
    parse_timestamp,
    summarize,
)


def ts(value: str) -> datetime:
    parsed = parse_timestamp(value, field="test")
    assert parsed is not None
    return parsed


def candidate(**overrides: object) -> Candidate:
    values: dict[str, object] = {
        "candidate_id": "case-1",
        "ticker": "META",
        "contract": "META 600C 2026-07-10",
        "direction": "BULL",
        "flow_time": ts("2026-06-25T09:30:00-04:00"),
        "heat_time": ts("2026-06-25T09:35:00-04:00"),
        "evaluation_end": ts("2026-06-25T09:50:00-04:00"),
        "flow_observed": True,
        "heat_observed": True,
        "heat_event": "NODE_FLIP",
        "breadth_confirmed": True,
        "flow_source": "fixture:flow",
        "heat_source": "fixture:heat",
    }
    values.update(overrides)
    return Candidate(**values)  # type: ignore[arg-type]


def quotes() -> list[Quote]:
    rows = [
        ("2026-06-25T09:30:00-04:00", 1.00, 1.10),
        ("2026-06-25T09:31:00-04:00", 0.70, 0.80),
        ("2026-06-25T09:35:00-04:00", 0.90, 1.00),
        ("2026-06-25T09:40:00-04:00", 1.40, 1.50),
        ("2026-06-25T09:50:00-04:00", 1.20, 1.30),
    ]
    return [Quote("case-1", ts(timestamp), bid, ask) for timestamp, bid, ask in rows]


class MidasFlowHeatGateTests(unittest.TestCase):
    def test_triggered_gate_compares_same_observed_path(self) -> None:
        row = analyze_candidate(candidate(), quotes(), GateConfig(require_breadth=True))

        self.assertEqual(row.lifecycle, "TRIGGERED")
        self.assertAlmostEqual(row.flow_entry_ask or 0.0, 1.10)
        self.assertAlmostEqual(row.gated_entry_ask or 0.0, 1.00)
        self.assertAlmostEqual(row.flow_mae_pct or 0.0, -36.363636, places=5)
        self.assertAlmostEqual(row.gated_mae_pct or 0.0, -10.0)
        self.assertAlmostEqual(row.mae_improvement_pp or 0.0, 26.363636, places=5)

    def test_missing_heat_stays_watching(self) -> None:
        row = analyze_candidate(
            candidate(heat_observed=False, heat_time=None, heat_source=""),
            quotes(),
            GateConfig(),
        )

        self.assertEqual(row.lifecycle, "WATCHING")
        self.assertEqual(row.reason, "heat_trigger_not_observed")
        self.assertIsNone(row.gated_entry_ask)

    def test_breadth_gate_is_explicit_not_silently_imputed(self) -> None:
        row = analyze_candidate(
            candidate(breadth_confirmed=False), quotes(), GateConfig(require_breadth=True)
        )

        self.assertEqual(row.lifecycle, "WATCHING")
        self.assertEqual(row.reason, "breadth_not_confirmed")

    def test_naive_timestamp_is_rejected(self) -> None:
        with self.assertRaisesRegex(DataValidationError, "timezone offset is required"):
            parse_timestamp("2026-06-25T09:30:00", field="event")

    def test_summary_does_not_convert_missing_data_to_success(self) -> None:
        triggered = analyze_candidate(candidate(), quotes(), GateConfig())
        blocked = analyze_candidate(
            candidate(candidate_id="case-2", heat_observed=False, heat_time=None, heat_source=""),
            [],
            GateConfig(),
        )

        result = summarize([triggered, blocked], bootstrap_samples=0)
        self.assertEqual(result["n_candidates"], 2)
        self.assertEqual(result["n_triggered"], 1)
        self.assertEqual(result["n_blocked"], 1)

    def test_cli_reads_csv_and_writes_auditable_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            events_path = root / "events.csv"
            quotes_path = root / "quotes.csv"
            rows_path = root / "rows.csv"
            summary_path = root / "summary.json"

            with events_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "candidate_id",
                        "ticker",
                        "contract",
                        "direction",
                        "flow_time_et",
                        "heat_time_et",
                        "evaluation_end_et",
                        "flow_observed",
                        "heat_observed",
                        "heat_event",
                        "breadth_confirmed",
                        "flow_source",
                        "heat_source",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "case-1",
                        "ticker": "META",
                        "contract": "META 600C 2026-07-10",
                        "direction": "BULL",
                        "flow_time_et": "2026-06-25T09:30:00-04:00",
                        "heat_time_et": "2026-06-25T09:35:00-04:00",
                        "evaluation_end_et": "2026-06-25T09:50:00-04:00",
                        "flow_observed": "true",
                        "heat_observed": "true",
                        "heat_event": "NODE_FLIP",
                        "breadth_confirmed": "true",
                        "flow_source": "fixture:flow",
                        "heat_source": "fixture:heat",
                    }
                )

            with quotes_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["candidate_id", "timestamp_et", "bid", "ask"],
                )
                writer.writeheader()
                for quote in quotes():
                    writer.writerow(
                        {
                            "candidate_id": quote.candidate_id,
                            "timestamp_et": quote.timestamp.isoformat(),
                            "bid": quote.bid,
                            "ask": quote.ask,
                        }
                    )

            status = main(
                [
                    "--events",
                    str(events_path),
                    "--quotes",
                    str(quotes_path),
                    "--out",
                    str(rows_path),
                    "--summary",
                    str(summary_path),
                    "--require-breadth",
                    "--bootstrap-samples",
                    "0",
                ]
            )

            self.assertEqual(status, 0)
            with rows_path.open("r", encoding="utf-8", newline="") as handle:
                output_rows = list(csv.DictReader(handle))
            self.assertEqual(output_rows[0]["lifecycle"], "TRIGGERED")
            with summary_path.open("r", encoding="utf-8") as handle:
                output_summary = json.load(handle)
            self.assertEqual(output_summary["n_triggered"], 1)


if __name__ == "__main__":
    unittest.main()
