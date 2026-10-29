# Research and model — supplementary SYNTHETIC example

**Scope:** Two-channel conflict-aware allocation for six hypothetical mobile cell sectors. This is NOT field data; it does not model or measure a commercial cellular network. It must not replace the locked six-node PS-O1 competition benchmark.

## Official documents inspected
- `OPTIMISATION_PS.docx`: PS-O1 requires locked six-vertex Max-Cut, QUBO, QAOA p=1, exact optimum and processor A/B/D comparisons.
- `QFF2026_Optimization_Challenge_Kit.docx`, especially Sections 3, 6, 10 and 11: locked graph and official settings; additional graphs allowed when labelled.
- `QFF_2026_Phase2_Optimization_Judging_Rubric_2page.pdf`: PS-O1 classical optimum must count BOTH complementary solutions; core criteria prioritize the official benchmark and reproducible processor results.
- Starter pack `instances.json`, `qff_phase2.py`, README, example_usage.py and requirements were inspected as supplied; not modified or copied into this supplement. Official A has only five physical qubits, so it cannot execute the six-qubit PS-O1 instance.

## Credible related literature
1. Shin, Lee and Choi (2024), *A Conflict-Aware Channel Assignment in Multi-Radio Multi-Channel Wireless Mesh Networks*, IEEE Access 12, 14751–14763. https://doi.org/10.1109/ACCESS.2024.3357142 — constructs weighted wireless conflict graphs and relates channel assignment to Max list-Cut.
2. Lee, Shin and Choi (2016), *Weighted conflict-aware channel assignment in 802.11-based mesh networks*, ICACT, 377–381. https://doi.org/10.1109/ICACT.2016.7423400 — develops weighted interference conflicts and Max list-Cut reasoning.
3. Abdelwedoud et al. (2020/2021), *Inference of a Clear Channel Assessment Based Conflict Graph*, Internet Technology Letters. https://doi.org/10.1002/itl2.227 — infers weighted conflict relationships from Wi-Fi access-point measurements.

**Transferability caveat:** These publications largely concern Wi-Fi/mesh networks, not validated LTE/5G interference scheduling. Our example borrows their modelling language, not their empirical outcomes. Our weights and coordinates are invented and not inferred from real measurements.

## Precisely defined instance
- **Vertex** `S0`–`S5`: one hypothetical cell sector; vertices are fixed transmission entities, not users or packets.
- **Binary assignment** `x_i ∈ {0,1}`: 0 = Channel A, 1 = Channel B, assumed orthogonal; both channels available to every sector.
- **Conflict edge** `(i,j)`: the designer assumes the pair would experience mutually relevant co-channel interference. Missing edge means no penalty **within this toy model**, not physical proof of zero interference.
- **Conflict strength** `s_ij ∈ {1,2,3,4,5}`: invented ordinal risk index; not received power, SINR, propagation loss or observed packets.
- **Priority factor** `p_i ∈ {1,2,3}`: invented importance (3 highest); this is not a clinical/emergency-service priority measure.
- **Weight** `w_ij = s_ij (p_i+p_j)`: nonnegative synthetic penalty units if pair shares a channel. This choice prioritizes strong conflicts involving higher-priority sectors; it is illustrative, not a calibrated physical model. We do NOT require these weights to lie in the organiser's 1–5 range because this is an EXTRA, clearly labelled graph, never a required run.
- **Illustrative coordinates**: `schematic_x_km`, `schematic_y_km` are hand-selected for legible display and general geographical plausibility. **They do not determine edges or weights** and are not measured/GPS/cell-layout data. Treat distances as schematic only; do not infer radio range from the drawing.

## Why Max-Cut is appropriate, and exactly when
Let E be listed conflicts, x_i binary and `1[·]` be the indicator of a true statement.

`C(x) = Σ_(i,j)∈E w_ij 1[x_i ≠ x_j]`: total *avoided same-channel penalty*, also called the cut value.

`I(x) = Σ_(i,j)∈E w_ij 1[x_i = x_j]`: total modelled residual same-channel conflict.

For every listed edge exactly one equality is true, hence `I(x)+C(x)=W`, where `W=Σ w_ij=187`. Therefore **argmax C = argmin I**. No empirical claims are required for this algebraic equivalence.

With binary values, `1[x_i ≠ x_j] = x_i+x_j-2x_ix_j`, giving a quadratic unconstrained binary optimisation (QUBO): `max Σw_ij(x_i+x_j-2x_ix_j)`, equivalently minimise its negative. That algebra is directly compatible with a Max-Cut QAOA cost formulation, but no QAOA is performed in this supplement.

**Assumptions essential to equivalence:** exactly two orthogonal channels; every sector can select either; fixed symmetric nonnegative pairwise penalties; penalty incurred fully when two sectors share a channel and entirely avoided when they differ; no channel budgets, capacities, channel-specific costs, interference from unmodelled pairs, or temporal dependencies. If constraints are added, the simple unconstrained Max-Cut may no longer represent the whole problem.

## What this does NOT establish
The solver only finds the mathematically optimal assignment for **this invented objective**. Network throughput, latency, dropped-call probability, coverage, SINR, fairness, energy, spectrum regulations, mobility, real traffic and emergency-call reliability are **not** measured or estimated. Graph layout coordinates are demonstrative. Orthogonal channels and pairwise additive interference are simplifications; in deployed cellular systems frequency reuse, power control, bandwidth, different carrier frequencies, antenna orientation, inter-cell coordination, dynamic load, scheduling, multi-channel needs and regulatory/site constraints matter.

## Measurement interpretation
The classical exhaustive-search timer covers 64 bitstring evaluations, excluding CSV parsing, plotting and file output. It is one local wall-clock observation, **not a rigorous benchmark** (OS load, Python version and hardware affect it). Search complexity is `O(2^n |E|)`, trivial for n=6 but grows exponentially. Sample random baseline is 1000 IID assignments drawn with replacement and fixed seed 2026. Exact uniform random expected cut is W/2=93.5, because each edge is cut with probability 1/2. The random sample mean may differ slightly.
