## Measured benchmark summary

```text
 depth  cx_count  explicit_swap_count  single_qubit_gate_count  total_operations  compiled_physical_qubits processor  physical_qubit_budget  logical_qubits  swap_diagnostic_count  swap_diagnostic_depth  unrestricted_cx_count  unrestricted_depth  cx_above_unrestricted  depth_above_unrestricted  extra_hops_proxy  nonlocal_cost_edges  mean_problem_edge_distance  ideal_expected_cut  classical_optimum
    38        24                    0                       46                75                         5         A                      5               5                      4                     32                     12                  21                     12                        17                 6                    5                    2.000000           11.822893                 16
    24        15                    0                       46                66                         9         B                      9               5                      1                     22                     12                  21                      3                         3                 2                    2                    1.333333           11.822893                 16
```

## Noisy trial summary

```text
processor  num_simulator_seeds  shots_per_seed  mean_cut  standard_error  approximation_ratio
        A                    5            4096 11.534668        0.019326             0.720917
        B                    5            4096 11.599072        0.015556             0.724942
```
