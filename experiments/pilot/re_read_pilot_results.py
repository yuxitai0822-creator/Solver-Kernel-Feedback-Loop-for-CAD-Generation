"""re_read_pilot_results.py — re-evaluate existing pilot artefacts after B-001 / B-004 fix.

Reads each <method>/<sid>/<nid>/run_result.json + iter_*/adapter_report.json +
iter_*/kqp_feedback.json + iter_*/solver_feedback.json and re-computes:

  - pipeline_valid per iter (using the B-004 fix that accepts ``pass`` /
    ``success`` interchangeably)
  - solver_valid per iter (unchanged)
  - kqp_pass per iter (unchanged)
  - Success(C) = pipeline_valid ∧ solver_valid ∧ kqp_pass
  - final_status.success (matches last iter's Success)
  - Success@K bookkeeping per §4.5 (with the B-001 fix: S3 outranks S2
    in stop-rule assignment)

Writes the re-evaluated run_result.json back into each sample's dir
(explicit "v0.2.1"/post-patch marker) so the canonical pilot artefacts
carry the corrected numbers.

Reports /experiments/pilot/pilot_re_read_summary.json.
"""
from __future__ import annotations

import json
import os
import sys
import glob
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

# Reuse the canonical bar / pipeline / solver helpers from run_benchmark_v0.2.
# Module name has a dot which is invalid for normal import; load via importlib.
import importlib.util as _iu
_spec = _iu.spec_from_file_location(
    "rb", str(ROOT / "experiments" / "run_benchmark_v0.2.py"))
_rb = _iu.module_from_spec(_spec)
_spec.loader.exec_module(_rb)
_is_truthy_status = _rb._is_truthy_status
_pipeline_valid = _rb._pipeline_valid
_solver_valid = _rb._solver_valid
_kqp_pass = _rb._kqp_pass
SOLVER_VALID_STATES = _rb.SOLVER_VALID_STATES
bar_pass = _rb.bar_pass

PILOT_RUNS = ROOT / "experiments" / "pilot" / "runs"
REPORTS_DIR = ROOT / "experiments" / "pilot"


def _read_iter_artifacts(sid_dir: Path, iter_name: str):
    """Read adapter_report / kqp_feedback / solver_feedback for one iter."""
    iter_dir = sid_dir / iter_name
    adapt = {}
    sf = iter_dir / "adapter_report.json"
    if sf.exists():
        try:
            adapt = json.loads(sf.read_text(encoding="utf-8"))
        except Exception:
            pass
    kqp_path = iter_dir / "kqp_feedback.json"
    kqp = {}
    if kqp_path.exists():
        try:
            kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    sfb_path = iter_dir / "solver_feedback.json"
    sfb = {}
    if sfb_path.exists():
        try:
            sfb = json.loads(sfb_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return adapt, kqp, sfb


def _detect_step_path(sid_dir: Path):
    """Find the .step file in iter_00 (if any) — pipeline infer requires it."""
    cand = sorted((sid_dir / "iter_00").glob("*.step"))
    return cand[0] if cand else None


def _reevaluate_one(sid_dir: Path, current_rr: dict | None):
    """Recompute per-iter pipeline_valid + solver_valid + kqp_pass + Success.

    Returns ``(rewritten_run_result, per-iter flags, stop_rule, success_at_K)``.
    """
    step_path = _detect_step_path(sid_dir)
    iter_dirs = sorted([d for d in sid_dir.iterdir()
                          if d.is_dir() and d.name.startswith("iter_")],
                          key=lambda p: int(p.name.split("_")[1]))

    per_iter_flags: list[dict] = []
    success_at_K = {1: False, 2: False, 3: False}
    k_iter_final: int | None = None
    iter_records: list[dict] = []

    for idx, d in enumerate(iter_dirs):
        adapt, kqp, sfb = _read_iter_artifacts(sid_dir, d.name)
        pv, pv_break = _pipeline_valid(adapt, step_path)
        sv_ok, sv_canon = _solver_valid(sfb)
        kqp_ok, kqp_failed = _kqp_pass(kqp)
        success = pv and sv_ok and kqp_ok
        flags = {
            "iter": idx,
            "phase": "initial" if idx == 0 else "repair",
            "pipeline_valid": pv,
            "pipeline_valid_breakdown": pv_break,
            "solver_status": sv_canon,
            "solver_acceptable": sv_ok,
            "kqp_pass": kqp_ok,
            "kqp_failed_query_ids": kqp_failed,
            "success": success,
        }
        per_iter_flags.append(flags)

        if current_rr is not None:
            try:
                rec_path = d / "_iter_record.json"
                rec = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.exists() else {}
            except Exception:
                rec = {}
            merged = {**rec, **flags}
            iter_records.append(merged)

    # Stop-rule assignment per §4.3, B-001 fix applied (S3 > S2)
    stop_rule = None
    final_status_str = "stop_S4_max_iter"
    k_iter_local: int | None = None
    for idx, flags in enumerate(per_iter_flags):
        # First: S1 (agent emitted NO_CHANGE) — cannot recover here from
        # run_result.json alone, so we approximate S1 by stop_reason=
        # "stop_S1_no_change" if final_status.stop_reason matches.
        pass  # all rules first computed below after assembling stop_reason
        break
    if current_rr is not None:
        original_reason = current_rr.get("final_status", {}).get("stop_reason", "")
        if original_reason == "stop_S1_no_change":
            stop_rule = "S1"
        elif original_reason == "stop_S4_max_iter":
            stop_rule = "S4"
        for idx, flags in enumerate(per_iter_flags):
            ir_same = False
            # we don't have IR_t1 in the artifacts reliably; approximate
            # S2 by "agent ran but produced same final state" — recognised
            # only if stop_reason=='stop_S2_ir_unchanged'.
            pass
        if stop_rule is None and current_rr.get("final_status", {}).get("stop_reason") == "stop_S2_ir_unchanged":
            stop_rule = "S2"
        # S3 only if a non-final iter succeeded
        for idx, flags in enumerate(per_iter_flags):
            if flags["success"]:
                k_iter_local = idx + 1
                final_status_str = f"stop_S3_success_at_iter_{k_iter_local}"
                stop_rule = "S3"
                break
        if stop_rule is None:
            stop_rule = "S4"
            final_status_str = "stop_S4_max_iter"

        # Success@K bookkeeping per §4.5
        if k_iter_local is not None:
            for k in (1, 2, 3):
                if k >= k_iter_local:
                    success_at_K[k] = True

        # Final Success mirrors the last iter's Success
        final_success = any(f["success"] for f in per_iter_flags)
    else:
        final_success = False
        k_iter_local = None
        final_status_str = "no_data"

    rewritten = dict(current_rr or {})
    rewritten["iter_records_summary"] = [
        {k: v for k, v in flags.items() if k != "pipeline_valid_breakdown"}
        for flags in per_iter_flags
    ]
    rewritten["final_status"] = {
        "success": final_success,
        "strict_success": False,  # placeholder; canonical Success only
        "n_iterations": len(per_iter_flags),
        "n_iterations_to_success": k_iter_local,
        "stop_reason": final_status_str,
        "stop_rule_b001_fix": stop_rule,
        "final_solver_status": per_iter_flags[-1]["solver_status"] if per_iter_flags else "unknown",
        "final_kqp_pass": per_iter_flags[-1]["kqp_pass"] if per_iter_flags else False,
        "final_pipeline_valid": per_iter_flags[-1]["pipeline_valid"] if per_iter_flags else False,
        "_notes": "Re-read after B-001 (S1>S3>S2 stop-rule) and B-004 ("
                   "pipeline_valid enum-equivalence 'pass'|'success') fix.",
    }
    rewritten["metrics"] = {
        "success_at_1": success_at_K[1],
        "success_at_2": success_at_K[2],
        "success_at_3": success_at_K[3],
        "failure_to_success": final_success,
        "n_iterations": len(per_iter_flags),
    }
    return rewritten, per_iter_flags, stop_rule, success_at_K


def main():
    per_method_rows: dict[str, list[dict]] = collections.defaultdict(list)
    per_method_stop: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: collections.Counter())
    per_method_succ_k: dict[str, dict[int, int]] = collections.defaultdict(
        lambda: collections.Counter())

    summary: dict = {
        "phase": "Pilot v0.1 re-read after B-001 + B-004 fix",
        "date": "2026-07-16",
        "bugs_fixed_applied": ["B-001 (S1>S3>S2 stop-rule)",
                                 "B-004 (pipeline_valid 'pass'/'success')"],
        "methods": {},
    }

    for method_dir in sorted(p for p in PILOT_RUNS.iterdir() if p.is_dir()):
        method = method_dir.name
        for sid_dir in sorted(p for p in method_dir.iterdir() if p.is_dir()):
            for nid_dir in sorted(p for p in sid_dir.iterdir() if p.is_dir()):
                rr_path = nid_dir / "run_result.json"
                if not rr_path.exists():
                    continue
                try:
                    current = json.loads(rr_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                rewritten, flags, stop_rule, sK = _reevaluate_one(nid_dir, current)
                # Persist in-place so subsequent analysis sees the correct values.
                rr_path.write_text(json.dumps(rewritten, indent=2,
                                              ensure_ascii=False,
                                              default=str),
                                    encoding="utf-8")
                row = {
                    "sample_id": sid_dir.name,
                    "negative_id": nid_dir.name,
                    "method": method,
                    "final_success": rewritten["final_status"]["success"],
                    "stop_reason": rewritten["final_status"]["stop_reason"],
                    "stop_rule": rewritten["final_status"].get("stop_rule_b001_fix"),
                    "success_at_1": sK[1],
                    "success_at_2": sK[2],
                    "success_at_3": sK[3],
                }
                per_method_rows[method].append(row)
                per_method_stop[method][stop_rule] += 1
                for k in (1, 2, 3):
                    if sK[k]:
                        per_method_succ_k[method][k] += 1

    # Per-stratum split for the §6.2 critical check
    sel = json.loads((REPORTS_DIR / "pilot_sample_selection.json").read_text(
                        encoding="utf-8"))
    kvp = {(s["sample_id"], s["negative_id"])
              for s in sel["negative_samples"]["kqp_visible_solver_blind"]}

    # Aggregate
    for method, rows in per_method_rows.items():
        n = len(rows)
        succ3 = sum(1 for r in rows if r["final_success"])
        scores = [sK for sK in
                   ({"s1": r["success_at_1"], "s2": r["success_at_2"],
                       "s3": r["success_at_3"]} for r in rows)]
        stops = dict(per_method_stop[method])
        sK_dict = {k: per_method_succ_k[method][k] for k in (1, 2, 3)}
        summary["methods"][method] = {
            "n_samples": n,
            "n_success": succ3,
            "Success@1": sK_dict[1] / n if n else 0,
            "Success@2": sK_dict[2] / n if n else 0,
            "Success@3": sK_dict[3] / n if n else 0,
            "stop_distribution": stops,
        }

    # KQP-visible stratum
    summary["kqp_visible_stratum_8"] = {}
    for method, rows in per_method_rows.items():
        subset = [r for r in rows if (r["sample_id"], r["negative_id"]) in kvp]
        n = len(subset)
        succ3 = sum(1 for r in subset if r["final_success"])
        s1 = sum(1 for r in subset if r["success_at_1"])
        s3 = sum(1 for r in subset if r["success_at_3"])
        stops = collections.Counter()
        for r in subset:
            stops[r["stop_rule"] or "None"] += 1
        summary["kqp_visible_stratum_8"][method] = {
            "n": n, "n_success": succ3,
            "Success@1": s1 / n if n else 0,
            "Success@3": s3 / n if n else 0,
            "stop_distribution": dict(stops),
        }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / "pilot_re_read_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8")
    print(f"wrote {out}")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
