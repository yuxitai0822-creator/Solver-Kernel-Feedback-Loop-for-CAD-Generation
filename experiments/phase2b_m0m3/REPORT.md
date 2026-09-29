# M0-M3 Perturbation Experiment — Report

**Frozen triples input**: 120  
**Trials on disk**: 480 (= frozen × 4 methods; some pairs may be partial if the run was interrupted)  
**Wallclock total**: 82350.7s  

## Per-method final status

| method | success | max_iter_exceeded | no_change | no_script | llm_error | runner_crash | total |
|---|---|---|---|---|---|---|---|
| M0_NoFeedback | 91 | 16 | 13 | 0 | 0 | 0 | 120 |
| M1_SolverOnly | 81 | 29 | 9 | 0 | 1 | 0 | 120 |
| M2_KQPOnly | 111 | 9 | 0 | 0 | 0 | 0 | 120 |
| M3_SolverKQP | 107 | 13 | 0 | 0 | 0 | 0 | 120 |

## Pass-rate by (method, operator)

(rows = operator; columns = method; entry = `success/total (pct)`)

| operator | M0_NoFeedback | M1_SolverOnly | M2_KQPOnly | M3_SolverKQP | all |
|---|---|---|---|---|---|
| E1_envelope_u | 17/19 (89%) | 12/19 (63%) | 18/19 (95%) | 18/19 (95%) | 65/76 (86%) |
| E1_envelope_v_shrink | 15/21 (71%) | 12/21 (57%) | 21/21 (100%) | 19/21 (90%) | 67/84 (80%) |
| E2_extrude_deep | 33/41 (80%) | 29/41 (71%) | 37/41 (90%) | 37/41 (90%) | 136/164 (83%) |
| E2_extrude_shallow | 0/1 (0%) | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) | 3/4 (75%) |
| E3_radius_up | 14/18 (78%) | 13/18 (72%) | 18/18 (100%) | 15/18 (83%) | 60/72 (83%) |
| E4_void_add | 8/9 (89%) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) | 35/36 (97%) |
| E4_void_remove_one | 3/10 (30%) | 4/10 (40%) | 6/10 (60%) | 7/10 (70%) | 20/40 (50%) |
| E5_extent_type_change | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) | 4/4 (100%) |

## Iter-to-success trajectory

Of the trials that ultimately succeeded, how many
iterations did the LLM require?  `1` is best (= passed on
the first attempt given the initial `code_perturbed.py`).

| method | 1 iter | 2 iters | 3 iters | mean |
|---|---:|---:|---:|---:|
| M0_NoFeedback | 86 | 4 | 1 | 1.07 |
| M1_SolverOnly | 77 | 4 | 0 | 1.05 |
| M2_KQPOnly | 85 | 19 | 7 | 1.30 |
| M3_SolverKQP | 82 | 24 | 1 | 1.24 |

## Per-operator mean iter-to-success

| operator | n success | mean iter |
|---|---:|---:|
| E1_envelope_u | 65 | 1.11 |
| E1_envelope_v_shrink | 67 | 1.21 |
| E2_extrude_deep | 136 | 1.14 |
| E2_extrude_shallow | 3 | 1.33 |
| E3_radius_up | 60 | 1.20 |
| E4_void_add | 35 | 1.11 |
| E4_void_remove_one | 20 | 1.50 |
| E5_extent_type_change | 4 | 1.50 |

## Notes

- `success`     = all 3 verifications passed at some iter.
- `max_iter_exceeded` = still failing after 3 iterations.
- `llm_error`   = API / network error (transient, retried on resume).
- `runner_crash` = unhandled exception in the runner (rare).

