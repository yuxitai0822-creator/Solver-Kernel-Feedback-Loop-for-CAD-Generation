# CHANGELOG — cgvm/kernel

## v0.2 (2026-09-30) — Module rename + 5-subdir restructure
- Renamed from `cad_verification/kernel.py` + `plan2kqp/core/dispatch/` → `cgvm/kernel/{core,runtime}/`
- Reorganized into `schema/` + `core/` + `runtime/` + `tests/` + `legacy/` structure
- 7 种 SUPPORTED_INTENTS 与 DEFAULT_TOLERANCE 保留在 `cgvm.kernel.core.verification`
- 旧 `plan2kqp/core/dispatch/dispatcher.py` 的 `sys.path.insert + import geometry_backend` 反模式清理为相对包导入

## v0.1 (original)
- `cad_verification/kernel.py::KernelVerification` (295 行) + `plan2kqp/core/dispatch/{dispatcher,geometry_backend,step_loader,result_builder}.py` (4 文件)