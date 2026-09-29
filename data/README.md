# Data Layer — 子课题1

数据层是子课题1所有实验的 ground-truth 仓库。Phase 0→3 沿"原料 → 正样本 → 负样本 → 已验证三元组"线性流动，每一层都是下一层的输入。

## 数据规模速览

| Phase | 项目数 | 说明 |
|---|---:|---|
| **phase0_initial** | 50 source samples | Fusion360 历史 + STEP/OBJ/SMT/PNG 5 模态 |
| **phase1_positive** | 51 instances | DesignPlan v0.6 + KQP v0.2 + CAD IR v0.1 + ReconstructionEngine 重建 |
| **phase2_perturbation** | 138 cases | 由 50 source × 平均 2.76 operator/case 派生 |
| **phase3_triplets** | **120 verified** | 通过 L1+L2+L3 三层验收 |

## 目录结构

```
data/
├── README.md                                # 本文件
├── INDEX.json                               # 顶层 manifest 索引
│
├── phase0_initial/                          # 原始数据
│   ├── README.md
│   ├── manifest.json
│   ├── history/                             # .json modeling history
│   ├── step/                                # .step 可读本体
│   ├── obj/                                 # .obj 视效
│   ├── smt/                                 # .smt 备用 B-rep
│   └── png/                                 # .png 缩略图
│
├── phase1_positive/                         # 正样本（GT 侧）
│   ├── README.md
│   ├── manifest.json
│   ├── reconstruction/                      # ReconstructionEngine 产物
│   │   ├── code/  # generated_code.py
│   │   ├── step/  # generated.step
│   │   ├── report/  # execution_report.json
│   │   └── log/  # stdout.txt / stderr.txt
│   ├── cad_ir/                              # CAD IR v0.1
│   │   ├── schema/cad_ir_schema_v0.1.json
│   │   └── instances/
│   │       ├── manual_ir_examples/          # 手工 + LLM 写的 IR examples
│   │       ├── history2ir_clean/            # History2IR Compiler 编译自 clean history
│   │       └── history2ir_negative/         # History2IR Compiler 编译自 perturbed history
│   ├── design_plan/                         # DesignPlan v0.6
│   │   ├── schema/DesignPlan_schema06.txt
│   │   └── instances/                       # _FROZEN.md
│   └── kqp/                                 # KQP v0.2
│       ├── schema/kqp_schema_v0.2.txt
│       └── instances/
│           ├── v0.1/  # legacy
│           └── v0.2/  # current
│
├── phase2_perturbation/                     # 扰动构造（raw negatives）
│   ├── README.md
│   ├── manifest.json
│   ├── operators/                           # 17 个 operator wrapper
│   ├── artifacts/                          # <sid>/<neg_id>/{perturbed_*, perturbation_meta}
│   └── reports/                             # 派生 reports
│
└── phase3_triplets/                         # 最终 verified triplets
    ├── README.md
    ├── manifest.json
    ├── _FROZEN.md                           # 120 verified 冻结说明
    ├── _frozen_manifest.json                # 120 verified (sid, nid) 索引
    └── <sid>__<neg_id>/
        ├── triplet.json                     # 三层验证记录
        ├── code_gt.py
        ├── code_perturbed.py
        ├── step_gt/generated.step
        └── step_perturbed/generated.step
```

## Lineage 流转图

```
phase0_initial.history
    │
    ├─→ history2cq.runtime.orchestrator ─→ phase1_positive.reconstruction
    │                                                  │
    │                                                  └─ step_gt/ (CD 验证基准)
    │
    ├─→ DesignPlan.compiler ──────────────────→ phase1_positive.design_plan
    │                                                  │
    │                                                  └─→ kqp.compiler ──→ phase1_positive.kqp
    │
    └─→ History2IR.compiler ────────────────→ phase1_positive.cad_ir (clean)
                                                       │
phase2_perturbation.operators                       │
    │  ├ E1_envelope_u/v                                  │
    │  ├ E2_extrude_deep/shallow                          │
    │  ├ E3_radius_up                                     │
    │  ├ E4_void_add/remove_one                           │
    │  ├ E5_extent_type_change                            │
    │  ├ E6_inner_gt_outer / zero_*                       │
    │  └ EX1/EX2 (execution-layer)                          │
    │                                                     │
    └─→ perturbed history ─┬─→ history2cq.runtime.orchestrator ─→ phase2_perturbation.artifacts (negative STEP)
                            │
                            └─→ History2IR.compiler ─→ phase1_positive.cad_ir (negative)
                                                       │
                                                       └─→ phase3_triplets (Code_gt + Code_perturbed + T_ref)
                                                              │
                                                              └─→ experiments/phase2b_m0m3 (consumer)
```

## 谁在用这些数据

| 下游 reader | 用到的 phase |
|---|---|
| `dataset/m0m3_external_metrics.py` | phase3_triplets/_frozen_manifest.json + step_gt/step_perturbed |
| `dataset/m0m3_significance.py` | experiments/phase2b_m0m3/pilot_results.json |
| `dataset/m0m3_analysis.py` | experiments/phase2b_m0m3/pilot_results.json |
| `dataset/triplet.py::build_triplet` | phase1_positive/* (read) + phase3_triplets (write) |
| `dataset/build_triplets.py` | phase2_perturbation/artifacts (read) |
| `dataset/freeze_verified.py` | phase3_triplets/triplet.json (read) → _frozen_manifest.json |
| `p2b_m0m3_on_frozen.py` | phase3_triplets/_frozen_manifest.json |

## Frozen 约定

带 `_FROZEN.md` 的目录在未经显式解冻流程前不应被修改：
- `data/phase3_triplets/` —— 120 verified 是 M0-M3 实验输入，**绝对 frozen**
- `data/phase1_positive/design_plan/instances/` —— DesignPlan v0.6 frozen
- `data/phase1_positive/cad_ir/instances/` —— cad_ir v0.1 frozen（Phase 2A 后转 legacy）

## 旧 → 新路径映射

| 旧路径 | 新路径 |
|---|---|
| `data/sanity_set_50/` | `data/phase0_initial/{history,step,obj,smt,png}/` |
| `Reconstruction_results/` | `data/phase1_positive/reconstruction/{code,step,report,log}/` |
| `kqp/outputs/compiler_v0.1/` | `data/phase1_positive/kqp/instances/v0.1/` |
| `kqp/outputs/compiler_v0.2/` | `data/phase1_positive/kqp/instances/v0.2/` |
| `kqp/kqp_schema_v0.2.txt` | `data/phase1_positive/kqp/schema/kqp_schema_v0.2.txt` |
| `DesignPlan/compiler/instances_v6/` | `data/phase1_positive/design_plan/instances/` |
| `DesignPlan/DesignPlan_schema06.txt` | `data/phase1_positive/design_plan/schema/DesignPlan_schema06.txt` |
| `cad_ir/results/` | `data/phase1_positive/cad_ir/instances/history2ir_batches/` |
| `cad_ir/samples/manual_ir_examples/` | `data/phase1_positive/cad_ir/instances/manual_ir_examples/` |
| `cad_ir/schema/cad_ir_schema_v0.1.json` | `data/phase1_positive/cad_ir/schema/cad_ir_schema_v0.1.json` |
| `experiments/history2ir/results/clean/` | `data/phase1_positive/cad_ir/instances/history2ir_clean/` |
| `experiments/history2ir/results/negative/` | `data/phase1_positive/cad_ir/instances/history2ir_negative/` |
| `task5_negative_perturbation/perturbations/` | `data/phase2_perturbation/artifacts/` |
| `experiments/phase2b_triplets/` | `data/phase3_triplets/` |

## Not part of this data layer

- `experiments/phase2b_m0m3/pilot_results.json` —— 实验产物（不是数据资产）
- `experiments/phase2a_parse_coverage/` —— 实验诊断
- `cad_verification/` `Freecadsolver_feedback/` `Kiwisolver_feedback/` —— 运行时 verification
- `experiments/phase2b_{pilot,_full}_/M{0..3}_*/.../agent.py|runner_script.py` —— transient 实验脚本