# Phase 2B Full Benchmark — Final Report

**Total trials in file**: 1237  
- real: 667
- errored (auth / network / OCP): 570

## Headline — per (method, layer)

| Method | Layer | n | step_export | occt_load | KQP run | KQP fail | rate |
|---|---|---:|---:|---:|---:|---:|---:|
| M0_NoFeedback | EX2 | 29 | 29 | 29 | 29 | 15 | 51.7% |
| M0_NoFeedback | TypeA | 138 | 129 | 129 | 129 | 61 | 47.3% |
| M1_SolverOnly | EX2 | 29 | 29 | 29 | 29 | 15 | 51.7% |
| M1_SolverOnly | TypeA | 138 | 132 | 132 | 132 | 59 | 44.7% |
| M2_KQPOnly | EX2 | 29 | 27 | 27 | 27 | 10 | 37.0% |
| M2_KQPOnly | TypeA | 138 | 120 | 120 | 120 | 55 | 45.8% |
| M3_SolverKQP | EX2 | 29 | 28 | 28 | 28 | 14 | 50.0% |
| M3_SolverKQP | TypeA | 137 | 125 | 125 | 125 | 43 | 34.4% |

## McNemar — M0 vs M2

| Layer | b (M0 pass, M2 fail) | c (M0 fail, M2 pass) | p (exact, two-sided) | direction |
|---|---:|---:|---:|---|
| TypeA | 17 | 23 | 0.4296 | M2 better (M0 fail-M2 pass by 6) |
| EX2 | 2 | 7 | 0.1797 | M2 better (M0 fail-M2 pass by 5) |

## McNemar — M0 vs M3

| Layer | b (M0 pass, M3 fail) | c (M0 fail, M3 pass) | p (exact, two-sided) | direction |
|---|---:|---:|---:|---|
| TypeA | 12 | 29 | 0.0115 | M3 better (M0 fail-M3 pass by 17) |
| EX2 | 6 | 7 | 1.0000 | M3 better (M0 fail-M3 pass by 1) |

## Per-operator — step_export rate

| operator | M0_NoFeedback | M1_SolverOnly | M2_KQPOnly | M3_SolverKQP |
|---|---|---|---|---|
| E1_envelope_u | 22/22 | 22/22 | 19/22 | 20/22 |
| E1_envelope_v_shrink | 21/24 | 21/24 | 21/24 | 20/24 |
| E2_extrude_deep | 41/45 | 44/45 | 41/45 | 43/45 |
| E2_extrude_shallow | 1/1 | 1/1 | 1/1 | 1/1 |
| E3_radius_up | 18/19 | 19/19 | 18/19 | 17/18 |
| E4_void_add | 10/10 | 10/10 | 10/10 | 10/10 |
| E4_void_remove_one | 9/10 | 8/10 | 4/10 | 8/10 |
| E5_extent_type_change | 1/1 | 1/1 | 1/1 | 1/1 |
| E6_inner_gt_outer | 6/6 | 6/6 | 5/6 | 5/6 |
| EX2_coordinate_flip | 29/29 | 29/29 | 27/29 | 28/29 |
