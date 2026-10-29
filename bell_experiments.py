"""Reusable QFF 2026 PS-O1 Bell-state benchmark runner.

Uses the organizer-provided qff_phase2.py without modifying it. No Processor D
is bundled or assumed: supply the team's final, validated JSON at runtime.

Required run (from this directory, in the official Python environment):
    python bell_experiments.py --processor path/to/processor_D.json

Default output matches the kit's required location: results/tables/bell.csv.
This script only writes the CSV after all four experiments complete successfully.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import tempfile
from collections import deque
from pathlib import Path
from typing import Any

# Lazy import keeps graph/schema unit tests runnable when Qiskit is not installed.
REQUIRED_SHOTS = 4096  # Official Challenge Kit Section 4; checked against qff_phase2.SHOTS at runtime.

def _official_api():
    try:
        from qff_phase2 import SHOTS, bell_experiment, load_processor, validate_processor_d
    except ImportError as exc:
        raise RuntimeError(
            "Official Qiskit dependencies are unavailable. Install the starter-pack requirements.txt "
            "in Python 3.10–3.12, and keep the unchanged qff_phase2.py beside this script."
        ) from exc
    if SHOTS != REQUIRED_SHOTS:
        raise RuntimeError(f"Official helper SHOTS={SHOTS}, but the Challenge Kit requires {REQUIRED_SHOTS}.")
    return SHOTS, bell_experiment, load_processor, validate_processor_d

# The kit specifies the table contents, not a machine-enforced header schema.
# These explicit columns preserve the requested metrics and their uncertainties.
CSV_FIELDS = [
    "processor", "pair_role", "pair_q0", "pair_q1", "pair_distance",
    "condition", "shots", "cx",
    "XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se",
    "fidelity", "fidelity_se",
]


def _adjacency(num_qubits: int, edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    graph = {q: set() for q in range(num_qubits)}
    for a, b in edges:
        graph[int(a)].add(int(b))
        graph[int(b)].add(int(a))
    return graph


def graph_distances(num_qubits: int, edges: list[tuple[int, int]], source: int) -> dict[int, int]:
    """Unweighted shortest-path distances by BFS; raises if graph is disconnected."""
    graph = _adjacency(num_qubits, edges)
    distances = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for neighbour in sorted(graph[node]):
            if neighbour not in distances:
                distances[neighbour] = distances[node] + 1
                queue.append(neighbour)
    if len(distances) != num_qubits:
        raise ValueError("Processor D coupling graph is disconnected; validate it before pair selection.")
    return distances


def choose_pairs(processor: dict[str, Any]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Choose a deterministic adjacent edge and a graph-diameter pair.

    Tie-break: lexicographically first normalized undirected edge; for diameter,
    lexicographically first normalized pair among all maximum-distance pairs.
    The Processor D design itself is never modified.
    """
    n = processor["num_qubits"]
    edges = sorted({tuple(sorted((int(a), int(b)))) for a, b in processor["edges"]})
    if not edges:
        raise ValueError("Processor D has no edges; cannot select an adjacent pair.")
    adjacent = edges[0]
    all_distances: dict[tuple[int, int], int] = {}
    for source in range(n):
        distances = graph_distances(n, processor["edges"], source)
        for target in range(source + 1, n):
            all_distances[(source, target)] = distances[target]
    diameter = max(all_distances.values())
    farthest = min(pair for pair, distance in all_distances.items() if distance == diameter)
    return adjacent, farthest


def build_rows(processor: dict[str, Any], shots: int = REQUIRED_SHOTS) -> list[dict[str, Any]]:
    """Run the four official aggregate experiments and return four CSV rows."""
    official_shots, bell_experiment, _, validate_processor_d = _official_api()
    if shots != official_shots:
        raise ValueError(f"Required benchmark uses exactly {official_shots} shots per basis; got {shots}.")
    errors = validate_processor_d(processor, required_qubits=6)
    if errors:
        raise ValueError("Processor D validation failed:\n- " + "\n- ".join(errors))

    adjacent, farthest = choose_pairs(processor)
    labelled_pairs = [("adjacent", adjacent), ("farthest", farthest)]
    rows: list[dict[str, Any]] = []
    for role, pair in labelled_pairs:
        # Repeated pair labels are intentional if a valid tiny graph has ties;
        # Processor D still must have >=6 qubits under the official validator.
        for noisy in (False, True):
            result = bell_experiment(processor, pair, noisy, shots=official_shots)
            row = {
                "processor": result["processor"],
                "pair_role": role,
                "pair_q0": pair[0],
                "pair_q1": pair[1],
                "pair_distance": result["pair_distance"],
                "condition": "noisy" if noisy else "ideal",
                "shots": result["shots"],
                "cx": result["cx"],
            }
            for key in ("XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se", "fidelity", "fidelity_se"):
                row[key] = result[key]
            rows.append(row)
    return rows


def write_csv(rows: list[dict[str, Any]], output_path: str | Path) -> Path:
    """Validate and atomically write four completed benchmark rows."""
    if len(rows) != 4:
        raise ValueError(f"Expected exactly four completed aggregate rows; received {len(rows)}.")
    for index, row in enumerate(rows):
        missing = [field for field in CSV_FIELDS if field not in row]
        if missing:
            raise ValueError(f"Row {index + 1} is missing required CSV fields: {', '.join(missing)}")
        if row.get("shots") != REQUIRED_SHOTS:
            raise ValueError(f"Row {index + 1} has shots={row.get('shots')}; expected {REQUIRED_SHOTS}.")
        if row.get("pair_role") not in {"adjacent", "farthest"} or row.get("condition") not in {"ideal", "noisy"}:
            raise ValueError(f"Row {index + 1} has an invalid pair role or condition.")
        q0, q1, distance, cx = (row["pair_q0"], row["pair_q1"], row["pair_distance"], row["cx"])
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (q0, q1, distance, cx)):
            raise ValueError(f"Row {index + 1} pair, distance and CX fields must be integers.")
        if q0 < 0 or q1 < 0 or q0 == q1 or distance < 1 or cx < 0:
            raise ValueError(f"Row {index + 1} has invalid qubit pair, distance or CX count.")
        numeric_fields = ("XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se", "fidelity", "fidelity_se")
        values = {}
        for field in numeric_fields:
            try:
                values[field] = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Row {index + 1}: {field} must be numeric.") from exc
            if not math.isfinite(values[field]):
                raise ValueError(f"Row {index + 1}: {field} must be finite.")
        if any(values[field] < 0 for field in ("XX_se", "YY_se", "ZZ_se", "fidelity_se")):
            raise ValueError(f"Row {index + 1}: standard errors cannot be negative.")
        expected_f = (1 + values["XX"] - values["YY"] + values["ZZ"]) / 4
        expected_f_se = math.sqrt(values["XX_se"]**2 + values["YY_se"]**2 + values["ZZ_se"]**2) / 4
        if not math.isclose(values["fidelity"], expected_f, rel_tol=1e-7, abs_tol=1e-9):
            raise ValueError(f"Row {index + 1}: fidelity does not match the official correlation formula.")
        if not math.isclose(values["fidelity_se"], expected_f_se, rel_tol=1e-7, abs_tol=1e-9):
            raise ValueError(f"Row {index + 1}: fidelity_se does not match propagated standard error.")
    expected_conditions = {("adjacent", "ideal"), ("adjacent", "noisy"),
                           ("farthest", "ideal"), ("farthest", "noisy")}
    actual_conditions = {(row.get("pair_role"), row.get("condition")) for row in rows}
    if len(actual_conditions) != 4 or actual_conditions != expected_conditions:
        raise ValueError("Rows must contain adjacent/farthest × ideal/noisy exactly once.")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temp_name = handle.name
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    return path


def run(processor_path: str | Path, output_path: str | Path = "results/tables/bell.csv") -> Path:
    _, _, load_processor, validate_processor_d = _official_api()
    processor = load_processor(str(processor_path))
    errors = validate_processor_d(processor, required_qubits=6)
    if errors:
        raise ValueError("Processor D validation failed:\n- " + "\n- ".join(errors))
    adjacent, farthest = choose_pairs(processor)
    print(f"Processor D validation: OK ({processor['num_qubits']} qubits)")
    print(f"Selected adjacent pair: {adjacent}; distance=1 (must be a listed edge)")
    print(f"Selected farthest pair: {farthest}; graph diameter pair")
    print("Running 4 aggregate experiments: 2 pairs × ideal/noisy; each uses XX/YY/ZZ × 4096 shots.")
    rows = build_rows(processor, shots=REQUIRED_SHOTS)
    path = write_csv(rows, output_path)
    for row in rows:
        print(
            f"{row['pair_role']:8s} {row['condition']:5s} pair=({row['pair_q0']},{row['pair_q1']}) "
            f"dist={row['pair_distance']} CX={row['cx']} "
            f"XX={row['XX']:+.5f}±{row['XX_se']:.5f} "
            f"YY={row['YY']:+.5f}±{row['YY_se']:.5f} "
            f"ZZ={row['ZZ']:+.5f}±{row['ZZ_se']:.5f} "
            f"F={row['fidelity']:.5f}±{row['fidelity_se']:.5f}"
        )
    print(f"Saved {len(rows)} completed rows to {path}")
    print("These are local Aer simulator results, not physical-hardware measurements.")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processor", required=True, help="Path to the team's final Processor D JSON")
    parser.add_argument("--out", default="results/tables/bell.csv", help="Output CSV (default: results/tables/bell.csv)")
    args = parser.parse_args()
    try:
        run(args.processor, args.out)
    except Exception as exc:
        parser.exit(2, f"BLOCKED/FAILED: {exc}\nNo valid results CSV should be reported.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
