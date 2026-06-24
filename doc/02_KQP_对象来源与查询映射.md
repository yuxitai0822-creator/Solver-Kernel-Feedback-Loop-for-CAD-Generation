# KQP 对象来源与查询映射设计（基于 Sanity Set）

> **核心问题**（来自任务）：确定性 KQP Compiler 要把"建模序列 → KQP"做成语义完全等价的映射。那么：
> 1. **拓扑查询的对象**（body/face/edge/vertex/shell/loop 数）从何处获取？
> 2. **尺寸查询的对象**（bbox、厚度、高度、孔径、距离、面积、体积）从何处获取？
> 3. **特征查询的对象**（孔/槽/凸台是否存在）从何处获取？
> 4. **健康查询的对象**（模型合法性）从何处获取？
> 5. 建模序列中**哪些语义要素不能遗漏**？
>
> 本文基于 50 个 sanity 样本（`data/sanity_set_50/`）逐一给出"JSON 来源 → KQP 期望值 → 查询实现"的确定性映射表。
> **配套**：`doc/01_Sanity50_建模序列结构分析.md`（结构基础）。

---

## 0. 核心原则：双源对齐（GT 验证 + 设计意图）

KQP 的每个查询都有**两个来源**，Compiler 必须让二者一致：

| 角色 | 来源 | 用途 |
|---|---|---|
| **设计意图值**（design intent） | `entities` 里的 sketch/extrude 字段（半径、高度、loop 数…） | 表达"设计方案要求什么"，是 KQP 的**主要语义依据** |
| **GT 几何值**（ground truth） | 顶层 `properties`（body_count、bbox、volume…） | 表达"重建后几何体实际是什么"，用于 **compiler 内部自检** |

> **判定规则**：Compiler 先从 entities 算出"设计意图值"，再与 properties 的 GT 比对。若一致 → 正常生成 KQP；若不一致 → 标记为 `OVER_CONSTRAINED` 或数据异常（不应静默忽略，因为这正是反馈闭环要捕获的失败模式）。

这一原则直接回应了实验设计里"KQP 要保持与设计方案相同的语义"——语义来自 entities，properties 是验证基准。

---

## 1. A 类：拓扑查询 —— 对象来源

KQP 的拓扑查询检查"模型有没有生成正确的结构数量"。**期望值（应有多少）来自哪里？**

### 1.1 期望值的确定性来源

对 sanity set（单 sketch+extrude，全 NewBody 操作），拓扑数量可**从草图/拉伸结构解析推导**：

| 拓扑量 | KQP 期望值来源（entities 解析） | GT 验证（properties） |
|---|---|---|
| `body_count` | operation=NewBody 且首个 extrude → **1**；N 个独立 NewBody extrude → N | `properties.body_count` |
| `shell_count` | 通常 = body_count（单壳实体） | `properties.shell_count` |
| `face_count` | 由草图轮廓几何推导（见 §1.2 公式） | `properties.face_count` |
| `edge_count` | 由轮廓几何推导 | `properties.edge_count` |
| `vertex_count` | 由轮廓几何推导 | `properties.vertex_count` |
| `loop_count` | face 的环数，通常 = face_count（每面1外环）+ 内环数 | `properties.loop_count` |

### 1.2 face/edge/vertex 的解析公式（sanity set 已验证）

对"1 外环 + k 个内环（孔）、外环含 L 条直线段 + C 个完整圆"的 sketch，单向拉伸 NewBody 后（基于欧拉-庞加莱公式与拉伸拓扑规则）：

- `face_count = 2(顶底面) + 侧面数`，侧面数 = 外环边数 + 内环边数中的直线/圆弧（每个独立线段/圆弧拉伸成 1 个侧面）。完整圆环拉伸成 1 个圆柱面。
- `vertex_count = 2 × 轮廓顶点数`（顶底面各一份）。
- `edge_count = 3 × 轮廓边数 − 内环修正`（竖边 + 顶底水平边）。

> ⚠️ 这些公式仅对 sanity set 的简单情形成立。**实践中 Compiler 不应硬算公式**，而应采用更稳健的策略（见 §1.3）。

### 1.3 推荐的 Compiler 策略：以 properties 为主 + 结构性约束

由于直接从草图解析 face_count 在含圆弧/相切时易错（相切圆弧会合并边），**Compiler 对拓扑量采用"properties GT 为期望值 + 结构性断言"的混合策略**：

1. **期望值 = `properties.<count>`**（确定性、零歧义）。
2. **附加结构性 KQP**：从 entities 生成"设计意图级"断言，如：
   - `body_count == 1`（因 operation=NewBody 且仅 1 extrude）—— 若 properties 不是 1，说明重建出错。
   - `外环存在性`: profile 必须有且仅有 1 个 `is_outer==true` 的 loop。
   - `内环数 == 孔数`: `sum(len(loops)-1 for profile)` 应等于预期孔数。

这样拓扑查询的"期望值"既来自 GT（精确），又通过结构性断言与设计意图绑定（语义一致）。

### 1.4 KQP 拓扑查询的最终生成形式（建议 JSON）

```jsonc
// KQP fragment (sample 100243_9fb796fe_0005)
{
  "topology": {
    "body_count":   {"expect": 1,  "source": "properties.body_count",
                     "rationale": "operation=NewBodyFeatureOperation, 1 extrude"},
    "shell_count":  {"expect": 1,  "source": "properties.shell_count"},
    "face_count":   {"expect": 6,  "source": "properties.face_count"},
    "edge_count":   {"expect": 12, "source": "properties.edge_count"},
    "vertex_count": {"expect": 8,  "source": "properties.vertex_count"},
    "loop_count":   {"expect": 6,  "source": "properties.loop_count"},
    "structure_asserts": [
       {"assert": "has_exactly_one_outer_loop", "per_profile": true},
       {"assert": "inner_loop_count", "expect": 0, "rationale": "no inner loops in sketch"}
    ]
  }
}
```

---

## 2. B 类：尺寸查询 —— 对象来源

尺寸查询检查 bbox、厚度、高度、孔径、距离、面积、体积。**每一项的期望值来源如下：**

| KQP 尺寸项 | 设计意图来源（entities） | GT 来源（properties） | 备注 |
|---|---|---|---|
| `bounding_box_x/y/z` | 由 points 极值 + extrude 距离推导 | `properties.bounding_box.{min,max}_point` | 直接用 GT 最稳 |
| `height_along_extrude` | `extrude.extent_one.distance.value` + `plane.normal` | bbox 沿 normal 轴投影 | **必读字段**：distance.value |
| `thickness` | profile 内外环间距 或 两平行直线距离 | bbox 最小维度 或 face 距离 | 视设计语义 |
| `cylinder_radius` / `hole_radius` | `curves[*].radius`（Circle/Arc） | 推断自圆柱面 | **必读字段**：radius |
| `hole_diameter` | `dimensions[SketchDiameterDimension].parameter.value` | — | driving dimension 优先 |
| `plane_area` (草图面积) | `profiles[*].properties.area` | — | sketch 自带 |
| `volume` | — | `properties.volume` | 只能从 GT |
| `center_distance` | `points` 两点欧氏距离 | — | 计算 |

### 2.1 拉伸高度查询的精确推导（关键，易错）

拉伸高度（沿拉伸轴的尺寸）的"设计意图值"：

```
ext_axis = sketch.reference_plane.plane.normal        # 拉伸方向
raw_dist = extrude.extent_one.distance.value          # 拉伸距离值
if extent_type == "OneSideFeatureExtentType":
    height = raw_dist
elif extent_type == "SymmetricFeatureExtentType":
    height = raw_dist                  # value 已是总高（对称分布）
elif extent_type == "TwoSidesFeatureExtentType":
    height = extrude.extent_one.distance.value + extrude.extent_two.distance.value
taper_angle = extrude.extent_one.taper_angle.value    # 非零时侧面带斜度，需 KQP 容忍
```

**GT 校验**：`height ≈ bbox 沿 ext_axis 的投影长度`（容差 1e-3）。样例 `100243`：distance.value=20.0，bbox y 维（normal=(0,1,0)）= 20.0 − 0.0 = 20.0 ✅ 一致。

> **不能遗漏**：若只读 `extent_one.distance.value` 而忽略 `extent_type` 与 `plane.normal`，则 TwoSides/Symmetric 样本的高度查询必然错。这正是 §5 清单第 1–3 条。

### 2.2 孔径/半径查询的精确来源

- **设计意图值** = `curves[<Circle-uuid>].radius`（来自 sketch）。
- **若该圆被标注了 driving SketchDiameterDimension**，则直径期望值 = `dimension.parameter.value`（语义更强，是设计师明确的尺寸）。
- 二者应一致：`2 × radius ≈ diameter.value`。Compiler 交叉验证，不一致则报警（过约束线索）。

### 2.3 KQP 尺寸查询的最终生成形式

```jsonc
{
  "dimensions": {
    "extrude_height": {"expect": 20.0, "tol": 1e-3,
       "source": "extrude.extent_one.distance.value",
       "axis": "plane.normal (0,1,0)", "extent_type": "OneSideFeatureExtentType"},
    "bbox_x": {"expect": 2.0,  "source": "properties.bounding_box", "tol":1e-3},
    "bbox_y": {"expect": 20.0, "source": "properties.bounding_box", "tol":1e-3},
    "bbox_z": {"expect": 1.9,  "source": "properties.bounding_box", "tol":1e-3},
    "volume":  {"expect": 72.2, "source": "properties.volume", "tol":1e-2}
  }
}
```

---

## 3. C 类：特征查询 —— 对象来源（孔/槽/凸台是否存在）

> **重要边界**（见 `data/report.md` R2）：本数据集**无独立 Hole/Slot/Boss 特征实体**，"孔"由 sketch 内环 + extrude 实现。因此特征查询必须映射到**拓扑/曲面类型**，不能查 HoleFeature 实体。

| 特征 | 判定来源（entities 语义） | 判定来源（GT） | KQP 实现 |
|---|---|---|---|
| 圆孔（through/盲孔） | profile 含 `is_outer==false` 的内环 + 内环曲线为 Circle | `surface_types` 含 CylindricalSurfaceType | `surface_types` 中 Cylinder 数量 == 内环 Circle 数；face_count 含相应圆柱面 |
| 矩形槽 | profile 含矩形内环 | bbox/face 凹陷 | 内环边数为 4 且为直线 |
| 凸台（本集合无） | 多 body 或 Cut/Join | body_count>1 | 扩展 Phase1 时补充 |

### 3.1 特征查询生成形式

```jsonc
{
  "features": {
    "hole_count": {"expect": 0, "rationale": "no inner loop in referenced profile",
                   "cross_check": "surface_types CylindricalSurfaceType count"},
    "cylinder_face_count": {"expect": 0, "source": "surface_types"},
    "has_through_hole": false
  }
}
```

样例 `100243` 的 `properties.surface_types = [{PlaneSurfaceType, face_count:6}]`，无圆柱面 → hole_count=0 ✅。

---

## 4. D 类：健康查询 —— 对象来源

健康查询检查几何内核层面的模型合法性。来源：

| 健康项 | 来源 | 说明 |
|---|---|---|
| 实体闭合（valid solid） | 执行结果（OCP `BRepCheck`） | KQP 调用内核验证 |
| 拓扑合法 | `properties.vertex_valence`（每个顶点价=3 等） | 欧拉规则 |
| 无自交/零长边 | 执行结果 | 内核 check |
| `shell_count>0` 且 body 是 solid | `properties.body_count/shell_count` | 必为 solid body |

```jsonc
{
  "health": {
    "is_valid_solid": {"expect": true},
    "euler_check": {"V-E+F=2*S-2H", "V":8,"E":12,"F":6,"S":1},
    "min_vertex_valence": {"expect": 3, "source": "properties.vertex_valence"}
  }
}
```

---

## 5. 建模序列中不能遗漏的语义要素（汇总 + 风险分级）

按"遗漏后果严重度"分级，**Compiler 必须读取**的字段：

### 🔴 致命级（遗漏 → KQP 语义彻底错误）

| 要素 | JSON 路径 | 后果 |
|---|---|---|
| 拉伸高度 | `extrude.extent_one.distance.value` | 高度/体积查询无意义 |
| 拉伸轴 | `sketch.reference_plane.plane.normal` | bbox 维度-语义错位（哪维是高度） |
| extent_type | `extrude.extent_type` | TwoSides/Symmetric 高度计算错 |
| 内/外环结构 | `profile.loops[*].is_outer` + `profile_curves` | 孔数量、face_count、特征查询全错 |
| extrude→sketch→profile 依赖链 | `extrude.profiles[{profile,sketch}]` | 无法回溯几何，KQP 退化 |

### 🟡 重要级（遗漏 → 部分查询失效）

| 要素 | JSON 路径 | 后果 |
|---|---|---|
| 圆/弧半径 | `curves[*].radius` | 孔径/圆柱半径查询失效 |
| 直线端点 | `curves[*].{start_point,end_point}` + `points[*]` | 长度/宽度/厚度查询失效 |
| driving dimensions | `dimensions[*]` (`is_driving==true`) | 设计意图关键尺寸丢失 |
| 草图面积/周长 | `profile.properties.{area,perimeter}` | 草图面积查询失效 |
| 草图平面变换 | `reference_plane.corrective_transform` | 局部↔世界坐标错位 |
| taper_angle | `extrude.extent_one.taper_angle.value` | 带拔模时侧面几何偏差 |

### 🟢 辅助级（用于自检/扩展）

| 要素 | JSON 路径 | 用途 |
|---|---|---|
| 约束图 | `constraints[*]` | Solver 侧可解性，间接验证 |
| operation | `extrude.operation` | 本集合全 NewBody；Phase1 扩展时区分 Cut/Join 影响 body_count 语义 |
| properties 全部 17 项 | `properties.*` | Compiler 内部 GT 自检 |
| fully_constrained | `curves[*].fully_constrained` | 欠约束预警（UC 样本识别） |

---

## 6. KQP Compiler 的确定性映射总表（一图流）

```
                    ┌─────────────── entities ───────────────┐
   JSON Plan ──────►│ Sketch: plane.normal, curves.radius,   │
                    │         points, profiles.loops,        │
                    │         dimensions(driving)            │
                    │ Extrude: extent_type, distance.value,  │
                    │          profiles→{sketch,profile}     │
                    └───────────────────┬────────────────────┘
                                        │ deterministic extract
                    ┌───────────────────▼────────────────────┐
                    │ 设计意图值 (design intent)             │
                    │  height, radius, hole_count, asserts   │
                    └───────────────────┬────────────────────┘
                                        │ cross-check (自检)
                    ┌───────────────────▼────────────────────┐
                    │ properties (GT)  ◄── 不一致则报警       │
                    └───────────────────┬────────────────────┘
                                        │
                                generate KQP (4 类查询)
                                        ▼
            ┌──────────┬──────────┬──────────┬──────────┐
            │ A 拓扑   │ B 尺寸   │ C 特征   │ D 健康   │
            │body/face │bbox/高/径│hole/cyl  │solid/欧拉│
            └──────────┴──────────┴──────────┴──────────┘
```

**映射的确定性保证**：
1. 无 LLM 参与（纯 JSON 解析 + 算术）。
2. 每个 KQP 期望值标注 `source`（设计意图路径）与 GT 交叉校验，语义可追溯。
3. 幂等：相同输入 JSON 永远产出相同 KQP。

---

## 7. 结论与下一步

1. **拓扑/尺寸/特征/健康四类查询的对象来源已全部定位**：设计意图来自 `entities`（sketch/extrude 字段），GT 验证来自 `properties`。Compiler 采用"双源对齐 + 结构性断言"策略，规避纯公式解析的不稳健。
2. **不能遗漏的致命级要素 5 项**（§5 🔴），Compiler 必须强制读取并在缺失时报错。
3. **下一步**：基于本文的映射表实现 `kqp_compiler.py`（确定性 JSON→KQP），并用 50 样本验证：① KQP 期望值与 properties GT 全部一致；② 对 LLM 生成的 CAD 脚本执行 KQP，验证能否正确区分 pass/fail。

> 本设计可直接覆盖 sanity set（Phase0）。扩展到 Phase1（多 sketch/多 extrude、Cut/Join）时，仅需在 §1.3 增补 operation→body_count 语义、在 §3 增补 Cut/Join 特征映射，核心映射表不变。
