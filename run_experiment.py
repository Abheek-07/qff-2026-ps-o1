"""One-command Phase-1 PS-O1 experiment. Requires pinned Qiskit dependencies.

Writes REAL transpiler/Aer results to results/{tables,figures}, replacing only
files it generates. Do not change scientific output numbers by hand.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import sys
import subprocess
import traceback
import numpy as np
import pandas as pd
from src.problem import (
    weighted_graph,edges,cut_score,cost_array,verify_reduction,exact_optimum,
    ideal_state,ideal_expected_cut,optimize_angles,qaoa_circuit,measured_circuit,
    score_counts,N_LOGICAL)
from src.processors import load,validate,noise_model,NOISE,processor_spec
from src.routing import compile_for,unrestricted_reference,topology_pressure
from src.metrics import resources
from src.visualization import plot_weighted_graph,plot_topologies,plot_metrics,plot_noise,plot_sensitivity

ROOT=Path(__file__).resolve().parent
TABLES=ROOT/'results'/'tables'
FIGURES=ROOT/'results'/'figures'
SHOTS=4096
SIM_SEEDS=(43,47,53,59,61)


def save_csv(name,rows):
    path=TABLES/name
    frame=pd.DataFrame(rows)
    frame.to_csv(path,index=False,float_format='%.10g')
    return frame


def verify_json_generators():
    for name in ('A','B'):
        before=(ROOT/'processors'/f'processor_{name}.json').read_bytes()
        subprocess.run([sys.executable,str(ROOT/'processors'/f'processor_{name}.py')],check=True,cwd=ROOT,capture_output=True,text=True)
        after=(ROOT/'processors'/f'processor_{name}.json').read_bytes()
        assert json.loads(after)==processor_spec(name)
        assert json.loads(before)==json.loads(after), f'Processor {name} generator changed JSON unexpectedly'
    return {n:load(n) for n in ('A','B')}


def write_summary_report(configs, gamma,beta,optimum,ideal_mean,frame,summary,free_ref):
    def v(p,k):return frame.set_index('processor').loc[p,k]
    def mean(p,k):return summary.set_index('processor').loc[p,k]
    a,b=map(lambda p:float(v(p,'depth')),('A','B'))
    comparison='B has lower native compiled depth' if b<a else ('A has lower native compiled depth' if a<b else 'A and B have equal compiled depth')
    # Actual numeric results, no fabricated SWAP claims.
    body=f'''# QFF 2026 Phase 1 — PS-O1 Experimental Report

## 1. Task and reference solution

**Track:** Quantum Optimization. **PS-O1:** Max-Cut on Weighted Graphs, as specified in the 2026 Phase 1 Master Challenge Guide (page 4).

The benchmark generates `networkx.erdos_renyi_graph(n=6, p=0.5, seed=42)`, then assigns integer edge weights 1–5 with `random.Random(42)` over sorted edges. The actual 9 weighted edges and seeds are saved in `data/weighted_graph.json`. Exhaustive enumeration over all 64 assignments gives **optimal cut = {optimum}**. One optimal six-bit assignment is **(0, 0, 1, 0, 1, 1)**.

We use the objective `C(x) = sum_(u,v) w_uv [x_u != x_v]`. As Max-Cut has global bit-flip symmetry, `C(x)=C(1-x)`, we fix vertex `x_0=0` and encode vertices 1–5 on five logical qubits, allowing deployment on five-qubit Processor A. The reduced objective is **exactly equivalent for finding the classical optimum**. However, a QAOA p=1 variational state on the 5-variable gauge-fixed subspace is **not generally equivalent to a standard six-qubit QAOA ansatz**; the comparison uses the same reduced ansatz on both A and B. Organiser confirmation of this symmetry encoding is recommended because the official guide does not state an encoding prescription.

### Mathematical formulation and QUBO/Hamiltonian

For each graph vertex let `x_i ∈ {{0,1}}` specify its partition. Each weighted edge contributes `w_ij` exactly when its endpoints differ:

`C(x) = Σ_(i,j) w_ij [x_i ≠ x_j] = Σ_(i,j) w_ij (x_i + x_j - 2 x_i x_j)`.

This is a quadratic unconstrained binary objective (QUBO) to **maximize** (or equivalently minimize `-C`). Using `x_i = (1 - Z_i)/2`, the cost operator is

`C_hat = (1/2) Σ_(i,j) w_ij (I - Z_i Z_j)`.

The QAOA cost evolution `exp(-i γ C_hat)` differs only by a global phase from `RZZ(-γ w_ij)` for each edge. The mixer is `exp(-i β Σ_i X_i)`, implemented as `RX(2β)` per logical qubit. Fixing vertex 0 gives local Z terms on its incident edges, but defines a **different five-qubit QAOA ansatz**, not a physical six-qubit compression preserving the same quantum distribution. The same original weighted objective and classical optimum are used for scoring both encodings.

## 2. QAOA and reference benchmark

The prepared state is `|+>^5`, with cost unitary `exp(-i * gamma * C)` (up to global phase) and mixer `exp(-i * beta * sum X_i)` for p=1. Edges not incident to vertex 0 use `rzz(-gamma*w)`; edges incident to fixed vertex 0 use `rz(-gamma*w)`. The circuit is built in `src/problem.py`.

A single pair of `(gamma,beta)` is optimized **once on an ideal logical statevector** (deterministic SciPy differential evolution, seed=42), then reused identically on A and B. No processor-specific parameter tuning occurs. Optimized gamma={gamma:.9f}; beta={beta:.9f}. The ideal expected weighted cut on this *reduced* ansatz is **{ideal_mean:.6f}** (approximation ratio {ideal_mean/optimum:.4%}) against the classical optimum {optimum}. The independent NumPy statevector probability calculation agrees with Qiskit Statevector within numerical tolerance.

## 3. Participant-designed processor models

Processor A: five physical qubits, sparse tree couplings `{configs['A']['coupling_map']}`. This architecture has only four links, forcing some requested two-qubit interactions to use longer paths. Processor B: nine physical qubits, connected 12-edge topology `{configs['B']['coupling_map']}`. This topology provides additional routes and physical qubits; it does not claim to model calibrated real IBM hardware. Both are undirected as modelled with bidirectional CX adjacency, and both use the same basis gates `{{rz,sx,x,cx}}`.

Processor models are generated by `processors/processor_A.py` and `processor_B.py`. The maps are **participant-defined**, which page 2 of the Master Guide explicitly permits. Schematics are in `results/figures/processor_topologies.png`.

## 4. Controlled protocol

- Exactly **five logical qubits** for the reduced six-node task on both processors; physical budgets A=5, B=9. Extra B qubits can be available to the transpiler as routing workspace, not as new logical variables.
- Qiskit transpilation: `optimization_level=1`, `seed_transpiler=42`, basis `rz/sx/x/cx` and **fixed initial layout** logical-to-physical `[0,1,2,3,4]` for both A and B.
- Qiskit Aer: 4096 measurement shots per simulation seed, baseline seeds `{list(SIM_SEEDS)}`. Counts measure the logical qubits into the five original classical bit positions, so the cut evaluator decodes bit order correctly after transpilation.
- Same synthetic noise on A and B: single-qubit depolarizing p=0.001 for `rz`, `sx`, `x`; CX depolarizing p=0.005; symmetric readout-flip p=0.01. `rz` is treated as noisy by explicit *synthetic* choice, not as a noiseless virtual-Z gate.
- The unlimited-connectivity reference is transpiled with the same native basis and optimization level but without any coupling restrictions. Differences from it are **compilation overhead estimates**, not a direct count of physical SWAP operations.
- A separate routing diagnostic compiles with `swap` provisionally allowed in the basis. It is **not the device-executable native benchmark**; its SWAP count is a probe of the routing decomposition and may be sensitive to compiler choices.

## 5. Actual benchmark outcomes

| Metric | A | B |
|---|---:|---:|
| Physical qubits | 5 | 9 |
| Native circuit depth | {int(v('A','depth'))} | {int(v('B','depth'))} |
| Native CX gates | {int(v('A','cx_count'))} | {int(v('B','cx_count'))} |
| Native explicit SWAP gates | {int(v('A','explicit_swap_count'))} | {int(v('B','explicit_swap_count'))} |
| Diagnostic SWAP gates (non-native probe) | {int(v('A','swap_diagnostic_count')) if pd.notna(v('A','swap_diagnostic_count')) else 'unavailable'} | {int(v('B','swap_diagnostic_count')) if pd.notna(v('B','swap_diagnostic_count')) else 'unavailable'} |
| Additional CX vs unrestricted compilation | {int(v('A','cx_above_unrestricted'))} | {int(v('B','cx_above_unrestricted'))} |
| Initial-layout excess hop proxy | {int(v('A','extra_hops_proxy'))} | {int(v('B','extra_hops_proxy'))} |
| Noise-averaged cut (5 seeds) | {float(mean('A','mean_cut')):.4f} | {float(mean('B','mean_cut')):.4f} |
| Standard error between seed means | {float(mean('A','standard_error')):.4f} | {float(mean('B','standard_error')):.4f} |
| Mean noisy approx ratio | {float(mean('A','approximation_ratio')):.3%} | {float(mean('B','approximation_ratio')):.3%} |

Unrestricted 5-qubit native reference: depth={int(free_ref['depth'])}, CX={int(free_ref['cx_count'])}.

**Observed depth result:** {comparison}. A depth={int(a)} and B depth={int(b)}. The difference follows the compiler's layout/routing/gate optimization under the chosen connectivity, not an isolated gate-error advantage. Native `explicit_swap_count` may be zero even if routing was implemented through native CX sequences or other rewrites; do not interpret zero explicit SWAPs as zero routing cost. Consult the CX overhead, diagnostic SWAPs, and hop proxy together.

The noisy-score comparison uses a small number of seeds. **Do not claim a statistically certain performance advantage without an appropriate uncertainty analysis.** No actual hardware calibration, hardware runtime, or physical qubit fidelity data is used.

## 6. Figures, supporting evidence, and limits

- `results/figures/weighted_graph.png`: exact six-node weighted problem input.
- `results/figures/processor_topologies.png`: our processor designs.
- `results/figures/architecture_resources.png`: depth/CX/SWAP-probe comparison.
- `results/figures/noisy_cut.png`: noisy score and across-seed SE.
- `results/figures/noise_sensitivity.png`: varying CX noise at fixed single-qubit/readout noise.
- `results/tables/processor_comparison.csv`, `routing_diagnostics.csv`, `noisy_trials.csv`, `noisy_summary.csv`, `noise_sensitivity.csv`: raw exported data.

Limitations: six-node-to-five-qubit symmetry fixing is classically exact but changes the variational search space; fixed starting layout affects compilations; synthetic uniform gate/readout error is illustrative; compiler SWAP exposure depends on the basis decomposition; seed-to-seed simulation variance does not fully quantify uncertainty from alternative layouts or optimizer minima; all 9 B qubits need not be logically active.

## 7. Future architecture ideas (NOT implemented Phase 2)

A future participant-designed processor could selectively add edges joining distant logical interactions and reduce graph-path pressure, subject to hardware constraints. Such improvements require benchmark evidence; Processor C/D construction is intentionally outside Phase 1.

## 8. Reproducibility and AI disclosure

Pinned software in `requirements.txt`; regenerate configs via the two `processor_*.py` scripts and execute `main.ipynb` or `python run_experiment.py`. Assertions check statevector probabilities, reference optimum, device configs, topology reachability, and native basis consistency. Synthetic simulator seeds and benchmark settings are recorded in `results/experiment_metadata.json`.

AI assistance was used in code development, debugging, documentation, and experiment design. The participant/team must independently understand and confirm the benchmark before submission. Numeric results above are generated by **executed** Qiskit/Aer runs, not made-up estimates.
'''
    # The Phase 1 Processor D proposal is report documentation, not executable Phase 2 work.
    # Source it from a tracked file so a clean Colab run cannot revert Section 7.
    old_d_start = '## 7. Future architecture ideas (NOT implemented Phase 2)'
    old_d_end = '## 8. Reproducibility and AI disclosure'
    assert body.count(old_d_start) == 1 and body.count(old_d_end) == 1
    section7 = (ROOT/'docs'/'processor_d_proposal.md').read_text(encoding='utf8').strip()
    assert section7.startswith('## 7. Processor D concept proposal')
    assert 'NOT implemented' in section7
    body = body[:body.index(old_d_start)] + section7 + '\n\n' + body[body.index(old_d_end):]
    body = ('> **Compliance status:** This A/B benchmark uses an exploratory five-qubit symmetry-fixed QAOA ansatz, NOT an organiser-approved replacement for full six-qubit QAOA. Noise/basis parameters are provisional, and the Challenge Kit and Master Guide differ on fixed-versus-custom topologies. See COMPLIANCE_NOTES.md.\n\n' + body)
    (ROOT/'report.md').write_text(body,encoding='utf8')
    (ROOT/'results'/'summary.md').write_text('## Measured benchmark summary\n\n```text\n'+frame.to_string(index=False)+'\n```\n\n## Noisy trial summary\n\n```text\n'+summary.to_string(index=False)+'\n```\n',encoding='utf8')


def main():
    from qiskit import __version__ as qiskit_version
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    print('Phase 1 PS-O1: clean run',flush=True)
    print('Qiskit',qiskit_version,'Qiskit Aer',importlib.metadata.version('qiskit-aer'),flush=True)
    FIGURES.mkdir(exist_ok=True,parents=True)
    TABLES.mkdir(exist_ok=True,parents=True)
    e=edges(); opt=verify_reduction(e)
    cfgs=verify_json_generators()
    for name,cfg in cfgs.items():validate(cfg)
    g=weighted_graph()
    stored=json.loads((ROOT/'data'/'weighted_graph.json').read_text())
    assert [{'u':u,'v':v,'weight':w} for u,v,w in e]==stored['edges']
    assert opt==16 and len(g.nodes)==6
    plot_weighted_graph(g);plot_topologies(cfgs)
    gamma,beta,ideal_mean=optimize_angles(e)
    print(f'Graph: 6 vertices, {len(e)} weighted edges, exact optimum {opt}',flush=True)
    print(f'Angles: gamma {gamma:.6f}; beta {beta:.6f}; ideal reduced-QAOA expected cut {ideal_mean:.6f}',flush=True)
    ideal_p=np.abs(ideal_state(gamma,beta,e))**2
    from_qiskit=np.abs(Statevector.from_instruction(qaoa_circuit(gamma,beta,e)).data)**2
    error=float(np.max(np.abs(from_qiskit-ideal_p)))
    assert error<1e-9, f'QAOA phase/mixer disagrees with independent NumPy ({error})'
    assert abs(float(np.dot(from_qiskit,cost_array(e)))-ideal_mean)<1e-9
    measured=measured_circuit(gamma,beta,e)
    free=resources(unrestricted_reference(measured))
    benchmark=[]; diagnostic=[]; trials=[];compiled={}
    # Reproducible simulator shot seeds. 10 baseline run calls; cost scales with backend.
    for name,config in cfgs.items():
        print(f'Compiling Processor {name}...',flush=True)
        native=compile_for(measured,config)
        compiled[name]=native
        ops=native.count_ops()
        illegal=set(ops)-set(config['basis_gates'])-{'measure','barrier','delay','reset'}
        assert not illegal, f'Non-native compiled gates for {name}: {illegal}'
        try:
            probe=compile_for(measured,config,allow_swap_diagnostic=True)
            n_swaps=resources(probe)['explicit_swap_count']
            probe_depth=probe.depth()
        except Exception as ex:
            print('Non-native SWAP routing diagnostic unavailable:',str(ex),flush=True)
            n_swaps=np.nan;probe_depth=np.nan
        pressure=topology_pressure(config,e)
        res=resources(native)
        res.update({'processor':name,'physical_qubit_budget':config['num_qubits'],
            'logical_qubits':5, 'swap_diagnostic_count':n_swaps,
            'swap_diagnostic_depth':probe_depth,
            'unrestricted_cx_count':free['cx_count'],
            'unrestricted_depth':free['depth'],
            'cx_above_unrestricted':res['cx_count']-free['cx_count'],
            'depth_above_unrestricted':res['depth']-free['depth'],
            'extra_hops_proxy':pressure['extra_hops_proxy'],
            'nonlocal_cost_edges':pressure['nonlocal_cost_edges'],
            'mean_problem_edge_distance':pressure['mean_problem_edge_distance'],
            'ideal_expected_cut':ideal_mean,'classical_optimum':opt})
        benchmark.append(res)
        for item in pressure['per_edge']:
            diagnostic.append({'processor':name,**item})
        sim=AerSimulator(noise_model=noise_model(config))
        for seed in SIM_SEEDS:
            out=sim.run(native,shots=SHOTS,seed_simulator=seed).result()
            counts=out.get_counts()
            assert sum(counts.values())==SHOTS
            score=score_counts(counts,e)
            trials.append({'processor':name,'seed':seed,'shots':SHOTS,
               'weighted_cut':score,'approximation_ratio':score/opt,
               'ideal_expected_cut':ideal_mean})
            print(f'   seed {seed}: weighted cut {score:.5f}',flush=True)
    compiled_frame=save_csv('processor_comparison.csv',benchmark)
    routing_frame=save_csv('routing_diagnostics.csv',diagnostic)
    trial_frame=save_csv('noisy_trials.csv',trials)
    grouped=[]
    for name,sub in trial_frame.groupby('processor',sort=True):
        cuts=np.asarray(sub['weighted_cut'],dtype=float)
        se=float(np.std(cuts,ddof=1)/np.sqrt(len(cuts)))
        grouped.append({'processor':name,'num_simulator_seeds':len(cuts),
                        'shots_per_seed':SHOTS,'mean_cut':float(np.mean(cuts)),
                        'standard_error':se,'approximation_ratio':float(np.mean(cuts)/opt)})
    summary=save_csv('noisy_summary.csv',grouped)
    sens=[]
    for cx_p in (0.,.005,.01):
        for name,config in cfgs.items():
            modified=json.loads(json.dumps(config))
            modified['noise']['two_qubit_depolarizing']=cx_p
            sim=AerSimulator(noise_model=noise_model(modified))
            scores=[]
            for seed in (71,73):
                counts=sim.run(compiled[name],shots=SHOTS,seed_simulator=seed).result().get_counts()
                scores.append(score_counts(counts,e))
            sens.append({'processor':name,'cx_error':cx_p,'oneq_error':.001,'readout_error':.01,
                         'mean_cut':float(np.mean(scores)),'n_seeds':len(scores)})
    sensitivity=save_csv('noise_sensitivity.csv',sens)
    pd.DataFrame({'basis_state_index':np.arange(32),
                 'original_six_bit_state':[''.join(map(str,(0,)+tuple((i>>q)&1 for q in range(5)))) for i in range(32)],
                 'weighted_cut':cost_array(e).astype(int),'ideal_probability':ideal_p}).to_csv(TABLES/'ideal_distribution.csv',index=False)
    plot_metrics(compiled_frame)
    plot_noise(summary)
    plot_sensitivity(sensitivity)
    meta={'problem_statement':'PS-O1: 6-node weighted Max-Cut',
          'vertex_zero_fixed':True,'logical_qubits':5,'classical_optimum':opt,
          'optimized_angles':{'gamma':gamma,'beta':beta},
          'ideal_expected_cut':ideal_mean,'statevector_max_probability_disagreement':error,
          'transpilation':{'optimization_level':1,'seed_transpiler':42,'initial_layout':[0,1,2,3,4]},
          'shots':SHOTS,'baseline_seeds':list(SIM_SEEDS),
          'noise':NOISE,'qiskit_version':qiskit_version,
          'qiskit_aer_version':importlib.metadata.version('qiskit-aer'),
          'unrestricted_compilation_reference':free,
          'caveat':'five logical qubits exactly preserve six-node Max-Cut objective; reduced QAOA ansatz is not same as standard six-qubit ansatz',
          'run_status':'COMPLETED'}
    (ROOT/'results'/'experiment_metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')
    write_summary_report(cfgs,gamma,beta,opt,ideal_mean,compiled_frame,summary,free)
    print('\nFINAL A/B RESOURCE COMPARISON\n',compiled_frame.to_string(index=False),flush=True)
    print('\nNOISY COMPARISON\n',summary.to_string(index=False),flush=True)
    print('\nCHECKS PASSED: 6-node optimum, 5-qubit exact reduction, phase unitary, processor JSON, measured basis, exported outputs.',flush=True)
    print('SUCCESS: Generated report.md and results/ for FINAL GitHub upload.',flush=True)
    return meta

if __name__=='__main__':
    try:main()
    except Exception:
        traceback.print_exc()
        print('FAILED: do not submit this version; fix the error and rerun.',file=sys.stderr)
        sys.exit(1)
