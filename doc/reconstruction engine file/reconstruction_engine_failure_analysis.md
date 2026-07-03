# Reconstruction Engine Failure Analysis

> **目的**：显式记录 Reconstruction Engine v0.1 在 50 个 sanity set 上的 Phase 2 (KQP on generated STEP) 失败情况，为 Task 5 (负样本扰动实验) 建立可靠的数据基础。

---

## 1. 总览

| 指标 | 值 |
|---|---|
| Phase 1 (compile/execute/export/occt_load) | **50/50 ✅** |
| Phase 2 (KQP on generated STEP) | **44/50 (88%)** |
| 总 queries | 334 |
| 通过 queries | 326 |
| 失败 queries | 8 |
| 失败样本数 | 6 |

---

## 2. 失败样本分类（A/B/C）

| 类别 | 描述 | 样本数 | 影响 Task 5？ |
|---|---|---|---|
| **A. 编译/执行失败** | 代码生成/运行/导出/OCCT 加载失败 | 0 | — |
| **B. 几何轻微误差** | arc discretization 导致 bbox 偏差 0.1–0.5mm | 3 | 可修复后消除 |
| **C. 几何语义错误/invalid** | hole cut 失败 / fillet 非法 / occt_valid=False | 3 (+2 overlap) | 需隔离 |

---

## 3. 失败明细表

| # | sample_id | failed query | expected | actual | error | root cause | severity | action |
|---|---|---|---|---|---|---|---|---|
| 1 | 102295_86f842dd_0000 | q_bbox_u | 48.0 | 47.914 | 0.086mm | arc discretization 24段 polyline 近似 stadium 弧 | medium | **fix_now** |
| 2 | 103552_c3a389ed_0003 | q_bbox_u | 225.0 | 224.893 | 0.107mm | arc discretization (stadium+2holes, 大尺寸) | medium | **fix_now** |
| 3 | 103552_c3a389ed_0003 | q_void_count | 2 | 1 | 1 hole | cut-prism 对 stadium+2holes 的第 2 个 hole 未成功切 | high | **isolate_for_task5** |
| 4 | 104453_aba0f2d1_0002 | q_bbox_u | 600.0 | 599.572 | 0.428mm | arc discretization (stadium 大尺寸 600mm) | medium | **fix_now** |
| 5 | 102369_65e5a7e6_0003 | q_void_count | 2 | 1 | 1 hole | polygon+2holes: cut-prism 切了 1 个, 第 2 个未对准 | high | **isolate_for_task5** |
| 6 | 102369_65e5a7e6_0003 | q_occt_valid | True | False | — | polygon fillet (corner arcs) 未成功生成, 几何不合法 | high | **isolate_for_task5** |
| 7 | 107075_beb19139_0000 | q_occt_valid | True | False | — | arbitrary_closed (大角度 arcs) 退化为 polygons | high | **isolate_for_task5** |
| 8 | 107466_72cd4ce9_0002 | q_void_count | 2 | 1 | 1 hole | stadium+2holes: cut-prism 第 2 个 hole 未成功切 | high | **isolate_for_task5** |

---

## 4. 处理策略

### 4.1 Arc discretization 误差 (3 个 bbox 失败 → fix_now)

**样本**: 102295, 103552 (bbox_u), 104453

**根因**: compiler.py 中 arc 用 24 段 polyline 离散化, 对 stadium 大尺寸弧 (如 600mm 直径) 引入 0.1–0.5mm 误差, 超出 KQP tolerance (0.05–0.06mm)。

**修复方案**: 将 N_ARC 从 24 提高到 128 段。这是最小改动, 不需要重构 compiler。

**预期效果**: 128 段的弦误差 = 2 * r * sin(π/128) ≈ r * 0.049。对 r=300mm 的 stadium, 误差 ≈ 0.015mm << tolerance 0.06mm。

**影响 Task 5**: 修复后这 3 个样本的 bbox query 应通过。但 103552 还有 void_count 失败 (C 类), 修复 arc 后仍需隔离。

### 4.2 多 polygon hole 切割 (3 个 void_count 失败 → isolate_for_task5)

**样本**: 103552, 102369, 107466

**根因**: cadquery 的 `result.cut(cut_prism)` 对非圆形 inner loop (或 stadium+多 holes) 不能保证 cut-prism 对准 body 范围。第 2 个 hole 经常未成功切割。

**修复尝试**: 可尝试 (1) cut prism overshoot 从 1.5× 增到 3.0×; (2) 沿 profile normal 双向 overshoot; (3) 对每个 inner loop 单独 cut。但这些修复不稳定, 且 cadquery 的 boolean cut 对复杂几何有已知限制。

**决策**: **隔离**。这 3 个样本不纳入 Task 5 主 negative set。后续可切换 OCP BRepAlgoAPI_Cut + 手动 face 构造解决。

### 4.3 Polygon fillet / arbitrary_closed 非法 (2 个 occt_valid 失败 → isolate_for_task5)

**样本**: 102369 (polygon_with_fillets), 107075 (arbitrary_closed)

**根因**: cadquery 不能生成 corner fillet (2 arc) + multi-hole 组合; arbitrary_closed 的大角度 arcs (343°, 94°) 退化为纯 polygon face, 几何不合法。

**决策**: **隔离**。这属于 backend limitation, 需要切换更底层的 OCP BRep 构造, 不在 Task 5 前修复。

---

## 5. Clean Reconstruction Set 定义

```
Clean Reconstruction Set = { sample | reconstruction engine 生成 STEP 后, KQP 100% pass }
```

**当前 Clean Set (修复前)**: 44 个样本

**修复 arc discretization 后预期 Clean Set**: 47 个样本 (修复 3 个 bbox 失败, 但 103552 仍有 void_count 失败 → 实际 46 个)

**隔离样本 (不纳入 Task 5)**:
- 102369_65e5a7e6_0003 (polygon_with_fillets: void + occt_valid)
- 103552_c3a389ed_0003 (stadium+2holes: void_count)
- 107075_beb19139_0000 (arbitrary_closed: occt_valid)
- 107466_72cd4ce9_0002 (stadium+2holes: void_count)

**最终 Clean Set (修复后)**: 46 个样本

**Task 5 负样本生成计划**: 46 clean samples × 2-3 perturbations/sample = 92-138 negative CADs (满足 ≥100 的要求)

---

## 6. Action 汇总

| Action | 样本数 | 样本列表 |
|---|---|---|
| **fix_now** (arc discretization 24→128) | 3 | 102295, 103552(bbox only), 104453 |
| **isolate_for_task5** | 4 | 102369, 103552(void), 107075, 107466 |
| **future_backend_upgrade** | 0 (subset of isolate) | — |

---

## 7. 隔离样本详情 (不纳入 Task 5)

| sample_id | profile type | 失败原因 | 隔离理由 |
|---|---|---|---|
| 102369_65e5a7e6_0003 | polygon_with_fillets | void_count=1/2 + occt_valid=False | fillet 未生成 + hole cut 失败 |
| 103552_c3a389ed_0003 | stadium+2holes | void_count=1/2 | 第 2 个 hole cut 未对准 |
| 107075_beb19139_0000 | arbitrary_closed | occt_valid=False | 大角度 arcs 退化为 polygons |
| 107466_72cd4ce9_0002 | stadium+2holes (degenerate_two_side) | void_count=1/2 | 第 2 个 hole cut 未对准 |

---

## 8. 下一步

1. **修复 arc discretization**: `N_ARC = 24 → 128` in compiler.py, 重新跑 3 个 bbox 失败样本
2. **确认 Clean Set**: 修复后重新跑 Phase 2 KQP, 确认 Clean Set ≥ 46
3. **导出 Clean Set 清单**: 写 `Reconstruction_results/clean_reconstruction_set.json`
4. **进入 Task 5**: 基于 Clean Set 做负样本扰动
