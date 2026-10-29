"""Create comparison plots from an actual, completed bell.csv.

This script deliberately refuses missing/incomplete benchmark data. It does not
simulate data or generate sample figures.
Usage: python plot_bell_results.py results/tables/bell.csv --out-dir results/figures
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

REQUIRED = {
    "pair_role", "pair_q0", "pair_q1", "pair_distance", "condition", "shots", "cx",
    "XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se", "fidelity", "fidelity_se",
}
EXPECTED = {("adjacent", "ideal"), ("adjacent", "noisy"),
            ("farthest", "ideal"), ("farthest", "noisy")}


def load_results(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if len(rows) != 4:
        raise ValueError(f"Expected four completed result rows; found {len(rows)}")
    conditions = {(r["pair_role"], r["condition"]) for r in rows}
    if conditions != EXPECTED:
        raise ValueError("CSV must contain adjacent/farthest × ideal/noisy exactly once")
    for i, row in enumerate(rows, 1):
        if int(row["shots"]) != 4096:
            raise ValueError(f"Row {i}: expected 4096 shots, got {row['shots']}")
        for field in ("XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se", "fidelity", "fidelity_se", "cx"):
            value = float(row[field])
            if not math.isfinite(value):
                raise ValueError(f"Row {i}: {field} is not finite")
    return rows


def plot_results(csv_path: Path, out_dir: Path) -> list[Path]:
    rows = load_results(csv_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda r: (r["pair_role"] != "adjacent", r["condition"] != "ideal"))
    labels = [f"{r['pair_role']} {r['condition']}\nq{r['pair_q0']}–q{r['pair_q1']} (d={r['pair_distance']})" for r in ordered]
    x = list(range(len(ordered)))
    outputs: list[Path] = []

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for metric, se_key, marker in (("XX", "XX_se", "o"), ("YY", "YY_se", "s"), ("ZZ", "ZZ_se", "^")):
        ax.errorbar(x, [float(r[metric]) for r in ordered],
                    yerr=[float(r[se_key]) for r in ordered], marker=marker,
                    capsize=4, linewidth=1.5, label=metric)
    ax.axhline(1, linewidth=0.8, linestyle="--")
    ax.axhline(-1, linewidth=0.8, linestyle="--")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Pauli correlation expectation")
    ax.set_ylim(-1.15, 1.15)
    ax.set_title("Bell-state correlations: ideal vs noisy, adjacent vs farthest")
    ax.legend(ncols=3)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    p = out_dir / "bell_correlations.png"
    fig.savefig(p, dpi=180)
    plt.close(fig)
    outputs.append(p)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(x, [float(r["fidelity"]) for r in ordered],
                yerr=[float(r["fidelity_se"]) for r in ordered], marker="o", capsize=5, linewidth=1.5)
    ax.axhline(1, linewidth=0.8, linestyle="--", label="Ideal target F=1")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Bell-state fidelity estimate")
    ax.set_title("Bell-state fidelity with propagated standard error")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    p = out_dir / "bell_fidelity.png"
    fig.savefig(p, dpi=180)
    plt.close(fig)
    outputs.append(p)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(x, [int(r["cx"]) for r in ordered])
    ax.set_xticks(x, labels)
    ax.set_ylabel("Transpiled CX count (ZZ circuit)")
    ax.set_title("Routing / transpilation cost proxy: CX count")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    p = out_dir / "bell_cx_counts.png"
    fig.savefig(p, dpi=180)
    plt.close(fig)
    outputs.append(p)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Actual results/tables/bell.csv")
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    for path in plot_results(args.csv, args.out_dir):
        print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
