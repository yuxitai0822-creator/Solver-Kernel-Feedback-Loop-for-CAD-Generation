# KQP Schema v0.1 → v0.2 Changelog (All Batches: samples 1-50)

> **本轮结论**：50/50 KQP instances 全部通过 4-标准审查（traceability/executability/non-leakage/diagnosticity）。**v0.2 schema 已最终冻结**。所有 50 个 hand-written KQP instances 与 v0.2 schema 完全兼容。**为后续 KQP compiler 的设计目标提供完整 ground truth**。

## 1. 各 Batch 交付情况

| Batch | Samples | 数量 | 关键 profile 类型 | 4-标准审查 | 备注 |
|---|---|---|---|---|---|
| 1 | 1-5 | 5 | rectangle x 5 | 0 issues | 模板建立 |
| 2 | 6-10 | 5 | rectangular_frame x 4, rectangle x 1 | 0 issues | 覆盖 rectangular_frame |
| 3 | 11-20 | 10 | rectangle, annulus, stadium, polygon_with_fillets | 0 issues | 含 1 修复：stadium sample bbox_u 错误 |
| 4 | 21-30 | 10 | circle (含 first negative extrude), rectangle, stadium+2holes, arbitrary_closed, rectangular_frame | 0 issues | 含 0-dim rectangle 和 negative extrude circle |
| 5 | 31-40 | 10 | stadium+2holes (degenerate_two_side), annulus (symmetric, dir=-w), arbitrary_closed, circle (flipped frame) | 0 issues | 含 symmetric_about_plane intent |
| 6 | 41-50 | 10 | annulus, rectangle (large panel), circle, rectangle_0d (0-dim) | 0 issues | 含 0-dim rectangle |
| **总计** | **1-50** | **50** | 7 种 profile | **0 issues** | **50/50 PASS** |

## 2. 4-标准审查结果 (`KQP/review/batch_1_review.json`)

| 标准 | 问题数 |
|---|---|
| Traceability | 0 ✅ |
| Executability | 0 ✅ |
| Non-Leakage | 0 ✅ |
| Diagnosticity | 0 ✅ |
| **Total** | **0 ✅** (50 KQP instances) |

## 3. v0.1 → v0.2 Schema 升级内容

### 3.1 source_field 路径语法：Dotted + Bracket + Array Index

v0.1 隐含只支持 `.N`；v0.2 显式支持：
- 点索引: `solid_bodies.0.dimensions.extrude_distance.value`
- 括号索引: `solid_bodies[0].dimensions.profiles[0].length_u.value`
- 数组元素: `profiles.0.dimensions.profiles.0.hole_radii[0].value` (支持 polygon_with_fillets)
- 计算表达式后缀: `<path> (computed: <expr>)` 或 `<path> (inferred_from_point_span)`

### 3.2 `(implicit: <note>)` 形式

v0.1 只接受 `(implicit)`；v0.2 接受 `(implicit: <description>)`，仅 D_health query 允许。

### 3.3 feedback_template "actual" 标记符

v0.2 明确：feedback_template 必须包含 actual-value marker：
- `{actual}` (推荐)
- `got X`, `actual=X`, `actual: X` (可接受)

`{expected}` 是可选的（硬编码预期值同样可读）。

### 3.4 symmetric_about_plane intent (v0.2 新增)

batch 5 中 sample 32 (symmetric bearing) 需要验证 body 关于 sketch plane 的对称性。v0.2 schema 的 D_health.ALLOWED_INTENTS 添加了此 intent。Compiler 仅在 design_plan.extrude.extent_type='symmetric' 时 emit。

## 4. 决策

✅ **v0.2 schema 已最终冻结**。

修改跟踪：

| 版本 | 时间 | 关键变化 | 触发原因 |
|---|---|---|---|
| v0.1 | 上一轮 | 初始 schema 定义 | 50 v6 design_plan 字段枚举 |
| **v0.2 (frozen)** | 本轮 (batches 1-6) | 形式化 path syntax、implicit 形式、computed 表达式、actual 标记、新增 symmetric_about_plane intent | 50 instances 手写 + 4-标准审查的 findings |
| v0.3 | 待定 | 视下一轮需求 | — |

## 5. v0.2 schema 下一步使用

50 个 KQP instances (samples 1-50) 已全部完成并通过 4-标准审查，构成 KQP compiler 的完整 ground truth。下一阶段：

1. **KQP compiler_v0.2 实现**（`kqp_compiler/plan_reader.py` + `query_builder.py`），将 design_plan_v0.6 → KQP_instance_v0.2，对照 50 个手写 instance 验证 semantic match。
2. **KQP runner 实现**（`kqp_compiler/executable_generator.py` + 主 runner），将 KQP_instance 解释执行。
3. **GT 验证**：50 个 GT STEP 全通过；100 个 perturbation CAD 检测率 ≥ 80%。
