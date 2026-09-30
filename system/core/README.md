# system/core/ — iter loop

| 文件 | 作用 |
|---|---|
| `iter_loop.py` | 原 `trial_iteration.py`，M0-M3 单 trial 的 iter loop 主函数 `run(method, sid, nid, layer, out_dir, initial_script, initial_per_iter, max_iterations)` |

## iter loop 流程

```
for it in range(max_iter):               # max_iter=3 from system.policy.policy
    filtered_history = _filter_iter_history(iter_records, channels)
    obj = call_cad_agent(design_plan, current_script, feedback=filtered_history, ...)
    pipeline_res = pipeline_v.run(new_script, iter_dir)
    solver_res   = solver_v.run(history_p)        # 仅 pipeline 通过时
    kernel_res   = kernel_v.run(step, kqp, plan)  # 仅前两者通过 + step + kqp 存在
    iter_records.append({...filtered verification...})
退出：三者全 pass → "success"；否则 max_iter 跑满 → "max_iter_exceeded"
```

`_filter_iter_history()` 是 iter loop 唯一与 `method` 相关的方法——它按 `method_policy.feedback_channels_for(method)` 给每个 verification 标 `exposed: bool`，prompt builder 据此决定渲染哪些 diagnostic。

## 上下游

- **上游（依赖）**：`system/policy/policy.py::METHOD_FEEDBACK_CHANNELS`、`cgvm.{pipeline,solver,kernel}.core.verification`、`system/agent/core/caller::call_cad_agent_v2`、`system/agent/prompt/builder::build_prompt`、`data/phase3_triplets/`（frozen triplets）
- **下游（被消费）**：`system/batch/runner.py::main`（480 trial batch）、`experiments/phase2b_m0m3/` 实验数据

## 公开 API

```python
from system.core.iter_loop import run as run_iter

# 跑一个 trial
run_iter(
    method="M0_NoFeedback",  # or M1/M2/M3
    sid="100243_9fb796fe_0005",
    nid="neg_01",
    layer="TypeA",
    out_dir=Path("experiments/phase2b_m0m3/M0_NoFeedback/100243_9fb796fe_0005/neg_01"),
    initial_script=Path("data/phase3_triplets/100243_9fb796fe_0005__neg_01/code_perturbed.py").read_text(),
)
```