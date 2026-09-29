# text2ir — (Natural language text) → CAD IR

模态转换模块：**CAD IR (v0.1 frozen) → CadQuery code**（adaptor）+ **CAD IR 验证**（validator）。

> 模块名 `text2ir` 反映该模式的潜在用途（natural language → IR）。当前 v0.1 IR schema 已 frozen，Phase 2A 后该模式转向 legacy（实际流水线直接生成 CadQuery 脚本而不经过 IR），但模块仍保留作受控编辑接口。

## 目录结构

```
text2ir/
├── README.md
├── __init__.py                # 公开 API
├── CHANGELOG.md
│
├── schema/
│   ├── current.json           # 当前 IR schema（原 cad_ir_schema_v0.1.json）
│   └── archive/               # 暂时空
│
├── core/
│   ├── adaptor/               # IR → CadQuery code
│   │   ├── __init__.py
│   │   ├── adapter.py             # IR JSON → CadQuery Python source
│   │   ├── cadquery_backend.py    # op_type emit 逻辑
│   │   ├── trace_builder.py
│   │   └── run_adaptor.py         # batch CLI
│   └── validator/             # IR schema + semantic 验证
│       ├── __init__.py
│       ├── validator.py
│       └── run_validation.py     # batch CLI
│
├── runtime/                   # 目前 core/ 已含 I/O；本目录预留
│
├── tests/
│   └── samples/
│       └── generate_from_clean_samples.py
│
└── legacy/
    ├── reports/               # phase_1/2/4_repair_loop 等历史报告
    ├── .gitignore
    └── cad_ir_schema_v0.1_spec.md
```

## 公开 API

```python
from text2ir.core.validator.validator import validate, validate_file
from text2ir.core.adaptor.adapter import adapt_file
```

## 上下游

- **上游**：LLM emit IR JSON（`data/phase1_positive/cad_ir/instances/`）
- **下游**：
  - `cad_repair_loop/_adaptor_subprocess.py` 使用 adaptor
  - 当前 M0-M3 实验实际**不**使用 IR（直接 LLM emit CadQuery），仅 frozen schema + validator 保留作受控编辑接口

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `cad_ir.adaptor.adapter` | `text2ir.core.adaptor.adapter` |
| `cad_ir.validator.validator` | `text2ir.core.validator.validator` |
| `cad_ir.adaptor.run_adaptor` | `text2ir.core.adaptor.run_adaptor` |