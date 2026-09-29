# Phase 2 — Perturbation (Raw Negatives)

## 描述
扰动构造阶段。从 phase0_initial.history 出发，由 17 个 operator 派生 138 个 negative cases（50 source × 平均 2.76 operator/case，4 个 source 在 EX 路径下失败）。

## 17 个 operator 分 7 类

| Family | Function | 作用 |
|---|---|---|
| E1 envelope | `op_E1_envelope(axis, scale)` | u/v 轴等比缩放 outer loop |
| E2 extrude depth | `op_E2_extrude_depth(scale)` | extrude.extent_one.distance 缩放 |
| E3 radius | `op_E3_radius(scale, target)` | circle/arc 半径缩放 |
| E4 void | `op_E4_void_remove/add` | 删除/添加 inner loop |
| E5 extent type | `op_E5_extent_type()` | one_side ↔ symmetric |
| E6 zero/inverted | `op_E6_zero_*` / `inner_gt_outer` | 极端值触发 is_solid/occt_valid fail |
| EX1/EX2 | `op_EX1_sketch_plane_swap` / `op_EX2_coordinate_flip` | frame-level 扰动 |

## Lineage
- `operators/` ← 17 个 operator wrapper（deterministic）
- `artifacts/<sid>/<neg_id>/` ← operator 应用结果：perturbed_history, perturbed_design_plan, perturbed_cad_ir, perturbed_script, perturbed.step, perturbation_meta, kqp_result, reconstruction_report

## Not frozen
扰动 raw 产物本身是中间产物，最终 verified 数据集在 phase3_triplets。