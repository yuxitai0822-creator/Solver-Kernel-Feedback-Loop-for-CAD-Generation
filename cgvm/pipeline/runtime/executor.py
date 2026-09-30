"""cad_runtime/executor.py — uniform cadquery script executor.

Phase 2A Task A1.4.  Replaces the IR-adaptor subprocess (used by v0.2)
with a script-only wrapper.  Inputs a cadquery Python script (string),
runs it, exports a STEP file, and returns a uniform status block.

Per the Phase 2A architecture, the LLM CAD Agent emits a complete
cadquery script each iteration; the executor runs it, captures
runtime artefacts, and feeds status back to the v0.3 loop.

The executor does NOT depend on:
  - CAD IR schema
  - IR adaptor
  - history2IR compiler

It DOES depend on the same cadquery (cad_subproject1) environment
that the v0.2 IR-adaptor used, so STEP files have the same format.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path


# Same env as v0.2 IR-adaptor (for the v0.2 KQP runner to read the
# STEP consistently).  Override via ``CADQUERY_PYTHON`` env var.
DEFAULT_CADQUERY_PYTHON = r"D:/Anaconda/envs/cad_subproject1/python.exe"


def _default_cadquery_python() -> str:
    return os.environ.get("CADQUERY_PYTHON", DEFAULT_CADQUERY_PYTHON)


# ---------------------------------------------------------------------------
# Pre-baked helper:  the script we feed to cadquery writes a STEP
# inside ``out_step_path`` and exits 0.  We give the user's script
# access to ``OUT_STEP_PATH`` via env, so it can do something portable
# like:
#
#     import os, cadquery as cq
#     out = os.environ["OUT_STEP_PATH"]
#     result = cq.Workplane("XY").rect(80, 50).extrude(20)
#     cq.exporters.export(result, out)
#
# This is the standard pattern the reconstruction engine and the v0.2
# IR-adaptor both used, so the executor is a thin shell.
# ---------------------------------------------------------------------------

_RUNNER_TEMPLATE = '''\
import os
import sys
import traceback
import json

# User script is wrapped in a function body so the try/except can
# capture it without indentation issues.
def _user_main():
{user_script_indented}

import cadquery as _cq_auto
_INSTANTIATED_WORKPLANES = []
_orig_wp_init = _cq_auto.Workplane.__init__
def _hooked_wp_init(self, *args, **kwargs):
    _INSTANTIATED_WORKPLANES.append(self)
    return _orig_wp_init(self, *args, **kwargs)
_cq_auto.Workplane.__init__ = _hooked_wp_init

def _export_latest_wp(OUT_STEP_PATH):
    if not _INSTANTIATED_WORKPLANES:
        return False, "no_workplane_created"
    wp = _INSTANTIATED_WORKPLANES[-1]
    try:
        solid_or_compound = wp.val() if hasattr(wp, "val") else wp
        _cq_auto.exporters.export(solid_or_compound, OUT_STEP_PATH)
        return True, "ok"
    except Exception as e:
        return False, f"export_error: {e}"

try:
    _user_main()
    out_path = os.environ.get("OUT_STEP_PATH", "")
    if out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(json.dumps({"status": "ok", "out_step": out_path}))
    else:
        ok, reason = _export_latest_wp(out_path) if out_path else (False, "no_out_path")
        if ok and out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            print(json.dumps({"status": "ok_autoexport", "out_step": out_path}))
        else:
            print(json.dumps({"status": "no_step_written", "out_step": out_path, "autoexport_reason": reason}))
except Exception as e:
    print(json.dumps({"status": "exception",
                       "error": str(e),
                       "traceback": traceback.format_exc()[-500:]}))
'''


def _indent_user_script(s: str) -> str:
    """Indent every non-empty line of the user script by 4 spaces so it
    fits inside the `_user_main` function body."""
    out = []
    for line in s.splitlines():
        if line.strip() == "":
            out.append("")
        else:
            out.append("    " + line)
    return "\n".join(out)


def execute_cad_script(script: str, out_dir: Path,
                        out_step_name: str = "generated.step",
                        cadquery_python: str | None = None,
                        timeout: int = 120) -> dict:
    """Run a cadquery Python script and export a STEP.

    Args:
        script: the cadquery source code.
        out_dir: directory to write the runner output, stdout, stderr,
            generated step into.
        out_step_name: filename of the STEP inside out_dir.
        cadquery_python: path to a Python with cadquery/OCP.  Defaults
            to the project's cad_subproject1 env.
        timeout: subprocess timeout in seconds.

    Returns a uniform status block (see plan §1.4.2):
      {
        "compile_status": bool,        # 脚本可解析
        "execution_status": bool,      # 无异常运行
        "step_export": bool,           # STEP 文件已生成
        "occt_load": bool,             # OCP 可读该 STEP
        "runtime_error": str | None,
        "step_path": str | None,
        "stdout": str, "stderr": str
      }
    """
    out_dir = Path(out_dir).absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    cadquery_python = cadquery_python or _default_cadquery_python()
    out_step_path = out_dir / out_step_name
    out_runner_path = out_dir / "runner_script.py"
    out_stdout_path = out_dir / "stdout.txt"
    out_stderr_path = out_dir / "stderr.txt"

    # Inject OUT_STEP_PATH env so the user script knows where to write
    # the STEP.  Compatibility shim: the v0.2 reconstruction-engine
    # scripts use a placeholder `OUT_STEP = r"REPLACE_ME_STEP_PATH"`
    # that needs to be replaced with the env-supplied path.  We rewrite
    # that line before exec so legacy scripts run unchanged.
    user_script = script
    user_script = user_script.replace(
        'OUT_STEP = r"REPLACE_ME_STEP_PATH"',
        'OUT_STEP = os.environ.get("OUT_STEP_PATH", r"REPLACE_ME_STEP_PATH")',
    )
    user_script = user_script.replace(
        "OUT_STEP = r'REPLACE_ME_STEP_PATH'",
        "OUT_STEP = os.environ.get('OUT_STEP_PATH', r'REPLACE_ME_STEP_PATH')",
    )
    # Also: if the user script defines `OUT_STEP = ...` to a literal
    # value, and it ends in `.step`, replace with the env value.
    import re as _re
    user_script = _re.sub(
        r'^(OUT_STEP\s*=\s*)[rR]?"[^"]*\.step"',
        r'\1os.environ.get("OUT_STEP_PATH", "\g<0>".split("=")[-1].strip().strip("r").strip("\\").strip("\\").strip("\\"))',
        user_script, flags=_re.MULTILINE,
    )
    # NOTE: auto-export via cadquery Workplane hook in _RUNNER_TEMPLATE.
    # Use str.replace instead of .format() because user scripts contain { and }.
    runner_source = _RUNNER_TEMPLATE.replace("{user_script_indented}", _indent_user_script(user_script), 1)
    out_runner_path.write_text(runner_source, encoding="utf-8")

    proc_env = os.environ.copy()
    proc_env["OUT_STEP_PATH"] = str(out_step_path)

    compile_status = False
    execution_status = False
    step_export = False
    runtime_error = None
    stdout_text = ""
    stderr_text = ""

    try:
        proc = subprocess.run(
            [cadquery_python, str(out_runner_path)],
            capture_output=True, text=True, timeout=timeout,
            env=proc_env, cwd=str(out_dir),
        )
        stdout_text = proc.stdout or ""
        stderr_text = proc.stderr or ""
        # Python parsed and ran the script without an exception.
        if proc.returncode == 0:
            compile_status = True
            execution_status = True
        else:
            # Failure — try to distinguish parse errors from runtime errors.
            compile_status = "SyntaxError" not in (stderr_text or "")
            execution_status = proc.returncode == 0
    except subprocess.TimeoutExpired as e:
        runtime_error = f"timeout after {timeout}s"
        stderr_text = (e.stderr.decode() if e.stderr else "") + "\n" + str(e)
    except Exception as e:
        runtime_error = f"{type(e).__name__}: {e}"
        stderr_text = traceback.format_exc()

    out_stdout_path.write_text(stdout_text, encoding="utf-8")
    out_stderr_path.write_text(stderr_text, encoding="utf-8")

    if out_step_path.exists() and out_step_path.stat().st_size > 0:
        step_export = True

    # OCCT load:  can OCP open the STEP?  Cheap to do here, in-process.
    occt_load = False
    if step_export:
        try:
            from OCP.STEPControl import STEPControl_Reader
            r = STEPControl_Reader()
            r.ReadFile(str(out_step_path))
            r.TransferRoots()
            r.OneShape()  # will raise if not parseable
            occt_load = True
        except Exception as e:
            runtime_error = (runtime_error or "") + f" | occt_load: {e}"

    return {
        "compile_status": compile_status,
        "execution_status": execution_status,
        "step_export": step_export,
        "occt_load": occt_load,
        "runtime_error": runtime_error,
        "step_path": str(out_step_path) if step_export else None,
        "stdout_path": str(out_stdout_path),
        "stderr_path": str(out_stderr_path),
    }


__all__ = ["execute_cad_script", "DEFAULT_CADQUERY_PYTHON"]
