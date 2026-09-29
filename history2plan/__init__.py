"""history2plan — History → DesignPlan (v0.5 frozen).

Re-exports the public API for back-compat with the old ``DesignPlan``
module.

Public API:
    compile_design_plan            (core.compiler)
"""
from history2plan.core.compiler import compile_design_plan

__all__ = ["compile_design_plan"]