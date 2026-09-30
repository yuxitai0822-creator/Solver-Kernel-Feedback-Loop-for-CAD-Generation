# system/agent/ — LLM caller + prompt builder

| 文件/目录 | 作用 |
|---|---|
| `schema.py` | 原 `cad_agent/schema.py`：`is_valid_output(obj)`、`make_no_change(reason)`、`make_repair(script, ops, notes, reasoning)`、`ALLOWED_OPERATIONS` |
| `core/caller.py` | 原 `cad_agent/agent_v2.py`，DeepSeek backend（含 `_bypass_dead_proxy()`、retry + jitter、`ThreadPoolExecutor` hard timeout 90s） |
| `prompt/builder.py` | 原 `cad_agent/prompt_builder_v2.py`，M0-M3 实际用的 iterative prompt builder（`_fmt_iter_history`、`_fmt_design_plan` 等） |
| `prompt/legacy_shim.py` | 原 `cad_agent/prompt_builder.py`，v0 single-shot shim（v0 ↔ v2 路由分发） |
| `legacy/agent_zhipu.py` | 原 `cad_agent/agent.py`，ZHIPU backend（legacy） |
| `legacy/agent_v0.1_FROZEN.py` | ZHIPU backend 的 frozen snapshot |
| `legacy/prompt_builder_v0.1_FROZEN.py` | v0 prompt builder frozen snapshot |
| `legacy/schema_v0.1_FROZEN.py` | v0 schema frozen snapshot |

## 公开 API

```python
from system.agent import (
    call_cad_agent,        # alias for call_cad_agent_v2 (DeepSeek)
    call_cad_agent_v2,     # DeepSeek backend (M0-M3 default)
    build_prompt,         # v2/v0 路由分发
    build_prompt_v2,      # v2 iterative prompt (M0-M3 actual)
    is_valid_output,
    make_no_change,
    make_repair,
    ALLOWED_OPERATIONS,
)
```

## 上下游

- **被消费**：`system/core/iter_loop.py` 调用 `call_cad_agent_v2` 与 `build_prompt`
- **依赖**：DeepSeek API（`DEEPSEEK_BASE_URL` 常量在 `system/agent/core/caller.py`）

## Legacy（不属于 M0-M3）

`system/agent/legacy/` 4 个文件是前世 ZHIPU backend 的快照，仅供考古，不参与 benchmark。如有需要，`legacy_shim.py` 会路由到 v0 单轮 prompt（`feedback is None` 时走 v0 模板）。