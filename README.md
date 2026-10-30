# QFF 2026 Phase 2 — PS-O1 | Team HACKSMITHS

**Submission branch:** `main` · **Problem:** Weighted Max-Cut with p=1 QAOA · **Evidence:** Qiskit Aer simulations (not physical quantum hardware).

## Official benchmark and key findings

The organiser's locked instance is `data/instances.json` (PS-O1): **6 vertices, 9 weighted edges, total weight 27**. Exhaustive classical enumeration of 64 assignments gives maximum cut **22**, with complementary optimum assignments `001011` and `110100` in vertex order. Uniform-random expected cut = **13.5**.

The official 5-qubit **Processor A is not executable** for the unreduced 6-logical-qubit circuit. **Processor B** is the organiser's fixed 9-qubit reference. **Processor D** is our selected, connected 6-qubit, 8-coupling design (max degree 4), recorded in `processors/processor_D.json`. Its physical graph preserves eight weighted problem interactions directly; the omitted weight-1 physical coupling (2,4) does **not** remove the corresponding logical problem edge.

| Recorded metric | Processor B | Processor D |
| --- | ---: | ---: |
| Physical qubits | 9 | 6 |
| Noisy sampled mean cut | 15.296631 | 15.315186 |
| Noisy approximation ratio | 0.695301 | 0.696145 |
| Noisy optimum-sample probability | 0.105225 | 0.113037 |
| Transpiled CX gates | 21 | 21 |
| SWAPs | 1 | 1 |
| Total circuit depth | 37 | 35 |
| Two-qubit depth | 17 | 19 |

**Interpretation:** D needs 33.3% fewer physical qubits than B and slightly less total depth in the recorded run, with similar sampled optimisation quality. **It does not reduce CX/SWAP counts**, has higher two-qubit depth, and the small single-run score difference does **not** prove statistically significant superiority or quantum speedup. Classical exhaustive search reaches the exact optimum of 22.

## Reproduction

Use Python 3.10–3.12, then from **the repository root**:

```powershell
python -m pip install -r requirements.txt
python preflight_check.py
python -m unittest -v bell_validation
python -m jupyter notebook main.ipynb
```

In Jupyter choose **Kernel → Restart & Run All**, save the notebook, and record elapsed time. The notebook calls the documented benchmark and Bell pipelines. It will regenerate result files; seeded simulator sampling is used. Alternatively:

```powershell
python benchmark_phase2.py
python bell_experiments.py --processor processors/processor_D.json --out results/tables/bell.csv
python make_figures.py
python plot_bell_results.py results/tables/bell.csv --out-dir results/figures
python check_outputs.py
python verify_release_evidence.py
```

The `main.ipynb` on `main` contains four executed code cells with saved outputs for the classical reference, B/D benchmark, Bell experiments, and verification. These are **recorded laptop results**, not independently reproduced here in a fresh Qiskit environment. A fully timed clean-environment execution remains an independent reproducibility check.

## Evidence and source

- `main.ipynb` — root-level executable experiment workflow, with saved outputs
- `qaoa_step2.py`, `benchmark_phase2.py` — p=1 QAOA, five ideal parameter starts (seeds 0–4), identical chosen angles on B/D, 4,096-shot ideal/noisy runs
- `data/instances.json`, `qff_phase2.py` — **unchanged official locked problem and starter helper**
- `processors/processor_D.json` — selected Processor D topology and noise settings
- `results/tables/results.csv`, `resources.csv`, `qaoa_five_starts.csv`, `sampled_details.json` — recorded numerical evidence
- `results/tables/bell.csv` — D Bell experiments: adjacent noisy fidelity 0.963257; farthest noisy fidelity 0.946899
- `results/figures/` — recorded graphs
- `report.md`, `ORGANISER_PROCESSOR_D_FINAL_REVIEW.md` — method, hardware design rationale, caveats and comparisons
- `supplementary_mobile_network/` — **separate synthetic**, classical two-channel wireless-sector demonstration; not the locked contest instance and not an empirical mobile network study
- `Phase One/` — unchanged Phase 1 archive; all Phase 2 files are at the repository root

**Limitations:** Simulated noise is not physical-hardware noise; an isolated 4096-shot run does not establish D's superiority, no real-world network throughput or emergency-call improvement is claimed, and the five optimiser starts are not five independent noisy benchmark repetitions. Qiskit count bit order is reversed relative to vertex order; the pipeline handles this via `counts_to_x`. Submit the public repository URL `https://github.com/Abheek-07/qff-2026-ps-o1` through the organiser's required submission channel before its deadline.
