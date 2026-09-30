"""system — 4-system iterative CAD generation (M0/M1/M2/M3 shared codebase).

Re-exports the policy declaration, the iter loop, the batch runner,
and the LLM agent + prompt builder entry points.
"""
from system.policy.policy import (
    METHOD_FEEDBACK_CHANNELS,
    MAX_ITERATIONS,
    METHODS_IN_ORDER,
    feedback_channels_for,
)
from system.core.iter_loop import run as run_iter
from system.batch.runner import main as run_batch
from system.agent.core.caller import call_cad_agent_v2

__all__ = [
    "METHOD_FEEDBACK_CHANNELS",
    "MAX_ITERATIONS",
    "METHODS_IN_ORDER",
    "feedback_channels_for",
    "run_iter",
    "run_batch",
    "call_cad_agent_v2",
]