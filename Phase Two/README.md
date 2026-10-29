# QFF Fall Fest 2026 — Phase 2, PS-O1 (HACKSMITHS)

**Official competition instance only:** `data/instances.json` (6 vertices, 9 edges, optimum 22). `qff_phase2.py` is the unchanged organisers’ helper. **Synthetic cellular allocation** is under `supplementary_mobile_network/` and does not replace official evidence.

## Reproduce on a Qiskit-enabled computer

Use Python 3.10–3.12 and open a terminal **inside `Phase Two`**:

```powershell
python -m pip install -r requirements.txt
python preflight_check.py
python -m unittest -v bell_validation
python -m jupyter notebook main.ipynb
```

In Jupyter choose **Kernel → Restart & Run All**. The notebook **reruns** the required p=1 QAOA and ideal/noisy B/D experiments, the Processor D Bell experiments, generates figures and validates output tables. It overwrites saved measurement tables with new actual simulator runs. Save the executed notebook, record environment and duration, and verify a total runtime under the organisers' limit. If notebook use is unavailable, equivalent terminal sequence:

```powershell
python benchmark_phase2.py
python bell_experiments.py --processor processors/processor_D.json --out results/tables/bell.csv
python make_figures.py
python plot_bell_results.py results/tables/bell.csv --out-dir results/figures
python check_outputs.py
python verify_release_evidence.py
```

Data sources: `results/tables/results.csv`, `resources.csv`, `qaoa_five_starts.csv`, `sampled_details.json`, `bell.csv`. `report.md` explains the recorded run, including the Qiskit reversed bit-count display convention and its limits. **All numbers presently in CSVs came from a separate laptop run; this release candidate has not been fully rerun here because Qiskit Aer is unavailable.** No physical hardware runs or quantum advantage claimed. The five ideal optimiser initialisations are **not** repeated independent noisy sampling runs; do not mislabel spread.

## GitHub and submission

Add this folder next to the existing **`Phase One`**, without overwriting it. Root README should link to `Phase Two/README.md`. Do not push until reviewed. Verify the official deadline and that the submitted repository URL points to the right commit. The included output files document the previously recorded run and are not a substitute for a clean notebook rerun. `processor_D.json` remains the team's candidate until formally signed off.
