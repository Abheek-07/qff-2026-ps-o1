"""Dependency-light validation tests for the Bell benchmark wrapper.

Run: python -m unittest -v bell_validation.py
These tests do not replace the official Qiskit/Aer simulation test. They validate
pair-selection logic, published formulas, required shot policy, and CSV schema.
"""
from __future__ import annotations

import csv
import math
import tempfile
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

from bell_experiments import (
    CSV_FIELDS, REQUIRED_SHOTS, build_rows, choose_pairs, graph_distances, run, write_csv,
)


class PairSelectionTests(unittest.TestCase):
    def setUp(self):
        # Test-only graph fixture; this is NOT a proposed Processor D.
        self.graph = {
            "num_qubits": 6,
            "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)],
        }

    def test_adjacent_is_a_real_edge_and_distance_one(self):
        adjacent, _ = choose_pairs(self.graph)
        self.assertIn(adjacent, {tuple(sorted(e)) for e in self.graph["edges"]})
        self.assertEqual(graph_distances(6, self.graph["edges"], adjacent[0])[adjacent[1]], 1)

    def test_farthest_pair_has_graph_diameter(self):
        _, farthest = choose_pairs(self.graph)
        distances = graph_distances(6, self.graph["edges"], farthest[0])
        all_distances = [
            graph_distances(6, self.graph["edges"], a)[b]
            for a in range(6) for b in range(a + 1, 6)
        ]
        self.assertEqual(distances[farthest[1]], max(all_distances))

    def test_disconnected_graph_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "disconnected"):
            graph_distances(6, [(0, 1), (2, 3), (3, 4), (4, 5)], 0)

    def test_no_edges_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no edges"):
            choose_pairs({"num_qubits": 6, "edges": []})


class FormulaAndSchemaTests(unittest.TestCase):
    def test_parity_expectation_formula(self):
        # Same parity convention as official helper: even=00/11, odd=01/10.
        counts = {"00": 45, "11": 45, "01": 5, "10": 5}
        n = sum(counts.values())
        even = counts["00"] + counts["11"]
        expectation = (2 * even - n) / n
        se = math.sqrt(max(1 - expectation * expectation, 0.0) / n)
        self.assertAlmostEqual(expectation, 0.8)
        self.assertAlmostEqual(se, math.sqrt(0.36 / 100))

    def test_phi_plus_fidelity_formula(self):
        xx, yy, zz = 1.0, -1.0, 1.0
        fidelity = (1 + xx - yy + zz) / 4
        self.assertEqual(fidelity, 1.0)

    def test_fidelity_standard_error_formula(self):
        se_xx, se_yy, se_zz = 0.01, 0.02, 0.03
        se_f = math.sqrt(se_xx**2 + se_yy**2 + se_zz**2) / 4
        self.assertAlmostEqual(se_f, math.sqrt(0.0014) / 4)

    def test_required_columns_are_unique_and_present(self):
        required = {
            "pair_role", "pair_q0", "pair_q1", "pair_distance", "condition", "shots", "cx",
            "XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se", "fidelity", "fidelity_se",
        }
        self.assertTrue(required.issubset(set(CSV_FIELDS)))
        self.assertEqual(len(CSV_FIELDS), len(set(CSV_FIELDS)))

    def test_csv_writer_rejects_missing_experiment_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "exactly four"):
                write_csv([], Path(tmp) / "bell.csv")

    def test_csv_writer_writes_four_completed_rows(self):
        rows = []
        for pair_role, q0, q1 in [("adjacent", 0, 1), ("farthest", 0, 3)]:
            for condition in ("ideal", "noisy"):
                row = {field: 0 for field in CSV_FIELDS}
                row.update({"processor": "test fixture", "pair_role": pair_role,
                            "pair_q0": q0, "pair_q1": q1, "pair_distance": 1 if pair_role == "adjacent" else 3,
                            "condition": condition, "shots": 4096, "XX": 1.0, "YY": -1.0, "ZZ": 1.0,
                            "XX_se": 0.0, "YY_se": 0.0, "ZZ_se": 0.0, "fidelity": 1.0, "fidelity_se": 0.0})
                rows.append(row)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(rows, Path(tmp) / "bell.csv")
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, CSV_FIELDS)
                read_rows = list(reader)
            self.assertEqual(len(read_rows), 4)


class MockedRunnerTests(unittest.TestCase):
    """Runner contract tests using mocked official API; these are NOT simulations."""

    def setUp(self):
        # Synthetic test fixture only; not a Processor D proposal or benchmark result.
        self.processor = {
            "name": "MOCK-ONLY TEST FIXTURE",
            "num_qubits": 6,
            "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)],
        }
        self.validate = Mock(return_value=[])
        self.load = Mock(return_value=self.processor)
        self.experiment = Mock(side_effect=self.fake_experiment)
        self.api = (REQUIRED_SHOTS, self.experiment, self.load, self.validate)

    def fake_experiment(self, processor, pair, noisy, shots):
        # Deterministic placeholder values used only to test wiring and row assembly.
        # They must never be interpreted as simulated measurements.
        distance = graph_distances(processor["num_qubits"], processor["edges"], pair[0])[pair[1]]
        return {
            "processor": processor["name"], "pair": pair, "noisy": noisy,
            "shots": shots, "pair_distance": distance, "cx": 2 if distance == 1 else 6,
            "XX": 0.99, "XX_se": 0.01, "YY": -0.98, "YY_se": 0.02,
            "ZZ": 0.97, "ZZ_se": 0.03, "fidelity": 0.985, "fidelity_se": 0.01,
        }

    def test_build_rows_calls_official_api_four_times_at_required_shots(self):
        with patch("bell_experiments._official_api", return_value=self.api):
            rows = build_rows(self.processor)
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            [(r["pair_role"], r["condition"]) for r in rows],
            [("adjacent", "ideal"), ("adjacent", "noisy"),
             ("farthest", "ideal"), ("farthest", "noisy")],
        )
        self.assertEqual(self.experiment.call_count, 4)
        self.assertTrue(all(c.kwargs["shots"] == 4096 for c in self.experiment.call_args_list))
        self.assertEqual(
            [(c.args[1], c.args[2]) for c in self.experiment.call_args_list],
            [((0, 1), False), ((0, 1), True), ((0, 3), False), ((0, 3), True)],
        )
        self.assertTrue(all(r["shots"] == 4096 for r in rows))
        self.assertTrue(all(r["processor"] == "MOCK-ONLY TEST FIXTURE" for r in rows))

    def test_build_rows_rejects_nonofficial_shot_count_before_running(self):
        with patch("bell_experiments._official_api", return_value=self.api):
            with self.assertRaisesRegex(ValueError, "exactly 4096 shots"):
                build_rows(self.processor, shots=100)
        self.experiment.assert_not_called()

    def test_invalid_processor_is_rejected_before_experiment_calls(self):
        self.validate.return_value = ["synthetic validation failure"]
        with patch("bell_experiments._official_api", return_value=self.api):
            with self.assertRaisesRegex(ValueError, "synthetic validation failure"):
                build_rows(self.processor)
        self.experiment.assert_not_called()

    def test_failed_experiment_does_not_write_partial_csv(self):
        failing_experiment = Mock(side_effect=[self.fake_experiment(self.processor, (0, 1), False, 4096),
                                               RuntimeError("mock failure")])
        failing_api = (REQUIRED_SHOTS, failing_experiment, self.load, self.validate)
        with tempfile.TemporaryDirectory() as tmp:
            processor_path = Path(tmp) / "processor_D.json"
            processor_path.write_text("{}", encoding="utf-8")
            output_path = Path(tmp) / "results" / "tables" / "bell.csv"
            with patch("bell_experiments._official_api", return_value=failing_api):
                with self.assertRaisesRegex(RuntimeError, "mock failure"):
                    run(processor_path, output_path)
            self.assertFalse(output_path.exists())

    def test_csv_writer_rejects_missing_required_metrics(self):
        rows = [{field: 0 for field in CSV_FIELDS} for _ in range(4)]
        del rows[0]["fidelity"]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "missing required CSV fields"):
                write_csv(rows, Path(tmp) / "bell.csv")

    def _valid_rows_for_writer(self):
        rows = []
        for role, q0, q1 in (("adjacent", 0, 1), ("farthest", 0, 3)):
            for condition in ("ideal", "noisy"):
                row = {field: 0 for field in CSV_FIELDS}
                row.update({"processor": "test fixture", "pair_role": role, "pair_q0": q0, "pair_q1": q1,
                            "pair_distance": 1 if role == "adjacent" else 3, "condition": condition,
                            "shots": 4096, "XX": 1.0, "YY": -1.0, "ZZ": 1.0,
                            "fidelity": 1.0, "fidelity_se": 0.0})
                rows.append(row)
        return rows

    def test_csv_writer_rejects_inconsistent_fidelity(self):
        rows = self._valid_rows_for_writer()
        rows[0]["fidelity"] = 0.25
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "fidelity does not match"):
                write_csv(rows, Path(tmp) / "bell.csv")

    def test_csv_writer_rejects_nonfinite_metrics(self):
        rows = self._valid_rows_for_writer()
        rows[0]["XX"] = float("nan")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "must be finite"):
                write_csv(rows, Path(tmp) / "bell.csv")

    def test_csv_writer_rejects_negative_standard_error(self):
        rows = self._valid_rows_for_writer()
        rows[0]["XX_se"] = -0.1
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "standard errors cannot be negative"):
                write_csv(rows, Path(tmp) / "bell.csv")


if __name__ == "__main__":
    unittest.main(verbosity=2)
