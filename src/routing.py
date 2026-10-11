"""Compile the same logical measured circuit for either physical architecture."""
from qiskit import transpile
from .processors import coupling

def compile_circuit(circuit, config, layout=None, seed=42):
    if layout is None: layout=list(range(circuit.num_clbits))
    return transpile(circuit, coupling_map=coupling(config), basis_gates=config['basis_gates'], initial_layout=layout, optimization_level=0, seed_transpiler=seed)
