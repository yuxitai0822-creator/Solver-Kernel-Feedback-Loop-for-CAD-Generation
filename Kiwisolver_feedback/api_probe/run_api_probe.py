"""run_api_probe.py — Run all 6 api_probe scripts and collect raw outputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBES = [
    "probe_under_constrained.py",
    "probe_fully_constrained.py",
    "probe_redundant.py",
    "probe_conflicting.py",
    "probe_invalid_reference.py",
    "probe_recompute_failure.py",
]


def main():
    results = {}
    for script in PROBES:
        print(f"\n=== Running {script} ===")
        try:
            script_path = str(HERE / script)
            ns = {"__name__": "__main__", "__file__": script_path}
            exec((HERE / script).read_text(encoding="utf-8"), ns)
            results[script] = {"ok": True}
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            results[script] = {"ok": False, "error": str(e)}

    out = {
        "phase": "API Probe — solver_feedback v0.1 backend capability check",
        "backend": "kiwisolver + python adapter (FreeCAD Sketcher NOT available)",
        "scripts": results,
    }
    (HERE / "api_probe_summary.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print("\n=== Summary ===")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()