# Processor D candidate — HACKSMITHS (not yet benchmarked)

This package extends the previously prepared Phase 2 B baseline by adding `processors/processor_D.json`. It is NOT a completed submission.

## Architecture rationale

The official PS-O1 graph has 9 weighted edges. Vertex 4 has five required neighbours, which exceeds the official maximum degree of 4. A six-physical-qubit D cannot directly connect all nine problem edges under an identity mapping. Our candidate keeps all edges except **(2,4), weight 1**, yielding an eight-edge connected architecture with degree sequence **[3,2,2,4,3,2]**. Eight problem interactions (26 of 27 edge-weight units) have direct coupling under the identity mapping; the remaining low-weight interaction has a two-hop route.

These counts describe **connectivity only**. They are not transpiler results, and a weighted edge of 5 does NOT imply five CX gates. A Qiskit transpiler may use a different layout, and reductions in routing cost or noise must be measured.

## Required next actions

1. Install `requirements.txt` in Python 3.10–3.12.
2. Run `python benchmark_phase2.py` from this folder; inspect `results/tables/results.csv` and `resources.csv`.
3. Open `main.ipynb` and Run All. If any error occurs, fix code before submitting.
4. Give validated D configuration to Bell teammate; run all Bell experiments and create `results/tables/bell.csv`.
5. Compare D and B **with identical optimized gamma/beta**. Make performance claims only after measurement.
6. Add final report, plot files, version notes, and official submission checklist.

### Handoff for website teammate

Use `processors/processor_D.json` to render D's 6 nodes and 8 edges. Do not show synthetic CX counts or fabricated noisy cut values. Wait for measured CSVs.

### A judge-ready explanation

"Processor D is a custom six-qubit, eight-coupler architecture. We designed its connectivity around the nine interactions of the official six-variable Max-Cut problem, keeping direct couplings for eight edges while excluding one low-weight edge to satisfy the maximum hardware degree of four. It is a proposed routing-aware design; we evaluate any actual benefits using the organiser's transpilation, noise model, and solution-quality metrics."
