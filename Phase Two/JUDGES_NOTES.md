# 60-second judges' script — HACKSMITHS

**0–15s:** “Our challenge is weighted Max-Cut: divide six graph vertices into two groups so the sum of edge weights crossing groups is as large as possible. We preserved the organisers’ locked graph. Exhaustive classical checking gives an optimum of 22.”

**15–35s:** “We implemented p=1 QAOA, optimised parameters from five initial seeds, and sampled 4096 shots per configuration. Processor A cannot fit six logical qubits. B has nine physical qubits; our custom D has six. Both have 21 CX gates after transpilation. In noisy simulation, their approximation ratios are about 0.6953 and 0.6961, respectively.”

**35–48s:** “We tested Bell states on adjacent and distant qubit pairs. In the simulated noisy model fidelity is 96.33% on the adjacent pair and 94.69% on the farthest, with more CX gates required for the distant pair.”

**48–60s:** “Our separate synthetic real-world example uses Max-Cut to allocate two radio channels to six fictional cell sectors. Its exact optimum is 140 out of a possible conflict-weight total of 187. This illustrates the method, but does not claim real cellular performance or quantum speedup.”

## If judges ask hard questions
- **Why no quantum advantage?** Six bits have only 64 allocations, trivial to search classically. We compare modelling and circuit engineering, not speedups.
- **Why is D better?** It uses fewer physical qubits; solution quality is essentially tied within one-run sampling variation. We don't claim decisive superiority.
- **Why CX count same?** The transpiler introduces one SWAP and 3 CX overhead in both runs even with different topology; compare actual resources, not assumed benefits.
- **Why two-qubit depth worse on D?** Connectivity/layout trade-offs can increase sequential two-qubit operations while total depth decreases.
- **Why the reversed bitstrings?** Qiskit count labels use a displayed bit ordering different from our graph-vertex indexing; explicitly reverse when evaluating classical cuts.
- **Is Bell fidelity real hardware?** No; these are shot-based Aer simulations under a specified noise model.
- **Why not real towers?** No operator traffic/antenna data. All sector priorities and interference weights are synthetic; two channels are a simplifying model.
- **What's the link to application?** Channel-separated interfering pairs correspond to cut edges; maximizing the cut minimizes the chosen same-channel weight sum.

## What to show in order
1. `results/figures/official_maxcut.png` and optimum 22.
2. `results/figures/qaoa_B_D_comparison.png` plus processor resource table.
3. `results/figures/bell_noisy_comparison.png`.
4. `supplementary_mobile_network/network_diagram.png` and dataset.

**Do not claim full clean-run validation** before rerunning the notebook and output check locally.
