"""Append the separately executed full-six benchmark to the generated reduced-report, safely."""
from pathlib import Path
import json

def main():
    root=Path(__file__).resolve().parents[1]
    d=json.loads((root/'results/full_six_qubit_reference.json').read_text())
    assert d['status']=='FULL_6Q_EXECUTED' and d['logical_qubits']==6 and d['processor_B']['physical_qubits']==9
    report=root/'report.md'
    text=report.read_text()
    marker='\n## 9. Executed full six-qubit QAOA — Processor B (separate experiment)'
    text=text.split(marker)[0].rstrip()+'\n'+SECTION
    report.write_text(text)
    print('Merged executed full six-qubit benchmark into report.md')

SECTION = "\n## 9. Executed full six-qubit QAOA — Processor B (separate experiment)\n\nThis **unreduced** p=1 QAOA benchmark covers the original six-node weighted graph using **six logical qubits** on **nine-physical-qubit Processor B**. Its numerical evidence was generated in Google Colab; the raw result is preserved in `results/full_six_qubit_reference.json`. The six-qubit circuit cannot be directly fitted onto Processor A's five physical qubits. Following the kit's capacity-reference interpretation, no fictitious six-qubit A run is reported.\n\n| Full 6-qubit QAOA metric | B (kit-style eight-edge coupling map) |\n|---|---:|\n| Classical exact optimum | 16 |\n| Ideal optimized expected cut | 11.978903 |\n| Ideal approximation ratio | 74.8681% |\n| Native compiled depth | 57 |\n| Native CX count | 27 |\n| Noisy mean weighted cut (4096 shots) | 11.662109 |\n| Noisy approximation ratio | 72.8882% |\n| Processor A with six qubits | **Infeasible (capacity: 5 physical qubits)** |\n\n**Comparability limit:** These six-qubit B results use the *eight-edge consolidated-kit B topology*, while the five-qubit A/B experiments above use *participant-designed* A and B topologies; they also use different ansätze and independently optimized parameters. Therefore, comparisons across sections 5 and 9 **cannot isolate architecture effects**. Only the within-section-5 A/B runs are controlled for a common five-qubit circuit. Neither noise settings nor this approach are represented as newly approved by the organisers. The six-qubit B result comes from one 4096-shot synthetic simulation, so no confidence interval for that result is asserted.\n\n**Reproduce:** `python -m src.full_six_reference` runs the full-size benchmark and updates the JSON. The notebook `main.ipynb` includes that additional run before packaging.\n"

if __name__ == '__main__':
    main()
