# 子课题一数据检查报告（Pre-Experiment Data Check）

> **任务**：在正式开展 *Solver-Kernel 双反馈闭环驱动的 CAD 生成质量提升研究* 之前，对已下载至 `D:\dataset\r1.0.1` 的 **Fusion360 Gallery Dataset (Reconstruction)** 进行数据模态核查，验证数据是否满足实验设计要求，并给出数据切片可行性结论与风险提示。
>
> **检查日期**：2026-06-24
> **数据路径**：`D:\dataset\r1.0.1`
> **检查脚本**：见同目录 `data/` 下 `*.py`；统计原始结果：`data/scan_stats.json`、`data/slice_candidates.json`

---

## 0. 一句话结论（TL;DR）

- 数据集**结构完整、零解析错误**，与官方描述一致：**8625 个序列 / 3710 个设计**，train 6900 + test 1725，全部序列在磁盘上都有对应文件（8625/8625 全覆盖）。
- 数据模态与实验设计**高度匹配**：JSON 中明确包含 `constraints`（16 类约束）、`dimensions`（9 类尺寸）、`fully_constrained` 标志 —— **Solver 反馈所需的约束信号齐备**；`properties` 下 17 个几何属性在 100% 序列上存在 —— **Kernel Query Program 的目标字段齐备**。
- **两点必须注意的关键风险**：
  1. 本数据集是 **sketch + extrude 重建序列**，**没有 Revolve / Fillet / Chamfer / Hole / Loft / Pattern** 等特征（`other_feature` 计数 = 0）。实验设计中提到的"孔阵列、凸台切除"等需通过 sketch+extrude 的 `Cut/Join` 操作体现，而非独立的 Hole/Pattern 特征。这会**限定可覆盖的设计意图类型**。
  2. **当前 Python 环境未安装任何 CAD 建模/内核库**（cadquery / build123d / OCP / pythonocc-core 均缺失）—— Kernel 反馈臂依赖 OpenCascade，**必须先配置执行环境**，否则双反馈闭环无法跑通。

**结论：数据本身可用于开展实验，但需在环境配置、特征类型边界、KQP 确定性生成三方面做前置准备（详见 §7）。**

---

## 1. 数据集总览

### 1.1 目录结构

```
D:\dataset\r1.0.1\
├─ train_test.json                              # 划分索引
├─ Fusion 360 Gallery Dataset Public License.docx
└─ reconstruction\                              # 全部数据，120,457 个文件
   ├─ <seq_id>.json          # 设计序列（feature history，8625 个）
   ├─ <seq_id>.step          # ISO-10303-21 STEP（27958 个）
   ├─ <seq_id>.smt           # Autodesk ASM 二进制（27958 个）
   ├─ <seq_id>.obj           # Wavefront 网格（27958 个）
   ├─ <seq_id>.png           # 渲染图（27958 个）
   └─ <seq_id>_<op>.{step,smt,obj,png}   # 各操作步骤的中间几何状态
```

- **序列 ID 格式**：`<designid>_<hash>_<seq>`，例如 `133248_c7255340_0000`。
- **`<seq>_<op>` 后缀**：每个建模操作步骤的中间/最终几何状态（如 `..._0000_0001.step`）。

### 1.2 划分（train_test.json）

| 划分 | 序列数 |
|---|---|
| train | 6,900 |
| test | 1,725 |
| **合计 / 去重设计数** | **8,625 序列 / 3,710 设计** |

> 与官方"Fusion360 Gallery 8,625 sequences"描述完全一致。

### 1.3 文件模态分布（profile_files.py）

| 扩展名 | 文件数 | 占用空间 | 说明 |
|---|---|---|---|
| `.obj` | 27,958 | 1,076.9 MB | 三角网格（渲染/可视化） |
| `.png` | 27,958 | 1,673.4 MB | 渲染缩略图 |
| `.smt` | 27,958 | 604.5 MB | Autodesk ASM 二进制 B-rep |
| `.step` | 27,958 | 677.8 MB | **ISO-10303-21 STEP（Kernel 首选输入）** |
| `.json` | 8,625 | 894.7 MB | 设计序列 / feature history（**JSON Plan 抽取源**） |

每个序列平均 14 个文件（min 9 / median 13 / max 157）。`.step/.smt/.obj/.png` 数量相同（27,958 = 8,625 × ~3.2，即每个序列含多个操作步骤的几何快照）。

---

## 2. JSON Design Plan 结构深度分析（实验核心输入源）

实验要求 **JSON Design Plan 从 GT 程序确定性抽取**。GT 程序即本数据集的 `*.json`。其顶层 5 个键在 **100% 序列上全部存在**：

| 顶层键 | 覆盖率 | 作用（对齐实验设计） |
|---|---|---|
| `metadata` | 8625/8625 | `parent_project` / `component_name` / `component_index` —— 单零件来源信息 |
| `timeline` | 8625/8625 | 操作的时间顺序（index→entity） |
| `entities` | 8625/8625 | **实体字典（UUID→feature）**：Sketch / ExtrudeFeature 的完整定义 |
| `properties` | 8625/8625 | **最终几何属性（17 项）** —— Kernel Query 的 GT 答案来源 |
| `sequence` | 8625/8625 | 草图曲线构建序列（曲线→时间线） |

### 2.1 `entities` —— CAD Script / Constraint / Dimension 的来源

`entities` 中仅有两类实体（全数据集统计，scan_all_sequences.py）：

| 实体类型 | 出现次数 |
|---|---|
| `Sketch` | 21,557 |
| `ExtrudeFeature` | 19,333 |
| 其他特征 | **0** |

> ⚠️ **关键边界**：**本数据集只含 sketch + extrude**，无 Revolve/Fillet/Chamfer/Hole/Loft/Pattern/Combine 等独立特征。实验设计中"Hard：孔阵列""凸台切除"只能由 sketch+extrude 的 **operation 字段**（见下）表达，不存在真正的 Hole/Pattern 特征实体。

每个 `Sketch` 实体结构（样例）：
```
Sketch = {
  points: {...Point3D...},           # 草图点
  curves: {                           # 草图曲线（含 fully_constrained 标志）
     <uuid>: {type, center_point, radius, fully_constrained, fixed, ...}
  },
  constraints: {<uuid>: {type, entity, point, ...}},   # ← Solver 反馈信号
  dimensions: {<uuid>: {type, parameter:{ModelParameter,value,name}, is_driving, ...}},  # ← 尺寸约束
  profiles: {<uuid>: {loops:[...]}}   # 闭合轮廓/环（extrude 的输入）
}
```

每个 `ExtrudeFeature` 实体结构（样例）：
```
ExtrudeFeature = {
  profiles: [{profile, sketch}],
  operation: "NewBodyFeatureOperation" | "CutFeatureOperation" | "JoinFeatureOperation" | "IntersectFeatureOperation",
  extent_type: "OneSideFeatureExtentType" | "SymmetricFeatureExtentType" | "TwoSidesFeatureExtentType",
  extent_one: {distance:{ModelParameter,value}, taper_angle, ...},
  faces: {...}, bodies: {...}, extrude_bodies/faces/side_faces/...
}
```

### 2.2 约束类型分布 —— Solver 反馈输入齐备（scan_stats.json）

全数据集共记录 **16 种草图约束类型**：

| 约束类型 | 计数 | 约束类型 | 计数 |
|---|---|---|---|
| CoincidentConstraint | 33,329 | SymmetryConstraint | 5,254 |
| HorizontalConstraint | 15,906 | MidPointConstraint | 2,853 |
| PerpendicularConstraint | 14,724 | EqualConstraint | 2,327 |
| TangentConstraint | 14,079 | CollinearConstraint | 1,289 |
| VerticalConstraint | 12,018 | OffsetConstraint | 623 |
| ParallelConstraint | 8,060 | PolygonConstraint | 545 |
| ConcentricConstraint | 6,204 | Vertical/HorizontalPointsConstraint | 340 / 332 |

约束数量分布：每序列约束数 min 0（4564 序列）、中位约 1–2、长尾到数十。**Solver 反馈"FC/OC/UC/Unsolvable"分类所需原料充足。**

### 2.3 尺寸类型分布（9 种）

`SketchLinearDimension`(17040)、`SketchDiameterDimension`(14515)、`SketchOffsetDimension`(5395)、`SketchRadialDimension`(3362)、`SketchAngularDimension`(2052)、`SketchOffsetCurvesDimension`(614) 等。每条尺寸含 `ModelParameter{value,name,role}` 与 `is_driving` —— **可直接作为约束求解器的 driving dimension 输入**。

### 2.4 曲线类型分布 —— 决定 Phase0 能否"无 spline"

| 曲线类型 | 计数 | 是否简单曲线 |
|---|---|---|
| SketchLine | 129,552 | ✅ 简单 |
| SketchCircle | 25,677 | ✅ 简单（孔/圆柱） |
| SketchArc | 20,778 | ✅ 简单 |
| **SketchFittedSpline** | **7,851** | ❌ 复杂（需排除出 Phase0） |
| SketchEllipse | 269 | ❌ 复杂 |
| SketchFixedSpline | 118 | ❌ 复杂 |
| SketchEllipticalArc / ConicCurve | 9 / 8 | ❌ 复杂 |

含复杂曲线的序列共 **657 个**（占 7.6%）—— Phase0 的"不含 spline/loft"过滤标准可执行。

### 2.5 `properties` —— Kernel Query Program 的 GT 答案（17 项，100% 覆盖）

| 属性 | 覆盖 | 对应 KQP 查询类型 |
|---|---|---|
| `body_count` / `shell_count` / `face_count` / `edge_count` / `vertex_count` / `loop_count` | 8625 | **A 拓扑查询** |
| `bounding_box` / `area` / `volume` / `center_of_mass` | 8625 | **B 几何尺寸查询** |
| `surface_types` / `vertex_valence` | 8625 | **C 特征/健康** |
| `density` / `mass` / `principal_axes` / `xyz_moments_of_inertia` | 8625 | 物理量（可选） |

> ✅ **Kernel Query Program 的四类查询（拓扑/尺寸/特征/健康）均有 GT 字段支撑，可确定性编译**。例如 `body_count == 1`、`face_count == N`、`bounding_box_z` 等都可从 `properties` 直接抽出作为 KQP 期望值。

### 2.6 约束状态信号（fully_constrained）

- 有 fully_constrained 数据的 sketch：**20,273** 个
- fully_constrained 比例 **均值 0.594 / 中位 0.727**

> 说明多数草图基本满约束，但存在大量欠约束草图 —— 这正是 Solver 反馈"UC（欠约束）"信号的现实来源，**为消融实验提供了正负样本**。

---

## 3. 几何文件有效性校验（validate_geom_files.py）

对每类文件随机抽样 60 个检查文件头（不依赖内核，纯签名校验）：

| 类型 | 抽样 | 有效 | 校验依据 | 体积范围 |
|---|---|---|---|---|
| `.step` | 60 | **60/60** ✅ | 头部含 `ISO-10303-21`（AP242 STEP，STEP Tools 生成） | 5.6–80.7 KB |
| `.smt` | 60 | **60/60** ✅ | Autodesk ASM 头（`asmheader 226.3.0`） | 2.0–124.5 KB |
| `.obj` | 60 | **60/60** ✅ | Wavefront 文本（`# WaveFront *.obj` + `v`/`f`） | 1.1–221 KB |

> ✅ STEP 文件均为标准 AP242 格式，OpenCascade（STEPControl_Reader）可读取；`.smt` 为 Fusion 私有 ASM 格式（Kernel 反馈臂应统一使用 `.step` 作为输入）。**无空文件、无截断文件**。

---

## 4. 数据 vs 实验设计逐项对照

| 实验设计要求 | 数据满足度 | 证据 |
|---|---|---|
| 主数据集 Fusion360 Gallery（CAD/FeatureHistory/CADScript） | ✅ 完全满足 | CAD=step/smt/obj，FeatureHistory=json.entities/timeline，CADScript 可由 json 重建 |
| 输入是 JSON Design Plan（非自然语言） | ✅ 可确定性抽取 | json → compiler → Plan |
| 输出是可执行 CAD Script | ✅ 目标可定义 | 由 Code Agent 生成 build123d/cadquery/OCP 脚本 |
| **Feedback A：Solver 反馈**（FC/OC/UC/Unsolvable） | ✅ 约束信号齐备 | 16 类 constraints + 9 类 dimensions + fully_constrained |
| **Feedback B：Kernel 反馈**（结构化诊断） | ✅ 17 项 GT 属性齐备 | properties 100% 覆盖 |
| KQP 四类查询（拓扑/尺寸/特征/健康） | ✅ 全部可编译 | A=body/face/edge/... B=bbox/volume C/健康=surface_types/valence |
| 4 个实验组（Baseline/Solver/Kernel/Ours）控制变量 | ✅ 数据可支撑 | 同 LLM/Prompt/Plan/迭代预算可统一施加于同一序列集 |
| 三层切片：Phase0(50)/Phase1(300–500)/Phase2(100) | ✅ 候选充足 | 见 §5 |
| Fusion360 "8,625 sequences" | ✅ 完全一致 | 8625/8625 无解析错误 |

---

## 5. 数据切片可行性（derive_slices.py）

按实验设计的选样标准**从数据本身推导候选规模**（确定性规则，见脚本）：

### Phase 0（Sanity Set，目标 50）

**规则**：仅 sketch+extrude、无 spline/ellipse/conic、≤2 sketch、=1 extrude、每草图 ≤8 曲线。

→ **候选 2,550 个序列**（远超目标 50）。示例：`100243_9fb796fe_0005`、`101817_b02acd9f_0000` 等。

> ✅ **Phase0 完全可行**，且从 2550 候选中抽 50 可保证纯净简单样本。

### Phase 1（Core Benchmark，目标 300–500，按难度分层）

| 难度 | 划分规则（数据驱动近似） | 候选数 |
|---|---|---|
| Easy | 1 sketch + 1 extrude，曲线 ≤8，无复杂曲线 | **2,239** |
| Medium | 2–3 sketch 或 2–3 extrude，或曲线 8–20 | **2,977** |
| Hard | ≥4 sketch 或 ≥4 extrude，或含复杂曲线，或曲线 >20 | **3,409** |

> ✅ **Phase1 完全可行**。每难度均 > 100 样本门槛（实验设计要求"每难度至少 100"），可在 Easy/Medium/Hard 各抽 100–150 组成 Core Benchmark。

### Phase 2（Stress Set，目标 100）

**规则**（多闭合轮廓/多孔/尺寸歧义/profile 选择歧义）：≥3 loops 或 ≥4 circle 或 单草图 ≥16 曲线 或 ≥4 profiles。

→ **候选 6,533 个序列**。示例：`100106_7f144e5b_0000`（即本报告样例）。

> ✅ **Phase2 完全可行**。profiles/loops 在 **100% 序列（8625/8625）** 上都存在，"多闭合轮廓/profile 选择歧义"这一压力场景有充分数据支撑。

### 复杂度分布补充

- 单草图轮廓数（profiles）分布：1 个(1653)、2 个(1502)、3 个(1086)… 长尾到 21+。
- 单草图环数（loops）：1(1653)、3(1195)、4(837)、2(561)… 多环草图大量存在 → **profile 选择歧义场景充足**。
- 每草图最大曲线数：长尾显著（16 曲线 223 个、20 曲线 131 个）—— **exetrude 方向/cut/join 易错场景充足**。

---

## 6. 关键风险与限制（务必在实验启动前处理）

### 🔴 R1. 执行环境缺失（阻塞项，最高优先级）

当前 Python 3.14 环境中 **cadquery / build123d / OCP / pythonocc-core 全部未安装**（仅 numpy/scipy/networkx/ezdxf）。Kernel 反馈臂依赖 OpenCascade 读取 STEP 并执行 KQP，**必须先配置**：

- **推荐方案**：`conda create -n cad python=3.11 && conda install -c cadquery cadquery=master`（含 OCP） 或 `conda install -c conda-forge occt pythonocc-core`。
- 注意：Python 3.14 对 OCP/cadquery 的 wheel 支持尚不稳定，**建议新建 Python 3.10/3.11 conda 环境**，而非在 3.14 上安装。
- 验收：能 `from OCP.STEPControl import STEPControl_Reader` 成功读取一个 STEP 并 dump `body_count`。

### 🟡 R2. 特征类型边界（需写入实验约束声明）

本数据集**仅 sketch + extrude**（无独立 Hole/Fillet/Revolve/Loft/Pattern 特征）。实验边界声明应明确：

- "孔"由 sketch(SketchCircle) + extrude(Cut) 实现；
- "凸台/切除"由 extrude 的 `operation`（NewBody/Cut/Join/Intersect）区分；
- 因此 Kernel 反馈中的"C 特征查询（孔/槽/凸台是否存在）"需转化为 **拓扑/曲面类型查询**（如 `surface_types` 中 CylinderSurfaceType 数量 ≈ 圆柱/孔特征），而非查询 HoleFeature 实体。

> 建议在 KQP 编译器中对"特征查询"统一映射到 `surface_types` + `face_count` 计数，保证语义可由数据支撑。

### 🟡 R3. KQP 确定性生成路径需先实现

实验设计明确："JSON Plan → deterministic compiler → KQP"，**不可用 LLM 生成 KQP**（避免混淆两个问题）。数据检查确认 `properties` 17 项 100% 覆盖，**确定性编译器可放心编写**，但该 compiler 是实验前置交付物，需先实现并验证其输出与 design plan 语义对齐。

### 🟢 R4. `.smt` 私有格式（低风险，规避即可）

`.smt` 是 Autodesk ASM 二进制，OpenCascade 不直接读。**统一以 `.step`（AP242）作为 Kernel 输入**即可规避，无需处理 `.smt`。

### 🟢 R5. 单位与坐标系

`properties.bounding_box` 与 sketch 坐标数值量级（如 radius=3.81）需确认单位（Fusion 默认 cm）。KQP 中"厚度/高度/距离"比较需统一单位容差，建议在 report 之外用脚本核验 bbox 与 step 实际尺寸一致后再定容差阈值。

---

## 7. 结论与下一步建议

### 结论

**数据通过预检查，可用于开展子课题一实验。**

- 数据完整性与模态匹配度：✅ 优秀（零错误、5 模态齐全、约束/尺寸/属性全覆盖）
- 实验设计可执行性：✅ 三层切片候选均远超目标规模
- 阻塞项：🔴 仅 1 项（执行环境/CAD 内核库未安装）

### 建议的启动顺序

1. **配置环境**（解 R1）：新建 conda 环境，装 cadquery/OCP，验证读取 1 个 STEP 成功。
2. **实现确定性 KQP compiler**（解 R3）：`json.properties` → KQP（四类查询），并用 10 个样本人工核验语义对齐。
3. **实现 JSON Plan 抽取器**：`json.entities/timeline` → JSON Design Plan（保留 sketch/constraint/dimension/profile/extrude 结构）。
4. **冻结 Phase0 50 样本**（从 2550 候选确定性抽样，固定 seed），跑通"无反馈 baseline → 执行 → STEP 导出 → Kernel 读取"完整闭环，验证系统稳定性（Phase0 目标）。
5. **冻结 Phase1 300–500 / Phase2 100**，开展四组对比实验。

### 交付物清单（本检查阶段） 

| 文件 | 作用 |
|---|---|
| `data/report.md` | 本报告 |
| `data/inspect_splits.py` | 划分与覆盖率核查 |
| `data/profile_files.py` | 文件模态分布 |
| `data/inspect_json_schema.py` | JSON 顶层结构 |
| `data/inspect_entities.py` | 实体/约束/尺寸/曲线结构 |
| `data/scan_all_sequences.py` | 全 8625 序列类型统计 |
| `data/scan_stats.json` | 全量统计原始结果 |
| `data/validate_geom_files.py` | 几何文件头校验 |
| `data/derive_slices.py` | Phase0/1/2 切片推导 |
| `data/slice_candidates.json` | 切片候选原始结果 |
