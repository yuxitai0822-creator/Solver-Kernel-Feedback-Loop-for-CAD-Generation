"""cad_agent/agent_v2.py — DeepSeek backend (Phase 2B full benchmark).

Replaces the ZHIPU glm-5.1 backend with DeepSeek via the
OpenAI-compatible API.  Drop-in replacement for ``call_cad_agent``.

Defensive mechanisms (added after the full run kept hanging on
unstable network conditions):

  * ``.env`` fallback for the API key (no shell env required).
  * Per-call SDK ``timeout`` (HTTP-level read deadline).
  * ``ThreadPoolExecutor`` with a ``hard_timeout`` that actually
    returns control to the caller after N seconds (we previously
    observed a 10 h hang that the SDK timeout did not interrupt).
  * Retry-with-jitter: transient ``openai.APIConnectionError`` /
    ``APITimeoutError`` / ``TimeoutError`` are retried up to
    ``max_retries`` times with exponential back-off.  JSON parse
    errors and validation errors are NOT retried — they indicate
    a bad model response, not a network problem.
  * The thread pool is kept module-level so we do not pay the
    thread-start cost on every call (and so the ``with`` block
    does not stall shutdown when a thread is mid-hang).
"""
from __future__ import annotations

import json
import os
import random
import time
from typing import Any

import concurrent.futures
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from schema import is_valid_output, make_no_change  # noqa: E402
from prompt_builder import build_prompt  # noqa: E402


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
# DeepSeek's public chat model.  Earlier this file referenced
# ``deepseek-v4-flash``, which is not a real DeepSeek model name and
# would 404 the chat completions endpoint.  Use the canonical name.
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"

# Retry policy
DEFAULT_MAX_RETRIES = 3
DEFAULT_HARD_TIMEOUT = 90          # seconds (covers connect + first byte + body)
DEFAULT_RETRY_BASE_DELAY = 2.0     # seconds; doubled each retry
DEFAULT_RETRY_MAX_DELAY = 30.0     # seconds; clamp

# Module-level pool.  Reusing the pool means the GIL cost of starting
# a new thread is paid once, and so an in-flight thread survives the
# ``with`` exit cleanly even if a call timed out.  4 workers is enough
# for the small concurrency of the benchmark runner.
_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=4)


# Exceptions that indicate a network / transport problem and are
# worth retrying.  We import openai lazily so the module loads even
# if openai is not installed (the benchmark runner needs it, but
# tests / static analysis may not).
def _transient_exceptions():
    import openai
    return (openai.APIConnectionError,
            openai.APITimeoutError,
            concurrent.futures.TimeoutError,
            TimeoutError,
            ConnectionError,
            OSError)


def _load_key_from_dotenv() -> str | None:
    """Fallback: read the API key from a ``.env`` file in the repo root.

    Looks for a line ``DEEPSEEK_API_KEY=<value>`` in ``<repo>/.env``
    (one level above ``cad_agent/``).  No-op if the file or key is
    missing.  Intentionally does not require python-dotenv so the
    agent stays dependency-light.
    """
    try:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if not env_path.exists():
            return None
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == DEEPSEEK_API_KEY_ENV:
                return v.strip().strip('"').strip("'")
    except Exception:
        return None
    return None


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = "\n".join(t.split("\n")[1:])
        if t.endswith("```"):
            t = "\n".join(t.split("\n")[:-1])
    return t.strip()


def _do_api_call(api_key, model, prompt, timeout):
    """The blocking part — extracted so we can run it in a thread."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL, timeout=timeout)
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=4096,
    )


def _submit_with_hard_timeout(api_key, model, prompt, hard_timeout):
    """Submit a call to the module-level pool and wait at most
    ``hard_timeout`` seconds.  Returns the response or raises.

    Using a module-level pool (rather than a per-call ``with``) is
    important: when the main thread times out, the worker thread is
    still attached to the pool and will not block process shutdown.
    """
    future = _POOL.submit(_do_api_call, api_key, model, prompt, hard_timeout)
    return future.result(timeout=hard_timeout)


def call_cad_agent(
    design_plan,
    current_script: str = "",
    out_dir: str = "./out",
    api_key: str = None,
    model: str = DEEPSEEK_MODEL,
    timeout: int = 90,
    hard_timeout: int = DEFAULT_HARD_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_base_delay: float = DEFAULT_RETRY_BASE_DELAY,
    retry_max_delay: float = DEFAULT_RETRY_MAX_DELAY,
    feedback: list[dict] | None = None,
    perturbation_description: str | None = None,
    iteration: int = 0,
    max_iterations: int = 3,
):
    """Call the LLM CAD Agent via DeepSeek's OpenAI-compatible API.

    Hard-timeout: the SDK-level ``timeout`` only bounds the *read* of
    an established connection.  We observed a 10 h hang in a stalled
    TCP connect, so the whole call is submitted to a module-level
    thread pool and waited on for at most ``hard_timeout`` seconds.
    On expiry, ``TimeoutError`` is raised and the worker thread is
    abandoned (it will finish or be reaped at process shutdown).

    Retry: transient errors (network blips, ``APITimeoutError``,
    ``APIConnectionError``) are retried up to ``max_retries`` times
    with exponential back-off and full jitter.  Validation /
    JSON-parse errors are NOT retried — they indicate a bad model
    response, not transport.

    M0-M3 iter loop: when ``feedback`` is provided the prompt is
    rendered by ``cad_agent.prompt_builder_v2.build_prompt_v2``
    (per the M0-M3 spec).  When ``feedback is None`` (the default)
    the original Phase 2A template is used — backward-compatible
    with the v0 single-shot ``p2b_full.py``.
    """
    # The prompt builder back-compat shim handles both v0 and v2
    # rendering based on whether ``feedback`` is None.
    prompt = build_prompt(
        design_plan,
        current_script,
        out_dir,
        feedback=feedback,
        perturbation_description=perturbation_description or "",
        iteration=iteration,
        max_iterations=max_iterations,
    )
    api_key = api_key or os.getenv(DEEPSEEK_API_KEY_ENV) or _load_key_from_dotenv()
    if not api_key:
        raise ValueError(f"{DEEPSEEK_API_KEY_ENV} not set; cannot call LLM")

    transient = _transient_exceptions()
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            resp = _submit_with_hard_timeout(api_key, model, prompt, hard_timeout)
            text = resp.choices[0].message.content or ""
            if not text:
                return make_no_change(reason="LLM returned empty content")
            text = _strip_code_fence(text)
            obj = json.loads(text)
            valid, err = is_valid_output(obj)
            if not valid:
                # Permanent — bad output, do not retry.
                raise ValueError(f"DeepSeek output invalid: {err}\nraw: {text[:200]}")
            return obj
        except json.JSONDecodeError as e:
            # Permanent — model returned malformed JSON.  Retry will
            # almost certainly hit the same problem with temp=0, so
            # surface it immediately.
            raise ValueError(f"DeepSeek output is not valid JSON: {e}\nraw: {text[:200]}")
        except (ValueError,) as e:
            # Re-raise the model-side validation errors as-is.
            if "DeepSeek output" in str(e):
                raise
            # Any other ValueError (key / import) is permanent.
            raise
        except transient as e:
            last_exc = e
            if attempt >= max_retries:
                # Out of retries — bubble the last transient error.
                raise
            # Exponential back-off with full jitter.
            delay = min(retry_max_delay,
                        retry_base_delay * (2 ** attempt))
            delay = random.uniform(0, delay)
            time.sleep(delay)
    # Should be unreachable, but be defensive.
    if last_exc is not None:
        raise last_exc


__all__ = ["call_cad_agent", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"]
