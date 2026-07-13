"""_adaptor_subprocess.py — Worker that runs the Phase 2 Adaptor in
cad_subproject1 env.  Called by `cad_repair_loop.subprocess_bridge`.

CLI:
    python _adaptor_subprocess.py <ir_path> <out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running this script directly (it adds ROOT to sys.path and
# imports the cad_ir.adaptor modules).
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cad_ir.adaptor.adapter import adapt  # noqa: E402


def main():
    ir_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    sample_id = ir.get("sample_id", "unknown")
    adapt(ir, out_dir, sample_id=sample_id)


if __name__ == "__main__":
    main()