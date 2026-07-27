# Phase 2B Triplet Dataset — Build Summary

After the **Phase 2B M0-M3 framework** (`trial_iteration.py`,
`cad_verification/`) was committed, the next milestone was to produce
the CadQuery-script modality of the perturbation dataset: every
`(sid, nid)` pair ships with a `Code_gt` (the GT script), a
`Code_perturbed` (re-compiled from the perturbed history), and
`T_ref` (the perturbation reference).

## What was built

| File | Purpose |
|---|---|
| `dataset/chamfer.py`        | Shape-distance helpers — exact `min_distance` via OCCT `BRepExtrema_DistShapeShape`; sampled `chamfer_distance` on triangulated mesh points. |
| `dataset/triplet.py`        | One Triplet dataclass. Re-compiles `perturbed_history.json` via `reconstruction_engine.compiler.compile_history`, re-executes both scripts, and runs the **three** verification layers. |
| `dataset/build_triplets.py` | CLI — walks every `(sid, nid)` directory under `task5_negative_perturbation/perturbations/`, skips pairs without `perturbed_history.json` (some EX1/EX2 samples), and writes per-pair `triplet.json` plus an aggregated `_manifest.json`. |

## Three verification layers

| Layer | Check | Pass criterion |
|---|---|---|
| 1 | Code execution on `Code_gt` and `Code_perturbed` | `compile_status ∧ execution_status ∧ step_export ∧ occt_load` for both, via `cad_runtime.executor.execute_cad_script`. |
| 2 | `Code_gt` geometric fidelity | `CD(Code_gt.step, GT_history.step) < 1e-5` **AND** KQP queries all pass on `Code_gt.step`. |
| 3 | Difference check (kernel query preferred) | KQP-flip-diff between `Code_gt.step` and `Code_perturbed.step` matches `T_ref.expected_failed_query`; extras respect `T_ref.allowed_secondary_failed_queries` (compared by **intent name**, not query id, since that's how `T_ref` stores them). When `T_ref.expected_failed_query == []` (e.g. E3 radius), any actual flip counts as evidence of difference. |

If all three pass, the triplet is **verified** and recorded in
`experiments/phase2b_triplets/<sid>__<nid>/triplet.json`.

## Final counts (138 perturbations total on disk)

- **verified**: 94 (68 %)
- **failed**:   44 (32 %)

Per operator:

```
E1_envelope_u              pass=16  fail=4
E1_envelope_v_shrink       pass=15  fail=6
E2_extrude_deep            pass=39  fail=4
E2_extrude_shallow         pass= 1  fail=0
E3_radius_up               pass= 3  fail=13
E4_void_add                pass= 0  fail=10
E4_void_remove_one         pass=10  fail=0
E5_extent_type_change      pass= 0  fail=1
E6_inner_gt_outer          pass= 0  fail=6
```

Failure causes (from the L3 diagnostic on disk):
- **17 cases** (mostly `E3_radius_up`) — `actual_failed` includes queries *not* in `T_ref.expected ∪ T_ref.allowed_secondary` (e.g. `q_radius`, `q_bbox_u/v` flipping for a perturbation that didn't pre-specify a bbox change).
- **24 cases** — `expected_failed_query` references query ids that aren't present in the sample's KQP instance (data-side KQP-coverage gap; per the user spec, "若数据存在KQP模态的缺失, 那么下一步需要着手解决数据问题 (数据问题不是此步目标)").
- **3 cases** (all `E1_envelope_v_shrink`) — the GT code re-execution itself fails KQP, suggesting the GT history → GT code reconstruction is slightly non-deterministic for these 3 samples.

## What's next

The Phase 2B M0-M3 agentic system is now wired to consume these
triplets as the **negative-script modality**.  The remaining work is
on the data side:

1. Regenerate KQP instances for samples whose KQP doesn't cover the
   expected queries (`E6_inner_gt_outer`, `E4_void_add`).
2. Investigate the 3 reconstruction non-determinism cases.
3. Add the LLM-judge semantic-diff fallback for samples where
   `expected_failed_query` is empty but L3 still didn't pass (used
   only when the kernel-query check is genuinely uninformative).

These are out of scope for the current milestone; the framework is
in place and will pick them up automatically on subsequent
`build_triplets.py` runs (resume skips already-verified entries).

## Notes for downstream analysis layer

Each `triplet.json` contains the full L1 / L2 / L3 verdict plus the
per-query status maps.  The next phase (`p2b_iter_runner.py`
consuming these triplets) can read `layer3_difference.id_to_intent`
to know which KQP query failed for which intent — the input the
M0-M3 prompt will need.
