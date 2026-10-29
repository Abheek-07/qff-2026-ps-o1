# QFF 2026 PS-O1 — supplementary synthetic two-channel allocation example

**Separate demonstration only. NOT the organisers' locked six-node graph, mandatory benchmark, quantum experiment or results.csv.** Do not replace official `instances.json`, `main.ipynb` or required submissions. No modifications were made to the team repository.

## Goal
Illustrate an interference-aware two-channel partition of six *hypothetical* cell sectors as weighted Max-Cut. Because strongly conflicting sectors should use different channels, maximising cut is equivalent to minimising residual same-channel penalty under the stated assumptions. The solver is strictly classical.

## Reproduce locally
Requires Python 3.10+ and pip, with networkx and matplotlib:

```bash
python -m pip install -r requirements.txt
python solve_synthetic.py
```

Run these from this directory. The script checks CSV data, evaluates all 64 possible assignments, writes `results.json`, `results_table.csv`, and redraws `network_diagram.png` and `network_diagram.pdf`. Runtime changes at each execution; the bundled results record one actual execution of the script in the build environment. No account or real mobile data is needed.

## Files
- `synthetic_sectors.csv`: 6 hypothetical sectors, schematic coordinates and priority ratings.
- `synthetic_conflicts.csv`: 11 invented interference edges, invented ordinal strength, priorities and computed weights.
- `solve_synthetic.py`: exact enumeration, deterministic seeded random baseline, assertions and chart generation.
- `results.json`, `results_table.csv`: measured solution output and comparison.
- `network_diagram.png` / `.pdf`: channel colouring, edges and random-baseline chart.
- `RESEARCH_AND_MODEL.md`: sources, equations, assumptions, scope and limitations.
- `JUDGES_GUIDE.md`: spoken demo and challenge questions.

## Dataset weight formula
For every conflict pair `(i,j)`, `weight = strength_ij × (priority_i + priority_j)` in arbitrary synthetic penalty units. Schematic coordinates are illustrative only and do not generate the edges or weights. All CSV data is fictional.

## Results from build-environment execution
64 assignments searched; total weight 187; exact maximum cut 140; minimized same-channel conflict 47; two complementary bitstrings `010110` and `101001`; exact expected cut from uniformly random bits 93.5; seeded 1000-sample random mean 92.683. Timing and detailed samples appear in `results.json`. Neither this optimum nor timing is evidence of faster mobile service or quantum advantage.

## Relation to official competition
Original official PS-O1 locked graph and mandatory A/B/D ideal/noisy QAOA benchmark remain separate. This supplemental dataset is **not** automatically comparable to official PS-O1 results and uses its own documented weight scale. Always present the required official tables first.
