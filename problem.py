"""Weighted Max-Cut problem and QAOA construction."""
import itertools
from qiskit import QuantumCircuit

EDGES = [(0,1,3),(0,2,2),(1,2,4),(1,3,5),(2,3,1)]
N = 4

def score(bits):
    return sum(w for u,v,w in EDGES if bits[u] != bits[v])

def optimum():
    return max(score(bits) for bits in itertools.product((0,1), repeat=N))

def qaoa(gamma,beta):
    qc=QuantumCircuit(N,N)
    qc.h(range(N))
    for u,v,w in EDGES:
        qc.rzz(-gamma*w,u,v)
    for q in range(N):
        qc.rx(2*beta,q)
    return qc

def measure(qc):
    result=qc.copy()
    for q in range(N):
        result.measure(q,q)
    return result

def expected_score(counts):
    total=sum(counts.values())
    return sum(score(tuple(int(bit) for bit in key.replace(' ','')[::-1][:N]))*freq for key,freq in counts.items())/total
