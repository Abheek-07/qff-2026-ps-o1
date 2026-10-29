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
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel,depolarizing_error,ReadoutError
    best, _=exact_optimum()
    fit=differential_evolution(lambda a:-objective(a),[(0,2*np.pi),(0,np.pi/2)],seed=42,maxiter=45,popsize=10,polish=True)
    ideal=objective(fit.x)
    # PS-O1 solution-quality metrics: all exact optima, ideal success probability.
    optimal_solutions=exact_optimum()[1]
    probabilities=Statevector.from_instruction(full_qaoa(*fit.x)).probabilities()
    decoded=lambda i: tuple((i>>j)&1 for j in range(6))
    ideal_success=float(sum(probabilities[i] for i in range(64) if cut_score(decoded(i))==best))
    # Repeat independent optimization searches; report all results, not just a single start.
    restart_rows=[{'seed':42,'gamma':float(fit.x[0]),'beta':float(fit.x[1]),'ideal_expected_cut':float(ideal)}]
    for seed in (43,44):
        trial=differential_evolution(lambda a:-objective(a),[(0,2*np.pi),(0,np.pi/2)],seed=seed,maxiter=45,popsize=10,polish=True)
        restart_rows.append({'seed':seed,'gamma':float(trial.x[0]),'beta':float(trial.x[1]),'ideal_expected_cut':float(-trial.fun)})

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
    success_shots=sum(n for k,n in counts.items() if cut_score(decoded(int(k.replace(' ',''),2)))==best)
    best_observed=max(cut_score(decoded(int(k.replace(' ',''),2))) for k,n in counts.items() if n)
    from qiskit.transpiler import CouplingMap
    unrestricted=transpile(measured,basis_gates=['rz','sx','x','cx'],optimization_level=1,seed_transpiler=42)
    diagnostic=transpile(measured,basis_gates=['rz','sx','x','cx','swap'],coupling_map=CouplingMap(couplinglist=coupling),optimization_level=1,seed_transpiler=42)

    mean=sum(cut_score(tuple((int(k,2)>>j)&1 for j in range(6)))*n for k,n in counts.items())/4096
    print('Processor B topology: consolidated-kit eight-edge model (specified above)')
    print('Provisional noise: 1q=.001, CX=.005, readout=.01; not official/frozen')
    print('B native circuit depth:',compiled.depth(),'CX:',compiled.count_ops().get('cx',0))
    print('B measured mean weighted cut:',round(mean,6),'approximation ratio:',round(mean/best,6))
    import json
    from pathlib import Path
    out=Path(__file__).resolve().parents[1]/'results'/'full_six_qubit_reference.json'
    out.write_text(json.dumps({'status':'FULL_6Q_EXECUTED','graph_vertices':6,'logical_qubits':6,'optimum':best,'ideal_expected_cut':ideal,'gamma':float(fit.x[0]),'beta':float(fit.x[1]),'processor_B':{'physical_qubits':9,'coupling_edges':KIT_B_EDGES,'native_depth':compiled.depth(),'native_cx':int(compiled.count_ops().get('cx',0)),'native_explicit_swaps':int(compiled.count_ops().get('swap',0)),'routing_diagnostic_swaps':int(diagnostic.count_ops().get('swap',0)),'unrestricted_native_depth':unrestricted.depth(),'unrestricted_native_cx':int(unrestricted.count_ops().get('cx',0)),'noisy_cut':mean,'approximation_ratio':mean/best},'shots':4096,'ideal_optimal_bitstring_probability':ideal_success,'noisy_optimal_bitstring_shots':success_shots,'noisy_optimal_bitstring_probability':success_shots/4096,'best_observed_cut':best_observed,'optimal_bitstrings_q0_to_q5':[list(z) for z in optimal_solutions],'counts_bitstring_msb_first':{k:int(v) for k,v in sorted(counts.items())},'optimizer_restarts':restart_rows,'noise_status':'PROVISIONAL_UNCONFIRMED'},indent=2))
    print('Ideal optimum-bitstring probability:',round(ideal_success,6))
    print('Noisy optimal shots:',success_shots,'/ 4096; best observed cut:',best_observed)
    print('SWAP diagnostic:',diagnostic.count_ops().get('swap',0),'unrestricted CX:',unrestricted.count_ops().get('cx',0))
    print('Reference output:',out)
if __name__=='__main__':main()
