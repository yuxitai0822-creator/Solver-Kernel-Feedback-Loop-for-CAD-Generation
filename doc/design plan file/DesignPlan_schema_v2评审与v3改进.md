# Design Plan Schema v0.2 评审与 v0.3 改进

> **评审对象**：`DesignPlan/DesignPlan_schema02.txt`（v0.2 schema）及 `DesignPlan/samples/v2/` 下的 5 个手写样本。
> **评审依据**：基于样本 1–5（v2 样本，纯矩形棱柱）已知问题 + 新增样本 6–20 的源数据预分析（含曲面、圆环、多 sketch、旋转 frame 等 v2 完全未覆盖的形态）。
> **评审目的**：在投入 v0.3 大规模手写（10 个新样本）之前，先把 schema 缺陷修干净，避免 v0.3 样本带着 v2 的旧病硬写。

---

## 0. 评审结论速览

| 维度 | v0.2 评分 | 致命缺陷 |
|---|---|---|
| Sufficiency | ❌ 不及格 | 无法表达曲面（圆柱/圆环）、无法表达环形/带孔 profile、无法表达旋转 frame |
| Non-Procedurality | ⚠️ 中等 | `solid_bodies` 单层结构无法表达"主特征+辅助特征"的非过程性组合 |
| Verifiability | ⚠️ 中等 | `bbox_size axis:x` 在旋转 frame 下语义模糊；无针对圆柱/圆环面的验证 intent |
| Non-Leakage | ✅ 较好 | `non_verifiable` + `forbidden_fields` 设计正确 |

**核心结论**：v0.2 是"纯棱柱专用 schema"，对样本 1–5 工作良好，但一旦遇到样本 13（圆柱面）、14（圆环带孔）、20（旋转 frame）就**结构性失效**，不是补字段能解决的，必须 v0.3 重构 profile 与 dimensions 的表达。

---

## 1. v0.2 已知问题回顾（来自样本 1–5，doc/03 §7）

为保持本文档自包含，先回顾 doc/03 §7 已发现的 6 个 v0.2 缺陷（手写样本 1–5 时暴露）：

| # | 缺陷 | 严重度 |
|---|---|---|
| 7.1 | 数据冗余：尺寸同时出现在 `profile.parameters`/`dimensions`/`derived.design_envelope` 三处 | ⚠️ |
| 7.2 | bbox 验证用世界轴 `axis:x`，与 frame-based `along_u` 映射缺失 | ⚠️ |
| 7.3 | `extrude.distance` 与 `dimensions.along_w` 完全重复 | ⚠️ |
| 7.4 | `part_category` 缺量化分类规则 | ⚠️ |
| 7.5 | `source_constraints` 是字符串列表，不可机器消费 | ⚠️ |
| 7.6 | `tolerance` 单位歧义（绝对 vs 相对） | ⚠️ |

这 6 个问题 v0.3 都要修，但**不是本文档的重点**——本文档重点是样本 6–20 暴露的**新结构性缺陷**。

---

## 2. 样本 6–20 暴露的新结构性缺陷

### 2.1 ❌ 致命：`profile.type` 枚举无法表达"带孔轮廓"

**证据**：样本 14（`102314_91648bfc_0000`）和样本 16/17（`102410_f9877a7b_*`）的 profile 是**同心圆环**——外圆减内圆，形成管状拉伸体。

样本 16 的 profile `cb180b2c`：`loops=2, total_curves=2, outer_loops=1`——即 1 个外环（外圆）+ 1 个内环（内圆），内环作为"减"区域。

v0.2 的 `profile.type` 枚举是 `rectangle | circle | polygon | arbitrary_closed`，**全部假设单环闭合**，没有"环 + 环"的多环表达。`profile.parameters` 也只有单环的 side_u/side_v 或 radius。

**影响**：圆环、带孔板、键槽等所有"主轮廓-减轮廓"形态**无法用 v0.2 表达**。这是 v0.3 必须解决的头号问题。

### 2.2 ❌ 致命：`primitive_type` 枚举无法表达"圆环/管状拉伸体"

**证据**：同上样本。v0.2 的 `primitive_type` 是 `rectangular_prism | cylinder | extruded_profile | unsupported`。

- `cylinder` 只能表达实心圆柱（单圆拉伸）
- 圆环（外圆-内圆拉伸）既不是 `cylinder` 也不是 `rectangular_prism`，只能塞进 `unsupported`

**影响**：v0.2 把大量合法工程形态（管、套筒、垫圈）降级为 `unsupported`，丧失设计意图。

### 2.3 ❌ 致命：`dimensions.along_u/v/w` 三轴模型无法表达曲面参数

**证据**：样本 13（`102295_86f842dd_0000`）是**跑道形截面**（2 直线 + 2 半圆弧）拉伸体。它的关键设计参数是：
- 直线段长度 2.8（两圆心距）
- 圆弧半径 1.0
- 拉伸距离 0.4

但 v0.2 的 `dimensions` 只有 `along_u/along_v/along_w` 三个标量，**无法表达"半径"这种曲面特有参数**。半径不是沿某轴的 span，而是圆弧的固有属性。

样本 15（三角形带圆角）更复杂：有 2 个圆角半径（0.5）+ 2 个圆孔半径（0.25）+ 3 个直线段长度。v0.2 的三轴 dimensions **完全无法承载**。

**影响**：所有含圆弧/圆角的轮廓，v0.2 丢失关键设计尺寸。

### 2.4 ❌ 致命：`solid_bodies` 单层结构无法表达"主特征+辅助特征"

**证据**：样本 14 的 timeline 有 **3 个 entity**：Sketch1（XY 平面，2 同心圆）+ Extrude1（拉伸成圆环体）+ **Sketch2（XZ 平面，孤立圆，未被任何 extrude 引用）**。

Sketch2 是一个**辅助草图**——它在 timeline 里但没被 extrude 消费，可能是后续操作的定位参考。v0.2 的 `solid_bodies[]` 只描述被 extrude 产出的 body，**没有地方放这种辅助几何**。

但更关键的是：样本 15 的 profile `c0ac867f` 有 `loops=3`——1 个外环（三角形）+ 2 个内环（2 个圆孔）。这 2 个孔是**和外轮廓同一次拉伸**成型的（不是后续 boolean cut）。v0.2 的 `modifications`（设计为"body 上的局部修改"）语义不对——这些孔不是 modification，是 profile 本身的多环结构。

**影响**：v0.2 混淆了"profile 内多环"和"body 上 modification"两种不同的"减"语义。

### 2.5 ⚠️ 严重：`frame` 的 u/v 方向符号歧义

**证据**：样本 18/19（`102525_06a3094b_0000/0004`）的 sketch plane：
- normal ≈ (0, 1, 0)
- **u_dir ≈ (0, 0, -1)**（注意是负 Z！）
- v_dir ≈ (-1, 0, 0)

样本 20（`102525_06a3094b_0006`）更极端：u_dir ≈ (-0.0049, 0, -0.9999)，v_dir ≈ (-0.9999, 0, 0.0049)——frame **轻微旋转**，既不严格对齐任何坐标轴，也不是干净的 90° 倍数。

v0.2 的 `dimensions.along_u` 在 u_dir=(0,0,-1) 时，"沿 u 的 span" 和 u_dir=(0,0,1) 时**数值相同**（span 是 max-min，与方向符号无关）。但 KQP 验证时，如果用顶点投影到 u_dir 算 span，正负方向结果一样；如果用 bbox 算，就要先把 frame 投影到世界轴——**v0.2 没规定用哪种**。

**影响**：旋转 frame 下，dimensions 的数值与 KQP 验证方法耦合不清。

### 2.6 ⚠️ 中等：`validation_intents` 缺曲面验证类型

**证据**：样本 13/14/15/16/17 都含 `CylinderSurfaceType`。v0.2 的 intent 枚举是 `body_count | bbox_size | all_faces_planar | is_solid | occt_is_valid | euler_characteristic | edge_orthogonality`。

- `all_faces_planar` 对这些样本 expected=false，但**无法验证"应该有几个圆柱面"**
- 没有 `cylinder_face_count` 或 `surface_type_distribution` intent

**影响**：含曲面的样本，v0.2 只能验证"非全平面"，无法验证"正确的曲面类型分布"。

### 2.7 ⚠️ 中等：`constraints` 无法表达 Tangent/Concentric/Parallel/Perpendicular

**证据**：
- 样本 13 有 4 个 TangentConstraint（直线与圆弧相切）+ 1 个 ParallelConstraint
- 样本 14 有 ConcentricConstraint（两圆同心）
- 样本 15 有 4 个 TangentConstraint（圆角与直线相切）
- 样本 18/19 有 PerpendicularConstraint + ParallelConstraint

v0.2 的 constraints 类型枚举是 `orthogonal_adjacent_edges | symmetry | tangent | concentric | parallel_edges`——枚举名有了，但**没有结构化字段**表达"哪两条曲线相切""哪两个圆同心"。我在 v2 样本里只写了 `orthogonal_adjacent_edges` 一种，其余类型从未实例化。

**影响**：含相切/同心的轮廓，v0.2 的 constraints 是空壳。

### 2.8 ⚠️ 轻微：`extrude.extent_type` 缺 `symmetric` 与样本 14 的孤立 sketch

样本 14 的 Sketch2 完全未被 extrude 引用。v0.2 的 `solid_bodies` 只描述被 extrude 产出的 body，**孤立 sketch 无处安放**。这本身可能是 Non-Leakage（辅助几何不入 Design Plan），但 compiler 需要明确规则"丢弃未消费的 sketch"。

---

## 3. v0.3 改进方案

### 3.1 核心重构：`profile` 改为多环结构

```
"profile": {
  "type": "<rectangle | circle | annulus | stadium | polygon_with_fillets | arbitrary_closed>",
  "rings": [
    {
      "role": "outer",                    // outer = 实体边界; inner = 减区域（孔）
      "loop_type": "<polyline | circle | composite_line_arc>",
      "curves": [ ... ]                   // 该环的曲线序列
    },
    {
      "role": "inner",
      "loop_type": "circle",
      "curves": [ ... ]
    }
  ],
  "closed": true
}
```

**关键**：`rings[]` 显式区分 outer/inner，解决 2.1（带孔轮廓）。每个 ring 的 `loop_type` 区分纯直线、纯圆、混合，解决 2.3（曲面参数）。

### 3.2 核心重构：`dimensions` 改为"参数化尺寸集"而非三轴标量

放弃 `along_u/along_v/along_w` 三标量模型，改为**按 profile 类型分发的参数化尺寸**：

```
"dimensions": {
  "extrude_distance": {"value": 0.4, "tol": 0.01, "source": "explicit"},
  // 类型特定参数（由 profile.type 决定存在哪些）：
  "rectangle": {"length_u": {...}, "width_v": {...}},
  "circle":    {"radius": {...}},
  "annulus":   {"outer_radius": {...}, "inner_radius": {...}},
  "stadium":   {"straight_length": {...}, "radius": {...}},
  "polygon_with_fillets": {"side_lengths": [...], "fillet_radii": [...], "hole_radii": [...]}
}
```

**关键**：每个 profile.type 有自己的尺寸模式，radius 不再硬塞进三轴模型，解决 2.3。`extrude_distance` 成为唯一必填项（所有拉伸体都有），其余按类型分发。

### 3.3 核心重构：`primitive_type` 改为 `extruded_{profile_type}` 派生

不再维护 `primitive_type` 枚举，改为**从 profile.type 派生**：
- rectangle → `extruded_rectangle`
- circle → `extruded_circle`（实心圆柱）
- annulus → `extruded_annulus`（管/套筒）
- stadium → `extruded_stadium`
- polygon_with_fillets → `extruded_polygon_with_fillets`

**关键**：消除 primitive_type 与 profile.type 的冗余，解决 2.2。

### 3.4 `solid_bodies` 引入 `auxiliary_geometry` 兄弟字段

```
"solid_bodies": [ ... ],
"auxiliary_geometry": {
  "unused_sketches": "<count or list of sketch purposes>",
  "_doc": "Sketches present in source timeline but not consumed by any extrude. Recorded for traceability; NOT verifiable."
}
```

解决 2.8（孤立 sketch），并明确标注不可验证。

### 3.5 `constraints` 结构化

```
"constraints": [
  {"type": "tangent", "curve_a": "<ring/curve ref>", "curve_b": "<ref>", "tol": 1e-6},
  {"type": "concentric", "circle_a": "<ref>", "circle_b": "<ref>", "tol": 1e-6},
  {"type": "parallel", "line_a": "<ref>", "line_b": "<ref>", "tol": 1e-6},
  {"type": "perpendicular", "line_a": "<ref>", "line_b": "<ref>", "tol": 1e-6},
  {"type": "orthogonal_adjacent_edges", "subject": "body_0", "expected": "..."}
]
```

解决 2.7。curve/line 引用用 `ring_index:curve_index` 形式（如 `"0:2"` = 第 0 个 ring 的第 2 条曲线），避免泄漏 Fusion UUID。

### 3.6 `validation_intents` 增曲面验证

新增 intent 类型：
- `surface_type_distribution`：`expected: {"PlaneSurfaceType": 4, "CylinderSurfaceType": 2}`，验证曲面类型与计数
- `cylinder_face_count`：`expected: 2`（简化版，当只有圆柱面时）
- `profile_closed`：验证拉伸前的 profile 闭合（通过 euler/拓扑间接）

解决 2.6。

### 3.7 `frame` 增 `span_computation_method` 字段

```
"frame": {
  "u_dir": [...], "v_dir": [...], "w_dir": [...],
  "span_computation": "vertex_projection"   // 唯一合法值，消除 2.5 歧义
}
```

强制规定：dimensions 的 span 一律用**顶点投影法**（exp01 KQP 已实现），不用 axis-aligned bbox。解决 2.5。

### 3.8 修复 doc/03 §7 的 6 个旧问题

| 旧问题 | v0.3 修复 |
|---|---|
| 7.1 三处冗余 | dimensions 为唯一真值源；删 `profile.parameters` 尺寸；删 `derived.design_envelope` |
| 7.2 bbox 世界轴 | bbox_size intent 改用 `frame_axis`，或直接删（用 span_u/v/w 替代） |
| 7.3 extrude.distance 冗余 | 并入 `dimensions.extrude_distance`，extrude 块只留 extent_type/operation/taper |
| 7.4 part_category 量化 | 归入 `derived`，给量化阈值规则 |
| 7.5 source_constraints 结构化 | 改为 `[{type, count, note}]` |
| 7.6 tolerance 单位 | 增 `tol_kind: absolute\|relative`，默认 absolute |

---

## 4. 四项标准复核（v0.2 vs v0.3）

| 标准 | v0.2 | v0.3 | 关键改进 |
|---|---|---|---|
| **Sufficiency** | ❌ | ✅ | 多环 profile + 参数化 dimensions 覆盖圆环/跑道/带孔/圆角 |
| **Non-Procedurality** | ⚠️ | ✅ | auxiliary_geometry 隔离辅助 sketch；rings 不规定建模顺序 |
| **Verifiability** | ⚠️ | ✅ | surface_type_distribution + frame_axis span + 结构化 constraints |
| **Non-Leakage** | ✅ | ✅ | 保持；auxiliary_geometry 标注不可验证 |

---

## 5. v0.3 未解决问题（留给 v0.4）

1. **多 body 装配关系**：v0.3 仍是单 body 为主，多 body 间的相对位置（如"孔阵列传回 body_0"）未设计关系谓词。
2. **RevolveFeature**：v0.3 只覆盖 ExtrudeFeature；旋转体（轴+角度）需新 profile 子类型。
3. **FilletFeature/ChamferFeature 作为独立特征**：v0.3 把圆角归入 profile（polygon_with_fillets），但 Fusion360 的 FilletFeature 是 post-extrude 的边圆角，两者语义不同，v0.3 暂不区分。
4. **复杂 profile 的自动识别**：v0.3 schema 能表达，但 compiler 能否从 sketch curves 自动识别 stadium/annulus 等类型，是 compiler 报告（doc/04）的问题。

---

## 6. 实施计划

1. 写 `DesignPlan/DesignPlan_schema03.txt`（v0.3 模板，落实 §3 全部改进）
2. 用 v0.3 手写 10 个样本（样本 11–20），归档 `DesignPlan/samples/v3/`
3. 基于这 10 个样本验证 compiler 设计，写 `doc/complier可行性验证-样本10-20.md`
