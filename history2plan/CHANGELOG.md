# CHANGELOG — history2plan

## v0.2 (2026-09-28) — Module rename + 5-subdir restructure
- Renamed from `DesignPlan/` → `history2plan/`
- Reorganized into `core/` + `runtime/` + `tests/` + `legacy/` structure
- Schemas consolidated into `schema/current.txt` + `schema/archive/schema0[1-4].txt`
- Analysis scripts → `tests/analysis/`, smoke scripts → `tests/smoke/`

## Schema history

| 版本 | 文件 | 状态 |
|---|---|---|
| schema01 | `archive/schema01.txt` | archived |
| schema02 | `archive/schema02.txt` | archived |
| schema03 | `archive/schema03.txt` | archived |
| schema04 | `archive/schema04.txt` | archived |
| schema05 | `current.txt` | **current** |

## v0.1 (2026-07) — Original release
- `design_plan_compiler.py` 6 阶段编译：parse → dep graph → profile → dimensions → extrude → frame