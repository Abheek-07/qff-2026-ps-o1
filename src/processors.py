"""Load processor JSON definitions and construct bidirectional couplings."""
import json
from pathlib import Path
from qiskit.transpiler import CouplingMap

def load(name):
    path=Path(__file__).resolve().parents[1]/'processors'/f'processor_{name}.json'
    return json.loads(path.read_text())

def coupling(config):
    edges=[]
    for u,v in config['coupling_map']:
        edges.extend([(u,v),(v,u)])
    return CouplingMap(edges)
