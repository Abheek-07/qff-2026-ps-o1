"""QFF 2026 PS-O1: exact, reproducible weighted Max-Cut reference.
Uses the organisers' *unaltered* locked instances.json.
Run: python classical_reference.py
"""
import csv
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'instances.json'
RESULTS = ROOT / 'results' / 'tables'


def load_problem():
    raw = json.loads(DATA.read_text(encoding='utf-8'))['PS-O1']
    n = int(raw['num_vertices'])
    edges = [tuple(map(int, edge)) for edge in raw['weighted_edges']]
    assert n == 6 and len(edges) == 9, 'Official PS-O1 graph unexpectedly changed'
    assert sum(w for _, _, w in edges) == 27, 'Unexpected edge weight sum'
    return n, edges


def cut_value(bits, edges):
    """C(x) = sum_{(i,j)} w_ij [x_i != x_j]."""
    return sum(w for i, j, w in edges if bits[i] != bits[j])


def enumerate_solutions(n, edges):
    solutions = []
    for bits in itertools.product((0, 1), repeat=n):
        solutions.append((''.join(map(str, bits)), cut_value(bits, edges)))
    return solutions


def main():
    n, edges = load_problem()
    solutions = enumerate_solutions(n, edges)
    best = max(score for _, score in solutions)
    best_bits = [bits for bits, score in solutions if score == best]
    mean = sum(score for _, score in solutions) / len(solutions)
    assert best == 22
    assert best_bits == ['001011', '110100']
    assert mean == 13.5
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / 'classical_partitions.csv').open('w', encoding='utf-8', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(('bitstring_x0_to_x5', 'cut_value', 'is_optimal'))
        writer.writerows((bits, score, int(score == best)) for bits, score in solutions)
    print('PS-O1 locked benchmark')
    print(f'Vertices: {n}; edges: {len(edges)}; total weight: {sum(w for _, _, w in edges)}')
    print(f'All possible bitstrings: {len(solutions)}')
    print(f'Classical optimum: {best}')
    print(f'Optimal x0...x5 bitstrings: {best_bits}')
    print(f'Uniform-random expected cut: {mean}')
    print('Saved: results/tables/classical_partitions.csv')


if __name__ == '__main__':
    main()
