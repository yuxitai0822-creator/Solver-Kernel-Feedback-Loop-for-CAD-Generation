# 第三部分：实验与测评层（Experiment & Evaluation Layer）

> 说明：本文件名 `03_experiment_metirc_and_doc.md` 按你的指示保留（原意应为 `03_experiment_metric_and_doc.md`，内部内容统一用「metric」正确拼写）。

## 1. 架构总览

第三层建立在数据层与模型系统层之上，是 M0-M3 消融实验与5 大外部指标的实际运行场。它由**3 个互相独立的子系统**组成：

1. **实验运行入口（runners）**：4 个 batch runner，按版本号命名（pilot_v0.2、pilot_v0.2_m0、full_v0.2、m0m3_v0.3）
2. **实验分析（analysis）**：6 个测评脚本 + chamfer（几何距离算法），平铺，< 10 个不分子目录
3. **数据生产工具（data/build_tools）**：4 个 phase3 triple 构造器，与第一层 `data/phase3_triplets/` 配套

```
data/phase3_triplets/                     ← 第一层数据资产
              ↑↑ build_triplet()
experiments/runners/                      ← 第二层 batch 入口
              ↓
experiments/analysis/                      ← 第三层评测
              ↓
experiments/REGISTRY.json                 ← 机器可读注册表
```

外加：
- **doc/** 子目录：当前 8 个 + `_archive/` 5 个过期文档
- **experiments/{frozen,results,...}/**：历史 phase 数据 + frozen v0.1/v0.2

## 2. experiments/ 顶层目录（重构后）

| 子目录/文件 | 描述 |
|---|---|
| **REGISTRY.json** | ⭐ 机器可读注册表（CGVMs/methods/analysis/experiment_phases） |
| `runners/` | 4 个 batch runner 入口 |
| `analysis/` | 6 个测评脚本 + chamfer |
| `b009_diagnosis/` | B-009 帧-only 回归诊断（frozen） |
| `pilot/` | 早期 pilot v0.x（独立老 pilot，保留原位） |
| `pilot_v0.2/` | 原 `phase2b_pilot/`（30 样本 × 4）|
| `pilot_v0.2_m0/` | 原 `phase2b_pilot_m0/`（70 样本 × M0）|
| `full_v0.2/` | 原 `phase2b_full/`（167 × 4）|
| `m0m3_v0.3/` | 原 `phase2b_m0m3/`（**CURRENT**：120 frozen × 4）|
| `history2ir_v0.1/` | 原 `experiments/history2ir/` batch 结果 + reports（仅产物）|
| `frozen/` | v0.1/v0.2 历史归档 |
| `phase2a_parse_coverage/` | phase2a v0.1 输出（独立）|
| `phase2a_sanity/` | phase2a v0.1 输出（独立）|
| `results/` | v0.1 老 trial artifact |
| `results_v0.2/` | v0.2 老 trial artifact |
| `reports/` | 跨 phase 汇总报告 |
| `config/` | benchmark 配置 |
| `schema/` | run_result schema |
| `bugs/` | bug DB |

## 3. experiments/runners/（4 个 runner，统一入口）

| 文件 | 来源（旧名）| 描述 |
|---|---|---|
| `iter_runner.py` | 原 `p2b_iter_runner.py` | 480 trial batch runner（120 frozen × 4）|
| `kqp_rerun.py` | 原 `p2b_kqp_rerun_v2.py` | KQP v0.2 重跑 |
| `final_analysis.py` | 原 `p2b_final_analysis.py` | McNemar + per-(method, layer) 失败率汇总 |
| `benchmark_v0.3.py` | 原 `experiments/run_benchmark_v0.3.py` | v0.3 benchmark runner |

## 4. experiments/analysis/（6 个测评脚本 + chamfer）

| 文件 | 来源（旧名）| 描述 |
|---|---|---|
| `m0m3_breakdown.py` | 原 `dataset/m0m3_analysis.py` | per-(method, layer) 成功/失败率 |
| `m0m3_significance.py` | 原 `dataset/m0m3_significance.py` | McNemar p-value |
| `m0m3_external_metrics.py` | 原 `dataset/m0m3_external_metrics.py` | 5 大外部指标（IVR/AUC-TR/VPR/MeanNCD/MedianNCD）|
| `benchmark_summary.py` | 原 `experiments/summarize.py` | 跨 benchmark 汇总 |
| `threshold_replay.py` | 原 `experiments/replay_threshold_trajectories.py` | §13 阈值回放 |
| `chamfer.py` | 原 `dataset/chamfer.py` | OCCT 几何距离（公共算法）|

## 5. experiments/REGISTRY.json（⭐ 新增：机器可读注册表）

```json
{
  "schema_version": "0.1",
  "last_updated": "2026-09-30",
  "cgvms": {
    "pipeline": {"path": "cgvm/pipeline", "since": "2026-09-30"},
    "solver":   {"path": "cgvm/solver",   "since": "2026-09-30"},
    "kernel":   {"path": "cgvm/kernel",   "since": "2026-09-30"}
  },
  "methods": {
    "M0_NoFeedback": {"channels": ["pipeline"],                  "since": "2026-07-24"},
    "M1_SolverOnly": {"channels": ["pipeline", "solver"],        "since": "2026-07-24"},
    "M2_KQPOnly":    {"channels": ["pipeline", "kernel"],       "since": "2026-07-24"},
    "M3_SolverKQP":  {"channels": ["pipeline", "solver", "kernel"], "since": "2026-07-24"}
  },
  "analysis_scripts": {
    "m0m3_breakdown":        {"path": "experiments/analysis/m0m3_breakdown.py",        "since": "2026-09-30"},
    "m0m3_significance":     {"path": "experiments/analysis/m0m3_significance.py",     "since": "2026-09-30"},
    "m0m3_external_metrics": {"path": "experiments/analysis/m0m3_external_metrics.py", "since": "2026-09-30"},
    "benchmark_summary":      {"path": "experiments/analysis/benchmark_summary.py",      "since": "2026-09-30"},
    "threshold_replay":      {"path": "experiments/analysis/threshold_replay.py",      "since": "2026-09-30"}
  },
  "experiment_phases": {
    "pilot_v0.2":     {"path": "experiments/pilot_v0.2/",     "samples": 30,  "status": "frozen",  "since": "2026-09-30"},
    "pilot_v0.2_m0":  {"path": "experiments/pilot_v0.2_m0/",  "samples": 70,  "status": "frozen",  "since": "2026-09-30"},
    "full_v0.2":      {"path": "experiments/full_v0.2/",      "samples": 167, "status": "frozen",  "since": "2026-09-30"},
    "m0m3_v0.3":      {"path": "experiments/m0m3_v0.3/",      "samples": 120, "status": "current", "since": "2026-09-30"}
  }
}
```

## 6. data/build_tools/（⭐ 新增：phase3 数据生产工具）

| 文件 | 来源（旧名）| 描述 |
|---|---|---|
| `__init__.py` | 原 `dataset/__init__.py` | package 入口 |
| `triplet.py` | 原 `dataset/triplet.py` | L1+L2+L3 三层验证 + build_triplet() |
| `build_triplets.py` | 原 `dataset/build_triplets.py` | CLI 入口（batch 构造 120 verified）|
| `freeze_verified.py` | 原 `dataset/freeze_verified.py` | 生成 `_frozen_manifest.json` |

注：`dataset/chamfer.py` 已迁到 `experiments/analysis/chamfer.py`（analysis 唯一需要的几何算法）。

## 7. doc/ 第三层（文档目录）

### 7.1 doc/ 顶层 md（当前 8 个）

| 文件 | 描述 |
|---|---|
| `experiment_contract_v0.1.md` | 主实验契约（FROZEN 2026-07-09）|
| `phase2AB_execution_guide.md` | Phase 2A+2B 执行指南 |
| `b009_diagnosis_guide.md` | B-009 诊断指南 |
| `execution_level_perturbation_plan_v0.1.md` | 扰动方案 |
| `pilot_protocol_v0.1.md` | pilot 协议 |
| `cad_edit_distance_spec.md` | CED v0.1 规范（FROZEN 2026-07-09）|

### 7.2 doc/ 子目录

| 子目录 | 状态 | 内容 |
|---|---|---|
| `project_asset_and_overview/` | 当前 | 3 层架构总览（01_data_layer、02_model_and_system_layer、03_experiment_metirc_and_doc）|
| `baseline_survey/` | 当前 | 14 文件（research surveys）|
| `portfolio/` | 当前 | 求职材料（与项目本身无关）|
| `_archive/` | ⭐ 新增 | 5 个过期文档归档（去空格 + 加 `_archive` 前缀）|

### 7.3 doc/_archive/（⭐ 新增：5 个过期文档）

| 旧（含空格）| 新（去空格）|
|---|---|
| `doc/KQP file/` | `doc/_archive/kqp_freeze/` |
| `doc/design plan file/` | `doc/_archive/design_plan_freeze/` |
| `doc/reconstruction engine file/` | `doc/_archive/reconstruction_engine_freeze/` |
| `doc/data_file/` | `doc/_archive/data_analysis/` |
| `doc/frozen_components_for_repair_benchmark.md` | `doc/_archive/frozen_components_for_repair_benchmark.md` |

## 8. 历史 phase2b_* → 版本号命名（Phase E 重命名）

| 旧 | 新 | 状态 | 样本数 |
|---|---|---|---:|
| `experiments/phase2b_pilot/` | `experiments/pilot_v0.2/` | frozen | 30 |
| `experiments/phase2b_pilot_m0/` | `experiments/pilot_v0.2_m0/` | frozen | 70 |
| `experiments/phase2b_full/` | `experiments/full_v0.2/` | frozen | 167 |
| `experiments/phase2b_m0m3/` | `experiments/m0m3_v0.3/` | **current** | 120 |

每个目录下加 README.md 说明：版本号、样本数、状态、对应原 phase2b 路径。

## 9. 命名约定统一（第三层）

| 维度 | 约定 | 实例 |
|---|---|---|
| Runner 入口 | `experiments/runners/<role>.py` | iter_runner、kqp_rerun、final_analysis、benchmark_v0.3 |
| Analysis 脚本 | `experiments/analysis/<metric>_<scope>.py` | m0m3_breakdown、m0m3_external_metrics、threshold_replay |
| Phase3 构建工具 | `data/build_tools/<role>.py` | triplet、build_triplets、freeze_verified |
| 实验阶段目录 | `experiments/<semantic_name>_v<M>.<p>/` | pilot_v0.2、full_v0.2、m0m3_v0.3 |
| Frozen 历史 | `experiments/frozen/<file>_v<N>.py` 或 `experiments/frozen/<name>/` | benchmark_v0.1、benchmark_v0.2_FROZEN |
| 过期文档 | `doc/_archive/<topic>/` | kqp_freeze、design_plan_freeze |

## 10. 第三层组织结构（Phase E 重构后）

```
experiments/                          # 实验运行 + 评测
├── runners/                          # 4 个 batch runner
│   ├── iter_runner.py               # 480 trial batch（120 frozen × 4）
│   ├── kqp_rerun.py                  # KQP v0.2 重跑
│   ├── final_analysis.py            # McNemar + 失败率
│   └── benchmark_v0.3.py            # v0.3 benchmark
├── analysis/                         # 6 个 analysis + chamfer
│   ├── m0m3_breakdown.py
│   ├── m0m3_significance.py
│   ├── m0m3_external_metrics.py
│   ├── benchmark_summary.py
│   ├── threshold_replay.py
│   └── chamfer.py
├── pilot_v0.2/                       # frozen (30 × 4)
├── pilot_v0.2_m0/                    # frozen (70 × M0)
├── full_v0.2/                        # frozen (167 × 4)
├── m0m3_v0.3/                        # current (120 frozen × 4)
├── history2ir_v0.1/                  # 原 experiments/history2ir/ batch 结果
├── frozen/                            # v0.1/v0.2 历史
│   ├── benchmark_v0.1.py
│   └── benchmark_v0.2_FROZEN.py
├── reports/                           # 跨 phase 汇总报告
├── config/                            # benchmark 配置
├── schema/                            # run_result schema
├── bugs/                              # bug DB
└── REGISTRY.json                      # ⭐ 新增：机器可读注册表

data/                                 # 第一层（Phase A/B/C 整理）
├── phase0_initial/                    # 50 source samples
├── phase1_positive/                   # positives
├── phase2_perturbation/               # 138 perturbation cases
├── phase3_triplets/                   # 120 verified
└── build_tools/                       # ⭐ 新增（phase3 数据生产工具）
    ├── __init__.py
    ├── triplet.py
    ├── build_triplets.py
    └── freeze_verified.py

history2ir/                            # ⭐ 新增（从 experiments/提升）
└── 5 个模态转换模块之一（与 history2cq/、history2plan/、plan2kqp/、text2ir/ 同级）

doc/                                   # 第三层文档
├── project_asset_and_overview/         # 架构总览（3 层）
├── baseline_survey/                    # 调研综述
├── portfolio/                          # 求职材料
├── experiment_contract_v0.1.md
├── phase2AB_execution_guide.md
├── b009_diagnosis_guide.md
├── execution_level_perturbation_plan_v0.1.md
├── pilot_protocol_v0.1.md
├── cad_edit_distance_spec.md
└── _archive/                           # ⭐ 新增：5 个过期文档归档
```

## 11. 未来扩展性保证

| 扩展场景 | 添加方式 |
|---|---|
| 新 CGVM（如 VLM-as-verifier `vision`）| `cgvm/<name>/`（5 子目录）+ `cgvm/__init__.py` re-export + REGISTRY.json 加 1 行 |
| 新 method（M4+）| `system/policy/policy.py` dict 加 1 行 + REGISTRY.json 加 1 行 |
| 新 analysis 指标 | `experiments/analysis/<script>.py` + REGISTRY.json 加 1 行 |
| 新数据模态 | 新顶层模块 + `data/phase*` 子目录 |
| 新实验组 | `experiments/<semantic_name>_v0.1/` |
| 新 frozen 版本 | `experiments/frozen/<name>_v<N>.py` |
| 新调研/文档 | `doc/<topic>.md` 或 `doc/baseline_survey/<topic>.md` |

## 12. import 路径变更（与三阶段一致）

| 旧 | 新 |
|---|---|
| `from dataset.triplet import ...` | `from data.build_tools.triplet import ...` |
| `from chamfer import ...` | `from experiments.analysis.chamfer import ...` |
| `import method_policy` | `from system.policy import policy as method_policy` |
| `import trial_iteration` | `from system.core import iter_loop as trial_iteration` |
| `ROOT / "experiments/phase2b_full"` | `ROOT / "experiments/full_v0.2"` |
| `ROOT / "kqp/runner/query_dispatcher.py"` | `ROOT / "cgvm/kernel/runtime/dispatcher.py"` |
| `ROOT / "kqp/runner"` | `ROOT / "cgvm/kernel/runtime"` |
| `from cad_agent` | `from system.agent.core.caller`（+ `system.agent.schema`）|
| `from cad_runtime` | `from cgvm.pipeline.runtime.executor` |

## 13. Phase E 重构数字

| 维度 | 重构前 | 重构后 |
|---|---|---|
| experiments/ 顶层 p2b_*.py runner 入口数 | 6（含版本混叠）| 0（全部移到 runners/ + frozen/）|
| experiments/phase2b_* 子目录数 | 4（命名混乱）| 0（全部按版本号命名为 pilot_v0.2 等）|
| Top-level *.py 含 runner 数 | 8 | 1（_test_concentric.py，无关）|
| experiments/analysis 文件数 | 0（散落多处）| 6（统一 + chamfer）|
| doc/ 含空格目录数 | 4（命名违规）| 0（全部进 _archive/）|
| doc/_archive/ 过期文档归档数 | 0 | 5 |
| experiments/REGISTRY.json | 不存在 | 存在（1759 字节，机器可读）|
| data/build_tools/ phase3 工具 | 不存在 | 存在（4 物理工具）|
| dataset/ 顶层残留 | 5 文件 + 跨两层 | 0（分散完成）|
| history2ir/ 顶层位置 | 在 experiments/ | 提升到顶层（5 个模态转换模块之一）|
| 数据层 cgvm system history2ir 一致性 | 散落 | **统一 5-subdir 约定**（核心 cgvm + system + 第三层 experiments）|

### 性能数字（不变）

5 大外部指标（PIVR/SIVR/PSIVR/VPR/AUC-TR/MeanNCD/MedianNCD）逐字与重构前一致。M2 92.5% > M3 89.2% > M0 75.8% > M1 67.5%。

## 14. git 提交历史（最近 6 条）

```
0aade25 Phase E: experiment/eval layer restructure
dbd7b5b Phase D: model/system layer rename
863e98f pre-phase-D-snapshot
0ec89d8 Phase C: module rename + 5-subdir restructure
43e3c20 data-layer B2.5: rewrite HISTORY_JSON absolute paths
55d912e data-layer B2: move raw+derived data
```

三阶段重构（数据 / 模型系统 / 实验测评）全部完成。各层文件 100% 自包含，扩展性满足"加新 method/CGVM/analysis 指标 1 行 REGISTRY.json 即可"的预期。