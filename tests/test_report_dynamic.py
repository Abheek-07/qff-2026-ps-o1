from pathlib import Path
import unittest

class DynamicReportTests(unittest.TestCase):
    def test_results_not_hardcoded(self):
        src=(Path(__file__).resolve().parents[1]/'src/finalize_report.py').read_text()
        self.assertNotIn('11.662109',src)
        self.assertNotIn('11.978903',src)
        self.assertIn("d['processor_B']",src)
    def test_six_qubit_metrics_exported(self):
        src=(Path(__file__).resolve().parents[1]/'src/full_six_reference.py').read_text()
        for key in ('ideal_optimal_bitstring_probability','noisy_optimal_bitstring_shots','best_observed_cut','optimizer_restarts','routing_diagnostic_swaps'):
            self.assertIn(key,src)
