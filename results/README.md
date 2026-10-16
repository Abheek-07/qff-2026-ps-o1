# Experiment results

The authoritative **current** PS-O1 results are in `tables/processor_comparison.csv`, `tables/noisy_trials.csv`, `tables/noisy_summary.csv`, `tables/noise_sensitivity.csv`, and `full_six_qubit_reference.json`. The six-qubit B and reduced five-qubit A/B experiments are **separate, not directly comparable**.

Run `python validate_and_package.py` or the complete `main.ipynb` to regenerate measurements and report.

All active plots are `figures/weighted_graph.png`, `figures/processor_topologies.png`, `figures/architecture_resources.png`, `figures/noisy_cut.png`, and `figures/noise_sensitivity.png`. Older plots for a different four-qubit test were removed because they could mislead evaluators; their data are not part of this experiment.
