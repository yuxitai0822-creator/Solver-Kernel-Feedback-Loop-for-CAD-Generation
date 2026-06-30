# Design Plan Schema v0.5 评审与 v0.6 改进

> **评审对象**：`DesignPlan/DesignPlan_schema05.txt`（v0.5 schema）及 `DesignPlan/samples/v5/` 下的 10 个手写样本（31–40）。
> **评审依据**：v0.5 样本暴露的遗留问题 + 新增样本 41–50 的源数据预分析。
> **评审目的**：在投入 v0.6 手写（10 个新样本，sanity set 最后 10 个）+ compiler 更新之前，把 v0.5 的缺陷修干净。

---

## 0. 评审结论速览

| 维度 | v0.5 评分 | 缺陷 |
|---|---|---|
| Sufficiency | ✅ 良好 | v0.5 已覆盖 symmetric/degenerate/arbitrary_closed；样本 41–50 无新形态缺口 |
| Non-Procedurality | ✅ 良好 | 保持 |
| Verifiability | ⚠️ 中等 | 大尺寸样本（如 2.4m 板）的 tolerance 相对/绝对混合规则不明确；多 profile body 的 span 合并仍未定义 |
| Non-Leakage | ✅ 良好 | 保持 |

**核心结论**：v0.5 经样本 31–40 验证已达较高成熟度。样本 41–50 形态保守（8 矩形 + 1 圆环 + 1 圆），无新 profile.type 缺口。v0.6 做**收尾性修补**：(1) tolerance 的相对/绝对混合规则明确化（应对大尺寸）；(2) 多 profile body span 合并定义；(3) 消除 extrude distance 双源冗余（doc/complier可行性验证-样本30-40.md §3.1 已识别）。不做大重构。

---

## 1. v0.5 已知问题回顾

来自 `doc/DesignPlan_schema_v4评审与v5改进.md` §5（v0.5 留给 v0.6 的未解决问题）+ `doc/complier可行性验证-样本30-40.md` §3.1（双源冗余）：

1. RevolveFeature（旋转体未覆盖，无样本）
2. post-extrude FilletFeature（无样本）
3. 多 body 装配关系谓词（无样本）
4. Taper 非零（无样本）
5. **extrude distance 双源冗余**（extract_extrude 与 extract_dimensions 独立计算，symmetric 易不一致）— 本轮修
6. 复杂 profile 自动 type 识别（v0.5 用 arbitrary_closed 兜底）

---

## 2. 样本 41–50 暴露的问题

### 2.1 ⚠️ 大尺寸样本的 tolerance 规则不明确

**样本 43**（`108412_8de2f9c3_0000`）：矩形板 2438.4×1219.2×12.7mm（2.4m×1.2m 板）。v0.5 的 tolerance 默认 `0.01mm` 绝对。对 2438mm 的边长，0.01mm 绝对公差 = 相对 4e-6，过于严格（浮点累积误差可能超此）。

v0.5 schema 有 `tol_kind: absolute` 但无 `relative` 选项的明确使用规则。`doc/03 §7.6` 曾提"混合规则 `effective_tol = max(absolute_tol, value*relative_tol)`"但未落实。

### 2.2 ⚠️ 双重欠约束矩形（0 dimension）

**样本 42**（`108244_329b1876_0000`）：矩形 **0 个 explicit dimension**（之前样本 5 是 1 个，样本 42 是 0 个）。两个尺寸都从 point span 反推。v0.5 的 `inferred_from_point_span` source 已支持，但 `compiler_notes.inferred_dimensions` 需明确标注"全部尺寸推断"而非"部分"。

### 2.3 ⚠️ extrude distance 双源冗余（已知）

`doc/complier可行性验证-样本30-40.md` §3.1：`extract_extrude`（产 distance_total）和 `extract_dimensions`（产 extrude_distance）独立计算 extrude 距离。v0.5 修复时两处同步了 symmetric 逻辑，但这是脆弱的——任何新 extent_type 都需两处改。

### 2.4 ⚠️ 多 profile body span 合并仍未定义

`doc/complier可行性验证-样本20-30.md` §4.2 已识别：多 profile body（如样本 27）的 `compute_spans` 只用 profile[0]，未取 union bbox。v0.5 未修。本轮样本无多 profile，但这是已知技术债。

### 2.5 ⚠️ part_category 对大板/长条的区分模糊

样本 43（2.4m×1.2m×12.7mm）是 flat_plate；样本 42（1.2m×44mm×2.6m）长宽比极端。v0.5 part_category 规则（`doc/03 §7.4`）对"长板 vs 长条"边界模糊。需明确：thickness 是最小维且 aspect>10 → flat_plate；否则 slat。

---

## 3. v0.6 改进方案

### 3.1 tolerance 混合规则明确化

```
"distance_total": {"value": ..., "tol": ..., "tol_kind": "absolute", "relative_tol": 1e-4},
```

- `tol_kind: absolute`（默认）：effective_tol = tol
- 新增 `relative_tol: 1e-4`（默认）：effective_tol = max(tol, value * relative_tol)
- KQP 验证时用 effective_tol

解决 2.1（大尺寸样本公差不过严）。

### 3.2 消除 extrude distance 双源

`extract_dimensions` 不再独立计算 extrude_distance，直接引用 `extract_extrude` 的 `distance_total`：

```
# in compile_design_plan:
extrude_block = extract_extrude(extrude_ent, properties)
dims = extract_dimensions(sketch_ent, profile_classes[0], extrude_block)  # 传 extrude_block 进去
# extract_dimensions 内部: dims["extrude_distance"] = extrude_block["distance_total"]
```

解决 2.3（双源冗余）。

### 3.3 多 profile body span 合并定义

`compute_spans` 改为取所有 profile 的 union：
```
for each profile: compute its u/v spans; track global min/max across all profiles
span_u = global_max_u - global_min_u  (union, not profile[0] only)
```

解决 2.4。

### 3.4 part_category 量化规则细化

```
sort [extrude, max_inplane, min_inplane] -> [d_min, d_mid, d_max]
aspect = d_max / d_min
if d_min == d_mid and aspect > 3: square_strut
elif aspect > 10 and d_min < d_mid * 0.3: flat_plate_or_panel   # 一维特薄
elif aspect > 10: rectangular_slat_or_strip                      # 一维特长但不特薄
elif aspect < 1.5: block
else: rectangular_prism_generic
```

解决 2.5。

### 3.5 inferred_dimensions 标注"全部 vs 部分"

`compiler_notes.inferred_dimensions` 增 `inference_mode: "none" | "partial" | "all"`：
- `none`：所有尺寸有 explicit dimension
- `partial`：部分推断（如样本 5）
- `all`：全部推断（如样本 42）

解决 2.2。

---

## 4. 四项标准复核（v0.5 vs v0.6）

| 标准 | v0.5 | v0.6 | 改进点 |
|---|---|---|---|
| Sufficiency | ✅ | ✅ | 保持（无新形态） |
| Non-Procedurality | ✅ | ✅ | 保持 |
| Verifiability | ⚠️ | ✅ | tolerance 混合规则；span 合并；双源消除 |
| Non-Leakage | ✅ | ✅ | 保持 |

---

## 5. v0.6 未解决问题（留给 v0.7）

1. RevolveFeature（仍无样本）
2. post-extrude FilletFeature（仍无样本）
3. 多 body 装配关系谓词（仍无样本）
4. Taper 非零（仍无样本）
5. 复杂 profile 自动 type 细分（arbitrary_closed 仍兜底）

**注意**：本轮是 sanity set 50 样本的最后 10 个。v0.6 后若需继续验证，需扩展数据集（sanity set 50 已耗尽）。

---

## 6. 实施计划

1. 写 `DesignPlan/DesignPlan_schema06.txt`（v0.6 模板，落实 §3 改进）
2. 用 v0.6 手写 10 个样本（41–50），归档 `DesignPlan/samples/v6/`
3. 用现有 compiler 测试 10 样本，分析缺陷，写 `doc/complier可行性验证-样本40-50.md`
4. 更新 `compiler/design_plan_compiler.py`（双源消除、span 合并、part_category 量化、inference_mode、relative_tol）
