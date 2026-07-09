"""run_adaptor.py — CLI entry to run the Deterministic Adaptor on a batch of IR examples.

Usage:
  python run_adaptor.py [examples_dir] [results_dir]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adaptor"))
from adapter import adapt_file  # noqa: E402


def main():
    examples_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        ROOT.parent / "cad_ir" / "samples" / "manual_ir_examples")
    results_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        ROOT.parent / "cad_ir" / "results")
    results_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(examples_dir.glob("*.cad_ir.json"))
    rows = []
    for f in files:
        out = results_dir / f.stem
        out.mkdir(exist_ok=True)
        try:
            rep = adapt_file(f, out)
        except Exception as e:
            rep = {"sample_id": f.stem,
                    "adapter_status": "fail",
                    "warnings": [f"adapter exception: {type(e).__name__}: {e}"]}
            (out / "adapter_report.json").write_text(
                json.dumps(rep, indent=2, ensure_ascii=False),
                encoding="utf-8")
        rows.append({"sample_id": f.stem,
                       "schema_check": rep.get("schema_check"),
                       "semantic_validation": rep.get("semantic_validation"),
                       "script_syntax_status": rep.get("script_syntax_status"),
                       "execution_status": rep.get("execution_status"),
                       "step_export_status": rep.get("step_export_status"),
                       "adapter_status": rep.get("adapter_status"),
                       "unsupported_ops": rep.get("unsupported_ops", []),
                       "warnings": rep.get("warnings", [])})

    summary = {
        "phase": "Phase 2 — Deterministic Adaptor",
        "backend": "cadquery 2.8.0 (cad_subproject1 env)",
        "total": len(rows),
        "schema_pass": sum(1 for r in rows if r["schema_check"] == "pass"),
        "semantic_pass": sum(1 for r in rows
                                 if r["semantic_validation"] == "pass"),
        "script_syntax_pass": sum(1 for r in rows
                                     if r["script_syntax_status"] == "pass"),
        "execution_pass": sum(1 for r in rows
                                 if r["execution_status"] == "pass"),
        "step_export_pass": sum(1 for r in rows
                                  if r["step_export_status"] == "pass"),
        "adapter_success": sum(1 for r in rows
                                  if r["adapter_status"] == "success"),
        "rows": rows,
    }
    summary["script_syntax_rate"] = summary["script_syntax_pass"] / max(1, summary["total"])
    summary["execution_rate"] = summary["execution_pass"] / max(1, summary["total"])
    summary["step_export_rate"] = summary["step_export_pass"] / max(1, summary["total"])
    summary["adapter_success_rate"] = summary["adapter_success"] / max(1, summary["total"])

    out_path = ROOT.parent / "cad_ir" / "reports" / "adaptor_run_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"},
                       indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()