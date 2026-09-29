# CHANGELOG — history2cq

## v0.2 (2026-09-28) — Module rename + 5-subdir restructure
- Renamed from `reconstruction_engine/` → `history2cq/`
- Reorganized into `core/` + `runtime/` + `tests/` + `legacy/` structure
- Old module path `reconstruction_engine.compiler` etc. → removed (compat shim not provided; see plan)
- Frozen v0.1 snapshots moved to `legacy/_FROZEN/`

## v0.1 (2026-07) — Original release
- `compiler.py` deterministic history → CadQuery
- `executor.py` subprocess wrapper around CadQuery
- `orchestrator.py` compile → execute → occt_load pipeline
- `generate_index.py`, `export_clean_set.py`, `run_kqp_validation.py` batch runners