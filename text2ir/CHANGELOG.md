# CHANGELOG — text2ir

## v0.1 (2026-09-28) — Module rename + 5-subdir restructure
- Renamed from `cad_ir/` → `text2ir/`
- Reorganized into `core/adaptor/` + `core/validator/` + `tests/` + `legacy/`
- Schemas consolidated into `schema/current.json`

## v0.1-schema (original)
- `cad_ir_schema_v0.1.json` frozen
- 11 种 op_type：sketch_rectangle/circle/annulus/rectangular_frame/stadium/polygon, extrude/cut/join/add_constraint/set_dimension/export_step
- Semantic validation：positive dims / annulus inner<outer / polygon ≥3 vertices 等

## Phase 2A 后状态
- LLM agent 改走 direct CadQuery 输出，CAD IR 转为受控编辑接口
- schema v0.1 仍保留作 validation 工具