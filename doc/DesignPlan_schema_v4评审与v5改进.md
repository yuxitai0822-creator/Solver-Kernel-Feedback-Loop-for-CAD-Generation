# Design Plan Schema v0.4 评审与 v0.5 改进

> **评审对象**：`DesignPlan/DesignPlan_schema04.txt`（v0.4 schema）及 `DesignPlan/samples/v4/` 下的 10 个手写样本（21–30）。
> **评审依据**：v0.4 样本暴露的遗留问题 + 新增样本 31–40 的源数据预分析（含 symmetric 拉伸、退化 two_side（extent_two=0）、无 dimension 复合轮廓、深度偏移 plane origin 等 v0.4 未充分覆盖的形态）。
> **评审目的**：在投入 v0.5 手写（10 个新样本）+ compiler 更新之前，把 v0.4 的结构性缺陷修干净。

---

## 0. 评审结论速览

| 维度 | v0.4 评分 | 致命缺陷 |
|---|---|---|
| Sufficiency | ⚠️ 中等 | symmetric 拉伸的 direction=both 丢失"对称"语义；退化 two_side（extent_two=0）未定义；复合轮廓（2 arc + 2 line 非 stadium）无 type |
| Non-Procedurality | ✅ 良好 | profiles[] 多 profile 已解耦建模顺序 |
| Verifiability | ⚠️ 中等 | 偏移 plane origin 导致的 frame.origin 约定在负拉伸+偏移组合下语义模糊 |
| Non-Leakage | ✅ 良好 | 保持 |

**核心结论**：v0.4 在拉伸语义上仍有盲区——`extent_type=symmetric` 与 `two_side`（extent_two=0 的退化情况）需要区分；复合非标准轮廓（2 arc + 2 line 但非 stadium）需新 type 或明确 arbitrary_closed 的 dimensions 表达。v0.5 做针对性修补，不做大重构。

---

## 1. v0.4 已知问题回顾

来自 `doc/DesignPlan_schema_v3评审与v4改进.md` §5（v0.4 留给 v0.5 的未解决问题）：
1. RevolveFeature（旋转体未覆盖）
2. FilletFeature 作为 post-extrude 特征
3. 多 body 装配关系谓词
4. Taper（拔模角）非零

这些 v0.5 仍不全面解决（本轮无对应样本），但本轮新增样本触及拉伸语义盲区。

---

## 2. v0.4 样本（21–30）暴露的遗留问题 + 新样本 31–40 新发现

### 2.1 ⚠️ `extent_type=symmetric` 的 direction=both 语义不足

**新样本 32**（`106323_77f22d29_0004`，bearing 2）：`extent_type=SymmetricFeatureExtentType`，`extent_one.distance=0.5`，`type=SymmetricExtentDefinition`。

v0.4 的 `direction` 枚举为 `+w | -w | both`，`both` 用于 two_side/symmetric。但 symmetric（两侧等长）与 two_side（两侧不等长）的几何含义不同：
- symmetric：拉伸体关于 sketch plane 对称（body 跨越 ±distance）
- two_side：两侧不等长（body 不对称跨越 plane）

v0.4 把两者都归为 `direction=both`，丢失了"对称性"这一设计意图。KQP 验证时，symmetric 体应满足"质心在 sketch plane 上"，two_side 不必。

### 2.2 ⚠️ 退化 two_side（extent_two=0）未定义

**新样本 38**（`107466_72cd4ce9_0002`，CrossLink）：`extent_type=TwoSidesFeatureExtentType`，但 `extent_two.distance=0`。即名义上是 two_side，实际只有一侧有拉伸（extent_one=1.0, extent_two=0），等价于 one_side 但 extent_type 标签不同。

v0.4 的 `extract_extrude` 逻辑：`if abs(e1-e2)<tol: symmetric else two_side`。此处 e1=1.0, e2=0.0，差值大→判为 two_side，direction=both，distance_total=1.0。但实际几何是 one_side（只向一侧拉伸 1.0）。**compiler 会误判 direction=both**，导致 KQP 期望 body 跨越 plane 两侧，而实际只在一侧。

### 2.3 ⚠️ 复合非标准轮廓（2 arc + 2 line 非 stadium）无 type

**新样本 37**（`107075_beb19139_0000`）：profile `f1a6425b` 有 4 曲线：1 大 arc（r=10.85, span 5.99rad≈343°）、1 小 arc（r=0.377, span 1.64rad）、2 line。这不是 stadium（两 arc 不等径、不等长、非半圆），也不是 polygon_with_fillets（line 不是多边形边）。

v0.4 无对应 type → `arbitrary_closed`。但 `arbitrary_closed` 的 dimensions 无 type-specific 提取，会丢失 2 个 arc 的 radius 和 line 长度。且此样本**无任何 dimension**（dimensions=0），所有尺寸必须从 curve 字段 + point span 推断。

### 2.4 ⚠️ 深度偏移 plane origin + 负拉伸的组合

**新样本 36**（`107055_0500fdd1_0027`，Washer (2)）：plane origin=(0,-9.53,-50.03)（深度偏移），extent_one.distance=0.036 但 GT bbox z∈[-0.036,0]（负方向拉伸）。

v0.4 的 `extract_extrude`：distance=0.036>0 → direction=+w。但 GT 显示 body 在 z∈[-0.036,0]，即沿 -w（world -Z）拉伸。**v0.4 的 direction 判定只看 distance 符号，但此处 distance 为正却实际向负方向拉伸**——可能是 start_extent 或 extent 定义的细节。这是 v0.4 direction 逻辑的盲区。

### 2.5 ⚠️ circle 的 center 偏移在 dimensions 中无表达

样本 33/34/35 的 circle center 都不在 sketch 原点（如样本 33 center=(11.43,0)）。v0.4 的 circle dimensions 只有 radius，无 center 位置。虽然 center 是装配上下文（Non-Leakage），但当 body 是多 profile 合并或需要验证"孔在某位置"时，center 相对位置是设计意图。

---

## 3. v0.5 改进方案

### 3.1 `extrude.extent_type` 增 `symmetric` 独立值 + direction 细化

```
"extrude": {
  "extent_type": "one_side | two_side | symmetric | degenerate_two_side",
  "direction": "+w | -w | both_symmetric | both_asymmetric",
  ...
}
```

- `symmetric`：SymmetricFeatureExtentType，direction=`both_symmetric`（body 关于 plane 对称）
- `degenerate_two_side`：TwoSidesFeatureExtentType 但 extent_two=0（实际 one_side），direction 按有效侧判定（+w 或 -w）
- `two_side`：两侧均非零且不等，direction=`both_asymmetric`
- `one_side`：OneSideFeatureExtentType，direction=+w/-w

**关键修正**（解决 2.2）：two_side 需检查 extent_two 是否为 0；为 0 则降级为 degenerate_two_side + 单向 direction。

### 3.2 `arbitrary_closed` 增 type-agnostic dimensions 提取规则

对 arbitrary_closed profile，提供通用 dimensions 提取：
```
"dimensions": {
  "profiles": [{
    "curve_count": <int>,
    "arc_radii": [{"value":..., "source":"curve_field"}, ...],   // 所有 arc 的 radius
    "line_lengths": [{"value":..., "source":"inferred_from_point_span"}, ...],  // 所有 line 的长度
    "circle_radii": [{"value":..., "source":"curve_field|explicit_dimension"}, ...]  // 所有 circle 的 radius
  }]
}
```

解决 2.3（复合轮廓尺寸不丢失）。这是通用兜底，不针对特定 type。

### 3.3 `direction` 判定增 start_extent / extent geometry 检查

对 distance>0 但 GT bbox 显示负方向的样本（如 36），compiler 应：
- 优先用 GT bbox 的 w 方向 span 符号判定实际拉伸方向
- 或检查 extent definition 的 geometry 字段（若存在 offset）

**简化方案**：compiler 输出 direction 后，用 GT bbox 的 min/max 在 w 轴的投影做交叉验证，若矛盾则标记 warning。

### 3.4 circle dimensions 增 `center_uv`（相对 sketch 原点）

```
"_type_circle": {
  "radius": {...},
  "center_uv": [u, v]   // 相对 sketch 原点的偏移（part-local，非世界坐标）
}
```

解决 2.5。center_uv 是 part-local（在 sketch UV 平面），不是世界坐标，符合 Non-Leakage。多 profile body 的各 circle center_uv 可表达相对位置关系。

### 3.5 `part_category` 增 `bearing` / `washer`

样本 32（bearing）、35/36（washer）是常见工程件。规则：annulus + 薄（extrude < 0.3*outer_radius）→ washer；annulus + 厚 → bearing/tube。

---

## 4. 四项标准复核（v0.4 vs v0.5）

| 标准 | v0.4 | v0.5 | 改进点 |
|---|---|---|---|
| Sufficiency | ⚠️ | ✅ | symmetric/degenerate_two_side 区分；arbitrary_closed 通用 dimensions；center_uv |
| Non-Procedurality | ✅ | ✅ | 保持 |
| Verifiability | ⚠️ | ✅ | direction 交叉验证；symmetric 可验证质心在 plane |
| Non-Leakage | ✅ | ✅ | center_uv 是 part-local |

---

## 5. v0.5 未解决问题（留给 v0.6）

1. RevolveFeature（仍无样本）
2. post-extrude FilletFeature（仍无样本）
3. 多 body 装配关系谓词
4. Taper 非零
5. 复合轮廓（如样本 37）的自动 type 识别——v0.5 用 arbitrary_closed 兜底，未来可能需细分

---

## 6. 实施计划

1. 写 `DesignPlan/DesignPlan_schema05.txt`（v0.5 模板，落实 §3 改进）
2. 用 v0.5 手写 10 个样本（31–40），归档 `DesignPlan/samples/v5/`
3. 用现有 compiler 测试 10 样本，分析缺陷，写 `doc/complier可行性验证-样本30-40.md`
4. 更新 `compiler/design_plan_compiler.py`（symmetric/degenerate_two_side、arbitrary_closed dimensions、direction 交叉验证、center_uv）
