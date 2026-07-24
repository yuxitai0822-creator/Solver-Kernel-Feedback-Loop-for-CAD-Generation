"""cad_verification/_base.py — Shared dataclasses for the
Verification Object framework.

A ``VerificationResult`` is the unit of output for every
Verification Object (pipeline / solver / kernel).  The same shape is
used regardless of which verification produced it, so the orchestrator
can treat them uniformly when filtering what to feed back to the LLM.

Three channels are always computed (when possible) by the orchestrator;
the ``method_policy.METHOD_FEEDBACK_CHANNELS`` dict decides which of
the three ``diagnostic`` fields are included in the next iteration's
prompt.  The ``full`` dict is always retained for offline analysis.

See ``experiments/phase2b_full/PHASE2B_FULL_REPORT.md`` §5 for the
unified Verification Object definition.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerificationResult:
    """Output of a single Verification Object.

    Attributes
    ----------
    name : str
        One of ``"pipeline"``, ``"solver"``, ``"kernel"``.
    passed : bool | None
        ``True``  → verification passed.
        ``False`` → verification failed.
        ``None``  → verification was skipped (e.g. missing artifact
                    upstream — script didn't compile, so KQP can't run).
    skipped : bool
        Convenience flag.  Always the same as ``passed is None``.
    diagnostic : dict
        Small, LLM-facing diagnostic.  Fed back to the LLM in the
        next iteration only if the method's feedback channel
        includes this verification.  Schema:

        * pipeline:  ``{stage, error_type, message, trace}``
        * solver:    ``{solver_status, dof, conflict_constraints,
                          redundant_constraints, severity}``
        * kernel:    ``{failed_queries: [{failed_query, target,
                          expected, actual, error, tolerance}]}``
    full : dict
        Complete record (always retained for offline analysis even
        when the diagnostic is hidden from the LLM).
    extras : dict
        Free-form extra metadata.  Currently used by the kernel
        verification to carry ``skipped_reason`` when it cannot
        run because the upstream STEP file does not exist.
    """

    name: str
    passed: bool | None
    diagnostic: dict = field(default_factory=dict)
    full: dict = field(default_factory=dict)
    skipped: bool = False
    extras: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.passed is None and not self.skipped:
            self.skipped = True
        elif self.passed is not None and self.skipped:
            # If caller explicitly set both, trust ``passed``.
            self.skipped = self.passed is None
