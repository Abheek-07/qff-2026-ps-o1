# Executed full six-logical-qubit reference (Processor B)

The supplied validated A/B benchmark is symmetry-reduced and does **not** satisfy an unqualified "full six-qubit QAOA on A" requirement. As an additional independent reference, `src/full_six_reference.py` builds the **unreduced six-qubit QAOA p=1** using the unchanged original weighted graph. It optimizes the full six-qubit circuit ideally, then transpires and executes it on **nine-qubit Processor B** using the *fixed B coupling map described in the consolidated Challenge Kit* and **provisional** synthetic noise assumptions.

In an environment with the `requirements.txt` dependencies installed, run:

```bash
python -m src.full_six_reference
```

This creates `results/full_six_qubit_reference.json` **only after actually executing** the reference benchmark. The full six-qubit experiment has been **successfully executed in Google Colab**; its observed results are stored in `results/full_six_qubit_reference.json` (depth 57, 27 CX, mean cut 11.662109 on 4096 noisy shots). Do not confuse these measurements with the original reduced-ansatz A/B results, which use different B topology and ansatz. Processor A cannot directly implement the full six-logical-qubit circuit within five physical qubits. The Master Guide and Challenge Kit conflict about whether the topology is fixed; explicitly document which topology the reported experiment used.

The exact six-qubit benchmark B coupling map is recorded in `processors/processor_B_kit_reference.json` and loaded by the script. This is intentionally distinct from exploratory `processors/processor_B.json`.
