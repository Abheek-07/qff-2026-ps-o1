# Judge-facing demonstration (60–90 seconds, ~170 words)

“Here is a separate, **synthetic real-world application** of Max-Cut. Our official PS-O1 benchmark remains untouched. Imagine six cellular sectors competing for just two non-overlapping channels. If two interfering sectors use the same channel, our simplified model adds a penalty. We represent the six sectors as graph vertices and 11 potential interference relationships as weighted edges.

Weights are **invented**, not measured: each one equals a conflict-strength score multiplied by the sum of the two sectors' priority scores. Green edges connect sectors placed on different channels, so their conflict penalty is avoided; dashed red edges remain on the same channel.

We evaluated **all 64 possible binary assignments** on a classical computer. The best weighted cut is **140 out of 187**, leaving **47** synthetic conflict units. For comparison, a uniformly random assignment has an exact expected cut of **93.5**. There are two optimal bitstrings, which differ only by swapping the channel labels.

This demonstrates the mathematical mapping and an exact benchmark for a small example. It **does not** establish real cellular throughput, dropped-call improvements or quantum speedup. Actual networks also require radio propagation measurements, scheduling, channel and power constraints, and dynamic optimisation.”

# Ten judge questions and beginner-friendly answers

1. **Why Max-Cut?** An edge is 'cut' if its sectors use different channels. The weighted sum of these cut edges represents conflicts avoided under our simple model.
2. **What do edge weights mean?** An invented penalty: conflict strength times the sum of endpoint priorities. They are not measured radio signals or throughput.
3. **Why is maximizing cut equivalent to minimizing conflict?** Each edge must be either same-channel or cross-channel. The two sums always add to the fixed 187.
4. **Are those real cell tower coordinates?** No. Coordinates are fictional and schematic; they are not used in the weight formula.
5. **How many possibilities did you evaluate?** Two choices per six sectors means `2^6=64`. We evaluate every one, so the optimum is mathematically exact for this dataset.
6. **Why are there two optimal answers?** Swapping every channel 0 to 1 and vice versa leaves every edge's same/different status unchanged.
7. **Where does the 93.5 baseline come from?** Any edge has a 50% chance of spanning two independently random channel labels; half of total weight 187 is 93.5.
8. **Does this prove a QAOA or quantum advantage?** No. This script is classical, and six nodes are easy to exhaustively search. QAOA is investigated separately in the official track.
9. **Can this predict data speed or emergency-call reliability?** No. No propagation, SINR, traffic, scheduling or packet measurements were made. Scores are abstract penalty units.
10. **What changes for real networks?** More channels, frequency-specific interference, constraints on spectrum and equipment, mobility, geographic reach, time-varying traffic, fairness, power control and measurement-based calibration. Max-Cut becomes only one part of a larger optimization system.

# Avoid these claims
Do not say “mobile speed increased by X%”, “interference reduced in the real world”, “emergency calls are safer”, “quantum advantage proven”, or “this is the official PS-O1 instance”. Say “the synthetic same-channel penalty was minimized under our stated assumptions.”
