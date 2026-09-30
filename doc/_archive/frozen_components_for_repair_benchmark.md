# Frozen Components for Repair Benchmark v0.1

> **Date**: 2026-07-09
> **Status**: FROZEN
> **Purpose**: lock component versions + paths so the benchmark is reproducible
>  and so any defect found during the experiment triggers a version bump
>  rather than a silent patch.

---

## 1. Phase-0 frozen artifacts

| Artifact | Path | Source of truth | Notes |
|---|---|---|---|
| Clean reconstruction set (46) | `Reconstruction_results/clean_reconstruction_set.json` | Reconstruction Engine v0.1 | defines the 46-sample clean set |
| Frozen reconstructed STEPs (46) | `Reconstruction_results/<sid>/generated.step` | Reconstruction Engine v0.1 | KQP GT |
| KQP instance (46) | `kqp/outputs/compiler_v0.1/<sid>.kqp_instance.json` | KQP Compiler v0.1 | per-sample |
| DesignPlan v0.6 (46) | `DesignPlan/compiler/instances_v6/<sid>.design_plan.json` | DesignPlan Compiler v6 | per-sample |
| Original Fusion360 history (46) | `Reconstruction_results/<sid>/input_history.json` | source dataset | for solver feedback |
| Manual IR examples (48) | `cad_ir/samples/manual_ir_examples/` | hand-crafted | validated 100% |
| Negative perturbation records (138) | `task5_negative_perturbation/` | task5 v0.1 | records both passed + failed perturbation attempts |

---

## 2. Component versions

| Component | Version | Path | Frozen on |
|---|---|---|---|
| DesignPlan Schema | v0.6 | `DesignPlan/DesignPlan_schema06.txt` | 2026-07-03 |
| DesignPlan Compiler | v6 | `DesignPlan/compiler/design_plan_compiler.py` | 2026-07-03 |
| KQP Instance Schema | v0.2 | `kqp/kqp_schema_v0.2.txt` | 2026-07-03 |
| KQP Compiler | v0.1 | `kqp/compiler/` | 2026-07-03 |
| KQP Runner | v0.1 | `kqp/runner/` | 2026-07-03 |
| Reconstruction Engine | v0.1 | `reconstruction_engine/` | 2026-07-03 |
| KQP Freeze Report | — | `doc/KQP file/frozen_KQPcomplier&runner.md` | 2026-07-03 |
| Reconstruction Engine Freeze Report | — | `doc/reconstruction engine file/reconstruction_engine_v0.1_freeze_report.md` | 2026-07-03 |
| Solver Feedback (kiwisolver) | v0.1 | `Kiwisolver_feedback/` | 2026-07-08 (reference only, not used in benchmark) |
| Solver Feedback (FreeCAD) | v0.1 | `Freecadsolver_feedback/` | 2026-07-09 |
| CAD IR Schema | v0.1 | `cad_ir/schema/cad_ir_schema_v0.1.json` | 2026-07-09 |
| CAD IR Validator | v0.1 | `cad_ir/validator/validator.py` | 2026-07-09 |
| CAD IR Adaptor | v0.1 | `cad_ir/adaptor/` | 2026-07-09 |
| CED | v0.1 | `cad_edit_distance/` | 2026-07-09 |
| Repair Loop | v0.1 | `cad_repair_loop/` | 2026-07-09 |

---

## 3. Runtime configuration (frozen for this benchmark)

| Setting | Value |
|---|---|
| LLM backend | ZHIPU API |
| Model | glm-5.1 |
| Base URL | `https://open.bigmodel.cn/api/paas/v4/` |
| Temperature | 0.0 |
| Max tokens | 4096 |
| LLM timeout | 120 s |
| LLM retries | 1 (no exponential backoff in V0.1) |
| Adaptor subprocess timeout | 60 s |
| KQP subprocess timeout | 180 s |
| max_iter | 3 |
| Primary success criterion | KQP overall pass |
| Strict success criterion | KQP pass + Solver acceptable |
| Cadquery backend | `D:/Anaconda/envs/cad_subproject1/python.exe` |
| FreeCAD backend (for solver) | `D:/Anaconda/envs/freecad_sketcher/python.exe` |
| Random seed | 42 (LLM temperature 0.0 makes it deterministic) |

---

## 4. Validator rules (frozen)

### 4.1 Schema check
- JSON-Schema validation
- `op_type` enum
- `op_id` uniqueness
- `input` reference existence

### 4.2 Semantic check
- All numeric geometry params strictly positive
- `annulus.inner_radius < outer_radius`
- `frame.inner_* < outer_*`
- `extrude.distance != 0`
- `polygon.vertices` ≥ 3 distinct points
- `cut.target` / `join.target` / `add_constraint.target` reference existing op_ids

### 4.3 Solver Validity (used in M9.0)
- Status ∉ {`conflicting`, `unsolvable`, `invalid_constraint_reference`}
- Under-constrained and redundant are valid (per spec §9)

---

## 5. CED rules (frozen)

| Edit kind | Cost |
|---|---|
| numeric parameter edit | 1 |
| non-numeric parameter edit | 1.5 |
| constraint value edit | 1 |
| constraint type edit | 2 |
| target / reference edit | 2 |
| entity edit (dimension) | 2 |
| add / delete constraint op | 2 |
| add / delete sketch primitive | 2 |
| add / delete feature op (extrude) | 3 |
| add / delete boolean op (cut/join) | 4 |
| add / delete topology op (export_step) | 1 |
| profile type change (rect↔circle) | 4 |
| boolean operation change (cut↔join) | 4 |
| topology structure change | 5 |
| full rewrite flag | 8 |
| `path` field (export_step) | EXCLUDED |

Base weights:
* sketch_* = 2
* extrude = 3
* cut/join = 4
* add_constraint/set_dimension = 2
* export_step = 1

Normalization: `CED = raw / max(weight_a, weight_b, 1)`, clipped to [0, 1].

---

## 6. Adaptor rules (frozen)

* Each IR operation maps to one CAD API call (deterministic).
* Pre-extrude is FORBIDDEN — the profile renderer returns a wire Workplane; the single extrude op consumes all pending wires.
* `add_constraint` and `set_dimension` are no-ops in V0.1 (cadquery doesn't expose these objects).
* STEP path is rewritten to `out_dir / <filename>` by the adapter; Windows-path escape is handled via `repr()`.

---

## 7. Validation freeze

If a defect is found in any of the above during the benchmark, the
experiment is **paused** and the component's version is bumped:

| Component | Bump target |
|---|---|
| DesignPlan | v0.7 |
| KQP | v0.3 instance / v0.2 compiler / v0.2 runner |
| Reconstruction | v0.2 |
| FreeCAD Solver Feedback | v0.2 |
| CAD IR | v0.2 |
| Adaptor | v0.2 |
| CED | v0.2 |
| Repair Loop | v0.2 |

All affected ablations (M0/M1/M2/M3) are re-run from scratch with the
bumped version.  No partial-state results are accepted.