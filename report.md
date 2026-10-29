# QFF 2026 Phase 2 — PS-O1 verified-results report (local judge draft)

**Team:** HACKSMITHS  
**Evidence:** Uploaded local-run tables (`results.csv`, `resources.csv`, `bell.csv`, `qaoa_five_starts.csv`, `sampled_details.json`) independently checked for numeric consistency. Not independently rerun in Qiskit in this workspace. **Do not claim quantum speedup or real device measurements.**

## Official locked graph and objective
Six vertices, nine weighted edges, total weight 27. Maximize `C(x) = sum_edges w_ij (x_i + x_j - 2*x_i*x_j)`. The classical exhaustive optimum over 64 assignments is **22**, at vertex-order assignments `001011` and `110100`. The uniform random expected cut is **13.5**. Minimize QUBO `-C(x)`; the equivalent cost Hamiltonian is `sum_edges (w_ij/2)*(I-Z_i Z_j)`.

## QAOA method
p=1 with five initial seeds (0–4) and classical Powell optimization using ideal statevector expectation. Recorded best seed is 1 (tied with seed 4), expected exact statevector cut **15.4936201764**. Angles are reused between processors and conditions. Each circuit's output was sampled 4096 times. A is infeasible because 5 physical qubits cannot host 6 logical qubits.

## Recorded comparison

| Metric | B ideal | D ideal | B noisy | D noisy |
|---|---:|---:|---:|---:|
| Mean cut | 15.451660 | 15.469727 | 15.296631 | 15.315186 |
| Approximation ratio (mean / 22) | 0.702348 | 0.703169 | 0.695301 | 0.696145 |
| Probability of optimal cut | 0.118652 | 0.125244 | 0.105225 | 0.113037 |

| Resource | B | D |
|---|---:|---:|
| Physical qubits | 9 | 6 |
| Circuit depth | 37 | 35 |
| Two-qubit depth | 17 | 19 |
| CX gates | 21 | 21 |
| SWAPs | 1 | 1 |
| CX overhead over logical 18 | 3 | 3 |

**Conclusion:** D uses 3 fewer physical qubits (33.3% reduction) while maintaining similar measured quality. The one-run ratio gain is ~0.00084 noisy; **not statistically established**. D has worse two-qubit depth, so do not claim it reduces all routing/noise costs.

## Bell verification
Processor D Bell |Phi+> correlation experiments: adjacent physical pair `(0,2)` at distance 1 (1 CX), farthest selected physical pair `(1,2)` at distance 3 (7 CX). Each measurement basis XX/YY/ZZ uses 4096 shots. Ideal fidelity for both = 1. Noisy adjacent = **0.9632568 ± 0.0020916**; noisy farthest = **0.9468994 ± 0.0024996** (propagated standard errors). Fidelity uses `(1+XX-YY+ZZ)/4`. The difference is an observation under this simulation/noise setup, not proof of distance-only causality.

## Critical bit-order convention
Qiskit count strings are displayed in reverse order to the vertex-order strings in the exact classical table. Recover the cut as `cut(count_key[::-1])`, *not* `cut(count_key)`. With this correction, all recorded sampled mean cuts reproduce exactly.

## Supplementary real-world interpretation
Separate, explicitly **SYNTHETIC** six-sector, two-channel conflict-allocation demonstration; not part of official benchmark. Eleven weighted interference edges, total penalty 187. Exact cut optimum 140; residual same-channel penalty 47. Random allocation expected cut 93.5. A fixed positive weighted conflict graph and two non-interfering channels are simplifying assumptions. No actual cellular traffic/coverage/throughput improvement demonstrated. See supplemental project and research file.

## Limitations and submission caution
Small instance solvable by 64 classical assignments; simulator noise is not physical hardware; one 4096-shot run per condition does not establish D superiority; processor configuration should be signed off as final; ensure official helper and locked input are not changed. The incorporated numerical tables are from the user's actual laptop run but the combined package has **not** been clean-reexecuted as a whole here. Check figure references and notebook before submission.
