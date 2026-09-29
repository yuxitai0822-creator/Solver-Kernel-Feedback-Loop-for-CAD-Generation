# Phase 3 — Verified Triplets

## 描述
最终 verified (Code_gt, Code_perturbed, T_ref) 三元组。  
120 个 (sid, nid) 对通过三层验收（L1 executability + L2 fidelity + L3 KQP-flip-diff），用于 M0-M3 ablation experiment。

## 三层验收

| 层 | 检查 | 通过条件 |
|---|---|---|
| **L1 (executability)** | Code_gt + Code_perturbed 都能跑 | compile ∧ execute ∧ STEP export ∧ OCCT load |
| **L2 (fidelity)** | Code_gt 与 GT history STEP 几何一致 | `CD(Code_gt.step, GT.step) < 1e-5` ∧ KQP queries all pass on Code_gt.step |
| **L3 (difference)** | Code_perturbed 与 Code_gt 几何差异符合 T_ref | KQP-flip-diff ⊇ T_ref.expected_failed_query；extras 通过 OPERATOR_NATURAL_SIDE_EFFECTS 白名单 |

## Frozen
**完全 frozen**：`_FROZEN.md` 记录 freeze_date 与三层验收规范。  
`_frozen_manifest.json` 是机器可读索引（120 entries + per-operator stats）。

## Layout

```
phase3_triplets/
├── _FROZEN.md
├── _frozen_manifest.json
├── manifest.json
└── <sid>__<neg_id>/
    ├── triplet.json                     # 三层 verification 详细记录
    ├── code_gt.py                       # GT side CadQuery (含 HISTORY_JSON 绝对路径)
    ├── code_perturbed.py                # perturbed side CadQuery
    ├── step_gt/generated.step           # 执行 code_gt 生成的 STEP
    └── step_perturbed/generated.step    # 执行 code_perturbed 生成的 STEP
```

## Downstream consumers
- `experiments/phase2b_m0m3/` —— M0-M3 ablation experiment 输入
- `dataset/m0m3_external_metrics.py` —— 外部指标 (IVR/AUC-TR/MeanNCD/MedianNCD/VPR)