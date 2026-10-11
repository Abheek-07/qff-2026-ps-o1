"""Resource counts and sampled objective metrics."""
from .problem import expected_score, optimum

def resources(circuit):
    ops=circuit.count_ops()
    return {'depth':int(circuit.depth()),'cx_gates':int(ops.get('cx',0)),'explicit_swaps':int(ops.get('swap',0)),'total_gates':int(sum(ops.values()))}

def summarize_counts(counts):
    mean=expected_score(counts)
    return {'mean_cut':mean,'approximation_ratio':mean/optimum()}
