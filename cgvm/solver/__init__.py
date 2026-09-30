"""cgvm.solver — Solver CGVM.

Re-exports:
    SolverVerification                       (cgvm.solver.core.verification)
    ACCEPTABLE_STATUSES, BLOCKING_STATUSES  (cgvm.solver.core.verification)
    build_solver_feedback                    (cgvm.solver.runtime.freecad.pipeline — default FreeCAD backend)
"""
from cgvm.solver.core.verification import (
    SolverVerification,
    ACCEPTABLE_STATUSES,
    BLOCKING_STATUSES,
)
from cgvm.solver.runtime.freecad.pipeline import build_solver_feedback

__all__ = [
    "SolverVerification",
    "ACCEPTABLE_STATUSES",
    "BLOCKING_STATUSES",
    "build_solver_feedback",
]