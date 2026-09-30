"""plan2kqp — DesignPlan → KQP (compile + dispatch).

Re-exports the public API for back-compat with the old ``kqp`` module.

NOTE: After Phase D, the dispatcher/loader/backend live under
``cgvm.kernel.runtime``. This shim re-exports the canonical names from
the new location for callers that still import via ``plan2kqp``.

Public API:
    compile_one, compile_batch     (now in cgvm.kernel.core.compiler)
    dispatch_query                 (now in cgvm.kernel.runtime.dispatcher)
    load_step                      (now in cgvm.kernel.runtime.step_loader)
"""
from plan2kqp.core.compiler.compiler import compile_one, compile_batch
from cgvm.kernel.runtime.dispatcher import dispatch_query
from cgvm.kernel.runtime.step_loader import load_step

__all__ = [
    "compile_one",
    "compile_batch",
    "dispatch_query",
    "load_step",
]
