"""Official PS-O1 benchmark pipeline. Run from repo root after installing requirements.
Requires official qff_phase2.py UNCHANGED; never fabricates missing D measurements.
"""
import csv
import json
from pathlib import Path
from itertools import product
import numpy as np
from qaoa_step2 import N, EDGES, qaoa_circuit, optimize_five_starts, cut_value
from qff_phase2 import (
    PROCESSOR_A, PROCESSOR_B, SHOTS, SEED,
    validate_processor_d, load_processor, circuit_metrics,
    transpile_for, simulator, counts_to_x,
)

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / 'results' / 'tables'
FIELDS = ['problem_id','processor','condition','executable','logical_qubits',
          'physical_qubits','logical_cx','cx','depth','two_q_depth','swaps',
          'cx_overhead','shots','quality_metric','quality_value','p_opt',
          'classical_optimum','random_baseline']


def all_reference_values():
    assignments = list(product((0,1), repeat=N))
    scores = [cut_value(x) for x in assignments]
    optimum = max(scores)
    optimal = {x for x,v in zip(assignments,scores) if v == optimum}
    return optimum, optimal, float(np.mean(scores)),len(optimal)/len(assignments)


def evaluate_processor(qc, processor, condition, optimum, optimal, random_ratio):
    metrics = circuit_metrics(qc,processor)
    base = dict(problem_id='PS-O1', processor=processor['name'].split()[-1],
                condition=condition,executable=metrics['executable'],
                logical_qubits=N, physical_qubits=processor['num_qubits'],
                quality_metric='approx_ratio',classical_optimum=optimum,
                random_baseline=random_ratio)
    if not metrics['executable']:
        return {**base, **{k: '' for k in FIELDS if k not in base}}, None
    tqc = transpile_for(qc, processor)
    counts = simulator(noisy=(condition=='noisy'),processor=processor).run(
        tqc,shots=SHOTS,seed_simulator=SEED).result().get_counts()
    assert sum(counts.values())==SHOTS
    counted = [(counts_to_x(key), num) for key,num in counts.items()]
    # Qiskit bitstring order is reversed; counts_to_x returns x0,...,x5.
    assert all(len(x)==N for x,_ in counted)
    mean = sum(cut_value(x)*n for x,n in counted)/SHOTS
    best = max(cut_value(x) for x,_ in counted)
    p_opt = sum(n for x,n in counted if x in optimal)/SHOTS
    data = {**base,**{k:metrics[k] for k in ('logical_cx','cx','depth',
               'two_q_depth','swaps','cx_overhead')},
            'shots':SHOTS,'quality_value':mean/optimum,'p_opt':p_opt}
    extra = {'processor':processor['name'],'condition':condition,'mean_cut':mean,
             'best_cut':best,'r_best':best/optimum,'p_opt':p_opt,
             'approx_ratio':mean/optimum,'counts':dict(counts)}
    return data,extra


def run():
    TABLES.mkdir(parents=True, exist_ok=True)
    optimum, optimal, random_cut, random_p = all_reference_values()
    assert (N,len(EDGES),sum(w for _,_,w in EDGES),optimum)==(6,9,27,22)
    assert len(optimal)==2 and random_cut==13.5
    records = optimize_five_starts()
    for record in records:
        record['ideal_statevector_approx_ratio'] = record['expected_cut']/optimum
    selected = max(records,key=lambda r:r['expected_cut'])
    with (TABLES/'qaoa_five_starts.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=records[0].keys())
        writer.writeheader();writer.writerows(records)
    qc = qaoa_circuit(selected['gamma'], selected['beta'],measure=True)
    Dpath = ROOT/'processors'/'processor_D.json'
    processors=[PROCESSOR_A, PROCESSOR_B]
    if Dpath.is_file():
        d=load_processor(str(Dpath))
        errors=validate_processor_d(d,required_qubits=N)
        if errors:
            raise ValueError('Processor D violates official rules: '+ '; '.join(errors))
        processors.append(d)
    else:
        print('WARNING: Processor D not present; output is INCOMPLETE, NOT SUBMISSION READY.')
    rows=[]; extras=[]; resources=[]
    for p in processors:
        m=circuit_metrics(qc,p)
        resources.append(m)
        for condition in ('ideal','noisy'):
            row, detail=evaluate_processor(qc,p,condition,optimum,optimal,random_cut/optimum)
            rows.append(row)
            if detail:extras.append(detail)
    with (TABLES/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore')
        writer.writeheader();writer.writerows(rows)
    with (TABLES/'resources.csv').open('w',newline='') as f:
        fields=sorted(set().union(*(r.keys() for r in resources)))
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(resources)
    with (TABLES/'sampled_details.json').open('w') as f:
        json.dump({'classical_optimum':optimum,'optimal_bitstrings_vertex_order':
                 [''.join(map(str,x)) for x in sorted(optimal)],
                 'random_expected_cut':random_cut,'random_approx_ratio':random_cut/optimum,
                 'random_p_opt':random_p,'best_seed':selected,'experiments':extras},f,indent=2)
    print('C*:',optimum,'random mean:',random_cut,'optimal solutions:',optimal)
    for row in rows:
        print(row['processor'],row['condition'], 'r=',row.get('quality_value'),
              'P_opt=',row.get('p_opt'))
    print('Five-start ideal statevector mean/std approximation ratio:',float(np.mean([r['ideal_statevector_approx_ratio'] for r in records])),float(np.std([r['ideal_statevector_approx_ratio'] for r in records])))
    print('Wrote:',TABLES/'results.csv')
    return rows

if __name__=='__main__':
    run()
