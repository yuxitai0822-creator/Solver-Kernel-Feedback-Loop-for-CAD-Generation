"""llm_agent.py — LLM agent that emits cad_ir_v0.1 IR.

The agent takes a prompt built from:
  * Design Plan (target intent)
  * Previous IR_t (current attempt)
  * Solver Feedback (sketch constraint health)
  * KQP Feedback (final-geometry intent compliance)

and produces IR_{t+1}.

Backend: ZHIPU API glm-5.1 (per task spec §7.4).
  Base URL: https://open.bigmodel.cn/api/paas/v4/
  Model Name: glm-5.1
  API key: os.getenv('ZHIPU_API_KEY')

If the API key is not set or the call fails, we fall back to a
deterministic offline mode that produces simple parameter-only edits
suitable for smoke-testing the pipeline.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad_ir" / "validator"))


PROMPT_TEMPLATE = """You are a CAD repair agent.  The user gives you:
  - The original Design Plan intent.
  - The previous attempt IR_t (a JSON conforming to cad_ir_v0.1).
  - Solver feedback (sketch constraint solver status, constraint conflicts).
  - KQP feedback (final-geometry intent compliance check).

Your job: produce IR_{{t+1}} in cad_ir_v0.1 JSON that fixes the reported
violations while minimizing changes to IR_t.

Rules:
  1. Prefer changing parameters (numeric values) over changing op_types.
  2. Only change op_type when the solver feedback explicitly says so.
  3. Do not add gratuitous ops; only add when feedback requires it.
  4. Output ONLY the JSON object (no markdown fences, no commentary).

Solver feedback: {solver_feedback}

KQP feedback: {kqp_feedback}

Design Plan summary: {design_plan}

Previous IR (IR_t):
{ir_t}

Output the new IR (IR_t+1):"""


def build_prompt(design_plan: dict, ir_t: dict,
                  solver_feedback: dict, kqp_feedback: dict) -> str:
    """Compose the LLM prompt from design plan + IR + feedbacks."""
    return PROMPT_TEMPLATE.format(
        solver_feedback=json.dumps(solver_feedback, ensure_ascii=False),
        kqp_feedback=json.dumps(kqp_feedback, ensure_ascii=False),
        design_plan=json.dumps(design_plan, ensure_ascii=False),
        ir_t=json.dumps(ir_t, ensure_ascii=False),
    )


def call_zhipu(prompt: str, model: str = "glm-5.1",
                 base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
                 api_key: str | None = None) -> str:
    """Call ZHIPU ChatCompletions endpoint, return assistant text."""
    import requests
    api_key = api_key or os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is not set")
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 4096,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def offline_param_patch(ir_t: dict, solver_feedback: dict,
                          kqp_feedback: dict) -> dict:
    """Deterministic offline fallback: apply small param edits.

    Strategy:
      * For each op whose `params` contains a numeric field that the
        KQP feedback reports as "actual vs expected > tolerance", bump
        the value toward the expected.
      * If solver_feedback has 'has_conflict', do nothing (we cannot
        locally resolve without re-engineering the sketch).
    """
    import copy
    new_ir = copy.deepcopy(ir_t)
    # Pull expected values from KQP feedback
    expected_fixes: dict[str, float] = {}
    qrs = kqp_feedback.get("query_results", []) or []
    for qr in qrs:
        if qr.get("status") == "fail":
            op_id = qr.get("op_id") or qr.get("intent", "")
            exp = qr.get("expected")
            if exp is not None:
                # crude: store expected by op_id for matching
                expected_fixes[op_id] = float(exp)

    if solver_feedback.get("flags", {}).get("has_conflict"):
        return new_ir  # cannot fix locally without re-engineering

    # For each op, if its op_id has an expected fix, modify the first numeric
    # param by ±10% toward expected.
    for op in new_ir.get("operations", []):
        op_id = op.get("op_id", "")
        if op_id not in expected_fixes:
            continue
        exp = expected_fixes[op_id]
        for k, v in op.get("params", {}).items():
            if isinstance(v, (int, float)) and v != 0:
                # Move 20% toward expected
                op["params"][k] = round(v + 0.2 * (exp - v), 4)
                break
    return new_ir


def call_agent(design_plan: dict, ir_t: dict,
                 solver_feedback: dict, kqp_feedback: dict,
                 *, mode: str = "auto") -> dict:
    """Produce IR_{t+1}.

    mode:
      'auto'  - try ZHIPU API, fallback to offline_param_patch
      'online' - require ZHIPU API
      'offline' - always use offline_param_patch (deterministic for testing)
    """
    if mode == "offline":
        return offline_param_patch(ir_t, solver_feedback, kqp_feedback)
    if mode == "online" or (
        mode == "auto" and os.getenv("ZHIPU_API_KEY")
    ):
        prompt = build_prompt(design_plan, ir_t,
                                 solver_feedback, kqp_feedback)
        try:
            text = call_zhipu(prompt)
            # Strip markdown fences if any
            text = text.strip()
            if text.startswith("```"):
                text = text.split("```", 2)[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.split("```", 1)[0]
            new_ir = json.loads(text)
            return new_ir
        except Exception as e:
            if mode == "online":
                raise
            print(f"[llm_agent] online call failed ({type(e).__name__}: {e}); "
                  "falling back to offline_param_patch")
            return offline_param_patch(ir_t, solver_feedback, kqp_feedback)
    return offline_param_patch(ir_t, solver_feedback, kqp_feedback)