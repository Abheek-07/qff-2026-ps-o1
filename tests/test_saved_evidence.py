"""Independent checks of submitted evidence; no Qiskit installation required.

These tests verify the data in the uploaded project ZIP, but do not substitute for
rerunning Qiskit/Aer or a real processor. They exercise a fresh NumPy statevector,
not the Qiskit implementation used to create the JSON.
"""
from pathlib import Path
import json
import unittest
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def cut(index, edges):
    return sum(w for u,v,w in edges if ((index >> u) & 1) != ((index >> v) & 1))


class SavedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = [(edge['u'],edge['v'],edge['weight']) for edge in json.loads((ROOT/'data/weighted_graph.json').read_text())['edges']]
        cls.ref = json.loads((ROOT/'results/full_six_qubit_reference.json').read_text())
        cls.values = np.array([cut(i,cls.e) for i in range(64)],dtype=float)

    def test_graph_and_full_six_classical_optimum(self):
        self.assertEqual(len(self.e),9)
        self.assertEqual(int(self.values.max()),16)
        self.assertEqual(int(np.sum(self.values==16)),2)
        self.assertEqual(set(self.values),set(np.array(self.values,dtype=int)))
        self.assertEqual(self.ref['optimum'],16)

    def test_full_six_statevector_independent(self):
        gamma, beta = self.ref['gamma'],self.ref['beta']
        amplitudes = np.exp(-1j*gamma*self.values)/8.0
        c,s=np.cos(beta),np.sin(beta)
        for q in range(6):
            updated=amplitudes.copy()
            for i in range(64):
                if i&(1<<q): continue
                j=i^(1<<q)
                updated[i]=c*amplitudes[i]-1j*s*amplitudes[j]
                updated[j]=c*amplitudes[j]-1j*s*amplitudes[i]
            amplitudes=updated
        p=np.abs(amplitudes)**2
        self.assertAlmostEqual(float(p.sum()),1.0,places=12)
        self.assertAlmostEqual(float(p@self.values),self.ref['ideal_expected_cut'],places=10)
        self.assertAlmostEqual(float(p[self.values==16].sum()),self.ref['ideal_optimal_bitstring_probability'],places=10)

    def test_full_six_noisy_shots_and_scores(self):
        d=self.ref
        counts={int(bits,2):n for bits,n in d['counts_bitstring_msb_first'].items()}
        self.assertEqual(sum(counts.values()),d['shots'])
        mean=sum(self.values[i]*n for i,n in counts.items())/d['shots']
        successes=sum(n for i,n in counts.items() if self.values[i]==16)
        self.assertAlmostEqual(mean,d['processor_B']['noisy_cut'],places=12)
        self.assertAlmostEqual(mean/16,d['processor_B']['approximation_ratio'],places=12)
        self.assertEqual(successes,d['noisy_optimal_bitstring_shots'])
        self.assertAlmostEqual(successes/d['shots'],d['noisy_optimal_bitstring_probability'],places=12)
        self.assertEqual(int(max(self.values[i] for i,n in counts.items() if n)),d['best_observed_cut'])

    def test_reduced_summaries_match_trials(self):
        trials=pd.read_csv(ROOT/'results/tables/noisy_trials.csv')
        summary=pd.read_csv(ROOT/'results/tables/noisy_summary.csv')
        for proc in ('A','B'):
            block=trials[trials.processor==proc]
            recorded=summary[summary.processor==proc].iloc[0]
            self.assertEqual(len(block),5)
            self.assertTrue((block.shots==4096).all())
            self.assertAlmostEqual(float(block.weighted_cut.mean()),float(recorded.mean_cut),places=7)
            self.assertAlmostEqual(float(block.weighted_cut.std(ddof=1)/np.sqrt(5)),float(recorded.standard_error),places=7)
            self.assertAlmostEqual(float(recorded.mean_cut/16),float(recorded.approximation_ratio),places=7)

    def test_report_and_result_scope(self):
        r=(ROOT/'report.md').read_text()
        d=(ROOT/'docs/processor_d_proposal.md').read_text().strip()
        self.assertEqual(r.count('## 7. Processor D concept proposal'),1)
        self.assertIn(d,r)
        self.assertIn('QUBO',r)
        self.assertNotIn('## 7. Future architecture ideas',r)
        for stale in ('layout_comparison.csv','processor_depth.png','processor_cx.png','noisy_mean_cut.png'):
            self.assertFalse(any(p.name==stale for p in (ROOT/'results').rglob('*')))


class RegenerationTests(unittest.TestCase):
    def test_reduced_report_builder_keeps_processor_d(self):
        import shutil
        import tempfile
        from unittest.mock import patch
        from run_experiment import write_summary_report
        from src.processors import load
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)
            (dest/'docs').mkdir()
            (dest/'results').mkdir()
            shutil.copyfile(ROOT/'docs/processor_d_proposal.md',dest/'docs/processor_d_proposal.md')
            frame=pd.read_csv(ROOT/'results/tables/processor_comparison.csv')
            summary=pd.read_csv(ROOT/'results/tables/noisy_summary.csv')
            meta=json.loads((ROOT/'results/experiment_metadata.json').read_text())
            with patch('run_experiment.ROOT', dest):
                write_summary_report({'A':load('A'),'B':load('B')},
                    meta['optimized_angles']['gamma'],meta['optimized_angles']['beta'],
                    16,meta['ideal_expected_cut'],frame,summary,
                    meta['unrestricted_compilation_reference'])
            out=(dest/'report.md').read_text()
            self.assertIn((dest/'docs/processor_d_proposal.md').read_text().strip(),out)
            self.assertIn('x_i ∈ {0,1}',out)
            self.assertNotIn('Future architecture ideas',out)

if __name__=='__main__': unittest.main()
