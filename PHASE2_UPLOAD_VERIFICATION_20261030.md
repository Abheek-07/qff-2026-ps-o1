# Phase 2 repository verification — 30 October 2026

## Current main branch (updated final review)

The earlier review examined an older uploaded `Phase Two.zip` with missing notebook outputs. **That warning no longer describes the current `main` branch.** The current root-level `main.ipynb` has four executed code cells (execution counts 1–4) with saved outputs for: classical optimum **22**, B/D ideal and noisy benchmark rows, Processor D Bell runs, and verification scripts.

The repository contains:
- `Phase One/` archive and Phase 2 implementation at root
- locked `data/instances.json` and organiser helper `qff_phase2.py`
- selected connected six-qubit Processor D configuration
- `results/tables/results.csv`, `resources.csv`, `bell.csv`, `qaoa_five_starts.csv`
- result figures, `report.md`, and synthetic supplementary network demonstration

## Measured conclusions

Recorded noisy mean cuts: **B 15.296631**, **D 15.315186**; classical optimum **22**, random expected **13.5**. D uses six physical qubits versus B's nine; both have 21 CX gates and one SWAP. D total depth is 35 vs B 37, but two-qubit depth is 19 vs B 17. No quantum speedup or statistically established superiority is claimed.

The final Processor D Bell CSV uses adjacent pair (0,2) and farthest pair (1,2). Test fixture pair IDs printed by unit tests are not the measured pair IDs.

## Remaining reproducibility caveat

Recorded laptop execution and saved notebook outputs are visible on GitHub. An **independent fresh-machine, timed, full Qiskit rerun has not been verified in this review**. Do not claim the time threshold was independently confirmed. A missing-output report about an earlier ZIP should not be interpreted as a current notebook failure.

The official repository URL still requires submission through the organisers' designated channel if that channel is separate from GitHub.
