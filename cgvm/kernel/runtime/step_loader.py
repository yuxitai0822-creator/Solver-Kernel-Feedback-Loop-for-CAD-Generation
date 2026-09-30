"""step_loader.py — load a STEP file into an OCCT TopoDS_Shape.

We use the OCP (Python wrappers for OpenCascade) interface. The reader
returns a STEPControl_Reader, and after ReadFile + TransferRoots we get
the single top-level shape (TopoDS_Shape).

The output is a tuple (shape, status) where status is one of the IFSelect_RetDone
constants — we treat anything != RetDone as a failure.
"""
from __future__ import annotations
from pathlib import Path
from typing import Tuple

# OCP imports (compatible with cadquery 2.x / OCP 7.8.x)
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone, IFSelect_RetVoid, IFSelect_RetError
from OCP.TopoDS import TopoDS_Shape


RET_NAMES = {
    IFSelect_RetDone: "RetDone",
    IFSelect_RetVoid: "RetVoid",
    IFSelect_RetError: "RetError",
}


def load_step(step_path: str | Path) -> Tuple[TopoDS_Shape, str]:
    """Load a STEP file and return (shape, status_string).

    Raises:
        FileNotFoundError: if the STEP file does not exist.
        RuntimeError: if the reader fails or returns no shape.
    """
    step_path = Path(step_path)
    if not step_path.exists():
        raise FileNotFoundError(f"STEP not found: {step_path}")

    reader = STEPControl_Reader()
    status = reader.ReadFile(str(step_path))
    status_name = RET_NAMES.get(status, f"Unknown({status})")
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP ReadFile returned {status_name} for {step_path}")

    n_roots = reader.TransferRoots()
    if n_roots == 0:
        raise RuntimeError(f"STEP {step_path} has no transferable roots")

    shape = reader.OneShape()
    if shape is None or shape.IsNull():
        raise RuntimeError(f"STEP {step_path} loaded but OneShape is null")
    return shape, status_name
