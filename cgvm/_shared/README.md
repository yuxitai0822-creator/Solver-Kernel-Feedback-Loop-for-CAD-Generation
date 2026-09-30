# cgvm/_shared/

3 个 CGVM 模块共用的唯一类型。

## 内容

- `base.py`（原 `cad_verification/_base.py`）—— `@dataclass VerificationResult(name, passed, diagnostic, full, skipped, extras)`，是 Pipeline / Solver / Kernel 三个 Verification Object 的统一输出 schema。

## 设计说明

3 个 CGVM 类（Pipeline / Solver / Kernel）**不继承同一基类**，仅通过 duck-typed `run()` → `VerificationResult` 接口对齐。`method_policy.METHOD_FEEDBACK_CHANNELS`（位于 `system/policy/policy.py`）按 `name` 决定哪些 `diagnostic` 字段被喂回 LLM。