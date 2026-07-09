"""run_validation.py — Run validator over all IR examples and produce schema_validation_report.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
from validator import validate  # noqa: E402

EXAMPLES_DIR = ROOT / "cad_ir" / "samples" / "manual_ir_examples"
REPORT_PATH = ROOT / "cad_ir" / "reports" / "schema_validation_report.json"


def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    files = sorted(EXAMPLES_DIR.glob("*.cad_ir.json"))
    for f in files:
        try:
            ir = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            rows.append({"file": f.name, "parse_error": str(e),
                          "schema_status": "fail", "semantic_status": "fail",
                          "overall": "fail"})
            continue
        result = validate(ir)
        rows.append({
            "file": f.name,
            "sample_id": ir.get("sample_id"),
            "op_count": len(ir.get("operations", [])),
            "schema_status": result["schema_status"],
            "semantic_status": result["semantic_status"],
            "overall": result["overall"],
            "schema_issue_count": len(result["schema_issues"]),
            "semantic_issue_count": len(result["semantic_issues"]),
            "schema_issues": result["schema_issues"][:3],
            "semantic_issues": result["semantic_issues"][:3],
        })

    summary = {
        "phase": "Phase 1 — Schema validation",
        "backend": "cad_ir_v0.1 (JSON Schema + semantic)",
        "total_examples": len(files),
        "schema_pass_count": sum(1 for r in rows if r["schema_status"] == "pass"),
        "semantic_pass_count": sum(1 for r in rows
                                      if r["semantic_status"] == "pass"),
        "overall_pass_count": sum(1 for r in rows if r["overall"] == "pass"),
        "schema_pass_rate": (sum(1 for r in rows if r["schema_status"] == "pass")
                              / max(1, len(rows))),
        "semantic_pass_rate": (sum(1 for r in rows
                                    if r["semantic_status"] == "pass")
                                / max(1, len(rows))),
        "rows": rows,
    }

    REPORT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"},
                       indent=2, ensure_ascii=False))
    print(f"\nTotal: {summary['total_examples']}  "
          f"schema pass: {summary['schema_pass_count']}  "
          f"semantic pass: {summary['semantic_pass_count']}")


if __name__ == "__main__":
    main()