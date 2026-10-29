"""Phase 2 PS-O1 p=1 QAOA: circuit builder and ideal optimisation.
Run from this folder after installing Qiskit + SciPy:
    python qaoa_step2.py
The organisers' locked data is loaded unchanged.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

INSTANCE = json.loads((Path(__file__).parent / 'data' / 'instances.json').read_text())['PS-O1']
N = INSTANCE['num_vertices']
EDGES = [tuple(row) for row in INSTANCE['weighted_edges']]


def cut_value(bits):
    """bits are ordered x0,x1,...,x5 (not Qiskit printed bitstring order)."""
    return sum(w for i,j,w in EDGES if bits[i] != bits[j])


def qaoa_circuit(gamma, beta, measure=False):
    """Cost phase e^{-i gamma H_C}, H_C=sum w(1-Z_i Z_j)/2;
    mixer e^{-i beta H_M}, H_M=sum X_i.
    The global phase in the cost term is physically irrelevant.
    """
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for i,j,w in EDGES:
        qc.cx(i,j)
        qc.rz(-gamma*w, j)  # equivalent to e^{-i gamma*w*(I-ZZ)/2}, up to global phase
        qc.cx(i,j)
    for q in range(N):
        qc.rx(2*beta,q)
    if measure:
        qc.measure_all()
    return qc


def probabilities(gamma,beta):
    state=Statevector.from_instruction(qaoa_circuit(gamma,beta))
    return state.probabilities()


def expected_cut(params):
    p=probabilities(*params)
    return float(sum(prob*cut_value(tuple((idx>>i)&1 for i in range(N)))
                     for idx,prob in enumerate(p)))


def optimize_five_starts():
    records=[]
    for seed in INSTANCE['initialization_seeds']:
        initial=np.random.default_rng(seed).uniform(0, np.pi, 2)
        # Powell supports bounded gamma, beta and is derivative-free.
        result=minimize(lambda x:-expected_cut(x), initial, method='Powell',
                        bounds=[(0,np.pi),(0,np.pi)],
                        options={'maxiter':150, 'xtol':1e-6,'ftol':1e-8})
        records.append({'seed':seed,'initial_gamma':float(initial[0]),
                        'initial_beta':float(initial[1]),'gamma':float(result.x[0]),
                        'beta':float(result.x[1]),'expected_cut':float(-result.fun),
                        'optimizer_success':bool(result.success)})
    return records


if __name__=='__main__':
    all_cuts=[cut_value([(k>>i)&1 for i in range(N)]) for k in range(2**N)]
    assert max(all_cuts)==22 and sum(w for *_,w in EDGES)==27
    records=optimize_five_starts()
    best=max(records,key=lambda r:r['expected_cut'])
    target=Path('results/tables');target.mkdir(parents=True,exist_ok=True)
    import csv
    with (target/'qaoa_five_starts.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
    print(json.dumps({'best':best,'all_starts':records},indent=2))
    print('Next: compare SAME best gamma,beta on B and D, ideal/noisy, using official qff_phase2.py')
