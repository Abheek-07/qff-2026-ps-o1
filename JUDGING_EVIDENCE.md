# Phase 1 judging evidence — QFF 2026 PS-O1

**Scope:** Six-vertex weighted Max-Cut with p=1 QAOA. Current Phase 1 evidence consists of a **full six-qubit run on B** and a **separate symmetry-fixed five-qubit experiment on A and B**. A full six-qubit circuit does **not** fit on five-physical-qubit A. No Processor D execution is claimed; see the design proposal in [report.md](report.md), Section 7.

## Where to find the evidence for each announced criterion

| 16 October judging category | Directly verifiable evidence | Qualification |
|---|---|---|
| Technical correctness (30) | [`src/problem.py`](src/problem.py), [`src/full_six_reference.py`](src/full_six_reference.py), [`data/weighted_graph.json`](data/weighted_graph.json), [`results/full_six_qubit_reference.json`](results/full_six_qubit_reference.json), [`tests/`](tests/) | Exact optimum 16 from all 64 assignments; full-six B ideal mean 11.978903; best sampled cut 16. |
| Processor A/B benchmarking (25) | [`results/tables/processor_comparison.csv`](results/tables/processor_comparison.csv), [`results/tables/noisy_summary.csv`](results/tables/noisy_summary.csv), report Sections 3–5 and 7 | Same **five-qubit reduced ansatz** on A and B, **not** a full six-qubit A/B comparison. Full-six B is separate and A is capacity-infeasible. |
| Performance analysis (20) | [`results/tables/routing_diagnostics.csv`](results/tables/routing_diagnostics.csv), [`results/figures/architecture_resources.png`](results/figures/architecture_resources.png), [`results/figures/noise_sensitivity.png`](results/figures/noise_sensitivity.png), report Section 5 | SWAP-allowed diagnostic counts are **not** executable native SWAP counts. Noise is provisional and synthetic. |
| Code quality/reproducibility (15) | [`main.ipynb`](main.ipynb), [`requirements.txt`](requirements.txt), [`validate_and_package.py`](validate_and_package.py), [`tests/`](tests/), [`results/experiment_metadata.json`](results/experiment_metadata.json) | Run entire notebook or `python validate_and_package.py` in a clean pinned environment; test suite checks stored evidence independently without Qiskit. |
| Technical explanation (10) | [`report.md`](report.md), [`COMPLIANCE_NOTES.md`](COMPLIANCE_NOTES.md), [`docs/processor_d_proposal.md`](docs/processor_d_proposal.md) | Processor D is a **proposed** six-physical-qubit coupling graph; no speedup has been measured. |

## One-minute numerical summary

- **Problem:** 6 original graph vertices; 9 weighted edges; exact weighted optimum **16**.
- **Full 6-logical-qubit QAOA on the historical eight-edge B:** ideal expected cut **11.978903**; 4096-shot noisy mean **11.662109**; noisy ratio **72.888%**; depth **57**, native CX **27**, additional CX versus unrestricted **9**, diagnostic SWAPs **3**. Optimal cut attained in **546/4096** sampled outcomes.
- **Separate matched 5-logical-qubit reduced A/B experiment, participant-defined graphs:** A native depth **38**, CX **24**, noisy mean **11.5347**; B native depth **24**, CX **15**, noisy mean **11.5991**. The full-six B and reduced-five B configurations/angles/topologies must **not** be pooled as a single A/B comparison.

## Additional verified six-qubit B topology evidence

The uploaded Colab run generated [`results/reference_b_comparison/full_six_b_topology_comparison.csv`](results/reference_b_comparison/full_six_b_topology_comparison.csv) and saved compiled circuit text for all three B topology variants. The published 12-link and custom 12-link B designs both yielded depth 38/CX 21 versus historical 8-link B depth 57/CX 27. See report Section 11. This is a full-six **B-versus-B** architecture study, not A/B evidence; don't mix these metrics with the reduced ansatz A/B table.

## Mathematical statement

Maximise `C(x) = Σ_(i,j) w_ij (x_i + x_j - 2 x_i x_j)` for `x_i ∈ {0,1}`. The cost Hamiltonian is `C_hat = (1/2) Σ_(i,j) w_ij (I - Z_i Z_j)`. The classical complement symmetry allows fixing vertex 0 without changing attainable cut values, **but changes the QAOA ansatz** and requires organiser acceptance if used as a required A implementation.

## Reproduction commands

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python validate_and_package.py
```

Running `validate_and_package.py` executes the Qiskit/Aer experiments; the unit tests alone validate mathematics and saved evidence, **not live Qiskit compilation**. Processor design/benchmark conventions are recorded in [`COMPLIANCE_NOTES.md`](COMPLIANCE_NOTES.md). AI assistance is disclosed in the README and report.
