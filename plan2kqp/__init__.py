"""plan2kqp — DesignPlan → KQP (compile + dispatch).

Re-exports the public API for back-compat with the old ``kqp`` module.

Public API:
    compile_one, compile_batch     (core.compiler.compiler)
    dispatch_query                 (core.dispatch.dispatcher)
    load_step                      (core.dispatch.step_loader)
"""
from plan2kqp.core.compiler.compiler import compile_one, compile_batch
from plan2kqp.core.dispatch.dispatcher import dispatch_query
from plan2kqp.core.dispatch.step_loader import load_step

__all__ = [
    "compile_one",
    "compile_batch",
    "dispatch_query",
    "load_step",
]