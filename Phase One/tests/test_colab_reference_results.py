"""Validate saved, measured three-topology B benchmarks without needing Qiskit."""
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestMeasuredReferenceResults(unittest.TestCase):
    def test_three_topologies_match_csv_and_raw_counts(self):
        location = ROOT / 'results/reference_b_comparison'
        raw = json.loads((location / 'full_six_b_topology_comparison.json').read_text())
        with (location / 'full_six_b_topology_comparison.csv').open() as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(raw['status'], 'MEASURED_AFTER_EXECUTION')
        self.assertEqual(len(rows), 3)
        self.assertEqual(set(raw['comparisons']), {r['configuration'] for r in rows})
        from src.problem import cut_score
        for row in rows:
            key = row['configuration']
            record = raw['comparisons'][key]
            metric = record['metrics']
            counts = record['counts_msb_first']
            self.assertEqual(sum(counts.values()), 4096)
            self.assertEqual(metric['physical_qubits_available'], 9)
            self.assertEqual(metric['logical_qubits'], 6)
            self.assertEqual(len(record['configuration']['coupling_map']), metric['coupling_edges'])
            scorer = lambda b: cut_score(tuple((int(b.replace(' ', ''), 2) >> k) & 1 for k in range(6)))
            expected = sum(scorer(bitstring) * count for bitstring, count in counts.items()) / 4096
            self.assertAlmostEqual(expected, metric['noisy_expected_cut'])
            self.assertEqual(sum(n for b,n in counts.items() if scorer(b)==16), metric['optimal_shots'])
            self.assertAlmostEqual(float(row['noisy_expected_cut']), metric['noisy_expected_cut'])
            self.assertEqual(int(row['native_cx']), metric['native_cx'])
            self.assertTrue((location / f'{key}_compiled.txt').exists())

if __name__ == '__main__':
    unittest.main()
