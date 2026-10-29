# PS-O1 — published twelve-edge Processor B reference benchmark

## Scope and authority

The QFF 2026 **Phase 1 Master Guide (page 2)** permits participant-designed coupling maps; the **Processor A/B Benchmark Configuration FINAL (page 2)** lists a twelve-edge reference topology for nine-qubit Processor B. That reference has connections `(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)`.

This optional *full-six-qubit Processor B versus Processor B* comparison keeps the original six-node instance, p=1 QAOA, previously optimized `(gamma, beta)`, 4096 shots, the declared native gate set, and synthetic noise rates fixed. The circuit uses six logical qubits on **nine available physical qubits**, not nine logical qubits.

## Inputs / honest labels

- `processors/processor_B_official_12edge_reference.json` — published reference graph, **twelve** edges.
- `processors/processor_B.json` — participant-designed graph, **twelve** edges. Its shape is different from the published reference and is allowed under the Master Guide.
- `processors/processor_B_kit_reference.json` — historical **eight-edge** topology used for the existing recorded full-six run. Despite its historical filename, **it is not the reference topology in the newly supplied official Processor A/B document**. Do not overwrite or relabel old measurements as twelve-edge measurements.
- `results/full_six_qubit_reference.json` — source of previously optimized full-six QAOA angles only. Original saved measurements remain untouched.

## Run

From the project root, in a fresh Colab environment (or other environment with Qiskit installed):

```bash
pip install -r requirements.txt
python -m pytest -q
python scripts/compare_full_six_b_topologies.py
```

Expected *new* files only after a successful three-case run:

- `results/reference_b_comparison/full_six_b_topology_comparison.json`
- `results/reference_b_comparison/full_six_b_topology_comparison.csv`
- `results/reference_b_comparison/*_compiled.txt`

**These files are not included in the current update package because Qiskit/Aer were unavailable for execution here. No performance improvement is asserted before actual measurement.**

## Comparing results fairly

Compare native depth, CX count, diagnostic SWAP count, `extra_cx_vs_unrestricted`, noisy expected weighted cut, approximation ratio, and optimum-bitstring probability. `diagnostic_swaps` is measured in a separate transpilation that permits explicit SWAP instructions. Never describe a diagnostic SWAP count as the number of SWAP instructions in the native-only transpilation. Hardware connectivity can alter mappings, and different compilers may choose layouts differently even with a fixed seed.

This is **not a Processor A versus Processor B full-six comparison**; A cannot fit the standard six-logical-qubit circuit. Continue to present the separate, symmetry-reduced **five-logical-qubit** A/B experiment with that limitation disclosed.

## Before publishing

1. Execute the script in Qiskit/Aer and inspect the complete outputs.
2. Check that all three cases use identical logical parameters and shot/noise configuration, and that results are numerically plausible.
3. Integrate the new CSV/JSON and a measured-only explanatory paragraph into `report.md` (and into the report generator if it rewrites that section).
4. Re-run the notebook and tests, confirm that the generator preserves the updated explanation, and review GitHub diff before pushing.

The existing reported ideal expected cut and classical optimum require no changes.
