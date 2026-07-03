"""executor.py — Execute the generated Python code as a subprocess.

Running the generated OCCT code in-process (via exec()) causes intermittent
segfaults because OCCT is sensitive to thread/process isolation. We run
each sample in a fresh subprocess instead.

Inputs:
  - generated_code: string (already with REPLACE_ME_STEP_PATH replaced)
  - step_out_path: absolute path to write STEP

Returns: dict with execute_success, export_success, stdout, stderr, error.
"""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def execute_generated_code(code: str, step_out_path: str | Path,
                            history_path: str | Path) -> dict:
    """Run the generated code in a subprocess and produce a STEP file.

    Steps:
      1. Strip the REPLACE_ME_STEP_PATH placeholder and write a real path.
      2. Write the code to a temp .py file.
      3. Run it as a subprocess with timeout.
      4. Verify the STEP file was written.
    """
    result: dict[str, Any] = {
        "execute_success": False,
        "export_success": False,
        "stdout": "",
        "stderr": "",
        "error": None,
    }

    step_path = Path(step_out_path)
    step_path.parent.mkdir(parents=True, exist_ok=True)
    # Substitute the placeholder with the real STEP path
    code = code.replace('r"REPLACE_ME_STEP_PATH"',
                          f'r"{str(step_path).replace(chr(92), "/")}"')

    # Write to a temp .py file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,
                                       encoding="utf-8") as tf:
        tf.write(code)
        tmp_path = Path(tf.name)

    try:
        proc = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True, text=True, timeout=60,
        )
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        result["execute_success"] = (proc.returncode == 0)
        if not result["execute_success"]:
            result["error"] = f"subprocess exit code {proc.returncode}"
    except subprocess.TimeoutExpired:
        result["error"] = "subprocess timeout (60s)"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass

    # Check if STEP was actually written
    if step_path.exists() and step_path.stat().st_size > 0:
        result["export_success"] = True
    else:
        if result["error"] is None:
            result["error"] = "STEP file not created or empty"

    return result
