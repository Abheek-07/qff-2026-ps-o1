"""Fast structural checks of actual output tables; fails if files absent."""
import csv, pathlib, math
r=pathlib.Path(__file__).resolve().parent/'results'/'tables'
needed={'results.csv','resources.csv','bell.csv','qaoa_five_starts.csv'}
for f in needed:
 if not (r/f).is_file(): raise SystemExit(f'MISSING: {r/f}')
def read(name):
 with (r/name).open(newline='') as fp: return list(csv.DictReader(fp))
rows=read('results.csv');starts=read('qaoa_five_starts.csv');bell=read('bell.csv')
assert len(rows)==6 and len(starts)>=5 and len(bell)==4,(len(rows),len(starts),len(bell))
assert {(x['processor'],x['condition']) for x in rows}=={(p,c) for p in 'ABD' for c in ['ideal','noisy']}
for row in rows:
 if row['processor']=='A': assert row['executable'].lower()=='false'
 else:
  assert row['executable'].lower()=='true',row
  assert int(row['shots'])==4096
  assert row['quality_metric']=='approx_ratio'
  assert float(row['classical_optimum'])==22
  assert 0<=float(row['quality_value'])<=1
  assert 0<=float(row['p_opt'])<=1
from bell_experiments import choose_pairs
import json
processor=json.loads((pathlib.Path(__file__).resolve().parent/'processors'/'processor_D.json').read_text())
adjacent,farthest=choose_pairs(processor)
for row in bell:
 expected=adjacent if row['pair_role']=='adjacent' else farthest
 assert (int(row['pair_q0']),int(row['pair_q1']))==expected, (row,expected)
 assert int(row['shots'])==4096
 assert row['condition'] in ('ideal','noisy')
assert {(x['pair_role'],x['condition']) for x in bell}=={(role,mode) for role in ('adjacent','farthest') for mode in ('ideal','noisy')}
print('PASS: Required rows, five starts, Bell pair IDs, and shots match processor_D.json:',adjacent,farthest)
print('NEXT: human review of Bell columns, circuits, noisy metrics, figure paths and submission docs')
