# Latest Phase Two ZIP verification (30 Oct 2026)

Participant-uploaded `Phase Two.zip` checked locally: preflight PASS; check_outputs PASS; verify_release_evidence PASS; 18/18 bell_validation unit tests PASS. Files include figures, result tables, scripts, report, and supplementary dataset.

**Submission blocker:** the uploaded `main.ipynb` has four code cells, all with null execution counts and empty saved outputs. Earlier screenshots showed a completed laptop run, but those notebook outputs are absent from this uploaded archive. Reopen the correct file, Restart & Run All, save, verify cell counts, and create another ZIP before claiming the final archived notebook was run.

**Caution:** Bell validation test output mentions auxiliary selected pairs (0,1) and (0,3); the generated results CSV and current Processor D use adjacent pair (0,2) and farthest pair (1,2). Do not confuse unit-test example stdout with the final recorded Bell experiment.

**Measured conclusions:** D uses 6 physical qubits vs B 9; both 21 CX, 1 SWAP; total depth 35 vs B 37; two-qubit depth 19 vs B 17. Recorded noisy QAOA expected cuts D=15.3152, B=15.2966; random classical expectation=13.5; exact classical optimum=22. No quantum speedup established.

This is a documentation-only review branch; ensure organiser topology approval and final generated notebook evidence before merging.