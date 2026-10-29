from scripts.verify_qubo import verify

def test_qubo_all_assignments():
    certificate=verify()
    assert certificate['tested_assignments']==64
    assert certificate['all_assignments_match_cut_score']
    assert certificate['classical_optimum']==16
