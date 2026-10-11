"""Generate the participant-defined Processor A JSON specification."""
import json
from pathlib import Path

def build_processor():
    return {'name': 'Processor A', 'num_qubits': 5, 'topology': 'five-node branching topology', 'coupling_map': [[0, 1], [0, 2], [0, 3], [3, 4]], 'coupling_bidirectional': True, 'basis_gates': ['rz', 'sx', 'x', 'cx'], 'noise': {'single_qubit_depolarizing': 0.001, 'two_qubit_depolarizing': 0.01}, 'source': 'Participant-defined model interpreted from organiser slide; synthetic noise; numbering assigned by participant', 'assumptions': 'All couplings bidirectional; identical uniform gate noise on both processors; no readout error'}

def write_json(path=None):
    output = Path(path) if path else Path(__file__).with_suffix('.json')
    output.write_text(json.dumps(build_processor(), indent=2) + "\n", encoding='utf-8')
    return output

if __name__ == '__main__':
    print(write_json())
