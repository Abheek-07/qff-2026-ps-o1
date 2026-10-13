"""Unreduced six-qubit p=1 QAOA reference for PS-O1. NO run results are asserted.

Invoke in Colab: python -m src.full_six_reference
Prints exact-classical and ideal-statevector benchmark, then compiles/simulates
on a specified 9-qubit B topology using provisional synthetic noise.
This is distinct from the five-qubit exploratory A/B experiment.
"""
from .problem import edges, exact_optimum, cut_score
import numpy as np

# Load a separately documented topology: the exploratory processor_B.json is different.
import json
from pathlib import Path
KIT_B_EDGES=[tuple(pair) for pair in json.loads((Path(__file__).resolve().parents[1]/'processors'/'processor_B_kit_reference.json').read_text())['coupling_map']]

def full_qaoa(gamma,beta,measure=False):
    from qiskit import QuantumCircuit
    q=QuantumCircuit(6, 6 if measure else 0)
    q.h(range(6))
    for u,v,w in edges():
        q.rzz(-gamma*w,u,v)
    for i in range(6): q.rx(2*beta,i)
    if measure: q.measure(range(6),range(6))
    return q

def objective(angles):
    from qiskit.quantum_info import Statevector
    q=full_qaoa(*angles)
    ps=Statevector.from_instruction(q).probabilities()
    values=np.array([cut_score(tuple((i>>j)&1 for j in range(6))) for i in range(64)])
    return float(np.dot(ps,values))

def main():
    from scipy.optimize import differential_evolution
    from qiskit import transpile
    from qiskit.transpiler import CouplingMap
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel,depolarizing_error,ReadoutError
    best, _=exact_optimum()
    fit=differential_evolution(lambda a:-objective(a),[(0,2*np.pi),(0,np.pi/2)],seed=42,maxiter=45,popsize=10,polish=True)
    ideal=objective(fit.x)
    print('Graph vertices: 6; logical qubits: 6; exact optimum:',best)
    print('Full six-qubit QAOA p=1 ideal expected cut:',round(ideal,6))
    print('Optimized gamma,beta:',fit.x.tolist())
    print('Full six-qubit QAOA is NOT directly executable on five-physical-qubit Processor A.')
    coupling=[pair for u,v in KIT_B_EDGES for pair in [(u,v),(v,u)]]
    measured=full_qaoa(*fit.x,measure=True)
    compiled=transpile(measured,basis_gates=['rz','sx','x','cx'],coupling_map=CouplingMap(couplinglist=coupling),optimization_level=1,seed_transpiler=42)
    nm=NoiseModel()
    for gate in ['rz','sx','x']: nm.add_all_qubit_quantum_error(depolarizing_error(.001,1),gate)
    nm.add_all_qubit_quantum_error(depolarizing_error(.005,2),'cx')
    nm.add_all_qubit_readout_error(ReadoutError([[.99,.01],[.01,.99]]))
    counts=AerSimulator(noise_model=nm,seed_simulator=42).run(compiled,shots=4096).result().get_counts()
    mean=sum(cut_score(tuple((int(k,2)>>j)&1 for j in range(6)))*n for k,n in counts.items())/4096
    print('Processor B topology: consolidated-kit eight-edge model (specified above)')
    print('Provisional noise: 1q=.001, CX=.005, readout=.01; not official/frozen')
    print('B native circuit depth:',compiled.depth(),'CX:',compiled.count_ops().get('cx',0))
    print('B measured mean weighted cut:',round(mean,6),'approximation ratio:',round(mean/best,6))
    import json
    from pathlib import Path
    out=Path(__file__).resolve().parents[1]/'results'/'full_six_qubit_reference.json'
    out.write_text(json.dumps({'status':'FULL_6Q_EXECUTED','graph_vertices':6,'logical_qubits':6,'optimum':best,'ideal_expected_cut':ideal,'gamma':float(fit.x[0]),'beta':float(fit.x[1]),'processor_B':{'physical_qubits':9,'coupling_edges':KIT_B_EDGES,'native_depth':compiled.depth(),'native_cx':int(compiled.count_ops().get('cx',0)),'noisy_cut':mean,'approximation_ratio':mean/best},'shots':4096,'noise_status':'PROVISIONAL_UNCONFIRMED'},indent=2))
    print('Reference output:',out)
if __name__=='__main__':main()
