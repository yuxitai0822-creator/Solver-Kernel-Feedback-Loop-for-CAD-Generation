# Sanity Set（50 样本）建模序列结构分析报告

> **目的**：为实现"确定性 KQP Compiler（建模序列 → Kernel Query Program，前后语义完全等价）"提供数据结构基础。本文档逐一拆解 50 个 sanity 样本的 JSON 建模序列：有哪些操作类型、各类型的字段结构、操作间的依赖关系。
> **配套数据**：`data/sanity_set_50/`（450 个文件）、`data/sanity50_structure_dump.txt`、`data/sanity50_structure.json`、`data/show_concrete_examples.py` 输出的真实字段实例。
> **适用范围**：Phase0 sanity set（仅 sketch + extrude，无 spline/loft/fillet）。Phase1/Phase2 扩展时本文的结论可直接继承，仅需补充新出现的特征类型。

---

## 1. 建模序列的整体形态（One-Shot Summary）

每个样本的 JSON 是一个 **feature-history 重建序列**，顶层固定 5 键：

| 顶层键 | 作用 | 是否参与 KQP |
|---|---|---|
| `metadata` | `parent_project`(design id) / `component_name` / `component_index` —— 零件归属 | 间接（命名/单零件判定） |
| `timeline` | 操作时间顺序：`[{index, entity}, ...]`，entity 指向 entities 的 UUID | ✅ 决定操作执行顺序 |
| `entities` | **核心**：`{UUID: feature}`，只有 `Sketch` 和 `ExtrudeFeature` 两类 | ✅ KQP 的主输入 |
| `properties` | 最终几何体的拓扑/尺寸/物理属性（17 项 GT 答案） | ✅ KQP 期望值来源（见拓扑/尺寸报告） |
| `sequence` | 曲线→时间线的构建细节 | 一般不直接用于 KQP |

**关键事实（50 样本统计）**：

- **操作类型只有 2 种**：`Sketch`（52 次）+ `ExtrudeFeature`（50 次）。全部 50 样本 `operation = NewBodyFeatureOperation`（即每次 extrude 都新建实体，无 Cut/Join/Intersect）。
- **时间线极简**：50 个样本 `timeline_len` 全为 2（1 个 sketch + 1 个 extrude，按序执行）。另有 2 个样本含 2 个 sketch（但仍是 ≤2 sketch）。
- **extent_type**：48 个 `OneSideFeatureExtentType`（单向拉伸）、1 个 `Symmetric`、1 个 `TwoSides`。
- **草图曲线类型**：仅 3 种 —— `SketchLine`(155) / `SketchCircle`(35) / `SketchArc`(12)。无 spline/ellipse（Phase0 过滤保证）。

> **结论**：sanity set 的建模序列可统一抽象为 **"1–2 个 Sketch → 1 个 Extrude"** 的线性流程。这使 KQP Compiler 的第一阶段只需覆盖这一种拓扑流程，复杂度可控。

---

## 2. 操作类型一：Sketch（草图）的完整结构

`entities[uuid]` 当 `type == "Sketch"` 时，**100% 样本**含以下键：

```
Sketch = {
  name, type,
  reference_plane: {  // 草图所在平面（决定拉伸方向轴）
     name, type,
     plane: { origin:{x,y,z}, normal:{x,y,z,length}, u_direction, v_direction },
     corrective_transform: { origin, x_axis, y_axis, z_axis }  // 平面→世界坐标变换
  },
  transform: {...},            // 草图自身变换
  points:   { <uuid>: {type, x, y, z}, ... },   // 草图点（2D 坐标实际存为3D）
  curves:   { <uuid>: {type, ...}, ... },        // 见 §2.1
  constraints: { <uuid>: {type, ...}, ... },     // 见 §2.2（Solver 反馈输入）
  dimensions:  { <uuid>: {type, parameter, ...}, ... },  // 见 §2.3
  profiles: { <uuid>: {loops, properties}, ... } // 见 §2.4（extrude 输入）
}
```

**注意**：`constraints` 在 47/50 样本出现，`dimensions` 在 48/50 出现 —— 少数草图几乎无约束（欠约束样本），这恰好为 Solver 反馈提供"UC 欠约束"案例。

### 2.1 曲线子结构（curves）—— 几何尺寸的直接来源

三种曲线的真实字段（取自 `show_concrete_examples.py`）：

```jsonc
// SketchLine：仅端点引用，长度由两点距离决定
{ "type":"SketchLine", "start_point":"<pt-uuid>", "end_point":"<pt-uuid>",
  "fully_constrained": false, "fixed": false, "visible": true,
  "construction_geom": false, "reference": false }

// SketchCircle：直接含 radius + center_point  ← 圆柱/孔半径来源
{ "type":"SketchCircle", "center_point":"<pt-uuid>", "radius": 0.7966,
  "fully_constrained": true, ... }

// SketchArc：含 radius + center + 起止角  ← 圆弧半径来源
{ "type":"SketchArc", "start_point":"...", "end_point":"...", "center_point":"...",
  "radius": 1.0, "start_angle":0.0, "end_angle":3.1416, "reference_vector":{...}, ... }
```

> **对 KQP 的意义**：圆/弧半径可直接从 `curves[*].radius` 读取，而直线的长度需用 `points[start_point]`/`points[end_point]` 计算欧氏距离。这是尺寸查询"厚度/孔径/距离"在 GT 序列侧的取值点。

### 2.2 约束子结构（constraints）—— Solver 反馈输入

50 样本共出现 **10 类约束**（全数据集是 16 类）：

| 约束类型 | 计数 | 关键字段 | 几何语义 |
|---|---|---|---|
| CoincidentConstraint | 60 | `entity`, `point` | 点落在曲线上（共点） |
| HorizontalConstraint | 43 | `line` | 直线水平 |
| VerticalConstraint | 33 | `line` | 直线竖直 |
| TangentConstraint | 22 | `curve_one`, `curve_two` | 两曲线相切 |
| PerpendicularConstraint | 19 | `line_one`, `line_two` | 两直线垂直 |
| ParallelConstraint | 16 | `line_one`, `line_two` | 两直线平行 |
| ConcentricConstraint | 11 | `curve_one`, `curve_two` | 两圆/弧同心 |
| OffsetConstraint | 4 | `distance`, `parent_curves[]`, `child_curves[]` | 等距偏移 |
| MidPointConstraint | 3 | `point`, `mid_point_curve` | 点在曲线中点 |
| EqualConstraint | 1 | （曲线等长） | 两曲线等长 |

约束通过 UUID 引用 `curves` / `points`，构成一个 **2D 草图约束图**。Solver 反馈臂正是把 `constraints + dimensions` 喂给约束求解器，求 FC/OC/UC/Unsolvable 状态。

### 2.3 尺寸子结构（dimensions）—— driving dimension

每条尺寸含 `parameter: {type:"ModelParameter", value, name, role}` 与 `is_driving: bool`。5 类尺寸：

| 尺寸类型 | 计数 | 字段 | 几何语义 |
|---|---|---|---|
| SketchLinearDimension | 50 | `entity_one`, `entity_two`, `orientation`, `parameter.value` | 两实体距离（含 H/V 方向） |
| SketchDiameterDimension | 33 | `curve`, `parameter.value` | 圆直径 ← 圆柱/孔直径来源 |
| SketchOffsetDimension | 10 | `line`, `entity_two`, `parameter.value` | 偏移距离 |
| SketchOffsetCurvesDimension | 4 | `offset_constraint`, `parameter.value` | 等距曲线间距 |
| SketchRadialDimension | 3 | `curve`, `parameter.value` | 圆弧半径 |

> **对 KQP 的意义**：`is_driving==true` 的尺寸是"设计意图中的关键尺寸"，KQP 的尺寸查询期望值应优先从 driving dimension 提取，保证语义与设计一致。

### 2.4 轮廓子结构（profiles）—— extrude 的输入，决定拓扑

每个 sketch 含 1–5 个 profile。`profile = {loops:[...], properties:{area,centroid,perimeter}}`，其中 **loop** 是闭合环：

```jsonc
loop = { "is_outer": true/false,
          "profile_curves": [ {type:"Line3D", start_point:{x,y,z}, end_point:{x,y,z}, curve:"<uuid>"}, ... ] }
```

50 样本分布：

| profile 数/草图 | 样本数 | loop 数/profile | 样本数 |
|---|---|---|---|
| 1 | 35 | 1（单闭合轮廓） | 58 |
| 2 | 13 | 2（外环+内环=带孔） | 14 |
| 3 | 3 | 3（外环+2内环=带多孔） | 3 |
| 5 | 1 | | |

> **对 KQP 的意义**：`is_outer` 标志 + loop 数量 = **孔/凹槽的拓扑来源**。一个 profile 若含 1 外环 + N 内环，extrude 后即为"带 N 个孔的板"。这是拓扑查询 face_count、特征查询"孔数量"在 GT 侧的依据。`profile.properties.area` 也可作为草图面积查询的期望值。

---

## 3. 操作类型二：ExtrudeFeature（拉伸）的完整结构

50 样本 100% 含以下键：

```jsonc
ExtrudeFeature = {
  name, type,
  profiles: [ {profile:"<profile-uuid>", sketch:"<sketch-uuid>"}, ... ],  // 消耗哪个草图的哪个轮廓
  operation: "NewBodyFeatureOperation",      // 本集合全是新建实体
  start_extent: {type},                       // 起始条件
  extent_type: "OneSideFeatureExtentType",    // 48 单向 / 1 对称 / 1 双向
  extent_one: {
     distance:  {type:"ModelParameter", value:20.0, name:"d462_1", role:"AlongDistance"},  // ← 拉伸高度
     taper_angle:{type:"ModelParameter", value:0.0,  name:"d463_1", role:"TaperAngle"},      // ← 拔模角
     type, is_full_length?
  },
  extent_two: {...},        // 仅 TwoSides 样本
  faces, bodies,            // 结果面/体引用
  extrude_bodies, extrude_faces, extrude_side_faces, extrude_end_faces, extrude_start_faces  // 各类结果面
}
```

**关键字段**：
- **`profiles`**：建立 extrude → sketch → profile 的依赖链（KQP 必须沿着这条链回溯到草图几何）。
- **`extent_one.distance.value`**：**拉伸高度** —— 尺寸查询"高度/厚度（沿拉伸方向）"的 GT 来源。例如样例 `100243_9fb796fe_0005` 的 `distance.value = 20.0`，对应 `properties.bounding_box` 沿拉伸轴的尺寸 20.0。
- **`extent_one.taper_angle.value`**：拔模角（本集合多为 0）。
- **`reference_plane.plane.normal`**（来自关联 sketch）：**拉伸方向轴** —— 决定 bounding_box 的"哪一维是高度"。

---

## 4. 操作依赖图（Data Flow）

50 样本的依赖图高度规整，统一形态为：

```
reference_plane (plane: origin/normal/u_dir/v_dir)
        │
        ▼
   Sketch ── points ──┐
      │   ── curves ──┤  (约束/尺寸引用这些)
      │   ── constraints / dimensions (Solver 输入)
      │   ── profiles ─┐
      ▼               │
   profile(外环+内环) ─┤
                      ▼
              ExtrudeFeature.profiles[{profile, sketch}]
                      │
                      ▼
            extent_one.distance (高度) → 沿 plane.normal 拉伸
                      │
                      ▼
                 最终 Solid  →  properties (GT 答案)
```

**三点对 KQP 设计的直接约束**：
1. KQP 必须能从 `extrude.profiles` **回溯到 sketch**（不能只看 extrude），因为孔/尺寸/拓扑全部编码在 sketch 与 reference_plane 中。
2. 拉伸高度取 `extent_one.distance.value`，但"哪个轴是高度"必须结合 `reference_plane.plane.normal` 与 `extent_type` 判断（OneSide 沿 normal 单向；Symmetric 沿 ±normal 对称各半）。
3. 所有结果（body/face/edge/vertex 数）在 `properties` 中给出 GT，KQP 只需对 LLM 生成的 CAD 脚本执行结果做同样查询并比对。

---

## 5. 不能遗漏的语义要素清单（KQP Compiler 必读字段）

按"遗漏即导致语义不一致"的风险排序：

| # | 语义要素 | JSON 路径 | 为何不能漏 |
|---|---|---|---|
| 1 | 拉伸高度 | `extrude.extent_one.distance.value` | 直接决定 bounding_box 高度与体积，遗漏则高度查询无意义 |
| 2 | 拉伸方向轴 | `sketch.reference_plane.plane.normal` | 决定 bbox 哪一维=高度；错误轴→高度查询维度错位 |
| 3 | extent_type | `extrude.extent_type` | Symmetric/TwoSides 下高度计算方式不同（单向 vs 对称） |
| 4 | profile 的 loop 结构 | `sketch.profiles[*].loops[*].is_outer` | 内环=孔；遗漏 loop → 孔数量/face_count 全错 |
| 5 | 圆/弧半径 | `curves[*].radius` (Circle/Arc) | 圆柱面/孔径查询的依据 |
| 6 | 直线长度 | `points[start]/points[end]` 计算距离 | 矩形长宽、厚度查询依据（直线无显式 length） |
| 7 | driving dimensions | `dimensions[*]` where `is_driving==true` | 设计意图关键尺寸，KQP 期望值应与之一致 |
| 8 | operation | `extrude.operation` | 本集合全 NewBody；但若扩展 Phase1，Cut/Join 会改变 body_count 语义 |
| 9 | 草图平面变换 | `reference_plane.corrective_transform` | 草图局部坐标↔世界坐标；bbox/位置查询依赖 |
| 10 | points 绝对坐标 | `sketch.points[*].{x,y,z}` | profile_curves 的坐标、距离计算的基础 |
| 11 | 约束图 | `constraints[*]` | 决定草图几何可解性（Solver 侧），间接决定能否稳定重建 |

---

## 6. 对 KQP Compiler 的结构启示

基于上述分析，确定性 KQP Compiler 处理 sanity 序列时需要 **3 个遍历阶段**：

1. **实体分类阶段**：扫描 `entities`，分为 sketches[] 与 extrudes[]，并记录 `extrude.profiles → sketch.uuid` 的映射。
2. **几何提取阶段**：对每个被 extrude 引用的 sketch，提取 `reference_plane.normal`、`curves`(半径/端点)、`profiles.loops`(内外环)、`points`(坐标)；对每个 extrude 提取 `distance.value` + `extent_type`。
3. **KQP 生成阶段**：据 §5 清单生成四类查询（拓扑/尺寸/特征/健康）的期望值，期望值同时与 `properties` 交叉验证（compiler 内部 sanity check：若从草图算出的预期 face_count 与 properties.face_count 不符，应报警而非静默）。

> 详细的"拓扑查询对象从哪来 / 尺寸查询对象从哪来 / 各类查询的 JSON→KQP 映射表"见同目录 **`02_KQP_对象来源与查询映射.md`**。
