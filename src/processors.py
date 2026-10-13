"""Device configurations, checks, Qiskit coupling graphs, and uniform synthetic noise."""
from pathlib import Path
import json
import networkx as nx

PROJECT_ROOT=Path(__file__).resolve().parents[1]
BASIS=['rz','sx','x','cx']
NOISE={'single_qubit_depolarizing':0.001,
       'two_qubit_depolarizing':0.005,
       'readout_error':0.01}

A_EDGES=[[0,1],[0,2],[0,3],[3,4]]
B_EDGES=[[0,1],[0,3],[1,2],[1,4],[2,3],[2,4],[2,7],[2,8],[4,5],[4,7],[5,6],[6,7]]

def processor_spec(name):
    if name not in ('A','B'):raise ValueError(name)
    return {
        'name':f'Processor {name}', 'num_qubits':5 if name=='A' else 9,
        'topology':'5-node branching tree' if name=='A' else '9-node 12-edge connected mesh',
        'coupling_map':A_EDGES if name=='A' else B_EDGES,
        'coupling_bidirectional':True,'basis_gates':BASIS,
        'noise':NOISE,
        'model_type':'Participant-defined synthetic architecture, not calibrated IBM hardware',
        'source':'QFF 2026 Phase 1 Master Guide, page 2: participant-defined topology; gate/noise configuration is provisional pending organiser clarification',
        'design_rationale':(
            'Sparse branching tree with only four links, requiring multi-hop interactions.' if name=='A' else
            'Connected nine-qubit graph with multiple alternate routes and twelve couplings; extra qubits may be routing ancillas.'
        ),
    }

def load(name):
    return json.loads((PROJECT_ROOT/'processors'/f'processor_{name}.json').read_text(encoding='utf8'))

def validate(config):
    n=config['num_qubits']
    assert n in (5,9)
    assert config['basis_gates']==BASIS
    assert config['noise']==NOISE
    g=nx.Graph()
    g.add_nodes_from(range(n));g.add_edges_from(config['coupling_map'])
    assert all(0<=u<n and 0<=v<n and u!=v for u,v in config['coupling_map'])
    assert len(set(tuple(sorted(e)) for e in config['coupling_map']))==len(config['coupling_map'])
    assert nx.is_connected(g)
    return g

def coupling(config):
    from qiskit.transpiler import CouplingMap
    pairs=[(u,v) for u,v in config['coupling_map']]
    return CouplingMap(pairs+[(v,u) for u,v in pairs])

def noise_model(config):
    from qiskit_aer.noise import NoiseModel,depolarizing_error,ReadoutError
    p=config['noise']
    noise=NoiseModel()
    # Synthetic uniform gate noise, INCLUDING rz (in contrast to virtual-rz hardware assumptions).
    noise.add_all_qubit_quantum_error(depolarizing_error(p['single_qubit_depolarizing'],1),['rz','sx','x'])
    noise.add_all_qubit_quantum_error(depolarizing_error(p['two_qubit_depolarizing'],2),['cx'])
    r=p['readout_error']
    noise.add_all_qubit_readout_error(ReadoutError([[1-r,r],[r,1-r]]))
    return noise
