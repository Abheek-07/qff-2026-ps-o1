"""Reject stale Bell CSVs that refer to a different processor topology/pair choice."""
import json,csv,pathlib
from bell_experiments import choose_pairs
P=pathlib.Path(__file__).resolve().parent
proc=json.loads((P/'processors/processor_D.json').read_text())
adj,far=choose_pairs(proc)
rows=list(csv.DictReader((P/'results/tables/bell.csv').open(newline='')))
assert len(rows)==4
for row in rows:
 expected=adj if row['pair_role']=='adjacent' else far
 observed=(int(row['pair_q0']),int(row['pair_q1']))
 assert observed==expected,(row['pair_role'],observed,expected)
 assert int(row['shots'])==4096
print('PASS: Bell CSV pair IDs match currently bundled Processor D:',adj,far)
