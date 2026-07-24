"""cad_verification/kernel.py — Kernel Verification Object.

Reads a pre-computed KQP instance from disk and evaluates every query
against the STEP the LLM just produced.  Per §5.2 of the spec:

    Kernel verification target:
        dimension / topology / spatial relation / derived geometry.

    Method:
        Design Plan → KQP instance (on disk) → OCCT geometry query →
        expected-vs-actual comparison.

    Success:
        Sample-level:  all required queries pass.
        Query-level:  abs(actual - expected) <= tolerance.

    Diagnostic:
        {"failed_queries": [{
            "failed_query": "bbox_size",
            "target":       "u" | "v" | "w" | "outer" | "inner" | "count" | "solid" | "valid" | ...,
            "expected":     <value>,
            "actual":       <value>,
            "error":        <abs diff>,
            "tolerance":    <value>
        }, ...]}

The KQP is **not** regenerated at runtime — we read the existing
``kqp/outputs/compiler_v0.2/<sid>.kqp_instance.json``.  A single KQP
is shared by every perturbed sample of the same source design plan.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cad_verification._base import VerificationResult  # noqa: E402

# Lazy import — the OCP / OCCT bridge is heavy and only required when
# the runner actually invokes the kernel verification.
def _import_dispatcher():
    from kqp.runner import query_dispatcher  # type: ignore
    return query_dispatcher


# Supported KQP intents (mirrors the current dispatcher in
# kqp/runner/query_dispatcher.py).  If a new intent is added, extend
# this list.
SUPPORTED_INTENTS = {
    "body_count",
    "bbox_size",
    "cylinder_radius",
    "through_void_count",
    "is_solid",
    "occt_valid",
    "symmetric_about_plane",
}


# Per-intent default tolerance.  KQP instances carry their own
# per-query tolerance; this is only a safety net for missing fields.
DEFAULT_TOLERANCE = {
    "body_count":             0,
    "bbox_size":              0.05,
    "cylinder_radius":        0.01,
    "through_void_count":     0,
    "is_solid":               None,    # exact boolean
    "occt_valid":             None,
    "symmetric_about_plane":  None,
}


def _frame_from_design_plan(plan: dict) -> dict:
    """Pull the body-local frame out of the design plan.  Defaults to
    the identity frame (which is wrong for non-axis-aligned bodies —
    callers should pass a design plan that already has the correct
    frame)."""
    try:
        f = plan["solid_bodies"][0].get("frame", {})
    except (KeyError, IndexError, AttributeError):
        f = {}
    return {
        "u_dir": list(f.get("u_dir", [1, 0, 0])),
        "v_dir": list(f.get("v_dir", [0, 1, 0])),
        "w_dir": list(f.get("w_dir", [0, 0, 1])),
    }


def _load_step_shape(step_path: Path):
    """Load a STEP file into an OCCT TopoDS_Shape.

    Imported lazily so that importing this module on a Python without
    OCP installed does not crash.
    """
    from OCP.STEPControl import STEPControl_Reader
    r = STEPControl_Reader()
    r.ReadFile(str(step_path))
    r.TransferRoots()
    return r.OneShape()


def _intent_to_target(query: dict) -> str:
    """Map a KQP query to the LLM-facing target field.

    Per the spec diagnostic schema ``{failed_query, target, ...}`` —
    the ``target`` is the per-intent axis / dimension / selector.
    """
    intent = query.get("intent", "")
    if intent == "bbox_size":
        return query.get("axis", "?")
    if intent == "cylinder_radius":
        # Selector may be "outer" / "inner" / a uuid.
        return (query.get("params") or {}).get("selector", "?")
    if intent == "body_count":
        return "count"
    if intent == "through_void_count":
        return "count"
    if intent == "is_solid":
        return "solid"
    if intent == "occt_valid":
        return "valid"
    if intent == "symmetric_about_plane":
        return "plane"
    return "?"


class KernelVerification:
    """Kernel Verification Object.

    Reads the KQP instance from ``kqp_instance_path`` and runs every
    query (across all 7 supported intents) against the STEP file at
    ``step_path``.  Returns a pass/fail plus the per-query diagnostic
    shaped for the LLM.
    """

    NAME = "kernel"

    def run(
        self,
        step_path: Path | None,
        kqp_instance_path: Path,
        design_plan: dict,
    ) -> VerificationResult:
        if step_path is None or not Path(step_path).exists():
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": "step_path_missing",
                        "step_path": str(step_path)},
            )
        if not Path(kqp_instance_path).exists():
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": "kqp_missing",
                        "kqp_path": str(kqp_instance_path)},
            )
        try:
            kqp = json.loads(Path(kqp_instance_path).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            return VerificationResult(
                name=self.NAME,
                passed=None,
                diagnostic={},
                full={},
                extras={"skipped_reason": f"kqp_load_failed: {type(e).__name__}: {e}"},
            )

        queries = kqp.get("queries", [])
        if not queries:
            return VerificationResult(
                name=self.NAME,
                passed=False,
                diagnostic={"failed_queries": [],
                            "error_type": "kqp_empty",
                            "message": "KQP instance has no queries."},
                full={"n_queries": 0},
            )

        # Load STEP once; reuse for every query.
        try:
            shape = _load_step_shape(Path(step_path))
        except Exception as e:  # noqa: BLE001
            return VerificationResult(
                name=self.NAME,
                passed=False,
                diagnostic={
                    "failed_queries": [{
                        "failed_query": "occt_load",
                        "target": "valid",
                        "expected": True,
                        "actual": False,
                        "error": None,
                        "tolerance": None,
                    }],
                    "error_type": "occt_load_failed",
                    "message": f"{type(e).__name__}: {e}",
                },
                full={"occt_load_error": f"{type(e).__name__}: {e}"},
            )

        frame = _frame_from_design_plan(design_plan)
        qd = _import_dispatcher()
        passed_queries: list[dict] = []
        failed_queries: list[dict] = []
        error_queries: list[dict] = []
        full_results: list[dict] = []

        for q in queries:
            intent = q.get("intent")
            qid = q.get("id", "?")
            if intent not in SUPPORTED_INTENTS:
                full_results.append({"id": qid, "intent": intent, "skipped": "unsupported_intent"})
                continue
            try:
                r = qd.dispatch_query(shape, q, frame)
            except Exception as e:  # noqa: BLE001
                # Dispatcher crashed — record as a per-query error, keep going.
                err = {
                    "failed_query": intent,
                    "target": _intent_to_target(q),
                    "expected": q.get("expected"),
                    "actual": None,
                    "error": None,
                    "tolerance": q.get("tolerance", DEFAULT_TOLERANCE.get(intent)),
                    "exception": f"{type(e).__name__}: {e}",
                }
                error_queries.append(err)
                full_results.append({"id": qid, "intent": intent, "exception": str(e)})
                continue
            status = r.get("status")
            rec = {
                "id": qid,
                "intent": intent,
                "status": status,
                "expected": r.get("expected"),
                "actual": r.get("actual"),
                "error": r.get("error"),
                "tolerance": r.get("tolerance", q.get("tolerance", DEFAULT_TOLERANCE.get(intent))),
            }
            full_results.append(rec)
            if status == "pass":
                passed_queries.append(rec)
            elif status == "fail":
                failed_queries.append({
                    "failed_query": intent,
                    "target": _intent_to_target(q),
                    "expected": r.get("expected"),
                    "actual": r.get("actual"),
                    "error": r.get("error"),
                    "tolerance": r.get("tolerance"),
                    "query_id": qid,
                })
            else:
                # "error" / "unsupported" — record as error_queries
                error_queries.append({
                    "failed_query": intent,
                    "target": _intent_to_target(q),
                    "expected": r.get("expected"),
                    "actual": r.get("actual"),
                    "error": r.get("error"),
                    "tolerance": r.get("tolerance"),
                    "query_id": qid,
                    "status": status,
                })

        passed = (len(failed_queries) == 0 and len(error_queries) == 0)
        return VerificationResult(
            name=self.NAME,
            passed=passed,
            diagnostic={
                "failed_queries": failed_queries + error_queries,
                "error_type": "none" if passed else "kqp_query_failed",
                "message": (f"All {len(queries)} KQP queries passed."
                            if passed
                            else f"{len(failed_queries) + len(error_queries)} of "
                                 f"{len(queries)} KQP queries failed."),
            },
            full={
                "n_queries": len(queries),
                "n_pass":    len(passed_queries),
                "n_fail":    len(failed_queries),
                "n_error":   len(error_queries),
                "results":   full_results,
            },
        )
