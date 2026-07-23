"""cad_agent — LLM CAD Agent (Phase 2A Task A1.3).

Exports:
  call_cad_agent(design_plan, current_script, out_dir) -> dict
  build_prompt(design_plan, current_script, out_dir) -> str
  is_valid_output(obj) -> (bool, error)
  make_no_change(reason) -> dict
  make_repair(script, operations_declared, notes) -> dict
"""
from .agent import call_cad_agent
from .prompt_builder import build_prompt
from . import schema

__all__ = ["call_cad_agent", "build_prompt", "is_valid_output",
           "make_no_change", "make_repair"]
