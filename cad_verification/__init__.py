"""cad_verification — Verification Object framework for the M0-M3
iterative agentic system.

Three Verification Objects share a uniform interface
(``VerificationResult``) and are decoupled from feedback.  The
runner always invokes all three (when their inputs are available);
the per-method ``method_policy.METHOD_FEEDBACK_CHANNELS`` dict
decides which diagnostics are copied into the next iteration's
prompt.

Per the spec, the verification objects are:

* ``PipelineVerification`` — compile + execute + STEP export + OCCT
  load of the LLM-emitted cadquery script.
* ``SolverVerification`` — sketch constraints are solvable, no
  conflict, not over-constrained.  Reads a Fusion360 history JSON
  from disk and runs FreeCAD Sketcher.
* ``KernelVerification`` — design intent vs. actual geometry, via the
  pre-computed KQP instances.  Does NOT regenerate KQP at runtime.

See ``experiments/phase2b_full/PHASE2B_FULL_REPORT.md`` §5 for the
unified Verification Object definition and §4 for the per-method
feedback exposure rules.
"""
from __future__ import annotations

from cad_verification._base import VerificationResult
from cad_verification.pipeline import PipelineVerification
from cad_verification.solver import SolverVerification
from cad_verification.kernel import KernelVerification

__all__ = [
    "VerificationResult",
    "PipelineVerification",
    "SolverVerification",
    "KernelVerification",
]
