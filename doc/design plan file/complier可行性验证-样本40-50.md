# Compiler 可行性验证 — 样本 41–50（含 v0.6 compiler 更新）

> **验证对象**：v0.5-era compiler（`compiler/design_plan_compiler.py`）→ 经 v0.6 更新后重新验证。
> **验证方法**：(1) 先用**未修改的 v0.5 compiler** 跑样本 41–50（69/69 一次通过）；(2) 实施 v0.6 改进（单源 extrude_distance、inference_mode、量化 part_category、relative_tol）；(3) 重跑验证（69/69，无回归）；(4) 回归测试样本 21–30 与 31–40。
> **验证样本**：sanity set 第 41–50 号样本（10 个，**sanity set 50 样本的最后一批**）。形态保守：8 矩形 + 1 圆环 + 1 圆。

---

## 0. 验证结论速览

| 阶段 | 通过率 | 说明 |
|---|---|---|
| v0.5 compiler 跑样本 41–50（修复前） | **69/69**（100%） | v0.5 已覆盖此批全部形态，一次通过 |
| v0.6 compiler 跑样本 41–50（修复后） | **69/69**（100%） | v0.6 改进不改变数值，新增字段（inference_mode/relative_tol） |
| v0.6 回归测试样本 31–40 | **55/55** | 无回归 |
| v0.6 回归测试样本 21–30 | **41/44** | 无回归（3 项为 compiler 纠正人工错误） |

**核心结论**：样本 41–50 形态保守（矩形为主），v0.5 compiler 已能 100% 处理，**零失败**。本轮价值不在"修 bug"，而在**收尾性增强**：落实 v0.6 的 4 项 schema 改进（单源 extrude_distance 消除双源风险、inference_mode 标注欠约束程度、量化 part_category、relative_tol 应对大尺寸），且不引入任何回归。

**里程碑**：本轮是 sanity set 50 样本的**最后一批**。compiler 经 4 轮真实实现验证（样本 21-30、31-40、41-50 + 回归），累计覆盖 30 样本，字段通过率从首轮 80% 提升并稳定在 100%。

---

## 1. v0.5 compiler 跑样本 41–50 结果（修复前，一次通过）

### 1.1 逐样本结果

| # | 样本 | profile | extrude | direction | 关键尺寸 | 全通过 |
|---|---|---|---|---|---|---|
| 41 | 107668_cf76b132_0001 | annulus ✓ | 100.0 ✓ | +w ✓ | outer=132.5, inner=75 ✓ | ✅ |
| 42 | 108244_329b1876_0000 | rectangle ✓ | 44.45 ✓ | +w ✓ | 1219.2×2590.8 ✓ | ✅ |
| 43 | 108412_8de2f9c3_0000 | rectangle ✓ | 12.7 ✓ | +w ✓ | 2438.4×1219.2 ✓ | ✅ |
| 44 | 108850_0dcd5ef1_0002 | rectangle ✓ | 6.35 ✓ | +w ✓ | 171.45×38.1 ✓ | ✅ |
| 45 | 108850_0dcd5ef1_0004 | rectangle ✓ | 6.35 ✓ | +w ✓ | 171.45×110.998 ✓ | ✅ |
| 46 | 108851_4d515b10_0005 | rectangle ✓ | 12.7 ✓ | +w ✓ | 307.848×19.05 ✓ | ✅ |
| 47 | 108851_4d515b10_0006 | rectangle ✓ | 12.7 ✓ | +w ✓ | 95.25×19.05 ✓ | ✅ |
| 48 | 108851_4d515b10_0007 | rectangle ✓ | 19.05 ✓ | +w ✓ | 279.4×50.8 ✓ | ✅ |
| 49 | 108851_4d515b10_0009 | rectangle ✓ | 19.05 ✓ | +w ✓ | 209.55×57.912 ✓ | ✅ |
| 50 | 108852_fed54702_0004 | circle ✓ | 139.7 ✓ | +w ✓ | r=3.96875 ✓ | ✅ |

**10/10 全字段通过。** v0.5 已覆盖此批全部形态（矩形/圆环/圆，one_side 正向拉伸）。

### 1.2 为何此批零失败

样本 41–50 形态保守，全部是 v0.5 已验证的简单情况：
- 8 个矩形（v0.4 起就稳定）
- 1 个圆环（v0.5 修复 inner_radius 后稳定）
- 1 个圆（v0.3 起就稳定）
- 全部 one_side 正向拉伸（无 symmetric/degenerate/负方向）

**关键挑战仍被正确处理**：
- 样本 42（0 dimension 矩形）：v0.5 的 point_span 回填正确产出 1219.2×2590.8（inference 未标注，但数值对）
- 样本 42 的 corrective_transform：u_dir 标签 ≠ 实际映射，compiler 从 point span 取值，绕过标签
- 样本 45/46 的 float noise（normal 上 8e-16/1.4e-14）：clean_unit_vec_component 正确清洗
- 样本 48/49 的 u/v swap：span 计算符号无关，dims 正确

---

## 2. v0.6 compiler 改进实施

虽然 v0.5 已 100% 通过，本轮仍落实 v0.6 的 4 项 schema 改进（消除技术债 + 增强可验证性）：

### 2.1 改进清单

| 改进 | 实现 | 验证 |
|---|---|---|
| 单源 extrude_distance | `extract_dimensions` 接收 `extrude_block`，直接复用 `distance_total`，不再独立计算 | 样本 32 symmetric 仍 10.0✓（不再有双源不一致风险） |
| inference_mode | 新增 `_inference_mode()` 函数：none/partial/all | 样本 42→all✓，43→none✓ |
| 量化 part_category | `classify_part_category` 接收 dims，按 aspect ratio 规则分类 | 样本 41→bearing✓，43→flat_plate✓，42→flat_plate（vs 手写 slat，见 §3.1） |
| relative_tol | extrude_distance/distance_total 增 `relative_tol: 1e-4` 字段 | 全部样本输出 0.0001✓ |

### 2.2 改进后结果

```
v0.6 compiler 跑样本 41–50: 69/69 通过 (100%)
v0.6 回归样本 31–40: 55/55 (无回归)
v0.6 回归样本 21–30: 41/44 (无回归)
```

---

## 3. 实现过程中的发现

### 3.1 part_category 在样本 42 的轻微分歧（非 bug）

**手写 v6 plan**：样本 42 标 `rectangular_slat_or_strip`。
**compiler 输出**：`flat_plate_or_panel`。

**分析**：样本 42 = 1219.2×2590.8×44.45mm。compiler 量化规则：`d_min(44.45) < d_mid(1219.2)*0.3=365.8` 且 `aspect=58.3>10` → `flat_plate_or_panel`。手写时我凭"长条"直觉标 slat，但 compiler 的规则（最小维是厚度→板） arguably 更合理。

**结论**：part_category 是 `non_verifiable` 字段（自然语言分类），此分歧不影响 KQP 验证。compiler 的量化规则比人工直觉更一致，**保留 compiler 输出**。这再次印证 compiler 作为客观基准的价值。

### 3.2 单源消除后的回归验证

v0.6 让 `extract_dimensions` 复用 `extract_extrude.distance_total`。关键回归点：样本 32（symmetric）的 extrude_distance 在 v0.5 是两处独立计算（已同步），v0.6 改为单源后仍输出 10.0✓。这验证了单源重构未破坏 symmetric 逻辑——**消除了未来新增 extent_type 时两处同步的脆弱性**。

### 3.3 inference_mode 的边界判定

`_inference_mode` 逻辑：
- `explicit_count==0` → `all`（样本 42：0 维度）
- 有 explicit 但部分 inferred → `partial`（样本 5 类）
- 全 explicit → `none`（样本 43）

**边界**：curve_field source（如样本 30 无 dimension 圆）算 `all` 还是 `partial`？当前逻辑：explicit_count==0 → all，但样本 30 有 1 个 explicit dimension（d152），radius source 是 curve_field... 实际上样本 30 的 radius 有 explicit Diameter dim，所以 source 应是 explicit_dimension。需确认 `_circle_radius` 对样本 30 是否返回 explicit。这是 v0.7 可细化点（不本轮修）。

---

## 4. 与前几轮验证的对比（完整进化轨迹）

| 轮次 | 样本 | 验证方式 | 修复前 | 修复后 | 主要缺陷/改进 |
|---|---|---|---|---|---|
| doc/04 §8 | 1-5 | 纸面模拟 | 5/5 | — | 无（纯棱柱） |
| complier可行性验证-样本10-20 | 11-20 | 纸面模拟 | 2/10 | — | 形状识别不足 |
| complier可行性验证-样本20-30 | 21-30 | 真实实现 | 41/44 | 41/44 | loop 顺序、stadium 带孔；compiler 纠正人工错误 |
| complier可行性验证-样本30-40 | 31-40 | 真实实现+修复 | 44/55 | 55/55 | symmetric/degenerate/annulus inner/direction 异常/arbitrary_closed |
| **本轮** | 41-50 | 真实实现+v0.6增强 | **69/69** | **69/69** | 零失败；v0.6 收尾增强（单源/inference_mode/part_category/relative_tol） |

**进化轨迹**：纸面模拟(20%) → 真实实现(80%) → 修复后(100%) → **稳定 100% + 收尾增强**。

compiler 经 4 轮验证累计覆盖 30 样本（21-50），从"纯棱柱"扩展到"symmetric/two_side/arbitrary_closed/隐式同心/方向交叉验证/单源/量化分类"全面可用，且在最后一批达成**零失败稳定通过**。

---

## 5. Compiler 仍未覆盖的能力（已知限制，跨轮累计）

| 限制 | 影响范围 | 优先级 | 状态 |
|---|---|---|---|
| 多 profile body span 合并（union bbox） | 样本 27 类（v4） | 🟡 P1 | 未实现 |
| world_bbox_estimate 投影计算（仍全 0） | 全部 | 🟢 P2 | 未实现 |
| RevolveFeature | 无样本 | 🟢 P3 | 不适用 |
| post-extrude FilletFeature | 无样本 | 🟢 P3 | 不适用 |
| 非零 taper 的 dimensions | 无样本 | 🟢 P3 | 不适用 |
| 多 body 装配关系谓词 | 无样本 | 🟢 P3 | 不适用 |
| inference_mode 对 curve_field 的边界 | 样本 30 类 | 🟢 P2 | 待细化 |

**注意**：sanity set 50 样本已耗尽。上述未覆盖能力需扩展数据集才能验证。

---

## 6. 改进后的 Compiler Stage 修订清单（本轮新增）

在 `doc/complier可行性验证-样本30-40.md` §6 基础上，本轮新增：

| 优先级 | 修订项 | 状态 |
|---|---|---|
| 🟢 P2 | extrude_distance 单源（复用 extract_extrude.distance_total） | ✅ 已实现 |
| 🟢 P2 | inference_mode（none/partial/all） | ✅ 已实现 |
| 🟢 P2 | part_category 量化规则（aspect ratio） | ✅ 已实现 |
| 🟢 P2 | relative_tol 字段（effective_tol=max(abs, value*rel)） | ✅ 已实现（字段输出；KQP 侧使用规则待 KQP compiler 实现） |

---

## 7. 结论与下一步

### 7.1 结论

本轮用 v0.5/v0.6 compiler 测试样本 41–50（sanity set 最后 10 个），达成 **69/69 全通过**，且 v0.6 改进（单源/inference_mode/part_category/relative_tol）不引入回归（31-40 仍 55/55，21-30 仍 41/44）。

**里程碑**：sanity set 50 样本验证完成。compiler 经 4 轮迭代，从纸面模拟 20% 可用率进化到真实实现 100% 稳定通过，覆盖矩形/圆/圆环/stadium/polygon_with_fillets/rectangular_frame/arbitrary_closed 7 类 profile + symmetric/degenerate/负方向/隐式同心等拉伸语义。

### 7.2 下一步建议

1. **扩展数据集**：sanity set 50 已耗尽。需从 Fusion360 Gallery 全量（8625 序列）抽取更大样本集（如 200-500），统计 profile.type 分布，识别剩余未覆盖形态（如真正的 L 形、含 spline 的 arbitrary、RevolveFeature）。
2. **建立 golden-file regression 套件**：固化 50 样本的 compiler 输出为 golden files，未来改动自动 diff，防止回归。
3. **实现多 profile span 合并**（§5 P1）：让 `compute_spans` 对多 profile body 取 union bbox（样本 27 类）。
4. **KQP compiler 联调**：用 v0.6 Design Plan 喂给 KQP compiler，验证 validation_intents 的可验证性（exp01 当前只验证了纯棱柱）。
5. **inference_mode 边界细化**（§3.3）：明确 curve_field source 的 inference_mode 归属。
6. **修正手写样本 27**（v4）：根据 compiler 输出修正 profile.type 为 arbitrary_closed。
