# 第二部分：模型与系统层（Model & System Layer）

## 1. 架构总览

模型与系统层建立在数据层之上，由两个**互相独立**的子系统组成：

1. **3 个 CGVM 模块**（`cad_verification/`）：Pipeline / Solver / Kernel，分别独立校验 CAD 的不同维度。它们是"反馈信号源"。
2. **4 个 iterative CAD generation system**（M0/M1/M2/M3）：共享同一套 iter loop + LLM agent + prompt 骨架，**唯一**差异是"提供哪些 CGVM feedback 通道给 LLM"。

**核心不变量**（`method_policy.py` docstring）：3 个 verification **永远全部执行**；method 参数只决定哪些 diagnostic 被注入 prompt。这与`cad_verification`层 +`trial_iteration.run()` 的"verification 无 method 分支"实现完全一致。

```
                  ┌─────────────── data/ ───────────────┐
                  │   phase0/1/2/3 历史 + 当前 数据资产  │
                  └──────────────┬────────────┬─────────┘
                                 │            │
                                 ▼            ▼
                  ┌────────────────────┐  ┌───────────────┐
                  │ history2cq / plan   │  │ history2plan  │
                  │ 2kqp / text2ir (4   │  │               │
                  │ 模态转换模块)        │  └───────┬───────┘
                  └────────┬───────────┘          │
                           │                      │
                           ▼                      ▼
              ┌─────────────────────────────────────────────┐
              │            CGVM (3 verification objects)        │
              │  Pipeline / Solver / Kernel                   │
              │  全部独立 run，全部 always-executed           │
              └─────────────────────┬───────────────────────┘
                                    │
                                    ▼
              ┌─────────────────────────────────────────────┐
              │   trial_iteration.run(method, ...)          │
              │   - filter feeding / method policy            │
              │   - call DeepSeek (cad_agent/agent_v2)        │
              │   - assemble prompt (prompt_builder_v2)      │
              └─────────────────────┬───────────────────────┘
                                    │
                                    ▼
              ┌─────────────────────────────────────────────┐
              │  experiments/phase2b_m0m3/ M0/M1/M2/M3 实验    │
              │  （下一部分）                                   │
              └─────────────────────────────────────────────┘
```

---

## 2. 3 个 CGVM 模块

3 个 CGVM 都定义在 `cad_verification/`，对外输出统一通过 `@dataclass VerificationResult`（`cad_verification/_base.py`），不共享基类，仅 duck-typed `run()` → `VerificationResult` 接口。

### 2.1 Pipeline Execution CGVM

| 项 | 内容 |
|---|---|
| **作用** | 验证 CAD code 能被 CAD runtime 正确执行并生成有效 artifact（syntax correctness / API availability / execution success / STEP export / OCCT loading） |
| **主文件** | `cad_verification/pipeline.py`（158 行，类 `PipelineVerification`） |
| **底层执行器** | `cad_runtime/executor.py`（239 行，`execute_cad_script()`） |
| **包入口** | `cad_verification/__init__.py`、`cad_runtime/__init__.py` |
| **基类** | `cad_verification/_base.py`（69 行，`@dataclass VerificationResult`） |
| **验证方式** | Pipeline executor: `CAD Script → CAD Runtime → Execution log → STEP file → OCCT loader` |
| **通过方式** | `compile_pass ∧ execute_pass ∧ export_pass ∧ load_pass`（4 个 boolean AND） |
| **诊断 schema** | `{stage: "execute", error_type: "runtime_error", message: "Undefined variable xxx", trace: "..."}` |
| **粒度** | code-level |

### 2.2 Solver CGVM

| 项 | 内容 |
|---|---|
| **作用** | 验证 CAD 中 sketch constraint 是否可求解、无冲突、满足工程约束 |
| **主文件（接口层）** | `cad_verification/solver.py`（195 行，类 `SolverVerification`） |
| **后端实现：FreeCAD** | `Freecadsolver_feedback/core/`（9 个文件） |
| **后端实现：Kiwisolver** | `Kiwisolver_feedback/core/`（9 个文件） |
| **Solver Acceptable 判定位置** | 接口层 `cad_verification/solver.py::_is_acceptable()`（L77-L97） |
| **Solver Acceptable 定义** | `solver_executed ∧ no_conflict ∧ no_redundant ∧ engineering_constraint_satisfied` |
| **通过方式** | `Solver Acceptable`（不要简单 `fully_constrained`，因为工业 CAD 不一定要求完全约束；allow `under_constrained` 与 `redundant`） |
| **诊断 schema** | `{solver_status: "over_constrained", dof: 0, conflict_constraints: [12, 15], redundant_constraints: [8]}` |
| **粒度** | constraint-level |

**Solver Acceptable 判定逻辑**（`cad_verification/solver.py::_is_acceptable()`）：
- 若 `solve.status ∈ BLOCKING_STATUSES = {conflicting, over_constrained, unsolvable, invalid_constraint_reference}` → False
- 若 `flags.has_conflict` 或 `has_over_constrained` → False
- 若 `severity ∈ {"blocking","error"}` → False
- 其余（含 `fully_constrained / under_constrained / redundant`）→ True

**状态字符串生成位置**：每个后端 `diagnostic_normalizer.py` 中的 `normalize_solve()`（FreeCAD `L46-L72`、Kiwisolver `L41-L61`），把原始 return code / dof / 各种 constraint 列表统一映射为 `{solve_status, severity, dof, flags, ...}`。

**后端实现层（每个后端都有 4 层 pipeline）**：

| 层 | FreeCAD | Kiwisolver |
|---|---|---|
| L1 raw | `solver_runner.py` (`run_solver_from_history`，调 FreeCAD Sketcher `sketch.solve()`) | `solver_runner.py` (`run_solver_from_history`，调 `kiwisolver` 求解 2D 线性约束) |
| L1 raw | `recompute_runner.py` (`run_recompute_from_state`) | `recompute_runner.py` (`run_recompute`，基于 per-feature sanity rules) |
| L2 诊断 formatter | `diagnostic_normalizer.py` (`normalize_solve/recompute`) | `diagnostic_normalizer.py` |
| L3 structured | `diagnostics_builder.py` (`build_constraint_diagnostics`) | `diagnostics_builder.py` |
| L3 fallback | `fallback_analyzer.py` (no-op) | `fallback_analyzer.py` (`leave_one_out_redundancy` + `leave_one_out_suspected_conflict`) |
| L4 LLM-facing | `feedback_builder.py`（输出 `{summary, blocking_errors, warnings, suggested_actions, do_not_change}`） | `feedback_builder.py` |
| Spec 翻译 | `history_parser.py`（Fusion360 history → FreeCAD sketch spec，含 annulus auto-pin B-006） | `history_parser.py` |
| Pipeline builder | `pipeline.py` (`build_solver_feedback` + `write_solver_feedback`) | `pipeline.py` |

### 2.3 Kernel CGVM（Kernel validation）

| 项 | 内容 |
|---|---|
| **作用** | 验证 CAD geometry 是否满足 Design Intent（dimension / topology / spatial relation / derived geometry） |
| **主文件（接口层）** | `cad_verification/kernel.py`（295 行，类 `KernelVerification`） |
| **底层 dispatch** | `plan2kqp/core/dispatch/dispatcher.py`（209 行，`dispatch_query()`，即原 `kqp/runner/query_dispatcher.py`） |
| **底层 geometry_backend** | `plan2kqp/core/dispatch/geometry_backend.py`（311 行，OCCT 原子查询） |
| **底层 step_loader** | `plan2kqp/core/dispatch/step_loader.py`（51 行，OCP `STEPControl_Reader`） |
| **底层 result_builder** | `plan2kqp/core/dispatch/result_builder.py`（37 行，组装 KQPResult JSON） |
| **包入口** | `plan2kqp/core/dispatch/__init__.py`（re-export `dispatch_query, load_step`） |
| **验证方式** | `Design Plan → Kernel Query → OCCT Geometry Query → Expected vs Actual comparison` |
| **通过方式（sample-level）** | All required queries pass |
| **通过方式（query-level）** | Actual within tolerance |
| **诊断 schema** | `{failed_query: "bbox_size", target: "x_length", expected: 50, actual: 72, error: 22}` |
| **粒度** | intent-level |

**`SUPPORTED_INTENTS`**（7 种 intent，`cad_verification/kernel.py` L54-L62）：
```
body_count, bbox_size, cylinder_radius, through_void_count,
is_solid, occt_valid, symmetric_about_plane
```

**`DEFAULT_TOLERANCE`**（`cad_verification/kernel.py` L67-L75）：
```
body_count=0, bbox_size=0.05, cylinder_radius=0.01,
through_void_count=0, is_solid=None, occt_valid=None, symmetric_about_plane=None
```

### 2.4 3 个 CGVM 共用基类

`cad_verification/_base.py` 定义**唯一**的共享类型 `@dataclass VerificationResult(name, passed, diagnostic, full, skipped, extras)`：
- `name ∈ {"pipeline", "solver", "kernel"}`
- `passed ∈ {True, False, None}`；`skipped` 从 `passed is None` 自动同步
- `diagnostic` 按 CGVM 类型填充不同 schema（pipeline: stage/error_type/message/trace；solver: solver_status/dof/conflict_constraints/redundant_constraints/severity；kernel: failed_queries[]）
- `full` 始终保留供离线分析
- `extras` 承载 `skipped_reason`

3 个 CGVM 类**不继承同一基类**，仅通过 duck-typed `run()` → `VerificationResult` 接口对齐。`method_policy.METHOD_FEEDBACK_CHANNELS` 按 `name` 决定哪些 `diagnostic` 字段被喂回 LLM。

---

## 3. 4 个 iterative CAD generation system（M0/M1/M2/M3）

### 3.1 系统差异（**唯一**）

| 系统 | feedback channels | max_iter | 共享代码 |
|---|---|---|---|
| **M0_NoFeedback** | `{pipeline}` | 3 | 100% 共享 |
| **M1_SolverOnly** | `{pipeline, solver}` | 3 | 100% 共享 |
| **M2_KQPOnly** | `{pipeline, kernel}` | 3 | 100% 共享 |
| **M3_SolverKQP** | `{pipeline, solver, kernel}` | 3 | 100% 共享 |

**唯一差异点是 `method_policy.METHOD_FEEDBACK_CHANNELS` dict 里每个 method 启用的 channel 集合**。3 个 verification 全部跑；method 只决定哪些 `diagnostic` 被注入 prompt。

### 3.2 iter loop（共享）

```
for it in range(MAX_ITERATIONS=3):
    filtered_history = _filter_iter_history(iter_records, channels)
    obj = call_cad_agent(design_plan, current_script, ..., feedback=filtered_history, ...)
    pipeline_res = pipeline_v.run(new_script, iter_dir)
    solver_res   = solver_v.run(history_p)  [仅在 pipeline 通过 + history 存在时]
    kernel_res   = kernel_v.run(step_path, kqp_p, plan)  [仅在 pipeline + solver 都通过 + step + kqp 存在时]
    iter_records.append({...filtered verification...})

退出：三者全 pass → "success"；否则 max_iter 跑满 → "max_iter_exceeded"
```

| 组件 | 文件 |
|---|---|
| Iter loop 主函数 | `trial_iteration.py::run(method, sid, nid, layer, out_dir, initial_script)` |
| Feedback 过滤 | `trial_iteration.py::_filter_iter_history()`（line 111-139，**保留**所有 verification result，**只翻动 `exposed` 标志**） |
| Verification 格式化 | `trial_iteration.py::_format_verification()`（line 142-157） |
| LLM agent 调用 | `cad_agent/agent_v2.py::call_cad_agent()`（DeepSeek backend + retry + jitter + hard_timeout） |
| Prompt 组装 | `cad_agent/prompt_builder_v2.py::build_prompt_v2()` + `_fmt_iter_history()`（line 57-102） |
| Prompt 后向兼容 shim | `cad_agent/prompt_builder.py::build_prompt()`（feedback=None → v0 模板；feedback≠None → v2 路由） |

### 3.3 batch runner

| 文件 | 角色 |
|---|---|
| `p2b_m0m3_on_frozen.py`（262 行） | **4-system batch runner**：遍历 120 frozen × 4 methods = 480 trials。读 `_frozen_manifest.json`，调 `trial_iteration.run()`，原子写 `pilot_results.json`。带 resume + defensive base-exception 捕获（`runner_crash`）。 |

### 3.4 Policy + Agent + Prompt 详情

**`method_policy.py`**（核心 policy 声明）：
```python
METHOD_FEEDBACK_CHANNELS: dict[str, set[str]] = {
    "M0_NoFeedback":  {"pipeline"},
    "M1_SolverOnly":  {"pipeline", "solver"},
    "M2_KQPOnly":     {"pipeline", "kernel"},
    "M3_SolverKQP":   {"pipeline", "solver", "kernel"},
}
MAX_ITERATIONS: int = 3
METHODS_IN_ORDER = ("M0_NoFeedback", "M1_SolverOnly", "M2_KQPOnly", "M3_SolverKQP")
VERIFICATION_NAMES = ("pipeline", "solver", "kernel")
```

**`cad_agent/agent_v2.py::call_cad_agent()`**：
- **Backend**: DeepSeek `deepseek-chat`（OpenAI-compatible API）
- **Hard timeout**: 90s（模块级 ThreadPoolExecutor 跨调用复用）
- **Retry**: max 3 次，仅 transient 异常（network/timeout）；JSON 解析 / 验证错误**不**重试
- **Fallback**: `.env` 文件读 API key；`_bypass_dead_proxy()` 探测死代理

**`cad_agent/prompt_builder_v2.py::build_prompt_v2()`**：
- 4 个区块：(1) System preamble（指定输出合同："reasoning" 字段 + "cadquery Python 脚本" + `cq.exporters.export` 显式写出 `OUT_STEP_PATH`）；(2) Design Plan；(3) Perturbation description；(4) Previous code + filtered iter-history
- `_fmt_iter_history()` 只渲染 `exposed=True` 的 channel；若所有 channel 都未暴露，告知 LLM "本方法没暴露任何反馈通道，自行从上下文纠错"

### 3.5 M0/M1/M2/M3 各自的 feedback 流（按 spec）

| 系统 | pipeline 失败时 | solver 失败时 | kernel 失败时 |
|---|---|---|---|
| **M0** | 暴露为 `feedback.pipeline`，下一轮 LLM 看到 | 不暴露（让 LLM 自纠错） | 不暴露（让 LLM 自纠错） |
| **M1** | 暴露为 `feedback.pipeline` | 暴露为 `feedback.solver` | 不暴露（让 LLM 自纠错） |
| **M2** | 暴露为 `feedback.pipeline` | 不暴露（让 LLM 自纠错） | 暴露为 `feedback.kernel` |
| **M3** | 暴露为 `feedback.pipeline` | 暴露为 `feedback.solver` | 暴露为 `feedback.kernel` |

---

## 4. Legacy / 并行系统（**不属于 M0-M3**）

`cad_repair_loop/` 是 M0-M3 之前的独立系统，**与 M0-M3 完全两套接口**：

| 维度 | cad_repair_loop（前世） | M0-M3（当前） |
|---|---|---|
| 状态单位 | **cad_ir_v0.1 IR JSON** | **cadquery Python 脚本** |
| LLM backend | **ZHIPU glm-5.1** | DeepSeek deepseek-chat |
| Feedback payload | 裸 dict `solver_feedback` + `kqp_feedback` | 带 `exposed` 标志的 `iter_records[]`，按 method policy 过滤 |
| Success metric | 含 CED（code edit distance） | VPR（pipeline ∧ solver ∧ kernel 全 pass） |
| Agent 接口 | `cad_repair_loop/llm_agent.py::call_zhipu()` | `cad_agent/agent_v2.py::call_cad_agent()` |

### `cad_repair_loop/` 全部文件

| 文件 | 角色 |
|---|---|
| `__init__.py` | 空 |
| `llm_agent.py` | ZHIPU backend agent（IR-based I/O，含 offline fallback） |
| `llm_agent_v0.1_FROZEN.py` | 冻结备份 |
| `repair_loop.py` | 顶层修复循环：`run_repair_loop(initial_ir, design_plan, out_dir, use_solver_feedback, agent_mode)` |
| `run_repair_loop.py` | CLI 入口：批量跑 manual IR examples |
| `subprocess_bridge.py` | 跨 conda env 子进程桥（`CADQUERY_PYTHON`, `FREECAD_PYTHON`） |
| `_adaptor_subprocess.py` | subprocess worker，从 `text2ir.core.adaptor.adapter` 引入 |
| `test_repair_against_perturbed_ir.py` | 故意减半 extrude distance 走 repair loop 验证 |

**结论**：`cad_repair_loop/` 与 M0-M3 共用 `Freecadsolver_feedback/` 与 `Kiwisolver_feedback/`（Solver CGVM 的两个后端实现），但状态表示、agent backend、success metric 完全不同。属前世/并行系统，**不属于 M0-M3 任何一组**。

---

## 5. Layer 间依赖

```
data/
    │   ↑↑
    │  读
    ▼
history2cq / history2plan / plan2kqp / text2ir
    │   ↑↑（re-export pipeline_feedback, kernel_feedback）
    │  读 STEP / 写 STEP
    ▼
cad_verification/  ← 3 个 CGVM（pipeline, solver, kernel）
    │   ↑↑  (VerificationResult)
    │  invoked by
    ▼
trial_iteration.run(method, ...)
    │   ↑↑ feedback filtered by method_policy.METHOD_FEEDBACK_CHANNELS
    │  invoked by
    ▼
cad_agent/agent_v2.py  (DeepSeek backend)
cad_agent/prompt_builder_v2.py  (M0-M3 iterative prompt)
    │   ↑↑
    │  driven by
    ▼
p2b_m0m3_on_frozen.py  (batch runner: 120 × 4 = 480 trials)
    │   ↑↑
    │  reads
    ▼
data/phase3_triplets/_frozen_manifest.json
```

**约束**：
- CGVM 层（`cad_verification/`）只**读**数据层，不依赖具体 system
- trial_iteration 层**全部 3 段 verification**都跑，method 只控制 feedback 过滤
- 4 个 system 共享 100% 代码路径；method_policy 是唯一差异源
- CGVM 与 trial_iteration 之间通过 `VerificationResult` dataclass（`cad_verification/_base.py`）解耦

---

## 6. 顶层布局（model & system 相关）

```
子课题1-.../
├── cad_verification/                # 3 个 CGVM + 基类
│   ├── _base.py                     # @dataclass VerificationResult
│   ├── pipeline.py                  # Pipeline CGVM
│   ├── solver.py                    # Solver CGVM（接口）
│   └── kernel.py                    # Kernel CGVM
│
├── cad_runtime/                     # Pipeline CGVM 底层
│   └── executor.py                  # execute_cad_script()
│
├── Freecadsolver_feedback/          # Solver CGVM FreeCAD 后端
│   └── core/{pipeline,solver_runner,recompute_runner,
│              registry_builder,diagnostic_normalizer,
│              diagnostics_builder,fallback_analyzer,
│              feedback_builder,history_parser}.py
│
├── Kiwisolver_feedback/            # Solver CGVM Kiwisolver 后端
│   └── core/...  (9 个文件，与 FreeCAD 同构)
│
├── plan2kqp/                        # Kernel CGVM 底层（Phase C 重构后）
│   └── core/dispatch/{dispatcher,geometry_backend,
│                        step_loader,result_builder}.py
│
├── cad_agent/                       # LLM agent + prompt
│   ├── agent_v2.py                  # DeepSeek backend + retry + hard_timeout
│   ├── prompt_builder_v2.py         # M0-M3 反馈注入
│   ├── prompt_builder.py            # 后向兼容 shim（feedback=None → v0；≠None → v2）
│   └── schema.py
│
├── trial_iteration.py               # M0-M3 iter loop（共享 100%）
├── method_policy.py                 # 唯一差异源：METHOD_FEEDBACK_CHANNELS
│
├── p2b_m0m3_on_frozen.py            # 480 trial batch runner
│
├── cad_repair_loop/                 # LEGACY（不属于 M0-M3）
│   ├── llm_agent.py                 # ZHIPU backend
│   ├── llm_agent_v0.1_FROZEN.py
│   ├── repair_loop.py
│   ├── run_repair_loop.py
│   ├── subprocess_bridge.py
│   ├── _adaptor_subprocess.py
│   └── test_repair_against_perturbed_ir.py
│
└── ...
```