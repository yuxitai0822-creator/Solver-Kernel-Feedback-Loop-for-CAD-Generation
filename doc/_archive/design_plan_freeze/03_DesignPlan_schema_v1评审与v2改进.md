# 03 Design Plan Schema v1 评审与 v2 改进建议

> **背景**：根据用户给出的 Design Plan 概念定位（结构化中间表示、解耦设计与建模过程、信息量少于建模历史 JSON、四项好坏标准 Sufficiency / Non-Procedurality / Verifiability / Non-Leakage），对 `DesignPlan/DesignPlan_schema01.txt` 第一版 schema 进行评审，并基于对 sanity set 前 5 个样本的手写 Design Plan 实践（见 `DesignPlan/samples/`），提出 v2 改进建议。
>
> **评审方法**：以 schema 中每个字段为粒度，逐项用"四项标准 + 实际样本验证"交叉检查。每个发现都附上样本证据。

---

## 1. 评审总结

| 维度 | v1 评分 | 主要问题 |
|---|---|---|
| Sufficiency（充分性） | ⚠️ 中等 | 缺少"坐标系规约/单位/方向语义"的强约束；特征参数对圆/弧支持不足 |
| Non-Procedurality（非过程性） | ❌ 弱 | `base_geometry` + `features` 的"基体+特征"分解本质上是建模顺序的隐式编码 |
| Verifiability（可验证性） | ✅ 较好 | `validation_intents` 设计方向正确，但 `source` JSONPath 字段冗余且耦合 |
| Non-Leakage（非泄露性） | ❌ 弱 | `global_envelope.bbox` 直接照搬 GT 的精确 bbox 值，是典型的 GT 泄露 |

**结论**：v1 schema 的整体骨架可用，但需要在 4 个方向上做实质性修订才能满足用户给出的 Design Plan 概念定位。

---

## 2. 字段级问题清单

### 2.1 ❌ 严重：`base_geometry` + `features` 的分解泄漏了建模过程

**问题**：v1 schema 把零件拆成 `base_geometry`（一个矩形棱柱）+ `features`（孔阵列）。这种"先建基体、再加特征"的分解方式**本质上就是建模时间线的抽象**——它只是把 Fusion360 的 `timeline` 从"操作序列"压缩成"两个语义块"，但仍然规定了建模顺序。

**证据**：在 sanity set 前 5 个样本中，**所有 5 个样本都是单步拉伸矩形棱柱**，没有附加特征。如果按 v1 schema 填写，每个样本都只能是"`base_geometry`=rectangular_prism, `features`=[]"。这说明：
- 对简单零件，`features` 字段总是空的，是冗余结构
- 对复杂零件，"哪个是 base、哪些是 feature"取决于建模者主观选择，不是零件本身的属性

**违反标准**：Non-Procedurality。

### 2.2 ❌ 严重：`global_envelope.bbox` 是 GT 泄露

**问题**：v1 schema 在 `global_envelope.bbox` 里直接写死了精确的 bbox 三轴尺寸（80.0, 50.0, 12.0）。但 bbox 是**几何结果**，不是**设计需求**——设计需求是"长 80、宽 50、高 12"，至于最终 bbox 是不是恰好 (80,50,12)，取决于有没有倒角、圆角、拔模。

**证据**：在样本 `100243_9fb796fe_0005` 中，bbox 恰好是 (1.9, 20.0, 1.9)，因为它是无特征的纯棱柱。但如果同一个零件加了 0.5mm 倒角，bbox 会变成 (1.9, 20.0, 1.9)（倒角不改变棱柱外包络），但 face_count 会从 6 变成 6+8=14。把 bbox 当作"设计需求"写入 Design Plan，会让带倒角的等价设计被判失败。

**违反标准**：Non-Leakage（bbox 是 GT 独有信息）+ Verifiability（bbox 不能区分"等价类内的合法变体"）。

### 2.3 ⚠️ 中等：`coordinate_system` 的 origin 用世界坐标，泄漏装配上下文

**问题**：v1 schema 的 `coordinate_system.origin` 默认是 `[0,0,0]`，但 Fusion360 的世界坐标原点是装配上下文的，不是零件本身的。样本 1 的 sketch 起点在 (-58.278, 0, 12.040)，这是它在 drone leg 装配中的位置，不是它的设计属性。

**违反标准**：Non-Leakage。

### 2.4 ⚠️ 中等：`validation_intents[].source` 字段冗余

**问题**：v1 schema 的每个 validation_intent 都带一个 `source` 字段，用 JSONPath 指回 Design Plan 自身的某个字段（如 `"source": "$.global_envelope.bbox.x"`）。这是冗余的——KQP compiler 既然能读 Design Plan，就能自己定位字段，不需要 Design Plan 显式告诉它。

**违反标准**：Verifiability（耦合了"声明意图"和"实现细节"）。

### 2.5 ⚠️ 中等：缺少对"方向语义"的显式表达

**问题**：v1 schema 用 `"axis": "z"` 这样的字符串表示方向，但 sanity set 的样本 1 和 5 的 sketch normal 不是 Z 轴（分别是 Y 和接近 Y），而是 XZ 平面。如果 Design Plan 只说"axis=z"，KQP 就无法验证非轴向的拉伸方向。

**证据**：
- 样本 1：sketch normal=(0,1,0)，沿 Y 拉伸
- 样本 5：sketch normal≈(0,1,0)（数值上 9.59e-32, 1.0, -3.26e-16），沿 Y 拉伸

**违反标准**：Sufficiency（不足以表达真实设计意图）+ Verifiability（无法对非轴向几何验证）。

### 2.6 ⚠️ 中等：`features` 的字段结构对非矩形特征支持不足

**问题**：v1 schema 的 `features` 示例只详细定义了 `through_hole_pattern`，但 sanity set 的扩展集（8625 序列）包含 16 种约束、9 种尺寸类型，对应的特征远不止孔阵列：圆弧拉伸、L 形截面、阶梯块等。当前 schema 没有为这些情况预留结构。

**违反标准**：Sufficiency。

### 2.7 ✅ 较好：`target.body_count` 和 `validation_intents` 方向正确

**问题**：无。`body_count=1` 是真正的设计需求（"这是一个单体零件"），KQP 能直接验证。`validation_intents` 把"要验证什么"和"期望值"显式列出，符合 Verifiability 标准。

### 2.8 ⚠️ 轻微：schema 文件本身有语法错误

**问题**：`DesignPlan_schema01.txt` 不是合法 JSON（有 `#` 注释、有中文逗号 `，`、有中文引号 `“”`）。虽然标注是"暂定 JSON"，但作为 schema 模板，应该至少是合法 JSONC 或 YAML。

---

## 3. v2 改进建议

基于以上评审，提出 v2 schema 的改进。**核心理念**：从"基体+特征的过程化分解"转向"几何体 + 参数 + 关系"的结果级描述。

### 3.1 结构性改进

#### 改进 A：用 `solid_bodies[]` 替代 `base_geometry + features`

```
"solid_bodies": [
  {
    "id": "body_0",
    "primitive_type": "rectangular_prism",   // 或 cylinder, extruded_profile, ...
    "envelope": {                            // 设计意图的尺寸，不是 GT bbox
      "length_along_u": {"value": 80.0, "tol": 0.1},
      "width_along_v":  {"value": 50.0, "tol": 0.1},
      "height_along_w": {"value": 12.0, "tol": 0.1}
    },
    "frame": {                               // body-local 坐标系
      "u_dir": [1,0,0], "v_dir": [0,1,0], "w_dir": [0,0,1],
      "origin": [0,0,0]                      // body-local 原点，不是世界坐标
    },
    "modifications": []                      // 该 body 上的局部修改（孔/槽/倒角），按需
  }
]
```

**理由**：每个 body 是一个独立的几何单元，有自己的局部坐标系和尺寸。`modifications` 是可选的、该 body 局部的修改列表，**不规定建模顺序**（可以先建孔再拉伸，也可以先拉伸再打孔，结果等价）。

#### 改进 B：把 `global_envelope.bbox` 改为 `design_envelope`（设计包络，非 GT）

```
"design_envelope": {
  "intent": "bounding_dimensions",           // 明确这是设计意图，不是测量值
  "along_x": {"value": 80.0, "tol": 0.1},
  "along_y": {"value": 50.0, "tol": 0.1},
  "along_z": {"value": 12.0, "tol": 0.1},
  "note": "Design specifies 80x50x12 nominal. Final bbox may differ within tolerance."
}
```

**理由**：明确标注这是"设计意图的标称尺寸"，KQP 验证时允许在 tolerance 内浮动，避免把倒角/圆角等合法变体判失败。

#### 改进 C：用 `frame` 显式表达任意方向

不再用 `"axis": "z"` 这种字符串，改用 `[u_dir, v_dir, w_dir]` 三个正交单位向量。对轴向情况退化为标准基，对非轴向（如样本 5 的 9.59e-32 噪声）也能精确表达。

#### 改进 D：删掉 `validation_intents[].source`，改为 compiler 自动推导

Design Plan 只声明 `intent` + `expected` + `tolerance`，KQP compiler 根据 `intent` 类型自动选择查询实现。`source` JSONPath 是实现细节，不应出现在 schema 里。

#### 改进 E：坐标系改为 `part_local`，世界坐标归入 `non_verifiable`

```
"coordinate_system": {
  "frame": "part_local",
  "origin_convention": "bbox_min_corner",    // 或 "centroid" / "first_sketch_point"
  "axes": {"x":[1,0,0], "y":[0,1,0], "z":[0,0,1]}
},
"non_verifiable": {
  "world_pose": "Assembly-context world coordinates are not part of the design spec."
}
```

### 3.2 新增字段

| 新字段 | 用途 | 来源样本证据 |
|---|---|---|
| `non_verifiable` | 显式标记"哪些信息是 GT 独有、设计不需要的" | 所有 5 个样本的世界坐标都应归入此 |
| `compiler_notes` | 给确定性 compiler 的提示（如"此样本欠约束"） | 样本 5 只有 1 个显式尺寸 |
| `tolerance`（每个数值字段） | 明确允许的工程公差 | 避免浮点噪声导致误判 |

### 3.3 删除字段

| 删除字段 | 原因 |
|---|---|
| `base_geometry`（作为顶层字段） | 与 `features` 一起被 `solid_bodies[]` 替代 |
| `global_envelope.bbox`（精确 GT 值） | 改为 `design_envelope`（标称值 + tolerance） |
| `validation_intents[].source` | 实现细节，compiler 自动推导 |
| `spatial_relations`（v1 中的 `hole_count` 重复定义） | 与 `features[].count` 重复，删冗余 |

---

## 4. v2 Schema 草案（关键片段）

```jsonc
{
  "schema_version": "design_plan_v0.2",
  "sample_id": "...",
  "unit": "mm",

  "coordinate_system": {
    "frame": "part_local",
    "origin_convention": "bbox_min_corner",
    "axes": {"x":[1,0,0], "y":[0,1,0], "z":[0,0,1]}
  },

  "target": {
    "object_type": "single_part",
    "part_category": "...",
    "body_count": 1,
    "engineering_description": "..."
  },

  "design_envelope": {
    "intent": "bounding_dimensions",
    "along_x": {"value": 80.0, "tol": 0.1},
    "along_y": {"value": 50.0, "tol": 0.1},
    "along_z": {"value": 12.0, "tol": 0.1}
  },

  "solid_bodies": [
    {
      "id": "body_0",
      "primitive_type": "rectangular_prism",
      "frame": {
        "u_dir": [1,0,0], "v_dir": [0,1,0], "w_dir": [0,0,1],
        "origin": [0,0,0]
      },
      "dimensions": {
        "length_along_u": {"value": 80.0, "tol": 0.1},
        "width_along_v":  {"value": 50.0, "tol": 0.1},
        "height_along_w": {"value": 12.0, "tol": 0.1}
      },
      "modifications": []
    }
  ],

  "constraints": [
    {
      "type": "orthogonal_adjacent_edges",
      "subject": "body_0",
      "expected": "edges fall into 3 mutually-orthogonal direction groups",
      "verifiable_via": "edge_direction_dot_product"
    }
  ],

  "validation_intents": [
    {"id": "q_body_count", "intent": "body_count", "expected": 1},
    {"id": "q_envelope_x", "intent": "bbox_size", "axis": "x",
     "expected": 80.0, "tolerance": 0.1},
    {"id": "q_all_planar", "intent": "all_faces_planar", "expected": true},
    {"id": "q_is_solid",   "intent": "is_solid",         "expected": true}
  ],

  "non_verifiable": {
    "world_pose": "Assembly-context coordinates omitted."
  },

  "compiler_notes": {}
}
```

---

## 5. 四项标准复核

对 v2 草案逐项复核：

| 标准 | v1 | v2 | 改进点 |
|---|---|---|---|
| **Sufficiency** | ⚠️ | ✅ | `frame` 显式表达任意方向；`solid_bodies` 支持多体；`modifications` 支持局部特征 |
| **Non-Procedurality** | ❌ | ✅ | 删除 `base_geometry`/`features` 的过程化分解；`modifications` 不规定顺序 |
| **Verifiability** | ✅ | ✅ | 删除冗余 `source`；`tolerance` 显式化；`intent` 枚举可被 KQP 直接消费 |
| **Non-Leakage** | ❌ | ✅ | `design_envelope` 取代 GT bbox；世界坐标归入 `non_verifiable`；删除精确 topology 计数 |

---

## 6. 待解决问题（Open Questions）

以下问题在本次评审中识别但未定论，需要后续实验或讨论确认：

1. **`modifications` 的粒度**：倒角、圆角是"modification"还是"base geometry 的一部分"？v2 暂列为 modification，但可能需要进一步分类。

2. **多 body 零件的位置关系**：v2 用 `solid_bodies[]` 支持多体，但 body 之间的相对位置（如"孔阵列传回 body_0"）如何表达而不泄漏建模过程？需要设计一套"关系谓词"（如 `centered_on`、`coaxial_with`）。

3. **欠约束样本的处理**：样本 5 只有 1 个显式尺寸，另一个尺寸是从点坐标反推的。compiler 如何区分"显式设计意图"和"隐式几何后果"？是否需要在 Design Plan 中标注 `inferred_from: "point_span"`？

4. **`engineering_description` 是否可验证**：自然语言描述（如"square strut"）无法被 KQP 直接验证，但有助人类理解。是否应归入 `non_verifiable`？

5. **公差的来源**：v2 给每个数值都加了 tolerance，但 tolerance 本身从哪来？是从 Fusion360 的 ModelParameter 推断，还是全局默认？需要制定 tolerance 推断规则。

---

## 7. v0.2 实践复审：手写 5 样本后发现的新缺陷

> 本节是在用 v0.2 schema 实际手写 5 个 Design Plan（归档于 `DesignPlan/samples/v2/`）之后追加的复审。手写过程暴露了 v0.2 草案（即上文第 4 节）的 6 个新缺陷，需要 v0.3 修复。

### 7.1 ❌ 数据冗余：同一尺寸出现在 3 处

**发现**：以样本 1 为例，1.9mm 这个值同时出现在：
- `solid_bodies[0].profile.parameters.side_u.value` (=1.9)
- `solid_bodies[0].dimensions.along_u.value` (=1.9)
- `derived.design_envelope.along_x` (=1.9)

三处都是 1.9，但语义略有不同（profile 是草图尺寸、dimensions 是 body 尺寸、envelope 是世界轴尺寸）。对纯棱柱三者恰好相等，但：
- 加倒角后，`dimensions` 不变但实际 bbox 可能变（envelope ≠ dimensions）
- 旋转 frame 后，`along_x` 不等于 `along_u`

**风险**：三个真值源（source of truth）会导致 compiler 和 KQP 不一致。如果 compiler 只填了一处忘了另一处，验证就会出错。

**v0.3 建议**：明确**唯一真值源 = `solid_bodies[].dimensions`**。删除 `profile.parameters`（或仅保留非尺寸信息如 `curve_count`），删除 `derived.design_envelope`（由 KQP compiler 自己算，不存 Design Plan）。

### 7.2 ❌ bbox 验证与 frame-based dimensions 的轴映射缺失

**发现**：v0.2 的 `validation_intents` 用 `bbox_size axis:x` 表达世界轴 bbox，但 `solid_bodies[].dimensions` 用 `along_u/along_v/along_w`（frame 轴）。这两套坐标系之间的映射关系在 schema 中没有定义。

**证据**：样本 1 的 frame 是 u=(0,0,1), v=(1,0,0), w=(0,1,0)。所以：
- `along_u=1.9` 对应世界 Z（不是 X！）
- `along_v=1.9` 对应世界 X
- `along_w=20.0` 对应世界 Y

我手写时在脑中做了这个映射（envelope_x=1.9=along_v，envelope_y=20.0=along_w，envelope_z=1.9=along_u），但 schema 没有强制这个映射规则。对 5 个轴对齐样本还能手算，对旋转 frame 会出错。

**v0.3 建议**：`bbox_size` intent 直接引用 frame 轴：`{"intent": "bbox_size", "frame_axis": "u", "expected": 1.9}`，由 KQP compiler 把 frame_axis 投影到世界轴计算 bbox。或者更彻底：删除世界轴 bbox 验证，只验证 frame 轴 span（这正是 exp01 KQP 已实现的 `span_u`/`span_v`/`height_along_normal`）。

### 7.3 ⚠️ `extrude.distance` 与 `dimensions.along_w` 完全重复

**发现**：对单向拉伸，`extrude.distance.value` 恒等于 `dimensions.along_w.value`。我在 5 个样本里都填了相同的值。这是冗余。

**但**：对 `two_side` 或 `symmetric` 拉伸，`extrude.distance` 是总长（两段之和），而 `along_w` 也是总长——仍然相等。所以这个冗余是结构性的，不是偶发的。

**v0.3 建议**：保留 `extrude` 块（含 `extent_type`/`operation`/`taper`），但删除 `extrude.distance`，让 `dimensions.along_w` 成为唯一长度真值源。`extrude` 块只保留非尺寸的拉伸语义（方向类型、操作类型、锥角）。

### 7.4 ⚠️ `part_category` 缺乏量化分类规则

**发现**：我手写时凭直觉分类（样本 1/2 是 square_strut，样本 3/4 是 flat_plate，样本 5 是 slat）。但"square_strut vs block"的边界是什么？我用了"两边相等且第三边显著长"的模糊标准。

**证据**：样本 1 是 1.9×1.9×20（长宽比 20/1.9≈10.5），样本 5 是 9.525×1.905×57.15（三个维度都不同）。如果我给样本 5 也叫 square_strut 就错了。

**v0.3 建议**：`part_category` 改为 **derived 字段**（从 dimensions 算），并给出量化规则表：
- `aspect_ratio = max_dim / min_dim`
- `aspect_ratio > 5` 且最小维是厚度 → `flat_plate` / `slat` / `strut`
- 两较小维相等 → `square_strut` / `cylinder`
- 三维接近（比 < 1.5）→ `block`
- 否则 → `rectangular_prism_generic`

由于 `part_category` 不可验证（自然语言），归入 `non_verifiable`，compiler 用规则自动填，失败填 `uncategorized`。

### 7.5 ⚠️ `source_constraints` 只是字符串列表，不可机器消费

**发现**：我在 `compiler_notes.source_constraints` 写了 `["HorizontalConstraint x2", "VerticalConstraint x2"]`。这是给人看的，机器无法解析"x2"。

**v0.3 建议**：改为结构化：
```json
"source_constraints": [
  {"type": "HorizontalConstraint", "count": 2},
  {"type": "VerticalConstraint", "count": 2},
  {"type": "CoincidentConstraint", "count": 1, "note": "geometrically_inert"}
]
```

### 7.6 ⚠️ tolerance 的单位歧义

**发现**：v0.2 给薄板厚度用了 `tol: 0.005`，给结构尺寸用了 `tol: 0.01`。但 schema 没说明 tolerance 是绝对值（mm）还是相对值（比例）。我默认用了绝对 mm，但对大尺寸（如 200mm）0.01mm 的绝对公差可能过严。

**证据**：样本 1 的 extrude=20.0，tol=0.01（相对 0.05%）。如果换成 200mm 的拉伸，0.01mm 就是相对 0.005%，可能因浮点误差误判。

**v0.3 建议**：tolerance 字段增加 `kind: "absolute" | "relative"`，默认 `absolute`。或采用混合规则：`effective_tol = max(absolute_tol, value * relative_tol)`，默认 `relative_tol = 1e-4`。

---

## 8. v0.3 修订要点总结

基于第 7 节的 6 个发现，v0.3 的核心修订是**消除冗余、统一坐标系语义**：

| 修订项 | 操作 | 解决的缺陷 |
|---|---|---|
| 删除 `profile.parameters` 的尺寸字段 | 只保留 `curve_count` 等非尺寸信息 | 7.1 冗余 |
| 删除 `derived.design_envelope` | KQP compiler 自行从 dimensions 投影计算 | 7.1 + 7.2 |
| 删除 `extrude.distance` | `dimensions.along_w` 为唯一长度源 | 7.3 冗余 |
| `bbox_size` intent 改用 `frame_axis` | 而非世界 `axis` | 7.2 轴映射 |
| `part_category` 归入 derived + 量化规则 | 或直接删除（不可验证） | 7.4 |
| `source_constraints` 结构化 | `[{type, count, note}]` | 7.5 |
| `tolerance` 增加 `kind` 字段 | 支持 absolute/relative | 7.6 |

**关键原则**：Design Plan 应该是**最小充分集**——每个事实只出现一次，出现在最权威的位置（`solid_bodies[].dimensions`）。所有其他字段要么是 derived（标注来源），要么是 metadata（标注不可验证）。v0.2 在"结果级描述"方向上正确，但在"最小化"上做得不够，v0.3 收紧。
