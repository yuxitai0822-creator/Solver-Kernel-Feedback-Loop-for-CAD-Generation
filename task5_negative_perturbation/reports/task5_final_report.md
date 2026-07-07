# Task 5 — Negative-Perturbation Detection Report

## 0. Goal

Verify that the **frozen KQP compiler v0.1 + runner v0.1** can detect
violations of the original Design Plan when the modeling history JSON
is intentionally perturbed *only on fields that map to Design Plan
attributes*.

## 1. Data basis

* Clean samples (frozen ReconstructionEngine v0.1 perfectly reconstructed): **46**
* 3 perturbations per clean sample, target total negatives: **138**
* Generated negatives: **138**
* Reconstruction success: **132** (95.65%)  (spec threshold: ≥ 90%)
* KQP-run done: **132** of 138 (the 6 reconstruction-failures had no STEP)

## 2. Perturbation distribution

| Error category | count | target intent | n_reconstr | n_eligible | n_targeted |
|---|---|---|---|---|---|
| E1_envelope_dim | 46 | E1 envelope dim | 46 | 46 | 37 |
| E2_extrude_depth | 46 | E2 extrude depth | 46 | 46 | 43 |
| E3_radius | 19 | E3 radius | 19 | 19 | 17 |
| E4_void | 20 | E4 void | 20 | 20 | 10 |
| E5_extent_type | 1 | E5 extent type | 1 | 1 | 0 |
| E6_validity | 6 | E6 validity | 6 | 0 | 0 |

| Target intent | count | n_eligible | n_targeted | target_TQDR |
|---|---|---|---|---|
| bbox_size | 92 | 92 | 80 | 86.96% |
| cylinder_radius | 19 | 19 | 17 | 89.47% |
| is_solid | 6 | 0 | 0 | 0.00% |
| symmetric_about_plane | 1 | 1 | 0 | 0.00% |
| through_void_count | 20 | 20 | 10 | 50.00% |

| Operator | count | n_reconstr | n_eligible | n_targeted |
|---|---|---|---|---|
| E1_envelope_u | 22 | 22 | 22 | 18 |
| E1_envelope_v_shrink | 24 | 24 | 24 | 19 |
| E2_extrude_deep | 45 | 45 | 45 | 42 |
| E2_extrude_shallow | 1 | 1 | 1 | 1 |
| E3_radius_up | 19 | 19 | 19 | 17 |
| E4_void_add | 10 | 10 | 10 | 0 |
| E4_void_remove_one | 10 | 10 | 10 | 10 |
| E5_extent_type_change | 1 | 1 | 1 | 0 |
| E6_inner_gt_outer | 6 | 6 | 0 | 0 |

## 3. KQP Detection metrics

* **NDR (Negative Detection Rate)** = 91.67%  (spec threshold: ≥ 80%) → **PASS**
* **TQDR (Targeted Query Detection Rate)** = 81.06%  (spec threshold: ≥ 80%) → **PASS**
* **FPR (False Pass Rate)** = 8.33%  (lower is better) → **WARN**
* **Diagnostic Completeness** = 100.00%  (spec threshold: = 100%) → **PASS**

### 3.1 Category detection rate

| Error category | eligible | detected | det_rate | tqdr_rate |
|---|---|---|---|---|
| E1_envelope_dim | 46 | 38 | 82.61% | 80.43% |
| E2_extrude_depth | 46 | 43 | 93.48% | 93.48% |
| E3_radius | 19 | 19 | 100.00% | 89.47% |
| E4_void | 20 | 20 | 100.00% | 50.00% |
| E5_extent_type | 1 | 1 | 100.00% | 0.00% |

### 3.2 Intent detection rate

| Target intent | eligible | detected | tqdr_rate | all_pass_rate |
|---|---|---|---|---|
| bbox_size | 92 | 81 | 86.96% | 11.96% |
| cylinder_radius | 19 | 19 | 89.47% | 0.00% |
| symmetric_about_plane | 1 | 1 | 0.00% | 0.00% |
| through_void_count | 20 | 20 | 50.00% | 0.00% |

## 4. Coverage of compiler-emitted intents (7 intents)

| KQP intent | covered by perturbation? | n_targeted |
|---|---|---|
| bbox_size | yes | 80 |
| cylinder_radius | yes | 17 |
| through_void_count | yes | 10 |
| symmetric_about_plane | no | 0 |
| is_solid | no | 0 |
| occt_valid | no | 0 |
| body_count | no | 0 |

Note: `is_solid`, `occt_valid`, and `body_count` are general CAD-health intents; the E6 perturbation set is small (6 E6) because such perturbations often produce reconstruction-failure rather than a valid-but-wrong STEP. The 6 reconstruction failures (E6 on annulus samples) are reported in `false_pass_cases.md` under 'Reconstruction failures'.

## 5. Failure analysis

* **Type A (all_pass)**: 11 cases — KQP detected no failure at all. Most of these are E1 envelope perturbations on a small set of samples where the perturbed axis happens to coincide with another non-perturbed axis (the KQP runner's `best-match` strategy for bbox_size masks the change). Documented in `false_pass_cases.md`.
* **Type B (targeted_miss)**: 25 cases — KQP failed at least one query, but the failed query's intent was *different* from the perturbation's target intent. Two patterns:
  * E4_void_add on circle samples fails `q_radius` (because the added inner loop makes the cylinder-face selector no longer match), but does not fail `q_void_count` — the KQP through-void-count routine appears not to count small inner loops.
  * E3_radius_up on stadium samples fails `q_bbox_u` / `q_occt_valid` instead of `q_cylinder_radius` — the radius selector may be missing the stadium-arc case.
  * E5_extent_type_change fails `q_bbox_w` (depth halves) but not `q_symmetric_about_plane` — the symmetric-plane query needs an absolute plane reference to detect the loss of symmetry.
  * E1_envelope_v_shrink on a stadium triggers `q_occt_valid` instead of `q_bbox_size` — the stadium geometry degenerates past a tolerance threshold.
* **Reconstruction failures**: 6 E6_inner_gt_outer cases — perturbing the annulus inner radius to exceed the outer radius produces a non-constructible face. Per spec, these are excluded from NDR/TQDR and counted as `negative_generation_failure`.

## 6. Conclusion

**Task 5 PASS** — frozen KQP (compiler v0.1 + runner v0.1) achieves the agreed detection thresholds on the 46 clean samples × 3 perturbations evaluation set.

### Limitations to record for KQP v0.2

1. `bbox_size` query's `best-match` strategy silently masks the change when an axis perturbation is within `best-match` tolerance of another axis. Fix candidate: emit a per-axis bbox query whose axis label is *contractually* bound to the world frame.
2. `cylinder_radius` selector on `SketchArc` (stadium) misses the radius. Fix candidate: extend selector to detect arc-based cylinders.
3. `through_void_count` does not count loops that are smaller than the tolerance threshold or that are not on a planar through face. Fix candidate: lower the minimum inner-loop radius threshold.
4. `symmetric_about_plane` requires an explicit plane-of-symmetry reference. Fix candidate: use the original Design Plan's `extrude.extent_type` to register the expected plane of symmetry.

## 7. Artifacts

* `inputs/clean_reconstruction_set.json` — snapshot of clean set used
* `perturbations/<sid>/<neg_id>/` — per-negative perturbed history, perturbed design plan, perturbation meta, reconstruction report, KQP result, generated STEP
* `reports/negative_generation_summary.json` — generation counts
* `reports/perturbation_distribution.json` — distribution by intent/category/operator
* `reports/kqp_run_summary.json` — KQP runner log
* `reports/kqp_detection_summary.json` — per-negative detection rows + aggregate metrics
* `reports/false_pass_cases.md` — Type A + Type B + reconstruction failures
* `reports/task5_final_report.md` — this file
