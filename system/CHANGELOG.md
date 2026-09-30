# CHANGELOG — system

## v0.2 (2026-09-30) — Module rename + 5-subdir restructure
- Renamed from `trial_iteration.py` + `method_policy.py` + `p2b_m0m3_on_frozen.py` + `cad_agent/` → `system/{core,policy,batch,agent}/`
- Reorganized into `core/` + `policy/` + `batch/` + `agent/` + `tests/` + `legacy/` structure
- 4-system feedback channels 与 policy 重写为 `system.policy.policy`
- `cad_repair_loop/` 整目录平移至 `system/legacy/cad_repair_loop/`（前世 IR-based 系统，不进 M0-M3）

## v0.1 (original)
- `trial_iteration.py::run(method, sid, nid, layer, out_dir, initial_script)` iter loop
- `method_policy.py::METHOD_FEEDBACK_CHANNELS` M0/M1/M2/M3 channel 声明
- `p2b_m0m3_on_frozen.py::main()` 480 trial batch runner
- `cad_agent/agent_v2.py::call_cad_agent` DeepSeek backend (v0 → v2)
- `cad_agent/prompt_builder_v2.py::build_prompt_v2` M0-M3 iterative prompt