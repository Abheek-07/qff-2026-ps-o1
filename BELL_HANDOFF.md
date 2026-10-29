# Bell-state verification handoff — HACKSMITHS / QFF 2026 PS-O1

## Implemented and verified in preflight
- The reported `SHOTS` NameError is fixed in this copy: the runner checks and forwards the official 4096 shots per basis.
- CSV validation checks the four required pair/condition combinations, required fields, integer pair/distance/CX metadata, finite correlations and uncertainties, non-negative standard errors, and consistency of fidelity and propagated uncertainty with the official formulas.
- CSV writing is atomic; the runner does not write a results CSV unless all four experiment calls return successfully.
- Added mocked runner tests. They verify API call count/order, 4096-shot forwarding, validation-before-experiment behavior, and no partial CSV after a simulated exception. Mocked tests are not quantum simulations.
- Plot generator refuses incomplete or non-finite data and creates correlation, fidelity and CX-count plots only from a complete CSV.
- `qff_phase2.py` is byte-for-byte identical to the official helper.

## Candidate Processor D static findings
The supplied candidate has 6 qubits and 8 edges; it is connected, maximum degree 4, and uses the required basis-gate set. The deterministic adjacent pair is `(0,2)`; the unique diameter pair is `(1,2)` at graph distance 3. These are static checks; official `validate_processor_d()` still needs to run in the compatible Qiskit environment.

## Required team-lead decision
**Please explicitly confirm whether `processor_D.json` in this package is the exact configuration to freeze for submission.** It is labelled a candidate and is not assumed final. If not, provide the final JSON path/file. Do not publish benchmark results against the candidate until approved.

## Run after confirmation
Use Python 3.10–3.12 and install the supplied requirements in a clean virtual environment:
```bash
python -m pip install -r requirements.txt
python -m unittest -v bell_validation.py
python bell_experiments.py --processor path/to/final/processor_D.json --out results/tables/bell.csv
python plot_bell_results.py results/tables/bell.csv --out-dir results/figures
```

The four runs are adjacent/ideal, adjacent/noisy, farthest/ideal, farthest/noisy. Each uses the official `bell_experiment()` helper for XX, YY and ZZ at 4096 shots per basis. Keep terminal output and Python/Qiskit/Aer versions with the results.

## Honest current status
- Syntax compilation: passed.
- Unit tests: **18/18 passed**, including mocked runner tests.
- Official helper byte comparison: passed.
- Actual Qiskit/Aer simulations: **not run** (runtime is Python 3.13.5 and Qiskit/Aer are absent).
- Actual `results/tables/bell.csv` and result plots: **not generated**.
- No GitHub changes or pushes made.
