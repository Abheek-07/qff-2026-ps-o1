"""Non-Qiskit assertions of the organizer reference topology and experiment isolation."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OFFICIAL={(0,1),(1,2),(1,6),(2,3),(2,6),(2,5),(3,4),(4,5),(5,6),(6,7),(6,8),(0,8)}


def test_official_twelve_edge_reference():
    obj=json.loads((ROOT/'processors'/'processor_B_official_12edge_reference.json').read_text())
    assert obj['num_qubits']==9
    assert {tuple(sorted(x)) for x in obj['coupling_map']}==OFFICIAL
    assert obj['basis_gates']==['rz','sx','x','cx']
    assert obj['noise']=={'single_qubit_depolarizing':.001,'two_qubit_depolarizing':.005,'readout_error':.01}


def test_participant_topology_is_not_misrepresented_as_official():
    obj=json.loads((ROOT/'processors'/'processor_B.json').read_text())
    assert obj['num_qubits']==9
    assert {tuple(sorted(x)) for x in obj['coupling_map']} != OFFICIAL


def test_existing_measurements_keep_historical_topology():
    data=json.loads((ROOT/'results'/'full_six_qubit_reference.json').read_text())
    assert len(data['processor_B']['coupling_edges'])==8
    assert len(data['processor_B']['coupling_edges'])!=len(OFFICIAL)


def test_comparison_is_non_destructive():
    p=(ROOT/'scripts'/'compare_full_six_b_topologies.py').read_text()
    assert "reference_b_comparison" in p
    assert "'full_six_qubit_reference.json'" in p
    assert "write_text(json.dumps(payload" in p
