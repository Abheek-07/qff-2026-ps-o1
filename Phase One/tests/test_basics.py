"""Tests that run WITHOUT Qiskit, to validate the mathematical instance and configs."""
import unittest,json
from pathlib import Path
import numpy as np
from src.problem import edges,exact_optimum,verify_reduction,ideal_state,ideal_expected_cut,cut_score,bits_from_index
from src.processors import processor_spec,validate,load

class TestPSO1(unittest.TestCase):
    def test_graph(self):
        self.assertEqual(len(edges()),9)
        self.assertEqual(exact_optimum()[0],16)
        self.assertEqual(verify_reduction(),16)
        self.assertTrue(all(1<=w<=5 for _,_,w in edges()))
    def test_probability(self):
        self.assertAlmostEqual(np.linalg.norm(ideal_state(.7,.4)),1)
        self.assertTrue(0<=ideal_expected_cut(.7,.4)<=16)
    def test_device(self):
        for name in ['A','B']:
            spec=processor_spec(name)
            self.assertTrue(validate(spec))
            self.assertEqual(load(name),spec)
    def test_complement_and_measure_order(self):
        self.assertEqual(bits_from_index(1),(0,1,0,0,0,0))
        self.assertEqual(cut_score((0,0,1,0,1,1)),16)

if __name__=='__main__':unittest.main()
