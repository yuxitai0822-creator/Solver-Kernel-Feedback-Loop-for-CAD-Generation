"""text2ir — CAD IR (v0.1 frozen) + adapt/validate.

Re-exports the public API for back-compat with the old ``cad_ir`` module.

Public API:
    validate, validate_file      (core.validator.validator)
    adapt_file                   (core.adaptor.adapter)
"""
from text2ir.core.validator.validator import validate, validate_file
from text2ir.core.adaptor.adapter import adapt_file

__all__ = ["validate", "validate_file", "adapt_file"]