# Design Plan Schema v0.3 评审与 v0.4 改进

> **评审对象**：`DesignPlan/DesignPlan_schema03.txt`（v0.3 schema）及 `DesignPlan/samples/v3/` 下的 10 个手写样本（11–20）。
> **评审依据**：v0.3 样本暴露的遗留问题 + 新增样本 21–30 的源数据预分析（含负拉伸、多 profile 单拉伸、矩形框轮廓、无 dimension 圆等 v0.3 完全未覆盖的形态）。
> **评审目的**：在投入 v0.4 手写（10 个新样本）+ compiler 实现之前，把 v0.3 的结构性缺陷修干净。

---

## 0. 评审结论速览

| 维度 | v0.3 评分 | 致命缺陷 |
|---|---|---|
| Sufficiency | ⚠️ 中等 | 无法表达负方向拉伸；无法表达单次拉伸多 profile；矩形框（外矩形+内矩形孔）无对应 profile.type |
| Non-Procedurality | ✅ 良好 | rings 多环结构正确隔离了 outer/inner |
| Verifiability | ⚠️ 中等 | 负拉伸的 span_w 语义不清；多 profile 拉伸的 body_count/body 归属模糊 |
| Non-Leakage | ✅ 良好 | auxiliary_geometry 隔离未消费 sketch |

**核心结论**：v0.3 解决了 v0.2 的曲面/多环问题，但在**拉伸方向语义**（负拉伸）和**多 profile 单拉伸**（一次 extrude 消费多个独立 profile）上仍有结构性盲区。v0.4 需补这两类，并细化 profile.type 枚举以覆盖矩形框。

---

## 1. v0.3 已知问题回顾

来自 `doc/DesignPlan_schema_v2评审与v3改进.md` §5（v0.3 留给 v0.4 的未解决问题）：
1. 多 body 装配关系（关系谓词未设计）
2. RevolveFeature（旋转体未覆盖）
3. FilletFeature/ChamferFeature 作为独立特征（post-extrude 边圆角）
4. 复杂 profile 的自动识别（compiler 问题）

这些 v0.4 仍不全面解决（超出本轮 10 样本范围），但本轮新增样本会触及其中部分。

---

## 2. v0.3 样本（11–20）暴露的遗留问题

### 2.1 ⚠️ `extrude.extent_type` 缺负方向语义

v0.3 的 `extent_type` 枚举为 `one_side | two_side | symmetric`，`extrude_distance` 是正标量。但 v0.3 样本中所有拉伸都是正向（distance>0）。

**新样本 21（`102760_26430589_0037`）**：`extent_one.distance = -0.4`（**负值**）。GT bbox 显示 y 范围 [-0.4, 0]，即拉伸沿 -Y 方向。v0.3 的 `extrude_distance.value` 若填 0.4（取绝对值），会丢失"沿 -w 方向"的语义；若填 -0.4，又与"距离"语义冲突。

### 2.2 ⚠️ `solid_bodies` 单 body 假设，未覆盖"单次拉伸多 profile"

**新样本 27（`104283_e5646f96_0001`）**：`input profiles (2)`——一次 ExtrudeFeature 消费 2 个独立 profile（`469d848f` 和 `d8a82cb5`），产出 1 个 body。v0.3 的 `solid_bodies[].profile` 是单数结构，无法表达"一个 body 由多个 profile 合并而成"。

### 2.3 ⚠️ `profile.type` 缺 `rectangular_frame`（矩形框）

**新样本 29（`104453_aba0f2d1_0006`）**：profile `e9625b6a` 有 `loops=2, total_curves=8`——外环是 50×30 矩形（4 线），内环是 40×20 矩形（4 线），形成矩形框（外矩形减内矩形）。v0.3 的 `profile.type` 有 `annulus`（圆环）但无 `rectangular_frame`（矩形框）。落入 `arbitrary_closed` 会丢失"两个矩形"的工程语义。

### 2.4 ⚠️ 无 dimension 的 circle（半径仅存于 curve）

**新样本 30（`104524_f829aab2_0001`）**：`dimensions (0)`——circle 的半径 0.75cm **没有显式 Dimension**，只存在于 `SketchCircle.radius` 字段。v0.3 的 `dimensions.radius.source` 枚举是 `explicit_dimension | inferred_from_point_span`，未覆盖"从 curve.radius 字段提取"这第三种来源。

---

## 3. v0.4 改进方案

### 3.1 `extrude` 增 `direction` 字段（解决负拉伸）

```
"extrude": {
  "extent_type": "one_side | two_side | symmetric",
  "direction": "+w | -w",           // 新增：拉伸方向相对 w_dir
  "distance_total": {"value": ..., "tol": ..., "source": ...},  // 总是正标量
  "operation": "new_body | join | cut | intersect",
  "taper_angle_deg": {...}
}
```

- `direction` 显式表达拉伸朝 w_dir 正向还是负向（解决样本 21 的 -0.4）
- `distance_total` 永远是正标量（绝对值），方向由 `direction` 单独表达
- 对 `two_side`/`symmetric`：`direction` 可为 `both`，distance_total = 两段之和

**重命名**：`extrude_distance` → `distance_total`（语义更清晰，避免与"沿某轴的距离"混淆）。

### 3.2 `solid_bodies[].profile` 改为 `profiles[]`（解决多 profile 单拉伸）

```
"solid_bodies": [
  {
    "id": "body_0",
    "primitive_type": "...",
    "frame": {...},
    "profiles": [                    // 改为复数：一次拉伸可消费多个 profile
      {"type": "rectangle", "rings": [...]},
      {"type": "circle", "rings": [...]}
    ],
    "extrude": {...},
    "dimensions": {...},             // 多 profile 时，按 profile 分组
    "modifications": []
  }
]
```

- 单 profile 样本：`profiles` 长度为 1（向后兼容）
- 多 profile 样本（如样本 27）：`profiles` 长度为 2+，每个 profile 独立描述
- `dimensions` 按 profile 分组：`dimensions.profiles[0].{...}`, `dimensions.profiles[1].{...}`，外加 `dimensions.extrude_distance`（所有 profile 共享）

### 3.3 `profile.type` 增 `rectangular_frame`

```
"profile": {
  "type": "rectangle | circle | annulus | stadium | polygon_with_fillets | rectangular_frame | arbitrary_closed",
  ...
}
```

`rectangular_frame`：外环矩形 + 内环矩形，两矩形同向（边平行）。参数：`outer_length_u`, `outer_width_v`, `inner_length_u`, `inner_width_v`。

### 3.4 `source` 枚举增 `curve_field`

```
"source": "explicit_dimension | inferred_from_point_span | curve_field"
```

`curve_field`：值直接来自 `SketchCircle.radius` / `SketchArc.radius` 字段，无对应 Dimension。解决样本 30。

### 3.5 `part_category` 增 `frame_or_hollow_box`

样本 29 的矩形框→`frame_or_hollow_box`。规则：`profile.type==rectangular_frame`。

### 3.6 `validation_intents` 增 `inner_void_check`

对带内环的 profile（annulus/rectangular_frame/polygon_with_holes），验证"内环确实形成穿透 void"：
```
{"id": "q_void_count", "intent": "through_void_count", "expected": 1}
```
通过 genus（欧拉示性数）或拓扑孔计数验证。

---

## 4. 四项标准复核（v0.3 vs v0.4）

| 标准 | v0.3 | v0.4 | 改进点 |
|---|---|---|---|
| Sufficiency | ⚠️ | ✅ | direction 字段；多 profile；rectangular_frame；curve_field source |
| Non-Procedurality | ✅ | ✅ | profiles[] 不规定建模顺序，仅描述合并结果 |
| Verifiability | ⚠️ | ✅ | distance_total+direction 解耦；through_void_count intent |
| Non-Leakage | ✅ | ✅ | 保持 |

---

## 5. v0.4 未解决问题（留给 v0.5）

1. **RevolveFeature**：仍不覆盖（本轮无旋转体样本）
2. **FilletFeature 作为 post-extrude 特征**：仍把圆角归入 profile（polygon_with_fillets），未区分 in-sketch fillet 与 post-extrude edge fillet
3. **多 body 装配关系谓词**：仍单 body 为主
4. **Taper（拔模角）非零**：v0.4 仍记录 taper_angle_deg 但本轮样本均为 0；非零 taper 的 dimensions 语义未验证

---

## 6. 实施计划

1. 写 `DesignPlan/DesignPlan_schema04.txt`（v0.4 模板，落实 §3 全部改进）
2. 用 v0.4 手写 10 个样本（21–30），归档 `DesignPlan/samples/v4/`
3. 基于样本 21–30 实现 + 测试确定性 compiler，写 `doc/complier可行性验证-样本20-30.md`
