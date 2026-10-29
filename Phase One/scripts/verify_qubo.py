"""Independent QUBO certificate for the six-vertex weighted Max-Cut task.

Maximize C(x) = sum_{(u,v)} w_uv * (x_u+x_v-2*x_u*x_v).
This script does not change or rerun QAOA; it verifies all 2^6 classical states.
"""
import itertools, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.problem import edges, cut_score, exact_optimum

def build_qubo():
    linear=[0]*6
    quadratic={}
    for u,v,w in edges():
        linear[u]+=w;linear[v]+=w
        quadratic[(u,v)]=-2*w
    return linear,quadratic

def evaluate_qubo(bits, linear, quadratic):
    return sum(a*x for a,x in zip(linear,bits))+sum(a*bits[u]*bits[v] for (u,v),a in quadratic.items())

def verify():
    linear,quadratic=build_qubo()
    for b in itertools.product((0,1),repeat=6):
        assert evaluate_qubo(b,linear,quadratic)==cut_score(b)
    val,bits=exact_optimum()
    assert val==16
    certificate={"problem":"PS-O1 six-vertex weighted Max-Cut", "objective":"maximize x^T Q x", "variable_order":"x0..x5", "linear":linear,"quadratic":[{"u":u,"v":v,"coefficient":w} for (u,v),w in sorted(quadratic.items())],"tested_assignments":64,"all_assignments_match_cut_score":True,"classical_optimum":val,"optimum_bitstrings":[list(x) for x in bits]}
    return certificate

if __name__=='__main__':
    path=ROOT/'results'/'qubo_verification.json'
    path.write_text(json.dumps(verify(),indent=2)+'\n',encoding='utf8')
    print('PASS: all 64 QUBO energies equal Max-Cut scores. Wrote',path)
