# Qiskit Fall Fest 2026 — PS-O1: Weighted Max-Cut QAOA

**Status: executed successfully in Google Colab; exported results included.**

This repository benchmarks the same 4-logical-qubit, p=1 weighted Max-Cut QAOA workload on participant-defined Processor A (5 physical qubits) and Processor B (9 physical qubits). Both use identical synthetic noise settings. It studies depth, CX gate overhead, layout sensitivity, solution quality, and noise sensitivity.

## Reproduce

1. Download or clone this repository; open a terminal in its root directory.
2. Install Python 3.11+ and `pip install -r requirements.txt`.
3. Open `main.ipynb` from the repository root (Jupyter or Colab). If using Colab, upload the entire repository, not just the notebook, or mount the repository in Drive.
4. **Restart kernel → Run all**. The notebook regenerates processor JSON files, tables and figures. In Colab, ensure the full repository is available under the runtime working directory; the notebook does not auto-download external project files.
5. Confirm that the noiseless correctness assertions pass and compare the newly generated CSVs to the notebook's printed values. The provided result files were generated in Colab; independently reproducing them requires rerunning the notebook.

## Files

- `main.ipynb`: End-to-end experiment and correctness assertions.
- `processors/processor_A.py`, `processor_B.py`: Generate matching JSON configs.
- `processors/*.json`: Checked-in configurations.
- `src/`: Reusable problem, processor, routing, metrics and visualization code.
- `data/weighted_graph.json`: Fixed weighted graph input.
- `results/tables/` and `results/figures/`: Created when the notebook is run.
- `report.md`: Methodology, limitations, and interpretation guidance.

## Important assumptions

- The organisers clarified that the same logical QAOA problem must be used on both processors; using all nine B qubits as active algorithm qubits is **not** required.
- Coupling maps, weighted graph, and noise parameters are participant-defined. The numbering and undirected connectivity are our interpretation of the provided slide.
- The processor models are **not calibrated real hardware**. Both use synthetic depolarizing error 0.001 per 1-qubit gate and 0.01 per CX for the baseline. No readout errors are modelled.
- A circuit's explicit SWAP count can be zero even when routing is implemented through CX decompositions.
- Classical measurement wires are defined before transpilation to avoid confusing physical measurement positions with logical Max-Cut bit assignments.

## AI assistance disclosure

AI assistance was used to develop, debug and document the implementation. All performance numbers should be taken from an actual clean notebook run; no unexecuted result is represented as measured.

## Observed benchmark summary

The corrected notebook was run in Google Colab using Qiskit 2.5.2 and Qiskit Aer 0.17.2. For the fixed initial layout, A compiled to depth 40 and B to depth 29; both had 16 CX gates. Ten noisy trials per processor gave mean weighted cuts 9.9107 (A) and 9.9216 (B). The difference is small relative to across-seed variability. See `report.md` and `results/tables/` for the detailed results.

## Colab note

Upload or clone the **entire repository**, not only `main.ipynb`; extract it and set the working directory to the repository root before running the notebook. The notebook deliberately excludes a Colab-specific ZIP extraction cell, so it also works in ordinary Jupyter.
