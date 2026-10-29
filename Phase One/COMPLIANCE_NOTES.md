# Phase 1 source reconciliation and submission status — 13 October 2026

## Source of truth and unresolved discrepancies

The team examined the **QFF Phase 1 Master Guide**, the distributed **Updated Challenge Kit**, and the organiser's subsequent written clarification (13 October 2026). The documents are not entirely consistent, so this repository separates **measured experiments** from **provisional benchmark conventions**.

* **Required input:** a six-vertex weighted Max-Cut instance; the nine weighted edges, graph seed, and the exact optimum (16) are unchanged.
* **Capacity conflict:** the Challenge Kit, section 3.1, explicitly states that when a problem needs more than five logical qubits, *do not delete variables solely to fit A*; treat A as a capacity/routing reference and use B for full-size execution. The organiser's more recent response does **not approve** a particular vertex-reduction method and promises further clarification. The existing A/B runs in this repository are an **exploratory five-qubit symmetry-fixed comparison**, **not proof of compliance with a mandated six-qubit A/B benchmark**. Fixing a vertex preserves the classical objective values but changes the QAOA ansatz.
* **Processor graphs:** the Master Guide (page 2) explicitly permits creative, participant-defined connected A/B maps. In contrast, the consolidated Challenge Kit (sections 3.1–3.2) specifies a five-node chain for A and an eight-edge sparse 9-node map for B. The existing graphs follow the Master Guide's design-freedom policy. They are **not identical to the fixed maps described in the Challenge Kit**; results should not be compared to teams using different maps as if they used one common fixed architecture.
* **Noise:** although the written kit and Master Guide show p(1q)=0.001, p(CX)=0.005, and p(readout)=0.01 with basis {rz,sx,x,cx}, the organiser's later message explicitly states that the final noise/basis specification has **not been frozen**. These numbers are **provisional modelling settings**, not approved final official parameters.
* **Phase 1 only:** A and B; no Processor C or D benchmark is required, per the Master Guide and organiser clarification. Some older kit passages still mention C/D and must not override the latest Phase 1 scope.

## What the uploaded benchmark demonstrates

The `report.md` and generated `results/` genuinely document a repeated, reproducible comparison of **the same five-logical-qubit reduced ansatz** on two participant-designed physical graphs (A: 5 physical; B: 9 physical). The reported optimum of 16 is for the **original six-vertex instance**. Device noise is simulated, not real hardware noise. The native-basis SWAP count is not interchangeable with the diagnostic SWAP count.

## Before presenting this as the required final benchmark

1. Ask the organisers whether Phase 1 should use **the six-qubit circuit on B with A as an infeasible capacity reference**, as the consolidated kit states, or whether a reduction is specifically acceptable.
2. Ask whether **Master Guide custom topology freedom** supersedes the kit's fixed A chain/B sparse graph when evaluating Phase 1 submissions.
3. Keep provisional noise values prominently labelled as assumptions until the organisers freeze them.
4. The original full-size six-qubit QAOA has **now been executed on B separately**; see `results/full_six_qubit_reference.json` and report section 9. The earlier reduced A/B data does **not** represent full six-qubit QAOA data, and cross-experiment score comparisons do not isolate topology effects.

## Latest Phase 1 judging clarification (16 October 2026)

The Hackathon Cell Head clarified that **Processor C is not required online**, and that Phase 1 needs an **ideology/design proposal for Processor D in `report.md`**, not Processor D execution. The new judging announcement weights technical correctness 30, A/B benchmarking 25, performance analysis 20, reproducibility 15, and explanation 10, with combined LLM-based (70%) and human (30%) assessment. This latest clarification supersedes earlier kit language suggesting D should be executed during Phase 1. Our Phase 1 Processor D concept is documented in report Section 7. No D benchmarking or enhanced Phase 2 implementation is claimed. The organiser has not explicitly approved the symmetry reduction as the official way to solve the original six-qubit problem on A.
