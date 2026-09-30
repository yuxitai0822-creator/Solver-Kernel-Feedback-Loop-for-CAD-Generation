"""dataset — Triplet dataset construction for the M0-M3 perturbation experiment.

Composes ``Edit-code pairs``: ``(Code_gt, Code_perturbed, T_ref)`` plus
optional KQP-delta + chamfer-distance metrics.  See
``dataset/build_triplets.py`` for the entry point and
``experiments/phase2b_full/PHASE2B_FULL_REPORT.md`` §6 for the
overall design rationale.
"""
