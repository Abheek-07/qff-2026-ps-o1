"""Optional Phase-1 architecture benchmark: exact same FULL six-logical-qubit QAOA on two nine-qubit B graphs.

Run from repository root: python scripts/compare_full_six_b_topologies.py
Requires Qiskit/Aer dependencies from requirements.txt. Does NOT overwrite any
existing experiment, figure, or original full-six-qubit result. Outputs only to
results/reference_b_comparison/. The historical eight-edge case is deliberately
not treated as the official twelve-edge reference.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.problem import cut_score, exact_optimum
from src.full_six_reference import full_qaoa

BASE = ROOT / 'results' / 'full_six_qubit_reference.json'
CONFIGS = {
    'official_12edge_B': ROOT / 'processors' / 'processor_B_official_12edge_reference.json',
    'participant_12edge_B': ROOT / 'processors' / 'processor_B.json',
    'historical_8edge_B': ROOT / 'processors' / 'processor_B_kit_reference.json',
}
OUT = ROOT / 'results' / 'reference_b_comparison'
BASIS = ['rz', 'sx', 'x', 'cx']
SHOTS = 4096
SEED = 42


def validate_config(config):
    import networkx as nx
    assert config['num_qubits'] == 9, 'Processor B must have nine physical qubits'
    assert config['basis_gates'] == BASIS
    edges = config['coupling_map']
    assert len({tuple(sorted(x)) for x in edges}) == len(edges)
    assert all(0 <= u < 9 and 0 <= v < 9 and u != v for u,v in edges)
    g = nx.Graph(); g.add_nodes_from(range(9)); g.add_edges_from(edges)
    assert nx.is_connected(g), 'Processor model must be connected'
    return edges


def score_bitstring(value):
    i = int(value.replace(' ', ''), 2)
    return cut_score(tuple((i >> j) & 1 for j in range(6)))


def run_one(label, config, angles, noise):
    from qiskit import transpile
    from qiskit.transpiler import CouplingMap
    from qiskit_aer import AerSimulator
    edges = validate_config(config)
    cmap = CouplingMap(couplinglist=[(u,v) for u,v in edges] + [(v,u) for u,v in edges])
    circuit = full_qaoa(*angles, measure=True)
    compiled = transpile(circuit, basis_gates=BASIS, coupling_map=cmap,
                         optimization_level=1, seed_transpiler=SEED)
    unrestricted = transpile(circuit, basis_gates=BASIS,
                            optimization_level=1, seed_transpiler=SEED)
    diagnostic = transpile(circuit, basis_gates=BASIS + ['swap'], coupling_map=cmap,
                          optimization_level=1, seed_transpiler=SEED)
    counts = AerSimulator(noise_model=noise, seed_simulator=SEED).run(compiled, shots=SHOTS).result().get_counts()
    assert sum(counts.values()) == SHOTS
    assert all(len(k.replace(' ', '')) == 6 for k in counts)
    best, _ = exact_optimum()
    mean = sum(score_bitstring(k) * n for k,n in counts.items()) / SHOTS
    optimal_shots = sum(n for k,n in counts.items() if score_bitstring(k) == best)
    row = {
        'configuration':label,'physical_qubits_available':9,
        'logical_qubits':6,'coupling_edges':len(edges),
        'native_depth':compiled.depth(),
        'native_cx':int(compiled.count_ops().get('cx',0)),
        'native_explicit_swaps':int(compiled.count_ops().get('swap',0)),
        'diagnostic_swaps':int(diagnostic.count_ops().get('swap',0)),
        'unrestricted_native_cx':int(unrestricted.count_ops().get('cx',0)),
        'extra_cx_vs_unrestricted':int(compiled.count_ops().get('cx',0)) - int(unrestricted.count_ops().get('cx',0)),
        'shots':SHOTS,'best_observed_cut':max(score_bitstring(k) for k in counts),
        'noisy_expected_cut':mean,'approximation_ratio':mean/best,
        'optimal_shots':optimal_shots,'optimal_probability':optimal_shots/SHOTS,
    }
    return row, counts, compiled


def main():
    from src.processors import noise_model
    original = json.loads(BASE.read_text(encoding='utf-8'))
    angles = (original['gamma'], original['beta'])
    rows = []
    payload = {'status':'MEASURED_AFTER_EXECUTION', 'graph_vertices':6,
               'logical_qubits':6, 'gamma':angles[0], 'beta':angles[1],
               'shots':SHOTS,'seed_transpiler':SEED,'seed_simulator':SEED,
               'optimization_level':1,'noise_type':'uniform synthetic',
               'comparisons':{}}
    # Stage output in memory; write ONLY after all three cases finish successfully.
    for name, path in CONFIGS.items():
        spec = json.loads(path.read_text(encoding='utf-8'))
        row, counts, compiled = run_one(name, spec, angles, noise_model(spec))
        rows.append(row)
        payload['comparisons'][name] = {'configuration':spec,'metrics':row,
                                        'counts_msb_first':dict(sorted(counts.items()))}
        payload['comparisons'][name]['compiled_circuit_text'] = str(compiled.draw(output='text'))
        print(name, 'depth', row['native_depth'], 'CX', row['native_cx'],
              'noisy cut', f"{row['noisy_expected_cut']:.6f}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'full_six_b_topology_comparison.json').write_text(json.dumps(payload,indent=2), encoding='utf-8')
    with (OUT/'full_six_b_topology_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    for name, item in payload['comparisons'].items():
        (OUT/(name+'_compiled.txt')).write_text(item['compiled_circuit_text'],encoding='utf-8')
    print('Measured comparison saved to', OUT)
    print('NOTE: These results are a FULL-SIX B-vs-B topology comparison, NOT a full-six Processor A/B benchmark.')

if __name__ == '__main__':
    main()
