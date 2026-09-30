# KQP Schema v0.1 初始化报告

> **目的**：从 50 个 Design Plan v6 实例中枚举所有可验证字段，据此设计 KQP Instance schema v0.1。
> **后续**：v0.1 之外的新需求延后到 v0.2（不在本轮扩张）。
> **来源**：`compiler/kqp_field_inventory.py` 对 50 个 v6 instances 自动枚举，输出在 `compiler/kqp_field_inventory/` 下。

---

## 0. 结论速览

| 维度 | v0.1 覆盖 |
|---|---|
| 50 个 v6 instances 的可验证字段枚举 | ✅ 已完成 |
| A 拓扑查询 | `body_count`（100% 覆盖），其他（face/edge/vertex/shell/wire）schema 已留 slot 但 compiler 不主动 emit（Non-Leakage） |
| B 几何尺寸查询 | `bbox_size`（3 轴，100% 覆盖），`cylinder_radius`（24 样本），`center_distance`（schema 留 slot 暂无 source），`plane_area`/`volume` 标记为 open-extension（design_plan v0.6 无 source） |
| C 特征查询 | `through_void_count`（15 样本有 inner ring） |
| D 健康查询 | `is_solid`、`occt_valid`、`all_faces_planar`、`euler_characteristic`（皆 implicit emit） |
| **sample 1 KQP 示例** | ✅ schema 末尾 built-in 示例 |

**核心决策**：schema v0.1 严格区分"现在能 emit"（design_plan 字段已有）与"schema 留 slot 但不 emit"（待 future 字段添加）。这避免 v0.1 compiler 凭空发明 queries 违反 Non-Leakage。

---

## 1. 字段枚举结果（50 samples, compiler_v6 instances）

`compiler/kqp_field_inventory/per_sample_facts.json` 包含每个样本的可验证事实。聚合统计：

```
Per-field coverage (out of 50 instances):
  target.body_count       :  50/50 (100%)
  extrude_distance        :  50/50 (100%)
  length_u                :  21/50 (42%)
  width_v                 :  21/50 (42%)
  inner_rings_count       :  15/50 (30%)
  circle_radius           :  10/50 (20%)
  outer_radius            :   7/50 (14%)
  inner_radius            :   7/50 (14%)
  outer_length_u / outer_width_v / inner_length_u / inner_width_v :   5/50 (10% each) [rectangular_frame samples]
  line_lengths            :   5/50 (10%)
  straight_length         :   4/50 (8%) [stadium]
  stadium_radius          :   4/50 (8%)
  arc_radii               :   2/50 (4%)  [arbitrary_closed]
```

**KQP query intents triggered**:
- `body_count`: 50 次（每个样本 1 个 implicit is_health + 1 个目标 field）
- `bbox_size`: 118 次（extrude + 2 个 in-plane spans per sample）
- `cylinder_radius`: 17 次（10 圆形 + 7 环面）
- `through_void_count`: 15 次（有 inner ring 的样本）
- `is_solid`、`occt_valid`: 各 50 次

---

## 2. KQP schema v0.1 字段 → Design Plan 字段映射

| KQP intent | Design Plan source field | 可用性 |
|---|---|---|
| `body_count` | `$.target.body_count` | 50/50 |
| `bbox_size (u axis)` | `$.solid_bodies[0].dimensions.profiles[0].length_u.value` (rectangle/stadium+hollow cases); otherwise compiler emits nothing for u axis | 21/50 (rect+frame cases); 通过 vertex_projection 泛化 |
| `bbox_size (v axis)` | `$.solid_bodies[0].dimensions.profiles[0].width_v.value` | 21/50 |
| `bbox_size (w axis)` | `$.solid_bodies[0].dimensions.extrude_distance.value` | 50/50 |
| `cylinder_radius` | `$.solid_bodies[0].dimensions.profiles[0].(radius|outer_radius|inner_radius).value` | 17/50 |
| `through_void_count` | `count(profiles[*].rings[*].role=='inner')` | 15/50 |
| `is_solid` | (implicit; valid extrude) | 50/50 |
| `occt_valid` | (implicit) | 50/50 |

**不可用字段**（Non-Leakage 阻止 emit）：
- `face_count` / `edge_count` / `vertex_count` / `shell_count` / `wire_count`：design_plan v0.6 没有这些字段。它们属于 GT-derived，B-rep topology 信息在 Non-Leakage 下严禁进入 feedback query。schema 保留 `intent` 名称供未来扩展（KQP runner 可以支持，但 compiler 永不 emit）。
- `plane_area`、`volume`、`center_distance`：design_plan v0.6 不含 area/volume/center-distance 字段。schema 留 slot，但 compiler 不 emit。

---

## 3. KQP instance JSON 顶层结构

```jsonc
{
  "instance_id": "kqp_100243_9fb796fe_0005",  // 唯一
  "design_plan_id": "100243_9fb796fe_0005",  // 指向 design_plan_v0.6 instance
  "step_file": "data/sanity_set_50/100243_9fb796fe_0005.step",  // 验证目标
  "queries": [
    {
      "id": "q_body_count",
      "category": "A_topology",
      "intent": "body_count",
      "expected": 1,
      "source_field": "$.target.body_count",
      "feedback_enabled": true,
      "feedback_template": "Expected body_count={expected}, got {actual}."
    },
    // ... 每个 query 必须含：id, category, intent, expected, source_field, feedback_enabled
}
```

关键约束（写入 schema 顶部）：
1. **Traceability**：source_field 必须非空（feedback_enabled=true 时）。
2. **Verifiability**：intent 必须在 ALLOWED_INTENTS 中。
3. **Non-Leakage**：expected 不来自 GT-only 字段（如 face_count）。
4. **Feedback Usefulness**：feedback_template 字符串有具体建议。

---

## 4. 实施后的下一步：compiler → runner → perturbation

本轮只完成 schema v0.1。下一步按用户路线图：

1. **手写 50 个 KQP instance JSON**（`KQP/samples/v0.1/`），使用 v0.1 的 query 模板。这将成为 compiler_v0.1 的 ground truth。
2. **实现 KQP compiler_v0.1**（`kqp_compiler/plan_reader.py` + `query_builder.py`），将 design_plan_v6 → KQP_instance。
3. **对比** compiler 输出 vs 手写 KQP instance：验收 semantic match（query_type/target/expected/tolerance/source_path/feedback_enabled 一致）。
4. **实现 KQP runner**（`kqp_compiler/executable_generator.py` + runner），把 KQP instance 解释执行，返回 pass/fail。
5. **GT 验证**：50 个 GT STEP 全部通过；perturbation 100 negative CAD 检测率 ≥ 80%。

---

## 5. v0.1 决策记录

| 决策 | 原因 |
|---|---|
| 不在 schema v0.1 emit `face_count/edge_count/vertex_count` | 这些字段在 design_plan v0.6 中缺失（Non-Leakage: 不容许从 GT 引入） |
| `is_solid`/`occt_valid` 允许 `source_field="(implicit)"` | 这两个 query 对任何 sane extrusion 都应通过；implicit emit 是合理的"健康基线" |
| `bbox_size` 使用 frame axes 而非 world axes | 与 exp01 KQP/compiler 中的 `oriented_dimensions` 设计一致；避免旋转 frame 下 world-axis bbox 不可靠 |
| `through_void_count` 仅数 inner rings，不依赖 genus | 直接 traceable；genus 推导要 OCCT topology，对扁圆环 annulus 不可靠 |
| `feedback_template` 用 `{expected}`/`{actual}` 占位符 | runner 在执行后替换；模板字符串 LLM-可读 |
| `plane_area`/`volume`/`center_distance`/`hole_radius` 仅留 schema slot、不 emit | 设计未来扩展，避免 v0.1 编译器硬发明 |
