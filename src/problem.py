"""Deterministic six-vertex weighted Max-Cut and exact 5-qubit gauge-fixed p=1 QAOA.

Fixing vertex 0 to 0 exactly preserves all attainable Max-Cut costs and the
classical optimum because C(x)=C(1-x). This reduced *ansatz* need not match a
six-qubit QAOA ansatz's full distribution; the reduction must be disclosed.
"""
import itertools
import random
import numpy as np
import networkx as nx

N_VERTICES = 6
N_LOGICAL = 5
GRAPH_SEED = 42
WEIGHT_SEED = 42


def weighted_graph():
    g = nx.erdos_renyi_graph(n=6, p=0.5, seed=GRAPH_SEED)
    rng = random.Random(WEIGHT_SEED)
    for u, v in sorted(g.edges()):
        g[u][v]['weight'] = rng.randint(1, 5)
    return g


def edges(g=None):
    g = g if g is not None else weighted_graph()
    return [(int(u), int(v), int(d['weight'])) for u, v, d in sorted(g.edges(data=True))]


def cut_score(bits, e=None):
    if len(bits) != 6:
        raise ValueError('Original graph uses six bits (including fixed vertex 0)')
    if e is None: e = edges()
    return sum(w for u,v,w in e if int(bits[u]) != int(bits[v]))


def exact_optimum(e=None):
    if e is None: e = edges()
    scored = [(cut_score(bits,e),bits) for bits in itertools.product((0,1),repeat=6)]
    score=max(x for x,_ in scored)
    return score, [bits for value,bits in scored if value==score]


def bits_from_index(index):
    """Little-endian logical qubits q0..q4 represent vertices 1..5."""
    return (0,)+tuple((index>>i)&1 for i in range(5))


def cost_array(e=None):
    if e is None: e=edges()
    return np.array([cut_score(bits_from_index(i),e) for i in range(32)],dtype=float)


def ideal_state(gamma,beta,e=None):
    """Independent NumPy statevector calculation: |+>^5, exp(-i gamma C), exp(-i beta sum X)."""
    amplitudes = np.exp(-1j*gamma*cost_array(e))/np.sqrt(32)
    c,s = np.cos(beta),np.sin(beta)
    for q in range(5):
        new = amplitudes.copy()
        for i in range(32):
            if not (i & (1<<q)):
                j=i^(1<<q)
                new[i] = c*amplitudes[i]-1j*s*amplitudes[j]
                new[j] = c*amplitudes[j]-1j*s*amplitudes[i]
        amplitudes=new
    return amplitudes


def ideal_expected_cut(gamma,beta,e=None):
    amplitudes=ideal_state(gamma,beta,e)
    return float(np.dot(np.abs(amplitudes)**2,cost_array(e)))


def optimize_angles(e=None):
    from scipy.optimize import differential_evolution
    if e is None:e=edges()
    output=differential_evolution(
        lambda x:-ideal_expected_cut(x[0],x[1],e),
        bounds=[(0,2*np.pi),(0,np.pi/2)],
        seed=42,maxiter=45,popsize=10,tol=1e-6,polish=True,workers=1)
    gamma,beta=map(float,output.x)
    return gamma,beta,float(-output.fun)


def qaoa_circuit(gamma,beta,e=None):
    from qiskit import QuantumCircuit
    if e is None:e=edges()
    qc=QuantumCircuit(N_LOGICAL,name='six_vertex_reduced_QAOA_p1')
    qc.h(range(N_LOGICAL))
    for u,v,w in e:
        if u==0:
            qc.rz(-gamma*w,v-1)
        elif v==0:
            qc.rz(-gamma*w,u-1)
        else:
            qc.rzz(-gamma*w,u-1,v-1)
    for i in range(N_LOGICAL):qc.rx(2*beta,i)
    return qc


def measured_circuit(gamma,beta,e=None):
    qc=qaoa_circuit(gamma,beta,e)
    qc.add_register(__import__('qiskit').ClassicalRegister(N_LOGICAL,'readout'))
    for i in range(N_LOGICAL):qc.measure(i,i)
    return qc


def score_counts(counts,e=None):
    if e is None:e=edges()
    total=sum(counts.values())
    if not total:raise ValueError('No measurement shots')
    weighted=0
    for text,n in counts.items():
        cleaned=text.replace(' ','')
        if len(cleaned)!=5:raise ValueError(f'Expected five measured logical bits, got {text!r}')
        index=int(cleaned,2)
        weighted+=n*cut_score(bits_from_index(index),e)
    return weighted/total


def verify_reduction(e=None):
    if e is None:e=edges()
    optimum,_=exact_optimum(e)
    for bs in itertools.product((0,1),repeat=6):
        assert cut_score(bs,e)==cut_score(tuple(1-x for x in bs),e)
    assert max(cut_score((0,)+bs,e) for bs in itertools.product((0,1),repeat=5))==optimum
    assert len(e)==9 and optimum==16, (len(e),optimum)
    assert np.isclose(np.linalg.norm(ideal_state(.7,.4,e)),1,atol=1e-12)
    assert np.isclose(ideal_expected_cut(0,0,e),sum(w for _,_,w in e)/2,atol=1e-10)
    return optimum
