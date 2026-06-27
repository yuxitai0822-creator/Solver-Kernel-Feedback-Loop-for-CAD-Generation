# 04 建模序列 JSON → Design Plan 确定性 Compiler 设计

> **目标**：设计一个确定性 compiler，将 Fusion360 Gallery 的建模历史 JSON 自动转换为 Design Plan（v2 schema）。"确定性"意味着：相同输入 JSON 永远产生相同输出 Design Plan，不依赖 LLM 推理、不依赖随机性。
>
> **输入**：`{sample_id}.json`（建模历史，含 metadata / timeline / entities / properties）
> **输出**：`{sample_id}.design_plan.json`（v2 Design Plan）
>
> **设计依据**：本报告基于 (a) sanity set 前 5 个样本的手写 Design Plan 实践，(b) `doc/03_DesignPlan_schema_v1评审与v2改进.md` 的 v2 schema，(c) `doc/01_Sanity50_建模序列结构分析.md` 的序列结构统计。

---

## 1. Compiler 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│  输入: modeling_history.json                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  Stage 1: 解析与归一化               │
        │  - 加载 JSON, 建立 entity_id → ent   │
        │  - 按 timeline 顺序遍历              │
        │  - 数值清洗 (浮点噪声 → 0)           │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  Stage 2: 操作序列分类               │
        │  - 识别 Sketch / Extrude / 其他     │
        │  - 构建 sketch → profile → extrude  │
        │    的依赖图                          │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  Stage 3: 几何特征提取               │
        │  - 从 sketch 提取 profile 形状       │
        │  - 从 extrude 提取拉伸参数           │
        │  - 计算设计尺寸 (含欠约束回填)       │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  Stage 4: 工程语义抽象               │
        │  - 识别 primitive_type               │
        │  - 识别 part_category                │
        │  - 生成 constraints                  │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  Stage 5: 验证意图生成               │
        │  - 从 design_envelope 生成 bbox 查询│
        │  - 从 body_count 生成拓扑查询        │
        │  - 标注 non_verifiable 项            │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  Stage 6: 输出 v2 Design Plan JSON   │
        └─────────────────────────────────────┘
```

每个 stage 都是**纯函数**（无副作用、无随机），保证确定性。

---

## 2. 各 Stage 详细设计

### Stage 1: 解析与归一化

**目标**：把原始 JSON 转成内部中间表示 (IR)，清洗浮点噪声。

**关键操作**：

1. **建立 entity 索引**：`entities` 是 dict[UUID→entity]，建立 `id → entity` 映射。
2. **timeline 排序**：`timeline` 已按 `index` 排序，直接遍历。
3. **浮点清洗**：把接近 0 的噪声归零。
   - 规则：`if abs(v) < 1e-10: v = 0.0`（处理样本 5 的 `9.590720814060841e-32`）
   - 规则：`if abs(v - round(v)) < 1e-6: v = round(v)`（处理 `1.9000000000000001`）
4. **单位标记**：JSON 内部单位是 cm（properties 中的 bbox/volume/area），但 sketch 点坐标和 extrude distance 也是 cm。Design Plan 统一用 mm，所以本 stage 记录 `unit_scale = 10.0`（cm→mm）。

**样本证据**：
- 样本 1 的 sketch normal `(0.0, 1.0, 0.0)` 是干净的
- 样本 5 的 sketch normal `(9.59e-32, 1.0, -3.26e-16)` 需要清洗为 `(0, 1, 0)`

### Stage 2: 操作序列分类与依赖图构建

**目标**：识别每个 entity 的类型，建立 `sketch → profile → extrude → body` 的依赖图。

**规则**：

```
for entity in timeline (按 index 顺序):
    if entity.type == "Sketch":
        注册 sketch_node, 提取其 profiles
    elif entity.type == "ExtrudeFeature":
        对每个 input profile:
            找到对应 sketch_node
            建立 edge: sketch_node → extrude_node
        提取 extrude 产出的 bodies
    else:
        记录为 unsupported_operation (Revolve, Fillet, etc.)
```

**输出**：DAG，节点 = {sketch, extrude, body}，边 = 依赖关系。

**样本证据**：前 5 个样本都是 `1 sketch + 1 extrude + 1 body` 的最简单 DAG。但 compiler 必须为更复杂情况（多 sketch、多 extrude、boolean 操作）预留扩展。

### Stage 3: 几何特征提取（核心 Stage）

**目标**：从 sketch + extrude 提取 Design Plan 的 `solid_bodies[].dimensions` 和 `primitive_type`。

#### 3.1 Profile 形状识别

对每个 sketch 的 profile，识别其轮廓类型：

| Profile 特征 | primitive_type | 提取逻辑 |
|---|---|---|
| 4 条 SketchLine，闭合，相邻边正交 | `rectangular_prism` | 取 4 个顶点的 X/Y span 作为长宽 |
| N 条 SketchLine（N>4），闭合 | `polygonal_prism` | 取顶点 span + 边数 |
| 含 SketchCircle，单环 | `cylinder` | 取 circle.radius 和 center |
| 含 SketchArc | `extruded_profile_with_arcs` | 标记为复杂，需人工或 LLM 辅助 |

**矩形识别算法**（最常见情况）：

```python
def is_orthogonal_rectangle(curves, points):
    if len(curves) != 4: return False
    if not all(c.type == "SketchLine" for c in curves): return False
    # 收集 4 条边的方向向量
    dirs = [edge_direction(c, points) for c in curves]
    # 检查：4 条边恰好分成 2 组平行方向，且两组互相垂直
    unique_dirs = dedupe_by_parallel(dirs, tol=1e-6)
    if len(unique_dirs) != 2: return False
    if abs(abs(dot(unique_dirs[0], unique_dirs[1])) - 0.0) > 1e-6: return False
    return True
```

#### 3.2 设计尺寸提取（含欠约束回填）

**关键挑战**：不能只读 `dimensions` 字段，因为可能欠约束（样本 5 只有 1 个 dimension）。

**策略：双源融合 + 优先级**

```
对矩形的两个方向 (u_dir, v_dir):
    dim_u = lookup_explicit_dimension(sketch, orientation="Horizontal")
    dim_v = lookup_explicit_dimension(sketch, orientation="Vertical")
    
    span_u = compute_point_span(points, along=u_dir)   # 从点坐标算
    span_v = compute_point_span(points, along=v_dir)
    
    # 优先用显式 dimension；若缺失或与 span 偏差大，用 span 回填
    final_u = dim_u if dim_u is not None else span_u
    final_v = dim_v if dim_v is not None else span_v
    
    if dim_u is None:
        compiler_notes["inferred_u"] = "point_span (no explicit dimension)"
```

**样本证据**：
- 样本 1-4：都有 2 个显式 dimension，与 point span 一致 → 直接用 dimension
- 样本 5：只有 1 个显式 dimension（9.525），另一个（57.15）必须从 point span 回填，并在 `compiler_notes` 标注 `inferred_from: "point_span"`

#### 3.3 拉伸参数提取

```
extrude_distance = extrude.extent_one.distance.value   # cm → mm
taper_angle = extrude.extent_one.taper_angle.value
extent_type = extrude.extent_type                       # OneSide / TwoSides
operation = extrude.operation                           # NewBody / Join / Cut / Intersect
```

**注意**：`extent_type == TwoSideFeatureExtentType` 时要读 `extent_two`，compiler 必须处理两种情况。

#### 3.4 坐标系 frame 提取

```
sketch_plane = sketch.reference_plane.plane
frame = {
    "u_dir": clean(sketch_plane.u_direction),
    "v_dir": clean(sketch_plane.v_direction),
    "w_dir": clean(sketch_plane.normal),       # = u × v
    "origin": "bbox_min_corner"                # 归一化，不用世界坐标
}
```

### Stage 4: 工程语义抽象

**目标**：从几何特征推断 `part_category` 和 `constraints`。

#### 4.1 part_category 推断（规则表）

| 几何特征 | part_category |
|---|---|
| rectangular_prism, 长宽比 > 5, 厚度小 | `flat_plate_or_strip` |
| rectangular_prism, 两边相等，第三边显著长 | `square_strut` |
| rectangular_prism, 三边接近 | `block` |
| cylinder, length > 2×radius | `cylindrical_strut` |
| cylinder, length < 0.5×radius | `disk` |

**注意**：`part_category` 是 `non_verifiable` 的辅助字段，用于人类理解，不影响 KQP。compiler 用规则表推断，失败时填 `"uncategorized"`。

#### 4.2 constraints 生成

对每个 body，自动生成"边正交性"约束：

```json
{
  "type": "orthogonal_adjacent_edges",
  "subject": "body_0",
  "expected": "edges fall into 3 mutually-orthogonal direction groups",
  "verifiable_via": "edge_direction_dot_product"
}
```

**约束来源映射**：

| Fusion360 约束类型 | Design Plan constraint |
|---|---|
| HorizontalConstraint + VerticalConstraint | `orthogonal_adjacent_edges` |
| CoincidentConstraint | （几何上自动满足，不生成独立 constraint） |
| SymmetryConstraint | `symmetry`（待 v2 扩展） |
| TangentConstraint | `tangent`（待 v2 扩展） |

### Stage 5: 验证意图生成

**目标**：从 `solid_bodies` 和 `design_envelope` 自动生成 `validation_intents`。

**规则表**（每个 intent 对应一个 KQP 查询类型）：

| intent | 生成条件 | expected 来源 |
|---|---|---|
| `body_count` | 总是 | `len(solid_bodies)` |
| `bbox_size` | 每个 axis | `design_envelope.along_{x,y,z}.value` |
| `all_faces_planar` | 当所有 surface_type == Plane | `true` |
| `is_solid` | 总是 | `true`（若 operation == NewBody） |
| `occt_is_valid` | 总是 | `true` |

**不生成的 intent**（避免 Non-Leakage 违规）：
- `face_count` / `edge_count` / `vertex_count`：这些是 GT 泄露
- `volume` / `surface_area`：这些是几何后果，非设计需求
- `center_of_mass`：装配上下文相关

### Stage 6: 输出

组装 v2 Design Plan JSON，写入 `DesignPlan/samples/{sample_id}.design_plan.json`。

---

## 3. 关键设计决策与权衡

### 3.1 为什么用规则表而非 LLM？

| 方案 | 确定性 | 可解释性 | 覆盖率 | 维护成本 |
|---|---|---|---|---|
| 纯规则表（本方案） | ✅ 100% | ✅ 高 | ❌ 中（复杂特征失败） | 中 |
| LLM 生成 | ❌ 低 | ❌ 低 | ✅ 高 | 低 |
| 规则表 + LLM 兜底 | ⚠️ 中 | ⚠️ 中 | ✅ 高 | 中 |

**选择纯规则表**：用户明确要求"确定性 compiler"。LLM 兜底留作未来扩展，但默认关闭。复杂特征（如含 SketchArc 的 profile）compiler 输出 `primitive_type: "unsupported"` 并标记 `compiler_notes.requires_manual_review = true`。

### 3.2 欠约束样本如何处理？

**策略**：永远不报错，永远回填，永远标注。

```
if 显式 dimension 覆盖所有方向:
    用 dimension, notes 标注 "fully_constrained"
elif 部分覆盖:
    缺失方向用 point_span 回填, notes 标注 "inferred_from_point_span"
else (全无 dimension):
    全部用 point_span, notes 标注 "geometry_only_no_driving_dims"
```

**样本 5 证据**：只有 `d1_18=9.525`（Horizontal），缺 Vertical。compiler 用点坐标 span 算出 57.15，在 `compiler_notes` 写：
```json
"inferred_dimensions": {
  "along_v": {"value": 57.15, "source": "point_span", "explicit_dimension_missing": true}
}
```

### 3.3 world 坐标如何处理？

**策略**：全部丢弃，归入 `non_verifiable.world_pose`。

**理由**：Fusion360 的世界坐标是装配上下文，同一零件在不同装配中坐标不同。Design Plan 描述的是零件本身的设计，不是它在装配中的位置。KQP 验证的是 STEP 文件的几何，STEP 文件可以平移而不改变设计意图。

### 3.4 tolerance 如何确定？

**规则**：
- 默认 tolerance = `max(0.01, abs(value) * 1e-4)`（绝对 0.01mm 或相对 0.01%，取大）
- 薄板厚度方向：tolerance = `max(0.005, abs(value) * 1e-3)`
- 拉伸距离：tolerance = `max(0.01, abs(value) * 1e-4)`

**理由**：Fusion360 ModelParameter 的默认精度是 1e-6 mm，但实际建模误差在 0.01mm 量级。薄板厚度对误差更敏感（厚度本身可能只有 0.15mm），用更紧的 tolerance。

---

## 4. 实现路线图

### Phase 1: MVP（覆盖前 5 个样本，纯矩形棱柱）

**输入**：single sketch + single extrude，profile 是正交矩形
**输出**：v2 Design Plan，含 `solid_bodies[1]` + `design_envelope` + 基础 `validation_intents`

**实现工作量**：约 300 行 Python，核心是 Stage 3.1（矩形识别）和 3.2（尺寸提取）。

**验证标准**：对前 5 个样本，compiler 输出与手写 Design Plan（`DesignPlan/samples/`）逐字段一致。

### Phase 2: 扩展（覆盖 sanity set 50 样本）

**新增**：
- 多 sketch + 多 extrude 的 DAG 处理
- 圆形 profile → cylinder
- L 形 / 多边形 profile
- TwoSide 拉伸
- Join / Cut / Intersect 布尔操作

**实现工作量**：约 800 行，需扩展 Stage 3.1 的形状识别规则表。

### Phase 3: 全量（覆盖 8625 序列）

**新增**：
- RevolveFeature
- FilletFeature / ChamferFeature（作为 `modifications`）
- 复杂约束（Symmetry, Tangent, Concentric）
- 失败回退（标记 `requires_manual_review`）

**实现工作量**：约 2000 行，需大量规则枚举。

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 浮点噪声导致矩形识别失败 | 样本 5 的 normal 有 1e-32 噪声 | Stage 1 强制清洗（阈值 1e-10） |
| 欠约束样本漏掉尺寸 | 样本 5 只有 1 个 dimension | Stage 3.2 双源融合 + point_span 回填 |
| 复杂 profile 无法识别 | L 形、含弧 profile | 标记 `unsupported`，不报错，留人工 |
| 坐标系非标准 | 样本 5 的 frame 近似但不严格正交 | 清洗后用 u×v 重新计算 w_dir，保证正交 |
| TwoSide 拉伸距离计算错 | 双向拉伸的总长 = extent_one + extent_two | Stage 3.3 显式处理两种 extent_type |

---

## 6. 与 KQP Compiler 的接口契约

Design Plan compiler（本报告）和 KQP compiler（`doc/02_KQP_对象来源与查询映射.md`）是两个独立模块，通过 Design Plan JSON 解耦：

```
建模历史 JSON ──[DP Compiler]──> Design Plan JSON ──[KQP Compiler]──> KQP ──[OCP]──> 验证结果
                                     ↑
                                     │ 也可由 Design Agent 直接生成（不经过 DP Compiler）
                                     │
                              Design Agent（LLM）
```

**接口契约**：
1. DP Compiler 输出的 Design Plan 必须通过 v2 schema 校验
2. KQP Compiler 只读 Design Plan，不读原始建模历史 JSON
3. Design Plan 中的每个 `validation_intent` 必须能被 KQP compiler 映射到一个具体的 OCP 查询
4. `non_verifiable` 字段中的内容，KQP compiler 必须忽略（不生成查询）

**这意味着**：DP Compiler 是"建模历史 → Design Plan"的单向桥，KQP Compiler 是"Design Plan → 验证查询"的单向桥。两者可以独立迭代，只要 Design Plan schema 稳定。

---

## 7. 结论

确定性 compiler 在技术上可行，核心挑战不在算法复杂度，而在：

1. **覆盖率的诚实性**：规则表无法覆盖所有 Fusion360 操作，必须明确标注 `unsupported` 而非强行猜测。
2. **欠约束的回填**：不能假设每个尺寸都有显式 dimension，必须双源融合（dimension + point_span）。
3. **Non-Leakage 的执行**：compiler 必须主动丢弃世界坐标、精确 topology 计数、volume 等 GT 泄露信息。

建议下一步实现 Phase 1 MVP，对前 5 个样本验证 compiler 输出与手写 Design Plan 的一致性。

---

## 8. 可行性验证：用 5 个手写 v0.2 Design Plan 回测 Compiler 设计

> 本节是在实际手写 5 个 v0.2 Design Plan（归档于 `DesignPlan/samples/v2/`）之后，对上文 Stage 1–6 设计的逐项回测。每个发现都标注"原设计是否成立"和"需修订之处"。**最重要发现是 §8.2 的单位陷阱**，它同时影响 DP Compiler、KQP Compiler 和 exp01 的既有结论。

### 8.1 ✅ Stage 2（依赖图）：5 样本全部验证通过

**预期**：5 个样本都是 `1 sketch → 1 profile → 1 extrude → 1 body` 的线性 DAG。

**实测**：5/5 样本的 timeline 都是 2 个 entity（1 Sketch + 1 ExtrudeFeature），extrude 的 `profiles[0].sketch` 指向 sketch 的 UUID，`bodies` 产出 1 个 body。Stage 2 的依赖图构建逻辑（§2 Stage 2）对这 5 个样本**零修正即可工作**。

**结论**：Stage 2 设计成立。Phase 1 MVP 的 DAG 处理已就绪。

### 8.2 🚨 重大发现：单位陷阱（影响 Stage 1 + KQP + exp01）

**原 Stage 1 设计**（§2 Stage 1 第 4 项）：JSON 单位是 cm，Design Plan 用 mm，`unit_scale = 10.0`。这个结论**方向正确但论证不足**，手写样本时发现了一个我之前没意识到的陷阱。

**陷阱详情**：通过密度反推验证——

| 字段 | 样本 1 数值 | 物理验证 |
|---|---|---|
| `bbox.x` | 1.9 | STEP 读出 19.0mm，比值 10× → JSON 是 **cm** |
| `volume` | 72.2 | 1.9×1.9×20 = 72.2，与 bbox 同单位 → **cm³** |
| `density` | 0.0027 | 铝合金 2.7 g/cm³ = 0.0027 **kg/cm³**（注意是 kg 不是 g！） |
| `mass` | 0.1949 | density×volume = 0.0027×72.2 = 0.195 **kg** = 195g ✓ |

**关键**：Fusion360 JSON 的 `density` 单位是 **kg/cm³**（不是 g/cm³，不是 g/mm³），`mass` 单位是 **kg**。这是一个反直觉的混合单位制——长度用 cm，但质量用 kg。`density=0.0027` 看起来像 g/mm³，实际是 kg/cm³，两者数值恰好相同（因为 1 kg/cm³ = 1000 kg/L... 不，0.0027 kg/cm³ = 2.7 g/cm³ = 2700 kg/m³ = 铝）。

**对 Compiler 的影响**：
- Stage 1 的 `unit_scale=10.0`（cm→mm）**正确**，所有几何数值（bbox/volume/area/sketch 点/extrude distance/dimension value）都用 cm，统一 ×10 转 mm。
- **但**：`density` 和 `mass` 字段**不应进入 Design Plan**（属于 Non-Leakage 的物理属性，且单位混合易错）。Stage 5 的 `validation_intents` 不应包含 mass/density 查询。

**对 exp01 的影响**：exp01 的 `kqp_sample1.py` 把 STEP 的 mm 值 ×0.1 与 JSON 的 cm 值比较，**结论方向正确**（19mm STEP = 1.9cm JSON），但 `verification_report.md` 中"STEP 内部 mm，JSON cm"的表述需要补充"mass 单位是 kg、density 是 kg/cm³"的完整单位制说明。

**手写样本中的 bug**：我在 `DesignPlan/samples/v2/` 的 5 个文件里写了 `"unit": "mm"` 但数值仍是 JSON 原值（如 1.9、20.0）。**这是错误的**——如果 unit=mm，数值应为 19.0、200.0。正确做法二选一：
- (A) 保持 `unit: "mm"`，所有数值 ×10（1.9→19.0）→ 与 KQP 原生输出（mm）一致 ✅ 推荐
- (B) 改 `unit: "cm"`，数值不变 → 与 JSON GT 直接可比，但偏离工程惯例

**建议采用 (A)**，并在 Compiler Stage 6 强制校验：`if unit=="mm": assert all(v > 1 for v in dimensions)` 作为单位一致性 sanity check（避免再次漏 ×10）。**这是一个真实的、会反复出错的陷阱**，必须写进 compiler 的 regression test。

### 8.3 ✅ Stage 3.2（欠约束回填）：样本 5 验证通过，但需修正方向标签

**原设计**：样本 5 缺 Vertical dimension，用 point_span 回填 along_v。

**实测发现**：我手写时把回填方向标成了 `along_u`（57.15mm），但仔细看源数据——样本 5 的 sketch 在 XZ 平面，u_dir=(0,0,1) 即世界 Z。57.15mm 是沿世界 Z 的 span，而世界 Z = frame 的 u_dir。所以 `along_u=57.15 source=inferred_from_point_span` **是正确的**。

**但原报告 §3.2 的示例代码写错了方向**（写成 `along_v`）。这说明：**compiler 必须显式计算每个方向是 u 还是 v，不能凭 dimension 的 orientation 字符串（"Horizontal"/"Vertical"）猜**——因为 sketch 旋转后，"Horizontal" dimension 可能对应 frame 的任意方向。

**修正规则**（写入 Stage 3.2）：
```
对每个 explicit dimension:
    取 entity_one 和 entity_two 的世界坐标 p1, p2
    dim_direction = normalize(p2 - p1)
    if |dot(dim_direction, u_dir)| > 0.5: 该 dimension 属于 along_u
    elif |dot(dim_direction, v_dir)| > 0.5: 该 dimension 属于 along_v
    else: 标记为 ambiguous_dimension（警告）
```

**结论**：Stage 3.2 的双源融合策略成立，但方向归属必须用点积判定，不能用 orientation 字符串。

### 8.4 ✅ Stage 3.4（frame 提取）：5 样本全部验证通过

**预期**：frame 由 sketch 的 `reference_plane.plane` 的 u/v/normal 提取。

**实测**：
- 样本 1/2：u=(0,0,1), v=(1,0,0), w=normal=(0,1,0) ✓
- 样本 3：u=(1,0,0), v=(0,1,0), w=(0,0,1) ✓
- 样本 4：同样本 3 ✓
- 样本 5：u≈(0,0,1)（含 2.4e-45 噪声）, v≈(1,0,0), w≈(0,1,0) ✓（需 Stage 1 清洗）

**结论**：Stage 3.4 设计成立。样本 5 的浮点噪声（2.4e-45）证实了 Stage 1 清洗规则的必要性——而且这个噪声量级（1e-45）远小于我原设的阈值 1e-10，说明阈值 1e-10 **绰绰有余**。

### 8.5 🚨 新发现：Sketch plane origin 偏移必须显式丢弃

**原设计**：§3.3 说"world 坐标全部丢弃"。但手写样本 4 时发现一个**之前没考虑的细节**：样本 4 的 sketch plane origin 是 `(1.27, 1.27, 3.49)`，不是原点。

**陷阱**：Stage 3.4 如果直接读 `reference_plane.plane.origin` 填入 `frame.origin`，会把装配偏移泄漏进 Design Plan。我在样本 4 的 `compiler_notes.warnings` 里专门标注了这一点。

**修正**（写入 Stage 3.4）：
```
frame.origin = "bbox_min_corner"   # 字符串约定，绝不读 reference_plane.plane.origin
```
frame 只保留方向向量（u/v/w），原点固定为 part-local 约定。**reference_plane.plane.origin 是装配上下文，必须丢弃**。

**结论**：原设计的"丢弃 world 坐标"原则正确，但 Stage 3.4 需要显式列出"哪些字段算 world 坐标"——plane.origin 是隐蔽的泄漏点，容易漏。

### 8.6 ✅ Stage 4.1（part_category）：规则表需量化，已给出阈值

**原设计**：§4.1 给了模糊规则（"长宽比 > 5"）。手写时发现需要精确阈值。

**5 样本实测分类**：

| 样本 | 尺寸(mm, ×10后) | 长宽比 | 我的人工分类 |
|---|---|---|---|
| 1 | 19×19×200 | 200/19≈10.5 | square_strut |
| 2 | 19×19×130 | 130/19≈6.8 | square_strut |
| 3 | 279.4×215.9×1.59 | 279/1.59≈176 | flat_plate |
| 4 | 254×190.5×3.18 | 254/3.18≈80 | flat_plate |
| 5 | 95.25×19.05×571.5 | 571/9.5≈60 | slat |

**量化规则**（修正 §4.1，写入 Stage 4.1）：
```
sort dimensions ascending -> [d_min, d_mid, d_max]
aspect = d_max / d_min
if d_min == d_mid:                   # 两小维相等
    category = "square_strut" if aspect > 3 else "block"
elif aspect > 10 and d_min < d_mid * 0.3:   # 一维特薄
    category = "flat_plate_or_panel"
elif aspect > 10:                    # 一维特长但不特薄
    category = "rectangular_slat_or_strip"
else:
    category = "block" if aspect < 1.5 else "rectangular_prism_generic"
```

**结论**：Stage 4.1 的规则表思路成立，阈值已用 5 样本标定。但 `part_category` 不可验证，归入 `non_verifiable`（与 doc/03 §7.4 一致）。

### 8.7 🚨 新发现：CoincidentConstraint 是"几何惰性"约束，需特殊处理

**原设计**：§4.2 的约束映射表只列了 Horizontal/Vertical/Symmetry/Tangent。但样本 3/4/5 都有 `CoincidentConstraint`。

**实测**：CoincidentConstraint 在这些样本里是"把 sketch 原点(0,0,0)和矩形第一个角点重合"——这是建模时的辅助约束，对最终几何**没有影响**（矩形角点本来就在那里）。我在样本 3 的 `compiler_notes` 标注了 `geometrically_inert`。

**修正**（写入 Stage 4.2）：
```
对 CoincidentConstraint:
    if 两个被约束点坐标已经相等 (距离 < 1e-6):
        标记 inert，不生成 Design Plan constraint
    else:
        生成 coincident_points constraint（罕见，标记警告）
```

**结论**：约束映射表需扩展 CoincidentConstraint 的"惰性检测"分支。

### 8.8 ✅ Stage 5（validation_intents）：5 样本生成的 intent 集合一致

**预期**：每个样本生成 7-8 个 intent（body_count + 3×bbox + all_planar + is_solid + occt_valid + edge_ortho）。

**实测**：5 样本的 `validation_intents` 集合**完全同构**（仅 expected 数值不同）。Stage 5 的规则表对纯棱柱**零修正可用**。

**但**（呼应 doc/03 §7.2）：`bbox_size axis:x` 用世界轴，而 dimensions 用 frame 轴。5 样本都是轴对齐 frame，所以恰好一致；旋转 frame 会出错。Stage 5 需配合 doc/03 §8 的 v0.3 修订，把 `axis:x` 改为 `frame_axis:u`。

---

## 9. 回测总结与 Compiler 设计修订清单

### 9.1 设计成立性总评

| Stage | 原设计 | 5 样本回测 | 状态 |
|---|---|---|---|
| Stage 1 解析归一化 | 浮点清洗 + unit_scale=10 | ✅ 成立，但单位论证需补充（§8.2） | ⚠️ 补强 |
| Stage 2 依赖图 | sketch→profile→extrude→body | ✅ 5/5 零修正 | ✅ 通过 |
| Stage 3.1 矩形识别 | 4 正交线 + 2 平行组 | ✅ 5/5 成立 | ✅ 通过 |
| Stage 3.2 尺寸提取 | 双源融合 + point_span 回填 | ✅ 成立，方向判定改用点积（§8.3） | ⚠️ 修正 |
| Stage 3.3 拉伸参数 | extent_one/two 处理 | ✅ 5/5 单向拉伸成立 | ✅ 通过 |
| Stage 3.4 frame 提取 | u/v/w + 清洗 | ✅ 成立，plane.origin 必须丢弃（§8.5） | ⚠️ 补强 |
| Stage 4.1 part_category | 模糊规则 | ✅ 思路成立，阈值已量化（§8.6） | ⚠️ 量化 |
| Stage 4.2 约束映射 | H/V→正交 | ✅ 成立，需加 Coincident 惰性检测（§8.7） | ⚠️ 扩展 |
| Stage 5 validation_intents | 规则表生成 | ✅ 5/5 同构，需改 frame_axis（§8.8） | ⚠️ 配合 v0.3 |

**总评**：原设计的 6 stage 架构**整体可行**，9 个子模块中 3 个零修正通过、6 个需要补强/修正。**没有推翻性的设计错误**，所有问题都是边界情况补强。Phase 1 MVP 可立即启动。

### 9.2 必须写入 Compiler 的修订项（按优先级）

| 优先级 | 修订项 | 来源 | 影响 Stage |
|---|---|---|---|
| 🔴 P0 | 单位强制校验：`if unit=="mm": assert values > 1` | §8.2 单位陷阱 | Stage 1, 6 |
| 🔴 P0 | density/mass 不进 validation_intents | §8.2 混合单位制 | Stage 5 |
| 🔴 P0 | `frame.origin` 固定 `"bbox_min_corner"`，绝不读 plane.origin | §8.5 隐蔽泄漏 | Stage 3.4 |
| 🟡 P1 | dimension 方向归属用点积判定，非 orientation 字符串 | §8.3 方向标签 | Stage 3.2 |
| 🟡 P1 | CoincidentConstraint 惰性检测（坐标已相等则跳过） | §8.7 几何惰性 | Stage 4.2 |
| 🟢 P2 | part_category 量化阈值规则表 | §8.6 分类阈值 | Stage 4.1 |
| 🟢 P2 | bbox_size intent 改用 frame_axis（配合 v0.3 schema） | §8.8 + doc/03 §7.2 | Stage 5 |

### 9.3 回测覆盖度与下一步验证

本次回测**仅覆盖最简单的 5 个样本**（全是 single sketch + single extrude + rectangular prism）。以下情况**未被验证**，是 Phase 2 的必测项：

| 未覆盖情况 | 风险 | Phase 2 验证样本来源 |
|---|---|---|
| 圆形 profile（cylinder） | 矩形识别规则不适用 | 在 sanity 50 中筛选含 SketchCircle 的样本 |
| L 形/多边形 profile | profile.type 判定逻辑 | 在 sanity 50 中筛选曲线数 >4 的样本 |
| TwoSide 拉伸 | extent_one+extent_two 求和 | 在 sanity 50 中筛选 TwoSidesFeatureExtentType |
| 多 sketch/多 extrude | DAG 多分支 | 在 sanity 50 中筛选 timeline >2 的样本 |
| Join/Cut 布尔 | operation ≠ new_body | 在 sanity 50 中筛选非 NewBodyFeatureOperation |

**建议**：Phase 1 MVP 实现后，先用 5 个已验证样本做 regression test（compiler 输出 vs 手写 v0.2 Design Plan 逐字段 diff），通过后再扩展到 sanity 50 做覆盖度统计。

### 9.4 与 doc/03 的交叉引用

本次回测发现的 schema 问题（单位、frame_axis、冗余）与 doc/03 §7-§8 的 v0.2 复审**高度重合**，证实了"手写样本是发现 schema/compiler 缺陷的最有效手段"。两个报告的修订项应同步推进：
- doc/03 §8 的 v0.3 schema 修订（删冗余、改 frame_axis）→ 影响 Compiler Stage 5/6
- 本报告 §9.2 的 compiler 修订（单位校验、方向点积）→ 不影响 schema，是 compiler 内部逻辑

两者共同构成 v0.3 的完整修订方案。
