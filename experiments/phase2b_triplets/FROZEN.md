# Frozen Dataset — 120 Verified (sid, nid) Pairs

**Freeze date**: 2026-07-24
**Source**: `experiments/phase2b_triplets/<sid>__<nid>/triplet.json`
**Manifest**: `experiments/phase2b_triplets/_frozen_manifest.json`

These 120 `(sid, nid)` pairs have passed **all three verification layers**
in `triplet.json`:

| Layer | Check |
|---|---|
| L1 | `Code_gt` and `Code_perturbed` both compile/execute/export STEP/load in OCCT. |
| L2 | `CD(Code_gt.step, GT_history.step) < 1e-5` AND KQP queries all pass on `Code_gt.step`. |
| L3 | KQP-flip-diff between `Code_gt.step` and `Code_perturbed.step` matches `T_ref.expected_failed_query`, with extras whitelisted via `OPERATOR_NATURAL_SIDE_EFFECTS`. |

The 18 un-verified triplets (data-side issues: GT STEP malformed on
4 samples, perturbed STEP malformed on 6 E6 samples, both out of
scope per the user spec) are **not** included in this frozen set.

## Per-operator breakdown

| Operator | # triples |
|---|---:|
| E2_extrude_deep | 41 |
| E1_envelope_v_shrink | 21 |
| E1_envelope_u | 19 |
| E3_radius_up | 18 |
| E4_void_remove_one | 10 |
| E4_void_add | 9 |
| E5_extent_type_change | 1 |
| E2_extrude_shallow | 1 |
| **Total** | **120** |

## Per-triple artefacts

For every frozen `(sid, nid)` the directory holds:

```
experiments/phase2b_triplets/<sid>__<nid>/
    code_gt.py             # GT script (CadQuery), copy of the engine output
    code_perturbed.py      # perturbed script, recompiled from perturbed_history.json
    step_gt/
        generated.step     # re-executed GT step (sanity)
        agent.py           # exact source as written to disk
        runner_script.py
        stdout.txt, stderr.txt
    step_perturbed/
        generated.step     # re-executed perturbed step
        agent.py
        runner_script.py
        stdout.txt, stderr.txt
    triplet.json           # L1 + L2 + L3 verdict + frozen=true
```

## What's next

These 120 triples are the **input** for the M0-M3 perturbation
repair experiment (`p2b_m0m3_on_frozen.py`):

- For each `(sid, nid)` and each method `M0_NoFeedback`,
  `M1_SolverOnly`, `M2_KQPOnly`, `M3_SolverKQP`, the runner feeds
  `code_perturbed.py` into the iter loop as the starting script.
- Each iteration runs up to 3 LLM calls + verification rounds.
- The verification considers KQP success vs. the **GT** design plan
  (i.e. the perturbation should be repaired back to a STEP that
  matches the original design).

The frozen triple is read-only for the runner — `triplet.json`
is the canonical record of the input data; iterations are written
to `experiments/phase2b_m0m3/<method>/<sid>/<nid>/`.
