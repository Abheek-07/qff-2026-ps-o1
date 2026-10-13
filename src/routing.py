"""Fixed-layout fair A/B transpilation and topology/routing diagnostics."""
import networkx as nx

def compile_for(circuit,config,allow_swap_diagnostic=False):
    from qiskit import transpile
    from .processors import coupling
    basis=list(config['basis_gates'])
    if allow_swap_diagnostic:
        # Swaps kept native here ONLY for analysis; not a valid hardware-basis circuit.
        basis+=['swap']
    return transpile(circuit,coupling_map=coupling(config),
        basis_gates=basis,initial_layout=list(range(5)),
        optimization_level=1,seed_transpiler=42)

def unrestricted_reference(circuit):
    from qiskit import transpile
    from .processors import BASIS
    return transpile(circuit,basis_gates=BASIS,optimization_level=1,seed_transpiler=42)

def topology_pressure(config,problem_edges):
    """Initial-layout proxy: sum(max(0, shortest_distance-1)), NOT a measured SWAP count."""
    g=nx.Graph()
    g.add_nodes_from(range(config['num_qubits']))
    g.add_edges_from(config['coupling_map'])
    distances=[]
    for u,v,w in problem_edges:
        if u>0 and v>0:
            d=nx.shortest_path_length(g,u-1,v-1)
            distances.append({'logical_edge':f'{u-1}-{v-1}','distance':d,'weight':w})
    return {
        'nonlocal_cost_edges':sum(item['distance']>1 for item in distances),
        'extra_hops_proxy':sum(max(0,item['distance']-1) for item in distances),
        'mean_problem_edge_distance':sum(item['distance'] for item in distances)/len(distances),
        'per_edge':distances,
    }
