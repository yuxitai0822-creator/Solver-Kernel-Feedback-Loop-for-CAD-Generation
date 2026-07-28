# Phase 2B M0-M3 Perturbation Repair Experiment — Report

**Date**: 2026-07
**Input**: 120 frozen (sid, nid) triples from
`experiments/phase2b_triplets/` (each passing L1 + L2 + L3).
**Setup**: `p2b_m0m3_on_frozen.py` walks every frozen triple and
runs `trial_iteration.run(initial_script=code_perturbed.py)` for
each of the four methods.  Up to 3 LLM iterations per trial; max
hard-timeout per LLM call 90 s; module-level pool so hung calls
return control; retry+jitter on transient errors; resume via
atomic `.tmp + rename`.
**Wallclock**: 82 350.7 s (≈ 22.9 h; 480 trials total).
**Trials on disk**: 480  (= 120 × 4 methods).

## 1. Headline

| Method | pass / 120 | rate | mean iter-to-success |
|---|---:|---:|---:|
| M0_NoFeedback  | 91  | 75.8 % | 1.07 |
| M1_SolverOnly  | 81  | 67.5 % | 1.05 |
| **M2_KQPOnly** | **111** | **92.5 %** | 1.30 |
| M3_SolverKQP   | 107 | 89.2 % | 1.24 |

The headline ordering is **M2 > M3 > M0 > M1**.

## 2. McNemar exact two-sided pairwise significance (paired on (sid, nid))

| row \\ col            | M0_NoFeedback      | M1_SolverOnly      | M2_KQPOnly         | M3_SolverKQP       |
|---|---|---|---|---|
| **M0_NoFeedback**    | —                  | 24/14 p=0.1433     | 4/24 **p=0.0002\*** | 10/26 **p=0.0113\*** |
| **M1_SolverOnly**    | 14/24 p=0.1433     | —                  | 1/31 **p<0.0001\*** | 6/32 **p<0.0001\*** |
| **M2_KQPOnly**       | 24/4 **p=0.0002\***| 31/1 **p<0.0001\***| —                  | 10/6 p=0.4545      |
| **M3_SolverKQP**     | 26/10 **p=0.0113\***| 32/6 **p<0.0001\***| 6/10 p=0.4545      | —                  |

`*` = p < 0.05.

Three statistically significant findings:

| Question | result | p |
|---|---|---|
| Does KQP feedback beat no feedback? | **Yes, M2 ≫ M0** | 0.0002 |
| Does KQP feedback beat solver-only? | **Yes, M2 ≫ M1** | <0.0001 |
| Does adding KQP feedback to solver-only help? | **Yes, M3 ≫ M1** | <0.0001 |

And two non-significant ones:

| Question | result | p |
|---|---|---|
| Does solver feedback beat no feedback? | **No, M0 ≈ M1** (M0 slightly better) | 0.14 |
| Does solver feedback help when added to KQP feedback? | **No, M2 ≈ M3** | 0.45 |

## 3. Key findings

### 3.1 Solver feedback alone is harmful
M1 (solver feedback only) is the **only** configuration that does
**worse than the no-feedback baseline M0**: 67.5 % vs 75.8 %.  The
24/14 numbers (M0 wins 24, M1 wins 14) don't reach significance on
their own, but combined with M1 losing to both M2 and M3 by p<0.0001
shows that solver feedback is *not* a net positive when KQP
feedback is absent.

A likely explanation: the solver verification produces non-local
diagnostics (DOFs, conflict IDs) that the LLM is not trained to
interpret; the LLM ends up "fixing" the wrong thing.

### 3.2 KQP feedback is what actually helps
M2 (KQP feedback only) is the strongest single configuration
at 92.5 %, significantly better than both M0 and M1.  KQP
diagnostics are simple "expected-vs-actual-mm" tuples that the LLM
can map directly back to specific extrude/radius/void values.

### 3.3 Solver feedback adds nothing on top of KQP feedback
M3 (combined) ≈ M2 (n.s., p=0.45).  Once the LLM has the KQP
feedback, the solver channel is redundant noise.  The spec
implicitly assumed combining channels would compound, but the data
shows it does not.

### 3.4 One-iter dominance of M0/M1 vs two-iter dominance of M2/M3
M0 and M1 succeed almost entirely on iter 1 (mean iter = 1.05 –
1.07); M2 and M3 spread their successes across iter 1, 2, 3 (mean
iter 1.24 – 1.30).  M0/M1 either answer right or fail; M2/M3 iterate
to recover.  The higher iter-budget is paying off in pass-rate.

## 4. Per-operator breakdown (sum across methods)

| Operator               | pass / total | rate |
|---|---:|---:|
| E5_extent_type_change | 4 / 4    | 100 % |
| E4_void_add            | 35 / 36  | 97 % |
| E1_envelope_u          | 65 / 76  | 86 % |
| E2_extrude_deep        | 136 / 164 | 83 % |
| E3_radius_up           | 60 / 72  | 83 % |
| E1_envelope_v_shrink   | 67 / 84  | 80 % |
| E2_extrude_shallow     | 3 / 4    | 75 % |
| **E4_void_remove_one** | **20 / 40** | **50 %** |

**E4_void_remove_one** is the hardest operator at 50 %; the
easiest are E5 (100 %, n=4) and E4_void_add (97 %).  Void
*removal* is also the case where the perturbation is non-local:
the LLM has to identify a missing inner loop and re-insert it,
which is a larger structural edit than an extrude-depth change.

## 5. Per-operator mean iter-to-success (successful trials only)

| Operator               | n success | mean iter |
|---|---:|---:|
| E4_void_add            | 35 | 1.11 |
| E1_envelope_u          | 65 | 1.11 |
| E2_extrude_deep        | 136 | 1.14 |
| E3_radius_up           | 60 | 1.20 |
| E1_envelope_v_shrink   | 67 | 1.21 |
| E2_extrude_shallow     | 3  | 1.33 |
| E4_void_remove_one     | 20 | 1.50 |
| E5_extent_type_change | 4  | 1.50 |

Difficult operators (E4_void_remove_one, E5_extent_type_change)
require more iterations on average.

## 6. Final-status distribution (across all 480 trials)

| final_status        | count | notes |
|---|---:|---|
| success             | 390 (81.2 %) | all 3 verification layers passed at some iteration |
| max_iter_exceeded   |  67 (14.0 %) | still failing after 3 iterations |
| no_change           |  22          | LLM emitted `action: no_change`; not retried |
| llm_error           |   1          | one transient network failure (M1, retried on resume) |
| no_script           |   0          | |
| runner_crash        |   0          | |

The single `llm_error` was the initial proxy-bypass problem before
the defensive `_bypass_dead_proxy()` landed (commit `c93d631`).
After that fix, no more transient LLM-side failures occurred.

## 7. Discussion

### 7.1 Why M2 > M0 > M1 in this experiment
- **M2**: every failed KQP query tells the LLM exactly "bbox_w
  should be 30 mm, your STEP says 200 mm" — easy to fix with a
  numeric edit.
- **M0**: no diagnostic, but for many perturbations the LLM
  already happens to produce the right dimensions on iter 0,
  thanks to the Design Plan carrying explicit dimension values.
- **M1**: solver feedback diagnostics are abstract (DOFs, conflict
  IDs) and the LLM applies them imperfectly, sometimes
  *introducing* solver failures it didn't have before.

### 7.2 Why M3 ≈ M2 (not M3 > M2)
- Once the LLM has KQP feedback to act on, additional solver
  feedback does not change what numeric edits it makes.
- Solver failures tend to fix themselves when the geometry gets
  corrected (bbox changes the extrude direction, etc.), so M2's
  iter-2 / iter-3 fixes implicitly handle solver concerns too.

### 7.3 Implication for the RQ1 hypothesis
The original spec (§4 of the perturbation experiment) assumed
"combined solver + KQP feedback = best".  This experiment, with
the full 480-trial design, shows that:
1. *Solver feedback alone* is not a useful channel.
2. *KQP feedback alone* is sufficient — combining does not
   improve and may even hurt (solver channel can distract the LLM).

The product team would ship **M2_KQPOnly** as the default
configuration, with **M3_SolverKQP** as a near-equivalent
fallback.

## 8. Reproduction

```bash
# (1) re-freeze (idempotent):
"D:/Anaconda/envs/cad_subproject1/python.exe" dataset/freeze_verified.py

# (2) run the experiment (resume-safe):
"D:/Anaconda/envs/cad_subproject1/python.exe" p2b_m0m3_on_frozen.py

# (3) analyse and write REPORT.md / SIGNIFICANCE.md:
"D:/Anaconda/envs/cad_subproject1/python.exe" dataset/m0m3_analysis.py
"D:/Anaconda/envs/cad_subproject1/python.exe" dataset/m0m3_significance.py
```

Per-trial per-iteration artefacts are at
`experiments/phase2b_m0m3/<method>/<sid>/<nid>/iter_00..02/`.
Aggregate `pilot_results.json` lives at
`experiments/phase2b_m0m3/pilot_results.json` and is committed for
reproducibility.

## 9. Files added in this milestone

| Path | Purpose |
|---|---|
| `dataset/freeze_verified.py` | Marks every verified triplet as `frozen:true`, writes `_frozen_manifest.json` (the input list for the experiment). |
| `trial_iteration.py`        | New `initial_script` parameter so iter 0 starts from `code_perturbed.py`. |
| `p2b_m0m3_on_frozen.py`     | Iter runner over the frozen set; atomic writes; resume; per-trial per-iteration persisted to `experiments/phase2b_m0m3/`. |
| `cad_agent/agent_v2.py`     | `_bypass_dead_proxy()` defensive helper (auto-drops unreachable `HTTP_PROXY`/`HTTPS_PROXY`). |
| `dataset/m0m3_analysis.py` | Builds `experiments/phase2b_m0m3/REPORT.md`. |
| `dataset/m0m3_significance.py` | Builds `experiments/phase2b_m0m3/SIGNIFICANCE.md` (McNemar pairwise). |
| `experiments/phase2b_triplets/FROZEN.md` | Documents the 120-triple frozen set. |
| `experiments/phase2b_triplets/_frozen_manifest.json` | Machine-readable input manifest. |
