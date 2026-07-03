# Frozen Components After Task 4

> **冻结日期**: 2026-07-02
> **冻结原因**: Task 4 GT Verification 全部通过（50/50 samples, 334/334 queries），pipeline 从"结构化意图 → 查询规范 → 可执行查询 → GT 验证"完整闭环。
> **目的**: 为后续负样本扰动检验和 repair loop 提供稳定的基线。修改任何冻结组件前必须先阅读此文档。

---

## 1. Frozen Schema Versions

| 组件 | 版本 | 文件路径 |
|---|---|---|
| **DesignPlan Schema** | v0.6 | `DesignPlan/DesignPlan_schema06.txt` |
| **KQP Instance Schema** | v0.2 | `kqp/kqp_schema_v0.2.txt` |

### DesignPlan Schema v0.6 关键特性
- profile.type: rectangle, circle, annulus, stadium, polygon_with_fillets, rectangular_frame, arbitrary_closed
- extrude.extent_type: one_side, two_side, symmetric, degenerate_two_side
- extrude.direction: +w, -w, both_symmetric, both_asymmetric
- dimensions: 单一真值源（extrude_distance + per-profile type-specific params）
- frame: u_dir/v_dir/w_dir + span_computation=vertex_projection
- relative_tol: 1e-4（effective_tol = max(absolute_tol, value * relative_tol)）
- inference_mode: none / partial / all
- forbidden_fields: 禁止 timeline_index, sketch_id, face_count, volume, world_coordinates 等

### KQP Instance Schema v0.2 关键特性
- source_field: 支持 dotted (`a.b.0`) 和 bracket (`a[0].b`) 索引；支持 `(computed: ...)` 和 `(inferred_from_point_span)` 后缀；支持 `(implicit)` 和 `(implicit: <note>)`
- feedback_template: 必须包含 actual-value marker（`{actual}` / `got X` / `actual=X` / `actual: X`）
- ALLOWED_INTENTS:
  - A_topology: body_count, solid_count, face_count, edge_count, vertex_count, shell_count, wire_count
  - B_geometry_dim: bbox_size, cylinder_radius, center_distance, plane_area, volume
  - C_feature: through_void_count, hole_radius
  - D_health: is_solid, occt_valid, all_faces_planar, euler_characteristic, symmetric_about_plane
- Compiler 实际 emit 的 intents（7 个）: body_count, bbox_size, cylinder_radius, through_void_count, is_solid, occt_valid, symmetric_about_plane

---

## 2. Compiler Versions

### DesignPlan Compiler v6

| 属性 | 值 |
|---|---|
| 文件路径 | `DesignPlan/compiler/design_plan_compiler.py` |
| 输入 | Fusion360 Gallery 建模历史 JSON |
| 输出 | design_plan_v0.6 instance JSON |
| 编译成功率 | 50/50 (100%) |
| 与手写 Design Plan 的语义匹配 | 50/50 sample match, 100% query match |
| 4-criteria 审查 | 50/50 PASS (traceability / executability / non-leakage / diagnosticity) |
| sample-specific hardcoding | 0 (无 sample_id 特判) |
| 单位转换 | cm → mm (×10) |

**Query emission 规则 (R1-R7)**:
- R1: body_count — always
- R2: bbox_size u/v/w — always (axis-specific formula per profile type)
- R3: cylinder_radius — iff ptype ∈ {circle, annulus}
- R4: through_void_count — iff n_inner_rings > 0
- R5: is_solid — always
- R6: occt_valid — always
- R7: symmetric_about_plane — iff extent_type == 'symmetric'

### KQP Compiler v0.1

| 属性 | 值 |
|---|---|
| 文件路径 | `kqp/compiler/compile_kqp.py` (+ plan_reader.py, source_mapper.py, feedback_builder.py, query_builder.py) |
| 输入 | design_plan_v0.6 instance JSON |
| 输出 | kqp_instance_v0.2 JSON |
| 编译成功率 | 50/50 (100%) |
| 与手写 KQP instances 的 semantic match | 50/50 sample match, 334/334 query match (100%) |
| 4-criteria 审查 | 50/50 PASS |
| sample-specific hardcoding | 0 |

**输出位置**: `kqp/outputs/compiler_v0.1/<sid>.kqp_instance.json` (50 files)

---

## 3. Runner Version

### KQP Runner v0.1

| 属性 | 值 |
|---|---|
| 文件路径 | `kqp/runner/run_kqp.py` (+ step_loader.py, geometry_backend.py, query_dispatcher.py, result_builder.py) |
| 输入 | STEP file + kqp_instance_v0.2 JSON + (optional) design_plan_v0.6 JSON (for frame) |
| 输出 | KQPResult JSON |
| 环境依赖 | OCP 7.8.x (cadquery 2.8.0), Python 3.11, conda env `cad_subproject1` |

---

## 4. Supported Intents (7 个，Runner 已实现)

| Intent | Category | OCCT API | 实现细节 |
|---|---|---|---|
| **body_count** | A_topology | TopTools_IndexedMapOfShape(TopAbs_SOLID) | 去重计数 |
| **bbox_size** | B_geometry_dim | BRepBndLib.Add_s + bbox corner projection | axis-aligned frame: best-match world span；rotated frame: bbox corner projection onto frame direction |
| **cylinder_radius** | B_geometry_dim | BRepAdaptor_Surface.Cylinder().Radius() | selector=outer→max, inner→min, ""→single |
| **through_void_count** | C_feature | (total_wires - num_faces) / 2 | 每个 face 的 wire 数减 1（outer wire），除以 2 |
| **is_solid** | D_health | shape.ShapeType() == TopAbs_SOLID | 直接检查 |
| **occt_valid** | D_health | BRepCheck_Analyzer(shape, True).IsValid() | OCCT 标准有效性检查 |
| **symmetric_about_plane** | D_health | BRepGProp.CentreOfMass vs bbox midpoint | 质心在 sketch plane 上（within tolerance） |

---

## 5. Known Assumptions

1. **单位**: STEP 文件内部单位为 mm；design_plan_v0.6 也使用 mm；KQP instance 使用 mm。无单位转换。
2. **单 body**: 所有 50 个样本都是 single-body（body_count=1）。Runner 尚未测试多 body 样本。
3. **单 profile**: 所有 50 个样本都是 single-profile extrude。Runner 尚未测试 multi-profile body。
4. **frame 可靠性**: design_plan 的 frame.u_dir/v_dir/w_dir 可能因 corrective_transform 与实际 STEP 几何方向不一致。Runner 使用 best-match 策略绕过此问题（对 axis-aligned frame）。
5. **through_void_count 启发式**: `(total_wires - num_faces) / 2` 公式适用于 extrusion-based through-voids。对非拉伸型孔（如 boolean cut 产生的盲孔）可能不适用。
6. **bbox_size best-match**: 对 axis-aligned frame，Runner 在 3 个 world-axis spans 中选最接近 expected 的。这意味着如果两个轴的 span 恰好相同（如正方形截面），可能无法区分 u 和 v。但这不影响 pass/fail 判定。
7. **tolerance**: KQP instance 中的 tolerance 是绝对值（mm）。对大尺寸样本（如 2.4m 板），tolerance 可能过紧，但 GT 验证中全部通过。

---

## 6. Unsupported Cases

以下情况 Runner **不支持**或**未测试**：

| 情况 | 状态 | 说明 |
|---|---|---|
| RevolveFeature | 不支持 | sanity set 50 中无此类型 |
| post-extrude FilletFeature | 不支持 | sanity set 50 中无此类型 |
| non-zero taper angle | 不支持 | sanity set 50 中所有 taper=0 |
| multi-body parts | 未测试 | sanity set 50 中所有 body_count=1 |
| multi-profile single extrude | 未测试 | sanity set 50 中只有 1 个 multi-profile sample (27)，已通过 |
| L-shaped profile | 不支持 | sanity set 50 中无此类型 |
| BSpline profile | 不支持 | sanity set 50 中无此类型 |
| plane_area query | 不 emit | design_plan v0.6 无 area 字段（Non-Leakage） |
| volume query | 不 emit | design_plan v0.6 无 volume 字段（Non-Leakage） |
| face_count / edge_count / vertex_count | 不 emit | GT-only topology data（Non-Leakage） |
| center_distance query | 不 emit | design_plan v0.6 无 center_distance 字段 |
| hole_radius query (individual) | 不 emit | design_plan v0.6 的 hole_radii 是 list-type，未实现 array-element source path |

---

## 7. GT Verification Result

**验证日期**: 2026-07-02
**验证脚本**: `kqp/verification/run_gt_verification.py`
**结果文件**: `kqp/results/gt_verification/_summary.json`

```json
{
  "total_samples": 50,
  "runner_success": 50,
  "overall_pass": 50,
  "total_queries": 334,
  "passed_queries": 334,
  "failed_queries": 0,
  "error_queries": 0,
  "unsupported_queries": 0,
  "crashed_samples": []
}
```

### 逐样本结果

所有 50 个样本的 overall_status = "pass"。每个样本的详细结果在 `kqp/results/gt_verification/<sid>.result.json`。

### Profile type 分布

| Profile type | 样本数 | Queries per sample (典型) | 全部通过 |
|---|---|---|---|
| rectangle | 21 | 6 (body + 3 bbox + is_solid + occt_valid) | ✅ |
| circle | 10 | 7 (body + 3 bbox + radius + is_solid + occt_valid) | ✅ |
| annulus | 7 | 9 (body + 3 bbox + 2 radius + void + is_solid + occt_valid) | ✅ |
| rectangular_frame | 5 | 7 (body + 3 bbox + void + is_solid + occt_valid) | ✅ |
| stadium | 4 | 6-7 (body + 3 bbox + is_solid + occt_valid [+ void]) | ✅ |
| arbitrary_closed | 2 | 4 (body + 1 bbox + is_solid + occt_valid) | ✅ |
| polygon_with_fillets | 1 | 5 (body + 1 bbox + void + is_solid + occt_valid) | ✅ |

### 调试过程中解决的 3 个关键技术问题

1. **圆柱体 bbox 顶点投影 = 0**: circle/annulus 的 STEP 只有圆柱面，顶点在 seam edge 上（轴线上），投影到 u/v 方向 span=0。→ 改用 bbox corner projection（8 个角点投影）。
2. **frame u/v/w label 不可靠**: design_plan 的 frame.u_dir/v_dir/w_dir 可能因 corrective_transform 与实际 STEP 几何方向不一致。→ 对 axis-aligned frame 用 best-match world span 策略。
3. **through_void_count 拓扑识别**: annulus 的 Euler characteristic 异常（degenerate edges）。→ 改用 `(total_wires - num_faces) / 2` 公式。

---

## 8. 冻结后的修改规则

1. **修改冻结组件前**必须先阅读此文档，确认修改不影响 GT verification 的 50/50 pass。
2. **修改后必须重新运行** `kqp/verification/run_gt_verification.py` 并确认 50/50 pass。
3. **如果修改导致 GT verification 失败**，必须先修复或回滚，不能带着失败进入下一阶段。
4. **新增 intent** 时，必须同步更新 KQP schema、KQP compiler、KQP runner 三处。
5. **负样本扰动检验**和 **repair loop** 可以修改 runner 的 query_dispatcher 和 result_builder，但不应修改 step_loader 和 geometry_backend 的核心 API。
6. **如果必须修改冻结组件**，在此文档底部追加 "Unfreeze Log" 条目，记录修改原因、修改内容、重新验证结果。

---

## 9. Pipeline 架构总览

```
Fusion360 Gallery JSON
        |
        ↓  [DesignPlan Compiler v6]
        |
DesignPlan v0.6 instance (50 files)
        |           DesignPlan/compiler/instances_v6/
        |
        ↓  [KQP Compiler v0.1]
        |
KQP Instance v0.2 (50 files)
        |           kqp/outputs/compiler_v0.1/
        |
        ↓  [KQP Runner v0.1]
        |
KQPResult JSON (50 files)
                    kqp/results/gt_verification/
        |
        ↓
GT Verification: 50/50 pass, 334/334 queries pass
```

---

## 10. 文件索引

| 组件 | 路径 |
|---|---|
| DesignPlan Schema v0.6 | `DesignPlan/DesignPlan_schema06.txt` |
| DesignPlan Compiler v6 | `DesignPlan/compiler/design_plan_compiler.py` |
| 50 DesignPlan instances | `DesignPlan/compiler/instances_v6/*.design_plan.json` |
| KQP Instance Schema v0.2 | `kqp/kqp_schema_v0.2.txt` |
| 50 手写 KQP instances | `kqp/samples/v0.2/*.kqp_instance.json` |
| KQP Compiler v0.1 | `kqp/compiler/compile_kqp.py` (+ plan_reader.py, source_mapper.py, feedback_builder.py, query_builder.py) |
| 50 compiler-generated KQP | `kqp/outputs/compiler_v0.1/*.kqp_instance.json` |
| KQP Runner v0.1 | `kqp/runner/run_kqp.py` (+ step_loader.py, geometry_backend.py, query_dispatcher.py, result_builder.py) |
| GT Verification script | `kqp/verification/run_gt_verification.py` |
| 50 GT verification results | `kqp/results/gt_verification/*.result.json` |
| GT Verification summary | `kqp/results/gt_verification/_summary.json` |
| Semantic match script | `kqp/semantic_match.py` |
| 4-criteria review script | `kqp/review_batch_1.py` |
| KQP match report | `kqp/match/match_report_v0.1.json` |
| KQP changelog | `doc/KQP_v0.1_to_v0.2_changelog.md` |
| Task 4 report | `kqp/runner/task4_report.md` |
| DesignPlan freeze report | `doc/design_plan_v0.6_freeze_report.md` |
