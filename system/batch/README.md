# system/batch/ — batch runner

| 文件 | 作用 |
|---|---|
| `runner.py` | 原 `p2b_m0m3_on_frozen.py`，4-system 480 trial batch runner |

## 功能

- 读 `data/phase3_triplets/_frozen_manifest.json`
- 遍历 120 frozen (sid, nid) × 4 methods = **480 trials**
- 调 `system.core.iter_loop.run()` 单 trial iter loop
- 输出 `experiments/phase2b_m0m3/<method>/<sid>/<nid>/`
- 聚合 `pilot_results.json`
- **resume**：已有 `final_status ∈ {success, max_iter_exceeded, no_change, no_script}` 的跳过；`llm_error / runner_crash` 重试
- **atomic write**：tmp + `os.replace` 防中途崩溃
- **Defensive**：`except BaseException as e` 捕获所有错误，写 `runner_crash` record 而不让循环挂掉
- **Defensive proxy bypass**：`_bypass_dead_proxy()` 在 `import method_policy` 前清掉坏 proxy

## 公开 API

```python
from system.batch.runner import main as run_batch

run_batch(
    methods=None,        # 默认全部 4 个 method
    max_pairs=None,      # 截断前 N 个 (sid, nid)
    only_sid=None,        # 白名单 sid
)
```

## 上下游

- **输入**：`data/phase3_triplets/_frozen_manifest.json`（120 个 verified triplets 索引）
- **输出**：`experiments/phase2b_m0m3/pilot_results.json`（480 trial 聚合结果）+ 每 trial 一个 `iter_XX/` 子目录
- **被消费**：`dataset/m0m3_external_metrics.py`、`dataset/m0m3_significance.py`、`dataset/m0m3_analysis.py`