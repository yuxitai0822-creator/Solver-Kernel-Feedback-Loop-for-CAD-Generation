# CHANGELOG — plan2kqp

## v0.2 (2026-09-28) — Module rename + 5-subdir restructure
- Renamed from `kqp/` → `plan2kqp/`
- Reorganized into `core/compiler/` + `core/dispatch/` + `runtime/` + `tests/` + `legacy/`
- Schemas consolidated into `schema/current.txt` + `schema/archive/v0.1.txt`
- Frozen v0.1 snapshots moved to `legacy/_FROZEN/`

## Schema history

| 版本 | 文件 | 状态 |
|---|---|---|
| v0.1 | `archive/v0.1.txt` | archived（与 v0.2 字段定义大致相同，仅 bugfix） |
| v0.2 | `current.txt` | **current** |

## v0.1 (2026-07) — Original release
- `compiler/compile_kqp.py` Plan → KQP instance
- `runner/run_kqp.py` CLI 入口
- `runner/query_dispatcher.py` 7 intent dispatch
- `runner/geometry_backend.py` OCCT 调用