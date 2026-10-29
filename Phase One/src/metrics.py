"""Native circuit resource counts and sampled/max-cut metrics."""
from .problem import score_counts

def resources(compiled):
    operations=compiled.count_ops()
    return {
        'depth':int(compiled.depth()),
        'cx_count':int(operations.get('cx',0)),
        'explicit_swap_count':int(operations.get('swap',0)),
        'single_qubit_gate_count':int(sum(operations.get(x,0) for x in ('rz','sx','x'))),
        'total_operations':int(sum(operations.values())),
        'compiled_physical_qubits':int(compiled.num_qubits),
    }
