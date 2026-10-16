## 7. Processor D concept proposal (Phase 1 design rationale only; NOT implemented)

**Observed problem and feasibility.** The benchmark graph has six vertices. Standard p=1 QAOA requires six logical qubits to encode all six variables, whereas Processor A has five physical qubits. The full six-qubit circuit therefore **cannot be transpiled for A as defined**. We executed the full six-qubit workload on Processor B and independently executed a five-qubit symmetry-fixed circuit on both A and B. Symmetry fixing preserves the classical Max-Cut optimum but changes the quantum ansatz; these results must not be treated as one full-six A/B benchmark.

### Feasibility and measured evidence

| Logical workload | Processor A (5 physical qubits) | Processor B (9 physical qubits) | Valid comparison |
|---|---|---|---|
| Original full six-qubit QAOA | **Infeasible:** insufficient physical qubits | **Executed**, historical eight-edge B topology; native depth **57**, native CX **27**, noisy cut **11.662109** | Full-six B evidence only; **not** an A/B performance comparison |
| Symmetry-fixed five-qubit QAOA | **Executed**, native depth **38**, CX **24**, 5-seed noisy mean cut **11.5347** | **Executed**, native depth **24**, CX **15**, 5-seed noisy mean cut **11.5991** | Matched reduced-ansatz A/B comparison on participant-defined topologies |

The full-six B run uses `processors/processor_B_kit_reference.json`, while the exploratory reduced A/B comparison uses `processors/processor_B.json`; the B circuit-resource metrics must not be combined as though they used a single topology. The historical eight-edge B model and participant-designed 12-edge B model are intentionally distinct and disclosed.

### Proposed Processor D design

**Design hypothesis, not a measured result:** a six-physical-qubit processor whose undirected coupling edges match the nine weighted Max-Cut interaction pairs: `(0,2)`, `(0,3)`, `(0,4)`, `(1,4)`, `(1,5)`, `(2,3)`, `(2,4)`, `(3,4)`, `(3,5)`. This is a *problem-informed topology proposal* rather than an existing hardware configuration. All six logical variables would fit. If logical-to-physical mapping preserves these labels, every original graph-edge ZZ cost interaction has a direct coupling edge, potentially reducing routing SWAPs and decomposed CX overhead compared with sparsely connected alternatives.

**Why this is not a guaranteed speedup.** More couplers mean more complex control, calibration, crosstalk and possibly lower per-link fidelity. Scheduling conflicts, gate synthesis, Qiskit layout choices and measured link errors also influence depth and expected cut. Lower graph distance alone cannot establish a noisy-algorithm advantage, and tailoring D to this single instance may reduce usefulness on other graphs.

**Proposed test methodology (not performed):** use identical six-logical-qubit p=1 QAOA parameters and graph, identical native basis and transpilation optimization level, a documented layout/routing policy, and matched synthetic noise for D and the official twelve-edge B reference (if used for future comparisons). Record native depth, CX count, additional CX versus an unrestricted reference, separately labelled SWAP-allowed diagnostic counts, and noisy expected cut across repeat seeds. Run sensitivity analysis if link-specific noise is introduced. Compare like-for-like full-six workloads only. Report uncertainty and distinguish measured observations from hypotheses.

**Phase boundary:** Per the latest Hackathon Cell clarification, Processor D needs a Phase 1 design rationale in `report.md`, not a completed implementation. No Processor D simulation or offline enhanced Phase 2 task is claimed here. Any enhanced Phase 2 challenge must wait until organisers officially begin that phase.

### Evidence index for evaluators

- Full six-qubit Processor B executed experiment: `results/full_six_qubit_reference.json` and report Section 9.
- Reduced matched Processor A/B circuit metrics: `results/tables/processor_comparison.csv` and `results/figures/architecture_resources.png`.
- SWAP diagnostic, native CX routing overhead and path proxy: `results/tables/routing_diagnostics.csv`; benchmark interpretation in Section 5.
- Noisy performance and trials: `results/tables/noisy_summary.csv`, `results/tables/noisy_trials.csv`, `results/figures/noisy_cut.png`.
- Noise sensitivity: `results/tables/noise_sensitivity.csv` and `results/figures/noise_sensitivity.png`.
- Capacity and differing source guides: `COMPLIANCE_NOTES.md`; precise reproduction protocol in Sections 4 and 8.
