# Compiler 可行性验证 — 样本 11–20

> **验证对象**：`doc/04_建模序列JSON到DesignPlan确定性Compiler设计.md` 提出的 6-stage 确定性 compiler 设计。
> **验证方法**：逐样本模拟 compiler 执行（Stage 1→6），判断"能否正确编译得到 `DesignPlan/samples/v3/` 下对应的手写 Design Plan"，记录失败点与改进意见。
> **验证样本**：sanity set 第 11–20 号样本（10 个），覆盖矩形棱柱、stadium、annulus、polygon_with_fillets、翻转/旋转 frame、多 sketch timeline 等 v0.2 完全未覆盖的形态。

---

## 0. 验证结论速览

| 样本 | profile 类型 | compiler 能否编译 | 失败 stage | 根因 |
|---|---|---|---|---|
| 11 | rectangle | ✅ 能 | — | doc/04 已覆盖 |
| 12 | rectangle | ✅ 能 | — | doc/04 已覆盖 |
| 13 | **stadium** | ❌ 不能 | Stage 3.1 | 矩形识别规则不适用；无 stadium 识别规则 |
| 14 | **annulus** | ❌ 不能 | Stage 2 + 3.1 | 多 sketch timeline 处理缺；annulus 识别缺 |
| 15 | **polygon_with_fillets** | ❌ 不能 | Stage 3.1 + 3.2 | 复合 profile 识别缺；多环 + 圆角尺寸提取缺 |
| 16 | annulus | ❌ 不能 | Stage 3.1 | 同 14（但单 sketch，比 14 简单） |
| 17 | annulus | ❌ 不能 | Stage 3.1 | 同 16 |
| 18 | rectangle (flipped) | ⚠️ 部分 | Stage 3.4 | u_dir/v_dir 负值清洗规则缺；construction line 过滤缺 |
| 19 | rectangle (flipped) | ⚠️ 部分 | Stage 3.4 | 同 18 |
| 20 | rectangle (rotated) | ⚠️ 部分 | Stage 3.4 | 旋转 frame 的 dimensions 提取规则缺 |

**总评**：doc/04 的 compiler 设计**只能正确编译 2/10 样本**（11、12，纯轴对齐矩形棱柱）。对 8/10 样本失败或部分失败。**这不是 doc/04 设计错误，而是 doc/04 明确声明仅覆盖 Phase 1 MVP（纯矩形棱柱）**——本次验证的价值在于：精确量化了 Phase 2 必须补的规则集，并发现了 doc/04 未预见的新陷阱。

---

## 1. 逐样本编译模拟

### 1.1 样本 11（`101817_b02acd9f_0004`，surface，rectangle 1200×600×20）✅

| Stage | 执行 | 结果 |
|---|---|---|
| 1 解析归一化 | 浮点清洗（120.0→120.0 干净）；unit_scale=10 | ✅ |
| 2 依赖图 | 1 sketch → 1 profile → 1 extrude → 1 body | ✅ |
| 3.1 矩形识别 | 4 SketchLine + 2 正交方向组 | ✅ 识别为 rectangle |
| 3.2 尺寸提取 | d90=120cm(Horizontal→u), d91=60cm(Vertical→v)；×10→1200mm/600mm | ✅ |
| 3.3 拉伸参数 | distance=2.0cm→20mm, one_side | ✅ |
| 3.4 frame | u=(0,0,1),v=(1,0,0),w=(0,1,0)；plane.origin=(0,0,0) 丢弃 | ✅ |
| 4 语义抽象 | aspect=1200/20=60>10, d_min(20)<d_mid(600)*0.3=180 → flat_plate | ✅ |
| 5 validation_intents | body_count + 3×span + all_planar + is_solid + occt_valid + edge_ortho | ✅ |
| 6 输出 | 与手写 v3 一致 | ✅ |

**结论**：compiler 完全可用。doc/04 Phase 1 设计对此样本零修正。

### 1.2 样本 12（`102175_699d5e7c_0003`，FLIP，rectangle 39×68×10）✅

同 1.1，额外验证：CoincidentConstraint 被 Stage 4.2 识别为 geometrically_inert（两被约束点坐标相等）。✅

### 1.3 样本 13（`102295_86f842dd_0000`，FBL，stadium）❌

| Stage | 执行 | 结果 |
|---|---|---|
| 1 | 清洗 OK | ✅ |
| 2 | 1 sketch → 1 profile(5 curves? 实际 profile fff68f5f: loops=1, total_curves=4) → 1 extrude | ✅ |
| 3.1 矩形识别 | **曲线含 2 SketchArc，非全 SketchLine → 矩形识别失败** | ❌ **FAIL** |
| 3.1 stadium 识别 | **doc/04 无 stadium 识别规则**（§2 Stage 3.1 只列了 rectangle/cylinder/polygon/arbitrary） | ❌ **FAIL** |

**根因**：doc/04 Stage 3.1 的形状识别规则表**没有 stadium（2 弧 + 2 直线，弧为半圆，直线平行等长）**这一项。compiler 会落入 `arbitrary_closed`，丢失 straight_length 和 radius 这两个关键设计尺寸。

**Stage 3.2 衍生问题**：即使识别为 stadium，doc/04 的"双源融合"（dimension + point_span）只针对矩形两方向。stadium 的 `straight_length`（圆心距）和 `radius` 需要新提取逻辑：
- radius ← SketchArc.radius 字段（或 Diameter Dimension ÷ 2）
- straight_length ← 两 SketchArc 的 center 坐标距离

**额外发现（关键）**：`reference_plane.u_direction=(0,0,1)=worldZ`，但 sketch 点的 x 坐标跨度 4.8cm 实际映射到 world X（GT bbox along_x=4.8cm）。**u_direction 标签与实际点→世界映射不一致**（存在 corrective_transform）。doc/04 Stage 3.4 假设"frame 由 reference_plane.plane 的 u/v/normal 提取"——这个假设在样本 13 **失效**。

**改进意见**：
- Stage 3.1 增 stadium 识别规则：`曲线数==4 && SketchArc 数==2 && SketchLine 数==2 && 两弧半径相等 && 两直线平行且长度相等 && 弧为半圆(start-end 差≈π)`
- Stage 3.2 增 stadium 尺寸提取：radius←arc.radius，straight_length←|center_a - center_b|
- Stage 3.4 增 corrective_transform 检测：若 reference_plane 含 corrective_transform 字段，frame 必须用 transform 后的方向；或一律从点坐标反推 frame（更鲁棒）

### 1.4 样本 14（`102314_91648bfc_0000`，Component1，annulus + unused sketch）❌

| Stage | 执行 | 结果 |
|---|---|---|
| 1 | OK | ✅ |
| 2 依赖图 | timeline 3 entity：Sketch1 + Extrude1 + **Sketch2（无 extrude 引用）** | ⚠️ **doc/04 未规定如何处理孤立 sketch** |
| 3.1 annulus 识别 | profile 4932856b: loops=2, total_curves=2（外圆+内圆）→ **doc/04 无 annulus 识别** | ❌ **FAIL** |

**根因 1（Stage 2）**：doc/04 Stage 2 的依赖图构建假设"每个 sketch 都被 extrude 消费"。样本 14 的 Sketch2 打破此假设。compiler 若强行把 Sketch2 也当 profile 处理，会产出错误的多 body；若忽略它，需明确规则。

**根因 2（Stage 3.1）**：doc/04 形状识别无 annulus（2 同心圆，一外一内）。compiler 会落入 arbitrary_closed，丢失 outer_radius/inner_radius。

**额外发现（Euler 异常）**：GT 报告 V=4,E=4,F=4（euler=4），但真 annulus 管拓扑 euler=0。这是 Fusion360 B-rep 表示的退化边（degenerate edge）所致。doc/04 Stage 5 若生成 `euler_characteristic` intent，expected 值无法简单推导——**annulus 的 euler 校验应标记为 non-authoritative 或跳过**。

**改进意见**：
- Stage 2 增规则：`sketch 不被任何 extrude.profiles[].sketch 引用 → 移入 auxiliary_geometry，不计入 solid_bodies`
- Stage 3.1 增 annulus 识别：`profile loops==2 && 两 loop 各含 1 SketchCircle && 两圆同心（center 距离<tol）`
- Stage 3.2 增 annulus 尺寸：outer_radius←外圆 radius，inner_radius←内圆 radius（均从 Diameter Dimension ÷ 2 或 SketchCircle.radius）
- Stage 5 增规则：annulus/tube 的 euler_characteristic intent 标 `non_authoritative: true`（因 B-rep 退化边导致 euler 不稳定）

### 1.5 样本 15（`102369_65e5a7e6_0003`，Lower Triangle，polygon_with_fillets + 2 holes）❌

| Stage | 执行 | 结果 |
|---|---|---|
| 1 | OK | ✅ |
| 2 | 1 sketch → 1 profile(loops=3, total_curves=7) → 1 extrude | ✅ |
| 3.1 识别 | profile 含 3 loop（1 外 + 2 内）+ 外 loop 含 line+arc 混合 → **doc/04 无 polygon_with_fillets 识别** | ❌ **FAIL** |
| 3.2 尺寸 | 8 dimensions 中 4 是 size（2 Diameter+2 Radial），4 是 positioning（Linear orient=None）→ **doc/04 的双源融合无法区分 size dim 和 positioning dim** | ❌ **FAIL** |

**根因 1（Stage 3.1）**：这是最复杂的 profile——外环 = 3 直线 + 2 圆弧（三角形带 2 圆角），2 内环 = 2 圆（孔）。doc/04 的形状识别完全无法处理"多环 + 混合曲线"。

**根因 2（Stage 3.2）**：8 个 dimension 里，d44-d47 是 Linear 但 `orient=None`（定位尺寸，约束孔/圆角位置，非边长）。doc/04 的双源融合规则"取 Horizontal/Vertical dimension 作为边长"在此失效——这些 positioning dim 不是边长。真正的边长（3 条边）**没有显式 dimension**，必须从点坐标距离反推。

**改进意见**：
- Stage 3.1 增 polygon_with_fillets 识别：`外环含 line+arc 混合 && arc 数≥1 && 内环（若存在）为 circle`
- Stage 3.2 增 size/positioning dimension 区分规则：
  - `dimension.orient ∈ {Horizontal, Vertical} && entity_one/entity_two 是 SketchLine 端点 → size dim（边长）`
  - `dimension.orient == None || entity_one/entity_two 是 SketchPoint（非线端点）→ positioning dim（位置）→ 转为 constraint（如 concentric），不进 dimensions`
- Stage 3.2 增多环尺寸：外环边长←点距离；圆角半径←Radial dimension 或 arc.radius；孔半径←Diameter dimension ÷ 2 或 circle.radius
- Stage 4.2 增规则：positioning dim + 共享圆心 → 生成 concentric constraint（如样本 15 的孔与圆角同心）

### 1.6 样本 16（`102410_f9877a7b_0000`，annulus，concentricity 隐式）❌

同 1.4 的 annulus 识别缺失。**额外发现**：样本 16 的同心性由 **2 个 CoincidentConstraint** 表达（两圆心都与 sketch 原点重合），而非显式 ConcentricConstraint。

**改进意见**：
- Stage 4.2 增 concentricity 推断规则：
  - `若 2+ SketchCircle 的 center 经 CoincidentConstraint 链指向同一 sketch 点 → 推断 concentric`
  - `若存在显式 ConcentricConstraint → 直接 concentric`
  - 两种编码都生成 `{"type":"concentric",...}` constraint

### 1.7 样本 17（`102410_f9877a7b_0012`，annulus，concentricity 显式）❌

同 1.6，但同心性是显式 ConcentricConstraint。验证 compiler 能否**同时处理两种编码**（16 隐式、17 显式）。doc/04 Stage 4.2 只列了"ConcentricConstraint → concentric"的显式映射，缺隐式推断。

### 1.8 样本 18（`102525_06a3094b_0000`，SOIC-8，rectangle flipped frame）⚠️

| Stage | 执行 | 结果 |
|---|---|---|
| 1 | 清洗 OK | ✅ |
| 2 | 1 sketch(6 curves) → 1 profile(4 curves) → 1 extrude | ⚠️ **sketch 有 6 curves 但 profile 只用 4（2 条是 construction 对角线）** |
| 3.1 矩形识别 | 若用 sketch 全部 6 curves → 识别失败；若只用 profile 的 4 curves → 识别成功 | ⚠️ **依赖 curve 过滤** |
| 3.4 frame | u_dir=(0,0,-1), v_dir=(-1,0,0) → **负值，doc/04 清洗规则未规定符号处理** | ⚠️ |

**根因 1（Stage 2/3.1）**：sketch 含 6 条 SketchLine（4 条构成矩形 + 2 条是对角构造线，经 CoincidentConstraint 塌缩到原点）。doc/04 Stage 3.1 假设"sketch curves 即 profile curves"，未处理"construction line 不属于 profile loop"的情况。compiler 必须从 `sketch.profiles[].loops[].profile_curves` 提取**真正构成闭环的曲线**，而非 sketch.curves 全集。

**根因 2（Stage 3.4）**：u_dir/v_dir 是负值（翻转 frame）。doc/04 Stage 1 的清洗规则只处理"接近 0 归零"和"接近整数归整"，未规定"负方向单位向量是否归一化为正"。实际上 span 计算对符号无感（max-min），所以 dimensions 不受影响——但若 compiler 试图用 u_dir 做"判断哪个轴是长边"的逻辑，负值会导致误判。建议：frame 方向向量**保留原符号**（反映真实 sketch 朝向），但所有依赖方向的计算用 abs/点积。

**改进意见**：
- Stage 2/3.1 增 curve 过滤：profile curves ← `sketch.profiles[profile_id].loops[*].profile_curves` 引用的 curve_id 集合；忽略未引用的 construction curves
- Stage 3.4 明确：frame 方向向量保留原符号（含负值）；dimensions 的方向归属用 `|dot(dim_dir, u_dir)|` 判定（绝对值，符号无关）
- Stage 1 清洗规则补充：单位向量不做符号归一化，仅做长度归一化（除以自身模长）

### 1.9 样本 19（`102525_06a3094b_0004`，SOP-28(1)，rectangle flipped）⚠️

同 1.8。**额外发现**：part_category 分类边界模糊。aspect=18/2.5=7.2，doc/04 §4.1（及 v0.3 part_category_rules）规则 `aspect>10 → flat_plate`，但 7.2 不满足。我手写时凭工程语境（IC 封装）判为 flat_plate，但规则表会判为 `rectangular_slat_or_strip` 或 `block`。

**改进意见**：
- part_category 规则增"工程语境"软规则：当 dimensions 接近已知标准件（如 IC 封装 6.5×5×1.5 系列），可标注 `part_category_confidence: low` 并保留规则表结果
- 或：part_category 完全弃用自动分类，仅作 `non_verifiable` 的人类注释字段（compiler 填 `uncategorized`，由 Design Agent 后续修正）

### 1.10 样本 20（`102525_06a3094b_0006`，SOP-28，rectangle rotated frame）⚠️

| Stage | 执行 | 结果 |
|---|---|---|
| 1 | 清洗：u_dir=(-0.0049, 0, -0.9999)——非轴对齐，doc/04 清洗规则**不能**把它归零（它不是噪声，是真实旋转） | ⚠️ **清洗阈值风险** |
| 3.4 frame | 旋转 frame，dimensions 必须用 vertex_projection | ⚠️ doc/04 未规定旋转 frame 的 dimensions 提取 |
| 5 validation | bbox_size intent 在旋转 frame 下语义模糊（v0.2 问题，v0.3 已改 span_along_frame_axis） | ⚠️ |

**根因 1（Stage 1 清洗）**：doc/04 清洗规则 `if abs(v)<1e-10: v=0`。样本 20 的 u_dir 分量 0.0049 远大于 1e-10，不会被错误归零——**这一点 doc/04 是安全的**。但需警惕：若未来遇到旋转角度极小（如 1e-11 弧度）的样本，清洗可能误伤。建议：**单位向量分量不做归零清洗**，只对坐标值清洗。

**根因 2（Stage 3.2/3.4 dimensions）**：旋转 frame 下，"沿 u 的 span"必须用顶点投影到 u_dir 计算，不能用 axis-aligned bbox。doc/04 Stage 3.2 的"point_span 回填"逻辑本质就是顶点投影，但**未明确投影到 frame 轴而非世界轴**。v0.3 schema 已强制 `span_computation=vertex_projection`，compiler 必须遵守。

**根因 3（GT bbox 异常）**：GT bbox 显示 along_x=11.3mm（=length_u），along_z=21mm（=width_v），与旋转 frame 的预期（axis-aligned bbox 应略大于 frame span）不符。推测 GT bbox 可能在 sketch-local frame 计算，或旋转角太小（0.28deg，膨胀 0.1mm）在 GT 精度内被吸收。**compiler 不应依赖 GT world bbox 验证旋转 frame**——必须用 STEP 实际几何的 vertex_projection。

**改进意见**：
- Stage 1 清洗规则细化：**坐标值**清洗（归零、归整）；**单位向量分量**仅归一化长度，不归零
- Stage 3.2 明确：所有 span 一律投影到 frame 的 u/v/w 轴（vertex_projection），禁止用 axis-aligned bbox
- Stage 5 明确：旋转 frame 样本，validation_intents 用 `span_along_frame_axis`（v0.3），不用世界轴 bbox_size

---

## 2. Compiler 设计的系统性缺陷汇总

### 2.1 Stage 3.1 形状识别规则表严重不足（影响 8/10 样本）

doc/04 Stage 3.1 仅覆盖 rectangle/cylinder/polygon/arbitrary_closed。实际需要：

| 形态 | 识别规则（需新增） | 影响样本 |
|---|---|---|
| stadium | 4 曲线（2 arc + 2 line），弧半径相等，直线平行等长，弧为半圆 | 13 |
| annulus | profile loops≥2，各 loop 单 circle，同心 | 14,16,17 |
| polygon_with_fillets | 外环 line+arc 混合，arc≥1；可选内环 circle | 15 |
| circle（实心圆柱） | profile loops==1，单 SketchCircle | （本批无，但 Phase 2 必需） |

**优先级**：🔴 P0。这是 compiler 从"2/10 可用"提升到"10/10 可用"的关键。

### 2.2 Stage 2 未处理孤立 sketch（影响 1/10，但后果严重）

样本 14 的 Sketch2 未被 extrude 消费。doc/04 Stage 2 假设 sketch 全被消费。

**改进**：Stage 2 增"孤立 sketch 检测"——遍历所有 extrude.profiles[].sketch，收集被引用的 sketch_id 集合；未引用的 sketch 移入 auxiliary_geometry。

**优先级**：🔴 P0（虽只影响 1 样本，但若不处理会导致多 body 误生成，污染下游）。

### 2.3 Stage 3.2 未区分 size dim 与 positioning dim（影响复杂 profile）

样本 15 的 8 个 dimension 中，4 个是 positioning（orient=None），不应作为边长。doc/04 双源融合规则未区分。

**改进**：Stage 3.2 增 dimension 分类：
- size dim：`orient ∈ {H,V} && entity_one/two 是 SketchLine 端点` → 边长
- positioning dim：`orient==None || entity 是 SketchPoint` → 转 constraint

**优先级**：🟡 P1。

### 2.4 Stage 3.4 frame 提取的 corrective_transform 盲区（影响 4/10）

样本 13/18/19/20 的 reference_plane.u_direction 与实际点→世界映射不一致（corrective_transform 隐含）。doc/04 Stage 3.4 直接用 u_direction 作 frame，会得到错误的 dimensions 方向归属。

**改进**：Stage 3.4 增 corrective_transform 处理：
- 优先用 reference_plane.corrective_transform（若存在）修正 u/v/w
- 或：彻底从 sketch 点坐标反推 frame（用 PCA 或边方向统计），不依赖 reference_plane 标签
- 兜底：dimensions 一律从 point_span 提取（已隐含在双源融合），frame 方向仅用于 KQP 投影

**优先级**：🔴 P0（影响 dimensions 正确性）。

### 2.5 Stage 4.2 约束映射缺隐式 concentricity 与 construction line 过滤

- 样本 16 的 concentricity 由 2 CoincidentConstraint 隐式表达，doc/04 只映射显式 ConcentricConstraint
- 样本 18 的 2 条 construction 对角线经 CoincidentConstraint 塌缩，不应生成 constraint

**改进**：
- Stage 4.2 增隐式 concentricity 推断（多 circle center 经 Coincident 链指向同点）
- Stage 4.2 增 CoincidentConstraint 惰性检测（被约束点坐标已相等 → inert，不生成）

**优先级**：🟡 P1。

### 2.6 Stage 1 清洗规则对单位向量分量需特殊处理（影响旋转 frame）

doc/04 清洗规则 `abs(v)<1e-10 → 0` 对坐标值安全，但对旋转 frame 的单位向量分量（如 0.0049）不能误清。

**改进**：Stage 1 分两类清洗：
- 坐标值（point.x/y/z, dimension.value）：归零（<1e-10）+ 归整（<1e-6）
- 单位向量分量（u_dir/v_dir/normal）：仅长度归一化，不归零

**优先级**：🟢 P2（当前阈值 1e-10 对 0.0049 安全，但需文档化防误改）。

### 2.7 Stage 5 euler_characteristic 对 annulus 不可靠（影响 annulus 样本）

样本 14 的 GT euler=4（非标准 0），因 B-rep 退化边。

**改进**：Stage 5 增规则：annulus/tube 的 euler intent 标 `non_authoritative: true` 或跳过；改用 `cylinder_face_count` + `is_solid` + `occt_is_valid` 组合验证。

**优先级**：🟡 P1。

---

## 3. doc/04 Phase 1 vs Phase 2 边界重新划定

doc/04 原划 Phase 1 = "前 5 样本纯矩形棱柱"。本次验证表明，**Phase 1 实际只覆盖 2/10 新样本**（11、12）。Phase 2 的范围需扩大：

| 原 Phase 2 项 | 本次验证后的必要项 | 优先级 |
|---|---|---|
| 圆形 profile → cylinder | ✅ 保留 | P1 |
| L 形/多边形 profile | ✅ 保留 | P1 |
| TwoSide 拉伸 | ✅ 保留 | P2 |
| Join/Cut 布尔 | ✅ 保留 | P2 |
| **stadium 识别**（新增） | 🔴 必需（样本 13） | P0 |
| **annulus 识别**（新增） | 🔴 必需（样本 14,16,17） | P0 |
| **polygon_with_fillets 识别**（新增） | 🔴 必需（样本 15） | P0 |
| **多环 profile（holes）**（新增） | 🔴 必需（样本 14,15,16,17） | P0 |
| **孤立 sketch 处理**（新增） | 🔴 必需（样本 14） | P0 |
| **corrective_transform / frame 反推**（新增） | 🔴 必需（样本 13,18,19,20） | P0 |
| **size/positioning dim 区分**（新增） | 🟡 必需（样本 15） | P1 |
| **隐式 concentricity 推断**（新增） | 🟡 必需（样本 16） | P1 |
| **construction curve 过滤**（新增） | 🟡 必需（样本 18,19,20） | P1 |

**Phase 2 工作量重估**：doc/04 原估 800 行。本次验证新增 8 项必需规则，**重估 1200-1500 行**。

---

## 4. 改进后的 Compiler Stage 修订清单（按优先级）

| 优先级 | 修订项 | 影响样本 | 影响 Stage |
|---|---|---|---|
| 🔴 P0 | Stage 3.1 增 stadium/annulus/polygon_with_fillets/circle 识别规则 | 13,14,15,16,17 | 3.1 |
| 🔴 P0 | Stage 3.1 增多环 profile 处理（outer/inner rings） | 14,15,16,17 | 3.1 |
| 🔴 P0 | Stage 2 增孤立 sketch 检测 → auxiliary_geometry | 14 | 2 |
| 🔴 P0 | Stage 3.4 增 corrective_transform 处理 / frame 反推 | 13,18,19,20 | 3.4 |
| 🔴 P0 | Stage 3.2 增曲面尺寸提取（radius/straight_length/fillet_radii/hole_radii） | 13,14,15,16,17 | 3.2 |
| 🟡 P1 | Stage 3.2 增 size/positioning dim 区分 | 15 | 3.2 |
| 🟡 P1 | Stage 4.2 增隐式 concentricity 推断 | 16 | 4.2 |
| 🟡 P1 | Stage 4.2 增 CoincidentConstraint 惰性检测（已扩展 doc/04 §8.7） | 12,15,16,17,18,19,20 | 4.2 |
| 🟡 P1 | Stage 2/3.1 增 construction curve 过滤（用 profile.loops 提取真曲线） | 18,19,20 | 2,3.1 |
| 🟡 P1 | Stage 5 annulus euler 标 non_authoritative | 14,16,17 | 5 |
| 🟢 P2 | Stage 1 单位向量分量不归零（仅长度归一化） | 20 | 1 |
| 🟢 P2 | Stage 4.1 part_category 增 confidence 字段或弃用自动分类 | 19 | 4.1 |

---

## 5. 与 doc/04 §8（前 5 样本回测）的对比

| 维度 | doc/04 §8（样本 1-5） | 本文（样本 11-20） |
|---|---|---|
| compiler 可用率 | 5/5（纯矩形棱柱） | 2/10（仅 11、12） |
| 失败主因 | 无（Phase 1 设计完备） | 形状识别规则表不足（stadium/annulus/多环） |
| 新发现的陷阱 | 单位陷阱、plane.origin 泄漏、Coincident 惰性 | corrective_transform、孤立 sketch、size/positioning dim 混淆、construction curve 过滤、annulus euler 异常 |
| Phase 边界 | Phase 1 = 5 样本 | Phase 1 实际仅 2 新样本；Phase 2 范围显著扩大 |

**核心结论**：doc/04 的 6-stage 架构**骨架正确**（Stage 1/2/5/6 稳定，Stage 3/4 需扩展），但 Stage 3.1（形状识别）和 Stage 3.2（尺寸提取）的规则表**严重不足**，是 compiler 从"纯棱柱可用"走向"通用可用"的主要瓶颈。建议下一步实现时，**优先攻克 Stage 3.1 的 stadium/annulus/polygon_with_fillets 三类识别**，这三类覆盖了本次 10 样本中 5 个失败样本，投入产出比最高。

---

## 6. 下一步建议

1. **实现 Stage 3.1 三类曲面 profile 识别**（stadium/annulus/polygon_with_fillets），用样本 13/14/15/16/17 做 regression test。
2. **实现 Stage 2 孤立 sketch 检测 + Stage 3.4 corrective_transform 处理**，用样本 14/13/20 验证。
3. **实现 Stage 3.2 size/positioning dim 区分**，用样本 15 验证。
4. 扩展 sanity set 到 30-50 样本，统计 stadium/annulus/polygon_with_fillets 的占比，确认规则表覆盖率。
5. 对 annulus 样本（14/16/17）跑 exp01 KQP，验证 `cylinder_face_count` + `surface_type_distribution` intent 的可验证性（exp01 当前只验证了纯棱柱）。
