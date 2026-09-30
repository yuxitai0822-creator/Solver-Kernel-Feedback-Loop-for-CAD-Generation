"""system.agent.prompt — v2 prompt builder + v0 legacy shim."""
from system.agent.prompt.builder import build_prompt_v2 as build_prompt
from system.agent.prompt.legacy_shim import build_prompt as build_prompt_v0

__all__ = ["build_prompt", "build_prompt_v2", "build_prompt_v0"]