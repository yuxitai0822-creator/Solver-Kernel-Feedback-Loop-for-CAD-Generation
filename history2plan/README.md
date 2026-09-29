# history2plan — History → DesignPlan

模态转换模块：**Fusion360 history JSON → DesignPlan JSON (v0.6 frozen)**。

## 目录结构

```
history2plan/
├── README.md
├── __init__.py                # 公开 API
├── CHANGELOG.md               # schema v0.1→v0.5 演进
│
├── schema/                    # DesignPlan schema
│   ├── current.txt            # 当前版本（原 DesignPlan_schema05.txt）
│   └── archive/
│           ├── schema01.txt
│           ├── schema02.txt
│           ├── schema03.txt
│           └── schema04.txt
│
├── core/
│   └── compiler.py            # history → DesignPlan（确定性 6 阶段编译）
│
├── runtime/
│   ├── batch_runner.py        # 原 run_all_50.py（统一 batch 运行入口）
│   └── comparison_report.json
│
├── tests/
│   ├── analysis/
│   │   ├── compare_compiler_vs_handwritten.py
│   │   ├── freeze_assessment.py
│   │   ├── freeze_summary.py
│   │   └── kqp_field_inventory.py
│   └── smoke/
│       ├── run_test_21_30.py
│       ├── run_test_31_40.py
│       └── run_test_41_50.py
│
└── legacy/                    # 停用代码 + 旧数据
    ├── _FROZEN/
    │   └── compiler_v0.6_FROZEN.py
    ├── samples/               # 原 DesignPlan/samples/（v1..v6 历史样本）
    ├── kqp_field_inventory/   # 原 DesignPlan/compiler/kqp_field_inventory/（旧 aggregate）
    ├── out/                   # 原 DesignPlan/compiler/out/
    ├── out_v5/ out_v6/
    ├── comparison_report.json
    └── comparison_report_v5.json
```

## 公开 API

```python
from history2plan.core.compiler import compile_design_plan
```

## 上下游

- **上游**：Fusion360 history JSON（`data/phase0_initial/history/<sid>.json`）
- **下游**：
  - `data/phase1_positive/design_plan/instances/<sid>.design_plan.json` — 编译产物
  - `plan2kqp.core.compiler.compiler.compile_one` — 读取 DesignPlan 编译 KQP

## 旧名映射

| 旧（已删除） | 新 |
|---|---|
| `DesignPlan.compiler.design_plan_compiler.compile_design_plan` | `history2plan.core.compiler.compile_design_plan` |
| `DesignPlan.compiler.run_all_50` | `history2plan.runtime.batch_runner` |