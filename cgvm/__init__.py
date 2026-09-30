"""cgvm — 3 个 CAD Generation Verification Module.

Re-exports the 3 CGVM verification classes plus the shared dataclass,
so callers can simply:

    from cgvm import PipelineVerification, SolverVerification, KernelVerification, VerificationResult
"""
from cgvm._shared.base import VerificationResult
from cgvm.pipeline.core.verification import PipelineVerification
from cgvm.solver.core.verification import SolverVerification
from cgvm.kernel.core.verification import KernelVerification

__all__ = [
    "VerificationResult",
    "PipelineVerification",
    "SolverVerification",
    "KernelVerification",
]