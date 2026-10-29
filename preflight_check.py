"""Dependency-light preflight. Does not simulate quantum results."""
import json, pathlib, zipfile, csv, ast
from itertools import product
from collections import deque
R=pathlib.Path(__file__).resolve().parent
data=json.loads((R/'data/instances.json').read_text())['PS-O1']
edges=data['weighted_edges']; n=data['num_vertices']
assert (n,len(edges),sum(w for _,_,w in edges))==(6,9,27)
scores={}
for x in product((0,1),repeat=n):
 scores[''.join(map(str,x))]=sum(w for i,j,w in edges if x[i]!=x[j])
assert max(scores.values())==22
assert sorted(k for k,v in scores.items() if v==22)==['001011','110100']
assert sum(scores.values())/64==13.5
p=json.loads((R/'processors/processor_D.json').read_text()); es={tuple(sorted(e)) for e in p['edges']}
assert p['num_qubits']==6 and len(es)==8
assert set(p['basis_gates'])=={'rz','sx','x','cx'}
deg=[sum(i in e for e in es) for i in range(6)]
assert max(deg)<=4
seen={0}; q=deque([0])
while q:
 for e in es:
  if q[0] in e:
   other=e[0] if e[1]==q[0] else e[1]
   if other not in seen: seen.add(other);q.append(other)
 q.popleft()
assert len(seen)==6
for name in ['benchmark_phase2.py','qaoa_step2.py','bell_experiments.py','bell_validation.py','plot_bell_results.py']:
 ast.parse((R/name).read_text())
assert (R/'main.ipynb').is_file()
print('PASS: Official locked graph, optimum, D topology, syntax, notebook present')
print('NOTICE: This does NOT run Qiskit, check noise simulations, or validate results.csv')
