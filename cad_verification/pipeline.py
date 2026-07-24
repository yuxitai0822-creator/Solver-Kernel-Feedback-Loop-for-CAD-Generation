"""cad_verification/pipeline.py — Pipeline Verification Object.

Wraps ``cad_runtime.executor.execute_cad_script``.  Verifies that the
LLM-emitted cadquery script:

    1.  Parses (Python compile),
    2.  Executes without raising,
    3.  Produces a non-empty STEP file,
    4.  Re-loads in OCCT.

Conforms to the §5.1 spec in ``experiments/phase2b_full/PHASE2B_FULL_REPORT.md``:

    Pipeline verification target:
        syntax correctness, API availability, execution success,
        STEP export, OCCT loading.

    Diagnostic format (code-level):
        {"stage": "compile" | "execute" | "export" | "load",
         "error_type": <short string>,
         "message":    <human-readable line>,
         "trace":      <optional, full stderr>}
"""
from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# cad_runtime is a project-level package.  Make sure the repo root is on
# sys.path before this module is imported.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cad_verification._base import VerificationResult  # noqa: E402
from cad_runtime.executor import execute_cad_script  # noqa: E402


class PipelineVerification:
    """Pipeline Verification Object.

    All four boolean sub-passes (compile / execute / export / load)
    must be True for the verification to count as passed.  When any
    fails, the LLM-facing diagnostic pinpoints the failing stage and
    the underlying error text.
    """

    NAME = "pipeline"

    def run(self, script: str, out_dir: Path) -> VerificationResult:
        """Execute the script and decide pass/fail.

        Parameters
        ----------
        script : str
            Full cadquery Python source emitted by the LLM.
        out_dir : Path
            Per-iteration working directory; the executor writes
            ``runner_script.py``, ``generated.step``, ``stdout.txt``,
            ``stderr.txt`` here.

        Returns
        -------
        VerificationResult
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        # 1. Persist the LLM-emitted script for human inspection.
        (out_dir / "agent.py").write_text(script, encoding="utf-8")

        # 2. Hand off to the cad_runtime executor.
        try:
            res = execute_cad_script(script, out_dir, out_step_name="generated.step")
        except Exception as e:  # noqa: BLE001
            return VerificationResult(
                name=self.NAME,
                passed=False,
                diagnostic={
                    "stage": "execute",
                    "error_type": "executor_crash",
                    "message": f"{type(e).__name__}: {e}",
                    "trace": traceback.format_exc(limit=4),
                },
                full={"exception": f"{type(e).__name__}: {e}"},
            )

        # 3. Map executor output → unified pass/fail.
        compile_pass  = bool(res.get("compile_status"))
        execute_pass  = bool(res.get("execution_status"))
        export_pass   = bool(res.get("step_export"))
        load_pass     = bool(res.get("occt_load"))
        passed        = compile_pass and execute_pass and export_pass and load_pass

        full = {
            "compile_status":  compile_pass,
            "execution_status": execute_pass,
            "step_export":     export_pass,
            "occt_load":       load_pass,
            "runtime_error":   res.get("runtime_error"),
            "step_path":       res.get("step_path"),
            "stdout_path":     res.get("stdout_path"),
            "stderr_path":     res.get("stderr_path"),
        }
        if passed:
            return VerificationResult(
                name=self.NAME,
                passed=True,
                diagnostic={"stage": "all_pass", "error_type": "none",
                            "message": "compile + execute + export + load all OK",
                            "trace": ""},
                full=full,
            )
        # Failed: identify the first stage that failed (left-to-right).
        stage, etype, msg = self._first_failure(res, full)
        return VerificationResult(
            name=self.NAME,
            passed=False,
            diagnostic={
                "stage": stage,
                "error_type": etype,
                "message": msg,
                "trace": self._last_lines(res.get("stderr_path"), n=12),
            },
            full=full,
        )

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _first_failure(res: dict, full: dict) -> tuple[str, str, str]:
        # Order: compile → execute → export → load.
        if not full["compile_status"]:
            err = (res.get("runtime_error") or "compile failed")
            return "compile", "compile_error", err
        if not full["execution_status"]:
            err = (res.get("runtime_error") or "execution failed")
            return "execute", "runtime_error", err
        if not full["step_export"]:
            err = (res.get("runtime_error") or "STEP export failed")
            return "export", "export_error", err
        if not full["occt_load"]:
            err = (res.get("runtime_error") or "OCCT load failed")
            return "load", "occt_load_error", err
        return "unknown", "unknown", "unknown failure"

    @staticmethod
    def _last_lines(path: str | None, n: int = 12) -> str:
        if not path:
            return ""
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
        lines = [ln for ln in text.splitlines() if ln.strip()]
        return "\n".join(lines[-n:])
