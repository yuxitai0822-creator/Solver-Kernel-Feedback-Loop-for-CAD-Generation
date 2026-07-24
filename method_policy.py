"""method_policy.py — M0-M3 feedback-channel policy.

Per the spec (§4.1-4.4), the four experiment groups differ ONLY in
which verification diagnostics are exposed to the LLM in the next
iteration.  All four groups run the same three Verification Objects
(pipeline / solver / kernel); the policy below is the single source
of truth for which of those diagnostics are copied into the prompt.

Verification-vs-feedback decoupling is the key invariant: even when
a verification is "not exposed" to the LLM, the runner still
computes and stores it.  This lets us (a) compute the real KQP /
solver / pipeline pass rate for every method, and (b) attribute
"self-correction" outcomes in M0 / M1 / M2 to the absence of
feedback rather than the absence of measurement.
"""
from __future__ import annotations

# Per-method feedback-channel set.  M0 / M1 / M2 / M3 are deliberately
# declared as plain string labels so the runner can use them as
# directory names; the set on the right is consumed by the trial
# loop to filter iteration history before it goes into the prompt.
METHOD_FEEDBACK_CHANNELS: dict[str, set[str]] = {
    "M0_NoFeedback":  {"pipeline"},
    "M1_SolverOnly":  {"pipeline", "solver"},
    "M2_KQPOnly":     {"pipeline", "kernel"},
    "M3_SolverKQP":   {"pipeline", "solver", "kernel"},
}

# Iteration cap per spec §4.1-4.4.  The trial loop terminates on
# (a) all 3 verifications passing, (b) the LLM emitting no_change, or
# (c) reaching MAX_ITERATIONS.
MAX_ITERATIONS: int = 3

# Stable order for directory iteration / result aggregation.  The
# orchestrator iterates methods in this order.
METHODS_IN_ORDER: tuple[str, ...] = (
    "M0_NoFeedback",
    "M1_SolverOnly",
    "M2_KQPOnly",
    "M3_SolverKQP",
)

# Canonical verification names — kept in sync with the NAME class
# attribute on each Verification Object.
VERIFICATION_NAMES: tuple[str, ...] = ("pipeline", "solver", "kernel")


def is_valid_method(method: str) -> bool:
    """True iff ``method`` is one of the four declared experiment groups."""
    return method in METHOD_FEEDBACK_CHANNELS


def feedback_channels_for(method: str) -> set[str]:
    """The set of verification channels the LLM may see for ``method``.

    Always returns a copy — callers may mutate without affecting
    other parts of the system.
    """
    if method not in METHOD_FEEDBACK_CHANNELS:
        raise KeyError(
            f"Unknown method {method!r}.  Known: {sorted(METHOD_FEEDBACK_CHANNELS)}"
        )
    return set(METHOD_FEEDBACK_CHANNELS[method])
