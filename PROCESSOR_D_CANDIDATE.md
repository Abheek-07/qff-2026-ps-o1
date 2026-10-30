# Processor D — measured candidate and outstanding release checks

Processor D is a **six-physical-qubit, eight-coupler** hardware-aware candidate for the locked Phase 2 six-vertex Max-Cut instance (nine weighted edges, sum of weights 27, exact classical optimum 22). Its organiser approval is not documented here.

## Design rationale
The unreduced circuit needs six logical qubits. The desired nine ZZ interactions have vertex 4 adjacent to five neighbours; a degree-four physical ceiling means all nine cannot be directly connected with identity mapping. We omitted the weight-one interaction **(2,4)** while retaining (0,2), (0,3), (0,4), (1,4), (1,5), (2,3), (3,4), (3,5). This leaves a connected six-qubit graph with maximum degree four, direct couplings for 8/9 interactions and 26/27 objective weight units. A different weight-one omission may also be valid; our choice is a heuristic, not a proof of global topology optimality.

**Important:** Edge weight is an objective coefficient, not a gate count. A non-direct interaction may be routed and a compiler may select different mappings. Assess architecture via measured transpilation and noisy simulated outcomes.

## Recorded Phase 2 results
| Metric | Processor B | Processor D |
|---|---:|---:|
| Physical qubits | 9 | 6 |
| CX gates | 21 | 21 |
| SWAP diagnostic | 1 | 1 |
| Total depth | 37 | 35 |
| Two-qubit depth | 17 | 19 |
| Noisy approximation ratio | 0.6953014 | 0.6961448 |

The one-run noisy QAOA cut expectations are B=15.29663 and D=15.31519. Both beat the exact **random-assignment expectation 13.5**, but not the **exact classical optimum 22**. These small D–B differences do not establish statistical superiority. The strongest recorded result is similar sampled quality with three fewer physical qubits and a mixed circuit-depth tradeoff. No actual quantum processor or classical runtime speedup is demonstrated.

## Bell-correlation results
Saved Bell experiment CSV uses adjacent pair **(0,2)** and farthest pair **(1,2)**; verify those pairs against the final processor file. Under the bundled simulation, noisy Bell fidelity was approximately 0.9633 adjacent and 0.9469 farthest. These are not physical-device measurements.

## Release conditions
- Re-run **all** cells in `main.ipynb`, save execution counts and outputs, and confirm the ZIP preserves them.
- Re-run checks, compare regenerated tables and plots to the report, and confirm official Processor D topology requirements.
- Do not change the locked official instance or helper code, substitute the synthetic mobile-network dataset, or claim quantum speedup.
- Review `ORGANISER_PROCESSOR_D_FINAL_REVIEW.md` for judge-facing rationale and comparisons.

The zipped notebook uploaded on 30 October 2026 has **four code cells with null execution counts and zero saved outputs**, despite the participant having previously shown a locally executed notebook in VS Code. This is an outstanding *packaging* blocker, not evidence that the participant did not run it.
