# CHANGELOG — cgvm/solver

## v0.2 (2026-09-30) — Module rename + 5-subdir restructure
- Renamed from `cad_verification/solver.py` + `Freecadsolver_feedback/` + `Kiwisolver_feedback/` → `cgvm/solver/{core,runtime/{freecad,kiwisolver}}`
- Reorganized into `schema/` + `core/` + `runtime/` + `tests/` + `legacy/` structure
- FreeCAD 后端保持为默认 runtime；Kiwisolver 后端标记为 archived（不参与 M0-M3 benchmark）
- `Freecadsolver_feedback/api_probe/` 整体作为 legacy/api_probe/

## v0.1 (original)
- `cad_verification/solver.py::SolverVerification` (195 行) 接口 + `Freecadsolver_feedback/core/` (9 文件) FreeCAD 后端 + `Kiwisolver_feedback/core/` (9 文件) Kiwisolver 后端