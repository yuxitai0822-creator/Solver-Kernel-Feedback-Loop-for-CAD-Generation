# 第一部分：数据层（Data Layer）

## 1. 数据层架构总览

数据层是子课题1实验/测评/报告层的基础，由两个**互相独立**的子系统组成：

1. **数据资产（Data Assets）**：位于 `data/` 顶层目录，按 **phase 0 → 1 → 2 → 3** 线性流动，4 个 phase 共存而非覆盖。
2. **数据模态转换模块（Modal Conversion Modules）**：4 个独立 Python 包，实现"源数据 → 中间表示 → 验证模态"的链式转换，命名为 `<source>2<target>/` 自解释范式。

数据层之上是实验 / 测评 / 报告层，下层无依赖——这是 2026-09-28 重构（Phase A/B 数据层整理 + Phase C 模块重组织）之后的稳定拓扑。

---

## 2. 数据资产（`data/`）

### 2.1 Phase 0 — Initial Dataset（`data/phase0_initial/`）

- 50 个 Fusion360 Gallery Reconstruction source samples
- 5 个模态（每个 sample 一份）：
  | 扩展 | 用途 |
  |---|---|
  | `.json` | Fusion360 modeling history（顶层键：`metadata` / `timeline` / `entities` / `properties` / `sequence`） |
  | `.step` | 可读本体（用于 KQP + 几何对比） |
  | `.obj` | 视效（三角网格） |
  | `.smt` | 备用 B-rep |
  | `.png` | 缩略图 |
- **Selection rule**（`data/build_sanity_set.py`）：仅 sketch + extrude（无 Revolve/Fillet/Hole/Loft），每 sketch ≤ 8 曲线，无 spline/ellipse/conic，按 sorted id 取前 50

### 2.2 Phase 1 — Positive Augmentation（`data/phase1_positive/`）

正样本增强。50 source → 51 instances，分 **4 个子模态**：

| 子目录 | 内容 | Schema |
|---|---|---|
| `reconstruction/` | ReconstructionEngine 产物：`<sid>/{generated_code.py, generated.step, execution_report.json, stdout.txt, stderr.txt}` + 顶层 `clean_reconstruction_set.json` / `runtime_config_v0.1.json` | — |
| `cad_ir/` | CAD IR v0.1（手工 examples + History2IR 批量编译产物） | `schema/cad_ir_schema_v0.1.json` |
| `design_plan/` | DesignPlan v0.5 frozen | `schema/DesignPlan_schema05.txt` |
| `kqp/` | KQP v0.2 (current) + v0.1 (legacy) | `schema/kqp_schema_v0.2.txt` |

**派生 lineage**：
- `phase0_initial/history` → `history2cq.runtime.orchestrator` → `reconstruction/`
- `phase0_initial/history` → `history2plan.core.compiler` → `design_plan/`
- `phase1_positive/design_plan` → `plan2kqp.core.compiler` → `kqp/`
- `phase0_initial/history` → `experiments/history2ir/batch/run_history2ir.py` → `cad_ir/instances/history2ir_*`

### 2.3 Phase 2 — Perturbation（`data/phase2_perturbation/`）

扰动构造（negative 样本的原始材料）。50 source × 平均 2.76 operator/case = **138 cases**（4 source 在 EX 路径下失败）。

`artifacts/<sid>/<neg_id>/` 包含 8 类产物：
- `perturbed_history.json`（原始扰动模态）
- `perturbed_design_plan.json`（同步镜像）
- `perturbed_cad_ir.json`（History2IR 重编译）
- `perturbed_script.py`（ReconstructionEngine 产物）
- `perturbed.step`（负样本 STEP）
- `perturbation_meta.json`（operator / target_intent / expected_failed_query）
- `kqp_result.json`（KQP 验证）
- `reconstruction_report.json`（4 状态）

### 2.4 Phase 3 — Verified Triplets（`data/phase3_triplets/`）

最终 verified (Code_gt, Code_perturbed, T_ref) 三元组。**120 verified**（138 损失 18：4 GT STEP 拓扑错误 + 6 E6 STEP 拓扑错误 + 8 KQP coverage/data gap）。

`_FROZEN.md` + `_frozen_manifest.json` 是冻结索引（freeze_date = 2026-07-24）。`triplet.json` 含 L1 + L2 + L3 三层 verification 详细记录。

### 2.5 数据层约定

| 约定 | 规则 |
|---|---|
| Schema 命名 | `schema/current.<ext>`（活动）+ `schema/archive/`（归档） |
| Manifest | 每个 phase 子目录有 `manifest.json`，机器可读 |
| README | 每个 phase 顶层有 `README.md`，人类可读 |
| Frozen | 带 `_FROZEN.md` 的目录未经解冻流程前不应修改 |
| Old → New 路径映射 | 详见 `data/README.md` 末尾 |

---

## 3. 数据模态转换模块（4 个）

命名统一遵循 `<source>2<target>/` 自解释范式；每个模块固定 **5 子目录**（schema / core / runtime / tests / legacy）。

### 3.1 `history2cq/` — History → CadQuery

| 项 | 内容 |
|---|---|
| 作用 | Fusion360 history JSON → CadQuery Python source |
| 关键代码 | `core/compiler.py`（确定性 history → CadQuery） |
| Runtime | `runtime/executor.py`（subprocess 包装）+ `runtime/orchestrator.py`（compile → execute → occt_load） |
| Schema | 无独立 schema（输入是 Fusion360 history.json） |
| Tests | 暂空（占位） |
| Legacy | `_FROZEN/` 保留 v0.1 frozen snapshots |
| 公开 API | `compile_history`、`execute_generated_code`、`reconstruct_sample`、`reconstruct_batch` |
| 旧名（已删除） | `reconstruction_engine/` |

### 3.2 `history2plan/` — History → DesignPlan

| 项 | 内容 |
|---|---|
| 作用 | Fusion360 history JSON → DesignPlan JSON |
| 关键代码 | `core/compiler.py`（6 阶段编译：parse → dep graph → profile recognition → dimension extraction → extrude params → frame + part_category） |
| Runtime | `runtime/batch_runner.py`（原 `run_all_50.py` 改名） |
| Schema | `schema/current.txt` (schema05)；`schema/archive/schema0[1-4].txt` |
| Tests | `tests/analysis/`（4 个分析脚本：compare / freeze_assessment / freeze_summary / kqp_field_inventory）+ `tests/smoke/`（3 个一次性 sanity 脚本） |
| Legacy | `_FROZEN/compiler_v0.6_FROZEN.py`、samples v1..v6、out/out_v5/out_v6 |
| 公开 API | `compile_design_plan` |
| 旧名（已删除） | `DesignPlan/`（该模块本身没有 `__init__.py`，原本是裸目录） |

### 3.3 `plan2kqp/` — DesignPlan → KQP

| 项 | 内容 |
|---|---|
| 作用 | DesignPlan JSON → KQP instance（**compile** 子模块）+ KQP instance + STEP → KQP result（**dispatch** 子模块） |
| core/compiler/ | `compiler.py`、`compiler_v0.1_FROZEN.py`、`query_builder.py`、`plan_reader.py`、`source_mapper.py`、`feedback_builder.py` |
| core/dispatch/ | `dispatcher.py`、`dispatcher_v0.1_FROZEN.py`、`dispatcher_v0.6_FROZEN.py`、`geometry_backend.py`、`step_loader.py`、`result_builder.py` |
| Runtime | `runtime/cli.py`（CLI 入口，原 `run_kqp.py`） |
| Schema | `schema/current.txt` (v0.2)；`schema/archive/v0.1.txt` |
| Tests | `tests/analysis/`（analyze_patterns、fix_canonical、semantic_match）+ `tests/smoke/`（gen_batch5/6、review_batch_1、run_review_v0.2） |
| Legacy | `_FROZEN/`（v0.1 snapshots）、samples v0.1/v0.2（重复数据保留作考古）、results/、match/、review/、verification/、exp01_sample1_feasibility/、task4_report.md |
| 公开 API | `compile_one`、`compile_batch`、`dispatch_query`、`load_step` |
| 旧名（已删除） | `kqp/` |

### 3.4 `text2ir/` — (Natural language text) → CAD IR

| 项 | 内容 |
|---|---|
| 作用 | CAD IR v0.1 → CadQuery code（**adaptor** 子模块）+ IR schema + semantic 验证（**validator** 子模块） |
| core/adaptor/ | `adapter.py`、`cadquery_backend.py`、`trace_builder.py`、`run_adaptor.py` |
| core/validator/ | `validator.py`（schema + semantic 校验）、`run_validation.py` |
| Tests | `tests/samples/generate_from_clean_samples.py` |
| Legacy | `reports/`（phase_1/2/4_repair_loop 历史报告）、`cad_ir_schema_v0.1_spec.md` |
| Schema | `schema/current.json` (v0.1 frozen) |
| 状态 | Phase 2A 之后 LLM 改走 direct CadQuery 输出，CAD IR 转为受控编辑接口；模块仍保留作 validation 工具 |
| 公开 API | `validate`、`validate_file`、`adapt_file` |
| 旧名（已删除） | `cad_ir/` |

---

## 4. 数据层组织结构（重构后）

### 4.1 顶层布局

```
子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究/
├── data/                          # 数据资产（4 phases）
│   ├── README.md
│   ├── INDEX.json
│   ├── phase0_initial/
│   ├── phase1_positive/{reconstruction,cad_ir,design_plan,kqp}/
│   ├── phase2_perturbation/
│   └── phase3_triplets/           # _FROZEN.md + 120 verified
│
├── history2cq/                    # 数据模态转换模块 1
│   ├── README.md / CHANGELOG.md / __init__.py
│   ├── schema/                    # (空 + README 说明)
│   ├── core/                      # compiler.py
│   ├── runtime/                   # executor / orchestrator / 3 batch runners
│   ├── tests/                     # 占位
│   └── legacy/_FROZEN/            # v0.1 snapshots
│
├── history2plan/                  # 数据模态转换模块 2
│   ├── schema/{current.txt, archive/schema0[1-4].txt}
│   ├── core/compiler.py
│   ├── runtime/batch_runner.py
│   ├── tests/{analysis/, smoke/}
│   └── legacy/{_FROZEN/, samples/, out/, out_v5/, out_v6/}
│
├── plan2kqp/                      # 数据模态转换模块 3
│   ├── schema/{current.txt, archive/v0.1.txt}
│   ├── core/{compiler/, dispatch/}
│   ├── runtime/cli.py
│   ├── tests/{analysis/, smoke/}
│   └── legacy/{_FROZEN/, samples/, results/, match/, review/, verification/, exp01_sample1_feasibility/, task4_report.md}
│
├── text2ir/                       # 数据模态转换模块 4
│   ├── schema/current.json
│   ├── core/{adaptor/, validator/}
│   ├── tests/samples/
│   └── legacy/{reports/, cad_ir_schema_v0.1_spec.md}
│
├── dataset/                       # 数据层工具
│   ├── chamfer.py                 # CD 距离
│   ├── triplet.py                 # build_triplet(L1+L2+L3)
│   ├── build_triplets.py
│   ├── freeze_verified.py
│   ├── m0m3_external_metrics.py   # 5 大外部指标
│   ├── m0m3_significance.py
│   └── m0m3_analysis.py
│
├── history2cq/         
├── history2Plan/                     
├── plan2kqp/                           
└── text2ir/                       
```

### 4.2 依赖图（无环）

```
history2cq ─→ 输出 STEP ─┐
                         ├─→ plan2kqp.core.dispatch.step_loader
history2plan ─→ DesignPlan → plan2kqp.core.compiler
text2ir ─→ IR JSON ─→ text2ir.core.adaptor ─→ CadQuery code
```

**约束**：4 个模块之间没有反向依赖；每个模块可独立测试 / 单独替换。

### 4.3 关键命名 / 命名空间

| 维度 | 约定 |
|---|---|
| 模块顶层名 | `<source>2<target>/`（4 个模块已统一） |
| 子目录 | `schema/`、`core/`、`runtime/`、`tests/`、`legacy/`（5 个固定） |
| Schema 文件 | `schema/current.<ext>`（活动）+ `schema/archive/`（归档） |
| Frozen snapshot | `legacy/_FROZEN/`（仍可加载，明确标注 FROZEN） |
| 公开 API 入口 | `<module>/__init__.py` re-export |
| 模块文档 | `<module>/README.md`（人类）+ `<module>/CHANGELOG.md`（版本） |