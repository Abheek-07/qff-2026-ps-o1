"""Rebuild full-six section using measured JSON, preserving compliance notices."""
import json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    d=json.loads((root/'results/full_six_qubit_reference.json').read_text())
    assert d['status']=='FULL_6Q_EXECUTED' and d['logical_qubits']==6
    b=d['processor_B']
    target=root/'report.md'
    original=target.read_text()
    original=original.split('\n## 9. Executed full six-qubit QAOA')[0].rstrip()
    rows=[('Classical optimum',d['optimum']),('Ideal optimized expected cut',f"{d['ideal_expected_cut']:.6f}"),('Ideal approximation ratio',f"{d['ideal_expected_cut']/d['optimum']:.3%}"),('Compiled native depth',b['native_depth']),('Compiled native CX',b['native_cx']),('4096-shot noisy mean cut',f"{b['noisy_cut']:.6f}"),('Noisy approximation ratio',f"{b['approximation_ratio']:.3%}"),('Processor A full-six feasibility','Not feasible: A has five physical qubits')]
    if 'ideal_optimal_bitstring_probability' in d:
        rows += [('Ideal optimal-string success probability',f"{d['ideal_optimal_bitstring_probability']:.3%}"),('Measured optimal-string frequency',f"{d['noisy_optimal_bitstring_shots']}/{d['shots']} = {d['noisy_optimal_bitstring_probability']:.3%}"),('Best observed weighted cut',d['best_observed_cut'])]
    if 'routing_diagnostic_swaps' in b:
        rows += [('SWAP-allowed non-native diagnostic',b['routing_diagnostic_swaps']),('Unrestricted connectivity native CX',b['unrestricted_native_cx']),('Extra native CX relative to unrestricted',b['native_cx']-b['unrestricted_native_cx'])]
    table='\n'.join(f'| {k} | {v} |' for k,v in rows)
    section='\n\n## 9. Executed full six-qubit QAOA — Processor B (separate experiment)\n\n'
    section+='Unreduced six-logical-qubit p=1 QAOA uses the original six-vertex graph on nine-physical-qubit Processor B (the historical eight-edge B topology, not the 12-edge exploratory B topology). Values below are read from `results/full_six_qubit_reference.json` at report generation time, not hard-coded.\n\n'
    section+='| Metric | B |\n|---|---:|\n'+table+'\n\n'
    if 'optimizer_restarts' in d:
        section+='### Independent optimizer restarts\n\n| Seed | Ideal expected cut |\n|---|---:|\n'
        section+='\n'.join(f"| {row['seed']} | {row['ideal_expected_cut']:.6f} |" for row in d['optimizer_restarts'])+'\n\n'
    section+='**Interpretation:** These numbers are not an apples-to-apples A/B comparison of the same full six-qubit circuit, since A cannot accommodate it. The separate five-qubit experiment fixes a vertex, preserving the classical optimum but changing the QAOA ansatz. The organiser has explicitly not approved that reduction as an official method. Native CX overhead and non-native SWAP diagnostic are different quantities. The latter is compiler-dependent. All device noise and basis parameters are provisional, not final organiser-approved benchmarks.\n\n'
    section+='## 10. Organiser clarifications and reproducibility\n\nThe updated Master Guide permits custom A/B coupling maps, while the consolidated Challenge Kit specifies example maps and allows A to be handled as a capacity reference for six-qubit workloads. The organiser subsequently clarified that neither the A-handling method nor the final noise/basis parameters are frozen. These inconsistencies are disclosed rather than silently reconciled. See `COMPLIANCE_NOTES.md`. `main.ipynb` regenerates all experimental results and this report section from the saved JSON.\n'
    # Verified optional full-six B architecture comparison. This is appended after
    # the generated reference section, so subsequent notebook runs preserve it.
    comparison_path = root / 'results/reference_b_comparison/full_six_b_topology_comparison.json'
    if comparison_path.exists():
        comparison = json.loads(comparison_path.read_text(encoding='utf-8'))
        if comparison.get('status') == 'MEASURED_AFTER_EXECUTION':
            cases = comparison['comparisons']
            expected = ['official_12edge_B', 'participant_12edge_B', 'historical_8edge_B']
            if all(label in cases for label in expected):
                section += '\n## 11. Measured architecture sensitivity — full six-qubit QAOA on three Processor B topologies\n\n'
                section += ('This supplementary **B-versus-B** experiment uses the same original six-logical-qubit '
                            'QAOA circuit, fixed optimized angles, p=1, 4096 measurement shots, synthetic noise, '
                            'and seeded transpilation on three **nine-physical-qubit** architectures. The twelve-edge '
                            'official topology is the configuration documented in the later QFF processor PDF; '
                            'the historical eight-edge model is a separately labelled earlier experiment. '
                            'This is **not** a full-six A/B comparison.\n\n')
                section += '| B topology | Links | Native depth | Native CX | Diagnostic SWAPs | Noisy expected cut | Approx. ratio | Optimal outcomes |\n'
                section += '|---|---:|---:|---:|---:|---:|---:|---:|\n'
                for label in expected:
                    m = cases[label]['metrics']
                    section += (f"| `{label}` | {m['coupling_edges']} | {m['native_depth']} | "
                                f"{m['native_cx']} | {m['diagnostic_swaps']} | {m['noisy_expected_cut']:.4f} | "
                                f"{m['approximation_ratio']:.2%} | {m['optimal_shots']}/{m['shots']} |\n")
                section += ('\n**Interpretation:** On this instance and selected placement/routing conditions, '
                            'both twelve-edge graphs compiled to lower depth and CX count than the earlier '
                            'eight-edge graph. The custom twelve-edge topology **did not outperform** the official '
                            'twelve-edge reference in these two circuit-cost measures. A single 4096-shot noisy '
                            'simulation per topology is insufficient to establish statistically significant '
                            'differences in quality. The native CX basis contains no explicit SWAP instruction; '
                            'diagnostic SWAP counts come from a separate non-native transpilation.\n\n')
                section += ('**Reproducible artifacts:** '
                            '`results/reference_b_comparison/full_six_b_topology_comparison.csv`, '
                            '`results/reference_b_comparison/full_six_b_topology_comparison.json`, '
                            'and three `*_compiled.txt` circuit exports. Recreate with '
                            '`python scripts/compare_full_six_b_topologies.py`.\n')
    target.write_text(original+section)
    print('Report updated from measured full-six-qubit JSON')

if __name__=='__main__':main()
