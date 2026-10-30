# Phase 2 final review — Processor D and organiser advice

## Status
Review-branch documentation for PS-O1. The official six-node, nine-edge weighted Max-Cut benchmark has classical optimum **22**, from checking all 64 assignments. A five-qubit Processor A cannot execute the full six-logical-qubit circuit. This document **does not** claim a quantum advantage.

## A credible classical comparison
For a uniform random binary assignment, each weighted edge is cut with probability 1/2. The official total edge weight is 27, so expected random cut = **13.5**. Recorded 4096-shot noisy p=1 QAOA results: Processor B mean cut **15.296630859375** (approximation ratio **0.6953014**), Processor D mean cut **15.315185546875** (ratio **0.6961448**). Both exceed the *random expected value*, but both are well below exact classical **22**. A six-node exhaustive classical solver is extremely effective; neither faster runtime nor better quality than optimal classical search has been demonstrated.

If the organiser wants a comparison against a nontrivial classical algorithm, use a documented greedy/local-search baseline, the *same graph and cut function*, independent random restarts, and total elapsed wall-clock timing; publish measured results in a separate table. A shot-based simulator is not physical quantum hardware.

## How we designed Processor D
1. **Capacity:** six logical Max-Cut variables require at least six physical qubits for unreduced QAOA. B has nine; D uses exactly six.
2. **Workload graph:** the official weighted graph has nine interactions, total weight 27. Its full interaction topology requires degree five at vertex 4, beyond the stated maximum physical degree four.
3. **Connectivity decision:** choose direct couplers for eight of the nine cost interactions, retaining 26 of 27 weighted interaction units under identity mapping; omit the low-weight edge (2,4), weight 1. Another weight-one edge also exists, so this is a heuristic, not a proven optimal or uniquely determined architecture.
4. **Feasibility:** D's undirected links are (0,2), (0,3), (0,4), (1,4), (1,5), (2,3), (3,4), (3,5). The graph is connected; maximum physical degree is four.
5. **Test the hypothesis:** the omitted interaction can be routed via intermediary qubits. Transpilation, layout, noise, and scheduling determine whether the proposed connectivity actually helps. Weight is an objective coefficient, **not** the number of CX gates needed.

## Recorded hardware comparison
| Metric | B | D |
|---|---:|---:|
| Physical qubits | 9 | 6 |
| CX | 21 | 21 |
| SWAP diagnostic | 1 | 1 |
| Total depth | 37 | 35 |
| Two-qubit depth | 17 | 19 |
| Noisy approximation ratio | 0.6953014 | 0.6961448 |

Thus D uses 3 fewer physical qubits and slightly lower total depth but *does not* reduce CX/SWAP counts and has *higher* two-qubit depth. The small one-run fidelity/quality differences do not prove D is superior. Claims concern Qiskit Aer simulations, not physical QPUs.

## Bell and reproducibility
The recorded Processor D Bell pairs are adjacent (0,2) and graph-farthest (1,2). Bell noisy fidelity is around 0.9633 and 0.9469, respectively, **under simulation only**. Preserve the original CSVs and source. User laptop checks (30 Oct 2026) reported: preflight PASS, results validation PASS, pair verification PASS, 18/18 Bell unit tests PASS, and final notebook cell successful. Independently reproducible full Qiskit rerun on another clean environment remains unverified.

Qiskit displayed count strings require reversing keys to match vertex-order classical bitstrings: `cut(count_key[::-1])`.

## Judge demonstration
Show locked graph and exact 22, random baseline 13.5, B/D noisy QAOA approximately 15.30/15.32, topology drawing, and resource CSV. State **why** D's eight couplings were selected, what hardware constraint forced omission, what the compiler actually produced, and what limits the conclusion.

Do not claim QAOA beats exact classical search, statistically significant D superiority, quantum speedup, or real network throughput improvement. The synthetic two-channel mobile-sector application is a *separate* illustrative dataset.

## Release safeguards
Do not merge until the organiser confirms the final Processor D topology and the team verifies the selected notebook/CSV outputs and submission deadline. Keep Phase One and official helper/locked files unchanged.
