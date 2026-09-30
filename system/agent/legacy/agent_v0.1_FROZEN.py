"""cad_agent/agent.py — LLM CAD Agent.

Phase 2A Task A1.3.  Receives a Design Plan and a current CAD script;
emits a strict-JSON contract (see schema.py) describing the next script
state.  Default backend:  ZHIPU glm-5.1 (same as the rest of the system).
Falls back to a deterministic stub if the API key is missing, so
end-to-end tests can run offline.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from . import schema
from .prompt_builder import build_prompt


# Match the canonical ZHIPU env var used by the rest of the project.
ZHIPU_API_KEY_ENV = "ZHIPU_API_KEY"
ZHIPU_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_DEFAULT_MODEL = "glm-5.1"


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        # Handle ```json ... ``` or ``` ... ```
        t = "\n".join(t.split("\n")[1:])
        if t.endswith("```"):
            t = "\n".join(t.split("\n")[:-1])
    return t.strip()


def call_cad_agent(design_plan: dict | str, current_script: str = "",
                     out_dir: str = "./out",
                     api_key: str | None = None,
                     model: str = ZHIPU_DEFAULT_MODEL,
                     timeout: int = 120) -> dict:
    """Call the LLM CAD Agent.

    Returns the validated contract dict (action='repair' or 'no_change').
    Raises ValueError if the LLM output is not a valid contract.
    """
    prompt = build_prompt(design_plan, current_script, out_dir)
    api_key = api_key or os.getenv(ZHIPU_API_KEY_ENV)
    if not api_key:
        # Offline stub: return NO_CHANGE so the loop can still progress.
        # A real LLM is required for repair; the test path uses this
        # to verify the surrounding plumbing.
        return schema.make_no_change(
            reason="no LLM API key set; returning NO_CHANGE for offline test"
        )
    import requests
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 4096,
        # Disable glm-5.1's default chain-of-thought; it burns the entire
        # token budget on `reasoning_content` and returns an empty
        # `content`.  See run_benchmark_v0.2.py for the same fix.
        "thinking": {"type": "disabled"},
    }
    r = requests.post(ZHIPU_ENDPOINT,
                       headers={"Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"},
                       json=payload, timeout=timeout)
    r.raise_for_status()
    body = r.json()
    text = body["choices"][0]["message"].get("content", "")
    if not text:
        # Treat empty content as NO_CHANGE (the model returned nothing
        # actionable; the loop can still stop).
        return schema.make_no_change(reason="LLM returned empty content")
    try:
        obj = json.loads(_strip_code_fence(text))
    except Exception as e:
        raise ValueError(f"CAD Agent output is not valid JSON: {e}\nraw: {text[:200]}")
    valid, err = schema.is_valid_output(obj)
    if not valid:
        raise ValueError(f"CAD Agent output invalid: {err}\nraw: {text[:200]}")
    return obj
