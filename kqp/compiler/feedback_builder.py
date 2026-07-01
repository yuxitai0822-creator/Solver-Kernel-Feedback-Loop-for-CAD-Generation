"""feedback_builder.py — Generate feedback_template strings.

All templates must contain an actual-value marker so LLM can see what kernel
observed. Accepted markers: {actual}, 'got X', 'actual=X', 'actual: X'.

Convention: short, action-agnostic templates. Earlier hand-written batches
(batches 1-2) had verbose templates with explicit 'tolerance X' suffix and
'check extrusion was complete' hint, but batches 3+ use short ones. Compiler
emits the short form for consistency.
"""
from __future__ import annotations


class FeedbackBuilder:
    """Build feedback_template strings deterministically."""

    @staticmethod
    def body_count(expected: int = 1) -> str:
        return f"Expected body_count={expected}, got {{actual}}."

    @staticmethod
    def bbox_size(axis: str, expected: float, *, extra: str = "") -> str:
        """E.g. 'Expected bbox u-size 19.0mm, got {actual}mm.' or with extra.

        extra: optional inline note, e.g. '(2*r)' or '(negative extrude)'.
        """
        return f"Expected bbox {axis}-size {expected}mm{extra}, got {{actual}}mm."

    @staticmethod
    def cylinder_radius(expected: float, *, role: str = "") -> str:
        if role == "outer":
            return f"Expected outer cylinder radius {expected}mm, got {{actual}}mm."
        if role == "inner":
            return f"Expected inner cylinder radius {expected}mm, got {{actual}}mm."
        return f"Expected cylinder radius {expected}mm, got {{actual}}mm."

    @staticmethod
    def through_void_count(expected: int, *, hint: str = "") -> str:
        if hint:
            return f"Expected {expected} through-void{suffix(expected)}, got {{actual}}."
        return f"Expected {expected} through-void(s), got {{actual}}."

    @staticmethod
    def is_solid() -> str:
        return "Body is not a closed solid. got {actual}."

    @staticmethod
    def occt_valid() -> str:
        return "OCCT validation failed. got {actual}."

    @staticmethod
    def symmetric_about_plane() -> str:
        return "Body is not symmetric about sketch plane (centroid not on plane). got {actual}."


def suffix(n: int) -> str:
    """E.g. '1 through-void', '2 through-voids'."""
    return "" if n == 1 else "s"
