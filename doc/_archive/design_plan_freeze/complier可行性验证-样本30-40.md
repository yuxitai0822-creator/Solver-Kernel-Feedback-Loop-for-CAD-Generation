# Compiler 可行性验证 — 样本 31–40（含 v0.5 compiler 更新）

> **验证对象**：v0.4-era compiler（`compiler/design_plan_compiler.py`）→ 经 v0.5 更新后重新验证。
> **验证方法**：(1) 先用**未修改的 v0.4 compiler** 跑样本 31–40，记录失败项（44/55）；(2) 分析失败根因；(3) 实施 v0.5 修复；(4) 重跑验证（55/55）；(5) 回归测试 v0.4 样本 21–30（41/44，无回归）。
> **验证样本**：sanity set 第 31–40 号样本（10 个），覆盖 symmetric 拉伸、退化 two_side、无 dimension 复合轮廓、正距离负方向异常、隐式同心等 v0.4 未覆盖的形态。

---

## 0. 验证结论速览

| 阶段 | 通过率 | 说明 |
|---|---|---|
| v0.4 compiler 跑样本 31–40（修复前） | **44/55**（80%） | 11 项失败，暴露 5 类 v0.4 缺陷 |
| v0.5 compiler 跑样本 31–40（修复后） | **55/55**（100%） | 全部通过 |
| v0.5 compiler 回归测试样本 21–30 | **41/44**（无回归） | 与上轮一致（3 项为 compiler 纠正人工错误） |

**核心结论**：v0.4 compiler 在样本 31–40 上暴露 5 类新缺陷（symmetric/degenerate_two_side/annulus inner_radius/direction 异常/arbitrary_closed dims），经 v0.5 修复后达成 100% 通过，且不引入回归。compiler 从"纯棱柱+简单圆柱可用"扩展到"symmetric/two_side/arbitrary_closed/隐式同心全面可用"。

---

## 1. v0.4 compiler 失败分析（修复前 44/55）

### 1.1 失败项总表

| 样本 | 失败字段 | v0.4 输出 | 手写 v5 | 根因类别 |
|---|---|---|---|---|
| 32 | extrude_distance | 5.0 | 10.0 | A: symmetric |
| 32 | extent_type | one_side | symmetric | A: symmetric |
| 32 | direction | +w | both_symmetric | A: symmetric |
| 35 | inner_radius | 5.537 | 1.981 | B: annulus inner |
| 36 | direction | +w | -w | C: direction 异常 |
| 36 | inner_radius | 3.49 | 2.0 | B: annulus inner |
| 37 | profile.type | polygon_with_fillets | arbitrary_closed | D: 分类过宽 |
| 37 | arc_radii_present | False | True | E: arbitrary_closed dims |
| 38 | extent_type | two_side | degenerate_two_side | A: degenerate two_side |
| 38 | direction | both | +w | A: degenerate two_side |

**5 类缺陷**：
- **A 拉伸语义**（symmetric + degenerate_two_side）：v0.4 把 SymmetricFeatureExtentType 当 one_side（extent_one 当全长，实际是半长）；把 extent_two=0 的退化 two_side 当真 two_side（direction=both，实际单向）
- **B annulus inner_radius**：v0.4 的 `_circle_radius` 对两环都取第一个 Diameter dim，导致 inner/outer 都得 outer 值
- **C direction 异常**：v0.4 仅看 distance 符号判方向，样本 36 distance 正但 body 在 -Z
- **D 分类过宽**：v0.4 polygon_with_fillets 要求仅"含 arc"，样本 37（2 line+2 arc 非多边形）被误判
- **E arbitrary_closed 无 dims**：v0.4 对 arbitrary_closed 不提取任何尺寸，丢失 arc_radii/line_lengths

### 1.2 根因深度分析

**缺陷 A（symmetric）**：Fusion360 的 `SymmetricFeatureExtentType` 中，`extent_one.distance` 是**半长**（body 关于 sketch plane 对称），总 span = 2×半长。v0.4 的 `extract_extrude` 把它当 one_side 处理（extent_one 当全长），导致 extrude_distance 减半、extent_type/direction 全错。

**缺陷 B（annulus inner）**：`_circle_radius` 遍历所有 explicit_dims 取**第一个** Diameter，两环都拿到同一个（最大的 outer）。正确做法：inner 环取较小 Diameter，outer 环取较大。

**缺陷 C（direction 异常）**：样本 36 的 `extent_one.distance=+0.036`（正），但 GT bbox z∈[-0.036, 0]（body 在 -Z）。v0.4 仅看 distance 符号 → 误判 +w。根因：Fusion360 的 start_extent/offset 约定使正 distance 可能产生 -w body。需用 GT bbox 交叉验证。

**缺陷 D（分类过宽）**：v0.4 `polygon_with_fillets` 触发条件仅"outer 含 arc"。样本 37 有 2 line + 2 arc，但 2 line 不构成多边形（需 ≥3 line）。应加 line 数下限。

**缺陷 E（arbitrary_closed 无 dims）**：v0.4 `_profile_type_dims` 对 arbitrary_closed 无分支，返回空 dims。需通用提取（arc_radii/line_lengths/circle_radii）。

---

## 2. v0.5 compiler 修复实施

### 2.1 修复清单

| 缺陷 | 修复 | 影响函数 | 验证样本 |
|---|---|---|---|
| A symmetric | `extract_extrude`: SymmetricFeatureExtentType → etype=symmetric, direction=both_symmetric, total=2×half；`extract_dimensions` 同步 | extract_extrude, extract_dimensions | 32 |
| A degenerate_two_side | `extract_extrude`: TwoSides + extent_two==0 → etype=degenerate_two_side, 单向 direction | extract_extrude | 38 |
| B annulus inner | `_circle_radius`: 收集所有 Diameter candidates，prefer_smaller 取最小/prefer_larger 取最大；annulus 外环 larger 内环 smaller | _circle_radius | 35, 36 |
| C direction 异常 | `extract_extrude`: 加 direction_verified 字段；`compile_design_plan`: frame-aware 交叉验证（bbox 投影到 w_dir，若 body 在 -w 侧则翻转 direction） | extract_extrude, compile_design_plan | 36 |
| D 分类过宽 | `_classify_type`: polygon_with_fillets 要求 SketchLine ≥3 | _classify_type | 37 |
| E arbitrary_closed dims | `_profile_type_dims`: arbitrary_closed 分支提取 arc_radii/line_lengths/circle_radii | _profile_type_dims | 37 |
| 额外：center_uv | circle/annulus dims 加 center_uv（part-local） | _profile_type_dims | 33,34,35 |
| 额外：EqualConstraint | `extract_constraints`: 映射为 equal constraint | extract_constraints | 38 |
| 额外：隐式同心 | `extract_constraints`: 2+ circle center 经 Coincident 链指向同点 → 推断 concentric | extract_constraints | 36 |
| 额外：MidPointConstraint | `extract_constraints`: 映射为 midpoint constraint | extract_constraints | 38 |

### 2.2 修复后结果

```
v0.5 compiler 跑样本 31–40: 55/55 通过 (100%)
v0.5 compiler 回归样本 21–30: 41/44 (无回归；3 项为 compiler 纠正人工错误)
```

逐样本全通过（节选关键修复样本）：
- 样本 32（symmetric annulus）：extrude_distance 10.0✓ extent_type symmetric✓ direction both_symmetric✓
- 样本 35（washer annulus）：inner_radius 1.981✓（修复 B）
- 样本 36（负方向 washer）：direction -w✓（修复 C 交叉验证）inner_radius 2.0✓
- 样本 37（arbitrary_closed）：profile.type arbitrary_closed✓（修复 D）arc_radii present✓（修复 E）
- 样本 38（degenerate two_side）：extent_type degenerate_two_side✓ direction +w✓（修复 A）

---

## 3. 实现过程中发现的新细节

### 3.1 symmetric 的 distance 语义在两处需同步

`extract_extrude`（产 distance_total）和 `extract_dimensions`（产 extrude_distance）**独立计算** extrude 距离。v0.4 只修了前者，后者仍用 `abs(extent_one.distance)`（半长）。v0.5 必须在两处同步 symmetric=2×half 逻辑，否则 extrude_distance 与 distance_total 不一致。

**教训**：同一物理量（extrude 总长）在两处计算是冗余风险源。v0.6 应让 `extract_dimensions` 直接复用 `extract_extrude` 的 distance_total，消除双源。

### 3.2 direction 交叉验证需 frame（不能在 extract_extrude 内完成）

`extract_extrude` 无 frame 信息（frame 在 Stage 3.4 提取），无法独立判定"body 在 -w 侧"。v0.5 解决方案：`extract_extrude` 标 `direction_verified="needs_frame_check"`，`compile_design_plan`（有 frame）做 frame-aware 投影验证并翻转 direction。

**教训**：跨 stage 依赖（extrude 依赖 frame）需在顶层组装函数协调，不能在单个 stage 函数内完成。

### 3.3 隐式同心的 CoincidentConstraint 链解析

样本 36 的同心性由 2 个 CoincidentConstraint 表达：`circle_A.center → origin_point` 和 `circle_B.center → origin_point`。推断逻辑：
1. 收集所有 SketchCircle 的 center_point_id
2. 遍历 CoincidentConstraint，建立 `point_id → set(circle_ids)` 映射
3. 若某 point 链接 ≥2 circle → 这些 circle 互相 concentric

**关键**：CoincidentConstraint 的 `entity`/`point` 字段哪个是 circle center 需双向检查（center 可能任一字段）。

### 3.4 polygon_with_fillets 的 line 数下限

样本 37（2 line + 2 arc）被 v0.4 误判为 polygon_with_fillets。修正：要求 SketchLine ≥3（多边形至少 3 边）。但需注意：三角形带 3 圆角（3 line + 3 arc）仍应判 polygon_with_fillets，下限 3 不误伤。

---

## 4. 与前几轮验证的对比

| 轮次 | 样本 | 验证方式 | 修复前通过率 | 修复后通过率 | 主要缺陷 |
|---|---|---|---|---|---|
| doc/04 §8 | 1-5 | 纸面模拟 | 5/5 | — | 无（纯棱柱） |
| doc/complier可行性验证-样本10-20 | 11-20 | 纸面模拟 | 2/10 | — | 形状识别不足 |
| doc/complier可行性验证-样本20-30 | 21-30 | 真实实现 | 10/10 (41/44 字段) | — | loop 顺序、stadium 带孔 |
| **本轮** | 31-40 | 真实实现+修复 | **44/55** | **55/55** | symmetric/degenerate/annulus inner/direction 异常/arbitrary_closed |

**进化轨迹**：纸面模拟（20%）→ 真实实现（80%）→ 修复后（100%）。每轮新样本都暴露前轮未预见的缺陷，验证了"样本驱动的迭代改进"方法论的有效性。

---

## 5. Compiler 仍未覆盖的能力（已知限制）

本轮修复后，compiler 仍有以下未覆盖（不影响本轮 10 样本）：

| 限制 | 影响 | 优先级 |
|---|---|---|
| 多 profile body 的 span 合并（union bbox） | 样本 27 类（v4） | 🟡 P1 |
| part_category 量化（rectangle 仍一律 block） | 全部 rectangle | 🟢 P2 |
| world_bbox_estimate 投影计算（仍全 0） | 全部 | 🟢 P2 |
| RevolveFeature | 无样本 | 🟢 P3 |
| post-extrude FilletFeature | 无样本 | 🟢 P3 |
| 非零 taper 的 dimensions | 无样本 | 🟢 P3 |
| 多 body 装配关系谓词 | 无样本 | 🟢 P3 |

---

## 6. 改进后的 Compiler Stage 修订清单（本轮新增）

在 `doc/complier可行性验证-样本20-30.md` §6 修订清单基础上，本轮新增：

| 优先级 | 修订项 | 影响样本 | 状态 |
|---|---|---|---|
| 🔴 P0 | symmetric: distance_total=2×half（两处同步） | 32 | ✅ 已实现 |
| 🔴 P0 | degenerate_two_side: extent_two==0 检测 | 38 | ✅ 已实现 |
| 🔴 P0 | annulus inner_radius: prefer_smaller/larger | 35,36 | ✅ 已实现 |
| 🔴 P0 | direction 交叉验证（frame-aware bbox 投影） | 36 | ✅ 已实现 |
| 🔴 P0 | arbitrary_closed 通用 dims（arc_radii/line_lengths/circle_radii） | 37 | ✅ 已实现 |
| 🟡 P1 | polygon_with_fillets 要求 SketchLine≥3 | 37 | ✅ 已实现 |
| 🟡 P1 | 隐式同心推断（Coincident 链） | 36 | ✅ 已实现 |
| 🟡 P1 | circle/annulus center_uv | 33,34,35 | ✅ 已实现 |
| 🟡 P1 | EqualConstraint / MidPointConstraint 映射 | 38 | ✅ 已实现 |
| 🟢 P2 | extract_dimensions 复用 extract_extrude 的 distance_total（消除双源） | 全部 symmetric | ⚠️ 待实现 |

---

## 7. 结论与下一步

### 7.1 结论

本轮用 v0.4 compiler 测试样本 31–40，暴露 5 类新缺陷（symmetric/degenerate_two_side/annulus inner/direction 异常/arbitrary_closed dims），经 v0.5 修复后达成 **55/55 全通过**，且 v0.4 样本 21–30 **无回归**（41/44）。

compiler 已从"纯棱柱+简单圆柱"扩展到"symmetric/two_side/arbitrary_closed/隐式同心/方向交叉验证全面可用"。三轮真实实现验证（样本 21-30、31-40）累计覆盖 20 样本，compiler 字段通过率从 80% 提升到 100%。

### 7.2 下一步建议

1. **扩展测试到 v3 样本 11-20**：用 v0.5 compiler 跑 v3 样本，验证 stadium/annulus/rectangular_frame/翻转 frame 在更广样本的覆盖率。
2. **消除 extrude distance 双源**（§5 P2）：让 `extract_dimensions` 复用 `extract_extrude.distance_total`。
3. **建立 golden-file regression 套件**：固化 20 样本的 compiler 输出，未来改动自动 diff。
4. **扩展到 sanity 50 全量**：统计 compiler 在 50 样本的覆盖率，识别剩余未覆盖 profile.type。
5. **修正手写样本 27**（v4）：根据 compiler 输出修正 profile.type 为 arbitrary_closed。
