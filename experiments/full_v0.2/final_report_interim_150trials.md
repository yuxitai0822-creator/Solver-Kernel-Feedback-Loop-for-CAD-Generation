# Phase 2B Full Benchmark — Final Report

**Total trials in file**: 707  
- real: 150
- errored (auth / network / OCP): 557

## Headline — per (method, layer)

| Method | Layer | n | step_export | occt_load | KQP run | KQP fail | rate |
|---|---|---:|---:|---:|---:|---:|---:|
| M0_NoFeedback | TypeA | 38 | 35 | 35 | 35 | 17 | 48.6% |
| M1_SolverOnly | TypeA | 39 | 35 | 35 | 34 | 17 | 50.0% |
| M2_KQPOnly | TypeA | 37 | 29 | 29 | 29 | 8 | 27.6% |
| M3_SolverKQP | TypeA | 36 | 30 | 30 | 30 | 10 | 33.3% |

## McNemar — M0 vs M2

| Layer | b (M0 pass, M2 fail) | c (M0 fail, M2 pass) | p (exact, two-sided) | direction |
|---|---:|---:|---:|---|
| TypeA | 1 | 10 | 0.0117 | M2 better (M0 fail-M2 pass by 9) |
| EX2 | 0 | 0 | 1.0000 | no discordant pairs |

## Per-operator — step_export rate

| operator | M0_NoFeedback | M1_SolverOnly | M2_KQPOnly | M3_SolverKQP |
|---|---|---|---|---|
| E1_envelope_u | 8/8 | 8/8 | 7/8 | 7/8 |
| E1_envelope_v_shrink | 8/8 | 8/9 | 8/8 | 6/8 |
| E2_extrude_deep | 11/13 | 12/13 | 10/12 | 11/12 |
| E3_radius_up | 1/1 | 1/1 | 1/1 | 0/0 |
| E4_void_remove_one | 7/8 | 6/8 | 3/8 | 6/8 |
