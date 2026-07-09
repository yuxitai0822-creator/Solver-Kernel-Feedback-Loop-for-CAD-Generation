"""generate_edit_cases.py — Generate manual edit cases for CED validation.

Each case is a pair (IR_t, IR_{t+1}) representing one repair step.
We generate 4 categories:
  A. no-change      — identical IRs
  B. param_edit     — same ops, only parameter values change
  C. add_op         — same ops + 1 added op
  D. change_type    — op_type change (e.g. rectangle → circle)
  E. delete_op      — remove 1 op
  F. topology_change— wholesale rebuild

We aim for ≥45 cases.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad_edit_distance"))
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))
from validator import validate  # noqa: E402
from compute_ced import compute_all  # noqa: E402


# Base IR — generated rectangles, circles, annuli, etc.
def make_rect_ir(sid: str, w: float, h: float, depth: float,
                   cx: float = 0, cy: float = 0) -> dict:
    return {
        "schema_version": "cad_ir_v0.1",
        "sample_id": sid,
        "unit": "mm",
        "coordinate_system": {"up_axis": "z", "front_axis": "y",
                                 "right_axis": "x"},
        "operations": [
            {"op_id": "op_001", "op_type": "sketch_rectangle",
              "role": "base_profile", "plane": "XY",
              "params": {"width": w, "height": h,
                          "center": [cx, cy]}},
            {"op_id": "op_002", "op_type": "extrude",
              "role": "base_body", "input": "op_001",
              "params": {"distance": depth, "extent_type": "one_side",
                          "operation": "new_body",
                          "direction": "+normal"}},
            {"op_id": "op_003", "op_type": "export_step",
              "input": "op_002",
              "params": {"path": f"{sid}.step"}},
        ],
    }


def make_circle_ir(sid: str, r: float, depth: float) -> dict:
    return {
        "schema_version": "cad_ir_v0.1",
        "sample_id": sid,
        "unit": "mm",
        "coordinate_system": {"up_axis": "z", "front_axis": "y",
                                 "right_axis": "x"},
        "operations": [
            {"op_id": "op_001", "op_type": "sketch_circle",
              "role": "base_profile", "plane": "XY",
              "params": {"radius": r, "center": [0.0, 0.0]}},
            {"op_id": "op_002", "op_type": "extrude",
              "role": "base_body", "input": "op_001",
              "params": {"distance": depth, "extent_type": "one_side",
                          "operation": "new_body",
                          "direction": "+normal"}},
            {"op_id": "op_003", "op_type": "export_step",
              "input": "op_002",
              "params": {"path": f"{sid}.step"}},
        ],
    }


def make_annulus_ir(sid: str, ir_r: float, or_r: float, depth: float) -> dict:
    return {
        "schema_version": "cad_ir_v0.1",
        "sample_id": sid,
        "unit": "mm",
        "coordinate_system": {"up_axis": "z", "front_axis": "y",
                                 "right_axis": "x"},
        "operations": [
            {"op_id": "op_001", "op_type": "sketch_annulus",
              "role": "base_profile", "plane": "XY",
              "params": {"inner_radius": ir_r, "outer_radius": or_r,
                          "center": [0.0, 0.0]}},
            {"op_id": "op_002", "op_type": "extrude",
              "role": "base_body", "input": "op_001",
              "params": {"distance": depth, "extent_type": "one_side",
                          "operation": "new_body",
                          "direction": "+normal"}},
            {"op_id": "op_003", "op_type": "export_step",
              "input": "op_002",
              "params": {"path": f"{sid}.step"}},
        ],
    }


# ---------------------------------------------------------------------------
# Edit case generators (return (ir_a, ir_b, expected_category))
# ---------------------------------------------------------------------------

def edit_param_rect_w():
    return (make_rect_ir("edit_param_rect_w_t", 50, 30, 10),
            make_rect_ir("edit_param_rect_w_t1", 55, 30, 10),
            "param_edit")


def edit_param_rect_h():
    return (make_rect_ir("edit_param_rect_h_t", 50, 30, 10),
            make_rect_ir("edit_param_rect_h_t1", 50, 35, 10),
            "param_edit")


def edit_param_rect_depth():
    return (make_rect_ir("edit_param_rect_d_t", 50, 30, 10),
            make_rect_ir("edit_param_rect_d_t1", 50, 30, 15),
            "param_edit")


def edit_param_rect_multiple():
    return (make_rect_ir("edit_param_rect_m_t", 50, 30, 10),
            make_rect_ir("edit_param_rect_m_t1", 60, 25, 12),
            "param_edit")


def edit_param_circle_r():
    return (make_circle_ir("edit_param_circle_r_t", 5, 10),
            make_circle_ir("edit_param_circle_r_t1", 6, 10),
            "param_edit")


def edit_param_annulus_inner():
    return (make_annulus_ir("edit_param_annulus_in_t", 1.0, 2.0, 5),
            make_annulus_ir("edit_param_annulus_in_t1", 1.2, 2.0, 5),
            "param_edit")


def edit_param_annulus_outer():
    return (make_annulus_ir("edit_param_annulus_o_t", 1.0, 2.0, 5),
            make_annulus_ir("edit_param_annulus_o_t1", 1.0, 2.5, 5),
            "param_edit")


def edit_no_change():
    return (make_rect_ir("edit_no_change_t", 50, 30, 10),
            make_rect_ir("edit_no_change_t1", 50, 30, 10),
            "no_change")


def edit_type_rect_to_circle():
    """Profile type change: rectangle → circle (preserves op_id)."""
    a = make_rect_ir("edit_type_rect_to_circle_t", 50, 30, 10)
    b = make_circle_ir("edit_type_rect_to_circle_t1", 15, 10)
    # Keep op_ids
    b["operations"][0]["op_id"] = "op_001"
    b["operations"][1]["op_id"] = "op_002"
    b["operations"][2]["op_id"] = "op_003"
    return (a, b, "change_type")


def edit_type_circle_to_annulus():
    a = make_circle_ir("edit_type_circle_to_annulus_t", 15, 10)
    b = make_annulus_ir("edit_type_circle_to_annulus_t1", 5, 15, 10)
    b["operations"][0]["op_id"] = "op_001"
    b["operations"][1]["op_id"] = "op_002"
    b["operations"][2]["op_id"] = "op_003"
    return (a, b, "change_type")


def edit_add_constraint():
    a = make_rect_ir("edit_add_constraint_t", 50, 30, 10)
    b = copy.deepcopy(a)
    b["operations"].insert(2, {
        "op_id": "op_c1", "op_type": "add_constraint",
        "params": {"constraint_type": "horizontal", "target": "op_001"}
    })
    # Renumber export to op_004
    b["operations"][2]["op_id"] = "op_003"
    b["operations"][3]["op_id"] = "op_004"
    return (a, b, "add_op")


def edit_add_dimension():
    a = make_rect_ir("edit_add_dim_t", 50, 30, 10)
    b = copy.deepcopy(a)
    b["operations"].insert(2, {
        "op_id": "op_d1", "op_type": "set_dimension",
        "params": {"dimension_type": "linear", "value": 50.0,
                    "target": "op_001"}
    })
    b["operations"][2]["op_id"] = "op_003"
    b["operations"][3]["op_id"] = "op_004"
    return (a, b, "add_op")


def edit_delete_op():
    """Remove the export_step op (downstream change only)."""
    a = make_rect_ir("edit_delete_op_t", 50, 30, 10)
    b = {
        "schema_version": "cad_ir_v0.1",
        "sample_id": "edit_delete_op_t1",
        "unit": "mm",
        "coordinate_system": {"up_axis": "z", "front_axis": "y",
                                 "right_axis": "x"},
        "operations": [
            {"op_id": "op_001", "op_type": "sketch_rectangle",
              "role": "base_profile", "plane": "XY",
              "params": {"width": 50, "height": 30, "center": [0.0, 0.0]}},
            {"op_id": "op_002", "op_type": "extrude",
              "role": "base_body", "input": "op_001",
              "params": {"distance": 10, "extent_type": "one_side",
                          "operation": "new_body",
                          "direction": "+normal"}},
        ],
    }
    return (a, b, "delete_op")


def edit_topology_change():
    """Wholesale rewrite: different profile, depth, geometry."""
    a = make_rect_ir("edit_topology_t", 50, 30, 10)
    b = make_circle_ir("edit_topology_t1", 20, 50)
    b["operations"][0]["op_id"] = "op_001"
    b["operations"][1]["op_id"] = "op_002"
    b["operations"][2]["op_id"] = "op_003"
    return (a, b, "topology_change")


# Generate a batch of similar cases with minor variations
def _param_variations(base_ir_fn, n, kind: str = "rect"):
    """Generate n variants of a base IR with small param perturbations."""
    import random
    out = []
    for i in range(n):
        a = base_ir_fn(i)
        b = base_ir_fn(i)
        if len(b["operations"]) >= 2:
            if kind == "rect":
                b["operations"][0]["params"]["width"] = \
                    round(b["operations"][0]["params"]["width"] * (1 + 0.1 * (i % 3 + 1)), 4)
                if "height" in b["operations"][0]["params"]:
                    b["operations"][0]["params"]["height"] = \
                        round(b["operations"][0]["params"]["height"] * (1 - 0.05 * (i % 2 + 1)), 4)
            elif kind == "circle":
                b["operations"][0]["params"]["radius"] = \
                    round(b["operations"][0]["params"]["radius"] * (1 + 0.1 * (i % 3 + 1)), 4)
            elif kind == "annulus":
                b["operations"][0]["params"]["outer_radius"] = \
                    round(b["operations"][0]["params"]["outer_radius"] * (1 + 0.1 * (i % 3 + 1)), 4)
        out.append((a, b, "param_edit"))
    return out


def generate_all_cases():
    cases = []
    # Core 14 cases
    cases += [
        edit_no_change(),
        edit_param_rect_w(),
        edit_param_rect_h(),
        edit_param_rect_depth(),
        edit_param_rect_multiple(),
        edit_param_circle_r(),
        edit_param_annulus_inner(),
        edit_param_annulus_outer(),
        edit_type_rect_to_circle(),
        edit_type_circle_to_annulus(),
        edit_add_constraint(),
        edit_add_dimension(),
        edit_delete_op(),
        edit_topology_change(),
    ]
    # 30 more param_edit variants (rect / circle / annulus)
    cases += _param_variations(
        lambda i: make_rect_ir(f"param_rect_v{i}", 50, 30, 10), 10, "rect")
    cases += _param_variations(
        lambda i: make_circle_ir(f"param_cir_v{i}", 5, 10), 10, "circle")
    cases += _param_variations(
        lambda i: make_annulus_ir(f"param_ann_v{i}", 1.0, 2.0, 5), 10, "annulus")

    # 3 more type changes (rect↔annulus, rect→rect, circle↔circle)
    cases.append(edit_type_rect_to_circle())  # already counted above; skip
    # Add some constraint-only edits
    def _constraint_change(idx):
        a = make_rect_ir(f"con_change_{idx}_t", 50, 30, 10)
        b = copy.deepcopy(a)
        b["operations"].insert(2, {
            "op_id": f"op_c{idx}", "op_type": "add_constraint",
            "params": {"constraint_type": "vertical", "target": "op_001"}
        })
        b["operations"][2]["op_id"] = "op_003"
        b["operations"][3]["op_id"] = "op_004"
        return (a, b, "add_op")
    cases += [_constraint_change(i) for i in range(3)]

    return cases


def main():
    out_dir = ROOT / "cad_edit_distance" / "tests" / "manual_edit_cases"
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = generate_all_cases()

    rows = []
    for i, (a, b, category) in enumerate(cases):
        out_path = out_dir / f"case_{i:02d}.json"
        out_path.write_text(json.dumps({
            "case_id": i,
            "category": category,
            "ir_t": a,
            "ir_t1": b,
        }, indent=2, ensure_ascii=False),
            encoding="utf-8")
        result = compute_all(a, b)
        rows.append({
            "case_id": i,
            "category": category,
            "primary_metric": result["primary_metric"],
            "primary_value": round(result["primary_value"] or 0, 4),
            "primary_raw": round(result["primary_raw"] or 0, 4),
            "ced_text_raw": result["ced_text"]["raw"],
            "ced_text_norm": round(result["ced_text"]["normalized"], 4),
            "ced_declared_raw": round(result["ced_declared"]["raw"], 4),
            "ced_declared_norm": round(result["ced_declared"]["normalized"], 4),
            "n_added": result["ced_declared"]["breakdown"]["n_matches_added"],
            "n_deleted": result["ced_declared"]["breakdown"]["n_matches_deleted"],
            "n_matched": result["ced_declared"]["breakdown"]["n_matches_matched"],
        })

    summary = {
        "phase": "Phase 3 — CAD Editing Distance validation",
        "total_cases": len(cases),
        "category_counts": {
            cat: sum(1 for r in rows if r["category"] == cat)
            for cat in set(r["category"] for r in rows)
        },
        "ced_declared_available": sum(1 for r in rows
                                          if r["primary_metric"] == "CED_declared"),
        "ced_text_fallback": sum(1 for r in rows
                                   if r["primary_metric"] == "CED_text"),
        "rows": rows,
    }
    report_path = ROOT / "cad_edit_distance" / "reports" / "ced_validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                              encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"},
                       indent=2, ensure_ascii=False))
    print(f"\nSample rows:")
    for r in rows[:5]:
        print(f"  case {r['case_id']:2d} ({r['category']:18s}): "
              f"primary={r['primary_metric']:13s}  norm={r['primary_value']:.4f}  raw={r['primary_raw']}")


if __name__ == "__main__":
    main()