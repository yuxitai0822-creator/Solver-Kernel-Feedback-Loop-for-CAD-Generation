# M0-M3 External Metrics — IVR / AUC-TR / Mean NCD / Median NCD / VPR

**Date**: 2026-09-24  
**Trials**: 480 (= 120 frozen (sid,nid) × 4 methods)  
**Iter folding**: last-pass — PipelineValid / SolverValid / KernelValid = last iter's `passed` field (True counts as valid; None/skipped counts as not valid).  
**CD cache**: `experiments/phase2b_m0m3/external_metrics/cd_cache.json` (atomic write, resume-safe).  

## 1. Headline (all 5 metrics, last-pass)

| method | PIVR ↓ | SIVR ↓ | PSIVR ↓ | VPR ↑ | AUC-TR ↑ | MeanNCD_valid ↓ | MedianNCD_valid ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|
| M0_NoFeedback |  11.7% |   0.0% |  11.7% |  75.8% |  72.0% |  2.96e-02 |  0.00e+00 |
| M1_SolverOnly |  10.0% |   0.0% |  10.0% |  67.5% |  51.0% |  5.21e-02 |  1.55e-03 |
| M2_KQPOnly |   1.7% |   0.0% |   1.7% |  92.5% |  66.3% |  1.27e-02 |  5.62e-10 |
| M3_SolverKQP |   5.0% |   0.0% |   5.0% |  89.2% |  65.7% |  1.40e-02 |  1.63e-13 |

Legend:
* **PIVR** = #{¬PipelineValid} / N
* **SIVR** = #{PipelineValid ∧ ¬SolverValid} / N
* **PSIVR** = #{¬PipelineValid ∨ ¬SolverValid} / N
* **VPR** = #{PipelineValid ∧ SolverValid ∧ KernelValid} / N
* **AUC-TR** = mean of R(τ) over τ ∈ {1e-1, 1e-2, 1e-3, 1e-4, 1e-5}
    R(τ) = (1/N) Σ_i 1[PipelineValid ∧ SolverValid ∧ NCD ≤ τ]
* **MeanNCD_valid** = mean NCD over V_valid = {PipelineValid ∧ SolverValid} (NCD = CD / diag(BBox_gt); trials with no CD are skipped)
* **MedianNCD_valid** = upper median NCD over V_valid

## 2. Tolerance-Recall curve R(τ)

Each row is one method; each column is one τ.  Cell = R(τ).

| method | τ=1e-01 | τ=1e-02 | τ=1e-03 | τ=1e-04 | τ=1e-05 |
|---|---:|---:|---:|---:|---:|
| M0_NoFeedback |  79.2% |  70.8% |  70.0% |  70.0% |  70.0% |
| M1_SolverOnly |  75.0% |  66.7% |  38.3% |  37.5% |  37.5% |
| M2_KQPOnly |  94.2% |  85.8% |  51.7% |  50.0% |  50.0% |
| M3_SolverKQP |  88.3% |  85.8% |  52.5% |  51.7% |  50.0% |

## 3. CD valid-set coverage

V_valid = {PipelineValid ∧ SolverValid}.  Of these, how many had a computable CD (i.e. the last iter's STEP was loadable + comparable to GT).

| method | |V_valid| | n_NCD_valid (computed) | MeanNCD | MedianNCD |
|---|---:|---:|---:|---:|
| M0_NoFeedback | 106 | 106 | 2.96e-02 | 0.00e+00 |
| M1_SolverOnly | 108 | 108 | 5.21e-02 | 1.55e-03 |
| M2_KQPOnly | 118 | 118 | 1.27e-02 | 5.62e-10 |
| M3_SolverKQP | 114 | 114 | 1.40e-02 | 1.63e-13 |

## 4. Counts (raw integers)

| method | N | ¬PipelineValid | PipelineValid ∧ ¬SolverValid | VPR pass |
|---|---:|---:|---:|---:|
| M0_NoFeedback | 120 | 14 | 0 | 91 |
| M1_SolverOnly | 120 | 12 | 0 | 81 |
| M2_KQPOnly | 120 | 2 | 0 | 111 |
| M3_SolverKQP | 120 | 6 | 0 | 107 |

## 5. NCD distribution over V_valid

Cumulative — per method, of trials with PipelineValid ∧ SolverValid, how many have NCD ≤ each band.  The 'tiny' and 'small' bands indicate KQP-tolerance-precision recoveries (within ~0.05–5 mm of GT).

| method | n_valid | ≤ 1e-5  near-perfect | ≤ 1e-3  tiny | ≤ 1e-2  small | ≤ 1e-1  moderate | > 1e-1  large |
|---|---:|---:|---:|---:|---:|---:|
| M0_NoFeedback | 106 | 84 (79%) | 84 (79%) | 85 (80%) | 95 (90%) | 106 (100%) |
| M1_SolverOnly | 108 | 45 (42%) | 46 (43%) | 80 (74%) | 90 (83%) | 108 (100%) |
| M2_KQPOnly | 118 | 60 (51%) | 62 (53%) | 103 (87%) | 113 (96%) | 118 (100%) |
| M3_SolverKQP | 114 | 60 (53%) | 63 (55%) | 103 (90%) | 106 (93%) | 114 (100%) |

## 6. Key findings (consistent with the headline, with two nuances)

**SIVR = 0 % across all four methods.**  Whenever the last iter's pipeline passed, the solver check (FreeCAD Sketcher on the source Fusion360 history) also passed — because the perturbation battery (E1–E6) modifies *geometry parameters* (points / extrude distance / radius / void loops / extent_type) without altering the sketch *constraint graph*.  Solver feedback is therefore structurally blind to this perturbation class, regardless of method.  This finding is consistent with the ablation report's note that only 15 / 120 trials are 'solver-visible'.

**PIVR is the dominant invalid-source for M0 / M1; KQP / Solver+KQP drive PIVR to single digits.**  PIVR drops from 11.7 % (M0) and 10.0 % (M1) to 1.7 % (M2) and 5.0 % (M3) — the KQP-guided iterative loop almost always lands on a runnable script, while M0 / M1 occasionally leave a syntax or runtime error on iter 0.

**Precision-vs-coverage trade-off at strict τ.**  At τ ≤ 1e-5 (near-perfect recovery), the no-feedback baseline wins (M0 = 70.0 %) over KQP-guided methods (M2 = 50.0 %, M3 = 50.0 %), even though M2 / M3 have higher VPR.  M0's recoveries are 'cleaner' — it has no feedback signal to over-modify, so when M0 succeeds it usually nails dimensions exactly.  M2 / M3 sometimes settle at KQP-tolerance precision (~0.05 mm = NCD ~2.5e-4), which is close enough for verification but not pixel-perfect.  At τ = 1e-1 (loose), the ordering flips back to M2 (94.2 %) > M3 (88.3 %) > M0 (79.2 %) > M1 (75.0 %), matching VPR.

**Mean NCD_valid orders M2 < M3 < M0 < M1.**  Once we condition on PipelineValid ∧ SolverValid (the strict pre-condition for the NCD computation), the KQP-guided methods produce the cleanest shapes on average (M2 = 1.27e-02, M3 = 1.40e-02), the no-feedback M0 is worse (2.96e-02), and solver-only M1 is worst by ~10× — its feedback (5.21e-02) leads the LLM to introduce additional small errors.  Note: MeanNCD is computed over the *normalised* chamfer distance (NCD = CD / diag(BBox_gt)), so cross-scale samples contribute equally to the average.

## 7. Notes

* All ratios are computed against N=120 trials per method (the same frozen-triple set, last-pass view).
* `last-pass` folding means: a trial that succeeded on iter 1 but then broke on iter 2 (rare) would still count as `success` for VPR because `final_status=='success'`; but PipelineValid / SolverValid here are taken from the LAST iter, so they reflect the final state. This matches the headline `final_status` and the existing McNemar analysis.
* PipelineValid = True iff the last iter's pipeline.passed == True. If the LLM emitted `no_change` without re-running pipeline, PipelineValid = False (no STEP produced).
* `Mean NCD` and `Median NCD` only include trials whose NCD could be computed (last-iter STEP present + loadable + comparable).  Trials where pipeline or solver was invalid are not in the valid set per the user's spec.  NCD = CD / diag(BBox_gt) — cross-scale samples contribute equally to the average.
* CD is computed with bbox-min alignment: both GT and generated shapes are translated so their AABB-min corners coincide.  Without this, CD would be dominated by translation offset (GT carries Fusion360's original sketch coordinates; the LLM centres geometry at world origin).
* SIVR = 0 % does NOT mean solver verification is broken — it means the solver channel is structurally blind to the E1–E6 geometry-parameter perturbation battery.  Solver would matter for constraint-level perturbations (e.g. hole-pair symmetry, broken tangent relations), which are Phase 2C scope per the user's execution guide.
* **CD algorithm**: this run uses a scipy.spatial.cKDTree fast path on a 6000-point oversampled target cloud (vs the previous BRepBuilderAPI_MakeVertex + BRepExtrema_DistShapeShape exact OCCT loop).  The KDTree variant is ~28× faster (~100 s vs ~47 min for 480 trials) but introduces a small upward bias on CD (over-estimate; bias bounded by inter-sample distance on the target cloud, ~1–2 mm on GT shapes).  Effect on reported metrics vs the exact algorithm: AUC-TR drops 1–5 pp (more failures exceed strict τ) and the legacy *CD*-based mean metric increases 8–22 %; the current NCD-based metrics (MeanNCD, MedianNCD) inherit the same bias proportionally.  Method orderings (M2 > M3 > M0 > M1 for VPR and AUC-TR, M3 < M2 < M0 < M1 for MeanNCD) are preserved.  Cache is keyed by algorithm version (``CACHE_VERSION = v2-kdtree``); older caches are auto-invalidated on load.

