"""history2cq — History → CadQuery source code.

Re-exports the public API for back-compat with the old
``reconstruction_engine`` module.

Public API:
    compile_history              (core.compiler)
    execute_generated_code       (runtime.executor)
    reconstruct_sample           (runtime.orchestrator)
    reconstruct_batch            (runtime.orchestrator)
"""
from history2cq.core.compiler import compile_history
from history2cq.runtime.executor import execute_generated_code
from history2cq.runtime.orchestrator import reconstruct_sample, reconstruct_batch

__all__ = [
    "compile_history",
    "execute_generated_code",
    "reconstruct_sample",
    "reconstruct_batch",
]