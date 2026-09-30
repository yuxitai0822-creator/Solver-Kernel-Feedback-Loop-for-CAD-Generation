# CHANGELOG — cgvm/pipeline

## v0.2 (2026-09-30) — Module rename + 5-subdir restructure
- Renamed from `cad_verification/pipeline.py` + `cad_runtime/executor.py` → `cgvm/pipeline/{core,runtime}/verification,executor`
- Reorganized into `schema/` + `core/` + `runtime/` + `tests/` + `legacy/` structure
- 4 子状态 contract 与诊断 schema 归入 `schema/current.txt`
- 旧顶层 `cad_runtime/` + `cad_verification/pipeline.py` 删除

## v0.1 (original)
- `cad_verification/pipeline.py::PipelineVerification` (158 行) + `cad_runtime/executor.py::execute_cad_script()` (239 行)