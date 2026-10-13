# Qiskit Fall Fest 2026 — Phase 1, PS-O1: Weighted Max-Cut QAOA

**Track:** Quantum Optimization. **Problem statement:** PS-O1 — Max-Cut on Weighted Graphs. **Stage:** Phase 1 (Processor A/B only).

This project implements **a full six-qubit QAOA benchmark on Processor B and a separate exploratory, symmetry-reduced A/B comparison** based on the QFF 2026 Phase 1 Master Challenge Guide, with a deterministic six-node weighted NetworkX instance, QAOA p=1, participant-defined synthetic processors A (5 physical qubits) and B (9 physical qubits), and controlled circuit-resource/noise benchmarks. It includes processor-generating scripts, fixed-seed compilation, exact classical validation, and an automated results/report builder.

## Key verified outcomes

The full **six-logical-qubit** p=1 QAOA run on **nine-qubit Processor B** is recorded in `results/full_six_qubit_reference.json`: depth **57**, **27 CX**, ideal expected cut **11.978903**, noisy 4096-shot mean cut **11.662109** (approximation ratio **72.8882%**), versus classical optimum **16**. This benchmark uses the consolidated kit's *eight-edge B topology* and provisional synthetic noise. **Processor A cannot directly execute six logical qubits on five physical qubits.**

Separately, an exploratory **five-logical-qubit symmetry-fixed** circuit was run identically on participant-designed A and B models. That is useful for architecture comparison but is **not an officially approved way to implement the six-qubit QAOA on A** and is **not directly comparable** with the full six-qubit B result. Read `report.md` sections 5 and 9 for the distinct measurements.

## Critical six-vertex / five-qubit encoding note

The Master Guide specifies **six graph vertices**, but Processor A has only **five physical qubits**. We exploit the exact **global complement symmetry of Max-Cut**: for every bit assignment `x`, complementing every bit gives the same cut weight. Therefore we can fix graph vertex 0 to bit 0 **without changing the set of attainable cut values or classical optimum**. Logical qubits 0 through 4 correspond to original graph vertices 1 through 5; all reported cut values are evaluated on the **original six-vertex graph**. Classical optimum for the generated graph is **16**.

This **does not** mean a five-qubit gauge-fixed QAOA state is identical to the full six-qubit QAOA state or optimization landscape. It is a transparent modelling choice needed for the five-qubit A budget. We use precisely the **same reduced logical circuit** on both A and B. The organiser has explicitly stated (13 October 2026) that this reduction is **not an approved official handling method** at present. See [COMPLIANCE_NOTES.md](COMPLIANCE_NOTES.md) for the conflicting kit guidance and submission limitations.

## Interpretation warning

The current measured Processor A/B results are **exploratory five-qubit symmetry-fixed QAOA**, not a validated full six-qubit implementation. Noise values and native basis are participant modelling assumptions pending organiser clarification. The consolidated Challenge Kit permits treating A as a capacity/routing reference while executing full six-qubit circuits on B. The Master Guide and Challenge Kit also conflict on custom versus fixed coupling maps. Consult [COMPLIANCE_NOTES.md](COMPLIANCE_NOTES.md) before submission.

## One-click notebook reproduction in Google Colab

1. Open [`main.ipynb`](main.ipynb) in Google Colab from the public GitHub repository.
2. Click **Runtime → Run all**. It automatically clones this GitHub repository into Colab if necessary, installs the pinned requirements, and runs **the exploratory reduced A/B comparison plus the full six-qubit Processor B reference**, all benchmark trials, graphs, CSV exports and report generation.
3. After a successful run, Colab automatically downloads a **validated-results ZIP** containing the updated `report.md`, `results/full_six_qubit_reference.json`, and actual experiment results. Replace the files in the GitHub repository with those from the ZIP; commit and push. **Do not submit the template report / missing benchmark results.**

Alternative: clone the repository, install `pip install -r requirements.txt`, run `python -m unittest discover -s tests -v`, then `python run_experiment.py` from the repository root. Python 3.11–3.12 is recommended.

## Provisional experiment settings (not organiser-frozen)

| Setting | Both processors |
|---|---|
| Physical qubit budget | A=5, B=9 |
| Logical qubits | 5 (symmetry-reduced six-vertex Max-Cut) |
| Coupling maps | Participant-defined and justified in `processors/*.json` |
| Basis | `rz`, `sx`, `x`, `cx` |
| Single-qubit depolarizing | 0.001 per `rz`, `sx`, `x` |
| CX depolarizing | 0.005 per CX |
| Readout bit-flip | 0.01 per measured qubit |
| Transpiler optimization | Level 1 |
| Transpiler seed | 42 |
| Shot count | 4096 per run |
| Starting layout | Fixed `[0,1,2,3,4]` on A and B |
| Parameter search | Optimized once for ideal reduced logical QAOA; fixed across A/B |

The synthetic uniformly noisy `rz` gate is a documented modelling assumption for this common benchmark; actual hardware may implement `rz` virtually and with different error behaviour. Neither device is claimed to represent calibrated IBM hardware.

## Repository navigation

- `data/weighted_graph.json` — six-node generated graph, weights and seeds.
- `processors/processor_A.py`, `processor_B.py` — generate the exploratory processor JSONs; `processors/processor_B_kit_reference.json` separately specifies the eight-edge B architecture used for the full six-qubit run.
- `src/problem.py` — deterministic generation, exhaustive classical optimum, symmetry proof, reduced QAOA circuit.
- `src/processors.py` — participant-designed topologies and uniform Qiskit Aer noise model.
- `src/routing.py` — fixed-layout native compilation, unrestricted baseline, non-native SWAP diagnostic.
- `src/metrics.py` and `src/visualization.py` — resource metrics and plots.
- `run_experiment.py` — single-command end-to-end executable.
- `main.ipynb` — Google Colab-compatible guided launcher for the same code.
- `results/tables` and `results/figures` — exported evidence after executing the experiment.
- `report.md` — methods and **measured** conclusions generated after benchmark run.
- `tests/test_basics.py` — tests runnable without Qiskit for core combinatorial and processor configuration assertions.

## Routing and evaluation caveat

The hardware-native target gate set has **no `swap` gate**. A compiled native circuit can consequently have zero *explicit* SWAPs even after physical routing. We therefore report native CX/depth differences, an unrestricted-connectivity compilation reference, **initial-layout shortest-path hop pressure** (a graph-theoretic proxy, not observed SWAP operations), and a separate **non-native SWAP-allowed routing diagnostic**; we never equate these distinct quantities. Results can depend on layout and compiler behavior. The report includes statistical uncertainty and does not infer a hardware advantage from small simulator differences.

## Assistance and participant responsibility

AI tools helped write, debug and document the implementation and experimental protocol. All displayed simulation results must come from an executed run, with the same settings on both processors. Participants must review and understand the methodology and comply with any updated organiser AI-use disclosure policy. Team identity and repository URL are entered in the official submission portal.

## Exact topology mapping for reviewers

**Two B architectures are intentionally used, not interchangeable:** `processors/processor_B.json` is a participant-designed **12-edge** model used only for the exploratory five-logical-qubit A/B analysis; `processors/processor_B_kit_reference.json` is the consolidated kit’s **8-edge** model used by `src/full_six_reference.py` for the full six-qubit B run. Each experiment has different logical ansatz and angles, so compare only within its own protocol. Full six-qubit Processor A metrics are not fabricated because it has insufficient physical qubits.
